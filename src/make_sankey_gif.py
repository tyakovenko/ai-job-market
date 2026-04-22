"""
Animated Sankey-style particle flow diagram.
Illustrates the Automation Paradox: high risk → adaptive capacity filter → two outcomes.
Output: docs/assets/sankey_flow.gif
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.animation import FuncAnimation
from matplotlib.patches import FancyBboxPatch

# ── Layout ─────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 5), facecolor="#0f1117")
ax.set_xlim(0, 11)
ax.set_ylim(0, 5)
ax.axis("off")
ax.set_facecolor("#0f1117")

COL_RED   = "#e74c3c"
COL_BLUE  = "#3498db"
COL_GREEN = "#2ecc71"
COL_TEXT  = "#ecf0f1"
COL_DIM   = "#7f8c8d"

# Node centres
NX_RISK  = 1.6;  NY_RISK  = 2.5
NX_ADP   = 5.5;  NY_ADP   = 2.5
NX_GROW  = 9.4;  NY_GROW  = 3.65
NX_DEC   = 9.4;  NY_DEC   = 1.35

def draw_box(cx, cy, lines, color, w=2.0, h=0.95):
    box = FancyBboxPatch(
        (cx - w/2, cy - h/2), w, h,
        boxstyle="round,pad=0.12",
        facecolor=color, alpha=0.88,
        edgecolor="white", linewidth=1.4,
    )
    ax.add_patch(box)
    ax.text(cx, cy, lines, ha="center", va="center",
            color="white", fontsize=8.5, fontweight="bold",
            linespacing=1.4)

draw_box(NX_RISK, NY_RISK,  "HIGH\nAUTOMATION RISK",  COL_RED)
draw_box(NX_ADP,  NY_ADP,   "ADAPTIVE\nCAPACITY",     COL_BLUE)
draw_box(NX_GROW, NY_GROW,  "JOB GROWTH",             COL_GREEN)
draw_box(NX_DEC,  NY_DEC,   "JOB DECLINE",            COL_RED)

# Label percentages (static)
ax.text(NX_GROW + 1.15, NY_GROW, "~35%", color=COL_GREEN,
        fontsize=9, va="center", fontweight="bold")
ax.text(NX_DEC  + 1.15, NY_DEC,  "~65%", color=COL_RED,
        fontsize=9, va="center", fontweight="bold")

# Flow label
ax.text(5.5, 4.7, "The Automation Paradox — High Risk Doesn't Always Mean Job Loss",
        ha="center", color=COL_TEXT, fontsize=9.5, style="italic", alpha=0.85)
ax.text(5.5, 0.22,
        "Adaptive capacity (wage + education) determines which stream workers enter.",
        ha="center", color=COL_DIM, fontsize=8.2)

# ── Bezier helpers ─────────────────────────────────────────────────────────
def cubic_bezier(p0, p1, p2, p3, t):
    t = np.asarray(t)
    u = 1 - t
    return (u**3)[:,None]*p0 + (3*u**2*t)[:,None]*p1 + \
           (3*u*t**2)[:,None]*p2 + (t**3)[:,None]*p3

# Three paths: risk→adaptive, adaptive→growth, adaptive→decline
def path_risk_adp(t):
    return cubic_bezier(
        np.array([NX_RISK + 1.0, NY_RISK]),
        np.array([3.3,            NY_RISK]),
        np.array([4.2,            NY_ADP ]),
        np.array([NX_ADP  - 1.0, NY_ADP ]),
        t,
    )

def path_adp_grow(t):
    return cubic_bezier(
        np.array([NX_ADP  + 1.0, NY_ADP  ]),
        np.array([7.2,            NY_ADP + 0.6]),
        np.array([8.1,            NY_GROW]),
        np.array([NX_GROW - 1.0, NY_GROW]),
        t,
    )

def path_adp_dec(t):
    return cubic_bezier(
        np.array([NX_ADP  + 1.0, NY_ADP  ]),
        np.array([7.2,            NY_ADP - 0.6]),
        np.array([8.1,            NY_DEC ]),
        np.array([NX_GROW - 1.0, NY_DEC ]),
        t,
    )

# Draw static faint flow bands
ts = np.linspace(0, 1, 200)
for path_fn, col, alpha in [
    (path_risk_adp, COL_BLUE,  0.12),
    (path_adp_grow, COL_GREEN, 0.10),
    (path_adp_dec,  COL_RED,   0.10),
]:
    pts = path_fn(ts)
    ax.plot(pts[:, 0], pts[:, 1], color=col, lw=14, alpha=alpha, solid_capstyle="round")

# ── Particles ──────────────────────────────────────────────────────────────
N_TOTAL  = 48          # total particles in circulation
N_GROWTH = 17          # ~35% go to growth, rest to decline
FRAMES   = 72
SPEED    = 1 / FRAMES  # one full traversal per animation loop

rng = np.random.default_rng(42)

# Each particle has a phase offset in [0, 1) and a y-jitter
phases  = rng.uniform(0, 1, N_TOTAL)
jitters = rng.uniform(-0.08, 0.08, N_TOTAL)
colors  = np.array([COL_GREEN]*N_GROWTH + [COL_RED]*(N_TOTAL - N_GROWTH))
rng.shuffle(colors)

scat = ax.scatter([], [], s=28, zorder=5)

def particle_pos(phase, jitter, color):
    t = phase % 1.0

    # Segment 0-0.45: risk → adaptive
    # Segment 0.45-1.0: adaptive → growth or decline
    if t < 0.45:
        u = t / 0.45
        pts = path_risk_adp(np.array([u]))
    else:
        u = (t - 0.45) / 0.55
        if color == COL_GREEN:
            pts = path_adp_grow(np.array([u]))
        else:
            pts = path_adp_dec(np.array([u]))

    return pts[0, 0], pts[0, 1] + jitter

def animate(frame):
    ph = (phases + frame * SPEED) % 1.0
    xs, ys, cs = [], [], []
    for i in range(N_TOTAL):
        x, y = particle_pos(ph[i], jitters[i], colors[i])
        xs.append(x); ys.append(y); cs.append(colors[i])
    scat.set_offsets(np.c_[xs, ys])
    scat.set_color(cs)
    scat.set_alpha(0.82)
    return (scat,)

ani = FuncAnimation(fig, animate, frames=FRAMES, interval=55, blit=True)

out = "docs/assets/sankey_flow.gif"
ani.save(out, writer="pillow", dpi=120)
print(f"Saved → {out}")
