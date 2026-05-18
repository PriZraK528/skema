import { FormEvent, useState } from "react";
import { api, User, UserRole } from "../../api";

interface AuthScreenProps {
  onAuth: (user: User, access: string, refresh: string) => void;
}

export function AuthScreen({ onAuth }: AuthScreenProps) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [error, setError] = useState("");
  const [form, setForm] = useState({
    email: "",
    password: "",
    full_name: "",
    phone: "",
    role: "patient" as UserRole,
  });

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    try {
      const res =
        mode === "login"
          ? await api.login(form.email, form.password)
          : await api.register({
              email: form.email,
              password: form.password,
              full_name: form.full_name,
              phone: form.phone,
              role: form.role,
            });
      onAuth(res.user, res.access_token, res.refresh_token);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Ошибка");
    }
  };

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
                <option value="registrar">Регистратор</option>
              </select>
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
          Демо: patient@clinic.example / Password123!
        </p>
      </div>
    </div>
  );
}


