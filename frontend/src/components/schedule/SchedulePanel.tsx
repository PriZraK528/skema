import { useEffect, useState } from "react";
import { api, AvailabilitySlot, User } from "../../api";
function toDatetimeLocal(d: Date): string {
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;
}

interface SchedulePanelProps {
  user: User;
}

export function SchedulePanel({ user }: SchedulePanelProps) {
  const [doctorId, setDoctorId] = useState(1);
  const [slots, setSlots] = useState<AvailabilitySlot[]>([]);
  const [startsAt, setStartsAt] = useState(() =>
    toDatetimeLocal(new Date(Date.now() + 86400000)),
  );
  const [duration, setDuration] = useState(30);
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  const load = async () => {
    const d = await api.doctors();
    const id =
      user.role === "doctor"
        ? d.items.find((x) => x.user_id === user.id)?.id ?? 1
        : doctorId;
    setDoctorId(id);
    setSlots(await api.availabilitySlots(id));
  };

  useEffect(() => {
    load().catch(console.error);
  }, []);

  const addSlot = async () => {
    setError("");
    try {
      const start = new Date(startsAt);
      await api.createAvailabilitySlot(doctorId, {
        starts_at: start.toISOString(),
        duration_minutes: duration,
      });
      setMsg("Окно для записи создано");
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка");
    }
  };

  const removeSlot = async (id: number) => {
    setError("");
    try {
      await api.deleteAvailabilitySlot(id);
      setMsg("Окно удалено");
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Ошибка");
    }
  };

  return (
    <div className="card">
      <h2>Мои окна для записи</h2>
      <p className="muted">
        Пациенты видят только те слоты, которые вы создали здесь. По умолчанию свободных окон нет.
      </p>
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
