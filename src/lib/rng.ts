// Seeded RNG. mulberry32 for uniform; Box-Muller for gauss.
// Every match seeds its own RNG so runs are reproducible & shareable.

export class RNG {
  private s: number;
  constructor(seed: number) {
    this.s = seed >>> 0;
  }

  /** Uniform [0,1). */
  next(): number {
    let t = (this.s += 0x6d2b79f5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  }

  /** Uniform [min,max). */
  range(min: number, max: number): number {
    return min + (max - min) * this.next();
  }

  /** Integer in [min,max] inclusive. */
  int(min: number, max: number): number {
    return Math.floor(this.range(min, max + 1));
  }

  /** Standard normal via Box-Muller. */
  gauss(): number {
    // avoid log(0)
    const u = Math.max(this.next(), 1e-9);
    const v = this.next();
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * v);
  }

  pick<T>(arr: readonly T[]): T {
    return arr[this.int(0, arr.length - 1)];
  }

  /** Pick k unique items from arr (Fisher-Yates partial). */
  sample<T>(arr: readonly T[], k: number): T[] {
    const copy = arr.slice();
    const n = Math.min(k, copy.length);
    for (let i = 0; i < n; i++) {
      const j = this.int(i, copy.length - 1);
      [copy[i], copy[j]] = [copy[j], copy[i]];
    }
    return copy.slice(0, n);
  }

  /** Choose by weights. */
  weighted<T>(items: readonly T[], weights: readonly number[]): T {
    const total = weights.reduce((a, b) => a + b, 0);
    let r = this.next() * total;
    for (let i = 0; i < items.length; i++) {
      r -= weights[i];
      if (r <= 0) return items[i];
    }
    return items[items.length - 1];
  }
}

export function randomSeed(): number {
  return (Math.random() * 0xffffffff) >>> 0;
}
