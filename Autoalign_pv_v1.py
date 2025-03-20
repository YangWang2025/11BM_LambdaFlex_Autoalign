import numpy as np
import time
import random
import matplotlib.pyplot as plt
import epics

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
        
def initialization():
    global fig_analyzer, fig_piezo, axes_analyzer, axes_piezo
    fig_analyzer = None
    fig_piezo = None
    axes_analyzer = None
    axes_piezo = None
    
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
    # Assign the analyzer and piezo motor PV name  
    motor_config = MotorConfig()

    # Move the 2thera arm to put detector in position for alignment
    two_theta_motor = TwoThetaDrive(detector_id)
    two_theta_motor.move_to() 
    
    # Create figures only if motor is selected
    if motor_name == "Analyzer":
        motor_pv = motor_config.analyzer_motors[detector_id - 1]
        fig_analyzer, axes_analyzer = create_figures("Analyzer")
        #fig_analyzer.canvas.manager.window.state('zoomed')
        ax = axes_analyzer[detector_id - 1]
        color = 'k'
    elif motor_name == "Piezo":
        motor_pv = motor_config.piezo_motors[detector_id - 1]
        fig_piezo, axes_piezo = create_figures("Piezo")
        #fig_piezo.canvas.manager.window.state('zoomed')
        ax = axes_piezo[detector_id - 1]
        color = 'b'
    else:
        print(f"Skipping {motor_name} alignment. Not selected.")
        return  # Exit if the motor isn't selected
    
    motor = MotorDrive(motor_pv)  # Example motor PV for Analyzer and Piezo
   # step_size = 0.1
    positions = np.arange(start_pos, end_pos + step_size, step_size)
    roi_counts = []   
    
    line, = ax.plot([], [], color + '-')
    peak_point, = ax.plot([], [], 'ro', markersize=8, label="Max ROI")
    legend = ax.legend(loc="lower left")

    # Perform the scan
    for pos in positions:
        motor.move_to(pos)
        detector = LambdaFlexCount(detector_id, motor_config)
        roi_value = detector.get_roi_intensity(pos)
        roi_counts.append(roi_value)
        update_plot(ax, line, peak_point, positions, roi_counts, legend)
        plt.pause(0.1)  # Ensure the figure updates independently

    # Find and move to the best position
    max_index = np.argmax(roi_counts)
    best_position = positions[max_index]
    motor.move_to(start_pos)
    motor.move_to(best_position)
    update_plot(ax, line, peak_point, positions, roi_counts, legend)
    plt.pause(0.1)  # Final refresh after best position is found
    
    # Print the peak position and its intensity after scan is complete
    max_intensity = roi_counts[max_index]
    print(f"   → Detector {detector_id}: max intensity {max_intensity:.0f} at {best_position:.5f} deg.")
    
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
