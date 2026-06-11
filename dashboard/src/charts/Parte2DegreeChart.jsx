import { useState, useMemo } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell,
} from 'recharts'
import { TooltipBox } from '../constants'
import { FilterChips, rotuloGenero } from '../components/Filters'

const AXIS = { fill: '#94a3b8', fontSize: 10 }
const GRID = 'rgba(148,163,184,0.08)'
const ACCENT = '#a78bfa'

/* Histograma da distribuição de graus (escala log no eixo Y).
 * Filtro: GÊNERO — restringe a distribuição aos atores que atuam no gênero
 * escolhido. Todas as faixas compartilham o mesmo eixo X (binning global). */
export default function Parte2DegreeChart({ generos }) {
  const [genero, setGenero] = useState('Todos')
  const opcoes = useMemo(
    () => generos.lista.map(g => ({ value: g, label: rotuloGenero(g) })),
    [generos],
  )

  const data = generos.histograma[genero] ?? []
  const max = data.length ? Math.max(...data.map(d => d.count)) : 1

  return (
    <div>
      <FilterChips label="Gênero" accent={ACCENT} options={opcoes} value={genero} onChange={setGenero} />
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} margin={{ top: 16, right: 20, left: 8, bottom: 40 }}>
          <CartesianGrid vertical={false} stroke={GRID} />
          <XAxis
            dataKey="faixa"
            tick={AXIS}
            interval={0}
            angle={-35}
            textAnchor="end"
            height={52}
            label={{ value: 'Faixa de grau (nº de colaboradores)', position: 'insideBottom', offset: -2, fill: '#94a3b8', fontSize: 12 }}
          />
          <YAxis
            scale="log"
            domain={[1, 'dataMax']}
            allowDataOverflow
            tick={AXIS}
            label={{ value: 'Atores (escala log)', angle: -90, position: 'insideLeft', offset: 14, fill: '#94a3b8', fontSize: 12 }}
          />
          <Tooltip content={<TooltipBox formatter={e => `${e.value.toLocaleString('pt-BR')} atores`} />} />
          <Bar dataKey="count" name="Atores" radius={[5, 5, 0, 0]}>
            {data.map((entry, i) => {
              const alpha = 0.45 + 0.55 * (1 - i / Math.max(data.length, 1))
              return <Cell key={entry.faixa} fill={`rgba(124,58,237,${alpha.toFixed(2)})`} />
            })}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
