import numpy as np
import time
import random
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
from tkinter import Tk, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from threading import Thread 

# Simulated Motor Class
class SimulatedMotor:
    def __init__(self, start_pos):
        self.position = start_pos

    def move_to(self, position):
        time.sleep(0.3)  # Simulated movement delay
        self.position = position

# Simulated Detector Class
class SimulatedDetector:
    def __init__(self, start_pos, end_pos, peak_intensity=1000, width=1.5, asymmetry_factor=0.5):
        self.peak_position = (start_pos + end_pos) / 2
        self.peak_intensity = peak_intensity
        self.width = width
        self.asymmetry_factor = asymmetry_factor  # Factor to control asymmetry
    
    def get_roi_intensity(self, position):
        # intensity = self.peak_intensity * np.exp(-((position - self.peak_position) ** 2) / (2 * self.width**2))
        # noise = random.uniform(-50, 50)

        # Gaussian intensity calculation
        intensity = self.peak_intensity * np.exp(-((position - self.peak_position) ** 2) / (2 * self.width**2))

        # Calculate distance from the peak position
        distance_from_peak = abs(position - self.peak_position)

        # Introduce asymmetry, which becomes stronger as the distance increases
        if position > self.peak_position:
            # Bias to the right side (larger positions)
            intensity *= (1 + self.asymmetry_factor * (distance_from_peak / self.width))
        else:
            # Bias to the left side (smaller positions)
            intensity *= (1 - self.asymmetry_factor * (distance_from_peak / self.width))

        # Add some noise to the intensity
        noise = random.uniform(-10, 10)
        return intensity + noise
        
def initialization():
    global fig, axes, alignment_counter
    fig = None
    axes = None
    alignment_counter = 0
    
def create_figure(motor_name):
    """Create and return a figure with 12 subplots based on the motor type."""
    global fig, axes

    fig, axes = plt.subplots(2, 6, figsize=(18, 8))
    fig.suptitle(f"{motor_name} Auto-alignment Results", fontsize=14)
    fig.subplots_adjust(left=0.05, right=0.95, top=0.9, bottom=0.05, wspace=0.3, hspace=0.3)
    axes = axes.flatten()
    
    for i in range(12):
        axes[i].set_title(f"Detector {i+1}", fontsize=10)
        axes[i].set_xlabel("Position", fontsize=10)
        axes[i].set_ylabel("Intensity", fontsize=10)
        axes[i].grid(True)
        
    return fig, axes

def gaussian(x, amplitude, mean, sigma):
    """Gaussian function for curve fitting."""
    return amplitude * np.exp(-(x - mean)**2 / (2 * sigma**2))

def run_alignment(start_pos, end_pos, step_size, motor_name, detector_id, axes, fig, canvas, update_callback):
    """Runs alignment for the given motor and updates live plot. After collecting intensity data, fits a Gaussian curve to the data."""
    global alignment_counter 
    # Check if the number of iterations has exceeded the limit
    alignment_counter += 1
    if alignment_counter > 3:
        print("Maximum alignment iterations reached. Stopping further alignment.")
        return   
    
    motor = SimulatedMotor(start_pos)
    detector = SimulatedDetector(start_pos, end_pos)

    positions = np.arange(start_pos, end_pos + step_size, step_size)
    roi_counts = []
    
    ax = axes[detector_id - 1]
    color = 'k' if motor_name == "Analyzer" else 'b'
    line, = ax.plot([], [], color + '-')
    peak_point, = ax.plot([], [], 'ro', markersize=8)
    legend = ax.legend([peak_point], ["Max ROI"], loc="lower left")

    # Perform the scan (in a separate thread to avoid blocking UI)
    for pos in positions:
        motor.move_to(pos)
        roi_value = detector.get_roi_intensity(pos)
        roi_counts.append(roi_value)
        update_plot(ax, line, peak_point, positions, roi_counts, legend)

        # Schedule the callback to refresh the figure
        update_callback()
        time.sleep(0.1)  # Simulated delay for the motor move and detector update

    # After the loop, perform Gaussian fit to the collected data
    try:
        popt, _ = curve_fit(gaussian, positions, roi_counts, p0=[np.max(roi_counts), positions[np.argmax(roi_counts)], 1])
        amplitude, mean, sigma = popt
        
        if sigma <= 0 or amplitude <= 0:
            raise ValueError("Invalid Gaussian fit parameters (amplitude or sigma are non-positive).")

        # The peak position is the 'mean' from the Gaussian fit
        best_position = mean
        print(f"Best position (from Gaussian fit): {best_position:.5f}")

        # Update the plot with the fitted curve
        fit_curve = gaussian(positions, *popt)
        gaussian_line, = ax.plot(positions, fit_curve, 'g--')
        legend = ax.legend([peak_point, gaussian_line], ["Max ROI", f"Gaussian Peak @ ({best_position:.5f})"], loc="lower left")
        update_plot(ax, line, peak_point, positions, roi_counts, legend)   
        
        if motor_name == "Analyzer":
            if best_position < start_pos or best_position > end_pos:
                range_size = end_pos - start_pos
                new_start_pos = best_position - range_size / 2
                new_end_pos = best_position + range_size / 2
                print(f"Fitted mean outside range. Adjusting range: New start_pos = {new_start_pos:.5f}, new_end_pos = {new_end_pos:.5f}")

                # Rerun the alignment with the new positions
                if abs(new_start_pos-start_pos) > 0.00125/2:
                    run_alignment(new_start_pos, new_end_pos, step_size, motor_name, detector_id, axes, fig, canvas, update_callback)
                return  # Exit the function so we don't continue with the old range
        
    except Exception as e:
        print(f"Error fitting Gaussian: {e}")
        # If Gaussian fitting fails, fallback to the position of the max intensity as the best position
        max_index = np.argmax(roi_counts)
        best_position = positions[max_index]
        print(f"Best position (from max ROI count): {best_position:.5f}")
    
    motor.move_to(start_pos)
    motor.move_to(best_position)
    max_vol = detector.get_roi_intensity(pos)
    print(f"Max ROI: ({best_position:.5f}, {max_vol:.0f})")
    update_callback()  # Final update after the best position is found
    
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
    
def show_figures_in_tabs(alignment_info):
    """Create a Tkinter window with tabs for Analyzer and Piezo plots."""
    global root  # Make root a global variable so we can use it inside update_canvas
    root = Tk()
    root.title("Motor Alignment Results")

    # Create a tab control
    tab_control = ttk.Notebook(root)

    # Create tabs
    analyzer_tab = ttk.Frame(tab_control)
    piezo_tab = ttk.Frame(tab_control)

    tab_control.add(analyzer_tab, text="Analyzer")
    tab_control.add(piezo_tab, text="Piezo")
    tab_control.pack(expand=1, fill="both")

    # Create and embed figures for both Analyzer and Piezo
    fig_analyzer, axes_analyzer = create_figure("Analyzer")
    canvas_analyzer = FigureCanvasTkAgg(fig_analyzer, analyzer_tab)

    toolbar_analyzer = NavigationToolbar2Tk(canvas_analyzer, analyzer_tab)
    toolbar_analyzer.update()
    toolbar_analyzer.pack(fill="x")  # Pack the toolbar at the top of the tab

    canvas_analyzer.get_tk_widget().pack(fill="both", expand=True)

    fig_piezo, axes_piezo = create_figure("Piezo")
    canvas_piezo = FigureCanvasTkAgg(fig_piezo, piezo_tab)

    toolbar_piezo = NavigationToolbar2Tk(canvas_piezo, piezo_tab)
    toolbar_piezo.update()
    toolbar_piezo.pack(fill="x")  # Pack the toolbar at the top of the tab

    canvas_piezo.get_tk_widget().pack(fill="both", expand=True)

    # Function to update the plot in Tkinter window
    def update_canvas():
        # Schedule canvas drawing in the main thread using after
        root.after(0, canvas_analyzer.draw)
        root.after(0, canvas_piezo.draw)
        
    def alignment_thread():
        """Loop over the alignment_info dictionary and update the plots."""
        for detector_id, motors in alignment_info.items():
            if 'analyzer' in motors:
                analyzer_info = motors['analyzer']
                run_alignment(analyzer_info['start'], analyzer_info['end'], analyzer_info['step'], 
                    "Analyzer", detector_id, axes_analyzer, fig_analyzer, canvas_analyzer, update_canvas)

            if 'piezo' in motors:
                piezo_info = motors['piezo']
                run_alignment(piezo_info['start'], piezo_info['end'], piezo_info['step'], 
                    "Piezo", detector_id, axes_piezo, fig_piezo, canvas_piezo, update_canvas)        
    
    # Start alignment in a separate thread to keep UI responsive
    thread = Thread(target=alignment_thread)  # Pass alignment_info as an argument
    thread.start()


    # Add a protocol to handle window close event
    def on_close():
        root.quit()  # Exit the Tkinter main loop
        root.destroy()  # Destroy the Tkinter window itself

    root.protocol("WM_DELETE_WINDOW", on_close)  # Capture window close event

    # Run Tkinter event loop
    root.mainloop()
