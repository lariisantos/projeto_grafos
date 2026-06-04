/**
 * Card padrão de um gráfico do dashboard.
 *
 * Props:
 *  - title    : título do gráfico
 *  - sub      : subtítulo curto (o que está no eixo / como ler)
 *  - tag      : etiqueta opcional ("Exploratória" | "Explanatória")
 *  - accent   : cor de destaque (faixa superior + tag)
 *  - insight  : texto de leitura analítica — o que o gráfico revela p/ o projeto
 *  - children : o gráfico em si
 *  - fullWidth: ocupa a linha inteira do grid
 */
export default function ChartCard({
  title, sub, tag, accent = '#3b82f6', insight, children, fullWidth = false,
}) {
  return (
    <div
      style={{
        position: 'relative',
        display: 'flex', flexDirection: 'column',
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
        e.currentTarget.style.boxShadow = '0 28px 70px rgba(0,0,0,.38)'
      }}
      onMouseLeave={e => {
        e.currentTarget.style.borderColor = 'rgba(148,163,184,.16)'
        e.currentTarget.style.boxShadow = '0 20px 56px rgba(0,0,0,.30)'
      }}
    >
      {/* faixa de destaque no topo */}
      <div style={{ height: 3, background: `linear-gradient(90deg, ${accent}, transparent)` }} />

      {/* header */}
      <div style={{
        padding: '18px 22px 14px',
        borderBottom: '1px solid rgba(148,163,184,.14)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap', marginBottom: sub ? 4 : 0 }}>
          <h3 style={{ fontSize: 15, fontWeight: 800, color: '#f0f9ff', lineHeight: 1.3 }}>
            {title}
          </h3>
          {tag && (
            <span style={{
              fontSize: 10, fontWeight: 800, letterSpacing: '.06em', textTransform: 'uppercase',
              color: accent, background: `${accent}1f`, border: `1px solid ${accent}55`,
              padding: '2px 9px', borderRadius: 999, whiteSpace: 'nowrap',
            }}>
              {tag}
            </span>
          )}
        </div>
        {sub && (
          <p style={{ fontSize: 12, color: '#94a3b8', lineHeight: 1.4 }}>{sub}</p>
        )}
      </div>

      {/* body — gráfico */}
      <div style={{ padding: '16px 8px 6px', flex: 1 }}>
        {children}
      </div>

      {/* insight — leitura analítica */}
      {insight && (
        <div style={{
          margin: '8px 14px 16px',
          padding: '12px 14px',
          background: `${accent}0f`,
          border: `1px solid ${accent}33`,
          borderRadius: 14,
          display: 'flex', gap: 10, alignItems: 'flex-start',
        }}>
          <span style={{
            flexShrink: 0, marginTop: 1,
            fontSize: 11, fontWeight: 900, letterSpacing: '.04em',
            color: accent, textTransform: 'uppercase',
          }}>
            Insight
          </span>
          <p style={{ fontSize: 12.5, color: '#cbd5e1', lineHeight: 1.55, margin: 0 }}>
            {insight}
          </p>
        </div>
      )}
    </div>
  )
}
