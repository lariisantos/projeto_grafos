import { useState, useEffect, useRef, useCallback } from 'react'
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

const NODE_R   = 22
const REPULSION = 6000
const SPRING_K  = 0.03
const REST_LEN  = 180
const GRAVITY   = 0.005
const DAMP      = 0.72
const MAX_TICKS = 400

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
              return (
                <line key={i}
                  x1={a.x} y1={a.y} x2={b.x} y2={b.y}
                  stroke={EDGE_COLORS[e.tipo] ?? '#1e3a5f'}
                  strokeWidth={e.peso * 1.8}
                  opacity={0.9}
                  strokeLinecap="round"
                />
              )
            })}

            {nodes.map(n => {
              const p   = posMap[n.id]
              if (!p) return null
              const cor = CORES[n.regiao] ?? '#64748b'
              return (
                <g key={n.id} className="node-g"
                  transform={`translate(${p.x},${p.y})`}
                  style={{ cursor: 'move' }}
                  onMouseDown={e => onNodeMouseDown(e, n.id)}
                  onMouseEnter={e => setTooltip({ node: n, x: e.clientX, y: e.clientY })}
                  onMouseMove={e => setTooltip(t => t ? { ...t, x: e.clientX, y: e.clientY } : null)}
                  onMouseLeave={() => setTooltip(null)}
                >
                  {/* glow ring */}
                  <circle r={NODE_R + 6} fill={cor} opacity={0.15} />
                  <circle r={NODE_R} fill={cor} stroke="rgba(255,255,255,.25)" strokeWidth={2}
                    style={{ filter: `drop-shadow(0 0 8px ${cor}88)` }} />
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
