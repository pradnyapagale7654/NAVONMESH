import '../styles/navbar.css'

function Navbar() {
  return (
    <header className="navbar">
      <div className="navbar-left">
        <div className="navbar-logo">SE</div>
        <div>
          <h1 className="navbar-title">Smart Energy AI System</h1>
          <p className="navbar-subtitle">Industrial energy intelligence for manufacturing</p>
        </div>
      </div>
      <div className="navbar-right">
        <span className="navbar-pill">Manufacturing Plant A</span>
        <span className="navbar-user">Energy Engineer</span>
      </div>
    </header>
  )
}

export default Navbar

