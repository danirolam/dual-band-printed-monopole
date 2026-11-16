"""IEEE-style |S11| figure from an HFSS report exported as CSV.

Usage:
    python s11_figure.py FINAL.csv [--where "Lp1 [mm]=5.2"] [--ref NO_L.csv]
                         [--ref-where ...] [--label "With L"] [--ref-label "Without L"]
                         [--out fig_s11]

Writes OUT.pdf (vector, for the report) and OUT.png (600 dpi, for slides).
"""
import argparse
import csv

import matplotlib.pyplot as plt
import numpy as np

ISM_BANDS = [(2.4, 2.4835), (5.725, 5.875)]  # GHz
LIMIT_DB = -10.0


def load(path, where=None):
    """Return (freq_GHz, s11_dB) for one trace of an HFSS CSV export."""
    with open(path, newline="") as f:
        rows = list(csv.reader(f))
    head, data = rows[0], rows[1:]
    fcol = next(i for i, h in enumerate(head) if h.startswith("Freq"))
    scol = next(i for i, h in enumerate(head) if h.startswith("dB(S"))
    for cond in where or []:
        name, value = cond.split("=")
        col = head.index(name.strip())
        data = [r for r in data if float(r[col]) == float(value)]
    if not data:
        raise SystemExit(f"No rows left in {path} after filtering on {where}")
    f = np.array([float(r[fcol]) for r in data])
    s = np.array([float(r[scol]) for r in data])
    order = np.argsort(f)
    return f[order], s[order]


def bands_below(f, s, limit=LIMIT_DB):
    """Frequency ranges where s < limit, with edges found by linear interpolation."""
    below = s < limit
    edges = np.flatnonzero(np.diff(below.astype(int)))
    cross = [f[i] + (limit - s[i]) * (f[i + 1] - f[i]) / (s[i + 1] - s[i]) for i in edges]
    if below[0]:
        cross.insert(0, f[0])
    if below[-1]:
        cross.append(f[-1])
    return list(zip(cross[::2], cross[1::2]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv")
    ap.add_argument("--where", action="append")
    ap.add_argument("--ref")
    ap.add_argument("--ref-where", action="append")
    ap.add_argument("--label", default="With parasitic L")
    ap.add_argument("--ref-label", default="Without parasitic L")
    ap.add_argument("--out", default="fig_s11")
    a = ap.parse_args()

    plt.rcParams.update({
        "font.family": "serif", "font.serif": ["Times New Roman"], "mathtext.fontset": "stix",
        "font.size": 8, "axes.linewidth": 0.6, "lines.linewidth": 1.1,
        "xtick.direction": "in", "ytick.direction": "in",
        "xtick.top": True, "ytick.right": True,
    })
    fig, ax = plt.subplots(figsize=(3.5, 2.4))  # IEEE single column

    for lo, hi in ISM_BANDS:
        ax.axvspan(lo, hi, color="0.85", lw=0, zorder=0)
    ax.axhline(LIMIT_DB, color="0.3", ls=":", lw=0.8, zorder=1)

    f, s = load(a.csv, a.where)
    if a.ref:
        fr, sr = load(a.ref, a.ref_where)
        ax.plot(fr, sr, color="0.5", ls="--", label=a.ref_label, zorder=2)
    ax.plot(f, s, color="black", label=a.label, zorder=3)

    # Mark each -10 dB band that covers an ISM band, with its fractional bandwidth.
    for lo, hi in bands_below(f, s):
        if not any(lo <= b0 and b1 <= hi for b0, b1 in ISM_BANDS):
            continue
        fc = (lo + hi) / 2
        ax.annotate("", xy=(lo, LIMIT_DB), xytext=(hi, LIMIT_DB),
                    arrowprops=dict(arrowstyle="<->", lw=0.6, shrinkA=0, shrinkB=0))
        ax.text(fc, LIMIT_DB + 1.2, f"{lo:.2f} to {hi:.2f} GHz\n({100 * (hi - lo) / fc:.1f}%)",
                ha="center", va="bottom", fontsize=6.5, zorder=4,
                bbox=dict(fc="white", ec="none", pad=0.6))
        print(f"-10 dB band: {lo:.3f}-{hi:.3f} GHz, {100 * (hi - lo) / fc:.1f}%")
    for b0, b1 in ISM_BANDS:
        worst = s[(f >= b0) & (f <= b1)].max()
        print(f"worst |S11| in {b0}-{b1} GHz: {worst:.1f} dB")

    ax.set_xlim(f[0], f[-1])
    ax.set_ylim(min(-40, np.floor(s.min() / 5) * 5), 0)
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel(r"$|S_{11}|$ (dB)")
    ax.grid(True, color="0.9", lw=0.4)
    ax.legend(loc="lower left", frameon=False, fontsize=7)
    fig.tight_layout(pad=0.3)
    fig.savefig(a.out + ".pdf")
    fig.savefig(a.out + ".png", dpi=600)


if __name__ == "__main__":
    main()
