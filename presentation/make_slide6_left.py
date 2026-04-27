import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

jobs = [
    ("Word processors\n& typists", -36),
    ("Telephone\noperators", -28),
    ("Data entry\nkeyers", -26),
    ("Telemarketers", -22),
    ("Payroll &\ntimekeeping clerks", -17),
]

labels = [j[0] for j in jobs]
values = [j[1] for j in jobs]

fig, ax = plt.subplots(figsize=(6, 5))
fig.patch.set_facecolor("white")
ax.set_facecolor("white")

bars = ax.barh(
    range(len(labels)),
    values,
    color="#e63946",
    height=0.6,
    zorder=3,
)

# Value labels inside bars
for i, (bar, val) in enumerate(zip(bars, values)):
    ax.text(
        val / 2,
        bar.get_y() + bar.get_height() / 2,
        f"{val}%",
        va="center",
        ha="center",
        color="white",
        fontsize=13,
        fontweight="bold",
    )

ax.set_yticks(range(len(labels)))
ax.set_yticklabels(labels, color="#222222", fontsize=11)
ax.invert_yaxis()

ax.set_xlim(-42, 0)
ax.set_xlabel("Projected employment change by 2034", color="#666666", fontsize=9)
ax.tick_params(axis="x", colors="#999999", labelsize=8)
ax.tick_params(axis="y", length=0)

for spine in ax.spines.values():
    spine.set_visible(False)

ax.xaxis.grid(True, color="#eeeeee", linewidth=0.5, zorder=0)
ax.set_axisbelow(True)

ax.set_title("Highest-Risk Jobs by Projected Decline", color="#222222", fontsize=12, pad=12, fontweight="bold")

plt.tight_layout()
plt.savefig("figures/slide6_vulnerable_jobs.png", dpi=180, bbox_inches="tight", facecolor="white")
print("saved: figures/slide6_vulnerable_jobs.png")
