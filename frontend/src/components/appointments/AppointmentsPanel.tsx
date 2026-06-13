import { useCallback, useEffect, useState } from "react";
import { api, Appointment, Doctor, FreeSlot, PatientBrief, User } from "../../api";
import { StatusBadge } from "../ui/StatusBadge";

interface AppointmentsPanelProps {
  user: User;
}

export function AppointmentsPanel({ user }: AppointmentsPanelProps) {
  const [doctors, setDoctors] = useState<Doctor[]>([]);
  const [patients, setPatients] = useState<PatientBrief[]>([]);
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [slots, setSlots] = useState<FreeSlot[]>([]);
  const [doctorId, setDoctorId] = useState(1);
  const [slot, setSlot] = useState("");
  const [note, setNote] = useState("");
  const [patientName, setPatientName] = useState("");
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");

  const staffView = user.role === "doctor" || user.role === "admin";

  const load = useCallback(async () => {
    const [d, a] = await Promise.all([
      api.doctors(),
      api.appointments(search ? `&q=${encodeURIComponent(search)}` : ""),
    ]);
    setDoctors(d.items);
    setAppointments(a.items);
    if (d.items.length) setDoctorId((prev) => d.items.some((x) => x.id === prev) ? prev : d.items[0].id);
  }, [search]);

  useEffect(() => {
    load().catch(console.error);
  }, [load]);

  useEffect(() => {
    if (!staffView) return;
    api.patients().then(setPatients).catch(console.error);
  }, [staffView]);

  const loadSlots = async () => {
    const from = new Date().toISOString().slice(0, 10);
    const to = new Date(Date.now() + 14 * 86400000).toISOString().slice(0, 10);
    const s = await api.freeSlots(doctorId, from, to);
    setSlots(s);
    if (s.length) setSlot(s[0].starts_at);
    else setSlot("");
  };

  const book = async () => {
    setError("");
    try {
      if (staffView) {
        await api.assign({
          patient_name: patientName.trim(),
          doctor_id: doctorId,
          starts_at: slot,
          note,
        });
      } else {
        await api.book({ doctor_id: doctorId, starts_at: slot, note });
      }
      setPatientName("");
      setNote("");
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
              disabled={user.role === "doctor"}
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
            <select value={slot} onChange={(e) => setSlot(e.target.value)} disabled={!slots.length}>
              {slots.map((s) => (
                <option key={s.starts_at} value={s.starts_at}>
                  {new Date(s.starts_at).toLocaleString("ru-RU")}
                </option>
              ))}
            </select>
            {staffView && (
              <>
                <label>ФИО пациента</label>
                <input
                  list="patients-list"
                  value={patientName}
                  onChange={(e) => setPatientName(e.target.value)}
                  placeholder="Например, Петров Пётр"
                />
                <datalist id="patients-list">
                  {patients.map((p) => (
                    <option key={p.id} value={p.full_name} />
                  ))}
                </datalist>
              </>
            )}
            <label>Комментарий</label>
            <input value={note} onChange={(e) => setNote(e.target.value)} />
            <button type="button" className="primary" onClick={book} disabled={!slot || (staffView && !patientName.trim())}>
              {user.role === "patient" ? "Записаться" : "Назначить приём"}
            </button>
          </div>
        </div>
      </div>
      <div className="card">
        <h2>Мои записи</h2>
        <input
          placeholder={
            staffView
              ? "Поиск по ФИО пациента, врача или комментарию..."
              : "Поиск по врачу или комментарию..."
          }
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <table>
          <thead>
            <tr>
              <th>Дата</th>
              {staffView && <th>Пациент</th>}
              <th>Врач</th>
              <th>Статус</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {appointments.map((a) => (
              <tr key={a.id}>
                <td>{new Date(a.starts_at).toLocaleString("ru-RU")}</td>
                {staffView && <td>{a.patient_name ?? "—"}</td>}
                <td>
                  {a.doctor_name} ({a.specialization})
                </td>
                <td>
                  <StatusBadge status={a.status} />
                </td>
                <td>
                  {a.status === "booked" && (
                    <button
                      type="button"
                      className="ghost danger"
                      onClick={() => api.cancel(a.id).then(load).catch((e) => setError(String(e)))}
                    >
                      Отменить
                    </button>
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
