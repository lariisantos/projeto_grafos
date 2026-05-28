import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ReferenceLine, ResponsiveContainer, Cell,
} from 'recharts'
import { CORES, TooltipBox } from '../constants'

const AXIS = { fill: '#94a3b8', fontSize: 11 }
const GRID = 'rgba(148,163,184,0.08)'

/* ── Histogram ── */
function GrauHistogram({ data, media }) {
  const max = Math.max(...data.map(d => d.count))
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
        <CartesianGrid vertical={false} stroke={GRID} />
        <XAxis dataKey="grau" tick={AXIS} label={{ value: 'Grau', position: 'insideBottom', offset: -12, fill: '#94a3b8', fontSize: 12 }} />
        <YAxis tick={AXIS} label={{ value: 'Aeroportos', angle: -90, position: 'insideLeft', offset: 10, fill: '#94a3b8', fontSize: 12 }} />
        <Tooltip content={<TooltipBox formatter={e => `${e.value} aeroportos`} />} />
        <ReferenceLine
          x={media}
          stroke="#E63946"
          strokeDasharray="5 3"
          strokeWidth={2}
          label={{ value: `Média ${media.toFixed(1)}`, fill: '#E63946', fontSize: 11, position: 'top' }}
        />
        <Bar dataKey="count" name="Aeroportos" radius={[4, 4, 0, 0]} maxBarSize={48}>
          {data.map((entry) => {
            const alpha = 0.45 + 0.55 * (entry.count / max)
            return (
              <Cell
                key={entry.grau}
                fill={`rgba(71,123,157,${alpha.toFixed(2)})`}
              />
            )
          })}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

/* ── Média por Região ── */
function GrauPorRegiao({ data }) {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 20 }}>
        <CartesianGrid vertical={false} stroke={GRID} />
        <XAxis dataKey="regiao" tick={{ ...AXIS, fontSize: 10 }} interval={0} angle={-20} textAnchor="end" height={48} />
        <YAxis tick={AXIS} label={{ value: 'Grau médio', angle: -90, position: 'insideLeft', offset: 10, fill: '#94a3b8', fontSize: 12 }} />
        <Tooltip content={
          <TooltipBox formatter={e => e.value.toFixed(2)} />
        } />
        <Bar dataKey="media" name="Grau médio" radius={[6, 6, 0, 0]} maxBarSize={52}>
          {data.map((entry) => (
            <Cell key={entry.regiao} fill={CORES[entry.regiao] ?? '#64748b'} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}

/* ── Export ── */
export default function GrauChart({ histData, regData, media }) {
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
      <div>
        <p style={{ color: '#94a3b8', fontSize: 12, marginBottom: 8, paddingLeft: 8 }}>
          Distribuição dos graus
        </p>
        <GrauHistogram data={histData} media={media} />
      </div>
      <div>
        <p style={{ color: '#94a3b8', fontSize: 12, marginBottom: 8, paddingLeft: 8 }}>
          Grau médio por região
        </p>
        <GrauPorRegiao data={regData} />
      </div>
    </div>
  )
}
