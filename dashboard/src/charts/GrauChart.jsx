import { useState, useMemo } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ReferenceLine, ResponsiveContainer, Cell,
} from 'recharts'
import { TooltipBox } from '../constants'
import { FilterChips, opcoesRegiao } from '../components/Filters'

const AXIS = { fill: '#94a3b8', fontSize: 11 }
const GRID = 'rgba(148,163,184,0.08)'
const ACCENT = '#3b82f6'

/* Histograma da distribuição de graus da rede.
 * Filtro: região — recalcula o histograma e a média só com os aeroportos da
 * região escolhida (usa `ego`, a lista por aeroporto com grau + região). */
export default function GrauChart({ histData, media, ego }) {
  const [regiao, setRegiao] = useState('Todas')
  const opcoes = useMemo(() => (ego ? opcoesRegiao(ego) : ['Todas']), [ego])

  const { data, mediaLocal } = useMemo(() => {
    if (!ego) return { data: histData, mediaLocal: media }
    const sub = regiao === 'Todas' ? ego : ego.filter(e => e.regiao === regiao)
    const cont = {}
    sub.forEach(e => { cont[e.grau] = (cont[e.grau] || 0) + 1 })
    const d = Object.keys(cont)
      .map(g => ({ grau: Number(g), count: cont[g] }))
      .sort((a, b) => a.grau - b.grau)
    const m = sub.length ? sub.reduce((s, e) => s + e.grau, 0) / sub.length : 0
    return { data: d, mediaLocal: m }
  }, [ego, regiao, histData, media])

  const max = data.length ? Math.max(...data.map(d => d.count)) : 1

  return (
    <div>
      <FilterChips label="Região" accent={ACCENT} options={opcoes} value={regiao} onChange={setRegiao} />
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} margin={{ top: 16, right: 24, left: 4, bottom: 24 }}>
          <CartesianGrid vertical={false} stroke={GRID} />
          <XAxis
            dataKey="grau"
            tick={AXIS}
            label={{ value: 'Grau (nº de conexões diretas)', position: 'insideBottom', offset: -14, fill: '#94a3b8', fontSize: 12 }}
          />
          <YAxis
            tick={AXIS}
            allowDecimals={false}
            label={{ value: 'Nº de aeroportos', angle: -90, position: 'insideLeft', offset: 12, fill: '#94a3b8', fontSize: 12 }}
          />
          <Tooltip content={<TooltipBox formatter={e => `${e.value} aeroportos`} />} />
          <ReferenceLine
            x={mediaLocal}
            stroke="#E63946"
            strokeDasharray="5 3"
            strokeWidth={2}
            label={{ value: `Média ${mediaLocal.toFixed(1)}`, fill: '#E63946', fontSize: 11, position: 'top' }}
          />
          <Bar dataKey="count" name="Aeroportos" radius={[5, 5, 0, 0]} maxBarSize={54}>
            {data.map((entry) => {
              const alpha = 0.45 + 0.55 * (entry.count / max)
              return (
                <Cell key={entry.grau} fill={`rgba(71,123,157,${alpha.toFixed(2)})`} />
              )
            })}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
