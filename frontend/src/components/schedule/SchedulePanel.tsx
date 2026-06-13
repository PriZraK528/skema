import { useEffect, useState } from "react";
import { api, AvailabilitySlot, Doctor, User } from "../../api";
import {
  DEFAULT_SLOT_DURATION_MINUTES,
  GENERIC_ERROR_RU,
  MAX_SLOT_DURATION_MINUTES,
  MIN_SLOT_DURATION_MINUTES,
  MS_PER_DAY,
} from "../../constants";
import { formatDateTime, toDatetimeLocal } from "../../utils/datetime";
import { isAdmin } from "../../utils/roles";

interface SchedulePanelProps {
  user: User;
}

export function SchedulePanel({ user }: SchedulePanelProps) {
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [doctorId, setDoctorId] = useState(1);
  const [slots, setSlots] = useState<AvailabilitySlot[]>([]);
  const [startsAt, setStartsAt] = useState(() =>
    toDatetimeLocal(new Date(Date.now() + MS_PER_DAY)),
  );
  const [duration, setDuration] = useState(DEFAULT_SLOT_DURATION_MINUTES);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  const adminView = isAdmin(user);

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
      setError(e instanceof Error ? e.message : GENERIC_ERROR_RU);
    }
  };

  const removeSlot = async (id: number) => {
    setError("");
    try {
      await api.deleteAvailabilitySlot(id);
      setMsg("Окно удалено");
      await loadSlots(doctorId);
    } catch (e) {
      setError(e instanceof Error ? e.message : GENERIC_ERROR_RU);
    }
  };

  const selectedDoctor = doctors.find((d) => d.id === doctorId);

  return (
    <div className="card">
      <h2>{adminView ? "Расписание врача" : "Мои окна для записи"}</h2>
      <p className="muted">
        Пациенты видят только те слоты, которые врач создал здесь. По умолчанию свободных окон нет.
      </p>
      {adminView && (
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
            min={MIN_SLOT_DURATION_MINUTES}
            max={MAX_SLOT_DURATION_MINUTES}
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
              <td>{formatDateTime(s.starts_at)}</td>
              <td>{formatDateTime(s.ends_at)}</td>
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
