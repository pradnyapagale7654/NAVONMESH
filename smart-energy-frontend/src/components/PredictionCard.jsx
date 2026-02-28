import '../styles/cards.css'

function PredictionCard({ title, items }) {
  return (
    <div className="prediction-card">
      <div className="prediction-card-header">
        <h3>{title}</h3>
      </div>
      <div className="prediction-card-body">
        {items.map((item) => (
          <div key={item.label} className="prediction-row">
            <span className="prediction-label">{item.label}</span>
            <span className="prediction-value">{item.value}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

export default PredictionCard

