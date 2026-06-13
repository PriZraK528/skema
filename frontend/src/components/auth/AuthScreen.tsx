import { FormEvent, useEffect, useState } from "react";
import { api, User, UserRole } from "../../api";
import {
  GENERIC_ERROR_RU,
  OTHER_SPECIALIZATION,
  SEED_PASSWORD,
  SEED_PATIENT_EMAIL,
} from "../../constants";

interface AuthScreenProps {
  onAuth: (user: User, access: string, refresh: string) => void;
}

export function AuthScreen({ onAuth }: AuthScreenProps) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [error, setError] = useState("");
  const [specializations, setSpecializations] = useState<string[]>([]);
  const [form, setForm] = useState({
    email: "",
    password: "",
    full_name: "",
    phone: "",
    role: "patient" as UserRole,
    specialization: "",
    customSpecialization: "",
    clinicKey: "",
  });

  useEffect(() => {
    if (mode === "register") {
      api.specializations().then(setSpecializations).catch(console.error);
    }
  }, [mode]);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      const payload: Record<string, unknown> = {
        email: form.email,
        password: form.password,
        full_name: form.full_name,
        phone: form.phone,
        role: form.role,
      };
      if (form.role === "doctor") {
        payload.specialization =
          form.specialization === OTHER_SPECIALIZATION
            ? form.customSpecialization.trim()
            : form.specialization;
        payload.clinic_key = form.clinicKey.trim();
      }
      const res =
        mode === "login"
          ? await api.login(form.email, form.password)
          : await api.register(payload);
      onAuth(res.user, res.access_token, res.refresh_token);
    } catch (err) {
      setError(err instanceof Error ? err.message : GENERIC_ERROR_RU);
    }
  };

  const isDoctorRegister = mode === "register" && form.role === "doctor";

  return (
    <div className="auth-wrap">
      <div className="card">
        <div className="auth-header">
          <h1 className="brand">SKEMA</h1>
          <p className="brand-sub">Онлайн-запись пациентов</p>
        </div>
        <h2>{mode === "login" ? "Вход" : "Регистрация"}</h2>
        {error && <p className="error">{error}</p>}
        <form onSubmit={submit}>
          <label>Email</label>
          <input
            type="email"
            required
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
          <label>Пароль</label>
          <input
            type="password"
            required
            minLength={8}
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
          {mode === "register" && (
            <>
              <label>ФИО</label>
              <input
                required
                value={form.full_name}
                onChange={(e) => setForm({ ...form, full_name: e.target.value })}
              />
              <label>Телефон</label>
              <input
                required
                value={form.phone}
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
              />
              <label>Роль</label>
              <select
                value={form.role}
                onChange={(e) =>
                  setForm({ ...form, role: e.target.value as UserRole })
                }
              >
                <option value="patient">Пациент</option>
                <option value="doctor">Врач</option>
              </select>
              {isDoctorRegister && (
                <>
                  <label>Специальность</label>
                  <select
                    required
                    value={form.specialization}
                    onChange={(e) =>
                      setForm({ ...form, specialization: e.target.value })
                    }
                  >
                    <option value="">Выберите специальность</option>
                    {specializations.map((s) => (
                      <option key={s} value={s}>
                        {s}
                      </option>
                    ))}
                    <option value={OTHER_SPECIALIZATION}>Другое</option>
                  </select>
                  {form.specialization === OTHER_SPECIALIZATION && (
                    <>
                      <label>Своя специальность</label>
                      <input
                        required
                        value={form.customSpecialization}
                        onChange={(e) =>
                          setForm({ ...form, customSpecialization: e.target.value })
                        }
                        placeholder="Например, ревматолог"
                      />
                    </>
                  )}
                  <label>Ключ клиники</label>
                  <input
                    required
                    type="password"
                    value={form.clinicKey}
                    onChange={(e) => setForm({ ...form, clinicKey: e.target.value })}
                    placeholder="Выдаётся администратором клиники"
                  />
                  <p className="muted">
                    Регистрация врача доступна только с ключом клиники.
                  </p>
                </>
              )}
            </>
          )}
          <button type="submit" className="primary">
            {mode === "login" ? "Войти" : "Зарегистрироваться"}
          </button>
        </form>
        <p className="muted" style={{ marginTop: "1rem" }}>
          {mode === "login" ? "Нет аккаунта?" : "Уже есть аккаунт?"}{" "}
          <a
            href="#"
            onClick={(e) => {
              e.preventDefault();
              setMode(mode === "login" ? "register" : "login");
            }}
          >
            {mode === "login" ? "Регистрация" : "Вход"}
          </a>
        </p>
        <p className="muted" style={{ marginTop: "0.5rem" }}>
          Демо: {SEED_PATIENT_EMAIL} / {SEED_PASSWORD}
        </p>
      </div>
    </div>
  );
}
