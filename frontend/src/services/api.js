import axios from "axios";

const API = "http://127.0.0.1:8000";

export const getLive = () =>
  axios.get(`${API}/live`);

export const getAnalytics = () =>
  axios.get(`${API}/analytics`);

export const getAlerts = () =>
  axios.get(`${API}/alerts`);