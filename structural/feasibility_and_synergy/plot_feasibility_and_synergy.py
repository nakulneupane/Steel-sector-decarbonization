#!/usr/bin/env python3
"""Feasibility Drivers + Sectoral Synergy, side by side (1x2).
  (a) Feasibility drivers                -- octagonal radar, S_T by EF
  (b) Sectoral synergy: Power and Steel  -- required grid-offset contour

Reads two separate files -- the outputs of each subfolder's own run
script, not raw solver output:
  feasibility_drivers/data/feasibility_drivers.xlsx, sheet "sobol_by_ef"
  sectoral_synergy/data/sectoral_synergy.xlsx, sheet "grid_offset"
"""
import os

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections import register_projection
from matplotlib.projections.polar import PolarAxes
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D, ScaledTranslation

plt.rcParams.update({
    "font.family": "Source Code Pro",
    "font.size": 14,
    "axes.labelsize": 14,
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
})

HERE = os.path.dirname(os.path.abspath(__file__))
SOBOL_XLSX = os.path.join(HERE, "feasibility_drivers", "data", "feasibility_drivers.xlsx")
GRID_XLSX = os.path.join(HERE, "sectoral_synergy", "data", "sectoral_synergy.xlsx")

# ---------------------------------------------------------------- (a) sobol
# sheet's plain-text driver names -> the multi-line LaTeX labels the radar
# spokes use
DRIVER_NICE = {
    "Build budget": "Build\nbudget",
    "Scrap growth": "Scrap\ngrowth",
    "H2 start year": "H$_2$\nstart\nyear",
    "Coking-coal supply": "Coal\nsupply",
    "Grid learning": "Grid\nlearning",
    "H2 supply ramp": "H$_2$\nsupply\nramp",
    "Legacy retirement": "Legacy\nretirement",
    "NG supply": "NG\nsupply",
}
SOBOL_EFS = [1.6, 1.8, 2.0]
SOBOL_COLORS = {1.6: "#264653", 1.8: "#377eb8", 2.0: "#e76f51"}
SOBOL_MARKERS = {1.6: "o", 1.8: "^", 2.0: "*"}
SOBOL_MSIZES = {1.6: 6, 1.8: 7, 2.0: 10}


def radar_factory(num_vars, frame="polygon"):
    theta = np.linspace(0, 2 * np.pi, num_vars, endpoint=False)

    class RadarTransform(PolarAxes.PolarTransform):
        def transform_path_non_affine(self, path):
            if path._interpolation_steps > 1:
                path = path.interpolated(num_vars)
            return Path(self.transform(path.vertices), path.codes)

    class RadarAxes(PolarAxes):
        name = "radar"
        PolarTransform = RadarTransform

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.set_theta_zero_location("N")

        def fill(self, *args, closed=True, **kwargs):
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)
            return lines

        def _close_line(self, line):
            x, y = line.get_data()
            if x[0] != x[-1]:
                x = np.append(x, x[0])
                y = np.append(y, y[0])
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            if frame == "circle":
                return Circle((0.5, 0.5), 0.5)
            return RegularPolygon((0.5, 0.5), num_vars, radius=0.5,
                                  edgecolor="k")

        def _gen_axes_spines(self):
            if frame == "circle":
                return super()._gen_axes_spines()
            spine = Spine(axes=self, spine_type="circle",
                          path=Path.unit_regular_polygon(num_vars))
            spine.set_transform(Affine2D().scale(0.5).translate(0.5, 0.5)
                                + self.transAxes)
            return {"polar": spine}

    register_projection(RadarAxes)
    return theta


RADAR_THETA = radar_factory(len(DRIVER_NICE), frame="polygon")


def panel_sobol(fig, ax):
    df = pd.read_excel(SOBOL_XLSX, sheet_name="sobol_by_ef")
    piv = df.pivot(index="driver", columns="avg_emi", values="S_T")
    piv = piv.loc[piv.mean(axis=1).sort_values(ascending=False).index]
    names = [DRIVER_NICE[d] for d in piv.index]
    ST = piv[SOBOL_EFS].values

    FS_DRIVER = 15
    FS_RADIAL = 12
    FS_LEGEND_A = 12
    FS_INDEX = 12

    ax.set_ylim(0, 0.68)
    ax.set_rgrids([0.2, 0.4, 0.6], labels=["", "", ""],
                  angle=225, fontsize=FS_RADIAL, color="black")
    for r, txt in zip([0.2, 0.4, 0.6], ["0.2", "0.4", "0.6"]):
        ax.text(np.deg2rad(225), r, txt, rotation=45, ha="center", va="center",
                fontsize=FS_RADIAL, color="black", zorder=20,
                bbox=dict(facecolor="white", edgecolor="0.45",
                         linewidth=0.8, boxstyle="round,pad=0.22"))
    ax.yaxis.grid(color="0.82", lw=0.5)
    ax.xaxis.grid(color="0.7", lw=0.9)
    ax.spines["polar"].set_color("0.15")
    ax.spines["polar"].set_linewidth(2.2)

    for j, ef in enumerate(SOBOL_EFS):
        vals = ST[:, j]
        ax.plot(RADAR_THETA, vals, color=SOBOL_COLORS[ef], lw=2.7,
                marker=SOBOL_MARKERS[ef], ms=SOBOL_MSIZES[ef],
                markerfacecolor=SOBOL_COLORS[ef], markeredgecolor="white",
                markeredgewidth=0.9, label=f"EF = {ef}", zorder=3 + j,
                clip_on=False)
        ax.fill(RADAR_THETA, vals, color=SOBOL_COLORS[ef], alpha=0.18,
                zorder=2)

    ax.set_varlabels(names)
    ax.tick_params(axis="x", pad=18)
    for lbl in ax.get_xticklabels():
        lbl.set_fontsize(FS_DRIVER)
        if lbl.get_text() == "Scrap\ngrowth":
            lbl.set_transform(lbl.get_transform() + ScaledTranslation(
                0, 6 / 72, fig.dpi_scale_trans))
        elif lbl.get_text() == "H$_2$\nsupply\nramp":
            lbl.set_transform(lbl.get_transform() + ScaledTranslation(
                0.1, 4 / 72, fig.dpi_scale_trans))
        elif lbl.get_text() == "H$_2$\nstart\nyear":
            lbl.set_transform(lbl.get_transform() + ScaledTranslation(
                -0.1, 4 / 72, fig.dpi_scale_trans))

    leg = ax.legend(loc="center", bbox_to_anchor=(0.75, 0.62), fontsize=FS_LEGEND_A,
                    frameon=False, labelspacing=0.35, handlelength=1.6)
    leg.set_zorder(40)
    ax.text(np.deg2rad(225), 0.50, "Total Sobol index", rotation=45,
            ha="center", va="center", fontsize=FS_INDEX, color="black",
            zorder=25,
            bbox=dict(facecolor="white", edgecolor="none", pad=1.5))


# ---------------------------------------------------------------- (b) grid offset
def panel_grid_offset(fig, ax):
    df = pd.read_excel(GRID_XLSX, sheet_name="grid_offset")
    scraps = sorted(df.scrap_rate.unique())
    years = sorted(df.h2_start.unique())
    Z = np.full((len(years), len(scraps)), np.nan)
    for i, y in enumerate(years):
        for j, s in enumerate(scraps):
            v = df[(df.h2_start == y) & (df.scrap_rate == s)]["offset_pct"].iloc[0]
            Z[i, j] = np.nan if str(v) == "INFEASIBLE" else float(v)

    X = np.array(scraps) * 100
    Y = np.array(years)
    Zm = np.ma.masked_invalid(Z)
    cmap_d = LinearSegmentedColormap.from_list(
        "blue_seq", ["#eaf1fb", "#8fb8dd", "#3c6ea5", "#152f52"])
    INFEASIBLE_GRAY = "#c7c9cc"
    ax.set_facecolor(INFEASIBLE_GRAY)
    cf = ax.contourf(X, Y, Zm, levels=np.linspace(0, 100, 201),
                     cmap=cmap_d, vmin=0, vmax=100)
    try:
        cf.set_edgecolor("face")
    except AttributeError:
        for coll in cf.collections:
            coll.set_edgecolor("face")
    cs_lo = ax.contour(X, Y, Zm, levels=[5, 10, 30], colors="black",
                       linewidths=1.1)
    ax.clabel(cs_lo, fmt="%d%%", fontsize=14, colors="black")
    cs_hi = ax.contour(X, Y, Zm, levels=[50, 70, 90], colors="white",
                       linewidths=1.1)
    ax.clabel(cs_hi, fmt="%d%%", fontsize=14, colors="white")

    ax.text(1.75, 2042.3, "Infeasible", fontsize=14, color="0.25",
            ha="center", va="center", rotation=52, zorder=100)

    ax.set_xlim(X.min(), X.max())
    ax.set_ylim(Y.min(), Y.max())
    ax.set_xticks(np.arange(1, 9))
    ax.set_yticks([2030, 2033, 2036, 2039, 2042, 2045])
    ax.set_xlabel("Scrap Availability Growth (%/yr)", fontsize=16)
    ax.set_ylabel(r"H$_2$ Start Year", fontsize=16)
    ax.tick_params(axis="both", labelsize=14)
    for spine in ax.spines.values():
        spine.set_linewidth(1.2)

    cbar = fig.colorbar(cf, ax=ax, ticks=[0, 20, 40, 60, 80, 100],
                        fraction=0.046, pad=0.04, aspect=40)
    cbar.set_label("Required Grid Emission Offset (%)", fontsize=16)
    cbar.ax.tick_params(labelsize=14)
    cbar.solids.set_rasterized(False)
    cbar.solids.set_edgecolor("face")


def main():
    fig = plt.figure(figsize=(13.5, 6.2))
    gs = fig.add_gridspec(1, 2, width_ratios=[1, 1.15])
    axA = fig.add_subplot(gs[0, 0], projection="radar")
    axB = fig.add_subplot(gs[0, 1])

    panel_sobol(fig, axA)
    panel_grid_offset(fig, axB)

    fig.tight_layout()
    fig.canvas.draw()
    posA = axA.get_position()
    posB = axB.get_position()

    top_label = max(axA.get_xticklabels(), key=lambda l: l.get_window_extent(
        renderer=fig.canvas.get_renderer()).y1)
    label_top_fig = fig.transFigure.inverted().transform(
        top_label.get_window_extent(renderer=fig.canvas.get_renderer()))[1, 1]

    title_y = max(label_top_fig, posB.y1) + 0.012
    fig.text(posA.x0, title_y, "(a) Feasibility drivers",
             ha="left", va="bottom", fontsize=16, fontweight="bold")
    fig.text(posB.x0, title_y, "(b) Sectoral synergy: Power and Steel",
             ha="left", va="bottom", fontsize=16, fontweight="bold")

    out = os.path.join(HERE, "fig_feasibility_and_synergy.png")
    fig.savefig(out, dpi=300, bbox_inches="tight", facecolor="white")
    print("written:", out)

    out_pdf = os.path.join(HERE, "fig_feasibility_and_synergy.pdf")
    fig.savefig(out_pdf, format="pdf", dpi=600, bbox_inches="tight", facecolor="white")
    print("written:", out_pdf)


if __name__ == "__main__":
    main()
