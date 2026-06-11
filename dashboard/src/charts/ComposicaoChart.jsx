import { useState, useMemo } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, Legend, ResponsiveContainer,
} from 'recharts'
import { CORES_TIPO, TooltipBox } from '../constants'
import { FilterChips, opcoesRegiao } from '../components/Filters'

const AXIS = { fill: '#94a3b8', fontSize: 10 }
const GRID = 'rgba(148,163,184,0.08)'
const TIPOS = ['Hub regional', 'Hub nacional']
const ACCENT = '#2dd4bf'

function CustomLegend({ payload }) {
  return (
    <div style={{ display: 'flex', gap: 16, justifyContent: 'center', marginTop: 4 }}>
      {payload.map(p => (
        <span key={p.value} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: '#cbd5e1' }}>
          <span style={{ width: 12, height: 12, borderRadius: 3, background: p.color, display: 'inline-block' }} />
          {p.value}
        </span>
      ))}
    </div>
  )
}

/* Composição das conexões por aeroporto. Filtro: região (subconjunto de aeroportos). */
export default function ComposicaoChart({ data }) {
  const [regiao, setRegiao] = useState('Todas')
  const opcoes = useMemo(() => opcoesRegiao(data), [data])
  const filtrada = useMemo(
    () => (regiao === 'Todas' ? data : data.filter(d => d.regiao === regiao)),
    [data, regiao],
  )

  return (
    <div>
      <FilterChips label="Região" accent={ACCENT} options={opcoes} value={regiao} onChange={setRegiao} />
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={filtrada} margin={{ top: 10, right: 20, left: 0, bottom: 60 }}>
          <CartesianGrid vertical={false} stroke={GRID} />
          <XAxis dataKey="aeroporto" tick={AXIS} interval={0} angle={-50} textAnchor="end" height={64} />
          <YAxis tick={AXIS} label={{ value: 'Conexões', angle: -90, position: 'insideLeft', offset: 10, fill: '#94a3b8', fontSize: 12 }} />
          <Tooltip content={<TooltipBox />} />
          <Legend content={<CustomLegend />} />
          {TIPOS.map(tipo => (
            <Bar
              key={tipo}
              dataKey={tipo}
              stackId="a"
              fill={CORES_TIPO[tipo]}
              name={tipo}
              radius={tipo === 'Hub nacional' ? [4, 4, 0, 0] : [0, 0, 0, 0]}
            />
          ))}
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
