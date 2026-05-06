import React from "react";
import ReactDOM from "react-dom/client";

function App() {
  return (
    <div style={{ fontFamily: "system-ui, sans-serif", padding: 24 }}>
      <h1>Clinic</h1>
      <p>Сервис управления онлайн-записями пациентов (каркас).</p>
      <p>API: {import.meta.env.VITE_API_BASE_URL ?? "(not set)"}</p>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
