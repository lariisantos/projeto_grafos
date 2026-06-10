import { useState, useEffect, useRef, useCallback, useMemo } from 'react'
import { CORES } from '../constants'

const EDGE_COLORS = {
  regional:     '#1e3a5f',
  regional_hub: '#475569',
  hub_nacional: '#3b82f6',
}

const EDGE_LABELS = {
  regional:     'Regional',
  regional_hub: 'Hub regional',
  hub_nacional: 'Hub nacional',
}

// Destaque do caminho mínimo (Dijkstra)
const PATH_EDGE    = '#fbbf24' // aresta da rota — âmbar, contrasta com azul/cinza
const ROLE_ORIGEM  = '#34d399' // origem  — verde
const ROLE_DESTINO = '#60a5fa' // destino — azul

const NODE_R   = 22
const REPULSION = 6000
const SPRING_K  = 0.03
const REST_LEN  = 180
const GRAVITY   = 0.005
const DAMP      = 0.72
const MAX_TICKS = 400

// ── Caminho mínimo no navegador ──────────────────────────────────────────
// O grafo da Parte 1 é pequeno (20 nós / 45 arestas), então rodamos o Dijkstra
// direto no front a cada seleção: qualquer par origem→destino funciona, sem
// depender de rotas pré-calculadas. Os pesos saem do próprio modelo (e.peso).
function buildAdjacency(edges) {
  const adj = {}
  edges.forEach(e => {
    const a = e.source, b = e.target, w = e.peso ?? 1
    ;(adj[a] ||= []).push({ to: b, w })
    ;(adj[b] ||= []).push({ to: a, w })
  })
  return adj
}

function dijkstra(adj, origem, destino) {
  if (!adj[origem] || !adj[destino]) return null
  const dist = {}, prev = {}, visited = {}
  for (const k in adj) dist[k] = Infinity
  dist[origem] = 0
  while (true) {
    let u = null, best = Infinity
    for (const k in dist) {
      if (!visited[k] && dist[k] < best) { best = dist[k]; u = k }
    }
    if (u === null || u === destino) break
    visited[u] = true
    for (const { to, w } of adj[u]) {
      const nd = dist[u] + w
      if (nd < dist[to]) { dist[to] = nd; prev[to] = u }
    }
  }
  if (dist[destino] === Infinity) return null
  const caminho = []
  let cur = destino
  while (cur !== undefined) { caminho.unshift(cur); cur = prev[cur] }
  return { custo: Math.round(dist[destino] * 100) / 100, caminho }
}

function initPositions(nodes, w, h) {
  const regions   = [...new Set(nodes.map(n => n.regiao))]
  const perRegion = {}
  nodes.forEach(n => { perRegion[n.regiao] = (perRegion[n.regiao] || 0) + 1 })
  const regionIdx = {}

  return nodes.map(n => {
    const ri  = regionIdx[n.regiao] = (regionIdx[n.regiao] ?? 0)
    regionIdx[n.regiao]++
    const rc    = perRegion[n.regiao]
    const rIdx  = regions.indexOf(n.regiao)
    const rTotal = regions.length
    const baseAngle = (rIdx / rTotal) * Math.PI * 2 - Math.PI / 2
    const spread    = (Math.PI * 2 / rTotal) * 0.7
    const angle     = baseAngle + (rc > 1 ? (ri / (rc - 1) - 0.5) * spread : 0)
    const dist      = Math.min(w, h) * 0.32
    return {
      id: n.id,
      x:  w / 2 + Math.cos(angle) * dist + (Math.random() - 0.5) * 24,
      y:  h / 2 + Math.sin(angle) * dist + (Math.random() - 0.5) * 24,
      vx: 0,
      vy: 0,
    }
  })
}

function runTick(posArr, edges, w, h) {
  const map = {}
  posArr.forEach(p => { map[p.id] = p; p.fx = 0; p.fy = 0 })
  const ids = posArr.map(p => p.id)

  for (let i = 0; i < ids.length; i++) {
    for (let j = i + 1; j < ids.length; j++) {
      const a = map[ids[i]], b = map[ids[j]]
      const dx = b.x - a.x, dy = b.y - a.y
      const d2 = dx * dx + dy * dy + 4
      const d  = Math.sqrt(d2)
      const f  = REPULSION / d2
      a.fx -= f * dx / d;  a.fy -= f * dy / d
      b.fx += f * dx / d;  b.fy += f * dy / d
    }
  }

  edges.forEach(e => {
    const a = map[e.source], b = map[e.target]
    if (!a || !b) return
    const dx = b.x - a.x, dy = b.y - a.y
    const d  = Math.sqrt(dx * dx + dy * dy) + 0.1
    const f  = SPRING_K * (d - REST_LEN)
    a.fx += f * dx / d;  a.fy += f * dy / d
    b.fx -= f * dx / d;  b.fy -= f * dy / d
  })

  posArr.forEach(p => {
    p.fx += GRAVITY * (w / 2 - p.x)
    p.fy += GRAVITY * (h / 2 - p.y)
    p.vx = (p.vx + p.fx) * DAMP
    p.vy = (p.vy + p.fy) * DAMP
    p.x  = Math.max(NODE_R + 4, Math.min(w - NODE_R - 4, p.x + p.vx))
    p.y  = Math.max(NODE_R + 4, Math.min(h - NODE_R - 4, p.y + p.vy))
  })
}

export default function NetworkGraph({ grafoDados }) {
  const { nodes, edges } = grafoDados

  const containerRef = useRef(null)
  const [size, setSize] = useState({ w: 800, h: 580 })
  const posRef       = useRef(null)
  const [renderPos, setRenderPos] = useState(null)
  const tickRef      = useRef(0)
  const animRef      = useRef(null)
  const draggingRef  = useRef(null)
  const panRef       = useRef(null)
  const [transform, setTransform] = useState({ x: 0, y: 0, scale: 1 })
  const transformRef = useRef({ x: 0, y: 0, scale: 1 })
  const [tooltip, setTooltip] = useState(null)

  // ── Caminho mínimo (origem / destino) ──
  const [origem, setOrigem]   = useState('')
  const [destino, setDestino] = useState('')

  const aeroportos = useMemo(
    () => nodes.map(n => ({ id: n.id, cidade: n.cidade }))
               .sort((a, b) => a.id.localeCompare(b.id)),
    [nodes],
  )
  const adjacency = useMemo(() => buildAdjacency(edges), [edges])

  const route = useMemo(() => {
    if (!origem || !destino) return { tipo: 'inicial' }
    if (origem === destino)  return { tipo: 'iguais' }
    const r = dijkstra(adjacency, origem, destino)
    if (!r) return { tipo: 'sem_caminho' }
    return { tipo: 'ok', custo: r.custo, caminho: r.caminho }
  }, [origem, destino, adjacency])

  // Conjuntos de destaque derivados da rota
  const hasRoute   = route.tipo === 'ok'
  const soloNode   = route.tipo === 'iguais' ? origem : null
  const pathIndex  = {}
  const pathEdges  = new Set()
  if (hasRoute) {
    route.caminho.forEach((id, i) => { pathIndex[id] = i })
    for (let i = 0; i < route.caminho.length - 1; i++) {
      pathEdges.add([route.caminho[i], route.caminho[i + 1]].sort().join('~'))
    }
  }
  const lastIdx = hasRoute ? route.caminho.length - 1 : -1

  const startSim = useCallback((w, h) => {
    cancelAnimationFrame(animRef.current)
    tickRef.current = 0
    const step = () => {
      if (tickRef.current >= MAX_TICKS || draggingRef.current || !posRef.current) return
      runTick(posRef.current, edges, w, h)
      tickRef.current++
      setRenderPos(posRef.current.map(p => ({ ...p })))
      animRef.current = requestAnimationFrame(step)
    }
    animRef.current = requestAnimationFrame(step)
  }, [edges])

  useEffect(() => {
    const { w, h } = size
    posRef.current = initPositions(nodes, w, h)
    setRenderPos(posRef.current.map(p => ({ ...p })))
    startSim(w, h)
    return () => cancelAnimationFrame(animRef.current)
  }, [size]) // eslint-disable-line

  useEffect(() => {
    if (!containerRef.current) return
    const ro = new ResizeObserver(entries => {
      for (const e of entries) {
        const w = Math.max(400, Math.floor(e.contentRect.width))
        const h = Math.round(w * 0.62)
        setSize(prev => (prev.w === w && prev.h === h ? prev : { w, h }))
      }
    })
    ro.observe(containerRef.current)
    return () => ro.disconnect()
  }, [])

  const onNodeMouseDown = useCallback((e, nodeId) => {
    e.stopPropagation()
    draggingRef.current = nodeId
    cancelAnimationFrame(animRef.current)
  }, [])

  const onSvgMouseDown = useCallback((e) => {
    if (e.target.closest?.('.node-g')) return
    panRef.current = { sx: e.clientX, sy: e.clientY, tx: transformRef.current.x, ty: transformRef.current.y }
  }, [])

  const onMouseMove = useCallback((e) => {
    if (draggingRef.current && posRef.current) {
      const svg  = containerRef.current?.querySelector('svg')
      if (!svg) return
      const rect = svg.getBoundingClientRect()
      const { x, y, scale } = transformRef.current
      const px = (e.clientX - rect.left - x) / scale
      const py = (e.clientY - rect.top  - y) / scale
      const p  = posRef.current.find(n => n.id === draggingRef.current)
      if (p) { p.x = px; p.y = py; p.vx = 0; p.vy = 0 }
      setRenderPos(posRef.current.map(q => ({ ...q })))
    } else if (panRef.current) {
      const next = {
        ...transformRef.current,
        x: panRef.current.tx + (e.clientX - panRef.current.sx),
        y: panRef.current.ty + (e.clientY - panRef.current.sy),
      }
      transformRef.current = next
      setTransform({ ...next })
    }
  }, [])

  const onMouseUp = useCallback(() => {
    if (draggingRef.current) {
      draggingRef.current = null
      startSim(size.w, size.h)
    }
    panRef.current = null
  }, [size, startSim])

  const onWheel = useCallback((e) => {
    e.preventDefault()
    const f    = e.deltaY < 0 ? 1.12 : 0.89
    const next = { ...transformRef.current, scale: Math.min(3, Math.max(0.3, transformRef.current.scale * f)) }
    transformRef.current = next
    setTransform({ ...next })
  }, [])

  const resetView = () => {
    const next = { x: 0, y: 0, scale: 1 }
    transformRef.current = next
    setTransform(next)
  }

  const posMap = {}
  if (renderPos) renderPos.forEach(p => { posMap[p.id] = p })

  const S = { color: '#94a3b8', fontSize: 12 }

  return (
    <div style={{ background: 'rgba(7,17,31,0.95)', borderRadius: 22, overflow: 'hidden' }}>

      {/* Toolbar */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '12px 18px', borderBottom: '1px solid rgba(148,163,184,.12)',
        flexWrap: 'wrap', gap: 10, background: 'rgba(15,23,42,0.7)',
      }}>
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
          {Object.entries(EDGE_LABELS).map(([tipo, label]) => (
            <span key={tipo} style={{ display: 'flex', alignItems: 'center', gap: 6, ...S }}>
              <span style={{ width: 22, height: 3, background: EDGE_COLORS[tipo], borderRadius: 2, display: 'inline-block' }} />
              {label}
            </span>
          ))}
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <span style={{ ...S, fontSize: 11, color: '#475569' }}>Arraste · Pan · Scroll zoom</span>
          <button onClick={resetView} style={{
            border: '1px solid rgba(148,163,184,.2)', background: 'rgba(30,41,59,.9)',
            color: '#cbd5e1', borderRadius: 8, padding: '5px 12px', cursor: 'pointer',
            fontSize: 12, fontWeight: 700, fontFamily: 'inherit',
          }}>Resetar</button>
        </div>
      </div>

      {/* Graph canvas */}
      <div
        ref={containerRef}
        style={{
          width: '100%', height: size.h, overflow: 'hidden', cursor: 'grab',
          position: 'relative',
          background: 'radial-gradient(ellipse at 50% 40%, rgba(59,130,246,0.07) 0%, transparent 65%), #07111f',
          backgroundImage: `
            radial-gradient(ellipse at 50% 40%, rgba(59,130,246,0.07) 0%, transparent 65%),
            linear-gradient(rgba(148,163,184,.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(148,163,184,.05) 1px, transparent 1px)
          `,
          backgroundSize: 'auto, 38px 38px, 38px 38px',
        }}
        onMouseMove={onMouseMove}
        onMouseUp={onMouseUp}
        onMouseLeave={onMouseUp}
        onWheel={onWheel}
      >
        {/* Menu de caminho mínimo (origem → destino via Dijkstra) */}
        <div
          style={mStyles.panel}
          onWheel={e => e.stopPropagation()}
          onMouseDown={e => e.stopPropagation()}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 }}>
            <h4 style={mStyles.titulo}>Caminho mínimo</h4>
            {(origem || destino) && (
              <button onClick={() => { setOrigem(''); setDestino('') }} style={mStyles.limpar}>limpar</button>
            )}
          </div>

          <label style={mStyles.label}>Origem</label>
          <select style={mStyles.select} value={origem} onChange={e => setOrigem(e.target.value)}>
            <option value="">— selecione —</option>
            {aeroportos.map(a => (
              <option key={a.id} value={a.id}>{a.id} · {a.cidade}</option>
            ))}
          </select>

          <label style={{ ...mStyles.label, marginTop: 8 }}>Destino</label>
          <select style={mStyles.select} value={destino} onChange={e => setDestino(e.target.value)}>
            <option value="">— selecione —</option>
            {aeroportos.map(a => (
              <option key={a.id} value={a.id}>{a.id} · {a.cidade}</option>
            ))}
          </select>

          <div style={mStyles.status}>
            {route.tipo === 'inicial' && (
              <span style={{ color: '#94a3b8' }}>
                Escolha origem e destino para destacar o caminho de menor custo (Dijkstra).
              </span>
            )}

            {route.tipo === 'iguais' && (
              <span style={{ color: '#cbd5e1' }}>
                <strong style={{ color: '#f0f9ff' }}>Origem e destino iguais.</strong><br />Custo: 0.0
              </span>
            )}

            {route.tipo === 'sem_caminho' && (
              <span style={{ color: '#f87171', fontWeight: 700 }}>
                Sem caminho viável entre os aeroportos.
              </span>
            )}

            {route.tipo === 'ok' && (
              <>
                <div style={{ display: 'flex', alignItems: 'baseline', gap: 6, marginBottom: 6 }}>
                  <span style={{ color: '#94a3b8' }}>Custo total</span>
                  <strong style={{ color: PATH_EDGE, fontSize: 16 }}>{route.custo}</strong>
                </div>
                <div style={{ color: '#e2e8f0', fontSize: 12, lineHeight: 1.5, fontWeight: 700 }}>
                  {route.caminho.map((id, i) => (
                    <span key={i}>
                      <span style={{
                        color: i === 0 ? ROLE_ORIGEM : i === lastIdx ? ROLE_DESTINO : PATH_EDGE,
                      }}>{id}</span>
                      {i < lastIdx && <span style={{ color: '#475569' }}> → </span>}
                    </span>
                  ))}
                </div>
                <div style={mStyles.legenda}>
                  {[['Origem', ROLE_ORIGEM], ['Destino', ROLE_DESTINO], ['Rota', PATH_EDGE]].map(([lbl, cor]) => (
                    <span key={lbl} style={{ display: 'inline-flex', alignItems: 'center', gap: 4 }}>
                      <span style={{ width: 8, height: 8, borderRadius: '50%', background: cor, display: 'inline-block' }} />
                      {lbl}
                    </span>
                  ))}
                </div>
              </>
            )}
          </div>
        </div>

        <svg
          width="100%"
          height={size.h}
          style={{ display: 'block', userSelect: 'none' }}
          onMouseDown={onSvgMouseDown}
        >
          <g transform={`translate(${transform.x},${transform.y}) scale(${transform.scale})`}>
            {edges.map((e, i) => {
              const a = posMap[e.source], b = posMap[e.target]
              if (!a || !b) return null
              const onPath = hasRoute && pathEdges.has([e.source, e.target].sort().join('~'))
              let stroke  = EDGE_COLORS[e.tipo] ?? '#1e3a5f'
              let width   = e.peso * 1.8
              let opacity = 0.9
              let glow
              if (hasRoute) {
                if (onPath) {
                  stroke = PATH_EDGE
                  width  = Math.max(e.peso * 1.8, 5.5)
                  opacity = 1
                  glow   = `drop-shadow(0 0 6px ${PATH_EDGE}aa)`
                } else {
                  opacity = 0.1
                }
              }
              return (
                <line key={i}
                  x1={a.x} y1={a.y} x2={b.x} y2={b.y}
                  stroke={stroke}
                  strokeWidth={width}
                  opacity={opacity}
                  strokeLinecap="round"
                  style={glow ? { filter: glow } : undefined}
                />
              )
            })}

            {nodes.map(n => {
              const p   = posMap[n.id]
              if (!p) return null
              const cor = CORES[n.regiao] ?? '#64748b'

              // papel do nó na rota destacada
              const role = !hasRoute ? null
                : pathIndex[n.id] === undefined ? 'dim'
                : pathIndex[n.id] === 0 ? 'origem'
                : pathIndex[n.id] === lastIdx ? 'destino'
                : 'meio'

              let ring = 'rgba(255,255,255,.25)', ringW = 2
              let gOpacity = 1, glowColor = cor, glowBlur = 8, ringFill = cor, ringFillOp = 0.15
              if (role === 'dim') {
                gOpacity = 0.2
              } else if (role) {
                ringW = 4.5; glowBlur = 15
                const c = role === 'origem' ? ROLE_ORIGEM : role === 'destino' ? ROLE_DESTINO : PATH_EDGE
                ring = c; glowColor = c; ringFill = c; ringFillOp = 0.28
              } else if (soloNode === n.id) {
                ringW = 4.5; glowBlur = 15
                ring = PATH_EDGE; glowColor = PATH_EDGE; ringFill = PATH_EDGE; ringFillOp = 0.28
              }

              return (
                <g key={n.id} className="node-g"
                  transform={`translate(${p.x},${p.y})`}
                  style={{ cursor: 'move', opacity: gOpacity }}
                  onMouseDown={e => onNodeMouseDown(e, n.id)}
                  onMouseEnter={e => setTooltip({ node: n, x: e.clientX, y: e.clientY })}
                  onMouseMove={e => setTooltip(t => t ? { ...t, x: e.clientX, y: e.clientY } : null)}
                  onMouseLeave={() => setTooltip(null)}
                >
                  {/* glow ring */}
                  <circle r={NODE_R + 6} fill={ringFill} opacity={ringFillOp} />
                  <circle r={NODE_R} fill={cor} stroke={ring} strokeWidth={ringW}
                    style={{ filter: `drop-shadow(0 0 ${glowBlur}px ${glowColor}88)` }} />
                  <text textAnchor="middle" dominantBaseline="middle"
                    fill="#fff" fontSize={11} fontWeight={900}
                    style={{ pointerEvents: 'none', userSelect: 'none', fontFamily: 'Inter,sans-serif' }}>
                    {n.id}
                  </text>
                  <text y={NODE_R + 15} textAnchor="middle"
                    fill="#e2e8f0" fontSize={10} fontWeight={600}
                    style={{
                      pointerEvents: 'none', userSelect: 'none', fontFamily: 'Inter,sans-serif',
                      paintOrder: 'stroke', stroke: '#07111f', strokeWidth: 5, strokeLinejoin: 'round',
                    }}>
                    {n.cidade}
                  </text>
                </g>
              )
            })}
          </g>
        </svg>

        {tooltip && (
          <div style={{
            position: 'fixed', pointerEvents: 'none', zIndex: 9999,
            left: tooltip.x + 14, top: tooltip.y + 14,
            background: 'rgba(2,6,23,.97)', border: '1px solid rgba(99,179,237,.25)',
            borderRadius: 14, padding: '10px 14px',
            boxShadow: '0 16px 40px rgba(0,0,0,.6)', fontSize: 13,
          }}>
            <p style={{ color: '#f0f9ff', fontWeight: 800, fontSize: 15, margin: '0 0 5px' }}>
              {tooltip.node.id} — {tooltip.node.cidade}
            </p>
            <p style={{ color: CORES[tooltip.node.regiao] ?? '#e5eefc', margin: '0 0 4px', fontSize: 12 }}>
              {tooltip.node.regiao}
            </p>
            <p style={{ color: '#94a3b8', margin: '0 0 2px', fontSize: 12 }}>
              Grau: <strong style={{ color: '#f0f9ff' }}>{tooltip.node.grau}</strong>
            </p>
            <p style={{ color: '#64748b', margin: 0, fontSize: 11 }}>
              Dens. ego: {tooltip.node.densidadeEgo?.toFixed(3)}
            </p>
          </div>
        )}
      </div>

      {/* Region legend */}
      <div style={{
        padding: '10px 18px', borderTop: '1px solid rgba(148,163,184,.1)',
        display: 'flex', flexWrap: 'wrap', gap: 14,
        background: 'rgba(15,23,42,0.7)',
      }}>
        {Object.entries(CORES).map(([reg, cor]) => (
          <span key={reg} style={{ display: 'flex', alignItems: 'center', gap: 7, fontSize: 12, color: '#94a3b8' }}>
            <span style={{ width: 10, height: 10, borderRadius: '50%', background: cor, display: 'inline-block', boxShadow: `0 0 6px ${cor}88` }} />
            {reg}
          </span>
        ))}
      </div>
    </div>
  )
}

const mStyles = {
  panel: {
    position: 'absolute', top: 12, left: 12, zIndex: 20, width: 226,
    background: 'rgba(2,6,23,0.92)', backdropFilter: 'blur(6px)',
    border: '1px solid rgba(99,179,237,.22)', borderRadius: 14,
    padding: '12px 14px', boxShadow: '0 16px 40px rgba(0,0,0,.5)',
    fontFamily: 'Inter,sans-serif',
  },
  titulo: {
    margin: 0, color: '#f0f9ff', fontSize: 13, fontWeight: 800,
    letterSpacing: '.01em',
  },
  limpar: {
    border: '1px solid rgba(148,163,184,.2)', background: 'rgba(30,41,59,.9)',
    color: '#94a3b8', borderRadius: 7, padding: '3px 9px', cursor: 'pointer',
    fontSize: 11, fontWeight: 700, fontFamily: 'inherit',
  },
  label: {
    display: 'block', fontSize: 10.5, fontWeight: 700, color: '#7c8aa0',
    textTransform: 'uppercase', letterSpacing: '.06em', marginBottom: 4,
  },
  select: {
    width: '100%', padding: '6px 8px', borderRadius: 8,
    border: '1px solid rgba(148,163,184,.25)', background: 'rgba(15,23,42,.95)',
    color: '#e2e8f0', fontSize: 12.5, fontFamily: 'inherit', cursor: 'pointer',
  },
  status: {
    marginTop: 12, paddingTop: 10, borderTop: '1px solid rgba(148,163,184,.14)',
    fontSize: 12, minHeight: 40, lineHeight: 1.45,
  },
  legenda: {
    display: 'flex', flexWrap: 'wrap', gap: 10, marginTop: 9,
    fontSize: 10.5, color: '#94a3b8',
  },
}
