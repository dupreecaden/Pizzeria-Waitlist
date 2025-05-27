import tkinter as tk
from tkinter import messagebox, PhotoImage, ttk
from collections import defaultdict
from Reservation import Reservation, save_reservation, load_reservations, clear_all_reservations
from PIL import Image, ImageTk, ImageSequence
from dotenv import load_dotenv
import os

load_dotenv()
ADMIN_USERNAME = os.environ["ADMIN_USERNAME"]
ADMIN_PASSWORD = os.environ["ADMIN_PASSWORD"]

class PizzeriaBiancoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Pizzeria Waitlist App")
        self.root.geometry("700x500")

        self.root.bind("<F11>", lambda e: self.toggle_fullscreen())
        self.root.bind("<Configure>", self.on_resize)

        self.reservation_counts = defaultdict(int)
        self.max_tables_per_hour = 2
        self.time_slots = [self.format_time(hour) for hour in range(11, 22)]

        self.left_frame = tk.Frame(root)
        self.left_frame.pack(side=tk.LEFT, padx=10, pady=10)

        try:
            self.logo = PhotoImage(file="pizza_logo.png")
            self.logo_label = tk.Label(self.left_frame, image=self.logo)
            self.logo_label.pack(pady=10)
        except:
            pass

        self.name_label = tk.Label(self.left_frame, text="Customer Name:")
        self.name_label.pack()
        self.name_entry = tk.Entry(self.left_frame, width=30)
        self.name_entry.pack(pady=5)

        self.time_label = tk.Label(self.left_frame, text="Reservation Time:")
        self.time_label.pack()
        self.time_var = tk.StringVar()
        self.time_dropdown = ttk.Combobox(self.left_frame, textvariable=self.time_var, values=self.time_slots, state="readonly")
        self.time_dropdown.pack(pady=5)
        self.time_dropdown.set("11:00 AM")

        self.party_size_var = tk.IntVar()
        self.party_size_var.set(2)
        self.radio_frame = tk.Frame(self.left_frame)
        self.radio_label = tk.Label(self.radio_frame, text="Party Size:")
        self.radio_label.pack(side=tk.LEFT)
        tk.Radiobutton(self.radio_frame, text="2", variable=self.party_size_var, value=2).pack(side=tk.LEFT)
        tk.Radiobutton(self.radio_frame, text="4", variable=self.party_size_var, value=4).pack(side=tk.LEFT)
        tk.Radiobutton(self.radio_frame, text="6+", variable=self.party_size_var, value=6).pack(side=tk.LEFT)
        self.radio_frame.pack(pady=10)

        self.add_button = tk.Button(self.left_frame, text="Add to Waitlist", command=self.add_to_waitlist)
        self.add_button.pack(pady=10)

        self.clear_button = tk.Button(self.left_frame, text="Clear All (Admin)", command=self.admin_clear_reservations)
        self.clear_button.pack(pady=5)

        self.exit_button = tk.Button(self.left_frame, text="Exit", command=self.root.quit)
        self.exit_button.pack(pady=5)

        self.right_frame = tk.Frame(root)
        self.right_frame.pack(side=tk.RIGHT, padx=10, pady=10, fill=tk.Y)

        self.list_label = tk.Label(self.right_frame, text="Current Reservations")
        self.list_label.pack()

        self.waitlist_box = tk.Listbox(self.right_frame, width=40)
        self.waitlist_box.pack(pady=10)

        self.analytics_label = tk.Label(self.right_frame, text="Reservation Summary")
        self.analytics_label.pack()
        self.analytics_box = tk.Text(self.right_frame, height=8, width=40, state="disabled")
        self.analytics_box.pack()

        try:
            im = Image.open("Dough-guy.gif")
            self.frames = [ImageTk.PhotoImage(frame.copy().resize((300, 300))) for frame in ImageSequence.Iterator(im)]
            self.mascot_label = tk.Label(root)
            self.mascot_label.place(x=1000, y=430)
            self.mascot_label.lower()
            self.animate_mascot()
        except:
            pass

        for r in load_reservations():
            self.waitlist_box.insert(tk.END, str(r))
            self.reservation_counts[r.time] += 1

        self.update_analytics()

    def format_time(self, hour):
        if hour == 12:
            return "12:00 PM"
        elif hour > 12:
            return f"{hour - 12}:00 PM"
        return f"{hour}:00 AM"

    def toggle_fullscreen(self):
        state = self.root.attributes("-fullscreen")
        self.root.attributes("-fullscreen", not state)

    def animate_mascot(self, counter=0):
        if hasattr(self, 'frames'):
            self.mascot_label.config(image=self.frames[counter])
            self.root.after(100, self.animate_mascot, (counter + 1) % len(self.frames))

    def on_resize(self, event):
        width = self.root.winfo_width()
        if width >= 1100:
            self.mascot_label.lift()
            self.mascot_label.place(x=width - 320, y=430)
        else:
            self.mascot_label.lower()

    def update_analytics(self):
        self.analytics_box.config(state="normal")
        self.analytics_box.delete("1.0", tk.END)
        for time in self.time_slots:
            count = self.reservation_counts[time]
            self.analytics_box.insert(tk.END, f"{time}: {count} reservations\n")
        self.analytics_box.config(state="disabled")

    def add_to_waitlist(self):
        name = self.name_entry.get().strip()
        time = self.time_var.get()
        party_size = self.party_size_var.get()

        if name and time:
            if self.reservation_counts[time] >= self.max_tables_per_hour:
                messagebox.showwarning("Time Slot Full", f"{time} is fully booked.")
                return

            reservation = Reservation(name, time, party_size)
            self.waitlist_box.insert(tk.END, str(reservation))
            self.reservation_counts[time] += 1
            save_reservation(reservation)
            self.update_analytics()
            messagebox.showinfo("Success", "Reservation saved!")
            self.name_entry.delete(0, tk.END)
        else:
            messagebox.showwarning("Missing Info", "Enter your name and choose a time.")

    def admin_clear_reservations(self):
        login = tk.Toplevel(self.root)
        login.title("Admin Login")

        tk.Label(login, text="Username:").pack()
        user_entry = tk.Entry(login)
        user_entry.pack()

        tk.Label(login, text="Password:").pack()
        pass_entry = tk.Entry(login, show="*")
        pass_entry.pack()

        def attempt_clear():
            if user_entry.get() == ADMIN_USERNAME and pass_entry.get() == ADMIN_PASSWORD:
                self.waitlist_box.delete(0, tk.END)
                self.reservation_counts.clear()
                clear_all_reservations()
                self.update_analytics()
                login.destroy()
                messagebox.showinfo("Cleared", "All reservations cleared.")
            else:
                messagebox.showerror("Error", "Invalid credentials.")

        tk.Button(login, text="Login", command=attempt_clear).pack(pady=5)

if __name__ == "__main__":
    root = tk.Tk()
    app = PizzeriaBiancoGUI(root)
    root.mainloop()





