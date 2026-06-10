import { useState, useMemo } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ReferenceLine, ResponsiveContainer, Cell, LabelList,
} from 'recharts'
import { CORES } from '../constants'
import { FilterChips, opcoesRegiao } from '../components/Filters'

const AXIS = { fill: '#94a3b8', fontSize: 11 }
const GRID = 'rgba(148,163,184,0.08)'
const ACCENT = '#fbbf24'

function hexAlpha(hex, a) {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  return `rgba(${r},${g},${b},${a.toFixed(2)})`
}

function CustomTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  return (
    <div style={{
      background: 'rgba(7,17,31,0.97)',
      border: '1px solid rgba(99,179,237,0.3)',
      borderRadius: 12,
      padding: '10px 14px',
      fontSize: 13,
      boxShadow: '0 20px 40px rgba(0,0,0,0.5)',
    }}>
      <p style={{ color: '#f0f9ff', fontWeight: 800, fontSize: 15, marginBottom: 6 }}>{d.aeroporto}</p>
      <p style={{ color: CORES[d.regiao] ?? '#e5eefc' }}>{d.regiao}</p>
      <p style={{ color: '#cbd5e1', marginTop: 4 }}>
        Grau: <strong style={{ color: '#f0f9ff' }}>{d.grau}</strong>
      </p>
      <p style={{ color: '#94a3b8', fontSize: 12, marginTop: 2 }}>
        Dens. ego: {d.densidade_ego?.toFixed(3)}
      </p>
    </div>
  )
}

/* Ranking de hubs por grau. Filtro: região (a linha de média continua sendo a
 * média GLOBAL, para comparar a região com o todo). */
export default function HubsChart({ data, media }) {
  const [regiao, setRegiao] = useState('Todas')
  const opcoes = useMemo(() => opcoesRegiao(data), [data])
  const filtrada = useMemo(
    () => (regiao === 'Todas' ? data : data.filter(d => d.regiao === regiao)),
    [data, regiao],
  )
  const maxGrau = filtrada.length ? Math.max(...filtrada.map(d => d.grau)) : 1

  return (
    <div>
      <FilterChips label="Região" accent={ACCENT} options={opcoes} value={regiao} onChange={setRegiao} />
      <ResponsiveContainer width="100%" height={Math.max(300, filtrada.length * 31)}>
        <BarChart
          data={filtrada}
          layout="vertical"
          margin={{ top: 10, right: 60, left: 8, bottom: 10 }}
        >
          <CartesianGrid horizontal={false} stroke={GRID} />
          <XAxis
            type="number"
            tick={AXIS}
            label={{ value: 'Grau (conexões diretas)', position: 'insideBottom', offset: -4, fill: '#94a3b8', fontSize: 12 }}
          />
          <YAxis
            type="category"
            dataKey="aeroporto"
            tick={AXIS}
            width={38}
          />
          <Tooltip content={<CustomTooltip />} />
          <ReferenceLine
            x={media}
            stroke="#64748b"
            strokeDasharray="4 3"
            strokeWidth={1.5}
            label={{ value: `Média ${media.toFixed(1)}`, fill: '#64748b', fontSize: 11, position: 'insideTopRight' }}
          />
          <Bar dataKey="grau" name="Grau" radius={[0, 6, 6, 0]} maxBarSize={20}>
            {filtrada.map((entry) => {
              const alpha = 0.45 + 0.55 * (entry.grau / maxGrau)
              return (
                <Cell key={entry.aeroporto} fill={hexAlpha(CORES[entry.regiao] ?? '#64748b', alpha)} />
              )
            })}
            <LabelList
              dataKey="grau"
              position="right"
              style={{ fill: '#cbd5e1', fontSize: 11, fontWeight: 700 }}
            />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
