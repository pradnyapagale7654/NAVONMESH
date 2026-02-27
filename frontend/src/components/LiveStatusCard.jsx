import React from "react";

function LiveStatusCard({ machine }) {

  return (
    <div style={{
      border: "1px solid gray",
      padding: 10,
      margin: 10,
      borderRadius: 5
    }}>

      <h4>{machine.Machine_ID}</h4>

      <p>Power: {machine.Power_kW} kW</p>

      <p>Energy: {machine.Energy_kWh} kWh</p>

      <p>Load: {machine["Load_%"]}%</p>

      <p>Time: {machine.Timestamp}</p>

    </div>
  );

}

export default LiveStatusCard;