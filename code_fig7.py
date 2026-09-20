"""Ablation bar chart for desired-pose and executed-pose residual targets.

Wide solid bars show Desired-Pose (Ours), while narrow hatched bars overlaid
at the same centers show Executed-Pose (Ablation).
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch


# ----------------------- Editable data -----------------------
tasks = ["Pump Bottle", "Clean Whiteboard", "Insert Plug", "Flip Rocker Switch"]
backbones = [r"$\pi_0$", r"$\pi_{0.5}$", "SmolVLA"]

# Rows correspond to tasks; columns correspond to VLA backbones.
data_desired = np.array([
    [85, 90, 70],
    [20, 40, 45],
    [70, 70, 65],
    [85, 75, 40],
], dtype=float)

data_executed = np.array([
    [15, 0, 0],
    [0, 5, 15],
    [0, 0, 0],
    [35, 55, 20],
], dtype=float)

# One fixed color for each VLA backbone.
# colors = [
#     (0.75, 0.75, 0.75),  # pi_0: light gray
#     (0.55, 0.75, 0.87),  # pi_0.5: light blue
#     (0.93, 0.72, 0.55),  # SmolVLA: light orange
# ]
colors = [
    (0.45, 0.45, 0.45),  # pi_0: neutral gray
    (0.00, 0.45, 0.70),  # pi_0.5: blue
    (0.84, 0.37, 0.00),  # SmolVLA: vermillion/orange
]



# ----------------------- Input checks ------------------------
expected_shape = (len(tasks), len(backbones))
if data_desired.shape != expected_shape or data_executed.shape != expected_shape:
    raise ValueError(
        f"Both data arrays must have shape {expected_shape}; "
        f"got {data_desired.shape} and {data_executed.shape}."
    )


# ----------------------- Figure style ------------------------
plt.rcParams.update({
    "font.family": "STIXGeneral",
    "mathtext.fontset": "stix",
    "font.size": 14,
    "axes.labelsize": 14,
    "xtick.labelsize": 14,
    "ytick.labelsize": 14,
    "legend.fontsize": 13,
    "axes.linewidth": 0.8,
    "xtick.direction": "in",
    "ytick.direction": "in",
    "hatch.linewidth": 0.7,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
})


# ----------------------- Nested grouped bars -----------------
x = np.arange(len(tasks))
bar_width = 0.18
inner_width = bar_width * 0.55
bar_gap = 0.04
bar_step = bar_width + bar_gap

# Extra height is needed for the two legend rows above the axes.
fig, ax = plt.subplots(figsize=(7.0, 4.0))

for backbone_idx, backbone in enumerate(backbones):
    offset = (backbone_idx - (len(backbones) - 1) / 2) * bar_step
    positions = x + offset

    # Wide solid bars: Desired-Pose (Ours).
    ax.bar(
        positions,
        data_desired[:, backbone_idx],
        width=bar_width,
        color=colors[backbone_idx],
        edgecolor="black",
        linewidth=0.7,
        zorder=2,
    )

    # Narrow hatched bars: Executed-Pose (Ablation).
    # Skip zeros to avoid small black lines at y = 0.
    visible = data_executed[:, backbone_idx] > 0
    ax.bar(
        positions[visible],
        data_executed[visible, backbone_idx],
        width=inner_width,
        color=colors[backbone_idx],
        hatch="////",
        edgecolor="black",
        linewidth=0.7,
        zorder=3,
    )


# ----------------------- Axes -------------------------------
ax.set_ylabel("Success Rate (%)")
ax.set_xticks(x)
ax.set_xticklabels(tasks)
ax.set_ylim(0, 100)
ax.set_yticks(np.arange(0, 101, 20))
ax.grid(axis="y", linestyle="--", linewidth=0.6, alpha=0.45, zorder=0)


# ----------------------- Two external legends ---------------
backbone_handles = [
    Patch(facecolor=colors[i], edgecolor="black", label=backbones[i])
    for i in range(len(backbones))
]

target_handles = [
    Patch(
        facecolor="white",
        edgecolor="black",
        label="Desired-Pose (Ours)",
    ),
    Patch(
        facecolor="white",
        edgecolor="black",
        hatch="////",
        label="Executed-Pose (Ablation)",
    ),
]

# Reserve the upper 30% of the figure for the two legend rows.
# The legends use figure coordinates, so their locations remain stable even
# when the axes margins change.
fig.subplots_adjust(left=0.03, right=0.985, bottom=0.17, top=0.80)

legend_backbone = fig.legend(
    handles=backbone_handles,
    ncol=3,
    loc="upper center",
    bbox_to_anchor=(0.5, 0.995),
    columnspacing=5.45,
    handletextpad=0.5,
    frameon=True,
    fancybox=False,
    framealpha=0.6,
    facecolor="white",
    edgecolor="black",
)

legend_target = fig.legend(
    handles=target_handles,
    ncol=2,
    loc="upper center",
    bbox_to_anchor=(0.5, 0.91),
    columnspacing=1.4,
    handletextpad=0.5,
    frameon=True,
    fancybox=False,
    framealpha=0.6,
    facecolor="white",
    edgecolor="black",
)


# ----------------------- Export ------------------------------
extra_artists = (legend_backbone, legend_target)
fig.savefig(
    "ablation_bar_chart.pdf",
    bbox_inches="tight",
    bbox_extra_artists=extra_artists,
    pad_inches=0.03,
)

plt.show()