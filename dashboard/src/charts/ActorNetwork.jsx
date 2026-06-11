import { useState, useEffect, useRef, useCallback } from 'react'

const NODE_BASE = 11
const REPULSION = 9000
const SPRING_K = 0.02
const REST_LEN = 150
const GRAVITY = 0.004
const DAMP = 0.74
const MAX_TICKS = 420

const COR_CENTRO = '#fbbf24'
const COR_NO = '#a78bfa'
const COR_ARESTA = 'rgba(167,139,250,0.28)'

function raioPorGrau(grau, min, max) {
  if (max === min) return NODE_BASE + 6
  return NODE_BASE + 16 * Math.sqrt((grau - min) / (max - min))
}

function initPositions(nodes, w, h) {
  return nodes.map((n, i) => {
    if (n.centro) return { id: n.id, x: w / 2, y: h / 2, vx: 0, vy: 0 }
    const ang = (i / nodes.length) * Math.PI * 2
    const dist = Math.min(w, h) * 0.36
    return {
      id: n.id,
      x: w / 2 + Math.cos(ang) * dist + (Math.random() - 0.5) * 30,
      y: h / 2 + Math.sin(ang) * dist + (Math.random() - 0.5) * 30,
      vx: 0, vy: 0,
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
      const d = Math.sqrt(d2)
      const f = REPULSION / d2
      a.fx -= f * dx / d; a.fy -= f * dy / d
      b.fx += f * dx / d; b.fy += f * dy / d
    }
  }
  edges.forEach(e => {
    const a = map[e.source], b = map[e.target]
    if (!a || !b) return
    const dx = b.x - a.x, dy = b.y - a.y
    const d = Math.sqrt(dx * dx + dy * dy) + 0.1
    const f = SPRING_K * (d - REST_LEN)
    a.fx += f * dx / d; a.fy += f * dy / d
    b.fx -= f * dx / d; b.fy -= f * dy / d
  })
  posArr.forEach(p => {
    p.fx += GRAVITY * (w / 2 - p.x)
    p.fy += GRAVITY * (h / 2 - p.y)
    p.vx = (p.vx + p.fx) * DAMP
    p.vy = (p.vy + p.fy) * DAMP
    p.x = Math.max(28, Math.min(w - 28, p.x + p.vx))
    p.y = Math.max(28, Math.min(h - 28, p.y + p.vy))
  })
}

export default function ActorNetwork({ rede }) {
  const { nodes, edges } = rede
  const graus = nodes.map(n => n.grau)
  const gMin = Math.min(...graus), gMax = Math.max(...graus)

  const containerRef = useRef(null)
  const [size, setSize] = useState({ w: 800, h: 560 })
  const posRef = useRef(null)
  const [renderPos, setRenderPos] = useState(null)
  const tickRef = useRef(0)
  const animRef = useRef(null)
  const draggingRef = useRef(null)
  const panRef = useRef(null)
  const [transform, setTransform] = useState({ x: 0, y: 0, scale: 1 })
  const transformRef = useRef({ x: 0, y: 0, scale: 1 })
  const [tooltip, setTooltip] = useState(null)

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
        const h = Math.round(w * 0.64)
        setSize(prev => (prev.w === w && prev.h === h ? prev : { w, h }))
      }
    })
    ro.observe(containerRef.current)
    return () => ro.disconnect()
  }, [])

  const onNodeMouseDown = useCallback((e, id) => {
    e.stopPropagation()
    draggingRef.current = id
    cancelAnimationFrame(animRef.current)
  }, [])

  const onSvgMouseDown = useCallback((e) => {
    if (e.target.closest?.('.node-g')) return
    panRef.current = { sx: e.clientX, sy: e.clientY, tx: transformRef.current.x, ty: transformRef.current.y }
  }, [])

  const onMouseMove = useCallback((e) => {
    if (draggingRef.current && posRef.current) {
      const svg = containerRef.current?.querySelector('svg')
      if (!svg) return
      const rect = svg.getBoundingClientRect()
      const { x, y, scale } = transformRef.current
      const px = (e.clientX - rect.left - x) / scale
      const py = (e.clientY - rect.top - y) / scale
      const p = posRef.current.find(n => n.id === draggingRef.current)
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
    if (draggingRef.current) { draggingRef.current = null; startSim(size.w, size.h) }
    panRef.current = null
  }, [size, startSim])

  const onWheel = useCallback((e) => {
    e.preventDefault()
    const f = e.deltaY < 0 ? 1.12 : 0.89
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

  return (
    <div style={{ background: 'rgba(7,17,31,0.95)', borderRadius: 22, overflow: 'hidden' }}>
      {/* toolbar */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '12px 18px', borderBottom: '1px solid rgba(148,163,184,.12)',
        flexWrap: 'wrap', gap: 10, background: 'rgba(15,23,42,0.7)',
      }}>
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', fontSize: 12, color: '#94a3b8' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ width: 12, height: 12, borderRadius: '50%', background: COR_CENTRO, display: 'inline-block' }} />
            Ator central
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ width: 12, height: 12, borderRadius: '50%', background: COR_NO, display: 'inline-block' }} />
            Colaborador (tamanho = grau total na rede)
          </span>
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <span style={{ fontSize: 11, color: '#475569' }}>Arraste · Pan · Scroll zoom</span>
          <button onClick={resetView} style={{
            border: '1px solid rgba(148,163,184,.2)', background: 'rgba(30,41,59,.9)',
            color: '#cbd5e1', borderRadius: 8, padding: '5px 12px', cursor: 'pointer',
            fontSize: 12, fontWeight: 700, fontFamily: 'inherit',
          }}>Resetar</button>
        </div>
      </div>

      {/* canvas */}
      <div
        ref={containerRef}
        style={{
          width: '100%', height: size.h, overflow: 'hidden', cursor: 'grab', position: 'relative',
          background: 'radial-gradient(ellipse at 50% 40%, rgba(167,139,250,0.08) 0%, transparent 65%), #07111f',
          backgroundImage: `
            radial-gradient(ellipse at 50% 40%, rgba(167,139,250,0.08) 0%, transparent 65%),
            linear-gradient(rgba(148,163,184,.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(148,163,184,.05) 1px, transparent 1px)`,
          backgroundSize: 'auto, 38px 38px, 38px 38px',
        }}
        onMouseMove={onMouseMove}
        onMouseUp={onMouseUp}
        onMouseLeave={onMouseUp}
        onWheel={onWheel}
      >
        <svg width="100%" height={size.h} style={{ display: 'block', userSelect: 'none' }} onMouseDown={onSvgMouseDown}>
          <g transform={`translate(${transform.x},${transform.y}) scale(${transform.scale})`}>
            {edges.map((e, i) => {
              const a = posMap[e.source], b = posMap[e.target]
              if (!a || !b) return null
              return (
                <line key={i} x1={a.x} y1={a.y} x2={b.x} y2={b.y}
                  stroke={COR_ARESTA} strokeWidth={Math.min(5, 1 + e.peso)} strokeLinecap="round" />
              )
            })}
            {nodes.map(n => {
              const p = posMap[n.id]
              if (!p) return null
              const r = raioPorGrau(n.grau, gMin, gMax)
              const cor = n.centro ? COR_CENTRO : COR_NO
              return (
                <g key={n.id} className="node-g" transform={`translate(${p.x},${p.y})`} style={{ cursor: 'move' }}
                  onMouseDown={e => onNodeMouseDown(e, n.id)}
                  onMouseEnter={e => setTooltip({ node: n, x: e.clientX, y: e.clientY })}
                  onMouseMove={e => setTooltip(t => t ? { ...t, x: e.clientX, y: e.clientY } : null)}
                  onMouseLeave={() => setTooltip(null)}>
                  <circle r={r + 5} fill={cor} opacity={0.15} />
                  <circle r={r} fill={cor} stroke="rgba(255,255,255,.3)" strokeWidth={n.centro ? 2.5 : 1.5}
                    style={{ filter: `drop-shadow(0 0 8px ${cor}88)` }} />
                  <text y={r + 13} textAnchor="middle" fill="#e2e8f0" fontSize={n.centro ? 12 : 10}
                    fontWeight={n.centro ? 800 : 600}
                    style={{
                      pointerEvents: 'none', userSelect: 'none', fontFamily: 'Inter,sans-serif',
                      paintOrder: 'stroke', stroke: '#07111f', strokeWidth: 4, strokeLinejoin: 'round',
                    }}>
                    {n.id.length > 18 ? n.id.slice(0, 17) + '…' : n.id}
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
            background: 'rgba(2,6,23,.97)', border: '1px solid rgba(167,139,250,.3)',
            borderRadius: 14, padding: '10px 14px', boxShadow: '0 16px 40px rgba(0,0,0,.6)', fontSize: 13,
          }}>
            <p style={{ color: '#f0f9ff', fontWeight: 800, fontSize: 14, margin: '0 0 4px' }}>{tooltip.node.id}</p>
            {tooltip.node.centro && (
              <p style={{ color: COR_CENTRO, margin: '0 0 3px', fontSize: 12, fontWeight: 700 }}>Ator central da amostra</p>
            )}
            <p style={{ color: '#94a3b8', margin: 0, fontSize: 12 }}>
              Colaboradores na rede: <strong style={{ color: '#f0f9ff' }}>{tooltip.node.grau}</strong>
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
