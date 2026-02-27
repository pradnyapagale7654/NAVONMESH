import React, { useEffect, useState } from "react";
import { getAlerts } from "../services/api";
import "../styles/alerts.css";
function Alerts() {

  const [alerts, setAlerts] = useState([]);

  useEffect(() => {

    load();

  }, []);

  const load = async () => {

    const res = await getAlerts();

    setAlerts(res.data);

  };

  return (
    <div>

      <h3>Alerts</h3>

      {alerts.map((a, i) => (

        <div key={i}
          style={{
            border: "1px solid red",
            padding: 10,
            margin: 10
          }}
        >

          {a.Machine_ID} — {a.message}

        </div>

      ))}

    </div>
  );
}

export default Alerts;