// The visualiser's random numbers: one shared stream, like the Python `random` module the engine modules import.
// R.random/uniform/randint/choice match PyRandomShim in src/web/pyrandom.py (mulberry32 from core.js), so the JS
// engine seeded like a Python reference run draws exactly the same numbers. R.seed(s) restarts the stream.
import { rng } from './core.js';

class PyRandom {
  constructor(seed = Date.now() % 2147483647) { this.seed(seed); }
  seed(s) { this.rand = rng(s); }
  random() { return this.rand(); }
  uniform(a, b) { return a + (b - a) * this.rand(); }
  randint(a, b) { return a + Math.trunc(this.rand() * (b - a + 1)); }
  choice(seq) { return seq[Math.trunc(this.rand() * seq.length)]; }
}

export const R = new PyRandom();

// Python's int() (truncate toward zero) and % (result has the sign of the divisor).
export const int = Math.trunc;
export const pymod = (a, b) => ((a % b) + b) % b;
