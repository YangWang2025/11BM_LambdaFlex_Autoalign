import tkinter as tk
from tkinter import messagebox
import Autoalign_2theta as Autoalign

# Create the main application window
class TwoThetaAlignmentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("TwoTheta Motor Alignment")

        # Create the main frame
        self.frame = tk.Frame(self.root)
        self.frame.grid(row=0, column=0, padx=20, pady=10)

        # Column headers for Detector checkboxes, Start, End, and Step size
        self.headers = ['Detector', 'Align', 'Start', 'End', 'Step Size']
        for col, header in enumerate(self.headers):
            header_label = tk.Label(self.frame, text=header, font=("Helvetica", 10, 'bold'))
            header_label.grid(row=0, column=col, padx=10, pady=5, sticky="w")

        self.detector_vars = []
        self.detector_range_entries = {}

        for i in range(12):  # 12 detectors
            # Create checkboxes and entries for alignment parameters
            align_var = tk.BooleanVar(value=False)
            self.detector_vars.append(align_var)

            # Detector number
            detector_label = tk.Label(self.frame, text=str(i+1), font=("Helvetica", 10, 'bold'))
            detector_label.grid(row=i + 1, column=0, padx=10, pady=5, sticky="w")

            # Alignment checkbox
            align_chk = tk.Checkbutton(self.frame, variable=align_var)
            align_chk.grid(row=i + 1, column=1, padx=10, pady=5, sticky="w")

            # Start angle
            start_entry = tk.Entry(self.frame)
            start_entry.grid(row=i + 1, column=2, padx=10, pady=5)
            start_entry.insert(0, '0')

            # End angle
            end_entry = tk.Entry(self.frame)
            end_entry.grid(row=i + 1, column=3, padx=10, pady=5)
            end_entry.insert(0, '10')

            # Step size
            step_entry = tk.Entry(self.frame)
            step_entry.grid(row=i + 1, column=4, padx=10, pady=5)
            step_entry.insert(0, '0.1')

            # Store entries in dictionary for easy access
            self.detector_range_entries[i] = {
                'align': align_var,
                'start': start_entry,
                'end': end_entry,
                'step': step_entry
            }

        # Align Motors Button
        self.align_button = tk.Button(self.root, text="Align TwoTheta", command=self.align_twotheta)
        self.align_button.grid(row=13, column=0, columnspan=5, padx=20, pady=20)

    def align_twotheta(self):
        """ Align selected detectors with the specified start, end, and step size."""
        
        selected_detectors = []
        error_message = ""

        for i in range(12):
            # If align checkbox is selected
            if self.detector_range_entries[i]['align'].get():
                start = self.detector_range_entries[i]['start'].get()
                end = self.detector_range_entries[i]['end'].get()
                step = self.detector_range_entries[i]['step'].get()

                if not start or not end or not step:
                    error_message += f"Error: Missing values for Detector {i+1}.\n"
                else:
                    try:
                        start = float(start)
                        end = float(end)
                        step = float(step)

                        if start >= end:
                            error_message += f"Start position must be less than End for Detector {i+1}.\n"
                    except ValueError:
                        error_message += f"Invalid values for Detector {i+1}.\n"
                    
                    selected_detectors.append(i+1)

        if not selected_detectors:
            messagebox.showwarning("No Detector Selected", "Please select at least one detector.")
            return
        
        if error_message:
            messagebox.showerror("Error", error_message)
            return

        for detector_id in selected_detectors:
            start = float(self.detector_range_entries[detector_id-1]['start'].get())
            end = float(self.detector_range_entries[detector_id-1]['end'].get())
            step = float(self.detector_range_entries[detector_id-1]['step'].get())
            
            print(f"Running alignment for Detector {detector_id}...")
            Autoalign.run_alignment(start, end, step, detector_id)
        
        Autoalign.show_figures()

# Create the Tkinter root window
root = tk.Tk()

# Create the TwoTheta alignment app
app = TwoThetaAlignmentApp(root)

# Run the application
root.mainloop()
