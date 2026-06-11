import { useEffect, useRef, useState, useCallback } from 'react'

/**
 * Renderiza o grafo de colaboração INTEIRO (todos os nós) em <canvas>.
 * O layout (posições x,y) é pré-calculado em Python e servido como JSON em
 * public/. Canvas + posições prontas evitam a simulação O(n²) no navegador,
 * permitindo desenhar dezenas de milhares de nós e arestas.
 *
 * Props:
 *  - src: URL do JSON em public/ (ex.: "grafo_parte2_15k.json")
 */
const COR_NO = '#a78bfa'
const COR_HUB = '#fbbf24'
const nf = (v) => Number(v).toLocaleString('pt-BR')

export default function ActorNetworkCanvas({ src }) {
  const wrapRef = useRef(null)
  const canvasRef = useRef(null)
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [erro, setErro] = useState(null)
  const [size, setSize] = useState({ w: 900, h: 600 })
  const [hover, setHover] = useState(null)

  const viewRef = useRef({ scale: 1, tx: 0, ty: 0 })
  const dragRef = useRef(null)
  const dirtyRef = useRef(false)
  const rafRef = useRef(0)

  // ── carrega o JSON do grafo ──
  useEffect(() => {
    let cancel = false
    setLoading(true); setErro(null)
    const url = (import.meta.env.BASE_URL || '/') + src
    fetch(url)
      .then(r => { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json() })
      .then(j => { if (!cancel) { setData(j); setLoading(false) } })
      .catch(e => { if (!cancel) { setErro(String(e)); setLoading(false) } })
    return () => { cancel = true }
  }, [src])

  // ── responsivo: acompanha a largura do container ──
  useEffect(() => {
    if (!wrapRef.current) return
    const ro = new ResizeObserver(entries => {
      for (const e of entries) {
        const w = Math.max(360, Math.floor(e.contentRect.width))
        const h = Math.round(w * 0.66)
        setSize(prev => (prev.w === w && prev.h === h ? prev : { w, h }))
      }
    })
    ro.observe(wrapRef.current)
    return () => ro.disconnect()
  }, [])

  // posições do grafo estão no espaço [0,1000]; encaixa na tela
  const fitView = useCallback(() => {
    const pad = 24
    const s = Math.min((size.w - pad * 2) / 1000, (size.h - pad * 2) / 1000)
    viewRef.current = {
      scale: s,
      tx: (size.w - 1000 * s) / 2,
      ty: (size.h - 1000 * s) / 2,
    }
    dirtyRef.current = true
  }, [size])

  useEffect(() => { if (data) fitView() }, [data, fitView])

  // ── desenho ──
  const draw = useCallback(() => {
    const cv = canvasRef.current
    if (!cv || !data) return
    const { w, h } = size
    const dpr = window.devicePixelRatio || 1
    if (cv.width !== Math.round(w * dpr)) cv.width = Math.round(w * dpr)
    if (cv.height !== Math.round(h * dpr)) cv.height = Math.round(h * dpr)
    const ctx = cv.getContext('2d')
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    ctx.clearRect(0, 0, w, h)

    const { scale, tx, ty } = viewRef.current
    const { x: X, y: Y, g, edges, labels, ids, meta } = data
    const gmax = meta.grauMax || 1
    const SX = (i) => X[i] * scale + tx
    const SY = (i) => Y[i] * scale + ty

    // arestas — opacidade e espessura crescem com o zoom: afastado fica suave
    // (densidade), aproximado fica nítido o suficiente para ver cada aresta.
    const eAlpha = Math.min(0.55, Math.max(0.05, scale * 0.12))
    ctx.strokeStyle = `rgba(167,139,250,${eAlpha})`
    ctx.lineWidth = Math.min(1.4, 0.5 + scale * 0.05)
    ctx.beginPath()
    for (let i = 0; i < edges.length; i += 2) {
      const a = edges[i], b = edges[i + 1]
      ctx.moveTo(SX(a), SY(a)); ctx.lineTo(SX(b), SY(b))
    }
    ctx.stroke()

    // nós — em um único path por cor (culling fora da tela)
    const raio = (i) => 1.1 + 4.6 * Math.sqrt(g[i] / gmax)
    ctx.fillStyle = COR_NO
    ctx.beginPath()
    for (let i = 0; i < X.length; i++) {
      const px = SX(i), py = SY(i)
      if (px < -8 || px > w + 8 || py < -8 || py > h + 8) continue
      const r = raio(i)
      ctx.moveTo(px + r, py); ctx.arc(px, py, r, 0, 6.283185)
    }
    ctx.fill()

    // hubs em destaque (cor + halo) e seus rótulos
    ctx.font = '700 11px Inter, system-ui, sans-serif'
    ctx.textAlign = 'center'
    for (const i of labels) {
      const px = SX(i), py = SY(i), r = Math.max(3, raio(i))
      ctx.beginPath(); ctx.fillStyle = COR_HUB
      ctx.arc(px, py, r, 0, 6.283185); ctx.fill()
      ctx.lineWidth = 3; ctx.strokeStyle = '#07111f'
      ctx.strokeText(ids[i], px, py - r - 4)
      ctx.fillStyle = '#f8fafc'
      ctx.fillText(ids[i], px, py - r - 4)
    }

    // nó sob o cursor: acende TODAS as arestas dele + os vizinhos
    if (hover != null) {
      ctx.strokeStyle = 'rgba(251,191,36,0.95)'
      ctx.lineWidth = Math.max(1, 0.7 + scale * 0.06)
      ctx.beginPath()
      const vizinhos = []
      for (let i = 0; i < edges.length; i += 2) {
        const a = edges[i], b = edges[i + 1]
        if (a === hover || b === hover) {
          ctx.moveTo(SX(a), SY(a)); ctx.lineTo(SX(b), SY(b))
          vizinhos.push(a === hover ? b : a)
        }
      }
      ctx.stroke()

      // vizinhos em destaque
      ctx.fillStyle = '#fcd34d'
      ctx.beginPath()
      for (const v of vizinhos) {
        const r = Math.max(2, raio(v))
        ctx.moveTo(SX(v) + r, SY(v)); ctx.arc(SX(v), SY(v), r, 0, 6.283185)
      }
      ctx.fill()

      // o próprio nó
      const px = SX(hover), py = SY(hover), r = Math.max(3.5, raio(hover))
      ctx.beginPath(); ctx.fillStyle = '#fff'
      ctx.arc(px, py, r + 1.5, 0, 6.283185); ctx.fill()
      ctx.beginPath(); ctx.fillStyle = COR_HUB
      ctx.arc(px, py, r, 0, 6.283185); ctx.fill()
    }
  }, [data, size, hover])

  // loop de render só quando "sujo"
  useEffect(() => {
    const tick = () => {
      if (dirtyRef.current) { dirtyRef.current = false; draw() }
      rafRef.current = requestAnimationFrame(tick)
    }
    rafRef.current = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(rafRef.current)
  }, [draw])

  useEffect(() => { dirtyRef.current = true }, [draw, hover])

  // ── interações ──
  const screenToGraph = (mx, my) => {
    const { scale, tx, ty } = viewRef.current
    return [(mx - tx) / scale, (my - ty) / scale]
  }

  // zoom com a roda: listener NATIVO não-passivo (senão o preventDefault é
  // ignorado e a página rola junto). Usa refs, então pode ser registrado uma vez.
  useEffect(() => {
    const cv = canvasRef.current
    if (!cv) return
    const handler = (e) => {
      e.preventDefault()
      const rect = cv.getBoundingClientRect()
      const mx = e.clientX - rect.left, my = e.clientY - rect.top
      const f = e.deltaY < 0 ? 1.15 : 0.87
      const v = viewRef.current
      const ns = Math.min(60, Math.max(0.05, v.scale * f))
      v.tx = mx - (mx - v.tx) * (ns / v.scale)   // mantém o ponto sob o cursor fixo
      v.ty = my - (my - v.ty) * (ns / v.scale)
      v.scale = ns
      dirtyRef.current = true
    }
    cv.addEventListener('wheel', handler, { passive: false })
    return () => cv.removeEventListener('wheel', handler)
  }, [])

  const onMouseDown = useCallback((e) => {
    const rect = canvasRef.current.getBoundingClientRect()
    dragRef.current = {
      sx: e.clientX, sy: e.clientY,
      tx: viewRef.current.tx, ty: viewRef.current.ty,
      moved: false,
    }
  }, [])

  const onMouseMove = useCallback((e) => {
    const rect = canvasRef.current.getBoundingClientRect()
    const mx = e.clientX - rect.left, my = e.clientY - rect.top
    if (dragRef.current) {
      dragRef.current.moved = true
      viewRef.current.tx = dragRef.current.tx + (e.clientX - dragRef.current.sx)
      viewRef.current.ty = dragRef.current.ty + (e.clientY - dragRef.current.sy)
      dirtyRef.current = true
      return
    }
    if (!data) return
    // hit-test: nó mais próximo do cursor (raio de tolerância em px)
    const { x: X, y: Y, g, meta } = data
    const { scale, tx, ty } = viewRef.current
    const gmax = meta.grauMax || 1
    let best = -1, bestD = 0
    for (let i = 0; i < X.length; i++) {
      const px = X[i] * scale + tx, py = Y[i] * scale + ty
      const r = (1.1 + 4.6 * Math.sqrt(g[i] / gmax)) + 3
      const dx = mx - px, dy = my - py, d2 = dx * dx + dy * dy
      if (d2 <= r * r && (best < 0 || d2 < bestD)) { best = i; bestD = d2 }
    }
    if (best !== (hover ?? -1)) setHover(best < 0 ? null : best)
    if (best >= 0) setTip({ x: e.clientX, y: e.clientY, i: best })
    else setTip(null)
  }, [data, hover])

  const [tip, setTip] = useState(null)
  const onMouseUp = useCallback(() => { dragRef.current = null }, [])
  const onMouseLeave = useCallback(() => { dragRef.current = null; setHover(null); setTip(null) }, [])

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
            <span style={{ width: 12, height: 12, borderRadius: '50%', background: COR_HUB, display: 'inline-block' }} />
            Hub (rotulado)
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
            <span style={{ width: 12, height: 12, borderRadius: '50%', background: COR_NO, display: 'inline-block' }} />
            Ator (tamanho = grau)
          </span>
          {data && (
            <span style={{ color: '#cbd5e1' }}>
              {nf(data.meta.n)} nós · {nf(data.meta.m)} arestas
            </span>
          )}
        </div>
        <div style={{ display: 'flex', gap: 8, alignItems: 'center' }}>
          <span style={{ fontSize: 11, color: '#475569' }}>Arraste · Scroll zoom · mouse no nó acende as arestas</span>
          <button onClick={fitView} style={{
            border: '1px solid rgba(148,163,184,.2)', background: 'rgba(30,41,59,.9)',
            color: '#cbd5e1', borderRadius: 8, padding: '5px 12px', cursor: 'pointer',
            fontSize: 12, fontWeight: 700, fontFamily: 'inherit',
          }}>Resetar</button>
        </div>
      </div>

      {/* canvas */}
      <div ref={wrapRef} style={{ width: '100%', height: size.h, position: 'relative', background: '#07111f' }}>
        {loading && (
          <p style={{ color: '#94a3b8', padding: 24, position: 'absolute', inset: 0 }}>
            Carregando grafo…
          </p>
        )}
        {erro && (
          <p style={{ color: '#fca5a5', padding: 24 }}>
            Não foi possível carregar <code>{src}</code> ({erro}). Rode <code>python src/solve.py</code> para gerá-lo.
          </p>
        )}
        <canvas
          ref={canvasRef}
          style={{ width: size.w, height: size.h, display: 'block', cursor: dragRef.current ? 'grabbing' : 'grab' }}
          onMouseDown={onMouseDown}
          onMouseMove={onMouseMove}
          onMouseUp={onMouseUp}
          onMouseLeave={onMouseLeave}
        />
        {tip && data && (
          <div style={{
            position: 'fixed', pointerEvents: 'none', zIndex: 9999,
            left: tip.x + 14, top: tip.y + 14,
            background: 'rgba(2,6,23,.97)', border: '1px solid rgba(167,139,250,.3)',
            borderRadius: 14, padding: '10px 14px', boxShadow: '0 16px 40px rgba(0,0,0,.6)', fontSize: 13,
          }}>
            <p style={{ color: '#f0f9ff', fontWeight: 800, fontSize: 14, margin: '0 0 4px' }}>{data.ids[tip.i]}</p>
            <p style={{ color: '#94a3b8', margin: 0, fontSize: 12 }}>
              Colaboradores: <strong style={{ color: '#f0f9ff' }}>{nf(data.g[tip.i])}</strong>
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
