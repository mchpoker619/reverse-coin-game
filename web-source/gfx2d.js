// 2D 俯視繪圖（Canvas 2D），取代 three.js 的 GFX，介面相同。測試版推廣版本 請勿銷售利用
const GFX = (() => {
  const stage = document.getElementById("stage");
  const cv = document.createElement("canvas");
  cv.style.cssText = "display:block;width:100%;height:100%;touch-action:none";
  stage.prepend(cv);
  const ctx = cv.getContext("2d");
  const cam = {mode: "top", follow: false, tTheta: 0, theta: 0, zoom: 1};
  const mouse = {x: 0, z: 0, ok: false};
  let k = 10, ox = 0, oy = 0, dpr = 1, cw = 0, ch = 0;
  let genFieldCv = null;

  function resize() {
    dpr = Math.min(2, window.devicePixelRatio || 1);
    cw = stage.clientWidth; ch = stage.clientHeight;
    cv.width = Math.max(1, cw * dpr); cv.height = Math.max(1, ch * dpr);
    const m = 14, top = 54, bot = 40;                       // 上方留給工具列、下方留給提示
    const vb = document.getElementById("vbars"), res = vb ? vb.offsetWidth + 12 : 0;   // 右側直式跑條
    k = Math.min((cw - 2 * Math.max(m, res)) / (W + 2 * RAIL_T), (ch - top - bot) / (H + 2 * RAIL_T));
    ox = cw / 2; oy = top + (ch - top - bot) / 2;
  }
  window.addEventListener("resize", resize);
  const sx = x => ox + x * k, sy = z => oy + z * k;

  // 輸入
  const screenPt = {x: 0, y: 0};
  function pick(ev) {
    screenPt.x = ev.clientX; screenPt.y = ev.clientY;
    const r = cv.getBoundingClientRect();
    mouse.x = (ev.clientX - r.left - ox) / k; mouse.z = (ev.clientY - r.top - oy) / k; mouse.ok = true;
    return mouse;
  }
  cv.addEventListener("contextmenu", e => e.preventDefault());
  cv.addEventListener("pointerdown", e => { if (e.button !== 0) return; pick(e); try { cv.setPointerCapture(e.pointerId); } catch (er) {} Input.click(mouse.x, mouse.z, e.pointerType); });
  cv.addEventListener("pointerup", e => { pick(e); Input.up(); });
  cv.addEventListener("pointercancel", () => Input.up());
  cv.addEventListener("pointermove", e => { pick(e); Input.move(mouse.x, mouse.z, e.pointerType); });

  function clack() {}
  function buildPieces() { for (const p of G.pieces) { p.mesh = true; p.label = {hidden: true}; } }
  function refreshTextures() { genFieldCv = null; }
  function followTurn() {}
  function setMode() {}

  // ---------- 小工具
  function img(id, face) { return ASSET.coinImg[id + "-" + face] || genFace(id, face); }
  // 虛線圓點（往前流動）：輔助線、後拉線都用這個
  function dots(pts, col, w) {
    const r = Math.max(2.2, w * 0.62), sp = r * 3.6, off = (performance.now() / 1000 * 5.5 * k) % sp;
    let acc = 0, next = off;
    for (let i = 0; i < pts.length - 1; i++) {
      const ax = sx(pts[i][0]), ay = sy(pts[i][1]), bx = sx(pts[i + 1][0]), by = sy(pts[i + 1][1]), L = Math.hypot(bx - ax, by - ay);
      while (next <= acc + L) {
        const t = L ? (next - acc) / L : 0, x = ax + (bx - ax) * t, y = ay + (by - ay) * t;
        ctx.fillStyle = "rgba(0,0,0,.9)"; ctx.beginPath(); ctx.arc(x, y, r + 2, 0, Math.PI * 2); ctx.fill();
        ctx.fillStyle = col; ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fill();
        next += sp;
      }
      acc += L;
    }
  }
  function line(x1, z1, x2, z2, col, w) { dots([[x1, z1], [x2, z2]], col, w); }
  function solidLine(x1, z1, x2, z2, col, w) {
    ctx.lineCap = "round";
    ctx.strokeStyle = "rgba(0,0,0,.9)"; ctx.lineWidth = w + 4; ctx.beginPath(); ctx.moveTo(sx(x1), sy(z1)); ctx.lineTo(sx(x2), sy(z2)); ctx.stroke();
    ctx.strokeStyle = col; ctx.lineWidth = w; ctx.beginPath(); ctx.moveTo(sx(x1), sy(z1)); ctx.lineTo(sx(x2), sy(z2)); ctx.stroke();
  }
  function poly(pts, col, w) {
    if (pts.length < 2) return;
    return dots(pts.filter(([x, z]) => !G.selected || Math.hypot(x - G.selected.x, z - G.selected.z) > R + 0.3), col, w);
    ctx.lineCap = ctx.lineJoin = "round";
    for (const [c, lw] of [["rgba(0,0,0,.9)", w + 4], [col, w]]) {
      ctx.strokeStyle = c; ctx.lineWidth = lw; ctx.beginPath();
      pts.forEach(([x, z], i) => i ? ctx.lineTo(sx(x), sy(z)) : ctx.moveTo(sx(x), sy(z))); ctx.stroke();
    }
  }
  function ring(x, z, r, col, w, a0 = 0, a1 = Math.PI * 2) {
    ctx.strokeStyle = col; ctx.lineWidth = w; ctx.beginPath(); ctx.arc(sx(x), sy(z), r * k, a0, a1); ctx.stroke();
  }
  // 攻擊力：沿金幣外圍下緣弧線排列（白方白字藍框、黑方黑字黃框）
  function arcValue(x, z, txt, camp, alpha) {
    const fs = Math.max(10, 0.78 * k), rb = (R + 1.5) * k, rmid = rb - fs * 0.38;
    ctx.save(); ctx.globalAlpha = alpha;
    ctx.font = `900 ${fs}px "Noto Sans TC","PingFang TC","Microsoft JhengHei",sans-serif`;
    ctx.textAlign = "center"; ctx.textBaseline = "alphabetic"; ctx.lineJoin = "round";
    const chars = [...String(txt)], ws = chars.map(c => ctx.measureText(c).width + fs * 0.04);
    let th = Math.PI / 2 + ws.reduce((a, b) => a + b, 0) / rmid / 2;
    chars.forEach((c, i) => {
      const a = th - ws[i] / rmid / 2; th -= ws[i] / rmid;
      ctx.save(); ctx.translate(sx(x) + Math.cos(a) * rb, sy(z) + Math.sin(a) * rb); ctx.rotate(a - Math.PI / 2);
      ctx.lineWidth = fs * 0.24; ctx.strokeStyle = camp === "O" ? "#1f4fd1" : "#e4ff3a"; ctx.strokeText(c, 0, 0);
      ctx.fillStyle = camp === "O" ? "#ffffff" : "#15131c"; ctx.fillText(c, 0, 0); ctx.restore();
    });
    ctx.restore();
  }
  function drawCoin(p, x, z, opts = {}) {
    const {scale = 1, squash = 1, showDown = false, alpha = 1, rot = p.angle} = opts;
    const up = p.camp === "O" ? "o" : "x", down = up === "o" ? "x" : "o";
    const face = img(p.coin.id, showDown ? down : up);
    const size = 2 * R * 1.4 * k * scale;
    ctx.save(); ctx.globalAlpha = alpha;
    // 影子
    ctx.fillStyle = "rgba(0,0,0,.35)"; ctx.beginPath(); ctx.ellipse(sx(x) + 0.25 * k * scale, sy(z) + 0.35 * k * scale, R * k * scale, R * k * scale * Math.max(0.3, Math.abs(squash)), 0, 0, Math.PI * 2); ctx.fill();
    ctx.translate(sx(x), sy(z)); ctx.rotate(rot); ctx.scale(1, Math.max(0.06, Math.abs(squash)));
    // 側邊（厚度感）
    ctx.fillStyle = (showDown ? p.camp !== "O" : p.camp === "O") ? "#e6e3da" : "#1b1920";
    ctx.beginPath(); ctx.arc(0, 0, R * k * scale * 1.02, 0, Math.PI * 2); ctx.fill();
    if (face) ctx.drawImage(face, -size / 2, -size / 2, size, size);
    ctx.restore();
  }

  // ---------- 主繪圖
  function render(dt) {
    if (stage.clientWidth !== cw || stage.clientHeight !== ch) resize();
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    ctx.fillStyle = "#d8cdb8"; ctx.fillRect(0, 0, cw, ch);
    const shk = window.FX ? FX.shake : 0;                // 撞擊震動：整個畫面小幅抖動
    if (shk > 0.01) ctx.setTransform(dpr, 0, 0, dpr, (Math.random() - 0.5) * shk * 12 * dpr, (Math.random() - 0.5) * shk * 12 * dpr);
    // 桌面
    ctx.fillStyle = "#d8cdb8"; ctx.fillRect(0, 0, cw, ch);
    // 邊框
    const fx0 = sx(-W / 2), fy0 = sy(-H / 2), fw = W * k, fh = H * k, rt = RAIL_T * k;
    ctx.fillStyle = "rgba(0,0,0,.25)"; ctx.fillRect(fx0 - rt + 4, fy0 - rt + 6, fw + 2 * rt, fh + 2 * rt);
    ctx.fillStyle = "#6b4a2e"; ctx.fillRect(fx0 - rt, fy0 - rt, fw + 2 * rt, fh + 2 * rt);
    ctx.fillStyle = "#2e2840"; ctx.fillRect(fx0 - rt * 0.35, fy0 - rt * 0.35, fw + rt * 0.7, fh + rt * 0.7);
    // 場地
    const fieldImg = genFieldCv || (genFieldCv = fieldCanvas());
    ctx.drawImage(fieldImg, fx0, fy0, fw, fh);

    const ph = G.phase, battle = G.scene === "battle";
    const aiming = battle && ["aim", "power", "accuracy"].includes(ph);
    const s = G.selected;

    // 弱點（對手）
    const ori = ph === "orient" ? (G.orientQueue || [])[0] : null;
    if (ori) ring(ori.x, ori.z, R + 0.55, "#e4ff3a", 0.4 * k);
    if (aiming || ori || (G.tut && G.tut.k > 0 && ph === "select")) for (const p of G.pieces) {   // 教學第 2、3 課：選球時也顯示弱點
      if (ori ? p !== ori : (!p.alive || p.out || p.team === G.turn)) continue;
      for (const a0 of [p.angle, p.angle + Math.PI]) {
        ctx.strokeStyle = "#fff"; ctx.lineWidth = 0.65 * k; ctx.beginPath(); ctx.arc(sx(p.x), sy(p.z), (R + 0.42) * k, a0 - P.SPOT, a0 + P.SPOT); ctx.stroke();
        ctx.strokeStyle = "#ff2a2a"; ctx.lineWidth = 0.4 * k; ctx.beginPath(); ctx.arc(sx(p.x), sy(p.z), (R + 0.42) * k, a0 - P.SPOT, a0 + P.SPOT); ctx.stroke();
      }
    }

    // 瞄準預測
    if (aiming && s) {
      let ux = Math.cos(G.aim), uz = Math.sin(G.aim), hit = null, ex, ez;
      if (UI.guide) {
        const lvl = RULES.spin && !cur().cpu ? (G.spinLvl || 0) : 0;
        if (lvl) {
          const pw = ["aim", "power", "accuracy"].includes(ph) && G.power > 0.05 ? G.power : 0.6;
          const r = predictPath(s, G.aim, lvl * P.SPIN_STEP, P.VMIN + pw * (P.VMAX - P.VMIN));
          poly(r.pts, "#18e0ff", Math.max(2, 0.3 * k)); hit = r.hit; ex = r.x; ez = r.z; if (hit) { ux = r.dx; uz = r.dz; }
        } else {
          let best = 1e9;
          for (const q of onField()) {
            if (q === s) continue;
            const f1 = s.x - q.x, f2 = s.z - q.z, b = f1 * ux + f2 * uz, c = f1 * f1 + f2 * f2 - 4 * R * R, disc = b * b - c;
            if (disc < 0) continue; const t = -b - Math.sqrt(disc); if (t > 0 && t < best) { best = t; hit = q; }
          }
          const len = hit ? best : 60; ex = s.x + ux * len; ez = s.z + uz * len;
          line(s.x + ux * (R + 0.4), s.z + uz * (R + 0.4), ex, ez, "#18e0ff", Math.max(2, 0.3 * k));
        }
        if (hit) {
          ring(ex, ez, R, "#000", 0.45 * k); ring(ex, ez, R - 0.05, "#18e0ff", 0.2 * k);
          let nx = hit.x - ex, nz = hit.z - ez; const nl = Math.hypot(nx, nz) || 1; nx /= nl; nz /= nl;
          line(hit.x, hit.z, hit.x + nx * 7, hit.z + nz * 7, "#ff8a00", Math.max(2, 0.32 * k));
          const dot = ux * nx + uz * nz, cx = ux - nx * dot, cz = uz - nz * dot, cl = Math.hypot(cx, cz);
          if (cl > 0.05) line(ex, ez, ex + cx / cl * 6 * cl, ez + cz / cl * 6 * cl, "#7dff3a", Math.max(2, 0.26 * k));
        }
      }
      // 後拉橡皮筋：從金幣往拉的方向延伸，顏色依力量
      if (ph === "aim" && G.power > 0.01) {
        const bx = Math.cos(G.aim), bz = Math.sin(G.aim), L = R + G.power * P.PULL_MAX * 0.7;
        line(s.x - bx * L, s.z - bz * L, s.x - bx * R * 0.9, s.z - bz * R * 0.9, G.power > 0.85 ? "#ff4d4d" : G.power > 0.5 ? "#ffc21a" : "#4ade80", Math.max(4, 0.5 * k));   // 圓點往發射方向流動
        ctx.save(); ctx.font = `900 ${Math.max(12, 0.9 * k)}px sans-serif`; ctx.textAlign = "center"; ctx.lineWidth = 4; ctx.strokeStyle = "#000"; ctx.fillStyle = "#fff";
        const tx = sx(s.x - bx * (L + 1.2)), ty = sy(s.z - bz * (L + 1.2)) + 5;
        ctx.strokeText(Math.round(G.power * 100) + "%", tx, ty); ctx.fillText(Math.round(G.power * 100) + "%", tx, ty); ctx.restore();
      }
      // 三角形箭頭
      const big = !UI.guide, L = (big ? 2.1 : 2.2) * 0.25 * k, st = (big ? 1.3 : 0.6) * k, a = G.aim;   // 輔助線關閉時的箭頭再縮小 50%
      ctx.save(); ctx.translate(sx(s.x), sy(s.z)); ctx.rotate(a);
      if (big) { ctx.restore(); line(s.x + Math.cos(a) * R, s.z + Math.sin(a) * R, s.x + Math.cos(a) * (R + st / k), s.z + Math.sin(a) * (R + st / k), "#e4ff3a", 0.4 * k);
        ctx.save(); ctx.translate(sx(s.x), sy(s.z)); ctx.rotate(a); }
      const bx = R * k + st;
      ctx.fillStyle = "#000"; ctx.beginPath(); ctx.moveTo(bx + L + 3, 0); ctx.lineTo(bx - 2, L * 0.62 + 3); ctx.lineTo(bx - 2, -L * 0.62 - 3); ctx.fill();
      ctx.fillStyle = "#e4ff3a"; ctx.beginPath(); ctx.moveTo(bx + L, 0); ctx.lineTo(bx, L * 0.62); ctx.lineTo(bx, -L * 0.62); ctx.fill();
      ctx.restore();
    }

    // 金幣
    const order = G.pieces.slice().sort((a, b) => (a.unlocked && ph === "jump") - (b.unlocked && ph === "jump"));
    for (const p of order) {
      if (!p.alive) p.fade = Math.max(0, (p.fade ?? 1) - dt * 1.2); else p.fade = 1;
      if (p.fade <= 0.01) continue;
      let scale = 1, squash = 1, showDown = false;
      if (p.out && p.outT >= 0) { const h = Math.min(1, p.outT / 0.45); scale += 4 * h * (1 - h) * 0.35; }
      if (ph === "jump" && p.unlocked) {
        const jp = jumpPose(p, G.jumpT);
        scale = 1 + 0.6 * jp.h;
        squash = Math.cos(jp.a);
        showDown = squash < 0;                         // 翻到背面時顯示另一面
      } else if (p.unlocked && p.flipped && (ph === "duel" || !p.alive)) showDown = true;
      // 旋轉中光圈
      if (Math.abs(p.spin || 0) > 1 && p.alive && !p.out) {
        const w = Math.abs(p.spin);
        ctx.save(); ctx.globalAlpha = Math.min(0.9, 0.25 + w / 20);
        for (const a0 of [p.angle, p.angle + Math.PI]) ring(p.x, p.z, R + 0.33, "#ff4fd8", 0.43 * k, a0, a0 + Math.PI * 1.2 / 2);
        ctx.restore();
      }
      drawCoin(p, p.x, p.z, {scale, squash, showDown, alpha: p.fade * (p.out ? 0.5 : 1)});
      if (p.alive && !(ph === "jump" && p.unlocked)) {
        const camp = p.flipped && p.unlocked && ph === "duel" ? (p.camp === "O" ? "X" : "O") : p.camp;
        arcValue(p.x, p.z, pval(p), camp, p.out ? 0.55 : 1);
      }
    }

    // 選取圈＋出手旋轉指示
    const selOn = battle && s && s.alive && ["select", "aim", "power", "accuracy"].includes(ph);
    if (selOn) {
      ring(s.x, s.z, R + 0.55, "#e4ff3a", 0.4 * k);
      const lvl = G.spinLvl || 0;
      if (lvl && !cur().cpu) {
        const t = performance.now() / 1000 * 2.2 * lvl, span = Math.PI * 1.3, dir = Math.sign(lvl);
        const a0 = t, a1 = t + span * dir;
        ctx.save(); ctx.lineCap = "round";
        ctx.strokeStyle = "#000"; ctx.lineWidth = 0.5 * k + 3; ctx.beginPath(); ctx.arc(sx(s.x), sy(s.z), (R + 2) * k, Math.min(a0, a1), Math.max(a0, a1)); ctx.stroke();
        ctx.strokeStyle = "#ff4fd8"; ctx.lineWidth = 0.3 * k; ctx.beginPath(); ctx.arc(sx(s.x), sy(s.z), (R + 2) * k, Math.min(a0, a1), Math.max(a0, a1)); ctx.stroke();
        const hx = sx(s.x) + Math.cos(a1) * (R + 2) * k, hy = sy(s.z) + Math.sin(a1) * (R + 2) * k, ta = a1 + dir * Math.PI / 2;
        ctx.fillStyle = "#ff4fd8"; ctx.beginPath();
        ctx.moveTo(hx + Math.cos(ta) * 0.8 * k, hy + Math.sin(ta) * 0.8 * k);
        ctx.lineTo(hx + Math.cos(ta + 2.4) * 0.55 * k, hy + Math.sin(ta + 2.4) * 0.55 * k);
        ctx.lineTo(hx + Math.cos(ta - 2.4) * 0.55 * k, hy + Math.sin(ta - 2.4) * 0.55 * k); ctx.fill();
        ctx.restore();
      }
    }

    // 回場放置
    if (battle && ph === "place" && !locked() && G.placeQueue.length && mouse.ok) {
      const p = G.placeQueue[0];
      drawCoin(p, mouse.x, mouse.z, {alpha: 0.6, rot: p.home + (G.placeRot || 0)});
      ring(mouse.x, mouse.z, 2 * R, placeValid(mouse.x, mouse.z, p) ? "#4ade80" : "#f87171", 0.18 * k);
    }
    drawFX();
  }
  // 撞擊特效：衝擊波圈＋火花
  function drawFX() {
    if (!window.FX || !FX.sparks.length) return;
    ctx.save();
    for (const f of FX.sparks) {
      const u = f.t / f.life, hot = f.kind === "coin" && f.k > 0.9, x = sx(f.x), y = sy(f.z);
      const col = f.kind === "rail" ? "#ffc23a" : hot ? "#ff3d1f" : "#ffa02a";
      if (u < 0.3 && f.kind === "coin") {               // 撞擊瞬間的白色閃光
        const rr = R * k * (1 + f.k), gr = ctx.createRadialGradient(x, y, 0, x, y, rr);
        gr.addColorStop(0, "rgba(255,255,255,.95)"); gr.addColorStop(0.5, "rgba(255,230,150,.6)"); gr.addColorStop(1, "rgba(255,200,80,0)");
        ctx.globalAlpha = (1 - u / 0.3) * Math.min(1, 0.4 + f.k); ctx.fillStyle = gr; ctx.beginPath(); ctx.arc(x, y, rr, 0, Math.PI * 2); ctx.fill();
      }
      const rad = R * k * (0.9 + u * (1.4 + 1.8 * f.k)), lw = Math.max(2, (0.45 + 0.45 * f.k) * k * (1 - u));
      ctx.globalAlpha = (1 - u) * Math.min(1, 0.55 + f.k * 0.5);
      ctx.strokeStyle = "rgba(40,20,0,.55)"; ctx.lineWidth = lw + 2; ctx.beginPath(); ctx.arc(x, y, rad, 0, Math.PI * 2); ctx.stroke();
      ctx.strokeStyle = col; ctx.lineWidth = lw; ctx.beginPath(); ctx.arc(x, y, rad, 0, Math.PI * 2); ctx.stroke();
      ctx.globalAlpha = 1 - u; ctx.lineCap = "round"; ctx.lineWidth = Math.max(2, (0.22 + 0.25 * Math.min(1, f.k)) * k);
      for (const d of f.dirs) {                          // 火花：往外飛的短線
        const t1 = f.t, t0 = Math.max(0, f.t - 0.05);
        ctx.strokeStyle = col; ctx.beginPath(); ctx.moveTo(sx(f.x + d[0] * t0), sy(f.z + d[1] * t0)); ctx.lineTo(sx(f.x + d[0] * t1), sy(f.z + d[1] * t1)); ctx.stroke();
      }
    }
    ctx.restore();
  }
  resize();
  function toScreen(x, z) { const r = cv.getBoundingClientRect(); return [r.left + sx(x), r.top + sy(z)]; }
  function setField() { genFieldCv = null; resize(); }
  return {render, buildPieces, refreshTextures, followTurn, setMode, resize, clack, cam, mouse, toScreen, setField, screen: screenPt};
})();
