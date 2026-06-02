import { useState, useRef, useCallback, useEffect } from 'react'
import { CORES } from '../constants'

export default function RouteTree({ percursosDados }) {
  const { nodes: initNodes, edges, caminhos } = percursosDados
  const [nodes, setNodes]   = useState(() => initNodes.map(n => ({ ...n })))
  const [transform, setTransform] = useState({ x: 0, y: 0, scale: 1 })
  const transformRef = useRef({ x: 0, y: 0, scale: 1 })
  const draggingRef  = useRef(null)
  const dragOff      = useRef({ dx: 0, dy: 0 })
  const panRef       = useRef(null)
  const containerRef = useRef(null)
  const [size, setSize]     = useState({ w: 800, h: 460 })
  const [tooltip, setTooltip] = useState(null)

  useEffect(() => {
    if (!containerRef.current) return
    const ro = new ResizeObserver(entries => {
      for (const e of entries) {
        const w = Math.max(400, Math.floor(e.contentRect.width))
        setSize({ w, h: Math.round(w * 0.52) })
      }
    })
    ro.observe(containerRef.current)
    return () => ro.disconnect()
  }, [])

  const nodeMap = {}
  nodes.forEach(n => { nodeMap[n.id] = n })

  const onNodeMouseDown = useCallback((e, nodeId) => {
    e.stopPropagation()
    const { x, y, scale } = transformRef.current
    const rect = e.currentTarget.closest('svg').getBoundingClientRect()
    const svgX = (e.clientX - rect.left - x) / scale
    const svgY = (e.clientY - rect.top  - y) / scale
    const node = nodes.find(n => n.id === nodeId)
    dragOff.current = { dx: svgX - node.x, dy: svgY - node.y }
    draggingRef.current = nodeId
  }, [nodes])

  const onSvgMouseDown = useCallback((e) => {
    if (e.target.closest?.('.node-g')) return
    panRef.current = { sx: e.clientX, sy: e.clientY, tx: transformRef.current.x, ty: transformRef.current.y }
  }, [])

  const onMouseMove = useCallback((e) => {
    if (draggingRef.current) {
      const svg = containerRef.current?.querySelector('svg')
      if (!svg) return
      const rect = svg.getBoundingClientRect()
      const { x, y, scale } = transformRef.current
      const px = (e.clientX - rect.left - x) / scale - dragOff.current.dx
      const py = (e.clientY - rect.top  - y) / scale - dragOff.current.dy
      setNodes(prev => prev.map(n => n.id === draggingRef.current ? { ...n, x: px, y: py } : n))
    } else if (panRef.current) {
      const next = { ...transformRef.current, x: panRef.current.tx + (e.clientX - panRef.current.sx), y: panRef.current.ty + (e.clientY - panRef.current.sy) }
      transformRef.current = next
      setTransform({ ...next })
    }
  }, [])

  const onMouseUp = useCallback(() => { draggingRef.current = null; panRef.current = null }, [])

  const onWheel = useCallback((e) => {
    e.preventDefault()
    const f    = e.deltaY < 0 ? 1.12 : 0.89
    const next = { ...transformRef.current, scale: Math.min(3, Math.max(0.3, transformRef.current.scale * f)) }
    transformRef.current = next; setTransform({ ...next })
  }, [])

  const resetView = () => {
    const next = { x: 0, y: 0, scale: 1 }
    transformRef.current = next; setTransform(next)
    setNodes(initNodes.map(n => ({ ...n })))
  }

  return (
    <div style={{ background: 'rgba(7,17,31,0.95)', borderRadius: 22, overflow: 'hidden' }}>

      {/* Route cards */}
      <div style={{ padding: '16px 18px', borderBottom: '1px solid rgba(148,163,184,.12)', display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(260px,1fr))', gap: 12, background: 'rgba(15,23,42,0.7)' }}>
        {caminhos.map((c, i) => (
          <article key={i} style={{ borderLeft: `5px solid ${c.cor}`, border: '1px solid rgba(148,163,184,.16)', borderLeftColor: c.cor, borderRadius: 14, padding: '12px 14px', background: 'rgba(15,23,42,.6)' }}>
            <span style={{ display: 'inline-block', padding: '3px 10px', borderRadius: 999, background: c.cor, color: '#fff', fontSize: 11, fontWeight: 800, marginBottom: 8 }}>Percurso {i + 1}</span>
            <h3 style={{ fontSize: 17, fontWeight: 900, color: '#f0f9ff', margin: '0 0 5px' }}>{c.origem} → {c.destino}</h3>
            <p style={{ color: '#cbd5e1', fontSize: 12, lineHeight: 1.5, margin: '0 0 6px' }}>{c.caminho.join(' → ')}</p>
            <strong style={{ color: '#f0f9ff', fontSize: 13 }}>Custo: {c.custo}</strong>
          </article>
        ))}
      </div>

      {/* Toolbar */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 18px', borderBottom: '1px solid rgba(148,163,184,.08)', flexWrap: 'wrap', gap: 10, background: 'rgba(15,23,42,0.6)' }}>
        <span style={{ color: '#475569', fontSize: 12 }}>Arraste nós · Pan · Scroll zoom</span>
        <div style={{ display: 'flex', gap: 8 }}>
          {[['+ Zoom', 1.15], ['- Zoom', 0.87]].map(([label, f]) => (
            <button key={label} onClick={() => { const next = { ...transformRef.current, scale: Math.min(3, Math.max(0.3, transformRef.current.scale * f)) }; transformRef.current = next; setTransform({ ...next }) }} style={{ border: '1px solid rgba(148,163,184,.2)', background: 'rgba(30,41,59,.9)', color: '#cbd5e1', borderRadius: 8, padding: '5px 12px', cursor: 'pointer', fontSize: 12, fontWeight: 700, fontFamily: 'inherit' }}>{label}</button>
          ))}
          <button onClick={resetView} style={{ border: '1px solid rgba(148,163,184,.2)', background: 'rgba(30,41,59,.9)', color: '#cbd5e1', borderRadius: 8, padding: '5px 12px', cursor: 'pointer', fontSize: 12, fontWeight: 700, fontFamily: 'inherit' }}>Resetar</button>
        </div>
      </div>

      {/* SVG */}
      <div ref={containerRef} style={{ width: '100%', height: size.h, overflow: 'hidden', cursor: 'grab', position: 'relative', background: 'radial-gradient(ellipse at 50% 40%, rgba(59,130,246,0.06) 0%, transparent 65%), #07111f', backgroundImage: 'linear-gradient(rgba(148,163,184,.05) 1px,transparent 1px),linear-gradient(90deg,rgba(148,163,184,.05) 1px,transparent 1px)', backgroundSize: '38px 38px' }}
        onMouseMove={onMouseMove} onMouseUp={onMouseUp} onMouseLeave={onMouseUp} onWheel={onWheel}>
        <svg width="100%" height={size.h} style={{ display: 'block', userSelect: 'none' }} onMouseDown={onSvgMouseDown}>
          <g transform={`translate(${transform.x},${transform.y}) scale(${transform.scale})`}>
            {edges.map((e, i) => {
              const a = nodeMap[e.source], b = nodeMap[e.target]
              if (!a || !b) return null
              const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2 - 12
              return (
                <g key={i}>
                  <line x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke={e.color} strokeWidth={5} opacity={0.9} strokeLinecap="round" style={{ filter: `drop-shadow(0 0 5px ${e.color}66)` }} />
                  <text x={mx} y={my} textAnchor="middle" fontSize={10} fontWeight={800} fill="#e2e8f0" style={{ paintOrder: 'stroke', stroke: '#07111f', strokeWidth: 4, strokeLinejoin: 'round', pointerEvents: 'none', userSelect: 'none', fontFamily: 'Inter,sans-serif' }}>{e.weight}</text>
                </g>
              )
            })}
            {nodes.map(n => {
              const cor = CORES[n.regiao] ?? '#64748b'
              return (
                <g key={n.id} className="node-g" transform={`translate(${n.x},${n.y})`} style={{ cursor: 'move' }}
                  onMouseDown={e => onNodeMouseDown(e, n.id)}
                  onMouseEnter={e => setTooltip({ node: n, x: e.clientX, y: e.clientY })}
                  onMouseMove={e => setTooltip(t => t ? { ...t, x: e.clientX, y: e.clientY } : null)}
                  onMouseLeave={() => setTooltip(null)}>
                  <circle r={30} fill={cor} opacity={0.12} />
                  <circle r={28} fill="#f8fafc" stroke="#ffffff" strokeWidth={2.5} style={{ filter: 'drop-shadow(0 6px 14px rgba(2,6,23,.55))' }} />
                  <text y={5} textAnchor="middle" dominantBaseline="middle" fill="#0f172a" fontSize={13} fontWeight={900} style={{ pointerEvents: 'none', userSelect: 'none', fontFamily: 'Inter,sans-serif' }}>{n.id}</text>
                  <text y={50} textAnchor="middle" fill="#e5e7eb" fontSize={11} fontWeight={700} style={{ paintOrder: 'stroke', stroke: '#07111f', strokeWidth: 4, strokeLinejoin: 'round', pointerEvents: 'none', userSelect: 'none', fontFamily: 'Inter,sans-serif' }}>{n.label}</text>
                  <circle cx={22} cy={-22} r={7} fill={cor} stroke="rgba(255,255,255,.35)" strokeWidth={1.5} style={{ boxShadow: `0 0 6px ${cor}` }} />
                </g>
              )
            })}
          </g>
        </svg>
        {tooltip && (
          <div style={{ position: 'fixed', pointerEvents: 'none', zIndex: 9999, left: tooltip.x + 14, top: tooltip.y + 14, background: 'rgba(2,6,23,.97)', border: '1px solid rgba(99,179,237,.25)', borderRadius: 14, padding: '10px 14px', boxShadow: '0 16px 40px rgba(0,0,0,.6)', fontSize: 13 }}>
            <p style={{ color: '#f0f9ff', fontWeight: 800, fontSize: 15, margin: '0 0 4px' }}>{tooltip.node.id}</p>
            <p style={{ color: '#cbd5e1', margin: '0 0 3px', fontSize: 12 }}>{tooltip.node.label}</p>
            <p style={{ color: CORES[tooltip.node.regiao] ?? '#e5eefc', margin: 0, fontSize: 12 }}>{tooltip.node.regiao}</p>
          </div>
        )}
      </div>
    </div>
  )
}
