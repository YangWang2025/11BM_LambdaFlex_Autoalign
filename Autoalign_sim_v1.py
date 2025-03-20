import numpy as np
import time
import random
import matplotlib.pyplot as plt


# Simulated Motor Class
class SimulatedMotor:
    def __init__(self, start_pos):
        self.position = start_pos

    def move_to(self, position):
        time.sleep(0.3)  # Simulated movement delay
        self.position = position

# Simulated Detector Class
class SimulatedDetector:
    def __init__(self, start_pos, end_pos, peak_intensity=1000, width=1.5):
        self.peak_position = (start_pos + end_pos) / 2
        self.peak_intensity = peak_intensity
        self.width = width
    
    def get_roi_intensity(self, position):
        intensity = self.peak_intensity * np.exp(-((position - self.peak_position) ** 2) / (2 * self.width**2))
        noise = random.uniform(-50, 50)
        return intensity + noise

def initialization():
    global fig_analyzer, fig_piezo, axes_analyzer, axes_piezo
    fig_analyzer = None
    fig_piezo = None
    axes_analyzer = None
    axes_piezo = None
    
# Function to Create Figures if Needed
def create_figures(motor_name):
    global fig_analyzer, fig_piezo, axes_analyzer, axes_piezo

    if motor_name == "Analyzer":
        if fig_analyzer is None:
            fig_analyzer, axes_analyzer = plt.subplots(2, 6, figsize=(18, 8))
            fig_analyzer.suptitle("Analyzer Auto-alignment Results", fontsize=14)
            fig_analyzer.canvas.manager.set_window_title("Analyzer Auto-alignment")
            fig_analyzer.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.05, wspace=0.3, hspace=0.3)
            axes_analyzer = axes_analyzer.flatten()
            for i in range(12):
                axes_analyzer[i].set_title(f"Detector {i+1}", fontsize=10)
                axes_analyzer[i].set_xlabel("Position", fontsize=10)
                axes_analyzer[i].set_ylabel("Intensity", fontsize=10)
                axes_analyzer[i].grid(True)
        return fig_analyzer, axes_analyzer
    
    elif motor_name == "Piezo":
        if fig_piezo is None:
            fig_piezo, axes_piezo = plt.subplots(2, 6, figsize=(18, 8))
            fig_piezo.suptitle("Piezo Auto-alignment Results", fontsize=14)
            fig_piezo.canvas.manager.set_window_title("Piezo Auto-alignment")
            fig_piezo.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.05, wspace=0.3, hspace=0.3)
            axes_piezo = axes_piezo.flatten()
            for i in range(12):
                axes_piezo[i].set_title(f"Detector {i+1}", fontsize=10)
                axes_piezo[i].set_xlabel("Position", fontsize=10)
                axes_piezo[i].set_ylabel("Intensity", fontsize=10)
                axes_piezo[i].grid(True)
        return fig_piezo, axes_piezo

    return None, None

# Function to Run Alignment and Update Live Plot
def run_alignment(start_pos, end_pos, step_size, motor_name, detector_id):
    """Runs alignment for the given motor and updates live plot."""
    
    # Create figures only if motor is selected
    if motor_name == "Analyzer":
        fig_analyzer, axes_analyzer = create_figures("Analyzer")
        #fig_analyzer.canvas.manager.window.state('zoomed')
        ax = axes_analyzer[detector_id - 1]
        color = 'k'
    elif motor_name == "Piezo":
        fig_piezo, axes_piezo = create_figures("Piezo")
        #fig_piezo.canvas.manager.window.state('zoomed')
        ax = axes_piezo[detector_id - 1]
        color = 'b'
    else:
        print(f"Skipping {motor_name} alignment. Not selected.")
        return  # Exit if the motor isn't selected
    
    motor = SimulatedMotor(start_pos)
    detector = SimulatedDetector(start_pos, end_pos)

    positions = np.arange(start_pos, end_pos + step_size, step_size)
    roi_counts = []
    
    print(f"   → {motor_name} alignment running for Detector {detector_id}.")
    
    line, = ax.plot([], [], color + '-')
    peak_point, = ax.plot([], [], 'ro', markersize=8, label="Max ROI")
    legend = ax.legend(loc="lower left")

    # Perform the scan
    for pos in positions:
        motor.move_to(pos)
        roi_value = detector.get_roi_intensity(pos)
        roi_counts.append(roi_value)
        update_plot(ax, line, peak_point, positions, roi_counts, legend)
        plt.pause(0.1)  # Ensure the figure updates independently
    
    print(f"   → {motor_name} alignment completed for Detector {detector_id}.")

    # Find and move to the best position
    max_index = np.argmax(roi_counts)
    best_position = positions[max_index]
    motor.move_to(best_position)
    update_plot(ax, line, peak_point, positions, roi_counts, legend)
    plt.pause(0.1)  # Final refresh after best position is found

# Function to Update Plot Dynamically
def update_plot(ax, line, peak_point, positions, roi_counts, legend):
    if not roi_counts:
        return
    
    line.set_xdata(positions[:len(roi_counts)])
    line.set_ydata(roi_counts)
    ax.relim()
    ax.autoscale_view()

    # Find the maximum ROI value (peak data point)
    max_index = np.argmax(roi_counts)
    max_pos = positions[max_index]
    max_val = roi_counts[max_index]

    # Set the peak point data
    peak_point.set_xdata([max_pos])
    peak_point.set_ydata([max_val])

    # Update the legend with the Max ROI info for the peak point
    legend.get_texts()[0].set_text(f"Max ROI: ({max_pos:.5f}, {max_val:.0f})")

    plt.draw()
    plt.pause(0.1)    

# Function to Show Figures After All Alignments
def show_figures():
    """Display the final alignment figures after all detectors are processed."""
    global fig_analyzer, fig_piezo
    if fig_analyzer is not None:
        fig_analyzer.tight_layout()
    if fig_piezo is not None:
        fig_piezo.tight_layout()
    plt.show()
