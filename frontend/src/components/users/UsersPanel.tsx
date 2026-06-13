import { useEffect, useState } from "react";
import { api, User } from "../../api";
import { ROLE_LABELS } from "../../constants";

export function UsersPanel() {
  const [users, setUsers] = useState<User[]>([]);
  const [q, setQ] = useState("");

  useEffect(() => {
    api.users(q || undefined).then((r) => setUsers(r.items));
  }, [q]);

  return (
    <div className="card">
      <h2>Пользователи</h2>
      <input placeholder="Поиск..." value={q} onChange={(e) => setQ(e.target.value)} />
      <table>
        <thead>
          <tr>
            <th>Email</th>
            <th>Имя</th>
            <th>Роль</th>
            <th>Специальность</th>
          </tr>
        </thead>
        <tbody>
          {users.map((u) => (
            <tr key={u.id}>
              <td>{u.email}</td>
              <td>{u.full_name ?? "—"}</td>
              <td>{ROLE_LABELS[u.role] ?? u.role}</td>
              <td>{u.role === "doctor" ? u.specialization ?? "—" : "—"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
