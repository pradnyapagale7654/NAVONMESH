import { useState } from 'react'
import PredictionCard from '../components/PredictionCard'
import { dummyAnalysisResult } from '../data/dummyData'
import '../styles/form.css'
import '../styles/cards.css'

function MachineAnalysis() {
  const [machineName, setMachineName] = useState('')
  const [onTime, setOnTime] = useState('')
  const [offTime, setOffTime] = useState('')
  const [result, setResult] = useState(null)

  const handleSubmit = (event) => {
    event.preventDefault()
    // Simulate analysis by combining form inputs with dummy analysis result.
    const simulated = {
      ...dummyAnalysisResult,
      machineName: machineName || 'Unnamed Machine',
      onTime,
      offTime,
    }
    setResult(simulated)
  }

  return (
    <div className="analysis-page">
      <section className="analysis-header">
        <div>
          <h2>Machine Analysis</h2>
          <p className="analysis-subtitle">
            Run AI-powered diagnostics on individual machines using operating profiles.
          </p>
        </div>
      </section>

      <section className="analysis-content">
        <form className="analysis-form" onSubmit={handleSubmit}>
          <div className="form-row">
            <label htmlFor="machineName">Machine Name</label>
            <input
              id="machineName"
              type="text"
              value={machineName}
              onChange={(e) => setMachineName(e.target.value)}
              placeholder="e.g. Press-01"
            />
          </div>
          <div className="form-row-inline">
            <div className="form-row">
              <label htmlFor="onTime">Machine On Time (hours)</label>
              <input
                id="onTime"
                type="number"
                min="0"
                value={onTime}
                onChange={(e) => setOnTime(e.target.value)}
                placeholder="e.g. 16"
              />
            </div>
            <div className="form-row">
              <label htmlFor="offTime">Machine Off Time (hours)</label>
              <input
                id="offTime"
                type="number"
                min="0"
                value={offTime}
                onChange={(e) => setOffTime(e.target.value)}
                placeholder="e.g. 8"
              />
            </div>
          </div>
          <button type="submit" className="analysis-button">
            Start Analyzing
          </button>
        </form>

        {result && (
          <div className="analysis-results">
            <PredictionCard
              title="AI Prediction Result"
              items={[
                { label: 'Machine', value: result.machineName },
                { label: 'Anomaly Status', value: result.anomalyStatus },
                { label: 'Predicted Energy Cost', value: result.predictedCost },
                { label: 'Efficiency Score', value: `${result.efficiencyScore}` },
                { label: 'Energy Wasted', value: result.energyWasted },
              ]}
            />
          </div>
        )}
      </section>
    </div>
  )
}

export default MachineAnalysis

