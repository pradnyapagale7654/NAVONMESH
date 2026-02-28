import axios from 'axios'
import {
  energyStats,
  energyConsumptionOverTime,
  machineEfficiencyComparison,
  predictionSummaries,
  dummyAnalysisResult,
} from '../data/dummyData'

const apiClient = axios.create({
  baseURL: 'https://api.smart-energy.local', // placeholder
})

export function getDashboardData() {
  // This simulates an async API call using dummy data.
  return Promise.resolve({
    stats: energyStats,
    consumptionSeries: energyConsumptionOverTime,
    efficiencySeries: machineEfficiencyComparison,
    predictions: predictionSummaries,
  })
}

export function analyzeMachine(payload) {
  // In a real implementation this would call:
  // return apiClient.post('/analysis', payload)
  const response = {
    ...dummyAnalysisResult,
    machineName: payload.machineName,
    onTime: payload.onTime,
    offTime: payload.offTime,
  }
  return Promise.resolve(response)
}

export default apiClient

