import '../styles/cards.css'

function StatCard({ title, value, subtitle }) {
  return (
    <div className="stat-card">
      <div className="stat-card-header">
        <p className="stat-card-title">{title}</p>
      </div>
      <p className="stat-card-value">{value}</p>
      {subtitle && <p className="stat-card-subtitle">{subtitle}</p>}
    </div>
  )
}

export default StatCard

