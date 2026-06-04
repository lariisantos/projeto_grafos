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

/**
 * Linha de gráficos RELACIONADOS.
 * O banner explicita a relação entre os dois gráficos (requisito do projeto:
 * apenas gráficos com relação ficam na mesma linha, e a relação fica no texto).
 */
function RelationRow({ eyebrow, accent, title, relation, children }) {
  return (
    <section style={{ marginBottom: 30 }}>
      <div style={{
        background: 'rgba(15,23,42,0.55)',
        border: '1px solid rgba(148,163,184,.14)',
        borderLeft: `4px solid ${accent}`,
        borderRadius: 14, padding: '14px 18px', marginBottom: 16,
      }}>
        <span style={{
          display: 'inline-block', fontSize: 10.5, fontWeight: 800, letterSpacing: '.09em',
          textTransform: 'uppercase', color: accent, marginBottom: 4,
        }}>
          {eyebrow}
        </span>
        <h3 style={{ fontSize: 16, fontWeight: 800, color: '#f0f9ff', marginBottom: 6, letterSpacing: '-.02em' }}>{title}</h3>
        <p style={{ fontSize: 13, color: '#cbd5e1', lineHeight: 1.6, margin: 0 }}>
          <strong style={{ color: '#e2e8f0' }}>Como ler em conjunto:</strong> {relation}
        </p>
      </div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))', gap: 18, alignItems: 'stretch' }}>
        {children}
      </div>
    </section>
  )
}

/* Caixa de descrição/insight para visualizações que ocupam a aba inteira */
function InsightBanner({ accent, title, children }) {
  return (
    <div style={{
      background: `${accent}0f`, border: `1px solid ${accent}33`,
      borderRadius: 16, padding: '14px 18px', marginBottom: 18,
      display: 'flex', gap: 12, alignItems: 'flex-start',
    }}>
      <span style={{
        flexShrink: 0, fontSize: 11, fontWeight: 900, letterSpacing: '.05em',
        textTransform: 'uppercase', color: accent, marginTop: 2,
      }}>
        {title}
      </span>
      <p style={{ fontSize: 13, color: '#cbd5e1', lineHeight: 1.6, margin: 0 }}>{children}</p>
    </div>
  )
}

export default function App() {
  const [tab, setTab] = useState('analise')
  const { global: glob, regioes, egoAeroportos, histData,
          composicao, hubs, grafoDados, percursosDados } = DATA

  const media = egoAeroportos.reduce((s, a) => s + a.grau, 0) / egoAeroportos.length
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
        <TabBtn label="Análise da Rede" active={tab === 'analise'}    onClick={() => setTab('analise')} />
        <TabBtn label="Percursos"       active={tab === 'percursos'}  onClick={() => setTab('percursos')} />
        <TabBtn label="Grafo da Rede"   active={tab === 'rede'}       onClick={() => setTab('rede')} />
      </nav>

      {/* ABA ANALISE */}
      {tab === 'analise' && (
        <div style={{ animation: 'fadeUp .28s ease' }}>
          <SectionHeader
            title="Análise Exploratória e Explanatória"
            sub="Gráficos relacionados ficam lado a lado · cada linha começa explicando a relação entre eles · passe o mouse para detalhes"
          />

          {/* LINHA 1 — Exploratórias: comportamento dos dados */}
          <RelationRow
            eyebrow="Exploratória · comportamento da rede"
            accent="#3b82f6"
            title="Quão conectado é cada aeroporto — e por quê"
            relation="o histograma mostra QUANTAS conexões cada aeroporto tem, e a composição mostra de que TIPO elas são. A cauda direita do histograma (graus 6–9) corresponde exatamente aos aeroportos que concentram conexões de hub nacional na composição ao lado — alto grau e papel de hub andam juntos."
          >
            <ChartCard
              title="Distribuição dos graus"
              sub="Histograma · quantos aeroportos existem para cada grau"
              tag="Exploratória 1"
              accent="#3b82f6"
              insight="A distribuição é assimétrica à direita: a maioria dos aeroportos tem grau entre 3 e 5 e apenas 4 superam a média de 4,5 conexões. É a assinatura de uma rede de poucos hubs dominantes, em vez de conexões uniformes."
            >
              <GrauChart histData={histData} media={media} />
            </ChartCard>

            <ChartCard
              title="Composição das conexões"
              sub="Barras empilhadas · tipo de aresta em cada aeroporto"
              tag="Exploratória 2"
              accent="#2dd4bf"
              insight="Decompõe o grau de cada aeroporto pelos três tipos de aresta do nosso modelo (regional, hub regional, hub nacional). Os maiores graus vêm de conexões de hub nacional: o alto grau resulta do papel de articulação entre regiões, não de muitas rotas locais."
            >
              <ComposicaoChart data={composicao} />
            </ChartCard>
          </RelationRow>

          {/* LINHA 2 — Explanatórias: comunicação de insights */}
          <RelationRow
            eyebrow="Explanatória · comunicando os insights"
            accent="#fbbf24"
            title="Onde está concentrada a conectividade"
            relation="os dois mudam de escala — o ranking olha o aeroporto individual, a comparação agrega por região. Lendo em conjunto, os hubs do topo do ranking (REC, GRU, MAO) são os que puxam o grau médio das suas regiões, e por isso Nordeste e Sudeste lideram a malha."
          >
            <ChartCard
              title="Ranking de hubs"
              sub="Barra ordenada · grau de cada aeroporto, colorido por região"
              tag="Explanatória 1"
              accent="#fbbf24"
              insight="Recife (9), Guarulhos (8) e Manaus (7) são os principais hubs da rede. Abaixo da média (4,5) ficam aeroportos periféricos como Goiânia (1) e Curitiba/Florianópolis (2). A cor revela a região a que cada hub pertence."
            >
              <HubsChart data={hubs} media={media} />
            </ChartCard>

            <ChartCard
              title="Comparação entre regiões"
              sub="3 indicadores · nº de aeroportos, arestas internas e grau médio"
              tag="Explanatória 2"
              accent="#a78bfa"
              insight="Agrega a rede por região. O Nordeste lidera nos três indicadores (6 aeroportos, 15 arestas internas, grau médio 5,7), seguido do Sudeste — concentração coerente com a presença dos maiores hubs nessas regiões."
            >
              <RegioesChart data={regioes} />
            </ChartCard>
          </RelationRow>
        </div>
      )}

      {/* ABA PERCURSOS */}
      {tab === 'percursos' && (
        <div style={{ animation: 'fadeUp .28s ease' }}>
          <SectionHeader title="Percursos Obrigatórios" sub="Caminhos de menor custo via Dijkstra · arraste nós, pan e scroll para zoom" />
          <InsightBanner accent="#2dd4bf" title="O que isto mostra">
            Cada cor é um percurso de menor custo resolvido pelo nosso Dijkstra; os rótulos das arestas trazem o peso
            do modelo (1.0 regional · 1.5 hub regional · 2.0 hub nacional). Repare que quase todos os caminhos passam
            por um hub (GRU, REC): é o efeito direto da nossa régua de pesos, que torna as conexões via hub o trajeto
            mais barato entre regiões distantes.
          </InsightBanner>
          {percursosDados
            ? <RouteTree percursosDados={percursosDados} />
            : <p style={{ color: '#94a3b8', padding: 24 }}>Dados indisponíveis. Execute python src/solve.py.</p>
          }
        </div>
      )}

      {/* ABA REDE */}
      {tab === 'rede' && (
        <div style={{ animation: 'fadeUp .28s ease' }}>
          <SectionHeader title="Grafo Completo da Rede" sub="Simulação de física interativa · nós coloridos por região, arestas por tipo de conexão" />
          <InsightBanner accent="#3b82f6" title="O que isto mostra">
            A malha inteira: {glob.ordem} aeroportos e {glob.tamanho} conexões. Os nós são coloridos por região e se
            organizam por uma simulação de forças; a espessura/cor das arestas distingue conexões regionais, de hub
            regional e de hub nacional. Visualmente, os cinco hubs nacionais (REC, GRU, MAO, POA, BSB) formam o núcleo
            que costura as cinco regiões do país.
          </InsightBanner>
          {grafoDados
            ? <NetworkGraph grafoDados={grafoDados} />
            : <p style={{ color: '#94a3b8', padding: 24 }}>Dados indisponíveis. Execute python src/solve.py.</p>
          }
        </div>
      )}

      <footer style={{ marginTop: 48, paddingTop: 24, borderTop: '1px solid rgba(148,163,184,.14)', display: 'flex', justifyContent: 'space-between', flexWrap: 'wrap', gap: 8, color: '#64748b', fontSize: 12 }}>
        <span>Teoria dos Grafos — Rede de Aeroportos do Brasil</span>
        <span>Front em React · Recharts &amp; SVG · Dados gerados em Python</span>
      </footer>

      <style>{`@keyframes fadeUp { from { opacity:0; transform:translateY(10px) } to { opacity:1; transform:none } }`}</style>
    </div>
  )
}
