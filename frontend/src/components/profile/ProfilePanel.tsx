import { useEffect, useState } from "react";
import { api, User } from "../../api";
import {
  GENERIC_ERROR_RU,
  OTHER_SPECIALIZATION,
} from "../../constants";
import { validateProfileForm, normalizePhone } from "../../utils/validation";
import { specializationOptions } from "../../utils/pickerOptions";
import { OptionPicker } from "../ui/OptionPicker";
import { RoleBadge } from "../ui/RoleBadge";

interface ProfilePanelProps {
  user: User;
  onUpdate: (u: User) => void;
  onLogout: () => void;
}

function resolveSpecializationSelect(current: string, options: string[]): string {
  if (!current) return "";
  if (options.includes(current)) return current;
  return OTHER_SPECIALIZATION;
}

export function ProfilePanel({ user, onUpdate, onLogout }: ProfilePanelProps) {
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
    setMsg("");
    const validationError = validateProfileForm({
      fullName,
      phone,
      isDoctor,
      specialization,
      customSpecialization,
    });
    if (validationError) {
      setError(validationError);
      return;
    }
    try {
      const payload: Record<string, unknown> = {
        full_name: fullName.trim(),
        phone: normalizePhone(phone) ?? phone,
      };
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
      <input
        value={phone}
        onChange={(e) => setPhone(e.target.value)}
        placeholder="+79001234567 или 89001234567"
      />
      {isDoctor && (
        <>
          <label>Специальность</label>
          <OptionPicker
            options={specializationOptions(specializations)}
            value={specialization}
            onChange={setSpecialization}
            placeholder="Выберите специальность"
          />
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
      <div className="profile-actions">
        <button type="button" className="primary" onClick={save}>
          Сохранить
        </button>
        <button type="button" className="ghost danger" onClick={onLogout}>
          Выход
        </button>
      </div>
    </div>
  );
}
