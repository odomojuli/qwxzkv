"""Throughput micro-benchmark for candidate generation.

    python benchmarks/bench_generate.py

Reports candidates produced and runs/second, with and without the provable
edit-distance closure. Use it to compare the pure-Python path against the Rust
kernel (build it with ``maturin develop`` first).
"""

from __future__ import annotations

import time

from typosquat import HAVE_RUST, generate
from typosquat.ecosystems import NPM, PYPI


def bench(target, eco, *, closure=False, runs=25):
    start = time.perf_counter()
    total = 0
    for _ in range(runs):
        total = len(generate(target, ecosystem=eco, closure=closure))
    elapsed = time.perf_counter() - start
    print(
        f"{target:16} {eco.name:7} closure={str(closure):5} "
        f"{total:7d} cands  {runs / elapsed:8.1f} runs/s"
    )


if __name__ == "__main__":
    print(f"rust kernel: {'ON' if HAVE_RUST else 'off (pure-Python)'}\n")
    for name in ("requests", "cross-env", "django", "vue-router"):
        bench(name, PYPI)
    bench("requests", NPM)
    print()
    bench("requests", PYPI, closure=True)
    bench("flask", PYPI, closure=True)
