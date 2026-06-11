import { useState } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell, LabelList,
} from 'recharts'
import { CORES } from '../constants'
import { FilterChips } from '../components/Filters'

const AXIS = { fill: '#94a3b8', fontSize: 10 }
const GRID = 'rgba(148,163,184,0.08)'
const ACCENT = '#a78bfa'

const METRICAS = [
  { value: 'ordem',      chip: 'Aeroportos', label: 'Aeroportos por região', fmt: v => v },
  { value: 'tamanho',    chip: 'Arestas',    label: 'Arestas internas',      fmt: v => v },
  { value: 'grau_medio', chip: 'Grau médio', label: 'Grau médio por região', fmt: v => v.toFixed(1) },
]

function MiniBar({ data, dataKey, label, fmt, height = 185 }) {
  return (
    <div>
      <p style={{ color: '#94a3b8', fontSize: 12, marginBottom: 6, paddingLeft: 6 }}>{label}</p>
      <ResponsiveContainer width="100%" height={height}>
        <BarChart data={data} margin={{ top: 28, right: 12, left: 0, bottom: 32 }}>
          <CartesianGrid vertical={false} stroke={GRID} />
          <XAxis
            dataKey="regiao"
            tick={{ ...AXIS, fontSize: 9 }}
            interval={0}
            angle={-20}
            textAnchor="end"
            height={44}
          />
          <YAxis tick={AXIS} width={28} />
          <Tooltip
            content={({ active, payload }) => {
              if (!active || !payload?.length) return null
              const d = payload[0]
              return (
                <div style={{
                  background: 'rgba(7,17,31,0.97)',
                  border: '1px solid rgba(99,179,237,0.3)',
                  borderRadius: 10, padding: '8px 12px', fontSize: 12,
                }}>
                  <p style={{ color: CORES[d.payload.regiao], fontWeight: 700 }}>{d.payload.regiao}</p>
                  <p style={{ color: '#e5eefc', marginTop: 3 }}>
                    {label}: <strong>{fmt(d.value)}</strong>
                  </p>
                </div>
              )
            }}
          />
          <Bar dataKey={dataKey} radius={[5, 5, 0, 0]} maxBarSize={44}>
            {data.map(entry => (
              <Cell key={entry.regiao} fill={CORES[entry.regiao] ?? '#64748b'} />
            ))}
            <LabelList
              dataKey={dataKey}
              position="top"
              formatter={fmt}
              style={{ fill: '#cbd5e1', fontSize: 10, fontWeight: 700 }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

/* Comparação entre regiões. Filtro: qual indicador exibir (ou todos). */
export default function RegioesChart({ data }) {
  const [metrica, setMetrica] = useState('todas')
  const opcoes = [{ value: 'todas', label: 'Todas' }, ...METRICAS.map(m => ({ value: m.value, label: m.chip }))]
  const visiveis = metrica === 'todas' ? METRICAS : METRICAS.filter(m => m.value === metrica)
  const unica = metrica !== 'todas'

  return (
    <div>
      <FilterChips label="Indicador" accent={ACCENT} options={opcoes} value={metrica} onChange={setMetrica} />
      <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 10 }}>
        {visiveis.map(m => (
          <MiniBar
            key={m.value}
            data={data}
            dataKey={m.value}
            label={m.label}
            fmt={m.fmt}
            height={unica ? 320 : 185}
          />
        ))}
      </div>
    </div>
  )
}
