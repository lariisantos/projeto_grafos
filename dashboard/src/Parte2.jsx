import { useState } from 'react'
import ChartCard from './components/ChartCard'
import { MetricCard, TabBtn, SectionHeader, RelationRow, InsightBanner } from './components/ui'
import Parte2DegreeChart from './charts/Parte2DegreeChart'
import Parte2RankingChart from './charts/Parte2RankingChart'
import Parte2Heatmap from './charts/Parte2Heatmap'
import ActorNetworkCanvas from './charts/ActorNetworkCanvas'
import { DATA_PARTE2 } from './data_parte2'

const nf = (v) => Number(v).toLocaleString('pt-BR')

export default function Parte2() {
  const [tab, setTab] = useState('analise')
  const { resumo, heatmap, generos, desempenho = {} } = DATA_PARTE2

  return (
    <div>
      {/* HERO */}
      <div style={{ padding: '36px 0 40px' }}>
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: 8,
          background: 'rgba(167,139,250,.12)', border: '1px solid rgba(167,139,250,.3)',
          color: '#c4b5fd', borderRadius: 999, fontSize: 12, fontWeight: 700,
          letterSpacing: '.08em', textTransform: 'uppercase', padding: '5px 14px', marginBottom: 18,
        }}>
          Parte 2 · Dataset Netflix
        </div>
        <h1 style={{
          fontSize: 'clamp(32px,5vw,58px)', fontWeight: 900, letterSpacing: '-.05em', lineHeight: 1.05,
          background: 'linear-gradient(135deg,#f0f9ff 30%,#c4b5fd 60%,#f0abfc 100%)',
          WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text',
        }}>
          Rede de Colaboração<br />de Atores
        </h1>
        <p style={{ color: '#94a3b8', marginTop: 12, fontSize: 16, maxWidth: 640, lineHeight: 1.6 }}>
          Grafo construído a partir do catálogo Netflix: cada nó é um ator e cada aresta liga atores que
          atuaram juntos. São {nf(resumo.ordem)} atores e {nf(resumo.tamanho)} colaborações.
        </p>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(160px,1fr))', gap: 14, marginTop: 32 }}>
          <MetricCard value={nf(resumo.ordem)} label="Atores (nós)" accent="#a78bfa" />
          <MetricCard value={nf(resumo.tamanho)} label="Colaborações (arestas)" accent="#2dd4bf" />
          <MetricCard value={nf(resumo.grauMedio)} label="Grau médio" accent="#3b82f6" />
          <MetricCard value={resumo.grauMax} label="Grau máximo" accent="#fbbf24" />
          <MetricCard value={resumo.atorTop} label={`Mais conectado · ${resumo.atorTopGrau} parcerias`} accent="#f472b6" />
        </div>
      </div>

      {/* TABS */}
      <nav style={{ display: 'flex', gap: 2, borderBottom: '1px solid rgba(148,163,184,.16)', marginBottom: 32 }}>
        <TabBtn label="Análise da Rede"      active={tab === 'analise'} onClick={() => setTab('analise')} />
        <TabBtn label="Grafo de Colaboração" active={tab === 'grafo'}   onClick={() => setTab('grafo')} />
      </nav>

      {/* ABA ANALISE */}
      {tab === 'analise' && (
        <div style={{ animation: 'fadeUp .28s ease' }}>
          <SectionHeader
            title="Distribuição e Concentração da Colaboração"
            sub="Como as parcerias se distribuem entre os atores e quem concentra mais conexões"
          />

          <RelationRow
            cols={1}
            eyebrow="Distribuição × concentração"
            accent="#a78bfa"
            title="Quantos colaboradores cada ator tem — e quem lidera"
            relation="o histograma mostra o FORMATO da distribuição (eixo Y em escala log): a imensa maioria dos atores tem pouquíssimos colaboradores e só um punhado forma a cauda. O ranking abaixo NOMEIA exatamente quem está nessa cauda — os atores mais colaborativos do catálogo."
          >
            <ChartCard
              title="Distribuição dos graus"
              sub="Histograma por faixa de grau · eixo Y em escala logarítmica · filtre por gênero"
              tag="Exploratória"
              accent="#a78bfa"
              insight={`Mais de 30 mil atores (de ${nf(resumo.ordem)}) têm no máximo 22 colaboradores, enquanto pouquíssimos passam de 200. É a cauda longa típica de redes de colaboração — por isso o eixo Y usa escala logarítmica, para a cauda ficar visível. Filtrar por gênero mostra a distribuição só dos atores daquele gênero.`}
            >
              <Parte2DegreeChart generos={generos} />
            </ChartCard>

            <ChartCard
              title="Ranking dos atores mais conectados"
              sub="Barra ordenada · top 20 por colaboradores únicos · filtre por gênero (comédia, drama…)"
              tag="Explanatória"
              accent="#fbbf24"
              insight={`${resumo.atorTop} (${resumo.atorTopGrau}), Samuel L. Jackson (239) e dubladores de anime como Takahiro Sakurai (228) lideram no geral. Troque o gênero para ver quem domina cada nicho — ex.: em Comédia, ${resumo.atorTop} segue no topo, mostrando atores que transitam entre vários gêneros.`}
            >
              <Parte2RankingChart generos={generos} />
            </ChartCard>
          </RelationRow>

          <div style={{ marginBottom: 30 }}>
            <ChartCard
              title="Distância entre os maiores hubs"
              sub="Heatmap · saltos mínimos (BFS) entre os 12 atores mais conectados · filtre por nº de saltos"
              tag="Explanatória"
              accent="#2dd4bf"
              insight="Mesmo com dezenas de milhares de atores, os maiores hubs estão a poucos saltos uns dos outros — o efeito 'mundo pequeno'. Anupam Kher chega a Shah Rukh Khan em 1 salto e até a dubladores de anime em cerca de 4. Células ∞ indicariam atores em componentes separadas da rede."
            >
              <Parte2Heatmap heatmap={heatmap} />
            </ChartCard>
          </div>
        </div>
      )}

      {/* TABELA DE DESEMPENHO */}
      {tab === 'analise' && Object.keys(desempenho).length > 0 && (
        <div style={{ marginBottom: 30 }}>
          <SectionHeader
            title="Métricas de Desempenho"
            sub="Tempo de execução dos algoritmos sobre o grafo de colaboração de atores"
          />
          <InsightBanner accent="#f97316" title="Como interpretar">
            Cada algoritmo foi executado a partir de um mesmo nó de origem. BFS e DFS percorrem
            a rede sem pesos; Dijkstra e Bellman-Ford calculam caminhos mínimos considerando
            os pesos das arestas. O maior tempo do Bellman-Ford é esperado: sua complexidade
            O(V·E) é maior que a do Dijkstra com heap.
          </InsightBanner>
          <div style={{
            background: 'rgba(15,23,42,0.82)', border: '1px solid rgba(148,163,184,0.16)',
            borderRadius: 16, overflow: 'hidden',
          }}>
            <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
              <thead>
                <tr style={{ borderBottom: '1px solid rgba(148,163,184,0.16)' }}>
                  {['Algoritmo', 'Tempo (ms)', 'Tempo (s)', 'Desempenho relativo'].map(h => (
                    <th key={h} style={{
                      padding: '14px 20px', textAlign: 'left',
                      fontSize: 11, fontWeight: 800, letterSpacing: '.07em',
                      textTransform: 'uppercase', color: '#64748b',
                    }}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {(() => {
                  const entradas = Object.entries(desempenho)
                  const max = Math.max(...entradas.map(([, v]) => v))
                  const CORES_ALGO = { BFS: '#3b82f6', DFS: '#2dd4bf', Dijkstra: '#fbbf24', 'Bellman-Ford': '#f472b6' }
                  return entradas.map(([algo, seg], i) => {
                    const pct = Math.round((seg / max) * 100)
                    const cor = CORES_ALGO[algo] || '#94a3b8'
                    return (
                      <tr key={algo} style={{
                        borderBottom: i < entradas.length - 1 ? '1px solid rgba(148,163,184,0.08)' : 'none',
                        transition: 'background .15s',
                      }}
                        onMouseEnter={e => e.currentTarget.style.background = 'rgba(148,163,184,0.05)'}
                        onMouseLeave={e => e.currentTarget.style.background = 'transparent'}
                      >
                        <td style={{ padding: '14px 20px' }}>
                          <span style={{
                            display: 'inline-block', width: 10, height: 10,
                            borderRadius: '50%', background: cor, marginRight: 10,
                            verticalAlign: 'middle',
                          }} />
                          <span style={{ color: '#e5eefc', fontWeight: 700 }}>{algo}</span>
                        </td>
                        <td style={{ padding: '14px 20px', color: '#cbd5e1', fontVariantNumeric: 'tabular-nums' }}>
                          {(seg * 1000).toFixed(1)}
                        </td>
                        <td style={{ padding: '14px 20px', color: '#94a3b8', fontVariantNumeric: 'tabular-nums' }}>
                          {seg.toFixed(4)}
                        </td>
                        <td style={{ padding: '14px 20px', minWidth: 180 }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                            <div style={{
                              flex: 1, height: 6, background: 'rgba(148,163,184,0.12)',
                              borderRadius: 3, overflow: 'hidden',
                            }}>
                              <div style={{
                                height: '100%', width: `${pct}%`,
                                background: `linear-gradient(90deg, ${cor}, ${cor}99)`,
                                borderRadius: 3, transition: 'width .4s ease',
                              }} />
                            </div>
                            <span style={{ fontSize: 12, color: '#64748b', width: 36, textAlign: 'right' }}>
                              {pct}%
                            </span>
                          </div>
                        </td>
                      </tr>
                    )
                  })
                })()}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* ABA GRAFO */}
      {tab === 'grafo' && (
        <div style={{ animation: 'fadeUp .28s ease' }}>
          <SectionHeader
            title="Grafo de Colaboração — 15 mil atores"
            sub="Núcleo dos 15.000 atores mais conectados (layout pré-calculado) · arraste e scroll para zoom"
          />
          <InsightBanner accent="#a78bfa" title="O que isto mostra">
            A rede com os 15.000 atores mais conectados e as 172.904 colaborações entre eles. O layout foi
            calculado por um algoritmo de forças (Fruchterman-Reingold) e desenhado em Canvas para dar conta de
            todos os nós. A nuvem densa no centro é o efeito “mundo pequeno”: poucos hubs (em destaque) costuram
            atores de muitas indústrias diferentes. Passe o mouse para ver o nome e o grau de cada ator.
          </InsightBanner>
          <ActorNetworkCanvas src="grafo_parte2_15k.json" />
        </div>
      )}
    </div>
  )
}
