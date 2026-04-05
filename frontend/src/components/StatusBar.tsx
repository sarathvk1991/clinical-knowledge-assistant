import { useEffect, useState } from "react";

export default function StatusBar() {
  const [healthy, setHealthy] = useState<boolean | null>(null);

  useEffect(() => {
    const healthUrl = import.meta.env.VITE_API_BASE_URL
      ? `${import.meta.env.VITE_API_BASE_URL}/health`
      : "/health";

    fetch(healthUrl)
      .then((r) => setHealthy(r.ok))
      .catch(() => setHealthy(false));
  }, []);

  return (
    <div className="status-bar">
      <span
        className={`status-dot ${healthy === true ? "green" : healthy === false ? "red" : "gray"}`}
      />
      <span>
        Backend: {healthy === true ? "Connected" : healthy === false ? "Disconnected" : "Checking..."}
      </span>
    </div>
  );
}
