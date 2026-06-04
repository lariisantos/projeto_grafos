// Paleta canônica por região — espelhada em src/viz.py (Python) para
// garantir conformidade visual entre o front React e as saídas estáticas.
export const CORES = {
  Nordeste:     '#E63946',
  Sudeste:      '#457B9D',
  Sul:          '#2A9D8F',
  Norte:        '#E9C46A',
  'Centro-Oeste': '#F4A261',
}

export const CORES_TIPO = {
  Regional:       '#A8DADC',
  'Hub regional': '#457B9D',
  'Hub nacional': '#E63946',
}

// tooltip escuro padrão usado em todos os charts
export function TooltipBox({ active, payload, label, formatter }) {
  if (!active || !payload?.length) return null
  return (
    <div style={{
      background: 'rgba(7,17,31,0.97)',
      border: '1px solid rgba(99,179,237,0.3)',
      borderRadius: 12,
      padding: '10px 14px',
      boxShadow: '0 20px 40px rgba(0,0,0,0.5)',
      fontSize: 13,
      minWidth: 140,
    }}>
      {label != null && (
        <p style={{ color: '#f0f9ff', fontWeight: 800, marginBottom: 6, fontSize: 14 }}>{label}</p>
      )}
      {payload.map((entry, i) => (
        <p key={i} style={{ color: entry.color ?? '#e5eefc', marginTop: 3 }}>
          <span style={{ color: '#94a3b8' }}>{entry.name}: </span>
          <strong style={{ color: entry.color ?? '#f0f9ff' }}>
            {formatter ? formatter(entry) : entry.value}
          </strong>
        </p>
      ))}
    </div>
  )
}
