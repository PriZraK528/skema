import { useCallback, useEffect, useState } from "react";
import { api, Appointment, Doctor, FreeSlot, PatientBrief, User } from "../../api";
import { GENERIC_ERROR_RU, SLOT_LOOKAHEAD_DAYS } from "../../constants";
import { addDaysIso, formatDateTime, todayIsoDate } from "../../utils/datetime";
import { isDoctor, isStaff } from "../../utils/roles";
import { StatusBadge } from "../ui/StatusBadge";

interface AppointmentsPanelProps {
  user: User;
  onActivity?: () => void;
}

export function AppointmentsPanel({ user, onActivity }: AppointmentsPanelProps) {
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

  const staffView = isStaff(user);
  const doctorView = isDoctor(user);
  const ownDoctor = doctors.find((d) => d.user_id === user.id);

  const load = useCallback(async () => {
    const [d, a] = await Promise.all([
      api.doctors(),
      api.appointments(search ? `&q=${encodeURIComponent(search)}` : ""),
    ]);
    setDoctors(d.items);
    setAppointments(a.items);
    if (doctorView) {
      const mine = d.items.find((x) => x.user_id === user.id);
      if (mine) setDoctorId(mine.id);
    } else if (d.items.length) {
      setDoctorId((prev) => (d.items.some((x) => x.id === prev) ? prev : d.items[0].id));
    }
  }, [search, doctorView, user.id]);

  useEffect(() => {
    load().catch(console.error);
  }, [load]);

  useEffect(() => {
    if (!staffView) return;
    api.patients().then(setPatients).catch(console.error);
  }, [staffView]);

  const loadSlots = async () => {
    const from = todayIsoDate();
    const to = addDaysIso(new Date(), SLOT_LOOKAHEAD_DAYS);
    const id = doctorView && ownDoctor ? ownDoctor.id : doctorId;
    const s = await api.freeSlots(id, from, to);
    setSlots(s);
    if (s.length) setSlot(s[0].starts_at);
    else setSlot("");
  };

  const book = async () => {
    setError("");
    try {
      const id = doctorView && ownDoctor ? ownDoctor.id : doctorId;
      if (staffView) {
        await api.assign({
          patient_name: patientName.trim(),
          doctor_id: id,
          starts_at: slot,
          note,
        });
      } else {
        await api.book({ doctor_id: id, starts_at: slot, note });
      }
      setPatientName("");
      setNote("");
      await load();
      onActivity?.();
    } catch (e) {
      setError(e instanceof Error ? e.message : GENERIC_ERROR_RU);
    }
  };

  const cancel = async (id: number) => {
    try {
      await api.cancel(id);
      await load();
      onActivity?.();
    } catch (e) {
      setError(String(e));
    }
  };

  return (
    <>
      <div className="card">
        <h2>Онлайн-запись</h2>
        {error && <p className="error">{error}</p>}
        <div className="grid2">
          <div>
            {doctorView && ownDoctor ? (
              <>
                <label>Врач</label>
                <p className="profile-meta">
                  {ownDoctor.full_name} — {ownDoctor.specialization}
                </p>
              </>
            ) : (
              <>
                <label>Врач</label>
                <select value={doctorId} onChange={(e) => setDoctorId(Number(e.target.value))}>
                  {doctors.map((d) => (
                    <option key={d.id} value={d.id}>
                      {d.full_name} — {d.specialization}
                    </option>
                  ))}
                </select>
              </>
            )}
            <button type="button" className="ghost" onClick={loadSlots}>
              Обновить свободные окна
            </button>
            {slots.length === 0 && (
              <p className="muted">
                {doctorView
                  ? "Нет свободных окон — добавьте их в разделе «Расписание»."
                  : "Нет свободных окон — врач должен добавить их в разделе «Расписание»."}
              </p>
            )}
            <label>Слот</label>
            <select value={slot} onChange={(e) => setSlot(e.target.value)} disabled={!slots.length}>
              {slots.map((s) => (
                <option key={s.starts_at} value={s.starts_at}>
                  {formatDateTime(s.starts_at)}
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
            <button
              type="button"
              className="primary"
              onClick={book}
              disabled={!slot || (staffView && !patientName.trim())}
            >
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
              {!doctorView && <th>Врач</th>}
              <th>Статус</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {appointments.map((a) => (
              <tr key={a.id}>
                <td>{formatDateTime(a.starts_at)}</td>
                {staffView && <td>{a.patient_name ?? "—"}</td>}
                {!doctorView && (
                  <td>
                    {a.doctor_name} ({a.specialization})
                  </td>
                )}
                <td>
                  <StatusBadge status={a.status} />
                </td>
                <td>
                  {a.status === "booked" && (
                    <button type="button" className="ghost danger" onClick={() => cancel(a.id)}>
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
