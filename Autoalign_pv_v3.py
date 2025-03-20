import numpy as np
import time
import epics
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from tkinter import Tk, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from threading import Thread

# TwoThetaDrive Class to Move the Arm to a Specified Angle 
class TwoThetaDrive:
    def __init__(self, detector_id):
        # PV for the TwoTheta motor
        self.pv_name = "11bmb:m28"  # TwoTheta motor PV name
        self.detector_id = detector_id
        self.angle = self.calculate_angle(self.detector_id)  # Initial angle based on detector ID
    
    def calculate_angle(self, detector_id):
        """Calculate the 2Theta angle based on detector ID (1 to 12)."""
        if 1 <= detector_id <= 12:
            return -2 * (detector_id - 1)  # Angle will be 0, -2, -4, ..., -22
        else:
            raise ValueError("Detector ID must be between 1 and 12")

    def get_pos(self):
        """Fetch the current motor position from EPICS."""
        self.position = epics.caget(self.pv_name)  # Update position
        return self.position
        
    def move_to(self):
        """Move the TwoTheta motor to the calculated angle."""
        print(f"Moving 2theta arm to {self.angle} degrees to align Detector {self.detector_id}.")
        try:
            epics.caput(self.pv_name, self.angle, wait=True, timeout=600)  # Move motor to the calculated angle
        except Exception as e:
            print(f"Error moving 2theta motor {self.pv_name} to position {self.angle}: {e}")    
        time.sleep(0.3)  # Simulate movement delay
        
# MotorDrive Class using epics.caput to set position
class MotorDrive:
    def __init__(self, pv_name):
        self.pv_name = pv_name
        self.position = epics.caget(self.pv_name)  # Get initial position

    def get_pos(self):
        """Fetch the current motor position from EPICS."""
        self.position = epics.caget(self.pv_name)  # Update position
        return self.position
        
    def move_to(self, position):
        try:
            epics.caput(self.pv_name, position, wait=True, timeout=600)
        except Exception as e:
            print(f"Error moving analyzer/piezo motor {self.pv_name} to position {position}: {e}")
        self.position = position
        time.sleep(0.3)  # Simulate movement delay

# LambdaFlexCount Class to Read Intensity using epics.caget       
class LambdaFlexCount:
    def __init__(self, detector_id, motor_config):
        self.pv_name = motor_config.lambda_flex_detectors[detector_id - 1]  # Access PV name based on detector_id
        self.peak_intensity = epics.caget(self.pv_name)  # Get initial intensity
        if self.peak_intensity is None:
            raise ValueError(f"Invalid intensity value from Detector {detector_id}")  
    
    def get_roi_intensity(self, position):
        intensity = self.peak_intensity  # Get the intensity from PV
        return intensity 
    
class MotorConfig:
    def __init__(self):
        self.analyzer_motors = [
            "11bmb:m22", "11bmb:m21", "11bmb:m20", "11bmb:m19", "11bmb:m18", "11bmb:m17",
            "11bmb:m14", "11bmb:m13", "11bmb:m12", "11bmb:m11", "11bmb:m10", "11bmb:m9"
        ]
        self.piezo_motors = [
            "11bmb:m44", "11bmb:m43", "11bmb:m42", "11bmb:m41", "11bmb:m40", "11bmb:m39",
            "11bmb:m38", "11bmb:m37", "11bmb:m36", "11bmb:m35", "11bmb:m34", "11bmb:m33"
        ]
        self.lambda_flex_detectors = [
            "11bmLambda:ROIStat1:12:Total_RBV", "11bmLambda:ROIStat1:11:Total_RBV", "11bmLambda:ROIStat1:10:Total_RBV",
            "11bmLambda:ROIStat1:9:Total_RBV", "11bmLambda:ROIStat1:8:Total_RBV", "11bmLambda:ROIStat1:7:Total_RBV",
            "11bmLambda:ROIStat1:6:Total_RBV", "11bmLambda:ROIStat1:5:Total_RBV", "11bmLambda:ROIStat1:4:Total_RBV",
            "11bmLambda:ROIStat1:3:Total_RBV", "11bmLambda:ROIStat1:2:Total_RBV", "11bmLambda:ROIStat1:1:Total_RBV"
        ]        

def initialization():
    global fig, axes
    fig = None
    axes = None
    
# Function to Create Figures if Needed
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
        axes[i].yaxis.set_major_formatter(ticker.ScalarFormatter())
        axes[i].yaxis.get_major_formatter().set_scientific(True)   
        axes[i].ticklabel_format(style='sci', axis='y', scilimits=(0, 0))        
        axes[i].grid(True)
        
    return fig, axes

def gaussian(x, amplitude, mean, sigma):
    """Gaussian function for curve fitting."""
    return amplitude * np.exp(-(x - mean)**2 / (2 * sigma**2))
    
def run_alignment(start_pos, end_pos, step_size, motor_name, detector_id, axes, fig, canvas, update_callback):
    """Runs alignment for the given motor and updates live plot."""    
    global alignment_counter 
    # Check if the number of iterations has exceeded the limit
    alignment_counter += 1
    if alignment_counter > 6:
        print("Maximum alignment iterations reached. Stopping further alignment.")
        return 
    
    # Assign the analyzer and piezo motor PV name
    motor_config = MotorConfig()
    
    # Move the 2thera arm to put detector in position for alignment
    two_theta_motor = TwoThetaDrive(detector_id)
    two_theta_motor.move_to() 
    
    # Create figures only if motor is selected
    if motor_name == "Analyzer":
        motor_pv = motor_config.analyzer_motors[detector_id - 1]
    elif motor_name == "Piezo":
        motor_pv = motor_config.piezo_motors[detector_id - 1]
    else:
        print(f"Skipping {motor_name} alignment. Not selected.")
        return  # Exit if the motor isn't selected
        
    motor = MotorDrive(motor_pv)
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
        detector = LambdaFlexCount(detector_id, motor_config)
        roi_value = detector.get_roi_intensity(pos)
        roi_counts.append(roi_value)
        update_plot(ax, line, peak_point, positions, roi_counts, legend)

        # Schedule the callback to refresh the figure
        update_callback()
        time.sleep(0.1)  # Simulated delay for the motor move and detector update
    
    # After the loop, perform Gaussian fit to the collected data
    if motor_name == "Analyzer": 
        finalrun_flag = True
        max_index = np.argmax(roi_counts)
        best_position = positions[max_index]  
    elif motor_name == "Piezo":       
        finalrun_flag = False
        max_index = np.argmax(roi_counts)
        max_position = positions[max_index]
        mid_pos = (start_pos + end_pos) / 2.0
        if abs(max_position - mid_pos) > 2.5:
            if max_position == start_pos: 
                scale = 0.005
            elif max_position < mid_pos:
                scale = 0.003
            elif max_position > mid_pos:
                scale = -0.003
            elif max_position == end_pos: 
                scale = -0.005
            analyzer_pv = motor_config.analyzer_motors[detector_id - 1]
            analyzer = MotorDrive(analyzer_pv)
            pos_adj = analyzer.get_pos() + scale * (-1)**(detector_id + 1)
            analyzer.move_to(pos_adj-0.1)
            analyzer.move_to(pos_adj)
            print(f"Fitted mean outside range. Adjusting analyzer with scale {scale}.") 
            run_alignment(start_pos, end_pos, step_size, motor_name, detector_id, axes, fig, canvas, update_callback)           
        else:
            try:
                popt, _ = curve_fit(gaussian, positions, roi_counts, p0=[np.max(roi_counts), positions[np.argmax(roi_counts)], 1])
                amplitude, mean, sigma = popt
                
                finalrun_flag = True
                best_position = mean
                print(f"Best position (from Gaussian fit): {mean:.5f}")

                # Update the plot with the fitted curve
                fit_curve = gaussian(positions, *popt)
                gaussian_line, = ax.plot(positions, fit_curve, 'g--')
                legend = ax.legend([peak_point, gaussian_line], ["Max ROI", f"Gaussian Peak @ ({mean:.5f})"], loc="lower left")
                update_plot(ax, line, peak_point, positions, roi_counts, legend)                 
                    
            except Exception as e:
                print(f"Error fitting Gaussian: {e}")
                # Fallback to using the max intensity position as the best position
                max_index = np.argmax(roi_counts)
                best_position = positions[max_index] 
                print(f"Falling back to max intensity position: {best_position:.5f}")
       
    if finalrun_flag == True:
        motor.move_to(start_pos)  
        motor.move_to(best_position)
        max_intensity = roi_counts[max_index]
        print(f"Max ROI for detector {detector_id} - {motor_name}: ({best_position:.5f}, {max_intensity:.0f})")
    update_callback()  # Final update after best position is found
    
    return
    
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
    canvas_analyzer.get_tk_widget().pack(fill="both", expand=True)

    toolbar_analyzer = NavigationToolbar2Tk(canvas_analyzer, analyzer_tab)
    toolbar_analyzer.update()
    toolbar_analyzer.pack(fill="x")  
    
    fig_piezo, axes_piezo = create_figure("Piezo")
    canvas_piezo = FigureCanvasTkAgg(fig_piezo, piezo_tab)
    canvas_piezo.get_tk_widget().pack(fill="both", expand=True)
    
    toolbar_piezo = NavigationToolbar2Tk(canvas_piezo, piezo_tab)
    toolbar_piezo.update()
    toolbar_piezo.pack(fill="x")  
    
    # Function to update the plot in Tkinter window
    def update_canvas():
        # Schedule canvas drawing in the main thread using after
        root.after(0, canvas_analyzer.draw)
        root.after(0, canvas_piezo.draw)
        
    def alignment_thread():
        """Loop over the alignment_info dictionary and update the plots."""
        global alignment_counter
        start_time = time.time()
        for detector_id, motors in alignment_info.items():
            alignment_counter = 0
            if 'analyzer' in motors:
                analyzer_info = motors['analyzer']
                run_alignment(analyzer_info['start'], analyzer_info['end'], analyzer_info['step'], 
                    "Analyzer", detector_id, axes_analyzer, fig_analyzer, canvas_analyzer, update_canvas)

            if 'piezo' in motors:
                piezo_info = motors['piezo']
                run_alignment(piezo_info['start'], piezo_info['end'], piezo_info['step'], 
                    "Piezo", detector_id, axes_piezo, fig_piezo, canvas_piezo, update_canvas)        
        end_time = time.time()
        print(f"Execution time: {end_time - start_time} seconds")
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
