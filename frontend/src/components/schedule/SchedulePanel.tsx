import { useEffect, useState } from "react";
import { api, AvailabilitySlot, Doctor, User } from "../../api";

function toDatetimeLocal(d: Date): string {
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

interface SchedulePanelProps {
  user: User;
}

export function SchedulePanel({ user }: SchedulePanelProps) {
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [doctorId, setDoctorId] = useState(1);
  const [slots, setSlots] = useState<AvailabilitySlot[]>([]);
  const [startsAt, setStartsAt] = useState(() =>
    toDatetimeLocal(new Date(Date.now() + 86400000)),
  );
  const [duration, setDuration] = useState(30);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  const isAdmin = user.role === "admin";

  const loadSlots = async (id: number) => {
    setSlots(await api.availabilitySlots(id));
  };

  const load = async () => {
    const d = await api.doctors();
    setDoctors(d.items);
    const id =
      user.role === "doctor"
        ? d.items.find((x) => x.user_id === user.id)?.id ?? d.items[0]?.id ?? 1
        : doctorId || d.items[0]?.id || 1;
    setDoctorId(id);
    if (id) await loadSlots(id);
  };

  useEffect(() => {
    load().catch(console.error);
  }, []);

  const onDoctorChange = async (id: number) => {
    setDoctorId(id);
    await loadSlots(id);
  };

  const addSlot = async () => {
    setError("");
    try {
      const start = new Date(startsAt);
      await api.createAvailabilitySlot(doctorId, {
        starts_at: start.toISOString(),
        duration_minutes: duration,
      });
      setMsg("Окно для записи создано");
      await loadSlots(doctorId);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка");
    }
  };

  const removeSlot = async (id: number) => {
    setError("");
    try {
      await api.deleteAvailabilitySlot(id);
      setMsg("Окно удалено");
      await loadSlots(doctorId);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка");
    }
  };

  const selectedDoctor = doctors.find((d) => d.id === doctorId);

  return (
    <div className="card">
      <h2>{isAdmin ? "Расписание врача" : "Мои окна для записи"}</h2>
      <p className="muted">
        Пациенты видят только те слоты, которые врач создал здесь. По умолчанию свободных окон нет.
      </p>
      {isAdmin && (
        <>
          <label>Врач</label>
          <select
            value={doctorId}
            onChange={(e) => onDoctorChange(Number(e.target.value))}
          >
            {doctors.map((d) => (
              <option key={d.id} value={d.id}>
                {d.full_name} — {d.specialization}
              </option>
            ))}
          </select>
          {selectedDoctor && (
            <p className="muted">
              Окна ниже относятся к: {selectedDoctor.full_name}, {selectedDoctor.specialization}
            </p>
          )}
        </>
      )}
      {msg && <p className="muted">{msg}</p>}
      {error && <p className="error">{error}</p>}
      <div className="grid2">
        <div>
          <label>Начало приёма</label>
          <input
            type="datetime-local"
            value={startsAt}
            onChange={(e) => setStartsAt(e.target.value)}
          />
          <label>Длительность (мин)</label>
          <input
            type="number"
            min={5}
            max={480}
            value={duration}
            onChange={(e) => setDuration(Number(e.target.value))}
          />
          <button type="button" className="primary" onClick={addSlot}>
            Создать окно
          </button>
        </div>
      </div>
      <table>
        <thead>
          <tr>
            <th>Начало</th>
            <th>Конец</th>
            <th>Статус</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {slots.length === 0 && (
            <tr>
              <td colSpan={4} className="muted">
                Нет созданных окон
              </td>
            </tr>
          )}
          {slots.map((s) => (
            <tr key={s.id}>
              <td>{new Date(s.starts_at).toLocaleString("ru-RU")}</td>
              <td>{new Date(s.ends_at).toLocaleString("ru-RU")}</td>
              <td>
                <span className={`badge ${s.is_booked ? "cancelled" : "booked"}`}>
                  {s.is_booked ? "Занято" : "Свободно"}
                </span>
              </td>
              <td>
                {!s.is_booked && (
                  <button type="button" className="ghost danger" onClick={() => removeSlot(s.id)}>
                    Удалить
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
