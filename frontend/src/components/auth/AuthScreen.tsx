import { FormEvent, useEffect, useState } from "react";
import { api, User, UserRole } from "../../api";
import {
  GENERIC_ERROR_RU,
  MIN_PASSWORD_LENGTH,
  OTHER_SPECIALIZATION,
  SEED_ADMIN_EMAIL,
  SEED_DOCTOR_EMAIL,
  SEED_PASSWORD,
  SEED_PATIENT_EMAIL,
} from "../../constants";
import { validateRegisterForm, normalizePhone } from "../../utils/validation";
import { roleOptions, specializationOptions } from "../../utils/pickerOptions";
import { OptionPicker } from "../ui/OptionPicker";

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
    if (mode === "register") {
      const validationError = validateRegisterForm({
        email: form.email,
        password: form.password,
        fullName: form.full_name,
        phone: form.phone,
        role: form.role,
        specialization: form.specialization,
        customSpecialization: form.customSpecialization,
        clinicKey: form.clinicKey,
      });
      if (validationError) {
        setError(validationError);
        return;
      }
    } else {
      if (!form.email.trim() || !form.password) {
        setError("Укажите email и пароль");
        return;
      }
    }
    try {
      const normalizedPhone = mode === "register" ? normalizePhone(form.phone) : null;
      const payload: Record<string, unknown> = {
        email: form.email.trim(),
        password: form.password,
        full_name: form.full_name.trim(),
        phone: normalizedPhone ?? form.phone,
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
            minLength={MIN_PASSWORD_LENGTH}
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
                placeholder="+79001234567 или 89001234567"
                onChange={(e) => setForm({ ...form, phone: e.target.value })}
              />
              <label>Роль</label>
              <OptionPicker
                options={roleOptions()}
                value={form.role}
                onChange={(role) => setForm({ ...form, role: role as UserRole })}
                searchable={false}
              />
              {isDoctorRegister && (
                <>
                  <label>Специальность</label>
                  <OptionPicker
                    options={specializationOptions(specializations)}
                    value={form.specialization}
                    onChange={(specialization) => setForm({ ...form, specialization })}
                    placeholder="Выберите специальность"
                  />
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
          Демо (пароль {SEED_PASSWORD}): {SEED_PATIENT_EMAIL}, {SEED_DOCTOR_EMAIL},{" "}
          {SEED_ADMIN_EMAIL}
        </p>
      </div>
    </div>
  );
}
