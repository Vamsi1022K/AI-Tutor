import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d

def generate_roc_curve():
    # Points derived from visually interpolating the provided ROC curve image.
    fpr_points = np.array([0.0, 0.012, 0.03, 0.05, 0.08, 0.12, 0.18, 0.26, 0.38, 0.55, 0.75, 1.0])
    tpr_points = np.array([0.0, 0.23, 0.46, 0.66, 0.78, 0.86, 0.91, 0.94, 0.965, 0.985, 0.995, 1.0])

    # Interpolate to make a smooth curve
    interp_func = interp1d(fpr_points, tpr_points, kind='cubic')
    fpr = np.linspace(0, 1, 100)
    tpr = np.clip(interp_func(fpr), 0, 1)

    # Force the start and end points for exactly 0 and 1
    fpr[0], tpr[0] = 0.0, 0.0
    fpr[-1], tpr[-1] = 1.0, 1.0

    # Set up the plot
    fig, ax = plt.subplots(figsize=(8, 6))

    # Grid - dashed, faint light blue/gray
    ax.grid(True, linestyle='--', color='#e0e6ed', alpha=0.7)
    
    # Background color slightly lighter than the curve shading if needed, 
    # but the image has a clear #f4f8fd fill under the curve.
    
    # Shaded Area under the curve
    ax.fill_between(fpr, tpr, color='#ebf1fa', alpha=1.0) # Matches the light blue tint

    # Plot the random baseline
    ax.plot([0, 1], [0, 1], color='#9ca3af', linestyle='--', linewidth=1.5, label='Random Baseline')

    # Plot the ROC Curve line
    ax.plot(fpr, tpr, color='#1e53c4', linewidth=2.5, label='ROC Curve (AUC = 0.9294)')

    # Limits and spines
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.01])

    # Labels and Title
    ax.set_xlabel('False Positive Rate', fontsize=10)
    ax.set_ylabel('True Positive Rate', fontsize=10)
    ax.set_title('ROC Curve on Test Set', fontsize=14, fontweight='bold')

    # Legend
    ax.legend(loc="lower right", framealpha=1, edgecolor='#cccccc', fontsize=10)

    # Remove offset to match standard box
    plt.tight_layout()
    plt.savefig('roc_curve.png', dpi=300, bbox_inches='tight')
    print("ROC curve cleanly generated and saved to 'roc_curve.png'")

if __name__ == "__main__":
    generate_roc_curve()
