import React, { useEffect, useState } from "react";
import { getAnalytics } from "../services/api";
import "../styles/analytics.css";
function Analytics() {

  const [data, setData] = useState({});

  useEffect(() => {

    load();

  }, []);

  const load = async () => {

    const res = await getAnalytics();

    setData(res.data);

  };

  return (
    <div>

      <h3>Analytics</h3>

      <p>Total Energy: {data.total_energy_kWh} kWh</p>

      <p>Average Power: {data.avg_power_kW} kW</p>

      <p>Average Load: {data.avg_load_percent}%</p>

    </div>
  );
}

export default Analytics;