import StatCard from '../components/StatCard'
import ChartComponent from '../components/ChartComponent'
import PredictionCard from '../components/PredictionCard'
import {
  energyStats,
  energyConsumptionOverTime,
  machineEfficiencyComparison,
  predictionSummaries,
} from '../data/dummyData'
import '../styles/dashboard.css'
import '../styles/cards.css'

function Home() {
  const lineLabels = energyConsumptionOverTime.map((p) => p.time)
  const lineData = energyConsumptionOverTime.map((p) => p.value)

  const barLabels = machineEfficiencyComparison.map((m) => m.name)
  const barData = machineEfficiencyComparison.map((m) => m.efficiency)

  return (
    <div className="dashboard-page">
      <section className="dashboard-header">
        <div>
          <h2>Energy Overview</h2>
          <p className="dashboard-subtitle">
            Live energy performance across all critical machines.
          </p>
        </div>
      </section>

      <section className="stat-grid">
        <StatCard title="Total Energy Consumption" value={energyStats.totalConsumption} />
        <StatCard title="Average Efficiency" value={energyStats.averageEfficiency} />
        <StatCard title="Total Energy Cost" value={energyStats.totalCost} />
        <StatCard
          title="Total Anomalies Detected"
          value={energyStats.totalAnomalies}
          subtitle="last 7 days"
        />
      </section>

      <section className="charts-grid">
        <ChartComponent
          title="Energy Consumption Over Time"
          type="line"
          labels={lineLabels}
          datasetLabel="MWh"
          data={lineData}
          color="#2563eb"
        />
        <ChartComponent
          title="Machine Efficiency Comparison"
          type="bar"
          labels={barLabels}
          datasetLabel="Efficiency %"
          data={barData}
          color="#0ea5e9"
        />
      </section>

      <section className="predictions-section">
        <div className="predictions-header">
          <h2>AI Prediction Summary</h2>
          <p className="dashboard-subtitle">
            ML-based forecasts for cost, anomalies, and efficiency per machine.
          </p>
        </div>
        <div className="prediction-grid">
          {predictionSummaries.map((prediction) => (
            <div key={prediction.id} className="prediction-summary-card">
              <div className="prediction-summary-header">
                <h3>{prediction.machineName}</h3>
                <span
                  className={`status-pill ${
                    prediction.status === 'Anomaly' ? 'status-pill-danger' : 'status-pill-success'
                  }`}
                >
                  {prediction.status}
                </span>
              </div>
              <div className="prediction-summary-body">
                <div>
                  <p className="prediction-summary-label">Predicted Cost</p>
                  <p className="prediction-summary-value">{prediction.predictedCost}</p>
                </div>
                <div>
                  <p className="prediction-summary-label">Efficiency Score</p>
                  <p className="prediction-summary-value">{prediction.efficiencyScore}</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  )
}

export default Home

