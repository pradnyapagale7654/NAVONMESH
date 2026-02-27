import React, { useEffect, useState } from "react";
import { getLive } from "../services/api";
import LiveStatusCard from "../components/LiveStatusCard";
import "../styles/Dashboard.css";
function Dashboard() {

  const [data, setData] = useState([]);

  useEffect(() => {

    load();

    const interval = setInterval(load, 5000);

    return () => clearInterval(interval);

  }, []);

  const load = async () => {

    const res = await getLive();

    setData(res.data);

  };

  return (
    <div>

      <h3>Live Machine Status</h3>

      {data.map((m, i) => (

        <LiveStatusCard key={i} machine={m} />

      ))}

    </div>
  );
}

export default Dashboard;