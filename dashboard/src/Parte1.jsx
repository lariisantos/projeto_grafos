import { useState } from 'react'
import { CORES } from './constants'
import ChartCard from './components/ChartCard'
import { MetricCard, TabBtn, SectionHeader, RelationRow, InsightBanner } from './components/ui'
import GrauChart from './charts/GrauChart'
import ComposicaoChart from './charts/ComposicaoChart'
import HubsChart from './charts/HubsChart'
import RegioesChart from './charts/RegioesChart'
import NetworkGraph from './charts/NetworkGraph'
import RouteTree from './charts/RouteTree'
import { DATA } from './data'

export default function Parte1() {
  const [tab, setTab] = useState('analise')
  const { global: glob, regioes, egoAeroportos, histData,
          composicao, hubs, grafoDados, percursosDados } = DATA

  const media = egoAeroportos.reduce((s, a) => s + a.grau, 0) / egoAeroportos.length
  const hubTop = [...egoAeroportos].sort((a, b) => b.grau - a.grau)[0]

  return (
    <div>
      {/* HERO */}
      <div style={{ padding: '36px 0 40px' }}>
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: 8,
          background: 'rgba(59,130,246,.12)', border: '1px solid rgba(59,130,246,.3)',
          color: '#93c5fd', borderRadius: 999, fontSize: 12, fontWeight: 700,
          letterSpacing: '.08em', textTransform: 'uppercase', padding: '5px 14px', marginBottom: 18,
        }}>
          Parte 1 · Malha Aérea Brasileira
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

          {/* LINHA 1 — Exploratórias (empilhadas: histograma sozinho, composição abaixo) */}
          <RelationRow
            cols={1}
            eyebrow="Exploratória · comportamento da rede"
            accent="#3b82f6"
            title="Quão conectado é cada aeroporto — e por quê"
            relation="o histograma mostra QUANTAS conexões cada aeroporto tem, e a composição mostra de que TIPO elas são. A cauda direita do histograma (graus 6–9) corresponde exatamente aos aeroportos que concentram conexões de hub nacional na composição abaixo — alto grau e papel de hub andam juntos."
          >
            <ChartCard
              title="Distribuição dos graus"
              sub="Histograma · quantos aeroportos existem para cada grau"
              tag="Exploratória 1"
              accent="#3b82f6"
              insightSide
              insight="A distribuição é assimétrica à direita: a maioria dos aeroportos tem grau entre 3 e 5 e apenas 4 superam a média de 4,5 conexões. É a assinatura de uma rede de poucos hubs dominantes, em vez de conexões uniformes."
            >
              <GrauChart histData={histData} media={media} ego={egoAeroportos} />
            </ChartCard>

            <ChartCard
              title="Composição das conexões"
              sub="Barras empilhadas · tipo de aresta em cada aeroporto"
              tag="Exploratória 2"
              accent="#2dd4bf"
              insightSide
              insight="Decompõe o grau de cada aeroporto pelos três tipos de aresta do nosso modelo (regional, hub regional, hub nacional). Os maiores graus vêm de conexões de hub nacional: o alto grau resulta do papel de articulação entre regiões, não de muitas rotas locais."
            >
              <ComposicaoChart data={composicao} />
            </ChartCard>
          </RelationRow>

          {/* LINHA 2 — Explanatórias (empilhadas: ranking sozinho, comparação abaixo) */}
          <RelationRow
            cols={1}
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
              insightSide
              insight="Recife (9), Guarulhos (8) e Manaus (7) são os principais hubs da rede. Abaixo da média (4,5) ficam aeroportos periféricos como Goiânia (1) e Curitiba/Florianópolis (2). A cor revela a região a que cada hub pertence."
            >
              <HubsChart data={hubs} media={media} />
            </ChartCard>

            <ChartCard
              title="Comparação entre regiões"
              sub="3 indicadores · nº de aeroportos, arestas internas e grau médio"
              tag="Explanatória 2"
              accent="#a78bfa"
              insightSide
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
          <SectionHeader title="Grafo Completo da Rede" sub="Simulação de física interativa · selecione origem e destino para destacar o caminho mínimo · nós coloridos por região, arestas por tipo de conexão" />
          <InsightBanner accent="#3b82f6" title="O que isto mostra">
            A malha inteira: {glob.ordem} aeroportos e {glob.tamanho} conexões. Os nós são coloridos por região e se
            organizam por uma simulação de forças; a espessura/cor das arestas distingue conexões regionais, de hub
            regional e de hub nacional. Visualmente, os cinco hubs nacionais (REC, GRU, MAO, POA, BSB) formam o núcleo
            que costura as cinco regiões do país. Use o painel <strong>Caminho mínimo</strong> para escolher origem e
            destino: o nosso Dijkstra calcula o trajeto de menor custo na hora e o destaca sobre o grafo.
          </InsightBanner>
          {grafoDados
            ? <NetworkGraph grafoDados={grafoDados} />
            : <p style={{ color: '#94a3b8', padding: 24 }}>Dados indisponíveis. Execute python src/solve.py.</p>
          }
        </div>
      )}
    </div>
  )
}
