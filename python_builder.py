import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import filedialog, messagebox, scrolledtext
import subprocess
import threading

PYTHON_EXE = r"C:\Program Files\Python\python.exe"
HARDCODED_DIST = r"C:\00\00_PyA\exe"  # hard-coded output folder

class PyInstallerGUI(tb.Window):
    def __init__(self):
        super().__init__(themename="flatly")
        self.title("Python → EXE Builder")
        self.geometry("760x500")
        self.resizable(False, False)

        self.py_file = tb.StringVar()
        self.icon_file = tb.StringVar()
        self.dist_path = tb.StringVar(value=HARDCODED_DIST)

        self.create_ui()

    def create_ui(self):
        frame = tb.Frame(self, padding=20)
        frame.pack(fill=BOTH, expand=True)

        tb.Label(
            frame,
            text="Python → EXE Builder",
            font=("Segoe UI", 20, "bold")
        ).pack(anchor=W, pady=(0, 20))

        self.create_row(frame, "Python file", self.py_file, self.browse_py)
        self.create_row(frame, "Icon (.ico)", self.icon_file, self.browse_icon)

        tb.Separator(frame).pack(fill=X, pady=15)

        tb.Button(
            frame,
            text="Build EXE",
            bootstyle=SUCCESS,
            width=28,
            command=self.start_build
        ).pack(pady=10)

        # Text area for live output
        self.output_text = scrolledtext.ScrolledText(frame, height=15, state='disabled')
        self.output_text.pack(fill=BOTH, expand=True, pady=10)

    def create_row(self, parent, label, variable, command):
        row = tb.Frame(parent)
        row.pack(fill=X, pady=6)

        tb.Label(row, text=label, width=16).pack(side=LEFT)
        tb.Entry(row, textvariable=variable).pack(side=LEFT, fill=X, expand=True, padx=8)
        tb.Button(row, text="Browse", command=command).pack(side=LEFT)

    def browse_py(self):
        file = filedialog.askopenfilename(filetypes=[("Python files", "*.py")])
        if file:
            self.py_file.set(file)

    def browse_icon(self):
        file = filedialog.askopenfilename(filetypes=[("Icon files", "*.ico")])
        if file:
            self.icon_file.set(file)

    def start_build(self):
        if not self.py_file.get():
            messagebox.showerror("Error", "Please select a Python file")
            return
        # Run build in a separate thread to keep GUI responsive
        threading.Thread(target=self.build_exe, daemon=True).start()

    def build_exe(self):
        self.output_text.config(state='normal')
        self.output_text.delete("1.0", "end")

        cmd = [
            PYTHON_EXE,
            "-m", "PyInstaller",
            "--onefile",
            "--noconsole",
            f"--distpath={HARDCODED_DIST}"
        ]

        if self.icon_file.get():
            cmd.append(f"--icon={self.icon_file.get()}")

        cmd.append(self.py_file.get())

        self.append_output(f"Running command:\n{' '.join(cmd)}\n\n")

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True
            )

            # Read output line by line
            for line in process.stdout:
                self.append_output(line)

            process.wait()
            if process.returncode == 0:
                self.append_output("\nBuild completed successfully!\n")
                messagebox.showinfo("Success", f"EXE build completed successfully!\nOutput folder:\n{HARDCODED_DIST}")
            else:
                self.append_output(f"\nBuild failed with exit code {process.returncode}\n")
                messagebox.showerror("Build Failed", f"Check output window for details.\nExit code: {process.returncode}")

        except Exception as e:
            self.append_output(f"\nError: {e}\n")
            messagebox.showerror("Error", str(e))
        finally:
            self.output_text.config(state='disabled')

    def append_output(self, text):
        self.output_text.insert('end', text)
        self.output_text.see('end')
        self.output_text.update()

if __name__ == "__main__":
    app = PyInstallerGUI()
    app.mainloop()
