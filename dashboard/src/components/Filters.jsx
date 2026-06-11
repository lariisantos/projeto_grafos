/**
 * Controles de filtro padronizados (chips/segmented) usados por cada gráfico.
 * Cada gráfico tem seu próprio filtro, contextual ao que mostra — este
 * componente só padroniza a aparência (combina com a toolbar do grafo).
 */

/* Barra de filtro: rótulo + chips de seleção única. */
export function FilterChips({ options, value, onChange, accent = '#3b82f6', label }) {
  return (
    <div style={{
      display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap',
      padding: '0 14px 12px',
    }}>
      {label && (
        <span style={{
          fontSize: 10.5, fontWeight: 800, color: '#64748b',
          textTransform: 'uppercase', letterSpacing: '.07em',
        }}>{label}</span>
      )}
      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
        {options.map(opt => {
          const v   = typeof opt === 'object' ? opt.value : opt
          const lbl = typeof opt === 'object' ? opt.label : opt
          const active = v === value
          return (
            <button
              key={String(v)}
              onClick={() => onChange(v)}
              style={{
                border: `1px solid ${active ? accent : 'rgba(148,163,184,.22)'}`,
                background: active ? `${accent}26` : 'rgba(30,41,59,.55)',
                color: active ? '#f0f9ff' : '#94a3b8',
                borderRadius: 999, padding: '4px 12px', cursor: 'pointer',
                fontSize: 11.5, fontWeight: 700, fontFamily: 'inherit',
                whiteSpace: 'nowrap', transition: 'all .15s',
              }}
            >
              {lbl}
            </button>
          )
        })}
      </div>
    </div>
  )
}

/* Ordem canônica das regiões (espelha a paleta em constants.jsx). */
const ORDEM_REGIAO = ['Nordeste', 'Sudeste', 'Sul', 'Norte', 'Centro-Oeste']

/* Deriva ['Todas', ...regiões presentes] na ordem canônica. */
export function opcoesRegiao(items, key = 'regiao') {
  const presentes = new Set(items.map(it => it[key]))
  const ordenadas = ORDEM_REGIAO.filter(r => presentes.has(r))
  for (const r of presentes) if (!ordenadas.includes(r)) ordenadas.push(r)
  return ['Todas', ...ordenadas]
}

/* Encurta o rótulo de gênero p/ caber no chip, sem colidir
 * (International Movies → International · International TV Shows → International TV). */
export function rotuloGenero(g) {
  if (g === 'Todos') return 'Todos'
  return g.replace(/ TV Shows$/, ' TV').replace(/ Movies$/, '')
}
