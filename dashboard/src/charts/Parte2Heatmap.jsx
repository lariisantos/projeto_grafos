/* Heatmap das distâncias (saltos BFS) entre os atores mais conectados. */
import { useState, useMemo } from 'react'
import { FilterChips } from '../components/Filters'

const ESCALA = ['#166534', '#3f6212', '#854d0e', '#9a3412', '#7f1d1d'] // 1, 2, 3, 4, 5+
const ACCENT = '#2dd4bf'

function corDistancia(d) {
  if (d == null) return { bg: '#172033', fg: '#64748b' }     // sem caminho (componentes distintas)
  if (d === 0) return { bg: '#0b1b33', fg: '#475569' }       // diagonal (o próprio ator)
  return { bg: ESCALA[Math.min(d - 1, ESCALA.length - 1)], fg: '#f8fafc' }
}

function texto(d) {
  if (d == null) return '∞'   // ∞
  if (d === 0) return '·'     // ·
  return String(d)
}

/* casa a célula com o filtro de distância selecionado */
function casa(d, destaque) {
  if (destaque === 'todas') return true
  if (destaque === 'inf') return d == null
  return d === destaque
}

function Celula({ d, de, para, destaque }) {
  const { bg, fg } = corDistancia(d)
  const ativo = casa(d, destaque)
  const filtrando = destaque !== 'todas'
  const titulo = d == null
    ? `${de} e ${para}: sem caminho (componentes distintas)`
    : d === 0 ? de : `${de} → ${para}: ${d} salto${d > 1 ? 's' : ''}`
  return (
    <div title={titulo} style={{
      background: bg, color: fg, aspectRatio: '1 / 1', minWidth: 30,
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontSize: 12, fontWeight: 700, borderRadius: 6,
      fontFamily: 'Inter, sans-serif', cursor: 'default',
      opacity: filtrando && !ativo ? 0.12 : 1,
      outline: filtrando && ativo ? '2px solid rgba(255,255,255,.85)' : 'none',
      outlineOffset: -2,
      transition: 'opacity .15s',
    }}>
      {texto(d)}
    </div>
  )
}

export default function Parte2Heatmap({ heatmap }) {
  const { atores, matriz } = heatmap
  const n = atores.length
  const [destaque, setDestaque] = useState('todas')

  // valores de distância presentes na matriz → vira o filtro
  const { distancias, temInf } = useMemo(() => {
    const set = new Set()
    let inf = false
    for (const linha of matriz) {
      for (const d of linha) {
        if (d == null) inf = true
        else if (d > 0) set.add(d)
      }
    }
    return { distancias: [...set].sort((a, b) => a - b), temInf: inf }
  }, [matriz])

  const opcoes = useMemo(() => {
    const o = [{ value: 'todas', label: 'Todas' }, ...distancias.map(d => ({ value: d, label: String(d) }))]
    if (temInf) o.push({ value: 'inf', label: '∞' })
    return o
  }, [distancias, temInf])

  const cols = `minmax(118px, 1.3fr) repeat(${n}, minmax(30px, 1fr))`

  return (
    <div style={{ padding: '4px 0 14px' }}>
      <FilterChips label="Distância (saltos)" accent={ACCENT} options={opcoes} value={destaque} onChange={setDestaque} />

      <div style={{ padding: '0 14px' }}>
        {/* legenda da escala */}
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flexWrap: 'wrap', marginBottom: 14, fontSize: 12, color: '#94a3b8' }}>
          <span>Distância (saltos):</span>
          {ESCALA.map((c, i) => (
            <span key={i} style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
              <span style={{ width: 14, height: 14, borderRadius: 4, background: c, display: 'inline-block' }} />
              {i < ESCALA.length - 1 ? i + 1 : '5+'}
            </span>
          ))}
          <span style={{ display: 'flex', alignItems: 'center', gap: 5 }}>
            <span style={{ width: 14, height: 14, borderRadius: 4, background: '#172033', display: 'inline-block' }} />
            {'∞'} sem caminho
          </span>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <div style={{ display: 'grid', gridTemplateColumns: cols, gap: 4, minWidth: 560 }}>
            {/* canto + cabeçalho (índices das colunas) */}
            <div />
            {atores.map((_, j) => (
              <div key={`h${j}`} style={{ textAlign: 'center', fontSize: 11, fontWeight: 800, color: '#94a3b8', paddingBottom: 2 }}>
                {j + 1}
              </div>
            ))}

            {/* linhas */}
            {atores.map((ator, i) => (
              <Linha key={i} idx={i + 1} ator={ator} valores={matriz[i]} atores={atores} destaque={destaque} />
            ))}
          </div>
        </div>

        {/* legenda numerada dos atores */}
        <div style={{
          marginTop: 16, display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '4px 18px', fontSize: 12, color: '#94a3b8',
        }}>
          {atores.map((a, i) => (
            <span key={i}><strong style={{ color: '#cbd5e1' }}>{i + 1}.</strong> {a}</span>
          ))}
        </div>
      </div>
    </div>
  )
}

function Linha({ idx, ator, valores, atores, destaque }) {
  return (
    <>
      <div style={{
        display: 'flex', alignItems: 'center', gap: 6, fontSize: 12, color: '#cbd5e1',
        overflow: 'hidden', whiteSpace: 'nowrap', textOverflow: 'ellipsis',
      }}>
        <strong style={{ color: '#64748b', flexShrink: 0 }}>{idx}.</strong>
        <span style={{ overflow: 'hidden', textOverflow: 'ellipsis' }}>{ator}</span>
      </div>
      {valores.map((d, j) => (
        <Celula key={j} d={d} de={ator} para={atores[j]} destaque={destaque} />
      ))}
    </>
  )
}
