import { FormEvent, useCallback, useEffect, useState } from "react";
import {
  api,
  Appointment,
  Doctor,
  FreeSlot,
  Notification,
  ScheduleRule,
  User,
  UserRole,
} from "./api";

const WEEKDAYS = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"];

type Tab = "appointments" | "schedule" | "notifications" | "profile" | "users";

function AuthScreen({
  onAuth,
}: {
  onAuth: (user: User, access: string, refresh: string) => void;
}) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    email: "",
    password: "",
    full_name: "",
    phone: "",
    role: "patient" as UserRole,
  });

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      const res =
        mode === "login"
          ? await api.login(form.email, form.password)
          : await api.register({
              email: form.email,
              password: form.password,
              full_name: form.full_name,
              phone: form.phone,
              role: form.role,
            });
      onAuth(res.user, res.access_token, res.refresh_token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка");
    }
  };

  return (
    <div className="auth-wrap">
      <div className="card">
        <div className="auth-header">
          <h1 className="brand">SKEMA</h1>
          <p className="brand-sub">Онлайн-запись пациентов</p>
        </div>
        <h2>{mode === "login" ? "Вход" : "Регистрация"}</h2>
        {error && <p className="error">{error}</p>}
        <form onSubmit={submit}>
          <label>Email</label>
          <input
            type="email"
            required
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
          <label>Пароль</label>
          <input
            type="password"
            required
            minLength={8}
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
          {mode === "register" && (
            <>
              <label>ФИО</label>
              <input
                required
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              />
              <label>Телефон</label>
              <input
                required
                value={form.phone}
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
              />
              <label>Роль</label>
              <select
                value={form.role}
                onChange={(e) =>
                  setForm({ ...form, role: e.target.value as UserRole })
                }
              >
                <option value="patient">Пациент</option>
                <option value="doctor">Врач</option>
                <option value="registrar">Регистратор</option>
              </select>
            </>
          )}
          <button type="submit" className="primary">
            {mode === "login" ? "Войти" : "Зарегистрироваться"}
          </button>
        </form>
        <p className="muted" style={{ marginTop: "1rem" }}>
          {mode === "login" ? "Нет аккаунта?" : "Уже есть аккаунт?"}{" "}
          <a
            href="#"
            onClick={(e) => {
              e.preventDefault();
              setMode(mode === "login" ? "register" : "login");
            }}
          >
            {mode === "login" ? "Регистрация" : "Вход"}
          </a>
        </p>
        <p className="muted" style={{ marginTop: "0.5rem" }}>
          Демо: patient@clinic.example / Password123!
        </p>
      </div>
    </div>
  );
}

function AppointmentsPanel({ user }: { user: User }) {
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [slots, setSlots] = useState<FreeSlot[]>([]);
  const [doctorId, setDoctorId] = useState(1);
  const [slot, setSlot] = useState("");
  const [note, setNote] = useState("");
  const [patientId, setPatientId] = useState(1);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");

  const load = useCallback(async () => {
    const [d, a] = await Promise.all([
      api.doctors(),
      api.appointments(search ? `&q=${encodeURIComponent(search)}` : ""),
    ]);
    setDoctors(d.items);
    setAppointments(a.items);
    if (d.items.length) setDoctorId(d.items[0].id);
  }, [search]);

  useEffect(() => {
    load().catch(console.error);
  }, [load]);

  const loadSlots = async () => {
    const from = new Date().toISOString().slice(0, 10);
    const to = new Date(Date.now() + 14 * 86400000).toISOString().slice(0, 10);
    const s = await api.freeSlots(doctorId, from, to);
    setSlots(s);
    if (s.length) setSlot(s[0].starts_at);
  };

  const book = async () => {
    setError("");
    try {
      if (user.role === "doctor" || user.role === "admin" || user.role === "registrar") {
        await api.assign({
          patient_id: patientId,
          doctor_id: doctorId,
          starts_at: slot,
          note,
        });
      } else {
        await api.book({ doctor_id: doctorId, starts_at: slot, note });
      }
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка");
    }
  };

  return (
    <>
      <div className="card">
        <h2>Онлайн-запись</h2>
        {error && <p className="error">{error}</p>}
        <div className="grid2">
          <div>
            <label>Врач</label>
            <select
              value={doctorId}
              onChange={(e) => setDoctorId(Number(e.target.value))}
            >
              {doctors.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.full_name} — {d.specialization}
                </option>
              ))}
            </select>
            <button type="button" className="ghost" onClick={loadSlots}>
              Показать свободные окна
            </button>
            <label>Слот</label>
            <select value={slot} onChange={(e) => setSlot(e.target.value)}>
              {slots.map((s) => (
                <option key={s.starts_at} value={s.starts_at}>
                  {new Date(s.starts_at).toLocaleString("ru-RU")}
                </option>
              ))}
            </select>
            {(user.role === "doctor" ||
              user.role === "admin" ||
              user.role === "registrar") && (
              <>
                <label>ID пациента</label>
                <input
                  type="number"
                  value={patientId}
                  onChange={(e) => setPatientId(Number(e.target.value))}
                />
              </>
            )}
            <label>Комментарий</label>
            <input value={note} onChange={(e) => setNote(e.target.value)} />
            <button type="button" className="primary" onClick={book}>
              {user.role === "patient" ? "Записаться" : "Назначить приём"}
            </button>
          </div>
        </div>
      </div>
      <div className="card">
        <h2>Мои записи</h2>
        <input
          placeholder="Поиск..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <table>
          <thead>
            <tr>
              <th>Дата</th>
              <th>Врач</th>
              <th>Статус</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {appointments.map((a) => (
              <tr key={a.id}>
                <td>{new Date(a.starts_at).toLocaleString("ru-RU")}</td>
                <td>
                  {a.doctor_name} ({a.specialization})
                </td>
                <td>
                  <span className={`badge ${a.status}`}>{a.status}</span>
                </td>
                <td>
                  {a.status === "booked" && (
                    <>
                      <button
                        type="button"
                        className="ghost danger"
                        onClick={() => api.cancel(a.id).then(load)}
                      >
                        Отменить
                      </button>
                      <button
                        type="button"
                        className="ghost"
                        onClick={() => {
                          const ns = prompt("Новое время (ISO):", a.starts_at);
                          if (ns) api.reschedule(a.id, ns).then(load);
                        }}
                      >
                        Перенести
                      </button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

function SchedulePanel({ user }: { user: User }) {
  const [doctorId, setDoctorId] = useState(1);
  const [rules, setRules] = useState<ScheduleRule[]>([]);
  const [weekday, setWeekday] = useState(0);
  const [start, setStart] = useState("09:00");
  const [end, setEnd] = useState("17:00");
  const [msg, setMsg] = useState("");

  const load = async () => {
    const d = await api.doctors();
    const id =
      user.role === "doctor"
        ? d.items.find((x) => x.user_id === user.id)?.id ?? 1
        : doctorId;
    setDoctorId(id);
    setRules(await api.scheduleRules(id));
  };

  useEffect(() => {
    load().catch(console.error);
  }, []);

  const addRule = async () => {
    await api.createScheduleRule(doctorId, {
      weekday,
      start_time: start,
      end_time: end,
      slot_minutes: 30,
    });
    setMsg("Правило добавлено");
    await load();
  };

  return (
    <div className="card">
      <h2>Расписание врача</h2>
      <p className="muted">Создание и редактирование графика, автообновление слотов</p>
      {msg && <p className="muted">{msg}</p>}
      <div className="grid2">
        <div>
          <label>День недели</label>
          <select value={weekday} onChange={(e) => setWeekday(Number(e.target.value))}>
            {WEEKDAYS.map((w, i) => (
              <option key={w} value={i}>
                {w}
              </option>
            ))}
          </select>
          <label>Начало</label>
          <input type="time" value={start} onChange={(e) => setStart(e.target.value)} />
          <label>Конец</label>
          <input type="time" value={end} onChange={(e) => setEnd(e.target.value)} />
          <button type="button" className="primary" onClick={addRule}>
            Добавить правило
          </button>
          <button
            type="button"
            className="ghost"
            onClick={() => api.refreshSchedule(doctorId).then((r) => setMsg(r.message))}
          >
            Обновить расписание
          </button>
        </div>
      </div>
      <table>
        <thead>
          <tr>
            <th>День</th>
            <th>Время</th>
            <th>Слот (мин)</th>
            <th>Активно</th>
          </tr>
        </thead>
        <tbody>
          {rules.map((r) => (
            <tr key={r.id}>
              <td>{WEEKDAYS[r.weekday]}</td>
              <td>
                {r.start_time} — {r.end_time}
              </td>
              <td>{r.slot_minutes}</td>
              <td>{r.is_active ? "да" : "нет"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function NotificationsPanel() {
  const [items, setItems] = useState<Notification[]>([]);

  const load = () => api.notifications().then((r) => setItems(r.items));

  useEffect(() => {
    load().catch(console.error);
  }, []);

  return (
    <div className="card">
      <h2>Уведомления</h2>
      <p className="muted">Записи, напоминания, изменения расписания</p>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {items.map((n) => (
          <li
            key={n.id}
            style={{
              padding: "0.75rem 0",
              borderBottom: "1px solid var(--border)",
              opacity: n.is_read ? 0.6 : 1,
            }}
          >
            <strong>{n.title}</strong>
            <br />
            <span className="muted">{n.message}</span>
            <br />
            <button
              type="button"
              className="ghost"
              style={{ marginTop: "0.35rem" }}
              onClick={() => api.markNotification(n.id).then(load)}
            >
              Прочитано
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

function ProfilePanel({ user, onUpdate }: { user: User; onUpdate: (u: User) => void }) {
  const [fullName, setFullName] = useState(user.full_name ?? "");
  const [phone, setPhone] = useState(user.phone ?? "");
  const [msg, setMsg] = useState("");

  const save = async () => {
    const u = await api.updateProfile({ full_name: fullName, phone });
    onUpdate(u);
    setMsg("Профиль сохранён");
  };

  return (
    <div className="card">
      <h2>Профиль</h2>
      <p className="muted">
        {user.email} · роль: <span className="badge">{user.role}</span>
      </p>
      {msg && <p className="muted">{msg}</p>}
      <label>ФИО</label>
      <input value={fullName} onChange={(e) => setFullName(e.target.value)} />
      <label>Телефон</label>
      <input value={phone} onChange={(e) => setPhone(e.target.value)} />
      <button type="button" className="primary" onClick={save}>
        Сохранить
      </button>
    </div>
  );
}

function UsersPanel() {
  const [users, setUsers] = useState<User[]>([]);
  const [q, setQ] = useState("");

  useEffect(() => {
    api.users(q || undefined).then((r) => setUsers(r.items));
  }, [q]);

  return (
    <div className="card">
      <h2>Пользователи</h2>
      <input placeholder="Поиск..." value={q} onChange={(e) => setQ(e.target.value)} />
      <table>
        <thead>
          <tr>
            <th>Email</th>
            <th>Имя</th>
            <th>Роль</th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td>{u.email}</td>
              <td>{u.full_name}</td>
              <td>{u.role}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function App() {
  const [user, setUser] = useState<User | null>(() => {
    const raw = localStorage.getItem("user");
    return raw ? (JSON.parse(raw) as User) : null;
  });
  const [tab, setTab] = useState<Tab>("appointments");

  const onAuth = (u: User, access: string, refresh: string) => {
    localStorage.setItem("user", JSON.stringify(u));
    localStorage.setItem("access_token", access);
    localStorage.setItem("refresh_token", refresh);
    setUser(u);
  };

  const logout = () => {
    localStorage.clear();
    setUser(null);
  };

  if (!user) return <AuthScreen onAuth={onAuth} />;

  const canSchedule =
    user.role === "doctor" || user.role === "admin" || user.role === "registrar";
  const canUsers = user.role === "admin" || user.role === "registrar";

  return (
    <div className="layout">
      <aside className="sidebar">
        <h1 className="brand">SKEMA</h1>
        <p className="brand-sub">Онлайн-запись</p>
        <button
          type="button"
          className={`nav-btn ${tab === "appointments" ? "active" : ""}`}
          onClick={() => setTab("appointments")}
        >
          Записи
        </button>
        {canSchedule && (
          <button
            type="button"
            className={`nav-btn ${tab === "schedule" ? "active" : ""}`}
            onClick={() => setTab("schedule")}
          >
            Расписание
          </button>
        )}
        <button
          type="button"
          className={`nav-btn ${tab === "notifications" ? "active" : ""}`}
          onClick={() => setTab("notifications")}
        >
          Уведомления
        </button>
        <button
          type="button"
          className={`nav-btn ${tab === "profile" ? "active" : ""}`}
          onClick={() => setTab("profile")}
        >
          Профиль
        </button>
        {canUsers && (
          <button
            type="button"
            className={`nav-btn ${tab === "users" ? "active" : ""}`}
            onClick={() => setTab("users")}
          >
            Пользователи
          </button>
        )}
        <button type="button" className="nav-btn" onClick={logout} style={{ marginTop: "auto" }}>
          Выход
        </button>
      </aside>
      <main className="main">
        {tab === "appointments" && <AppointmentsPanel user={user} />}
        {tab === "schedule" && canSchedule && <SchedulePanel user={user} />}
        {tab === "notifications" && <NotificationsPanel />}
        {tab === "profile" && <ProfilePanel user={user} onUpdate={(u) => setUser(u)} />}
        {tab === "users" && canUsers && <UsersPanel />}
      </main>
    </div>
  );
}
