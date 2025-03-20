import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
# import Autoalign_sim_v3 as Autoalign
import Autoalign_pv_v3 as Autoalign

# Create the main application window
class MotorAlignmentApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Motor Alignment")
        
        # Create the main frame
        self.frame = tk.Frame(self.root)
        self.frame.grid(row=0, column=0, padx=10, pady=10)

        # Column headers for Analyzer checkbox, Start/End/Step for Analyzer, Piezo checkbox, Start/End/Step for Piezo
        self.headers = ['Detector', 'Analyzer', 'Start', 'End', 'Step', 'Piezo', 'Start', 'End', 'Step']
        for col, header in enumerate(self.headers):
            header_label = tk.Label(self.frame, text=header, font=("Helvetica", 10, 'bold'))
            header_label.grid(row=0, column=col, padx=10, pady=5, sticky="w")

        # Create variables for global checkboxes
        self.global_analyzer_var = tk.BooleanVar(value=False)
        self.global_piezo_var = tk.BooleanVar(value=False)

        # Create global checkboxes for Analyzer and Piezo with bold font
        self.global_analyzer_chk = tk.Checkbutton(self.frame, text="Analyzer", variable=self.global_analyzer_var, command=self.toggle_analyzer_checkboxes, font=("Helvetica", 10, 'bold'))
        self.global_analyzer_chk.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        self.global_piezo_chk = tk.Checkbutton(self.frame, text="Piezo", variable=self.global_piezo_var, command=self.toggle_piezo_checkboxes, font=("Helvetica", 10, 'bold'))
        self.global_piezo_chk.grid(row=0, column=5, padx=10, pady=5, sticky="w")

        self.detector_vars = []
        self.detector_range_entries = {}
        self.analyzer_vars = []  
        self.piezo_vars = []  

        for i in range(12):  
            # Create checkboxes for Analyzer and Piezo Motor alignment
            analyzer_var = tk.BooleanVar(value=False)
            piezo_var = tk.BooleanVar(value=False)
            self.analyzer_vars.append(analyzer_var)
            self.piezo_vars.append(piezo_var)

            # Detector number
            detector_label = tk.Label(self.frame, text=str(i+1), font=("Helvetica", 10, 'bold'))
            detector_label.grid(row=i + 1, column=0, padx=5, pady=5)

            # Analyzer checkbox
            analyzer_chk = tk.Checkbutton(self.frame, variable=analyzer_var, command=lambda i=i: self.update_range_color(i, "Analyzer"))
            analyzer_chk.grid(row=i + 1, column=1, padx=5, pady=5)
            
            
            # Analyzer Start
            analyzer_start_entry = tk.Entry(self.frame,width=25)
            analyzer_start_entry.grid(row=i + 1, column=2, padx=5, pady=5)
            
            # Analyzer End
            analyzer_end_entry = tk.Entry(self.frame,width=25)
            analyzer_end_entry.grid(row=i + 1, column=3, padx=5, pady=5)
            
            # Analyzer Step
            analyzer_step_entry = tk.Entry(self.frame,width=25)
            analyzer_step_entry.grid(row=i + 1, column=4, padx=5, pady=5)
            analyzer_step_entry.insert(0, '0.00125')

            # Piezo checkbox
            piezo_chk = tk.Checkbutton(self.frame, variable=piezo_var, command=lambda i=i: self.update_range_color(i, "Piezo"))
            piezo_chk.grid(row=i + 1, column=5, padx=10, pady=5)

            # Piezo Start
            piezo_start_entry = tk.Entry(self.frame,width=25)
            piezo_start_entry.grid(row=i + 1, column=6, padx=5, pady=5)

            # Piezo End
            piezo_end_entry = tk.Entry(self.frame,width=25)
            piezo_end_entry.grid(row=i + 1, column=7, padx=5, pady=5)
            
            # Piezo Step
            piezo_step_entry = tk.Entry(self.frame,width=25)
            piezo_step_entry.grid(row=i + 1, column=8, padx=5, pady=5)
            piezo_step_entry.insert(0, '0.1')

            # Store entries in dictionary for easy access
            self.detector_range_entries[i] = {
                'analyzer_start': analyzer_start_entry,
                'analyzer_end': analyzer_end_entry,
                'analyzer_step': analyzer_step_entry,
                'piezo_start': piezo_start_entry,
                'piezo_end': piezo_end_entry,
                'piezo_step': piezo_step_entry
            }

        # Add a block and copy button for Analyzer Start
        self.analyzer_start_block = tk.Entry(self.frame, width=10)  
        self.analyzer_start_block.grid(row=0, column=2, padx=5, pady=5)
        self.analyzer_start_block.insert(0, '4.2')  

        self.refresh_button = tk.Button(self.frame, text="↻", command=self.copy_analyzer_start, font=("Helvetica", 12, 'bold'))
        self.refresh_button.grid(row=0, column=2, padx=5, pady=5, sticky="e") 

        # Add a block and copy button for Analyzer End
        self.analyzer_end_block = tk.Entry(self.frame, width=10)
        self.analyzer_end_block.grid(row=0, column=3, padx=5, pady=5)
        self.analyzer_end_block.insert(0, '4.3')

        self.refresh_button_end = tk.Button(self.frame, text="↻", command=self.copy_analyzer_end, font=("Helvetica", 12, 'bold'))
        self.refresh_button_end.grid(row=0, column=3, padx=5, pady=5, sticky="e")

        # Add a block and copy button for Analyzer Step
        self.analyzer_step_block = tk.Entry(self.frame, width=10)
        self.analyzer_step_block.grid(row=0, column=4, padx=5, pady=5)
        self.analyzer_step_block.insert(0, '0.00125')

        self.refresh_button_step = tk.Button(self.frame, text="↻", command=self.copy_analyzer_step, font=("Helvetica", 12, 'bold'))
        self.refresh_button_step.grid(row=0, column=4, padx=5, pady=5, sticky="e")

        # Add a block and copy button for Piezo Start
        self.piezo_start_block = tk.Entry(self.frame, width=10)
        self.piezo_start_block.grid(row=0, column=6, padx=5, pady=5)
        self.piezo_start_block.insert(0, '2')

        self.refresh_button_piezo_start = tk.Button(self.frame, text="↻", command=self.copy_piezo_start, font=("Helvetica", 12, 'bold'))
        self.refresh_button_piezo_start.grid(row=0, column=6, padx=5, pady=5, sticky="e")

        # Add a block and copy button for Piezo End
        self.piezo_end_block = tk.Entry(self.frame, width=10)
        self.piezo_end_block.grid(row=0, column=7, padx=5, pady=5)
        self.piezo_end_block.insert(0, '12')

        self.refresh_button_piezo_end = tk.Button(self.frame, text="↻", command=self.copy_piezo_end, font=("Helvetica", 12, 'bold'))
        self.refresh_button_piezo_end.grid(row=0, column=7, padx=5, pady=5, sticky="e")

        # Add a block and copy button for Piezo Step
        self.piezo_step_block = tk.Entry(self.frame, width=10)
        self.piezo_step_block.grid(row=0, column=8, padx=5, pady=5)
        self.piezo_step_block.insert(0, '0.1')

        self.refresh_button_piezo_step = tk.Button(self.frame, text="↻", command=self.copy_piezo_step, font=("Helvetica", 12, 'bold'))
        self.refresh_button_piezo_step.grid(row=0, column=8, padx=5, pady=5, sticky="e")

        # Align Motors Button
        self.align_button = tk.Button(self.root, text="Align Motors", command=self.align_motors)
        self.align_button.grid(row=1, column=0, columnspan=9, padx=20, pady=20)

        # Success Label
        self.success_label = tk.Label(self.root, text="", fg="green", font=("Helvetica", 12))
        self.success_label.grid(row=2, column=0, columnspan=9, padx=20, pady=10, sticky="e")

    def toggle_analyzer_checkboxes(self):
        """ Toggles all individual Analyzer checkboxes based on the global Analyzer checkbox """
        state = self.global_analyzer_var.get()
        for var in self.analyzer_vars:
            var.set(state)

        # Update the range color when toggling Analyzer checkboxes
        for i in range(12):
            self.update_range_color(i, "Analyzer")

    def toggle_piezo_checkboxes(self):
        """ Toggles all individual Piezo checkboxes based on the global Piezo checkbox """
        state = self.global_piezo_var.get()
        for var in self.piezo_vars:
            var.set(state)

        # Update the range color when toggling Piezo checkboxes
        for i in range(12):
            self.update_range_color(i, "Piezo")

    def update_range_color(self, detector_id, motor_type):
        """ Update the background color of the range entry boxes when a checkbox is checked or unchecked """
        if motor_type == "Analyzer":
            if self.analyzer_vars[detector_id].get():
                # Set range entry fields to green when Analyzer is checked
                self.detector_range_entries[detector_id]['analyzer_start'].config(bg="lightgreen")
                self.detector_range_entries[detector_id]['analyzer_end'].config(bg="lightgreen")
                self.detector_range_entries[detector_id]['analyzer_step'].config(bg="lightgreen")
            else:
                # Reset to default color when Analyzer is unchecked
                self.detector_range_entries[detector_id]['analyzer_start'].config(bg="white")
                self.detector_range_entries[detector_id]['analyzer_end'].config(bg="white")
                self.detector_range_entries[detector_id]['analyzer_step'].config(bg="white")

        elif motor_type == "Piezo":
            if self.piezo_vars[detector_id].get():
                # Set range entry fields to green when Piezo is checked
                self.detector_range_entries[detector_id]['piezo_start'].config(bg="lightgreen")
                self.detector_range_entries[detector_id]['piezo_end'].config(bg="lightgreen")
                self.detector_range_entries[detector_id]['piezo_step'].config(bg="lightgreen")
            else:
                # Reset to default color when Piezo is unchecked
                self.detector_range_entries[detector_id]['piezo_start'].config(bg="white")
                self.detector_range_entries[detector_id]['piezo_end'].config(bg="white")
                self.detector_range_entries[detector_id]['piezo_step'].config(bg="white")

    def copy_analyzer_start(self):
        """ Copy the value from the Analyzer Start block to all Analyzer Start positions """
        analyzer_start_value = self.analyzer_start_block.get()

        # Set the value in all analyzer start fields
        for i in range(12):
            self.detector_range_entries[i]['analyzer_start'].delete(0, tk.END)
            self.detector_range_entries[i]['analyzer_start'].insert(0, analyzer_start_value)

    def copy_analyzer_end(self):
        """ Copy the value from the Analyzer End block to all Analyzer End positions """
        analyzer_end_value = self.analyzer_end_block.get()

        # Set the value in all analyzer end fields
        for i in range(12):
            self.detector_range_entries[i]['analyzer_end'].delete(0, tk.END)
            self.detector_range_entries[i]['analyzer_end'].insert(0, analyzer_end_value)

    def copy_analyzer_step(self):
        """ Copy the value from the Analyzer Step block to all Analyzer Step positions """
        analyzer_step_value = self.analyzer_step_block.get()

        # Set the value in all analyzer step fields
        for i in range(12):
            self.detector_range_entries[i]['analyzer_step'].delete(0, tk.END)
            self.detector_range_entries[i]['analyzer_step'].insert(0, analyzer_step_value)

    def copy_piezo_start(self):
        """ Copy the value from the Piezo Start block to all Piezo Start positions """
        piezo_start_value = self.piezo_start_block.get()

        # Set the value in all piezo start fields
        for i in range(12):
            self.detector_range_entries[i]['piezo_start'].delete(0, tk.END)
            self.detector_range_entries[i]['piezo_start'].insert(0, piezo_start_value)

    def copy_piezo_end(self):
        """ Copy the value from the Piezo End block to all Piezo End positions """
        piezo_end_value = self.piezo_end_block.get()

        # Set the value in all piezo end fields
        for i in range(12):
            self.detector_range_entries[i]['piezo_end'].delete(0, tk.END)
            self.detector_range_entries[i]['piezo_end'].insert(0, piezo_end_value)

    def copy_piezo_step(self):
        """ Copy the value from the Piezo Step block to all Piezo Step positions """
        piezo_step_value = self.piezo_step_block.get()

        # Set the value in all piezo step fields
        for i in range(12):
            self.detector_range_entries[i]['piezo_step'].delete(0, tk.END)
            self.detector_range_entries[i]['piezo_step'].insert(0, piezo_step_value)


    def align_motors(self):
        """ Runs alignment for each selected detector in sequence. """
        
        # Get selected detectors in order
        selected_detectors = []
        alignment_info = {}
        error_message = ""  

        for i in range(12):
            detector_info = {}
            # Check if either Analyzer or Piezo checkbox is checked
            if self.analyzer_vars[i].get() or self.piezo_vars[i].get():
                # Check if Start, End, and Step values are provided for Analyzer
                if self.analyzer_vars[i].get():
                    analyzer_start = self.detector_range_entries[i]['analyzer_start'].get()
                    analyzer_end = self.detector_range_entries[i]['analyzer_end'].get()
                    analyzer_step = self.detector_range_entries[i]['analyzer_step'].get()
                    if not analyzer_start or not analyzer_end or not analyzer_step:
                        error_message += f"Error: Analyzer Start, End, and Step values missing for Detector {i+1}.\n"
                    else:
                        try:
                            analyzer_start = float(analyzer_start)
                            analyzer_end = float(analyzer_end)
                            analyzer_step = float(analyzer_step)
                            if analyzer_start >= analyzer_end:
                                error_message += f"Analyzer start position must be less than the end position for Detector {i+1}.\n"
                            if analyzer_step <= 0:
                                error_message += f"Analyzer step size must be positive for Detector {i+1}.\n"
                            else:
                                detector_info['analyzer'] = {
                                    'start': analyzer_start,
                                    'end': analyzer_end,
                                    'step': analyzer_step
                                }                            
                        except ValueError:
                            error_message += f"Invalid value for Analyzer Start/End/Step for Detector {i+1}.\n"
                # Check if Start, End, and Step values are provided for Piezo
                if self.piezo_vars[i].get():
                    piezo_start = self.detector_range_entries[i]['piezo_start'].get()
                    piezo_end = self.detector_range_entries[i]['piezo_end'].get()
                    piezo_step = self.detector_range_entries[i]['piezo_step'].get()
                    if not piezo_start or not piezo_end or not piezo_step:
                        error_message += f"Error: Piezo Start, End, and Step values missing for Detector {i+1}.\n"
                    else:
                        try:
                            piezo_start = float(piezo_start)
                            piezo_end = float(piezo_end)
                            piezo_step = float(piezo_step)
                            if piezo_start >= piezo_end:
                                error_message += f"Piezo start position must be less than the end position for Detector {i+1}.\n"                                                         
                            if not (0 <= piezo_start <= 15) or not (0 <= piezo_end <= 15):
                                error_message += f"Error: Piezo range for Detector {i+1} is out of bounds (0-15).\n"
                            if piezo_step <= 0:
                                error_message += f"Piezo step size must be positive for Detector {i+1}.\n"
                            else:
                                detector_info['piezo'] = {
                                    'start': piezo_start,
                                    'end': piezo_end,
                                    'step': piezo_step
                                }
                        except ValueError:
                            error_message += f"Error: Invalid Piezo range or Step for Detector {i+1}.\n"

            if detector_info:
                alignment_info[i + 1] = detector_info
                selected_detectors.append(i + 1)                

        if not selected_detectors:
            messagebox.showwarning("No Detector Selected", "Please select at least one detector (Analyzer or Piezo).")
            return
        
        # If there are error messages, show them and stop
        if error_message:
            messagebox.showerror("Missing or Invalid Values", error_message)
            return
        
        print(f"🔲 Running alignment for detectors: {selected_detectors}")
        self.success_label.config(text=f"Running alignment for detectors: {selected_detectors}")

        # Get the alignment requests and ranges
        Autoalign.initialization()
        Autoalign.show_figures_in_tabs(alignment_info)
        
        print("✅ All selected detectors processed.\n")        
        self.success_label.config(text=f"All selected detectors processed.")
        
        # Call the update function after the alignment is done
        self.update_gui()

    def update_gui(self):
        """ Updates the GUI after alignment to allow for a new run. """
        # Enable checkboxes and clear range entries for the next run
        for i in range(12):
            # Deselect all checkboxes (Analyzer and Piezo)
            self.analyzer_vars[i].set(False)
            self.piezo_vars[i].set(False)
            
            # Reset range entry colors to the default (white)
            self.detector_range_entries[i]['analyzer_start'].config(bg="white")
            self.detector_range_entries[i]['analyzer_end'].config(bg="white")
            self.detector_range_entries[i]['analyzer_step'].config(bg="white")
            self.detector_range_entries[i]['piezo_start'].config(bg="white")
            self.detector_range_entries[i]['piezo_end'].config(bg="white")
            self.detector_range_entries[i]['piezo_step'].config(bg="white")       

# Create the Tkinter root window
root = tk.Tk()

# Create the motor alignment app
app = MotorAlignmentApp(root)

# Run the application
root.mainloop()
