"""CTG-Federal themed plotting helpers for the AI Roadshow notebooks.

The whole point: keep the *lesson* cells free of matplotlib boilerplate. A
visual is one call — `bars(...)`, `compare(...)`, `lines(...)`, `scatter(...)` —
and it comes out on-brand (CTG blues + orange accent) every time.

    from roadshow_viz import bars, compare, lines, scatter

Each function just draws and shows the chart; it returns the Axes if a caller
wants to tweak it, but notebooks normally ignore the return value.
"""
from __future__ import annotations

import matplotlib.pyplot as plt
from matplotlib import font_manager  # noqa: F401  (ensures fonts are discoverable)

# ── CTG-Federal brand palette ────────────────────────────────────────────────
CTG = {
    "blue":    "#0073fe",   # primary
    "navy":    "#002550",   # dark
    "blue2":   "#0055bc",
    "blue3":   "#003b82",
    "sky":     "#5a9cff",
    "sky_lt":  "#9cc2ff",
    "orange":  "#f68d2e",   # accent / "watch this"
    "orange_dk": "#c06000",
    "gray":    "#54585c",
    "grid":    "#e9eaeb",
    "panel":   "#f4f5f6",
    "ink":     "#0b1220",
}
# Ordered series colors: lead blue, then navy, accent orange, then lighter blues.
CYCLE = [CTG["blue"], CTG["navy"], CTG["orange"], CTG["blue2"], CTG["sky"], CTG["gray"]]


def _theme(ax, title="", xlabel="", ylabel=""):
    """Apply the CTG look to an Axes."""
    fig = ax.figure
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    if title:
        ax.set_title(title, fontsize=14, fontweight="bold", color=CTG["navy"], pad=14)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=11, color=CTG["gray"])
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=11, color=CTG["gray"])
    ax.grid(axis="y", color=CTG["grid"], linewidth=1)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(CTG["grid"])
    ax.tick_params(colors=CTG["gray"], labelsize=10)
    return ax


def _newax(w=7.5, h=4.2):
    fig, ax = plt.subplots(figsize=(w, h), dpi=110)
    return ax


def _hline(ax, hline):
    """Draw an optional reference line: hline=(value, "label") — e.g. an SLO."""
    if not hline:
        return
    value, label = hline
    ax.axhline(value, color=CTG["orange_dk"], linestyle="--", linewidth=1.5)
    ax.annotate(label, (0.99, value), xycoords=("axes fraction", "data"),
                ha="right", va="bottom", color=CTG["orange_dk"], fontsize=9, fontweight="bold")


def bars(data: dict, title="", ylabel="", xlabel="", highlight=None, fmt="{:.0f}", hline=None):
    """Vertical bars from a {label: value} dict.

    highlight: a key (or list of keys) to paint in the accent orange — use it to
    point the room at the bar that matters.
    """
    ax = _newax()
    labels, values = list(data.keys()), list(data.values())
    hi = {highlight} if isinstance(highlight, str) else set(highlight or [])
    colors = [CTG["orange"] if k in hi else CTG["blue"] for k in labels]
    bars_ = ax.bar(labels, values, color=colors, width=0.62)
    for b, v in zip(bars_, values):
        ax.annotate(fmt.format(v), (b.get_x() + b.get_width() / 2, v),
                    ha="center", va="bottom", fontsize=10, color=CTG["navy"], fontweight="bold")
    _theme(ax, title, xlabel, ylabel)
    _hline(ax, hline)
    ax.margins(y=0.15)
    plt.tight_layout(); plt.show()
    return ax


def compare(data: dict, title="", ylabel="", xlabel="", fmt="{:.0f}", hline=None):
    """Like bars(), but tuned for A/B/C comparisons — each bar a distinct brand
    color so the contrast reads at a glance. First bar leads in primary blue."""
    ax = _newax()
    labels, values = list(data.keys()), list(data.values())
    colors = [CYCLE[i % len(CYCLE)] for i in range(len(labels))]
    bars_ = ax.bar(labels, values, color=colors, width=0.6)
    for b, v in zip(bars_, values):
        ax.annotate(fmt.format(v), (b.get_x() + b.get_width() / 2, v),
                    ha="center", va="bottom", fontsize=10, color=CTG["navy"], fontweight="bold")
    _theme(ax, title, xlabel, ylabel)
    _hline(ax, hline)
    ax.margins(y=0.15)
    plt.tight_layout(); plt.show()
    return ax


def lines(series: dict, x=None, title="", xlabel="", ylabel="", markers=True, hline=None):
    """One or more line series from {name: [y-values]}. Optional shared x list."""
    ax = _newax()
    for i, (name, ys) in enumerate(series.items()):
        xs = x if x is not None else list(range(len(ys)))
        ax.plot(xs, ys, label=name, color=CYCLE[i % len(CYCLE)],
                linewidth=2.4, marker="o" if markers else None, markersize=5)
    _theme(ax, title, xlabel, ylabel)
    _hline(ax, hline)
    if len(series) > 1:
        ax.legend(frameon=False, fontsize=10, labelcolor=CTG["gray"])
    plt.tight_layout(); plt.show()
    return ax


def stacked(data: dict, title="", ylabel="", xlabel="", show_total=True):
    """Stacked bars from a nested {group: {segment: value}} dict.

    Each group is a bar; segments stack in the brand color cycle (shared legend).
    Use it to show where a budget goes — e.g. tokens split into
    system / question / payload / scratch per context layout.
    """
    ax = _newax(8, 4.4)
    groups = list(data.keys())
    # Union of segment names across ALL groups (order-preserving) — groups may
    # carry different segments (e.g. a "skill" group has router/knowledge while a
    # "bloated" group has one inlined block); using only the first group's keys
    # would silently render the others as zero.
    segs = []
    for g in data.values():
        for s in g:
            if s not in segs:
                segs.append(s)
    bottoms = [0.0] * len(groups)
    for i, seg in enumerate(segs):
        vals = [data[g].get(seg, 0) for g in groups]
        ax.bar(groups, vals, bottom=bottoms, label=seg,
               color=CYCLE[i % len(CYCLE)], width=0.6)
        bottoms = [b + v for b, v in zip(bottoms, vals)]
    if show_total:
        for x, tot in enumerate(bottoms):
            ax.annotate(f"{tot:.0f}", (x, tot), ha="center", va="bottom",
                        fontsize=10, color=CTG["navy"], fontweight="bold")
    _theme(ax, title, xlabel, ylabel)
    ax.legend(frameon=False, fontsize=9, labelcolor=CTG["gray"], loc="upper right")
    ax.margins(y=0.15)
    plt.tight_layout(); plt.show()
    return ax


def scatter(points: dict, title="", xlabel="", ylabel=""):
    """Annotated scatter from {label: (x, y)} — e.g. cost vs quality per option."""
    ax = _newax()
    for i, (label, (px, py)) in enumerate(points.items()):
        c = CYCLE[i % len(CYCLE)]
        ax.scatter([px], [py], s=140, color=c, edgecolor="white", linewidth=1.5, zorder=3)
        ax.annotate(label, (px, py), textcoords="offset points", xytext=(8, 6),
                    fontsize=10, color=CTG["navy"], fontweight="bold")
    _theme(ax, title, xlabel, ylabel)
    ax.margins(0.18)
    plt.tight_layout(); plt.show()
    return ax


def timeline(events, title="Agent loop unrolled"):
    """Render an agent loop as a per-step timeline of moves.

    events: list of (kind, step, payload) tuples from the agent loop, where kind
    is one of reason/act/observe/final/compact. One row per step; a colored
    segment per move, left-to-right in canonical order.
    """
    move_color = {"reason": CTG["blue"], "act": CTG["orange"], "observe": CTG["blue3"],
                  "final": CTG["sky"], "compact": CTG["gray"]}
    order = ["reason", "act", "observe", "compact", "final"]
    by_step = {}
    for kind, step, _ in events:
        by_step.setdefault(step, []).append(kind)
    steps = sorted(by_step)
    fig, ax = plt.subplots(figsize=(8.5, 0.6 * max(len(steps), 1) + 1.2), dpi=110)
    fig.patch.set_facecolor("white"); ax.set_facecolor("white")
    for step in steps:
        x = 0
        for kind in order:
            if kind in by_step[step]:
                ax.barh(step, 1.0, left=x, color=move_color.get(kind, CTG["gray"]), edgecolor="white")
                ax.text(x + 0.5, step, kind, ha="center", va="center", color="white",
                        fontsize=8, fontweight="bold")
                x += 1.0
    ax.set_yticks(steps); ax.set_yticklabels([f"step {s}" for s in steps])
    ax.invert_yaxis()
    ax.set_title(title, fontsize=14, fontweight="bold", color=CTG["navy"], pad=12)
    ax.set_xlabel("moves within each step  →", fontsize=11, color=CTG["gray"])
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(CTG["grid"])
    ax.tick_params(colors=CTG["gray"], labelsize=10)
    ax.set_xlim(0, max(5, max((len(v) for v in by_step.values()), default=1)))
    plt.tight_layout(); plt.show()
    return ax


def hbars(data: dict, title="", xlabel="", highlight=None, fmt="{:.0f}"):
    """Horizontal bars from {label: value} — good when labels are long or you
    want a ranked list. highlight a key to paint it accent-orange."""
    ax = _newax(7.5, max(2.5, 0.5 * len(data) + 1))
    labels, values = list(data.keys()), list(data.values())
    hi = {highlight} if isinstance(highlight, str) else set(highlight or [])
    colors = [CTG["orange"] if k in hi else CTG["blue"] for k in labels]
    ax.barh(labels, values, color=colors, height=0.62)
    for y, v in enumerate(values):
        ax.annotate(fmt.format(v), (v, y), ha="left", va="center", xytext=(4, 0),
                    textcoords="offset points", fontsize=10, color=CTG["navy"], fontweight="bold")
    ax.invert_yaxis()
    fig = ax.figure; fig.patch.set_facecolor("white"); ax.set_facecolor("white")
    if title: ax.set_title(title, fontsize=14, fontweight="bold", color=CTG["navy"], pad=12)
    if xlabel: ax.set_xlabel(xlabel, fontsize=11, color=CTG["gray"])
    ax.grid(axis="x", color=CTG["grid"], linewidth=1); ax.set_axisbelow(True)
    for s in ("top", "right"): ax.spines[s].set_visible(False)
    for s in ("left", "bottom"): ax.spines[s].set_color(CTG["grid"])
    ax.tick_params(colors=CTG["gray"], labelsize=10)
    ax.margins(x=0.12)
    plt.tight_layout(); plt.show()
    return ax


def matrix(row_labels, col_labels, grid, title="", present="✓", absent="–"):
    """Themed presence matrix (heatmap). grid[i][j] truthy = present (blue),
    else absent (light gray). Use it for capability/coverage grids."""
    import matplotlib.colors as mcolors
    cmap = mcolors.ListedColormap([CTG["panel"], CTG["blue"]])
    ax = _newax(1.4 * len(col_labels) + 3, 0.5 * len(row_labels) + 1.5)
    ax.imshow([[1 if v else 0 for v in row] for row in grid], cmap=cmap, vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(col_labels))); ax.set_xticklabels([c.upper() for c in col_labels], fontweight="bold")
    ax.set_yticks(range(len(row_labels))); ax.set_yticklabels(row_labels)
    for i, row in enumerate(grid):
        for j, v in enumerate(row):
            ax.text(j, i, present if v else absent, ha="center", va="center",
                    color="white" if v else CTG["gray"], fontsize=11, fontweight="bold")
    fig = ax.figure; fig.patch.set_facecolor("white")
    if title: ax.set_title(title, fontsize=14, fontweight="bold", color=CTG["navy"], pad=12)
    ax.tick_params(colors=CTG["gray"], labelsize=10, length=0)
    for s in ax.spines.values(): s.set_visible(False)
    ax.set_xticks([x - 0.5 for x in range(1, len(col_labels))], minor=True)
    ax.set_yticks([y - 0.5 for y in range(1, len(row_labels))], minor=True)
    ax.grid(which="minor", color="white", linewidth=2)
    plt.tight_layout(); plt.show()
    return ax
