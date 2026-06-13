import { useEffect, useState } from "react";
import { api, User } from "../../api";
import {
  GENERIC_ERROR_RU,
  OTHER_SPECIALIZATION,
} from "../../constants";
import { RoleBadge } from "../ui/RoleBadge";

interface ProfilePanelProps {
  user: User;
  onUpdate: (u: User) => void;
}

function resolveSpecializationSelect(current: string, options: string[]): string {
  if (!current) return "";
  if (options.includes(current)) return current;
  return OTHER_SPECIALIZATION;
}

export function ProfilePanel({ user, onUpdate }: ProfilePanelProps) {
  const [fullName, setFullName] = useState(user.full_name ?? "");
  const [phone, setPhone] = useState(user.phone ?? "");
  const [specializations, setSpecializations] = useState<string[]>([]);
  const [specialization, setSpecialization] = useState("");
  const [customSpecialization, setCustomSpecialization] = useState("");
  const [msg, setMsg] = useState("");
  const [error, setError] = useState("");

  const isDoctor = user.role === "doctor";

  useEffect(() => {
    if (!isDoctor) return;
    api
      .specializations()
      .then((items) => {
        setSpecializations(items);
        const current = user.specialization ?? "";
        const selected = resolveSpecializationSelect(current, items);
        setSpecialization(selected);
        if (selected === OTHER_SPECIALIZATION) {
          setCustomSpecialization(current);
        }
      })
      .catch(console.error);
  }, [isDoctor, user.specialization]);

  const save = async () => {
    setError("");
    try {
      const payload: Record<string, unknown> = { full_name: fullName, phone };
      if (isDoctor) {
        payload.specialization =
          specialization === OTHER_SPECIALIZATION
            ? customSpecialization.trim()
            : specialization;
      }
      const u = await api.updateProfile(payload);
      onUpdate(u);
      setMsg("Профиль сохранён");
    } catch (e) {
      setError(e instanceof Error ? e.message : GENERIC_ERROR_RU);
    }
  };

  return (
    <div className="card">
      <h2>Профиль</h2>
      <p className="muted profile-meta">
        {user.email} · роль: <RoleBadge role={user.role} />
      </p>
      {msg && <p className="muted">{msg}</p>}
      {error && <p className="error">{error}</p>}
      <label>ФИО</label>
      <input value={fullName} onChange={(e) => setFullName(e.target.value)} />
      <label>Телефон</label>
      <input value={phone} onChange={(e) => setPhone(e.target.value)} />
      {isDoctor && (
        <>
          <label>Специальность</label>
          <select
            value={specialization}
            onChange={(e) => setSpecialization(e.target.value)}
          >
            <option value="">Выберите специальность</option>
            {specializations.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
            <option value={OTHER_SPECIALIZATION}>Другое</option>
          </select>
          {specialization === OTHER_SPECIALIZATION && (
            <>
              <label>Своя специальность</label>
              <input
                value={customSpecialization}
                onChange={(e) => setCustomSpecialization(e.target.value)}
              />
            </>
          )}
        </>
      )}
      <button type="button" className="primary" onClick={save}>
        Сохранить
      </button>
    </div>
  );
}
