import { useState } from 'react'
import { CORES } from './constants'
import ChartCard from './components/ChartCard'
import GrauChart from './charts/GrauChart'
import ComposicaoChart from './charts/ComposicaoChart'
import HubsChart from './charts/HubsChart'
import RegioesChart from './charts/RegioesChart'
import NetworkGraph from './charts/NetworkGraph'
import RouteTree from './charts/RouteTree'
import { DATA } from './data'

function MetricCard({ value, label, accent }) {
  const [hov, setHov] = useState(false)
  return (
    <div onMouseEnter={() => setHov(true)} onMouseLeave={() => setHov(false)} style={{
      position: 'relative', overflow: 'hidden',
      background: 'rgba(15,23,42,0.82)',
      border: `1px solid ${hov ? 'rgba(99,179,237,0.3)' : 'rgba(148,163,184,0.16)'}`,
      borderRadius: 18, padding: '20px 22px', backdropFilter: 'blur(18px)',
      boxShadow: hov ? '0 24px 60px rgba(0,0,0,.38)' : '0 12px 36px rgba(0,0,0,.28)',
      transform: hov ? 'translateY(-3px)' : 'none', transition: 'all .2s ease',
    }}>
      <div style={{ position: 'absolute', inset: '0 0 auto 0', height: 2, background: `linear-gradient(90deg, ${accent}, transparent)` }} />
      <div style={{ fontSize: 30, fontWeight: 900, letterSpacing: '-.04em', color: accent, lineHeight: 1 }}>{value}</div>
      <div style={{ fontSize: 11, color: '#94a3b8', marginTop: 6, fontWeight: 700, textTransform: 'uppercase', letterSpacing: '.07em' }}>{label}</div>
    </div>
  )
}

function TabBtn({ label, active, onClick }) {
  return (
    <button onClick={onClick} style={{
      position: 'relative', border: 'none', background: 'none', cursor: 'pointer',
      color: active ? '#e5eefc' : '#94a3b8', fontFamily: 'inherit',
      fontWeight: 700, fontSize: 14, padding: '12px 24px 15px',
      borderRadius: '10px 10px 0 0', marginBottom: -1,
      transition: 'color .18s, background .18s',
      backgroundColor: active ? 'rgba(255,255,255,.04)' : 'transparent',
    }}>
      {label}
      {active && <span style={{ position: 'absolute', bottom: -1, left: 0, right: 0, height: 3, borderRadius: '3px 3px 0 0', background: '#3b82f6' }} />}
    </button>
  )
}

function SectionHeader({ title, sub }) {
  return (
    <div style={{ marginBottom: 24 }}>
      <h2 style={{ fontSize: 22, fontWeight: 800, color: '#f0f9ff', letterSpacing: '-.03em' }}>{title}</h2>
      {sub && <p style={{ color: '#94a3b8', fontSize: 13, marginTop: 5 }}>{sub}</p>}
    </div>
  )
}

export default function App() {
  const [tab, setTab] = useState('analise')
  const { global: glob, regioes, egoAeroportos, histData, regData,
          composicao, hubs, grafoDados, percursosDados } = DATA

  const media  = egoAeroportos.reduce((s, a) => s + a.grau, 0) / egoAeroportos.length
  const hubTop = [...egoAeroportos].sort((a, b) => b.grau - a.grau)[0]

  return (
    <div style={{ maxWidth: 1240, margin: '0 auto', padding: '0 28px 72px' }}>

      {/* HERO */}
      <div style={{ padding: '52px 0 40px' }}>
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: 8,
          background: 'rgba(59,130,246,.12)', border: '1px solid rgba(59,130,246,.3)',
          color: '#93c5fd', borderRadius: 999, fontSize: 12, fontWeight: 700,
          letterSpacing: '.08em', textTransform: 'uppercase', padding: '5px 14px', marginBottom: 18,
        }}>
          Teoria dos Grafos · Malha Aérea Brasileira
        </div>
        <h1 style={{
          fontSize: 'clamp(32px,5vw,58px)', fontWeight: 900, letterSpacing: '-.05em', lineHeight: 1.05,
          background: 'linear-gradient(135deg,#f0f9ff 30%,#93c5fd 65%,#818cf8 100%)',
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
        }}>
          Rede de Aeroportos<br />do Brasil
        </h1>
        <p style={{ color: '#94a3b8', marginTop: 12, fontSize: 16, maxWidth: 600, lineHeight: 1.6 }}>
          Análise exploratória e explanatória de {glob.ordem} aeroportos e {glob.tamanho} conexões em {regioes.length} regiões.
        </p>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginTop: 20 }}>
          {Object.entries(CORES).map(([reg, cor]) => (
            <span key={reg} style={{ padding: '5px 12px', borderRadius: 999, fontSize: 11, fontWeight: 700, background: `${cor}1a`, border: `1px solid ${cor}55`, color: cor }}>{reg}</span>
          ))}
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(155px,1fr))', gap: 14, marginTop: 32 }}>
          <MetricCard value={glob.ordem}      label="Aeroportos"            accent="#3b82f6" />
          <MetricCard value={glob.tamanho}     label="Conexões"              accent="#2dd4bf" />
          <MetricCard value={regioes.length}   label="Regiões"               accent="#ff4d6d" />
          <MetricCard value={glob.densidade.toFixed(4)} label="Densidade global" accent="#fbbf24" />
          <MetricCard value={hubTop?.aeroporto} label={`Hub principal · ${hubTop?.grau} conexões`} accent="#a78bfa" />
        </div>
      </div>

      {/* TABS */}
      <nav style={{ display: 'flex', gap: 2, borderBottom: '1px solid rgba(148,163,184,.16)', marginBottom: 32 }}>
        <TabBtn label="Análise Q10"   active={tab === 'analise'}    onClick={() => setTab('analise')} />
        <TabBtn label="Percursos"     active={tab === 'percursos'}  onClick={() => setTab('percursos')} />
        <TabBtn label="Grafo da Rede" active={tab === 'rede'}       onClick={() => setTab('rede')} />
      </nav>

      {/* ABA ANALISE */}
      {tab === 'analise' && (
        <div style={{ animation: 'fadeUp .28s ease' }}>
          <SectionHeader title="Análise Exploratória e Explanatória" sub="Passe o mouse para detalhes · Clique na legenda para filtrar" />
          <div style={{ display: 'grid', gap: 20 }}>
            <ChartCard title="Exploratório 1 — Distribuição dos Graus" sub="Histograma de graus e grau médio por região">
              <GrauChart histData={histData} regData={regData} media={media} />
            </ChartCard>
            <ChartCard title="Exploratório 2 — Composição das Conexões" sub="Tipos de conexão em cada aeroporto (barras empilhadas)">
              <ComposicaoChart data={composicao} />
            </ChartCard>
            <ChartCard title="Explanatório 1 — Ranking de Hubs" sub="Aeroportos ordenados pelo grau, coloridos por região">
              <HubsChart data={hubs} media={media} />
            </ChartCard>
            <ChartCard title="Explanatório 2 — Comparação entre Regiões" sub="Volume de aeroportos, arestas internas e grau médio">
              <RegioesChart data={regioes} />
            </ChartCard>
          </div>
        </div>
      )}

      {/* ABA PERCURSOS */}
      {tab === 'percursos' && (
        <div style={{ animation: 'fadeUp .28s ease' }}>
          <SectionHeader title="Percursos Obrigatórios" sub="Caminhos de menor custo via Dijkstra · Arraste nós, pan e scroll para zoom" />
          {percursosDados
            ? <RouteTree percursosDados={percursosDados} />
            : <p style={{ color: '#94a3b8', padding: 24 }}>Dados indisponíveis. Execute python src/solve.py.</p>
          }
        </div>
      )}

      {/* ABA REDE */}
      {tab === 'rede' && (
        <div style={{ animation: 'fadeUp .28s ease' }}>
          <SectionHeader title="Grafo Completo da Rede" sub="Simulação de física interativa · Nós coloridos por região, arestas por tipo de conexão" />
          {grafoDados
            ? <NetworkGraph grafoDados={grafoDados} />
            : <p style={{ color: '#94a3b8', padding: 24 }}>Dados indisponíveis. Execute python src/solve.py.</p>
          }
        </div>
      )}

      <footer style={{ marginTop: 48, paddingTop: 24, borderTop: '1px solid rgba(148,163,184,.14)', display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8, color: '#64748b', fontSize: 12 }}>
        <span>Teoria dos Grafos — Rede de Aeroportos do Brasil</span>
        <span>React · Recharts · SVG · Python</span>
      </footer>

      <style>{`@keyframes fadeUp { from { opacity:0; transform:translateY(10px) } to { opacity:1; transform:none } }`}</style>
    </div>
  )
}
