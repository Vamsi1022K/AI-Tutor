import os
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def add_box(ax, x, y, w, h, text, fc="#eef3fa", ec="#9fb0c8", fs=10, bold=False):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.012,rounding_size=0.02",
        linewidth=1.2, edgecolor=ec, facecolor=fc
    )
    ax.add_patch(box)
    ax.text(
        x + w / 2, y + h / 2, text,
        ha="center", va="center",
        fontsize=fs, color="#1f2a3a",
        fontweight="bold" if bold else "normal",
        wrap=True
    )


def add_arrow(ax, p1, p2, color="#7c8fa8"):
    arr = FancyArrowPatch(
        p1, p2, arrowstyle="-|>", mutation_scale=12,
        linewidth=1.2, color=color
    )
    ax.add_patch(arr)


def diagram_v1(path):
    fig, ax = plt.subplots(figsize=(15, 9))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(0.5, 0.965, "AI Compiler Tutor System Architecture", ha="center",
            fontsize=18, fontweight="bold", color="#1f2a3a")
    ax.text(0.5, 0.935, "with Green Compiler Integration", ha="center",
            fontsize=12, color="#4b5d75")

    # UI layer
    add_box(ax, 0.08, 0.82, 0.18, 0.09, "Web UI\nweb/index.html", bold=True)
    add_box(ax, 0.30, 0.82, 0.18, 0.09, "Desktop GUI\nsrc/gui.py", bold=True)

    # API
    add_box(
        ax, 0.53, 0.78, 0.40, 0.14,
        "Flask API Server (src/server.py)\n"
        "/api/health, /api/files, /api/file/<name>, /api/analyze_all,\n"
        "/api/analyze, /api/security, /api/ast, /api/evaluate",
        fc="#e8eef8", ec="#8ea2bf", fs=9, bold=True
    )
    add_arrow(ax, (0.26, 0.865), (0.53, 0.85))
    add_arrow(ax, (0.48, 0.865), (0.53, 0.85))

    # Pipeline
    y = 0.60
    w = 0.11
    h = 0.11
    xs = [0.05, 0.18, 0.31, 0.44, 0.57, 0.70, 0.83]
    labels = [
        "1) GCC\nCompile+Parse",
        "2) Rule Match\n+ Dataset",
        "3) AI\nFallback",
        "4) Static\nChecks",
        "5) Security\nScan",
        "6) AST\nBuild",
        "7) Green\nMetrics",
    ]
    for x, t in zip(xs, labels):
        add_box(ax, x, y, w, h, t, fc="#f2f6fc", ec="#aab8cc", fs=9)
    for i in range(len(xs) - 1):
        add_arrow(ax, (xs[i] + w, y + h / 2), (xs[i + 1], y + h / 2))
    add_arrow(ax, (0.73, 0.78), (0.11, y + h))

    # Storage
    add_box(ax, 0.06, 0.36, 0.20, 0.10, "errors/*.c", fc="#f5f7fb")
    add_box(ax, 0.29, 0.36, 0.20, 0.10, "phase4_dataset/\nannotated_errors.json", fc="#f5f7fb")
    add_box(ax, 0.52, 0.36, 0.20, 0.10, "models/flan-t5-compiler-tutor\n(optional)", fc="#f5f7fb")
    add_box(ax, 0.75, 0.36, 0.20, 0.10, "green_history\n(in-memory)", fc="#f5f7fb")

    add_arrow(ax, (0.16, 0.46), (0.11, y))
    add_arrow(ax, (0.39, 0.46), (0.24, y))
    add_arrow(ax, (0.62, 0.46), (0.37, y))
    add_arrow(ax, (0.85, 0.46), (0.88, y))

    # CLI + outputs
    add_box(ax, 0.06, 0.18, 0.30, 0.12,
            "CLI Orchestrator (src/main.py)\n-> executor.py / ast_parser.py /\nsecure_checker.py / evaluate.py",
            fc="#eef4ff", ec="#9db0cf", fs=9)
    add_box(ax, 0.47, 0.16, 0.46, 0.16,
            "JSON Output to UI\nerrors + explanations + fixes\nsecurity issues + AST nodes\nenergy_j + carbon_mg + avg_power_w + stage breakdown",
            fc="#eaf6ee", ec="#96b89f", fs=10, bold=True)
    add_arrow(ax, (0.88, y), (0.70, 0.32))

    plt.tight_layout()
    plt.savefig(path, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close()


def diagram_v2(path):
    fig, ax = plt.subplots(figsize=(16, 8))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("white")

    ax.text(0.5, 0.95, "End-to-End Architecture: AI Compiler Tutor + Green Compiler",
            ha="center", fontsize=17, fontweight="bold", color="#1f2a3a")

    add_box(ax, 0.03, 0.62, 0.13, 0.22, "Input\nUser + Code\nEditor + Upload", bold=True)
    add_box(ax, 0.19, 0.62, 0.15, 0.22, "Application\nWeb UI +\nDesktop GUI", bold=True)
    add_box(ax, 0.37, 0.62, 0.15, 0.22, "Server\nsrc/server.py", bold=True, fc="#e8eef8")
    add_box(ax, 0.55, 0.62, 0.18, 0.22,
            "Analysis Core\nGCC + Rule Matcher\nAI Fallback\nSecurity + AST +\nStatic Checks", bold=True)
    add_box(ax, 0.76, 0.62, 0.21, 0.22,
            "Output Layer\nIssues + Fixes\nSecurity Report\nAST + Green Metrics", bold=True, fc="#eaf6ee", ec="#96b89f")

    add_arrow(ax, (0.16, 0.73), (0.19, 0.73))
    add_arrow(ax, (0.34, 0.73), (0.37, 0.73))
    add_arrow(ax, (0.52, 0.73), (0.55, 0.73))
    add_arrow(ax, (0.73, 0.73), (0.76, 0.73))

    add_box(ax, 0.40, 0.30, 0.34, 0.22,
            "Green Compiler Core\n"
            "1) Stage Profiler\n"
            "2) Energy Provider Selector\n"
            "   (CodeCarbon / Intel CSV / TDP Fallback)\n"
            "3) Carbon Calculator\n"
            "4) Energy Virtualization", fc="#edf8f0", ec="#7fb48f", bold=True)
    add_arrow(ax, (0.64, 0.62), (0.57, 0.52))
    add_arrow(ax, (0.74, 0.41), (0.84, 0.62))

    add_box(ax, 0.03, 0.10, 0.20, 0.14, "errors folder\n+ demo C files", fc="#f5f7fb")
    add_box(ax, 0.26, 0.10, 0.20, 0.14, "annotated_errors.json", fc="#f5f7fb")
    add_box(ax, 0.49, 0.10, 0.20, 0.14, "optional trained model", fc="#f5f7fb")
    add_box(ax, 0.72, 0.10, 0.25, 0.14, "generated plots\nroc_curve.png\nconfusion_matrix.png\ntraining_metrics.png", fc="#f5f7fb")

    add_arrow(ax, (0.13, 0.24), (0.44, 0.62))
    add_arrow(ax, (0.36, 0.24), (0.48, 0.62))
    add_arrow(ax, (0.59, 0.24), (0.58, 0.62))
    add_arrow(ax, (0.84, 0.24), (0.86, 0.62))

    add_box(
        ax, 0.03, 0.36, 0.31, 0.16,
        "Formula Note\nenergy_j = avg_power_w * duration_s\n"
        "carbon_mg = (energy_j / 3,600,000) * 0.475 * 1,000,000",
        fc="#fffaf0", ec="#d2c39b", fs=10
    )

    plt.tight_layout()
    plt.savefig(path, dpi=220, bbox_inches="tight", facecolor="white")
    plt.close()


if __name__ == "__main__":
    p1 = os.path.join(BASE_DIR, "architecture_diagram_v1.png")
    p2 = os.path.join(BASE_DIR, "architecture_diagram_v2.png")
    diagram_v1(p1)
    diagram_v2(p2)
    print(f"Generated: {p1}")
    print(f"Generated: {p2}")
