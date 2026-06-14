import { useCallback, useEffect, useMemo, useState } from "react";
import { api, Appointment, Doctor, FreeSlot, PatientBrief, User } from "../../api";
import { GENERIC_ERROR_RU, SLOT_LOOKAHEAD_DAYS } from "../../constants";
import { addDaysIso, formatDateTime, todayIsoDate } from "../../utils/datetime";
import {
  doctorOptions,
  patientOptions as buildPatientOptions,
  slotOptions,
} from "../../utils/pickerOptions";
import { isAdmin, isDoctor, isStaff } from "../../utils/roles";
import { validateBookForm } from "../../utils/validation";
import { OptionPicker } from "../ui/OptionPicker";
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
  const [doctorId, setDoctorId] = useState(0);
  const [slot, setSlot] = useState("");
  const [note, setNote] = useState("");
  const [patientName, setPatientName] = useState("");
  const [error, setError] = useState("");
  const [search, setSearch] = useState("");
  const [slotsLoading, setSlotsLoading] = useState(false);

  const staffView = isStaff(user);
  const doctorView = isDoctor(user);
  const adminView = isAdmin(user);
  const ownDoctor = doctors.find((d) => d.user_id === user.id);
  const activeDoctorId = doctorView && ownDoctor ? ownDoctor.id : doctorId;

  const doctorPickerOptions = useMemo(() => doctorOptions(doctors), [doctors]);
  const slotPickerOptions = useMemo(() => slotOptions(slots), [slots]);
  const patientPickerOptions = useMemo(
    () => buildPatientOptions(patients.map((p) => p.full_name)),
    [patients],
  );

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

  const loadSlots = useCallback(async () => {
    if (!activeDoctorId) {
      setSlots([]);
      setSlot("");
      return;
    }
    setSlotsLoading(true);
    try {
      const from = todayIsoDate();
      const to = addDaysIso(new Date(), SLOT_LOOKAHEAD_DAYS);
      const s = await api.freeSlots(activeDoctorId, from, to);
      setSlots(s);
      if (s.length) setSlot(s[0].starts_at);
      else setSlot("");
    } catch (e) {
      console.error(e);
      setSlots([]);
      setSlot("");
    } finally {
      setSlotsLoading(false);
    }
  }, [activeDoctorId]);

  useEffect(() => {
    loadSlots().catch(console.error);
  }, [loadSlots]);

  const book = async () => {
    setError("");
    const validationError = validateBookForm({
      slot,
      note,
      patientName,
      staffView,
    });
    if (validationError) {
      setError(validationError);
      return;
    }
    try {
      if (staffView) {
        await api.assign({
          patient_name: patientName.trim(),
          doctor_id: activeDoctorId,
          starts_at: slot,
          note,
        });
      } else {
        await api.book({ doctor_id: activeDoctorId, starts_at: slot, note });
      }
      setPatientName("");
      setNote("");
      await load();
      await loadSlots();
      onActivity?.();
    } catch (e) {
      setError(e instanceof Error ? e.message : GENERIC_ERROR_RU);
    }
  };

  const cancel = async (id: number) => {
    try {
      await api.cancel(id);
      await load();
      await loadSlots();
      onActivity?.();
    } catch (e) {
      setError(e instanceof Error ? e.message : GENERIC_ERROR_RU);
    }
  };

  const listTitle = adminView ? "Общие записи" : "Мои записи";

  return (
    <>
      <div className="card">
        <h2>Онлайн-запись</h2>
        {error && <p className="error">{error}</p>}
        <div className="form-stack">
          {!doctorView && (
            <>
              <label>Врач</label>
              <OptionPicker
                options={doctorPickerOptions}
                value={String(doctorId)}
                onChange={(id) => setDoctorId(Number(id))}
                placeholder="Выберите врача"
              />
            </>
          )}
          {slotsLoading && <p className="muted">Загрузка свободных окон…</p>}
          {!slotsLoading && slots.length === 0 && (
            <p className="muted">
              {doctorView
                ? "Нет свободных окон — добавьте их в разделе «Расписание»."
                : "Нет свободных окон — врач должен добавить их в разделе «Расписание»."}
            </p>
          )}
          <label>Слот</label>
          <OptionPicker
            options={slotPickerOptions}
            value={slot}
            onChange={setSlot}
            placeholder="Выберите время"
            disabled={!slots.length}
            emptyHint="Нет свободных окон"
          />
          {staffView && (
            <>
              <label>ФИО пациента</label>
              <OptionPicker
                options={patientPickerOptions}
                value={patientName}
                onChange={setPatientName}
                placeholder="Выберите пациента"
                emptyHint="Пациент не найден"
              />
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
      <div className="card">
        <h2>{listTitle}</h2>
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
              <th>Комментарий</th>
              <th>Статус</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {appointments.length === 0 && (
              <tr>
                <td colSpan={adminView ? 6 : 5} className="muted">
                  Нет записей
                </td>
              </tr>
            )}
            {appointments.map((a) => (
              <tr key={a.id}>
                <td>{formatDateTime(a.starts_at)}</td>
                {staffView && <td>{a.patient_name ?? "—"}</td>}
                {!doctorView && (
                  <td>
                    {a.doctor_name} ({a.specialization})
                  </td>
                )}
                <td>{a.note?.trim() ? a.note : "—"}</td>
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
