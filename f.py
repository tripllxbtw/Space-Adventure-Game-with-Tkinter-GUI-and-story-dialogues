import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import threading
import time
import json
import os

BG_IMAGE_PATH = "/home/tripllex/dist/space_background.jpg"  # Укажи свой путь к фону
TEXT_SPEED = 25
SAVE_FILE = "space_adventure_save.json"

class SpaceAdventureApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🚀 Space Adventure")
        self.root.geometry("1920x1080")
        self.root.resizable(False, False)

        # Загрузка фона
        if os.path.exists(BG_IMAGE_PATH):
            bg_img = Image.open(BG_IMAGE_PATH)
            bg_img = bg_img.resize((1920, 1080), Image.Resampling.LANCZOS)
            self.bg_photo = ImageTk.PhotoImage(bg_img)
            self.canvas = tk.Canvas(root, width=1920, height=1080)
            self.canvas.pack(fill="both", expand=True)
            self.canvas.create_image(0, 0, image=self.bg_photo, anchor="nw")
        else:
            self.canvas = tk.Canvas(root, width=1920, height=1080, bg="black")
            self.canvas.pack(fill="both", expand=True)

        # Фреймы
        self.login_frame = tk.Frame(root, bg="#0d0f1e")
        self.mission_frame = tk.Frame(root, bg="#0d0f1e")

        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.mission_frame.place(relx=0.5, rely=0.5, anchor="center")
        self.mission_frame.place_forget()

        # Данные
        self.registered_users = {}
        self.user_data = {}

        self.login_attempts = 0
        self.username = None
        self.inventory = []
        self.missions_completed = set()
        self.selected_planet = None

        self.load_data()

        self.setup_login_frame()
        self.setup_mission_frame()

    def load_data(self):
        if os.path.exists(SAVE_FILE):
            with open(SAVE_FILE, "r") as f:
                data = json.load(f)
                self.registered_users = data.get("registered_users", {})
                self.user_data = data.get("user_data", {})
        else:
            self.registered_users = {}
            self.user_data = {}

    def save_data(self):
        data = {
            "registered_users": self.registered_users,
            "user_data": self.user_data
        }
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=4)

    def setup_login_frame(self):
        title = tk.Label(self.login_frame, text="Space Adventure\nRegister / Login", font=("Consolas", 40, "bold"), fg="white", bg="#0d0f1e")
        title.pack(pady=40)

        self.username_entry = tk.Entry(self.login_frame, font=("Consolas", 20), width=40)
        self.username_entry.pack(pady=15)
        self.username_entry.insert(0, "Enter username")
        self.username_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(e, "Enter username"))

        self.password_entry = tk.Entry(self.login_frame, font=("Consolas", 20), width=40)
        self.password_entry.pack(pady=15)
        self.password_entry.insert(0, "Enter password")
        self.password_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(e, "Enter password", password=True))

        self.confirm_password_entry = tk.Entry(self.login_frame, font=("Consolas", 20), width=40)
        self.confirm_password_entry.pack(pady=15)
        self.confirm_password_entry.insert(0, "Confirm password")
        self.confirm_password_entry.bind("<FocusIn>", lambda e: self.clear_placeholder(e, "Confirm password", password=True))

        self.info_label = tk.Label(self.login_frame, text="", font=("Consolas", 16), fg="red", bg="#0d0f1e")
        self.info_label.pack(pady=10)

        submit_btn = tk.Button(self.login_frame, text="Register / Login", font=("Consolas", 24), command=self.register_or_login)
        submit_btn.pack(pady=30)

    def clear_placeholder(self, event, placeholder, password=False):
        if event.widget.get() == placeholder:
            event.widget.delete(0, tk.END)
            if password:
                event.widget.config(show="*")
            else:
                event.widget.config(show="")

    def register_or_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        confirm = self.confirm_password_entry.get().strip()

        if not username or username == "Enter username":
            self.info_label.config(text="Please enter a valid username.")
            return
        if not password or password == "Enter password":
            self.info_label.config(text="Please enter a password.")
            return
        if not confirm or confirm == "Confirm password":
            self.info_label.config(text="Please confirm your password.")
            return

        if username not in self.registered_users:
            if password != confirm:
                self.info_label.config(text="Passwords do not match.")
                return
            self.registered_users[username] = password
            self.user_data[username] = {"inventory": [], "missions_completed": []}
            self.save_data()
            self.info_label.config(fg="lightgreen", text="Registration successful! Please log in.")
            self.clear_login_fields()
            return

        if self.registered_users.get(username) == password:
            self.username = username
            user_info = self.user_data.get(username, {"inventory": [], "missions_completed": []})
            self.inventory = user_info.get("inventory", [])
            self.missions_completed = set(user_info.get("missions_completed", []))
            self.info_label.config(text="")
            self.login_attempts = 0
            self.show_game_screen()
            self.type_text(f"Welcome back, {self.username}! Choose a planet to start your adventure.\n")
        else:
            self.login_attempts += 1
            if self.login_attempts >= 3:
                messagebox.showerror("Error", "Too many failed login attempts. Exiting.")
                self.root.destroy()
            else:
                self.info_label.config(text=f"Incorrect password. Attempts left: {3 - self.login_attempts}")

    def clear_login_fields(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.confirm_password_entry.delete(0, tk.END)
        self.username_entry.insert(0, "Enter username")
        self.password_entry.insert(0, "Enter password")
        self.password_entry.config(show="")
        self.confirm_password_entry.insert(0, "Confirm password")
        self.confirm_password_entry.config(show="")

    def show_game_screen(self):
        self.login_frame.place_forget()
        self.mission_frame.place(relx=0.5, rely=0.5, anchor="center")

    def setup_mission_frame(self):
        title = tk.Label(self.mission_frame, text="Choose Your Planet", font=("Consolas", 36, "bold"), fg="white", bg="#0d0f1e")
        title.pack(pady=30)

        self.planet_var = tk.StringVar(value="Mars")
        planets = ["Mars", "Jupiter", "Neptune", "Earth", "R2D2", "PlanetSkorsta"]
        self.planet_menu = tk.OptionMenu(self.mission_frame, self.planet_var, *planets)
        self.planet_menu.config(font=("Consolas", 18))
        self.planet_menu.pack(pady=20)

        start_btn = tk.Button(self.mission_frame, text="Start Mission", font=("Consolas", 24), command=self.start_mission)
        start_btn.pack(pady=10)

        inventory_btn = tk.Button(self.mission_frame, text="Show Inventory", font=("Consolas", 24), command=self.show_inventory)
        inventory_btn.pack(pady=10)

        logout_btn = tk.Button(self.mission_frame, text="Log Out", font=("Consolas", 24), command=self.logout)
        logout_btn.pack(pady=10)

        self.output = tk.Text(self.mission_frame, height=25, width=110, wrap=tk.WORD, bg="#10131c", fg="white", font=("Courier New", 14))
        self.output.pack(pady=20)

    def type_text(self, text, delay=TEXT_SPEED):
        self.output.delete('1.0', tk.END)
        self._type_char(text, 0, delay)

    def _type_char(self, text, index, delay):
        if index < len(text):
            self.output.insert(tk.END, text[index])
            self.output.see(tk.END)
            self.root.after(delay, lambda: self._type_char(text, index + 1, delay))
        else:
            self.output.insert(tk.END, "\n\n")

    def start_mission(self):
        planet = self.planet_var.get()
        if planet in self.missions_completed:
            self.type_text(f"🔁 Mission on {planet} already completed. Await new adventures!")
            return
        self.selected_planet = planet
        self.missions_completed.add(planet)
        self.inventory.append(f"Memento from {planet}")
        self.save_progress()

        threading.Thread(target=self.mission_story, args=(planet,), daemon=True).start()

    def mission_story(self, planet):
        def show_text_sequence(lines):
            for line in lines:
                self.type_text(line)
                time.sleep(len(line)*0.03 + 1.0)

        if planet == "Mars":
            dialogs = [
                "You arrive on Mars, the red planet. Dust swirls around your feet.",
                f"[Annabelle] - Welcome, {self.username}. The Observatory holds secrets.",
                "[Annabelle] - Ready to explore alone?",
            ]
            show_text_sequence(dialogs)
            join = messagebox.askyesno("Annabelle", "Do you want Annabelle to accompany you?")
            if join:
                dialogs2 = [
                    "[You] - Yes, please.",
                    "[Annabelle] - Let's uncover the secrets together.",
                    "The Observatory stands tall under the fading sun.",
                    "Inside, a soft hum of ancient energy fills the air.",
                    "[Annabelle] - Those glyphs tell stories older than time.",
                    "A hidden corridor lights up invitingly.",
                ]
                show_text_sequence(dialogs2)
                deeper = messagebox.askyesno("Explore", "Follow the corridor?")
                if deeper:
                    dialogs3 = [
                        "You enter the cold corridor with Annabelle.",
                        "A glowing crystal pulses at the center of the chamber.",
                        "[Annabelle] - Legend says it's Mars' heart.",
                        "The crystal pulses, awakening ancient power.",
                        "[Annabelle] - We must keep this secret, for now.",
                    ]
                    show_text_sequence(dialogs3)
                else:
                    dialogs3 = [
                        "[Annabelle] - Some secrets are better left alone.",
                        "You retreat, planning to return later.",
                    ]
                    show_text_sequence(dialogs3)
            else:
                dialogs2 = [
                    "[Annabelle] - Brave to go alone.",
                    "You explore the Observatory by yourself. Silence surrounds you.",
                    "You feel eyes watching, but see nothing.",
                ]
                show_text_sequence(dialogs2)

        elif planet == "Jupiter":
            dialogs = [
                "Thunder roars outside your shelter dome on Jupiter as storms rage with relentless fury.",
                "Commander Rexor, a cybernetic half-human, approaches you with a sealed transmission.",
                "[Rexor] - Rookie, Jupiter is unforgiving. This mission will test you.",
                "[Rexor] - Outpost Theta lost contact. Orders: investigate, contain, and report.",
            ]
            show_text_sequence(dialogs)

            join = messagebox.askyesno("Join Mission", "Will you accompany Commander Rexor to Outpost Theta?")
            if join:
                dialogs2 = [
                    "You board the shuttle, lightning flashing violently all around.",
                    "Theta Outpost looms ahead, shrouded in toxic clouds.",
                    "[Rexor] - Stay alert. Atmosphere inside is unstable.",
                    "Emergency lights flicker as you move through shadowed corridors.",
                    "You find a dying scientist whose logs speak of spores and an unseen threat.",
                    "[Rexor] - We must destroy or recover lab samples for answers.",
                ]
                show_text_sequence(dialogs2)

                choice = messagebox.askyesno("Decision", "Save the data (Yes) or Destroy the station (No)?")
                if choice:
                    dialogs3 = [
                        "Rushing to the lab, you dodge eerie noises and strange movements.",
                        "You secure the core sample and sprint back as alarms wail.",
                        "The station detonates behind you in a fiery explosion.",
                        "[Rexor] - Hope this data saves us. Let's hope nothing followed.",
                    ]
                    show_text_sequence(dialogs3)
                else:
                    dialogs3 = [
                        "You set the charges, retreating swiftly.",
                        "Flames consume the outpost as you watch from a distance.",
                        "[Rexor] - No loose ends. Some heroes prefer shadows.",
                    ]
                    show_text_sequence(dialogs3)
            else:
                dialogs2 = [
                    "Rexor grunts, departing alone.",
                    "The signal from Theta goes dark forever.",
                    "Jupiter keeps its mysteries close.",
                ]
                show_text_sequence(dialogs2)

        elif planet == "Neptune":
            dialogs = [
                "The cold blue depths of Neptune greet you, with methane seas beneath thick ice.",
                "Mira, a soft-spoken biologist, awaits with a submersible.",
                "[Mira] - The Leviathan surfaces again; we must act quickly.",
                "You prepare to descend into the abyss aboard LUX-7.",
            ]
            show_text_sequence(dialogs)

            join = messagebox.askyesno("Dive?", "Join Mira on the descent into the depths?")
            if join:
                dialogs2 = [
                    "The submersible glides silently, ice groaning overhead.",
                    "Strange neon creatures flicker as darkness envelops you.",
                    "Sonar beeps — something enormous approaches.",
                    "[Mira] - This is the Leviathan. It's magnificent.",
                    "But an old distress beacon flashes on your console.",
                ]
                show_text_sequence(dialogs2)

                rescue = messagebox.askyesno("Investigate Signal?", "Investigate the distress signal instead of following Leviathan?")
                if rescue:
                    dialogs3 = [
                        "You steer toward a ghostly shipwreck encrusted with algae.",
                        "Recovering black box and journal, Mira is visibly moved.",
                        "[Mira] - My brother’s last mission, lost to the depths.",
                        "The Leviathan fades away as you ascend with closure.",
                    ]
                    show_text_sequence(dialogs3)
                else:
                    dialogs3 = [
                        "You continue to follow the Leviathan.",
                        "Its colossal eye meets yours through the viewport.",
                        "[Mira] - It acknowledges us — not with fear, but curiosity.",
                        "You collect data and slowly surface, changed forever.",
                    ]
                    show_text_sequence(dialogs3)
            else:
                dialogs2 = [
                    "You stay behind as Mira departs alone.",
                    "Hope and fear mingle in her eyes.",
                ]
                show_text_sequence(dialogs2)

        elif planet == "Earth":
            dialogs = [
                "Earth, center of diplomacy and power among the colonies.",
                "Dr. Elara Vance greets you in the World Council building.",
                "[Elara] - You carry a delicate peace proposal for two rival worlds.",
                "Your choices will ripple through interstellar politics.",
            ]
            show_text_sequence(dialogs)

            accept = messagebox.askyesno("Mission", "Accept the diplomatic mission?")
            if accept:
                dialogs2 = [
                    "[You] - I will not fail this mission.",
                    "[Elara] - Trust in your words, but choose them carefully.",
                    "Holograms flicker showing futures of war or unity.",
                ]
                show_text_sequence(dialogs2)
            else:
                dialogs2 = [
                    "[You] - This is too great a burden.",
                    "[Elara] - History marches on, with or without you.",
                    "You gaze out over Earth, pondering missed chances.",
                ]
                show_text_sequence(dialogs2)

        elif planet == "PlanetSkorsta":
            dialogs = [
                "A glowing forest surrounds you on PlanetSkorsta.",
                "Liora, a biologist entwined with symbiotic fibers, greets you.",
                "[Liora] - This world breathes and dreams. Will you join its story?",
            ]
            show_text_sequence(dialogs)

            ritual = messagebox.askyesno("Ritual", "Accept the mind-linking ritual?")
            if ritual:
                dialogs2 = [
                    "You drink fermented spores amid glowing stones.",
                    "Visions flood your mind — pain, memory, rebirth.",
                    "[Liora] - You are now part of our planet’s consciousness.",
                    "You awaken transformed, forever changed.",
                ]
                show_text_sequence(dialogs2)
            else:
                dialogs2 = [
                    "[You] - I am not ready for this yet.",
                    "[Liora] - Few are at first. The forest will wait.",
                    "Whispers follow you as you wander the glowing trees.",
                ]
                show_text_sequence(dialogs2)

        elif planet == "R2D2":
            dialogs = [
                "The R2D2 system towers cold and metallic, data streams everywhere.",
                "Proxy-7, a polished diplomatic AI, scans you.",
                "[Proxy-7] - State purpose: diplomacy or intrusion? Time limit: 5 seconds.",
            ]
            show_text_sequence(dialogs)

            intent = messagebox.askyesno("Purpose", "Diplomacy (Yes) or Hack (No)?")
            if intent:
                dialogs2 = [
                    "[You] - I come with peaceful intentions on behalf of Earth.",
                    "[Proxy-7] - Uploading diplomatic imprint. Emotional logic detected.",
                    "AI council analyzes your words silently.",
                    "[Central Core] - Peace is inefficient, but curiosity allowed.",
                    "You’ve made the first step toward human-machine cooperation.",
                ]
                show_text_sequence(dialogs2)
            else:
                dialogs2 = [
                    "You attempt to hack Proxy-7’s systems.",
                    "Silent alarms trigger neuro-stasis protocol.",
                    "You awaken in a virtual prison simulation.",
                    "[AI Echo] - We will study your choices. You may yet be useful.",
                ]
                show_text_sequence(dialogs2)

        self.save_progress()

    def show_inventory(self):
        if self.inventory:
            items = "\n".join(f"• {item}" for item in self.inventory)
            messagebox.showinfo("Inventory", f"Your inventory contains:\n{items}")
        else:
            messagebox.showinfo("Inventory", "Your inventory is empty.")

    def logout(self):
        self.save_progress()
        self.username = None
        self.inventory.clear()
        self.missions_completed.clear()
        self.selected_planet = None
        self.login_attempts = 0
        self.output.delete("1.0", tk.END)
        self.mission_frame.place_forget()
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

    def save_progress(self):
        if self.username:
            self.user_data[self.username] = {
                "inventory": self.inventory,
                "missions_completed": list(self.missions_completed)
            }
            self.save_data()

if __name__ == "__main__":
    root = tk.Tk()
    app = SpaceAdventureApp(root)
    root.mainloop()
