import tkinter as tk
from tkinter import messagebox, filedialog
import csv
import os
from datetime import datetime, timedelta

# --- CONFIGURATION ---
CSV_FILE = 'todo_tasks.csv'
TXT_FILE_DEFAULT = 'weekly_todo_list.txt'
BG_COLOR = '#000000'  # Black
FG_COLOR = '#00FF00'  # Bright Green (Classic terminal green)
FONT_STYLE = ("Courier", 10) # Monospaced font for terminal look

class TodoApp:
    def __init__(self, master):
        self.master = master
        master.title("Weekly Todo Planner")
        master.geometry("850x650")
        
        # Apply global terminal styling
        master.configure(bg=BG_COLOR)

        # 1. Initialize Data
        self.tasks = self.load_tasks()
        
        # 2. Setup the UI Components
        self.setup_ui()
        
        # 3. Display the Week
        self.display_week()

    def setup_ui(self):
        """Sets up the layout: Input Area and Display Area."""
        
        # --- Input Frame (Adding new tasks) ---
        input_frame = tk.Frame(self.master, bg=BG_COLOR)
        input_frame.pack(pady=10, padx=10, fill='x')

        tk.Label(input_frame, text="Add New Task:", bg=BG_COLOR, fg=FG_COLOR, font=FONT_STYLE).pack(side=tk.LEFT, padx=5)

        self.task_entry = tk.Entry(input_frame, width=50, bg='#111111', fg=FG_COLOR, insertbackground=FG_COLOR, font=FONT_STYLE)
        self.task_entry.pack(side=tk.LEFT, padx=10, expand=True)

        add_button = tk.Button(input_frame, text="Add Task", command=self.add_task, bg='#003300', fg=FG_COLOR, activebackground='#005500', activeforeground=FG_COLOR, font=FONT_STYLE)
        add_button.pack(side=tk.LEFT, padx=10)
        
        # --- Export Button ---
        export_button = tk.Button(input_frame, text="Export Weekly Task List", command=self.export_tasks_to_txt, 
                                   bg='#003300', fg=FG_COLOR, activebackground='#005500', activeforeground=FG_COLOR, font=FONT_STYLE)
        export_button.pack(side=tk.LEFT, padx=20)

        # --- Display Frame (Weekly View) ---
        self.display_frame = tk.Frame(self.master, bg=BG_COLOR)
        self.display_frame.pack(pady=10, padx=10, fill='both', expand=True)

    def load_tasks(self):
        """Loads tasks from the CSV file."""
        tasks = {}
        if not os.path.exists(CSV_FILE):
            return tasks
        
        try:
            with open(CSV_FILE, mode='r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    date_str = row['Date']
                    if date_str not in tasks:
                        tasks[date_str] = []
                    
                    tasks[date_str].append({
                        'task': row['Task'],
                        'done': row['Completed'] == 'True'
                    })
        except Exception as e:
            messagebox.showerror("Error", f"Could not load tasks: {e}")
        return tasks

    def save_tasks(self):
        """Saves all current tasks (including status) back to the CSV file."""
        data = []
        for date, tasks_list in self.tasks.items():
            for task_data in tasks_list:
                data.append({
                    'Date': date,
                    'Task': task_data['task'],
                    'Completed': 'True' if task_data['done'] else 'False'
                })
        
        fieldnames = ['Date', 'Task', 'Completed']
        try:
            with open(CSV_FILE, mode='w', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            return True
        except Exception as e:
            messagebox.showerror("Save Error", f"Could not save tasks to CSV: {e}")
            return False

    def add_task(self):
        """Adds a new task for the current date."""
        task_text = self.task_entry.get().strip()
        if not task_text:
            messagebox.showerror("Error", "Please enter a task description.")
            return

        today_date = datetime.now().strftime('%Y-%m-%d')
        
        if today_date not in self.tasks:
            self.tasks[today_date] = []

        # Add the new task structure
        self.tasks[today_date].append({
            'task': task_text,
            'done': False
        })

        self.task_entry.delete(0, tk.END)
        self.display_week() # Refresh the display
        self.save_tasks() # Save immediately

    def toggle_task_done(self, date, task_index, checked_state):
        """Updates the completion status of a task and saves."""
        if date in self.tasks and 0 <= task_index < len(self.tasks[date]):
            task_data = self.tasks[date][task_index]
            task_data['done'] = checked_state
            self.save_tasks()

    def export_tasks_to_txt(self):
        """
        Generates the weekly task list content and prompts the user to save it as a TXT file.
        """
        # 1. Get the weekly date range (same logic as display_week)
        today = datetime.now()
        start_date = today - timedelta(days=today.weekday() + 1) 
        days_of_week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        
        export_content = ["=" * 60]
        export_content.append("        WEEKLY TODO LIST EXPORT")
        export_content.append("=" * 60 + "\n")

        # 2. Iterate through the week and build the string
        for i, day_name in enumerate(days_of_week):
            current_date = start_date + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            display_date = current_date.strftime("%A, %B %d, %Y")
            
            export_content.append(f"\n--- {display_date} ({day_name}) ---")
            
            tasks_for_day = self.tasks.get(date_str, [])
            
            if not tasks_for_day:
                export_content.append("  [No tasks scheduled for this day.]")
            else:
                for task_data in tasks_for_day:
                    status = "[DONE]" if task_data['done'] else "[PENDING]"
                    # Formatting: Status | Task Description
                    formatted_task = f"  {status:<10} {task_data['task']}"
                    export_content.append(formatted_task)

        # 3. Prompt for file saving
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt", 
            initialfile=TXT_FILE_DEFAULT,
            title="Save Weekly Task List"
        )

        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write('\n'.join(export_content))
                messagebox.showinfo("Export Success", f"Successfully exported task list to:\n{file_path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to write file: {e}")


    def display_week(self):
        """
        Clears the display and populates the widget with the weekly view (Sun-Sat).
        """
        # Clear previous widgets
        for widget in self.display_frame.winfo_children():
            widget.destroy()

        # Determine the start date (Sunday) for the current week
        today = datetime.now()
        start_date = today - timedelta(days=today.weekday() + 1)
        
        days_of_week = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
        
        # Create the weekly grid layout
        for i, day_name in enumerate(days_of_week):
            current_date = start_date + timedelta(days=i)
            date_str = current_date.strftime('%Y-%m-%d')
            
            # Day Column Frame
            day_frame = tk.Frame(self.display_frame, bg=BG_COLOR, padx=10, pady=5, bd=1, relief=tk.SOLID)
            day_frame.pack(side=tk.LEFT, padx=5, expand=True, fill='y')

            # Title (e.g., Sunday, Oct 22)
            tk.Label(day_frame, text=f"{day_name}\n{current_date.strftime('%b %d')}", 
                     bg=BG_COLOR, fg=FG_COLOR, font=("Courier", 12, "bold")).pack(pady=5)
            
            # Task List Container
            task_container = tk.Frame(day_frame, bg=BG_COLOR, padx=5, pady=5)
            task_container.pack(fill='both', expand=True)
            
            # Populate tasks for this specific date
            tasks_for_day = self.tasks.get(date_str, [])
            
            if not tasks_for_day:
                tk.Label(task_container, text="No tasks scheduled.", bg=BG_COLOR, fg="#006600").pack(pady=10)
            else:
                for index, task_data in enumerate(tasks_for_day):
                    self.create_task_widget(task_container, date_str, index, task_data)

    def create_task_widget(self, parent_frame, date_str, index, task_data):
        """Creates a single task row with a checkbox and label."""
        
        var = tk.BooleanVar(value=task_data['done'])
        task_frame = tk.Frame(parent_frame, bg=BG_COLOR)
        task_frame.pack(fill='x', pady=2)

        checkbox = tk.Checkbutton(task_frame, 
                                   variable=var, 
                                 command=lambda d=date_str, i=index, v=var: self.toggle_task_done(d, i, v.get()), 
                                   bg=BG_COLOR, fg=FG_COLOR, selectcolor='#000000', 
                                   indicatoron=2, 
                                   font=FONT_STYLE)
        checkbox.pack(side=tk.LEFT, padx=5)

        task_label = tk.Label(task_frame, 
                              text=task_data['task'], 
                              bg=BG_COLOR, 
                              fg=FG_COLOR, 
                              font=FONT_STYLE,
                              wraplength=350)
        task_label.pack(side=tk.LEFT, expand=True)
        
        if task_data['done']:
            task_label.config(fg='#006600', overstrike=True)


if __name__ == "__main__":
    root = tk.Tk()
    app = TodoApp(root)
    
    root.mainloop()