from mcrcon import MCRcon
import customtkinter as ct
import json

# Get Server log-in info
server_info_file = open("JSON/servers.json", mode="r+")
servers_info_list = json.load(server_info_file)
server_name_list = []
current_server = None

for mcserver in servers_info_list:
    server_name_list.append(mcserver["name"])
    if mcserver["default"] == "True":
        current_server = mcserver
        rcon_host = mcserver["host"]
        rcon_password = mcserver["password"]
        rcon_port = mcserver["port"]

# Get selected server's commands
server_command_file = open("JSON/" + current_server["filename"], mode="r+")
command_tab_list = json.load(server_command_file)


def on_select_server(event):
    global current_server, rcon_host, rcon_password, rcon_port, mcserver

    for mcserver in servers_info_list:
        if mcserver["name"] == event:
            current_server = mcserver
            rcon_host = mcserver["host"]
            rcon_password = mcserver["password"]
            rcon_port = mcserver["port"]


def display_saved_commands():
    for tab in command_tab_list:
        for saved_command in tab["commands"]:
            # Create new button
            command = saved_command["command"]

            saved_command_button = ct.CTkButton(
                tab_view.tab(tab["tab"]),
                text=saved_command["name"],
                command=lambda temp=command: run_command(temp),
                width=100,
                height=100
            )

            saved_command_button.pack(side="left", anchor="nw", padx=2, pady=2)


def save_raw_command():
    name = command_name_entry.get() if command_name_entry.get() != "" else "No name"
    command = command_input.get()

    if command != "":
        # Add to JSON file
        for tab in command_tab_list:
            if tab["tab"] == tab_view.get():
                tab["commands"].append({"name": name, "command": command})

        server_command_file.seek(0)
        json.dump(command_tab_list, server_command_file, indent=4)
        server_command_file.truncate()

        # Create new button
        saved_command = ct.CTkButton(
            tab_view.tab(tab_view.get()),
            text=name,
            command=lambda temp=command: run_command(temp),
            width=100,
            height=100
        )

        saved_command.pack(side="left", anchor="nw", padx=2, pady=2)
    else:
        print("You must enter a command to save it")


def run_command(command):
    try:
        with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
            resp = mcr.command(command)
            text = console.cget("text") + "\n" + resp.title()
            console.configure(text=text)
            print(resp.title())
    except Exception:
        print("Invalid Command")


def run_raw_command():
    command = command_input.get()
    run_command(command)


def command_resp(command):
    try:
        with MCRcon(rcon_host, rcon_password, port=rcon_port) as mcr:
            return mcr.command(command)
    except Exception:
        print("Invalid Command")


# System Settings
ct.set_appearance_mode("System")
ct.set_default_color_theme("blue")

# Window
window = ct.CTk()
window.geometry("800x600")
window.title("MCRCON")

# Frames
login_frame = ct.CTkFrame(window)
saved_buttons_frame = ct.CTkFrame(window)
console_frame = ct.CTkScrollableFrame(window, label_anchor="sw")
raw_command_frame = ct.CTkFrame(window)

# Widgets
#   Log-in Frame
servers_combo = ct.CTkComboBox(login_frame, values=server_name_list, command=on_select_server)

#   Saved buttons frame
tab_view = ct.CTkTabview(saved_buttons_frame)
for tab in command_tab_list:
    tab_view.add(tab["tab"])

#   Console frame
text = current_server["name"] + ": " + command_resp("/list")
console = ct.CTkLabel(console_frame, text=text, anchor="nw", justify="left")

#   Raw Command Frame
raw_save_button = ct.CTkButton(raw_command_frame, text="Save", command=save_raw_command, width=50)
command_name_entry = ct.CTkEntry(raw_command_frame, width=200, placeholder_text="Name")
command_input = ct.CTkEntry(raw_command_frame, placeholder_text="Command")
run_button = ct.CTkButton(raw_command_frame, text="Run", command=run_raw_command, width=75)

# Layout
#   Login Frame
servers_combo.pack(side="left")
login_frame.pack(fill="x")

#   Saved Command Frame
tab_view.pack(fill="both", expand=True)
display_saved_commands()
saved_buttons_frame.pack(fill="both", expand=True)

#   Console
console.pack(fill="both", expand=True, anchor="n")
console_frame.pack(fill="both", expand=True)

#   Raw Command Frame
raw_save_button.pack(padx=2, pady=(2, 15), side="left")
command_name_entry.pack(padx=2, pady=(2, 15), side="left")
command_input.pack(padx=2, pady=(2, 15), side="left", fill="x", expand=True)
run_button.pack(padx=2, pady=(2, 15), side="left")
raw_command_frame.pack(side="bottom", fill="x")

# Run app
window.mainloop()
server_info_file.close()
server_command_file.close()
