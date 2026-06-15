/* Browser Frogger demo — mirrors product/frogger.py for the presentation slide */
(function () {
  const TILE = 40;
  const COLS = 16;
  const ROWS = 17;
  const HUD = 44;
  const W = COLS * TILE;
  const H = HUD + ROWS * TILE;
  const FPS = 60;

  const C = {
    safe: '#22683a', water: '#1a4678', road: '#303038', goal: '#2d7a45',
    frog: '#3cc850', log: '#784828', text: '#dff0e8',
    cars: ['#e04040', '#dc9a20', '#4878dc', '#b450b4'],
  };

  const goalRows = new Set([1, 2]);
  const waterRows = new Set([4, 5, 7, 8, 10, 11]);
  const roadRows = new Set([13, 14]);
  const startRow = ROWS - 2;

  function rowY(r) { return HUD + r * TILE; }
  function colX(c) { return c * TILE + TILE / 2; }

  class Frog {
    constructor() { this.reset(); this.cooldown = 0; }
    reset() {
      this.col = Math.floor(COLS / 2);
      this.row = startRow;
      this.rideLog = null;
      this.rideSlot = null;
    }
    get centerX() {
      return this.rideLog ? this.rideLog.slotCenterX(this.rideSlot) : colX(this.col);
    }
    rect() {
      const s = TILE - 14, h = s / 2;
      const cx = this.centerX, cy = rowY(this.row) + TILE / 2;
      return { x: cx - h, y: cy - h, w: s, h: s };
    }
    tryHop(dc, dr, lanes) {
      if (this.cooldown > 0) return null;
      const nc = this.col + dc, nr = this.row + dr;
      if (nc < 0 || nc >= COLS || nr < 0 || nr >= ROWS) return null;
      this.col = nc; this.row = nr;
      this.rideLog = null; this.rideSlot = null;
      this.cooldown = 0.14;
      if (goalRows.has(nr) && lanes.markGoal(nr, nc)) return 'goal';
      if (waterRows.has(nr) && !lanes.attachFrog(this, nc, nr)) return 'drown';
      return null;
    }
    update(dt, lanes) {
      this.cooldown = Math.max(0, this.cooldown - dt);
      if (waterRows.has(this.row)) {
        if (!this.rideLog) return 'drown';
        const cx = this.rideLog.slotCenterX(this.rideSlot);
        if (cx < -TILE || cx > W + TILE || !this.rideLog.slotOnScreen(this.rideSlot)) return 'drown';
        this.col = Math.max(0, Math.min(COLS - 1, Math.round((cx - TILE / 2) / TILE)));
      } else {
        this.rideLog = null; this.rideSlot = null;
      }
      if (roadRows.has(this.row)) {
        const fr = this.rect();
        for (const car of lanes.carsInRow(this.row)) {
          if (hit(fr, car.rect())) return 'squash';
        }
      }
      return null;
    }
  }

  class Car {
    constructor(row, x, speed, color) {
      this.row = row; this.x = x; this.baseSpeed = speed; this.speed = speed;
      this.color = color;
      this.w = [TILE * 1.6, TILE * 2.2, TILE * 2.8][Math.floor(Math.random() * 3)];
    }
    rect() { return { x: this.x, y: rowY(this.row) + 5, w: this.w, h: TILE - 10 }; }
    update(dt) {
      this.x += this.speed * dt;
      if (this.speed > 0 && this.x > W + 20) this.x = -this.w - 20;
      else if (this.speed < 0 && this.x < -this.w - 20) this.x = W + 20;
    }
  }

  class Log {
    constructor(row, x, speed, slots) {
      this.row = row; this.x = x; this.baseVx = speed; this.vx = speed;
      this.slots = Math.max(1, Math.min(3, slots));
    }
    get length() { return this.slots * TILE; }
    rect() { return { x: this.x, y: rowY(this.row) + 5, w: this.length, h: TILE - 10 }; }
    slotCenterX(i) { return this.x + i * TILE + TILE / 2; }
    slotOnScreen(i) {
      const left = this.x + i * TILE;
      return left + TILE > 0 && left < W;
    }
    slotForCol(col) {
      const px = colX(col);
      for (let i = 0; i < this.slots; i++) {
        const left = this.x + i * TILE;
        if (left <= px && px < left + TILE) return i;
      }
      return null;
    }
    update(dt) {
      this.x += this.vx * dt;
      if (this.vx > 0 && this.x > W + 30) this.x = -this.length - 30;
      else if (this.vx < 0 && this.x < -this.length - 30) this.x = W + 30;
    }
  }

  class Lanes {
    constructor() {
      this.cars = []; this.logs = [];
      this.goals = {};
      for (const r of goalRows) {
        for (let c = 2; c < COLS - 2; c += 2) this.goals[`${r},${c}`] = false;
      }
      this.spawn();
    }
    spawn() {
      for (const row of roadRows) {
        const n = 3 + (row % 2), spd = row === 13 ? 95 : -110, gap = W / n;
        for (let i = 0; i < n; i++) {
          this.cars.push(new Car(row, i * gap + Math.random() * 40, spd,
            C.cars[Math.floor(Math.random() * C.cars.length)]));
        }
      }
      const specs = [[4, 70], [5, -85], [7, 95], [8, -75], [10, 80], [11, -100]];
      for (const [row, spd] of specs) {
        const gap = W / 2;
        for (let i = 0; i < 2; i++) {
          this.logs.push(new Log(row, i * gap, spd, 1 + Math.floor(Math.random() * 3)));
        }
      }
    }
    markGoal(row, col) {
      const sc = col % 2 === 0 ? col : col - 1;
      const k = `${row},${sc}`;
      if (k in this.goals && !this.goals[k]) { this.goals[k] = true; return true; }
      return false;
    }
    allGoalsFilled() { return Object.values(this.goals).every(Boolean); }
    resetGoals() { for (const k of Object.keys(this.goals)) this.goals[k] = false; }
    carsInRow(row) { return this.cars.filter(c => c.row === row); }
    logsOnRow(row) { return this.logs.filter(l => l.row === row); }
    attachFrog(frog, col, row) {
      for (const log of this.logsOnRow(row)) {
        const slot = log.slotForCol(col);
        if (slot !== null) { frog.rideLog = log; frog.rideSlot = slot; return true; }
      }
      return false;
    }
    update(dt) {
      this.cars.forEach(c => c.update(dt));
      this.logs.forEach(l => l.update(dt));
    }
  }

  function hit(a, b) {
    return a.x < b.x + b.w && a.x + a.w > b.x && a.y < b.y + b.h && a.y + a.h > b.y;
  }

  function draw(ctx, frog, lanes, score, lives, level, gameState, overlay) {
    ctx.fillStyle = '#0a1422';
    ctx.fillRect(0, 0, W, H);

    for (let row = 0; row < ROWS; row++) {
      const y = rowY(row);
      if (goalRows.has(row)) ctx.fillStyle = C.goal;
      else if (waterRows.has(row)) ctx.fillStyle = C.water;
      else if (roadRows.has(row)) ctx.fillStyle = C.road;
      else ctx.fillStyle = C.safe;
      ctx.fillRect(0, y, W, TILE);
    }

    for (const [key, filled] of Object.entries(lanes.goals)) {
      const [row, col] = key.split(',').map(Number);
      const x = col * TILE + 4, y = rowY(row) + 4;
      ctx.beginPath();
      ctx.ellipse(x + TILE - 4, y + (TILE - 8) / 2, TILE - 6, (TILE - 8) / 2, 0, 0, Math.PI * 2);
      ctx.fillStyle = filled ? '#64dc82' : 'transparent';
      ctx.fill();
      if (!filled) { ctx.strokeStyle = '#327a4a'; ctx.lineWidth = 2; ctx.stroke(); }
    }

    for (const log of lanes.logs) {
      const r = log.rect();
      ctx.fillStyle = C.log;
      roundRect(ctx, r.x, r.y, r.w, r.h, 6);
      ctx.fill();
      for (let i = 1; i < log.slots; i++) {
        const lx = log.x + i * TILE;
        ctx.strokeStyle = '#4a3018'; ctx.beginPath();
        ctx.moveTo(lx, r.y + 3); ctx.lineTo(lx, r.y + r.h - 3); ctx.stroke();
      }
    }

    for (const car of lanes.cars) {
      const r = car.rect();
      ctx.fillStyle = car.color;
      roundRect(ctx, r.x, r.y, r.w, r.h, 4);
      ctx.fill();
      const hx = car.speed > 0 ? r.x + r.w - 6 : r.x + 6;
      ctx.fillStyle = '#fff5b4';
      ctx.beginPath();
      ctx.arc(hx, r.y + r.h / 2 - 4, 3, 0, Math.PI * 2);
      ctx.arc(hx, r.y + r.h / 2 + 4, 3, 0, Math.PI * 2);
      ctx.fill();
    }

    if (gameState !== 'title') {
      const fr = frog.rect();
      ctx.fillStyle = C.frog;
      ctx.beginPath();
      ctx.ellipse(fr.x + fr.w / 2, fr.y + fr.h / 2, fr.w / 2, fr.h / 2, 0, 0, Math.PI * 2);
      ctx.fill();
      const cx = fr.x + fr.w / 2;
      ctx.fillStyle = '#e0f0ff';
      ctx.beginPath();
      ctx.arc(cx - 7, fr.y + 9, 4, 0, Math.PI * 2);
      ctx.arc(cx + 7, fr.y + 9, 4, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.fillStyle = '#121820';
    ctx.fillRect(0, 0, W, HUD);
    ctx.fillStyle = C.text;
    ctx.font = '16px monospace';
    ctx.fillText(`Score ${score}   Lives ${lives}   Level ${level}`, 12, 28);

    if (overlay) {
      ctx.fillStyle = 'rgba(0,0,0,0.55)';
      ctx.fillRect(0, 0, W, H);
      ctx.fillStyle = C.text;
      ctx.font = 'bold 28px monospace';
      ctx.textAlign = 'center';
      ctx.fillText(overlay.title, W / 2, H / 2 - 10);
      if (overlay.sub) {
        ctx.font = '14px monospace';
        ctx.fillStyle = '#9ab8a8';
        ctx.fillText(overlay.sub, W / 2, H / 2 + 22);
      }
      ctx.textAlign = 'left';
    }
  }

  function roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath();
    ctx.moveTo(x + r, y);
    ctx.arcTo(x + w, y, x + w, y + h, r);
    ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r);
    ctx.arcTo(x, y, x + w, y, r);
    ctx.closePath();
  }

  window.initFroggerDemo = function (canvas) {
    const ctx = canvas.getContext('2d');
    canvas.width = W;
    canvas.height = H;

    let frog = new Frog();
    let lanes = new Lanes();
    let score = 0, lives = 3, level = 1;
    let gameState = 'title';
    let deadTimer = 0;
    let raf = null;
    let last = 0;
    let onKey = null;

    function overlay() {
      if (gameState === 'title') return { title: 'FROGGER', sub: 'Space to start' };
      if (gameState === 'dead') return { title: 'SPLAT!', sub: 'Space to continue' };
      if (gameState === 'win') return { title: `Level ${level - 1} clear!`, sub: 'Space for next' };
      if (gameState === 'gameover') return { title: 'GAME OVER', sub: 'Space to retry' };
      return null;
    }

    function handleHop(dc, dr) {
      if (gameState !== 'play') return;
      const hop = frog.tryHop(dc, dr, lanes);
      if (hop === 'goal') {
        score += 100 + frog.row * 10;
        frog.reset();
        if (lanes.allGoalsFilled()) {
          level++;
          lanes.resetGoals();
          lanes.cars.forEach(c => c.baseSpeed *= 1.08);
          lanes.logs.forEach(l => l.baseVx *= 1.08);
          gameState = 'win';
        }
      } else if (hop === 'drown') {
        lives--;
        frog.reset();
        gameState = lives <= 0 ? 'gameover' : 'dead';
        deadTimer = 1.2;
      }
    }

    function onDeath() {
      lives--;
      frog.reset();
      if (lives <= 0) gameState = 'gameover';
      else { gameState = 'dead'; deadTimer = 1.2; }
    }

    function frame(ts) {
      const dt = Math.min(0.05, (ts - last) / 1000 || 0);
      last = ts;

      if (gameState === 'play') {
        const mult = 1 + (level - 1) * 0.12;
        lanes.cars.forEach(c => c.speed = c.baseSpeed * mult);
        lanes.logs.forEach(l => l.vx = l.baseVx * mult);
        lanes.update(dt);
        const death = frog.update(dt, lanes);
        if (death) onDeath();
      } else if (gameState === 'dead') {
        deadTimer -= dt;
        if (deadTimer <= 0) gameState = 'play';
      }

      draw(ctx, frog, lanes, score, lives, level, gameState, overlay());
      raf = requestAnimationFrame(frame);
    }

    function bindKeys() {
      onKey = (e) => {
        if (gameState === 'title' && (e.code === 'Space' || e.code === 'Enter')) {
          e.preventDefault(); gameState = 'play'; return;
        }
        if (gameState === 'dead' && (e.code === 'Space' || e.code === 'Enter')) {
          e.preventDefault(); gameState = 'play'; frog.reset(); return;
        }
        if (gameState === 'win' && (e.code === 'Space' || e.code === 'Enter')) {
          e.preventDefault(); gameState = 'play'; frog.reset(); return;
        }
        if (gameState === 'gameover' && (e.code === 'Space' || e.code === 'Enter')) {
          e.preventDefault();
          score = 0; lives = 3; level = 1;
          frog = new Frog(); lanes = new Lanes();
          gameState = 'title';
          return;
        }
        if (gameState === 'play') {
          if (e.code === 'ArrowUp' || e.code === 'KeyW') { e.preventDefault(); handleHop(0, -1); }
          if (e.code === 'ArrowDown' || e.code === 'KeyS') { e.preventDefault(); handleHop(0, 1); }
          if (e.code === 'ArrowLeft' || e.code === 'KeyA') { e.preventDefault(); handleHop(-1, 0); }
          if (e.code === 'ArrowRight' || e.code === 'KeyD') { e.preventDefault(); handleHop(1, 0); }
        }
      };
      window.addEventListener('keydown', onKey);
    }

    return {
      start() {
        if (raf) return;
        last = 0;
        bindKeys();
        raf = requestAnimationFrame(frame);
      },
      stop() {
        if (raf) cancelAnimationFrame(raf);
        raf = null;
        if (onKey) window.removeEventListener('keydown', onKey);
        onKey = null;
      },
    };
  };
})();
