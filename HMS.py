import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import os

#  COLORS 
BG = "#2C3E50"
PANEL = "#34495E"
BTN = "#B7950B"
TXT = "#ECF0F1"

#  FILES 
ADMIN_FILE = "admins.txt"
ROOM_FILE = "rooms.txt"
BOOKING_FILE = "bookings.txt"


#  UTILITIES 
def center(win, w, h):
    x = (win.winfo_screenwidth() // 2) - (w // 2)
    y = (win.winfo_screenheight() // 2) - (h // 2)
    win.geometry(f"{w}x{h}+{x}+{y}")


def read_file(file):
    if not os.path.exists(file):
        return []
    with open(file, "r") as f:
        return f.read().splitlines()


def write_file(file, data, mode="w"):
    with open(file, mode) as f:
        f.write("\n".join(data) + ("\n" if mode == "a" else ""))


#  LOAD DATA 
admins = {}
for line in read_file(ADMIN_FILE):
    u, p = line.split("|")
    admins[u] = p

if not os.path.exists(ROOM_FILE):
    write_file(ROOM_FILE, [
        "101|Single|3000|Available",
        "102|Double|5000|Available",
        "103|Deluxe|8000|Available"
    ])

rooms = {}
for line in read_file(ROOM_FILE):
    r, t, p, s = line.split("|")
    rooms[r] = [t, int(p), s]

# active bookings only (in memory)
active_bookings = {}


#  LOGIN WINDOW 
login = tk.Tk()
login.title("Admin Login")
center(login, 330, 300)
login.configure(bg=BG)


def register_window():
    reg = tk.Toplevel(login)
    reg.title("Register Admin")
    center(reg, 320, 260)
    reg.configure(bg=BG)

    tk.Label(reg, text="New Username", bg=BG, fg=TXT).pack(pady=5)
    u = tk.Entry(reg)
    u.pack()

    tk.Label(reg, text="New Password", bg=BG, fg=TXT).pack(pady=5)
    p = tk.Entry(reg, show="*")
    p.pack()

    def register():
        if not u.get() or not p.get():
            messagebox.showerror("Error", "All fields required")
            return
        if u.get() in admins:
            messagebox.showerror("Error", "Admin already exists")
            return
        admins[u.get()] = p.get()
        write_file(ADMIN_FILE, [f"{k}|{v}" for k, v in admins.items()])
        messagebox.showinfo("Success", "Admin Registered")
        reg.destroy()

    tk.Button(reg, text="Register", bg=BTN, command=register).pack(pady=15)


def login_admin():
    if admins.get(username.get()) == password.get():
        login.withdraw()
        dashboard()
    else:
        messagebox.showerror("Login Failed", "Invalid credentials")


tk.Label(login, text="Admin Login", font=("Arial", 16, "bold"),
         bg=BG, fg=TXT).pack(pady=15)

tk.Label(login, text="Username", bg=BG, fg=TXT).pack()
username = tk.Entry(login)
username.pack()

tk.Label(login, text="Password", bg=BG, fg=TXT).pack()
password = tk.Entry(login, show="*")
password.pack()

tk.Button(login, text="Login", bg=BTN, command=login_admin).pack(pady=10)
tk.Button(login, text="Register New Admin", command=register_window).pack()


#  DASHBOARD 
def dashboard():
    root = tk.Toplevel()
    root.title("Hotel Management System")
    center(root, 950, 600)
    root.configure(bg=BG)

    def logout():
        root.destroy()
        login.deiconify()

    def refresh_table():
        table.delete(*table.get_children())
        for r, d in rooms.items():
            table.insert("", "end", values=(r, d[0], d[1], d[2]))

    def save_rooms():
        write_file(
            ROOM_FILE,
            [f"{r}|{d[0]}|{d[1]}|{d[2]}" for r, d in rooms.items()]
        )

    #  CHECK-IN 
    def check_in():
        g = guest_name.get().strip()
        r = room_no.get().strip()

        if not g or r not in rooms:
            messagebox.showerror("Error", "Invalid input")
            return
        if rooms[r][2] == "Occupied":
            messagebox.showwarning("Unavailable", "Room already occupied")
            return

        checkin_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        rooms[r][2] = "Occupied"

        active_bookings[r] = {
            "name": g,
            "price": rooms[r][1],
            "checkin": checkin_time
        }

        save_rooms()
        refresh_table()
        messagebox.showinfo("Success", "Guest Checked In")

    #  CHECK-OUT 
    def check_out():
        r = room_no.get().strip()

        if r not in active_bookings:
            messagebox.showerror("Error", "No active booking found")
            return

        booking = active_bookings[r]
        checkout_time = datetime.now()

        checkin_time = datetime.strptime(
            booking["checkin"], "%Y-%m-%d %H:%M:%S"
        )

        days = max((checkout_time - checkin_time).days, 1)
        total = days * booking["price"]

        record = (
            f"{booking['name']}|{r}|{booking['price']}|"
            f"{booking['checkin']}|"
            f"{checkout_time.strftime('%Y-%m-%d %H:%M:%S')}|"
            f"{days}|{total}"
        )

        write_file(BOOKING_FILE, [record], mode="a")

        rooms[r][2] = "Available"
        del active_bookings[r]

        save_rooms()
        refresh_table()

        messagebox.showinfo(
            "Bill",
            f"Guest: {booking['name']}\n"
            f"Days: {days}\n"
            f"Total Bill: Rs {total}"
        )

    #  ADD ROOM 
    def add_room():
        r = new_room.get().strip()
        t = room_type.get().strip()
        p = price.get().strip()

        if not r or not t or not p:
            messagebox.showerror("Error", "Fill all fields")
            return
        if r in rooms:
            messagebox.showerror("Error", "Room already exists")
            return
        if not p.isdigit():
            messagebox.showerror("Error", "Price must be numeric")
            return

        rooms[r] = [t, int(p), "Available"]
        save_rooms()
        refresh_table()

        new_room.delete(0, tk.END)
        room_type.delete(0, tk.END)
        price.delete(0, tk.END)

        messagebox.showinfo("Success", "Room Added")

    #  UI
    tk.Label(root, text="Hotel Management System",
             font=("Arial", 18, "bold"),
             bg=BG, fg=TXT).pack(pady=10)

    columns = ("Room No", "Type", "Price", "Status")
    table = ttk.Treeview(root, columns=columns, show="headings", height=10)
    for c in columns:
        table.heading(c, text=c)
    table.pack()
    refresh_table()

    form = tk.Frame(root, bg=PANEL)
    form.pack(pady=15)

    tk.Label(form, text="Guest Name", bg=PANEL, fg=TXT).grid(row=0, column=0)
    guest_name = tk.Entry(form)
    guest_name.grid(row=0, column=1)

    tk.Label(form, text="Room No", bg=PANEL, fg=TXT).grid(row=1, column=0)
    room_no = tk.Entry(form)
    room_no.grid(row=1, column=1)

    tk.Button(form, text="Check In", bg=BTN, command=check_in).grid(row=2, column=0, pady=5)
    tk.Button(form, text="Check Out", bg=BTN, command=check_out).grid(row=2, column=1)

    admin = tk.LabelFrame(root, text="Add New Room",
                          bg=PANEL, fg=TXT)
    admin.pack(pady=15)

    tk.Label(admin, text="Room No", bg=PANEL, fg=TXT).grid(row=0, column=0)
    new_room = tk.Entry(admin)
    new_room.grid(row=0, column=1)

    tk.Label(admin, text="Type", bg=PANEL, fg=TXT).grid(row=1, column=0)
    room_type = tk.Entry(admin)
    room_type.grid(row=1, column=1)

    tk.Label(admin, text="Price", bg=PANEL, fg=TXT).grid(row=2, column=0)
    price = tk.Entry(admin)
    price.grid(row=2, column=1)

    tk.Button(admin, text="Add Room", bg=BTN, command=add_room)\
        .grid(row=3, column=0, columnspan=2, pady=10)

    tk.Button(root, text="Logout", bg="darkred", fg="white",
              command=logout).pack(pady=10)


login.mainloop()
