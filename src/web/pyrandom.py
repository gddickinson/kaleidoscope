"""Seeded random stream shared with the browser: mulberry32 (bit-for-bit `rng()` in static/core.js).

`PyRandomShim` offers the four `random` module functions the visualiser uses (random, uniform, randint, choice) on
top of that stream; the reference runs swap it in for the `random` module of the engine modules, and
static/pyrandom.js implements the same four functions in JS, so both engines consume an identical random stream.
"""

M32 = 0xFFFFFFFF


def _imul(a, b):
    return (a * b) & M32


class Mulberry32:
    """mulberry32, identical to rng(seed) in static/core.js."""

    def __init__(self, seed):
        self.a = seed & M32

    def __call__(self):
        self.a = (self.a + 0x6D2B79F5) & M32
        a = self.a
        t = _imul(a ^ (a >> 15), 1 | a)
        t = ((t + _imul(t ^ (t >> 7), 61 | t)) & M32) ^ t
        return ((t ^ (t >> 14)) & M32) / 4294967296.0


class PyRandomShim:
    """Stands in for the `random` module. uniform() has the stdlib formula; randint/choice use floor(r * n)."""

    def __init__(self, seed):
        self.rand = Mulberry32(seed)

    def random(self):
        return self.rand()

    def uniform(self, a, b):
        return a + (b - a) * self.rand()

    def randint(self, a, b):
        return a + int(self.rand() * (b - a + 1))

    def choice(self, seq):
        return seq[int(self.rand() * len(seq))]
