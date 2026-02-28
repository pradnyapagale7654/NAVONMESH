export const energyStats = {
  totalConsumption: '1,250 MWh',
  averageEfficiency: '92.4%',
  totalCost: '$342,000',
  totalAnomalies: 18,
}

export const energyConsumptionOverTime = [
  { time: 'Mon', value: 180 },
  { time: 'Tue', value: 195 },
  { time: 'Wed', value: 210 },
  { time: 'Thu', value: 190 },
  { time: 'Fri', value: 220 },
  { time: 'Sat', value: 205 },
  { time: 'Sun', value: 198 },
]

export const machineEfficiencyComparison = [
  { name: 'Press-01', efficiency: 94 },
  { name: 'Lathe-02', efficiency: 88 },
  { name: 'Cutter-03', efficiency: 91 },
  { name: 'Welder-04', efficiency: 86 },
  { name: 'Mixer-05', efficiency: 95 },
]

export const predictionSummaries = [
  {
    id: 1,
    machineName: 'Press-01',
    status: 'Normal',
    predictedCost: '$12,400',
    efficiencyScore: 95,
  },
  {
    id: 2,
    machineName: 'Lathe-02',
    status: 'Anomaly',
    predictedCost: '$18,900',
    efficiencyScore: 82,
  },
  {
    id: 3,
    machineName: 'Cutter-03',
    status: 'Normal',
    predictedCost: '$9,750',
    efficiencyScore: 93,
  },
]

export const dummyAnalysisResult = {
  anomalyStatus: 'Low Anomaly Risk',
  predictedCost: '$15,200 / month',
  efficiencyScore: 89,
  energyWasted: '3.8%',
}

