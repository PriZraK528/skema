import { useCallback, useEffect, useState } from "react";
import { api, Appointment, Doctor, FreeSlot, User } from "../../api";
import { StatusBadge } from "../ui/StatusBadge";

function toDatetimeLocal(d: Date): string {
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

interface AppointmentsPanelProps {
  user: User;
}

export function AppointmentsPanel({ user }: AppointmentsPanelProps) {
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [slots, setSlots] = useState<FreeSlot[]>([]);
  const [doctorId, setDoctorId] = useState(1);
  const [slot, setSlot] = useState("");
  const [note, setNote] = useState("");
  const [patientId, setPatientId] = useState(1);
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [rescheduleId, setRescheduleId] = useState<number | null>(null);
  const [rescheduleTime, setRescheduleTime] = useState("");

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

  const startReschedule = (a: Appointment) => {
    setRescheduleId(a.id);
    setRescheduleTime(toDatetimeLocal(new Date(a.starts_at)));
  };

  const confirmReschedule = async () => {
    if (rescheduleId == null) return;
    setError("");
    try {
      await api.reschedule(rescheduleId, new Date(rescheduleTime).toISOString());
      setRescheduleId(null);
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка");
    }
  };

  const staffBooking =
    user.role === "doctor" || user.role === "admin" || user.role === "registrar";

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
              Обновить свободные окна
            </button>
            {slots.length === 0 && (
              <p className="muted">
                Нет свободных окон — врач должен добавить их в разделе «Расписание».
              </p>
            )}
            <label>Слот</label>
            <select value={slot} onChange={(e) => setSlot(e.target.value)}>
              {slots.map((s) => (
                <option key={s.starts_at} value={s.starts_at}>
                  {new Date(s.starts_at).toLocaleString("ru-RU")}
                </option>
              ))}
            </select>
            {staffBooking && (
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
                  <StatusBadge status={a.status} />
                </td>
                <td>
                  {a.status === "booked" && rescheduleId !== a.id && (
                    <>
                      <button
                        type="button"
                        className="ghost danger"
                        onClick={() => api.cancel(a.id).then(load).catch((e) => setError(String(e)))}
                      >
                        Отменить
                      </button>
                      <button
                        type="button"
                        className="ghost"
                        onClick={() => startReschedule(a)}
                      >
                        Перенести
                      </button>
                    </>
                  )}
                  {rescheduleId === a.id && (
                    <div className="reschedule-inline">
                      <input
                        type="datetime-local"
                        value={rescheduleTime}
                        onChange={(e) => setRescheduleTime(e.target.value)}
                      />
                      <button type="button" className="primary" onClick={confirmReschedule}>
                        Сохранить
                      </button>
                      <button
                        type="button"
                        className="ghost"
                        onClick={() => setRescheduleId(null)}
                      >
                        Отмена
                      </button>
                    </div>
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
