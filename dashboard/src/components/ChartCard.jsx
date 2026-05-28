export default function ChartCard({ icon, title, sub, children, fullWidth = false }) {
  return (
    <div style={{
      background: 'rgba(15,23,42,0.82)',
      border: '1px solid rgba(148,163,184,0.16)',
      borderRadius: 22,
      overflow: 'hidden',
      backdropFilter: 'blur(18px)',
      boxShadow: '0 20px 56px rgba(0,0,0,.30)',
      transition: 'border-color .2s, box-shadow .2s',
      gridColumn: fullWidth ? '1 / -1' : undefined,
    }}
    onMouseEnter={e => {
      e.currentTarget.style.borderColor = 'rgba(148,163,184,.32)'
      e.currentTarget.style.boxShadow   = '0 28px 70px rgba(0,0,0,.38)'
    }}
    onMouseLeave={e => {
      e.currentTarget.style.borderColor = 'rgba(148,163,184,.16)'
      e.currentTarget.style.boxShadow   = '0 20px 56px rgba(0,0,0,.30)'
    }}
    >
      {/* header */}
      <div style={{
        padding: '18px 22px 14px',
        borderBottom: '1px solid rgba(148,163,184,.14)',
        display: 'flex', gap: 12, alignItems: 'flex-start',
      }}>
        <span style={{ fontSize: 22, flexShrink: 0, marginTop: 2 }}>{icon}</span>
        <div>
          <h3 style={{ fontSize: 15, fontWeight: 800, color: '#f0f9ff', lineHeight: 1.3 }}>
            {title}
          </h3>
          {sub && (
            <p style={{ fontSize: 12, color: '#94a3b8', marginTop: 3, lineHeight: 1.4 }}>{sub}</p>
          )}
        </div>
      </div>
      {/* body */}
      <div style={{ padding: '16px 8px 12px' }}>
        {children}
      </div>
    </div>
  )
}
