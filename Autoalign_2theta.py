import numpy as np
import time
import matplotlib.pyplot as plt
import epics


# TwoThetaDrive Class to Move the Arm to a Specified Angle
class TwoThetaDrive:
    def __init__(self, detector_id):
        self.pv_name = "11bmb:m28"  # TwoTheta motor PV name
        self.detector_id = detector_id
        self.angle = self.calculate_angle(self.detector_id)  # Initial angle based on detector ID
    
    def calculate_angle(self, detector_id):
        """Calculate the 2Theta angle based on detector ID (1 to 12)."""
        if 1 <= detector_id <= 12:
            return -2 * (detector_id - 1)  # Angle will be 0, -2, -4, ..., -22
        else:
            raise ValueError("Detector ID must be between 1 and 12")
    
    def move_to(self, angle):
        """Move the TwoTheta motor to the specified angle."""

        try:
            epics.caput(self.pv_name, angle, wait=True, timeout=600)  # Move motor to the calculated angle
        except Exception as e:
            print(f"Error moving 2theta motor {self.pv_name} to position {self.angle}: {e}")    
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

# MotorConfig Class with the PV names of the detectors and motors
class MotorConfig:
    def __init__(self):
        self.lambda_flex_detectors = [
            "11bmLambda:ROIStat1:12:Total_RBV", "11bmLambda:ROIStat1:11:Total_RBV", "11bmLambda:ROIStat1:10:Total_RBV",
            "11bmLambda:ROIStat1:9:Total_RBV", "11bmLambda:ROIStat1:8:Total_RBV", "11bmLambda:ROIStat1:7:Total_RBV",
            "11bmLambda:ROIStat1:6:Total_RBV", "11bmLambda:ROIStat1:5:Total_RBV", "11bmLambda:ROIStat1:4:Total_RBV",
            "11bmLambda:ROIStat1:3:Total_RBV", "11bmLambda:ROIStat1:2:Total_RBV", "11bmLambda:ROIStat1:1:Total_RBV"
        ]  

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
    legend.get_texts()[0].set_text(f"Max ROI: ({max_pos:.3f}, {max_val:.0f})")

    plt.draw()
    plt.pause(0.1)

# Function to Run Alignment and Update Live Plot
def run_alignment(start_angle, end_angle, step_size, detector_id):
    """Runs alignment for the given TwoTheta motor and updates live plot based on ROI intensity."""  
    motor_config = MotorConfig()
    
    # Create figure for live plotting
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_title(f"TwoTheta Alignment for Detector {detector_id}")
    ax.set_xlabel("TwoTheta Angle (degrees)")
    ax.set_ylabel("Intensity")
    
    two_theta_motor = TwoThetaDrive(detector_id)    

    angles = np.arange(start_angle, end_angle + step_size, step_size)
    roi_counts = []
      
    line, = ax.plot([], [], 'k-')
    peak_point, = ax.plot([], [], 'ro', markersize=8, label="Max ROI")
    legend = ax.legend(loc="lower left")

    # Perform the alignment scan by moving the TwoTheta motor
    for angle in angles:
        two_theta_motor.move_to(angle)  # Move the TwoTheta motor to the new angle
        detector = LambdaFlexCount(detector_id, motor_config)
        roi_value = detector.get_roi_intensity(angle)  # Get intensity at this angle
        roi_counts.append(roi_value)
        update_plot(ax, line, peak_point, angles, roi_counts, legend)
        plt.pause(0.1)  # Ensure the figure updates independently

    # Find and move to the best angle (max ROI)
    max_index = np.argmax(roi_counts)
    best_angle = angles[max_index]
    two_theta_motor.move_to(best_angle)  # Move the motor to the best angle
    update_plot(ax, line, peak_point, angles, roi_counts, legend)
    plt.pause(0.1)  # Final refresh after best position is found
    
    # Print the peak position and its intensity after scan is complete
    max_intensity = roi_counts[max_index]
    print(f"   → Detector {detector_id}: max intensity {max_intensity:.0f} at {best_angle:.4f} deg.")
    
# Function to Show the Plot After Alignment
def show_figures():
    """Display the final alignment figure after the scan is complete."""
    plt.show()

