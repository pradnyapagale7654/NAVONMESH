import React from "react";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";

import Dashboard from "./pages/Dashboard.jsx";
import Analytics from "./pages/Analytics.jsx";
import Alerts from "./pages/Alerts.jsx";

function App() {
  return (
    <BrowserRouter>

      <div style={{ padding: 20 }}>

        <h2>Energy Monitoring System</h2>

        <nav style={{ marginBottom: 20 }}>
          <Link to="/">Dashboard</Link> |{" "}
          <Link to="/analytics">Analytics</Link> |{" "}
          <Link to="/alerts">Alerts</Link>
        </nav>

        <Routes>

          <Route path="/" element={<Dashboard />} />

          <Route path="/analytics" element={<Analytics />} />

          <Route path="/alerts" element={<Alerts />} />

        </Routes>

      </div>

    </BrowserRouter>
  );
}

export default App;