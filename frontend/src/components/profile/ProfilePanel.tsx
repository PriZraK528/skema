import { useState } from "react";
import { api, User } from "../../api";
import { RoleBadge } from "../ui/RoleBadge";

interface ProfilePanelProps {
  user: User;
  onUpdate: (u: User) => void;
}

export function ProfilePanel({ user, onUpdate }: ProfilePanelProps) {
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
      <p className="muted profile-meta">
        {user.email} · роль: <RoleBadge role={user.role} />
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
