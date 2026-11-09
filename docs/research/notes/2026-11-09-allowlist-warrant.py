#!/usr/bin/env python3
"""Every figure in 2026-11-09-allowlist-warrant.md, recomputed from scratch.

Inputs are transcribed from arxiv:2610.07639 v2, tables 6 and 7, read in full
this run (tools/read_paper.py 2610.07639, exit 0, 115,605 chars). Standard
library only -- this sandbox has no scipy, which is why Fisher, the chi-square
tail and the permutation null are implemented here rather than imported.

    python3 docs/research/notes/2026-11-09-allowlist-warrant.py
"""
from itertools import permutations, combinations
from math import comb, sqrt, erfc, log

H = ["Codex CLI", "Claude Code", "Gemini CLI", "gptme", "Qwen Code", "GitHub Copilot"]

# Table 6, AA block. "off" is the mechanism disengaged; AA disengaged == gate ENGAGED.
AA = {
    "ut_off":  [95.4, 94.6, 94.6, 66.9, 50.0, 60.8],
    "ut_on":   [96.2, 93.8, 96.9, 97.7, 94.6, 93.1],
    "asr_off": [81.7, 43.3,  3.3, 45.0,  0.0,  1.7],
    "asr_on":  [96.7,100.0,100.0,100.0, 90.0, 86.7],
    "asr_off_n": [49, 26, 2, 27, 0, 1],      # of 60
    "asr_on_n":  [58, 60, 60, 60, 54, 52],   # of 60
}
# Table 6, CAL block. "on" is the allowlist ENGAGED.
CAL = {
    "ut_off":  [100.0,100.0, 99.1, 96.4,100.0,100.0],
    "ut_on":   [100.0, 94.5, 97.3, 99.1, 96.4, 99.1],
    "asr_off": [ 95.0,100.0,100.0,100.0, 93.3,100.0],
    "asr_on":  [ 80.0, 23.3, 41.7, 95.0, 18.3, 41.7],
    "asr_on_n":  [48, 14, 25, 57, 11, 25],   # of 60
    "d_asr":   [-15.0,-76.7,-58.3, -5.0,-75.0,-58.3],
}


def ranks(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    out, i = [0.0] * len(v), 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and v[order[j + 1]] == v[order[i]]:
            j += 1
        for k in range(i, j + 1):
            out[order[k]] = (i + j) / 2 + 1
        i = j + 1
    return out


def pearson(x, y):
    n = len(x)
    mx, my = sum(x) / n, sum(y) / n
    num = sum((a - mx) * (b - my) for a, b in zip(x, y))
    return num / sqrt(sum((a - mx) ** 2 for a in x) * sum((b - my) ** 2 for b in y))


def spearman(x, y):
    """Tie-corrected: Pearson on midranks, which is what scipy.spearmanr returns."""
    return pearson(ranks(x), ranks(y))


def spearman_shortcut(x, y):
    """1 - 6*sum(d^2)/(n(n^2-1)). Exact only when neither vector has ties."""
    rx, ry = ranks(x), ranks(y)
    n = len(x)
    d2 = sum((a - b) ** 2 for a, b in zip(rx, ry))
    return 1 - 6 * d2 / (n * (n * n - 1)), d2


def spearman_exact_p(x, y):
    """Exact permutation p, two- and one-sided, over all n! rank assignments."""
    rx, ry = ranks(x), ranks(y)
    obs = pearson(rx, ry)
    two = one = 0
    for p in permutations(ry):
        r = pearson(rx, list(p))
        if r >= obs - 1e-12:
            one += 1
        if abs(r) >= abs(obs) - 1e-12:
            two += 1
    tot = 1
    for i in range(2, len(x) + 1):
        tot *= i
    return two / tot, one / tot, tot


def _hyper(r1, n, c1, x):
    return comb(r1, x) * comb(n - r1, c1 - x) / comb(n, c1)


def fisher(a, b, c, d, two_sided=True):
    n, r1, c1 = a + b + c + d, a + b, a + c
    p0 = _hyper(r1, n, c1, a)
    lo, hi = max(0, c1 - (n - r1)), min(r1, c1)
    if not two_sided:
        return sum(_hyper(r1, n, c1, x) for x in range(a, hi + 1))
    return sum(_hyper(r1, n, c1, x) for x in range(lo, hi + 1)
               if _hyper(r1, n, c1, x) <= p0 * (1 + 1e-12))


def chi2_1df(a, b, c, d, yates=False):
    n = a + b + c + d
    num = n * (abs(a * d - b * c) - (n / 2 if yates else 0)) ** 2
    x2 = num / ((a + b) * (c + d) * (a + c) * (b + d))
    return x2, erfc(sqrt(x2 / 2))


def gtest(a, b, c, d):
    n = a + b + c + d
    o = [a, b, c, d]
    e = [(a + b) * (a + c) / n, (a + b) * (b + d) / n,
         (c + d) * (a + c) / n, (c + d) * (b + d) / n]
    g = 2 * sum(oi * log(oi / ei) for oi, ei in zip(o, e) if oi > 0)
    return g, erfc(sqrt(g / 2))


def rng(v):
    return min(v), max(v), round(max(v) - min(v), 1)


def main():
    print("== 1. the four that reproduce ==")
    print("AA utility-off (gate engaged):  %.1f to %.1f, range %.1f pp" % rng(AA["ut_off"]))
    print("CAL delta ASR:                  %.1f to %.1f, range %.1f pp"
          % (max(CAL["d_asr"]), min(CAL["d_asr"]), max(CAL["d_asr"]) - min(CAL["d_asr"])))
    print("CAL utility-on band:            %.1f to %.1f, range %.1f pp" % rng(CAL["ut_on"]))
    print("CAL utility-off band:           %.1f to %.1f, range %.1f pp" % rng(CAL["ut_off"]))
    off, on = sum(AA["asr_off_n"]), sum(AA["asr_on_n"])
    print("posture: %d/360 = %.1f%% -> %d/360 = %.1f%%, delta %+.1f pp"
          % (off, 100 * off / 360, on, 100 * on / 360, 100 * (on - off) / 360))

    print("\n== 2. the p-value that does not reproduce ==")
    print("message reported: 1.3e-13, on 57/60 against 14/60")
    for name, p in [
        ("Fisher two-sided", fisher(57, 3, 14, 46)),
        ("Fisher one-sided", fisher(57, 3, 14, 46, two_sided=False)),
        ("chi-square, no correction", chi2_1df(57, 3, 14, 46)[1]),
        ("chi-square, Yates", chi2_1df(57, 3, 14, 46, yates=True)[1]),
        ("G-test", gtest(57, 3, 14, 46)[1]),
    ]:
        print("  %-28s %.3g" % (name, p))
    print("  the ASR-on COLUMN endpoints are gptme 57/60 and Qwen Code 11/60:")
    print("  %-28s %.3g" % ("Fisher two-sided", fisher(57, 3, 11, 49)))

    tests = {"fisher2": lambda t: fisher(*t),
             "fisher1": lambda t: fisher(*t, two_sided=False),
             "chi2": lambda t: chi2_1df(*t)[1],
             "yates": lambda t: chi2_1df(*t, yates=True)[1],
             "g": lambda t: gtest(*t)[1]}
    target, best = 1.3e-13, []
    for (i, j) in combinations(range(6), 2):
        hi, lo = max(CAL["asr_on_n"][i], CAL["asr_on_n"][j]), min(CAL["asr_on_n"][i], CAL["asr_on_n"][j])
        for tn, fn in tests.items():
            p = fn((hi, 60 - hi, lo, 60 - lo))
            best.append((abs(log(p) - log(target)), p, H[i], H[j], tn))
    best.sort()
    print("  nearest of all %d (CAL cell pair x test) combinations to 1.3e-13:" % len(best))
    for _, p, a, b, tn in best[:3]:
        print("    %-15s vs %-15s %-8s p=%.3g" % (a, b, tn, p))

    print("\n== 3. the test does not separate the blocks ==")
    print("AA ASR-off endpoint cells, Codex 49/60 vs Qwen 0/60: Fisher %.3g"
          % fisher(49, 11, 0, 60))
    print("CAL ASR-on delta endpoints, gptme 57/60 vs Claude 14/60: Fisher %.3g"
          % fisher(57, 3, 14, 46))
    print("-> the arm barred as confounded has the SMALLER p by four orders of magnitude")
    print("denominator: CAL is 2 tasks x 6 attack oracles x 10 trials, so 57/60 is 10 runs")

    print("\n== 4. the ranking is the same in both blocks ==")
    for label, d, asr_key in [("AA  (gate engaged)", AA, "asr_off"),
                              ("CAL (allowlist engaged)", CAL, "asr_on")]:
        ut = d["ut_off"] if d is AA else d["ut_on"]
        rho = spearman(d[asr_key], ut)
        sc, d2 = spearman_shortcut(d[asr_key], ut)
        ar, ur = rng(d[asr_key])[2], rng(ut)[2]
        print("  %-24s rho=%+.4f (shortcut %+.4f, sum d2=%.1f)  ASR range %.1f  utility range %.1f  ratio %.1f"
              % (label, rho, sc, d2, ar, ur, ar / ur))
    print("  CAL spearman(signed delta ASR as printed, utility on) = %+.4f"
          % spearman(CAL["d_asr"], CAL["ut_on"]))
    print("  the AA tie that makes the shortcut inexact:"
          " Claude Code and Gemini CLI both 94.6 percent utility-off")
    two, one, tot = spearman_exact_p(AA["asr_off"], AA["ut_off"])
    print("  AA exact permutation p over %d assignments: two-sided %.4f, one-sided %.4f" % (tot, two, one))
    print("  critical values at n=6: 0.886 two-tailed, 0.829 one-tailed, alpha=.05")

    print("\n== 4b. the endpoint claim, which needs no test ==")
    lo_i, hi_i = AA["asr_off"].index(min(AA["asr_off"])), AA["asr_off"].index(max(AA["asr_off"]))
    print("  lowest ASR  %-15s %.1f%%  utility %.1f%%  (is utility min? %s)"
          % (H[lo_i], AA["asr_off"][lo_i], AA["ut_off"][lo_i], AA["ut_off"][lo_i] == min(AA["ut_off"])))
    print("  highest ASR %-15s %.1f%%  utility %.1f%%  (is utility max? %s)"
          % (H[hi_i], AA["asr_off"][hi_i], AA["ut_off"][hi_i], AA["ut_off"][hi_i] == max(AA["ut_off"])))

    print("\n== 7. the posture effect's utility half is disjoint by group ==")
    d_ut = [round(on - off, 1) for on, off in zip(AA["ut_on"], AA["ut_off"])]
    d_asr = [round(on - off, 1) for on, off in zip(AA["asr_on"], AA["asr_off"])]
    for h, u, du, da in sorted(zip(H, AA["ut_off"], d_ut, d_asr), key=lambda r: -r[1]):
        print("  %-15s utility engaged %5.1f%%  d_utility %+5.1f pp  d_ASR %+5.1f pp" % (h, u, du, da))
    print("  spearman(utility engaged, d_utility) = %+.4f" % spearman(AA["ut_off"], d_ut))
    top = [du for u, du in zip(AA["ut_off"], d_ut) if u >= 94.0]
    bot = [du for u, du in zip(AA["ut_off"], d_ut) if u < 94.0]
    print("  three highest-utility harnesses gain %.1f to %.1f pp; three lowest gain %.1f to %.1f pp"
          % (min(top), max(top), min(bot), max(bot)))
    print("  disjoint: %s" % (max(top) < min(bot)))


if __name__ == "__main__":
    main()
