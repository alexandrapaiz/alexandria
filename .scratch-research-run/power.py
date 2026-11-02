import math
from math import comb

def exact_p(b, nd):
    """Two-sided exact McNemar (binomial sign test on discordant pairs, p=0.5)."""
    if nd == 0:
        return 1.0
    tail = sum(comb(nd, i) for i in range(0, min(b, nd - b) + 1)) / 2 ** nd
    return min(1.0, 2 * tail)

print("Hard floor: smallest number of discordant cases that can ever reach p<=0.05,")
print("with every one of them falling the same way.")
for nd in range(1, 9):
    print(f"  n_d={nd}  best achievable two-sided p = {exact_p(nd, nd):.4f}"
          f"  {'DECIDABLE' if exact_p(nd, nd) <= 0.05 else ''}")
print()

def power(N, delta, pi, alpha=0.05):
    tot = 0.0
    for nd in range(0, N + 1):
        pnd = comb(N, nd) * delta ** nd * (1 - delta) ** (N - nd)
        if pnd < 1e-15:
            continue
        rej = 0.0
        for b in range(0, nd + 1):
            if exact_p(b, nd) <= alpha:
                rej += comb(nd, b) * pi ** b * (1 - pi) ** (nd - b)
        tot += pnd * rej
    return tot

DELTA = 3 / 67
print(f"Observed discordance rate delta = 3/67 = {DELTA:.4f}; observed split 3-0 so pi_hat = 1.0")
print(f"Current suite: n_d=3 all one way -> two-sided exact p = {exact_p(3,3):.4f} (not decidable)")
print()
print("Power to call an engine change at alpha=0.05, by suite size:")
hdr = f"{'N cases':>8} {'pi=1.00':>9} {'pi=0.90':>9} {'pi=0.80':>9} {'pi=0.67':>9}"
print(hdr)
for N in (67, 100, 134, 150, 200, 250, 300, 400, 500, 750, 1000):
    row = "  ".join(f"{power(N, DELTA, pi):7.3f}" for pi in (1.0, 0.9, 0.8, 0.67))
    print(f"{N:>8}   {row}")
print()
for pi in (1.0, 0.9, 0.8, 0.67):
    N = 67
    while N <= 4000 and power(N, DELTA, pi) < 0.80:
        N += 1
    print(f"  pi={pi:.2f}: N for 80% power = {N if N <= 4000 else '>4000'}")
