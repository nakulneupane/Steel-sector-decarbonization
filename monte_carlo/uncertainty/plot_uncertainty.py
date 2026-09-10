#!/usr/bin/env python3
"""MC uncertainty risk figure (2x2), reading each panel's precomputed
data straight from its own subfolder -- no raw solves touched here.

  (a) 2050 route shares      -- P10-P90 risk range per route, EF 1.8.
      Reads shares/data/shares.xlsx.
  (b) Drivers of cost risk   -- tornado diagram: one-at-a-time LCOP swing
      across each driver's own sampled low->high, baseline at the
      cell-demeaned mean. Reads cost_risk/data/cost_risk.xlsx.
  (c) Matched-world LCOP     -- violin of whole-horizon PV LCOP (USD/t),
      one violin per emissions target, over the SAME structural cells x
      50 shared draws solved once per target -- isolates the pure effect
      of the target, unconfounded by which cells happen to be feasible
      at each EF. Reads cost_distribution/data/cost_distribution.xlsx.
      The median CO2-abatement-cost (diamond marker) uses the three
      values from the original project's figure as a PLACEHOLDER --
      that computation depended on a "frozen-structure Baseline run"
      whose script and underlying data are both gone (lost to a
      file-corruption incident, 2026-09-01); to be replaced once a
      baseline methodology is designed for this repository.
  (d) Stochasticity of coking coal -- box/whisker of matched LCOP delta
      per H2-delay step x the draw's coal price. Reads
      coking_coal_stochasticity/data/coking_coal_stochasticity.xlsx.

    python plot_uncertainty.py
"""
import pathlib

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

plt.rcParams.update({
    "font.family": "Source Code Pro",
    "font.size": 16,
    "axes.labelsize": 16,
    "xtick.labelsize": 16,
    "ytick.labelsize": 16,
})

HERE = pathlib.Path(__file__).resolve().parent
SHARES_XLSX = HERE / "shares" / "data" / "shares.xlsx"
COSTRISK_XLSX = HERE / "cost_risk" / "data" / "cost_risk.xlsx"
COSTDIST_XLSX = HERE / "cost_distribution" / "data" / "cost_distribution.xlsx"
COKINGCOAL_XLSX = HERE / "coking_coal_stochasticity" / "data" / "coking_coal_stochasticity.xlsx"

# PLACEHOLDER: the three values from the original project's finalized
# figure, whose derivation (a frozen-structure baseline scenario) is not
# reproducible from anything that survives in this repository or the
# original project. See module docstring.
AC_MEDIAN_PLACEHOLDER = {1.6: 25.701126, 1.8: 17.559270, 2.0: 10.413427}

MC_COLS = ["ccoal_price", "scrap_price", "ng_price", "theta_tech", "theta_ccs"]
GROUP = ["ccoal", "ng", "h2_start", "scrap_rate", "theta_grid_target",
         "ramp", "build_cap", "legacy"]
RANGE = {"ccoal_price": 300, "ng_price": 20, "scrap_price": 200,
         "theta_tech": 1, "theta_ccs": 1}
NICE = {"ccoal_price": "Coal", "scrap_price": "Scrap",
        "ng_price": "NG", "theta_tech": r"H$_2$",
        "theta_ccs": "CCS"}
GREEN, NAVY = "#4daf4a", "#313e61"
COALC = {100: "#a8c9a6", 250: "#4daf4a", 400: "#313e61"}
EF_COLORS = {1.6: "#264653", 1.8: "#377eb8", 2.0: "#e76f51"}

SHARE_COLS = [("share_bof", "BF-BOF"), ("share_cdri", "Coal DRI-EAF"),
             ("share_ngdri", "NG DRI-EAF"), ("share_h2", r"H$_2$-DRI-EAF"),
             ("share_scrap", "Scrap-EAF")]
ROUTE_COLOR = {
    "BF-BOF": "#313e61", "Coal DRI-EAF": "#5c5c5c", "NG DRI-EAF": "#e67e22",
    r"H$_2$-DRI-EAF": "#4daf4a", "Scrap-EAF": "#377eb8",
}


def ols(sub, ycol):
    X = sub[MC_COLS].values.astype(float)
    X = X - X.mean(0)
    y = sub[ycol].values.astype(float)
    Xd = np.column_stack([np.ones(len(X)), X])
    coef, *_ = np.linalg.lstsq(Xd, y, rcond=None)
    return coef[1:]


# ---------------------------------------------------------------- (b)
def panel_drivers(ax, d):
    d = d.copy()
    d["y"] = d.lcop - d.groupby(GROUP).lcop.transform("mean")

    PRICE_AT = {
        "theta_tech": {0.0: "$5.00/kg", 1.0: "$1.50/kg"},
        "theta_ccs": {0.0: r"\$100/tCO$_2$", 1.0: r"\$60/tCO$_2$"},
    }
    UNIT = {"ccoal_price": "/t", "scrap_price": "/t", "ng_price": "/MMBtu"}

    betas = ols(d, "y")
    base = d.lcop.mean()
    rows = []
    for p, b in zip(MC_COLS, betas):
        lo, hi = d[p].min(), d[p].max()
        xm = d[p].mean()
        y_lo = base + b * (lo - xm)
        y_hi = base + b * (hi - xm)
        if y_lo <= y_hi:
            yleft, yright, vleft, vright = y_lo, y_hi, lo, hi
        else:
            yleft, yright, vleft, vright = y_hi, y_lo, hi, lo
        rows.append((p, yleft, yright, vleft, vright))
    rows.sort(key=lambda r: r[2] - r[1])

    xlo = min(r[1] for r in rows)
    xhi = max(r[2] for r in rows)
    pad = 0.32 * (xhi - xlo)
    ax.set_xlim(xlo - pad, xhi + pad)

    ypos = np.arange(len(rows)) + 1
    for i, (p, ylo, yhi, vleft, vright) in enumerate(rows):
        ax.barh(ypos[i], yhi - ylo, left=ylo, height=0.6, color=NAVY, zorder=3)
        if p in PRICE_AT:
            lo_s, hi_s = PRICE_AT[p][vleft], PRICE_AT[p][vright]
        else:
            lo_s = f"${vleft:.0f}{UNIT[p]}"
            hi_s = f"${vright:.0f}{UNIT[p]}"
        ax.text(ylo - pad * 0.12, ypos[i], lo_s, va="center", ha="right", fontsize=14)
        ax.text(yhi + pad * 0.12, ypos[i], hi_s, va="center", ha="left", fontsize=14)
    ax.axvline(base, color="0.4", lw=1, ls="--", zorder=4)
    ax.text(base, len(rows) + 0.75, "Baseline", ha="center", fontsize=14,
            color="0.3", zorder=5,
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                      edgecolor="0.4", linewidth=1))
    ax.set_yticks(list(ypos))
    ax.set_yticklabels([NICE[r[0]] for r in rows])
    ax.set_ylim(0.3, len(rows) + 1.1)
    ax.set_xlabel("LCOP across sampled range (USD/t)")
    ax.grid(axis="x", alpha=0.15)


# ---------------------------------------------------------------- (c)
def panel_lcop_violin(ax, matched):
    efs = [1.6, 1.8, 2.0]
    data = [matched[f"lcop_{ef}"].values for ef in efs]
    ac_median = AC_MEDIAN_PLACEHOLDER

    parts = ax.violinplot(data, positions=range(len(efs)), showmedians=True,
                          showextrema=True, widths=0.75)
    for i, pc in enumerate(parts["bodies"]):
        color = EF_COLORS[efs[i]]
        pc.set_facecolor(color)
        pc.set_edgecolor(color)
        pc.set_alpha(0.55)
    for key in ["cmedians", "cbars", "cmins", "cmaxes"]:
        parts[key].set_color("#1a1a1a")
        parts[key].set_linewidth(1.4)

    for i, ef in enumerate(efs):
        med = np.median(data[i])
        ax.text(i, med, f"{med:.0f}", ha="center", va="center", fontsize=14,
                color="white",
                bbox=dict(boxstyle="round,pad=0.25", fc="#1a1a1a", ec="none"))

    ymin = min(v.min() for v in data)
    ymax = max(v.max() for v in data)
    pad = 0.08 * (ymax - ymin)
    ax.set_ylim(ymin - pad, ymax + 0.06 * (ymax - ymin))
    for i, ef in enumerate(efs):
        ax.text(i, ymin - pad * 0.45, rf"◆ ${ac_median[ef]:.0f}/t", ha="center",
                va="center", fontsize=13, color="#1a1a1a")

    ax.set_xticks(range(len(efs)))
    ax.set_xticklabels([f"{ef}" for ef in efs])
    handles = [plt.Line2D([], [], marker="D", color="#1a1a1a", ls="", ms=6,
                          label="Median CO$_2$ abatement\n" r"Cost (\$/tCO$_2$)")]
    ax.legend(handles=handles, loc="upper right", fontsize=14, frameon=True,
             framealpha=0.95, edgecolor="black")
    ax.set_xlabel(r"Cumulative emission target, 2025-2050 (tCO$_2$/tCS)")
    ax.set_ylabel("LCOP (USD/t)")
    ax.grid(axis="y", alpha=0.15)
    ax.set_axisbelow(True)


# ---------------------------------------------------------------- (d)
def panel_coal_delay(ax, d):
    # No draw_id column is carried in this repo's filtered data -- but the
    # shared-draw design means a draw's own 5 values (MC_COLS) uniquely
    # identify it, so matching on those is equivalent to matching on
    # draw_id for pairing the SAME world across different h2_start years.
    other = [c for c in GROUP if c != "h2_start"]
    piv = d.pivot_table(index=other + MC_COLS, columns="h2_start",
                        values="lcop").reset_index()
    piv["coal"] = piv["ccoal_price"]

    lvls = [100, 250, 400]
    w = 0.26
    for li, lvl in enumerate(lvls):
        sub = piv[piv.coal == lvl]
        for gi, yr in enumerate([2035, 2040, 2045]):
            delta = (sub[yr] - sub[2030]).dropna()
            pos = gi + (li - 1) * w
            bp = ax.boxplot([delta], positions=[pos], widths=w * 0.82,
                            patch_artist=True, showfliers=False, zorder=3,
                            whiskerprops=dict(color="black", linewidth=0.9),
                            capprops=dict(color="black", linewidth=0.9),
                            medianprops=dict(color="black", linewidth=1.4))
            bp["boxes"][0].set(facecolor=COALC[lvl], edgecolor="black",
                               linewidth=0.8)
    ax.axhline(0, color="0.5", lw=0.8, ls=":")
    ax.set_xticks(range(3))
    ax.set_xticklabels(["2030 → 2035", "2030 → 2040", "2030 → 2045"])
    ax.set_xlim(-0.6, 2.6)
    ax.set_xlabel(r"H$_2$ delay")
    ax.set_ylabel(r"$\Delta$LCOP (USD/t)")
    ax.grid(axis="y", alpha=0.15)
    handles = [Patch(facecolor=COALC[l], edgecolor="black",
                     label=f"Coal USD {l}/t") for l in lvls]
    ax.legend(handles=handles, fontsize=14, loc="upper left", frameon=True,
             framealpha=0.95, edgecolor="black", fancybox=False)

    ymin, ymax = ax.get_ylim()
    pad = 0.16 * (ymax - ymin)
    ax.set_ylim(ymin - pad, ymax)
    base = piv[2030].notna()
    for gi, yr in enumerate([2035, 2040, 2045]):
        lost = 100 * (base & piv[yr].isna()).sum() / base.sum()
        ax.text(gi, ymin - pad * 0.15, f"{lost:.0f}% world\nLOST", ha="center",
                va="top", fontsize=13, color="#c0392b")
    ax.set_yticks([t for t in ax.get_yticks() if t >= 0])


# ---------------------------------------------------------------- (a)
def _range_stats(s):
    s = s.dropna()
    p95 = s.quantile(0.95)
    return dict(mean=s.mean(), p10=s.quantile(0.10), p50=s.quantile(0.50),
               p90=s.quantile(0.90), cvar95=s[s >= p95].mean())


def panel_shares(ax, d):
    rows = [(label, _range_stats(d[col] * 100)) for col, label in SHARE_COLS]
    rows.sort(key=lambda r: r[1]["mean"])

    bar_h = 0.5
    ypos = np.arange(len(rows))
    for y, (label, st) in zip(ypos, rows):
        color = ROUTE_COLOR[label]
        ax.barh(y, st["p90"] - st["p10"], left=st["p10"], height=bar_h,
               color=color, alpha=0.28, edgecolor=color, linewidth=1.3, zorder=2)
        ax.plot([st["p50"], st["p50"]], [y - bar_h / 2, y + bar_h / 2],
               color="0.1", lw=2.6, ls=":", zorder=4)
        ax.scatter([st["mean"]], [y], marker="D", s=95, color="black",
                  edgecolor="black", linewidth=0.8, zorder=5)
        ax.scatter([st["cvar95"]], [y], marker="^", s=140, color="black",
                  edgecolor="black", linewidth=0.6, zorder=5)

    ax.set_yticks(ypos)
    ax.set_yticklabels([label for label, _ in rows], fontweight="bold")
    for y, (label, _) in zip(ypos, rows):
        ax.get_yticklabels()[y].set_color(ROUTE_COLOR[label])

    ax.set_xlabel("2050 route share (%)")
    ax.set_xlim(-6, 82)
    ax.grid(axis="x", alpha=0.18, zorder=0)
    ax.set_axisbelow(True)
    ax.set_ylim(-0.7, len(rows) - 0.3)

    handles = [
        plt.Rectangle((0, 0), 1, 1, facecolor="0.6", alpha=0.35,
                      edgecolor="0.3", label="P10-P90 range"),
        plt.Line2D([], [], color="0.1", lw=2.6, ls=":", label="Median (P50)"),
        plt.Line2D([], [], marker="D", color="black", ls="", ms=9,
                   markeredgecolor="black", label="Mean"),
        plt.Line2D([], [], marker="^", color="black", ls="", ms=11,
                   markeredgecolor="black", label="CVaR (95%)"),
    ]
    ax.legend(handles=handles, loc="lower right", frameon=True, edgecolor="black",
             framealpha=0.95, fontsize=14)


def main():
    shares = pd.read_excel(SHARES_XLSX, sheet_name="plot_data")
    cost_risk = pd.read_excel(COSTRISK_XLSX, sheet_name="plot_data")
    cost_dist = pd.read_excel(COSTDIST_XLSX, sheet_name="plot_data")
    coking_coal = pd.read_excel(COKINGCOAL_XLSX, sheet_name="plot_data")

    fig, axes = plt.subplots(2, 2, figsize=(14.5, 10.5))
    fig.subplots_adjust(left=0.13, right=0.97, top=0.955, bottom=0.07,
                        wspace=0.32, hspace=0.3)
    axA, axB, axC, axD = axes.ravel()

    panel_shares(axA, shares)
    panel_drivers(axB, cost_risk)
    panel_lcop_violin(axC, cost_dist)
    panel_coal_delay(axD, coking_coal)

    titles = ["(a) 2050 route shares",
              "(b) Drivers of cost risk",
              "(c) Matched-world cost distribution",
              "(d) Stochasticity of coking coal"]
    for ax, title in zip((axA, axB, axC, axD), titles):
        ax.set_title(title, loc="left", fontsize=16, fontweight="bold")
        for spine in ax.spines.values():
            spine.set_linewidth(1.2)

    out = HERE / "fig_uncertainty.png"
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    print(f"written: {out}")

    out_pdf = HERE / "fig_uncertainty.pdf"
    fig.savefig(out_pdf, format="pdf", dpi=600, bbox_inches="tight", facecolor="white")
    print(f"written: {out_pdf}")


if __name__ == "__main__":
    main()
