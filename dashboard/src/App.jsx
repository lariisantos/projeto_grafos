import { useState } from 'react'
import Parte1 from './Parte1'
import Parte2 from './Parte2'

const PARTES = [
  { id: 'p1', label: 'Parte 1', sub: 'Aeroportos do Brasil', grad: 'linear-gradient(135deg,#3b82f6,#6366f1)' },
  { id: 'p2', label: 'Parte 2', sub: 'Filmes · Netflix', grad: 'linear-gradient(135deg,#a78bfa,#f472b6)' },
]

function TopNav({ parte, setParte }) {
  return (
    <div style={{
      position: 'sticky', top: 0, zIndex: 50,
      background: 'rgba(2,6,23,0.72)', backdropFilter: 'blur(14px)',
      borderBottom: '1px solid rgba(148,163,184,.14)',
    }}>
      <div style={{
        maxWidth: 1240, margin: '0 auto', padding: '12px 28px',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16, flexWrap: 'wrap',
      }}>
        <span style={{ fontSize: 13, fontWeight: 800, color: '#cbd5e1', letterSpacing: '-.01em' }}>
          Teoria dos Grafos
          <span style={{ color: '#475569', fontWeight: 600 }}> · Projeto Final</span>
        </span>
        <div style={{
          display: 'inline-flex', background: 'rgba(15,23,42,.7)',
          border: '1px solid rgba(148,163,184,.16)', borderRadius: 12, padding: 4, gap: 4,
        }}>
          {PARTES.map(p => {
            const active = parte === p.id
            return (
              <button key={p.id} onClick={() => setParte(p.id)} style={{
                border: 'none', cursor: 'pointer', fontFamily: 'inherit', textAlign: 'left',
                padding: '7px 16px', borderRadius: 9,
                background: active ? p.grad : 'transparent',
                color: active ? '#fff' : '#94a3b8', transition: 'all .18s',
                display: 'flex', flexDirection: 'column', lineHeight: 1.2,
              }}>
                <span style={{ fontSize: 13, fontWeight: 800 }}>{p.label}</span>
                <span style={{ fontSize: 10, fontWeight: 600, opacity: active ? 0.85 : 0.7 }}>{p.sub}</span>
              </button>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default function App() {
  const [parte, setParte] = useState('p1')

  return (
    <>
      <TopNav parte={parte} setParte={setParte} />

      <div style={{ maxWidth: 1240, margin: '0 auto', padding: '0 28px 72px' }}>
        {parte === 'p1' ? <Parte1 /> : <Parte2 />}

        <footer style={{
          marginTop: 48, paddingTop: 24, borderTop: '1px solid rgba(148,163,184,.14)',
          display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8, color: '#64748b', fontSize: 12,
        }}>
          <span>Teoria dos Grafos — Aeroportos do Brasil &amp; Rede de Colaboração Netflix</span>
          <span>Front em React · Recharts &amp; SVG · Dados gerados em Python</span>
        </footer>
      </div>

      <style>{`@keyframes fadeUp { from { opacity:0; transform:translateY(10px) } to { opacity:1; transform:none } }`}</style>
    </>
  )
}
