import tkinter as tk
from tkinter import simpledialog, messagebox
from datetime import datetime
import os

# Folder where journal entries will be saved
SAVE_DIR = r"C:\Users\jacobc\Documents\Notes\Journal"

os.makedirs(SAVE_DIR, exist_ok=True)


class JournalTerminal:

    def __init__(self, root):

        self.root = root
        self.root.title("Journal Terminal")
        self.shell_mode = False
        self.custom_datetime = None

        self.text = tk.Text(
            root,
            bg="black",
            fg="white",
            insertbackground="white",   # cursor color
            font=("Consolas", 12),
            wrap="word",
            undo=True
        )

        self.text.pack(expand=True, fill="both") # expand to fill entire window

        # block cursor
        self.text.config(insertwidth=8)

        # initial prompt
        self.insert_prompt() # insert >>

        # enforce prompt behavior
        self.text.bind("<Return>", self.new_line) # press enter - call new_line()
        self.text.bind("<KeyPress>", self.on_key) # key press - call on_key()

        # Ctrl+C ends session
        root.bind("<Control-c>", self.exit_and_save) # ctrl-c - calls exit_and_save()

        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        options = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="Options", menu=options)
        options.add_command(label="Enter Shell Mode", command=self.enable_shell)
        options.add_command(label="Exit Shell Mode", command=self.disable_shell)
        options.add_command(label="Change Entry Date", command=self.change_date)

    def enable_shell(self):
        self.shell_mode = True

    def disable_shell(self):
        self.shell_mode = False

    def get_current_line(self):
        cursor = self.text.index("insert")
        line_num = cursor.split(".")[0] # move cursor to start of line
        line_start = line_num + ".0"
        line_end = cursor.split(".")[0] + ".end" # 3.end - end of line

        line = self.text.get(line_start, line_end)

        if line.startswith(">> "):
            line = line[3:]

        return line.strip()

    def handle_command(self, line):
        print("COMMAND:", line)

        if line.startswith("tc"): # needs work
            if "-blue" in line:
                self.text.config(fg="blue")
            elif "-green" in line:
                self.text.config(fg="green")
            else:
                self.text.insert("end", "\nUnkown color\n")

        elif line.startswith("cfp"):
            path = line[4:].strip()
            if os.path.exists(path):
                global SAVE_DIR
                SAVE_DIR = path

        elif line == "shell exit":
            self.shell_mode = False

    def insert_prompt(self):
        self.text.insert("end", ">> ") # 'end' = the position just after the last char in the widget -- >> Hello - 'end' is right after o
        self.text.mark_set("insert", "end") # writes >> at end and moves cursor to end so >> |.. 

    def new_line(self, event):
        
        line = self.get_current_line()

        if self.shell_mode:
            self.handle_command(line)
        else:
            if line.strip() == "shell begin":
                self.shell_mode = True

        self.text.insert("end", "\n") # manually insert new line
        self.insert_prompt() # add new >> prompt
        return "break" # return break - overwrite default 'Enter' behavior

    def on_key(self, event):
        # prevent deleting the prompt
        cursor = self.text.index("insert") # get cursor position - line 3 column 5 -- "3.5"
        line_start = cursor.split(".")[0] + ".0" # convert '3.5' to 3.0' e.g.
        if event.keysym == "BackSpace": # prevent deletion of the '>>' 
            if self.text.get(line_start, line_start + "+3c") == ">> ": # get first 3 characters of line 
                if self.text.compare("insert", "<=", line_start + "+3c"): # if character is less than the '>> +3c'
                    return "break"

    def change_date(self):

        user_input = simpledialog.askstring("Change Entry Date", "Enter date (YYYY-MM-DD HH:MM:SS)\nExample: 2026-03-20 14:30:00")
        
        if not user_input:
            return

        try:
            self.custom_datetime = datetime.strptime(user_input, "%Y-%m-%d %H:%M:%S")
            messagebox.showinfo("Success", f"Date set to: {self.custom_datetime}")
        except ValueError:
            messagebox.showerror("Error", "Invalid format. Use YYYY-MM-DD HH:MM:SS")

    def exit_and_save(self, event=None):

        content = self.text.get("1.0", "end").strip() # extract text from line 1 column 0 to 'end' 

        now = self.custom_datetime if self.custom_datetime else datetime.now()
        filename = now.strftime("%Y-%m-%d_%H-%M-%S.txt")

        filepath = os.path.join(SAVE_DIR, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"Journal Entry - {now}\n\n")
            f.write(content)

        print("Saved to:", filepath)

        self.root.destroy()


root = tk.Tk()
app = JournalTerminal(root)
root.mainloop()
