import { useState } from 'react'

/* Cartão de métrica do hero */
export function MetricCard({ value, label, accent }) {
  const [hov, setHov] = useState(false)
  return (
    <div onMouseEnter={() => setHov(true)} onMouseLeave={() => setHov(false)} style={{
      position: 'relative', overflow: 'hidden',
      background: 'rgba(15,23,42,0.82)',
      border: `1px solid ${hov ? 'rgba(99,179,237,0.3)' : 'rgba(148,163,184,0.16)'}`,
      borderRadius: 18, padding: '20px 22px', backdropFilter: 'blur(18px)',
      boxShadow: hov ? '0 24px 60px rgba(0,0,0,.38)' : '0 12px 36px rgba(0,0,0,.28)',
      transform: hov ? 'translateY(-3px)' : 'none', transition: 'all .2s ease',
    }}>
      <div style={{ position: 'absolute', inset: '0 0 auto 0', height: 2, background: `linear-gradient(90deg, ${accent}, transparent)` }} />
      <div style={{ fontSize: 28, fontWeight: 900, letterSpacing: '-.04em', color: accent, lineHeight: 1.05 }}>{value}</div>
      <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 6, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '.07em' }}>{label}</div>
    </div>
  )
}

/* Botão de aba (sub-navegação dentro de uma parte) */
export function TabBtn({ label, active, onClick }) {
  return (
    <button onClick={onClick} style={{
      position: 'relative', border: 'none', background: 'none', cursor: 'pointer',
      color: active ? '#e5eefc' : '#94a3b8', fontFamily: 'inherit',
      fontWeight: 700, fontSize: 14, padding: '12px 24px 15px',
      borderRadius: '10px 10px 0 0', marginBottom: -1,
      transition: 'color .18s, background .18s',
      backgroundColor: active ? 'rgba(255,255,255,.04)' : 'transparent',
    }}>
      {label}
      {active && <span style={{ position: 'absolute', bottom: -1, left: 0, right: 0, height: 3, borderRadius: '3px 3px 0 0', background: '#3b82f6' }} />}
    </button>
  )
}

export function SectionHeader({ title, sub }) {
  return (
    <div style={{ marginBottom: 24 }}>
      <h2 style={{ fontSize: 22, fontWeight: 800, color: '#f0f9ff', letterSpacing: '-.03em' }}>{title}</h2>
      {sub && <p style={{ color: '#94a3b8', fontSize: 13, marginTop: 5 }}>{sub}</p>}
    </div>
  )
}

/**
 * Linha de gráficos RELACIONADOS.
 * O banner explicita a relação entre os dois gráficos (requisito do projeto:
 * apenas gráficos com relação ficam na mesma linha, e a relação fica no texto).
 */
export function RelationRow({ eyebrow, accent, title, relation, children, cols }) {
  const gridTemplateColumns = cols === 1 ? '1fr' : 'repeat(auto-fit, minmax(380px, 1fr))'
  return (
    <section style={{ marginBottom: 30 }}>
      <div style={{
        background: 'rgba(15,23,42,0.55)',
        border: '1px solid rgba(148,163,184,.14)',
        borderLeft: `4px solid ${accent}`,
        borderRadius: 14, padding: '14px 18px', marginBottom: 16,
      }}>
        <span style={{
          display: 'inline-block', fontSize: 10.5, fontWeight: 800, letterSpacing: '.09em',
          textTransform: 'uppercase', color: accent, marginBottom: 4,
        }}>
          {eyebrow}
        </span>
        <h3 style={{ fontSize: 16, fontWeight: 800, color: '#f0f9ff', marginBottom: 6, letterSpacing: '-.02em' }}>{title}</h3>
        <p style={{ fontSize: 13, color: '#cbd5e1', lineHeight: 1.6, margin: 0 }}>
          <strong style={{ color: '#e2e8f0' }}>Como ler em conjunto:</strong> {relation}
        </p>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns, gap: 18, alignItems: 'stretch' }}>
        {children}
      </div>
    </section>
  )
}

/* Caixa de descrição/insight para visualizações que ocupam a linha inteira */
export function InsightBanner({ accent, title, children }) {
  return (
    <div style={{
      background: `${accent}0f`, border: `1px solid ${accent}33`,
      borderRadius: 16, padding: '14px 18px', marginBottom: 18,
      display: 'flex', gap: 12, alignItems: 'flex-start',
    }}>
      <span style={{
        flexShrink: 0, fontSize: 11, fontWeight: 900, letterSpacing: '.05em',
        textTransform: 'uppercase', color: accent, marginTop: 2,
      }}>
        {title}
      </span>
      <p style={{ fontSize: 13, color: '#cbd5e1', lineHeight: 1.6, margin: 0 }}>{children}</p>
    </div>
  )
}
