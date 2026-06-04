import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ReferenceLine, ResponsiveContainer, Cell,
} from 'recharts'
import { TooltipBox } from '../constants'

const AXIS = { fill: '#94a3b8', fontSize: 11 }
const GRID = 'rgba(148,163,184,0.08)'

/* Histograma da distribuição de graus da rede */
export default function GrauChart({ histData, media }) {
  const max = Math.max(...histData.map(d => d.count))
  return (
    <ResponsiveContainer width="100%" height={320}>
      <BarChart data={histData} margin={{ top: 16, right: 24, left: 4, bottom: 24 }}>
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
          x={media}
          stroke="#E63946"
          strokeDasharray="5 3"
          strokeWidth={2}
          label={{ value: `Média ${media.toFixed(1)}`, fill: '#E63946', fontSize: 11, position: 'top' }}
        />
        <Bar dataKey="count" name="Aeroportos" radius={[5, 5, 0, 0]} maxBarSize={54}>
          {histData.map((entry) => {
            const alpha = 0.45 + 0.55 * (entry.count / max)
            return (
              <Cell key={entry.grau} fill={`rgba(71,123,157,${alpha.toFixed(2)})`} />
            )
          })}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
