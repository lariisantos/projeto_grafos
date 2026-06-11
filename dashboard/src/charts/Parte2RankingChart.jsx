import { useState, useMemo } from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid,
  Tooltip, ResponsiveContainer, Cell, LabelList,
} from 'recharts'
import { FilterChips, rotuloGenero } from '../components/Filters'

const AXIS = { fill: '#cbd5e1', fontSize: 11 }
const GRID = 'rgba(148,163,184,0.08)'
const ACCENT = '#fbbf24'

function CustomTooltip({ active, payload, genero }) {
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  return (
    <div style={{
      background: 'rgba(7,17,31,0.97)', border: '1px solid rgba(99,179,237,0.3)',
      borderRadius: 12, padding: '10px 14px', fontSize: 13, boxShadow: '0 20px 40px rgba(0,0,0,0.5)',
    }}>
      <p style={{ color: '#f0f9ff', fontWeight: 800, fontSize: 14, marginBottom: 4 }}>{d.ator}</p>
      <p style={{ color: '#cbd5e1' }}>
        Colaboradores únicos: <strong style={{ color: '#a78bfa' }}>{d.grau}</strong>
      </p>
      {genero !== 'Todos' && (
        <p style={{ color: '#64748b', fontSize: 11, marginTop: 3 }}>atua em {rotuloGenero(genero)}</p>
      )}
    </div>
  )
}

/* Ranking dos atores mais conectados (barra horizontal ordenada).
 * Filtro: GÊNERO — mostra os atores que atuam em filmes/séries do gênero
 * escolhido (grau = nº total de colaboradores, não muda com o gênero). */
export default function Parte2RankingChart({ generos }) {
  const [genero, setGenero] = useState('Todos')
  const opcoes = useMemo(
    () => generos.lista.map(g => ({ value: g, label: rotuloGenero(g) })),
    [generos],
  )

  // recharts desenha de baixo p/ cima → ordena asc para o maior ficar no topo
  const ordenado = useMemo(() => {
    const data = generos.ranking[genero] ?? []
    return [...data].sort((a, b) => a.grau - b.grau)
  }, [generos, genero])

  const maxGrau = ordenado.length ? Math.max(...ordenado.map(d => d.grau)) : 1

  return (
    <div>
      <FilterChips label="Gênero" accent={ACCENT} options={opcoes} value={genero} onChange={setGenero} />
      <ResponsiveContainer width="100%" height={Math.max(300, ordenado.length * 26)}>
        <BarChart data={ordenado} layout="vertical" margin={{ top: 8, right: 52, left: 8, bottom: 10 }}>
          <CartesianGrid horizontal={false} stroke={GRID} />
          <XAxis
            type="number"
            tick={{ fill: '#94a3b8', fontSize: 11 }}
            label={{ value: 'Colaboradores únicos (grau)', position: 'insideBottom', offset: -2, fill: '#94a3b8', fontSize: 12 }}
          />
          <YAxis type="category" dataKey="ator" tick={AXIS} width={150} />
          <Tooltip content={<CustomTooltip genero={genero} />} cursor={{ fill: 'rgba(148,163,184,0.06)' }} />
          <Bar dataKey="grau" name="Grau" radius={[0, 6, 6, 0]} maxBarSize={18}>
            {ordenado.map(entry => {
              const alpha = 0.5 + 0.5 * (entry.grau / maxGrau)
              return <Cell key={entry.ator} fill={`rgba(167,139,250,${alpha.toFixed(2)})`} />
            })}
            <LabelList dataKey="grau" position="right" style={{ fill: '#cbd5e1', fontSize: 11, fontWeight: 700 }} />
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
