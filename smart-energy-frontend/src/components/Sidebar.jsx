import { NavLink } from 'react-router-dom'
import '../styles/sidebar.css'

function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-section">
        <p className="sidebar-section-title">Overview</p>
        <nav className="sidebar-nav">
          <NavLink
            to="/"
            end
            className={({ isActive }) =>
              `sidebar-link ${isActive ? 'sidebar-link-active' : ''}`
            }
          >
            <span className="sidebar-icon">📊</span>
            <span>Dashboard</span>
          </NavLink>
          <NavLink
            to="/analysis"
            className={({ isActive }) =>
              `sidebar-link ${isActive ? 'sidebar-link-active' : ''}`
            }
          >
            <span className="sidebar-icon">⚙️</span>
            <span>Machine Analysis</span>
          </NavLink>
        </nav>
      </div>
    </aside>
  )
}

export default Sidebar

