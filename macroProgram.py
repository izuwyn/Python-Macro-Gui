import os
import sys
import ctypes

# Set unique AppUserModelID for Windows taskbar icon grouping
if sys.platform == "win32":
    try:
        myappid = 'antigravity.python.macro.studio.v1'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    except Exception:
        pass

import pynput as p
import customtkinter as ctk
import time
import threading
import pyautogui
from PIL import Image, ImageTk

# Configure PyAutoGUI settings for high responsiveness
pyautogui.PAUSE = 0.0
pyautogui.FAILSAFE = True

# Set appearance and theme
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Modifier keys mapping
MODIFIER_KEYS = {
    'ctrl', 'shift', 'alt', 'win', 'cmd', 
    'ctrlleft', 'ctrlright', 'shiftleft', 'shiftright', 
    'altleft', 'altright', 'command'
}

class MacroStepRow(ctk.CTkFrame):
    """A custom widget representing a single macro action row"""
    def __init__(self, master, action_type, value, x, y, delay, app_ref=None, **kwargs):
        super().__init__(master, **kwargs)
        self.app_ref = app_ref
        self.action_type = action_type # e.g., "Mouse Click", "Mouse Down", "Mouse Up", "Key Press", "Key Down", "Key Up"
        
        self.configure(fg_color="gray15", height=45)
        
        # Configure columns for clean alignment
        self.grid_columnconfigure(0, minsize=115)  # Type Badge
        self.grid_columnconfigure(1, minsize=140)  # Value/Key Entry
        self.grid_columnconfigure(2, minsize=80)   # X Entry
        self.grid_columnconfigure(3, minsize=80)   # Y Entry
        self.grid_columnconfigure(4, minsize=90)   # Delay Entry
        self.grid_columnconfigure(5, minsize=60)   # Test Button
        self.grid_columnconfigure(6, minsize=40)   # Delete Button

        # Action Badge
        if "Mouse" in self.action_type:
            self.type_badge = ctk.CTkLabel(self, text=self.action_type, fg_color="#1f538d", text_color="white", corner_radius=6, height=26, font=ctk.CTkFont(size=11, weight="bold"))
        else:
            self.type_badge = ctk.CTkLabel(self, text=self.action_type, fg_color="#2e7d32", text_color="white", corner_radius=6, height=26, font=ctk.CTkFont(size=11, weight="bold"))
        self.type_badge.grid(row=0, column=0, padx=5, pady=8, sticky="ew")

        # Value Entry (Key name or Mouse Button name)
        self.val_entry = ctk.CTkEntry(self, width=130, height=28)
        self.val_entry.insert(0, str(value))
        self.val_entry.grid(row=0, column=1, padx=5, pady=8, sticky="w")

        # X Entry
        self.x_entry = ctk.CTkEntry(self, width=70, height=28)
        if x is not None and x != "":
            self.x_entry.insert(0, str(x))
        else:
            self.x_entry.configure(state="disabled", fg_color="gray25")
        self.x_entry.grid(row=0, column=2, padx=5, pady=8, sticky="w")

        # Y Entry
        self.y_entry = ctk.CTkEntry(self, width=70, height=28)
        if y is not None and y != "":
            self.y_entry.insert(0, str(y))
        else:
            self.y_entry.configure(state="disabled", fg_color="gray25")
        self.y_entry.grid(row=0, column=3, padx=5, pady=8, sticky="w")

        # Delay Entry (wait before this step in seconds)
        self.delay_entry = ctk.CTkEntry(self, width=80, height=28)
        self.delay_entry.insert(0, f"{delay:.3f}" if isinstance(delay, (int, float)) else str(delay))
        self.delay_entry.grid(row=0, column=4, padx=5, pady=8, sticky="w")

        # Test Button (plays just this step)
        self.test_btn = ctk.CTkButton(self, text="▶", width=35, height=28, fg_color="#4a4a4a", hover_color="#626262", command=self.test_step)
        self.test_btn.grid(row=0, column=5, padx=5, pady=8)

        # Delete Button
        self.del_btn = ctk.CTkButton(self, text="X", width=30, height=28, fg_color="#a13333", hover_color="#7c2727", command=self.destroy)
        self.del_btn.grid(row=0, column=6, padx=5, pady=8)

    def get_data(self):
        """Returns the dictionary representing the current state of this step"""
        val = self.val_entry.get().strip()
        x_val = self.x_entry.get().strip()
        y_val = self.y_entry.get().strip()
        delay_val = self.delay_entry.get().strip()
        
        try:
            delay = float(delay_val)
        except ValueError:
            delay = 0.0
            
        x = None
        y = None
        if "Mouse" in self.action_type:
            try:
                x = int(x_val)
                y = int(y_val)
            except ValueError:
                x = 0
                y = 0
                
        return {
            "type": self.action_type,
            "value": val,
            "x": x,
            "y": y,
            "delay": delay
        }

    def test_step(self):
        """Simulates just this single step immediately"""
        if self.app_ref:
            self.app_ref.test_single_step(self.get_data())

    def set_interactive(self, state: bool):
        s = "normal" if state else "disabled"
        self.val_entry.configure(state=s)
        self.delay_entry.configure(state=s)
        self.test_btn.configure(state=s)
        self.del_btn.configure(state=s)
        
        if state:
            if "Mouse" in self.action_type:
                self.x_entry.configure(state="normal", fg_color="gray20")
                self.y_entry.configure(state="normal", fg_color="gray20")
            else:
                self.x_entry.configure(state="disabled", fg_color="gray25")
                self.y_entry.configure(state="disabled", fg_color="gray25")
        else:
            self.x_entry.configure(state="disabled", fg_color="gray25")
            self.y_entry.configure(state="disabled", fg_color="gray25")


class MacroMakerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Python Macro Studio")
        self.geometry("960x650")
        self.resizable(True, True)

        # Set window icon
        try:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            ico_path = os.path.join(current_dir, "icon.ico")
            png_path = os.path.join(current_dir, "pfp.png")
            
            # Generate icon.ico dynamically from pfp.png if it does not exist
            if not os.path.exists(ico_path) and os.path.exists(png_path):
                try:
                    img = Image.open(png_path)
                    img.save(ico_path, format="ICO", sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
                except Exception as ex:
                    print(f"Could not generate icon.ico: {ex}")
            
            # Use iconbitmap if ico file exists (works natively on Windows)
            if os.path.exists(ico_path) and sys.platform == "win32":
                self.iconbitmap(ico_path)
            elif os.path.exists(png_path):
                # Fallback / non-Windows platforms
                icon_img = Image.open(png_path)
                icon_photo = ImageTk.PhotoImage(icon_img)
                self.iconphoto(False, icon_photo)
                self._icon_ref = icon_photo  # Keep reference to prevent garbage collection
        except Exception as e:
            print(f"Error loading window icon: {e}")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # State Variables
        self.recording = False
        self.playback_running = False
        self.stop_playback_flag = False
        self.currently_pressed_keys = set()
        self.last_mouse_press = None
        self.start_time = 0.0
        self.last_event_time = 0.0

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(11, weight=1) # push status to bottom
        
        ctk.CTkLabel(self.sidebar_frame, text="Macro Studio", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=20)
        
        # Recording section
        self.record_label = ctk.CTkLabel(self.sidebar_frame, text="Recording Controls", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray")
        self.record_label.grid(row=1, column=0, padx=15, pady=(10, 2), sticky="w")

        self.add_record_btn = ctk.CTkButton(self.sidebar_frame, text="Start Recording (F1)", fg_color="#b32424", hover_color="#8c1c1c", command=self.start_recording)
        self.add_record_btn.grid(row=2, column=0, padx=15, pady=5, sticky="ew")

        self.add_stop_record_btn = ctk.CTkButton(self.sidebar_frame, text="Stop Recording (F2)", state="disabled", fg_color="gray25", command=self.stop_recording)
        self.add_stop_record_btn.grid(row=3, column=0, padx=15, pady=5, sticky="ew")
        
        # Playback section
        self.playback_label = ctk.CTkLabel(self.sidebar_frame, text="Playback Controls", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray")
        self.playback_label.grid(row=4, column=0, padx=15, pady=(15, 2), sticky="w")
        
        self.play_btn = ctk.CTkButton(self.sidebar_frame, text="Play Macro (F3)", fg_color="#2e7d32", hover_color="#1b5e20", command=self.start_playback)
        self.play_btn.grid(row=5, column=0, padx=15, pady=5, sticky="ew")
        
        self.stop_play_btn = ctk.CTkButton(self.sidebar_frame, text="Stop Playback (F4)", state="disabled", fg_color="gray25", command=self.stop_playback)
        self.stop_play_btn.grid(row=6, column=0, padx=15, pady=5, sticky="ew")
        
        # Playback Options
        self.loop_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        self.loop_frame.grid(row=7, column=0, padx=15, pady=10, sticky="ew")
        
        self.loop_checkbox = ctk.CTkCheckBox(self.loop_frame, text="Loop", width=60)
        self.loop_checkbox.pack(side="left", padx=(5, 5))
        
        self.loop_count_entry = ctk.CTkEntry(self.loop_frame, width=50)
        self.loop_count_entry.insert(0, "1")
        self.loop_count_entry.pack(side="left", padx=5)
        ctk.CTkLabel(self.loop_frame, text="times", text_color="gray").pack(side="left")
        
        # Manual actions
        self.manual_label = ctk.CTkLabel(self.sidebar_frame, text="Manual Editing", font=ctk.CTkFont(size=12, weight="bold"), text_color="gray")
        self.manual_label.grid(row=8, column=0, padx=15, pady=(15, 2), sticky="w")
        
        self.add_click_btn = ctk.CTkButton(self.sidebar_frame, text="+ Click Step", fg_color="#3a3a3a", hover_color="#4a4a4a", command=self.add_manual_click_step)
        self.add_click_btn.grid(row=9, column=0, padx=15, pady=5, sticky="ew")
        
        self.add_key_btn = ctk.CTkButton(self.sidebar_frame, text="+ Key Step", fg_color="#3a3a3a", hover_color="#4a4a4a", command=self.add_manual_key_step)
        self.add_key_btn.grid(row=10, column=0, padx=15, pady=5, sticky="ew")
        
        self.clear_btn = ctk.CTkButton(self.sidebar_frame, text="Clear All Steps", fg_color="#6d2e2e", hover_color="#8d3e3e", command=self.clear_all_steps)
        self.clear_btn.grid(row=12, column=0, padx=15, pady=15, sticky="ew")

        # Status Display (Anchored at the bottom)
        self.status_frame = ctk.CTkFrame(self.sidebar_frame, fg_color="gray12", height=60)
        self.status_frame.grid(row=13, column=0, padx=15, pady=(10, 20), sticky="ew")
        self.status_frame.pack_propagate(False)
        
        self.status_title = ctk.CTkLabel(self.status_frame, text="STATUS", font=ctk.CTkFont(size=10, weight="bold"), text_color="gray")
        self.status_title.pack(anchor="w", padx=10, pady=(5, 0))
        
        self.status_lbl = ctk.CTkLabel(self.status_frame, text="Idle", font=ctk.CTkFont(size=12, weight="bold"), text_color="#00c896")
        self.status_lbl.pack(anchor="w", padx=10, pady=(2, 5))

        # --- Main Macro List ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(self.main_frame, text="Macro Sequence Editor", font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=20, pady=(15, 5), sticky="w")

        # Column headers frame
        self.header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.header_frame.grid(row=1, column=0, padx=20, pady=(5, 0), sticky="ew")
        
        self.header_frame.grid_columnconfigure(0, minsize=115)
        self.header_frame.grid_columnconfigure(1, minsize=140)
        self.header_frame.grid_columnconfigure(2, minsize=80)
        self.header_frame.grid_columnconfigure(3, minsize=80)
        self.header_frame.grid_columnconfigure(4, minsize=90)
        self.header_frame.grid_columnconfigure(5, minsize=60)
        self.header_frame.grid_columnconfigure(6, minsize=40)
        
        ctk.CTkLabel(self.header_frame, text="Action Type", font=ctk.CTkFont(size=11, weight="bold"), text_color="gray70").grid(row=0, column=0, sticky="w", padx=5)
        ctk.CTkLabel(self.header_frame, text="Key / Button", font=ctk.CTkFont(size=11, weight="bold"), text_color="gray70").grid(row=0, column=1, sticky="w", padx=5)
        ctk.CTkLabel(self.header_frame, text="X Coord", font=ctk.CTkFont(size=11, weight="bold"), text_color="gray70").grid(row=0, column=2, sticky="w", padx=5)
        ctk.CTkLabel(self.header_frame, text="Y Coord", font=ctk.CTkFont(size=11, weight="bold"), text_color="gray70").grid(row=0, column=3, sticky="w", padx=5)
        ctk.CTkLabel(self.header_frame, text="Delay (s)", font=ctk.CTkFont(size=11, weight="bold"), text_color="gray70").grid(row=0, column=4, sticky="w", padx=5)
        ctk.CTkLabel(self.header_frame, text="Test", font=ctk.CTkFont(size=11, weight="bold"), text_color="gray70").grid(row=0, column=5, sticky="w", padx=5)
        ctk.CTkLabel(self.header_frame, text="Remove", font=ctk.CTkFont(size=11, weight="bold"), text_color="gray70").grid(row=0, column=6, sticky="w", padx=5)

        # The Scrollable Container for Rows
        self.scroll_container = ctk.CTkScrollableFrame(self.main_frame, label_text="Macro Action List")
        self.scroll_container.grid(row=2, column=0, padx=20, pady=10, sticky="nsew")

        # Override window close protocol
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        # Start persistent global keyboard listener for hotkeys and recording
        self.keyboard_listener = p.keyboard.Listener(
            on_press=self.on_key_press,
            on_release=self.on_key_release
        )
        self.keyboard_listener.start()

    def update_status(self, text, success=False, error=False):
        def _update():
            color = "#00c896"
            if error:
                color = "#ff4f4f"
            elif not success and text == "Idle":
                color = "#00c896"
            elif not success:
                color = "#3b8ed0"
            self.status_lbl.configure(text=text, text_color=color)
        self.after(0, _update)

    def set_gui_interactive(self, state: bool):
        for child in self.scroll_container.winfo_children():
            if isinstance(child, MacroStepRow):
                child.set_interactive(state)
        s = "normal" if state else "disabled"
        self.add_click_btn.configure(state=s)
        self.add_key_btn.configure(state=s)
        self.clear_btn.configure(state=s)
        self.loop_checkbox.configure(state=s)
        self.loop_count_entry.configure(state=s)
        self.add_record_btn.configure(state=s)

    def add_step_to_ui(self, action_type, value, x, y, delay):
        new_step = MacroStepRow(
            master=self.scroll_container,
            action_type=action_type,
            value=value,
            x=x,
            y=y,
            delay=delay,
            app_ref=self
        )
        new_step.pack(fill="x", padx=5, pady=2)
        try:
            self.scroll_container._canvas.yview_moveto(1.0)
        except Exception:
            pass

    def add_manual_click_step(self):
        self.add_step_to_ui(action_type="Mouse Click", value="Left", x=500, y=500, delay=0.5)
        self.update_status("Added click step")

    def add_manual_key_step(self):
        self.add_step_to_ui(action_type="Key Press", value="space", x="", y="", delay=0.5)
        self.update_status("Added key step")

    def clear_all_steps(self):
        for child in self.scroll_container.winfo_children():
            if isinstance(child, MacroStepRow):
                child.destroy()
        self.update_status("Cleared all steps")

    # --- Recording Logic ---
    
    def clean_key_name(self, key):
        try:
            if hasattr(key, 'char') and key.char is not None:
                return key.char
        except AttributeError:
            pass
        
        key_name = str(key)
        if key_name.startswith('Key.'):
            key_name = key_name[4:]
        
        key_name = key_name.lower()
        
        # Map suffixes for pyautogui
        if key_name.endswith('_l'):
            key_name = key_name[:-2] + 'left'
        elif key_name.endswith('_r'):
            key_name = key_name[:-2] + 'right'
            
        return key_name

    def on_mouse_click(self, x, y, button, pressed):
        if not self.recording:
            return
            
        # Ignore clicks inside the application window
        win_x = self.winfo_x()
        win_y = self.winfo_y()
        win_w = self.winfo_width()
        win_h = self.winfo_height()
        if win_x <= x <= win_x + win_w and win_y <= y <= win_y + win_h:
            return

        current_time = time.time()
        
        if pressed:
            self.last_mouse_press = (x, y, button, current_time)
        else:
            if self.last_mouse_press and self.last_mouse_press[2] == button:
                press_x, press_y, press_btn, press_time = self.last_mouse_press
                
                # If released quickly at the same position, combine into Mouse Click
                if abs(x - press_x) <= 3 and abs(y - press_y) <= 3 and (current_time - press_time) < 0.4:
                    delay = press_time - self.last_event_time
                    self.last_event_time = current_time
                    btn_name = press_btn.name.capitalize()
                    self.after(0, lambda: self.add_step_to_ui("Mouse Click", btn_name, press_x, press_y, delay))
                else:
                    # Otherwise, record Mouse Down and Mouse Up separately
                    delay1 = press_time - self.last_event_time
                    delay2 = current_time - press_time
                    self.last_event_time = current_time
                    btn_name = press_btn.name.capitalize()
                    self.after(0, lambda: self.add_step_to_ui("Mouse Down", btn_name, press_x, press_y, delay1))
                    self.after(0, lambda: self.add_step_to_ui("Mouse Up", btn_name, x, y, delay2))
                self.last_mouse_press = None

    def on_key_press(self, key):
        # Check hotkeys first
        if key == p.keyboard.Key.f1:
            if not self.recording and not self.playback_running:
                self.after(0, self.start_recording)
            return
            
        if key == p.keyboard.Key.f2:
            if self.recording:
                self.after(0, self.stop_recording)
            return
            
        if key == p.keyboard.Key.f3:
            if not self.recording and not self.playback_running:
                self.after(0, self.start_playback)
            return
            
        if key == p.keyboard.Key.f4:
            if self.playback_running:
                self.after(0, self.stop_playback)
            return

        # Esc key terminates recording/playback as fallback
        if key == p.keyboard.Key.esc:
            if self.recording:
                self.after(0, self.stop_recording)
            elif self.playback_running:
                self.after(0, self.stop_playback)
            return

        if not self.recording:
            return

        cleaned = self.clean_key_name(key)
        if cleaned in self.currently_pressed_keys:
            return # Ignore key repeats
            
        self.currently_pressed_keys.add(cleaned)
        
        current_time = time.time()
        delay = current_time - self.last_event_time
        self.last_event_time = current_time
        
        action_type = "Key Down" if cleaned in MODIFIER_KEYS else "Key Press"
        self.after(0, lambda: self.add_step_to_ui(action_type, cleaned, "", "", delay))

    def on_key_release(self, key):
        if not self.recording:
            return
            
        # Ignore release of control keys
        if key in {p.keyboard.Key.f1, p.keyboard.Key.f2, p.keyboard.Key.f3, p.keyboard.Key.f4, p.keyboard.Key.esc}:
            return
            
        cleaned = self.clean_key_name(key)
        if cleaned in self.currently_pressed_keys:
            self.currently_pressed_keys.remove(cleaned)
            
        if cleaned in MODIFIER_KEYS:
            current_time = time.time()
            delay = current_time - self.last_event_time
            self.last_event_time = current_time
            self.after(0, lambda: self.add_step_to_ui("Key Up", cleaned, "", "", delay))

    def start_recording(self):
        if self.recording:
            return
            
        self.recording = True
        self.currently_pressed_keys = set()
        self.last_mouse_press = None
        self.start_time = time.time()
        self.last_event_time = self.start_time
        
        self.update_recording_buttons()
        self.update_status("Recording (F2 to stop)...")
        
        # Start background mouse listener
        self.mouse_listener = p.mouse.Listener(
            on_click=self.on_mouse_click
        )
        self.mouse_listener.start()

    def stop_recording(self):
        if not self.recording:
            return
            
        self.recording = False
        
        if hasattr(self, 'mouse_listener') and self.mouse_listener:
            self.mouse_listener.stop()
            self.mouse_listener = None
            
        self.update_recording_buttons()
        self.update_status("Idle")

    def update_recording_buttons(self):
        if self.recording:
            self.add_record_btn.configure(state="disabled", fg_color="gray25", text="Recording...")
            self.add_stop_record_btn.configure(state="normal", fg_color="#ff4f4f", text="Stop Recording (F2)")
        else:
            self.add_record_btn.configure(state="normal", fg_color="#b32424", hover_color="#8c1c1c", text="Start Recording (F1)")
            self.add_stop_record_btn.configure(state="disabled", fg_color="gray25", text="Stop Recording (F2)")

    # --- Playback Logic ---

    def start_playback(self):
        if self.playback_running:
            return
            
        self.playback_actions = []
        for child in self.scroll_container.winfo_children():
            if isinstance(child, MacroStepRow):
                self.playback_actions.append(child.get_data())
                
        if not self.playback_actions:
            self.update_status("No actions to play", error=True)
            return
            
        self.playback_running = True
        self.stop_playback_flag = False
        self.update_playback_buttons()
        
        threading.Thread(target=self._playback_loop, daemon=True).start()

    def stop_playback(self):
        self.stop_playback_flag = True
        self.update_status("Stopping playback...")

    def update_playback_buttons(self):
        if self.playback_running:
            self.play_btn.configure(state="disabled", fg_color="gray25", text="Playing...")
            self.stop_play_btn.configure(state="normal", fg_color="#ff4f4f", text="Stop Playback (F4)")
            self.set_gui_interactive(False)
        else:
            self.play_btn.configure(state="normal", fg_color="#2e7d32", hover_color="#1b5e20", text="Play Macro (F3)")
            self.stop_play_btn.configure(state="disabled", fg_color="gray25", text="Stop Playback (F4)")
            self.set_gui_interactive(True)

    def sleep_interruptible(self, seconds):
        start = time.time()
        while time.time() - start < seconds:
            if self.stop_playback_flag:
                break
            time.sleep(0.05)

    def play_action(self, action):
        action_type = action["type"]
        val = action["value"]
        x = action["x"]
        y = action["y"]
        delay = action["delay"]
        
        if delay > 0:
            self.sleep_interruptible(delay)
            
        if self.stop_playback_flag:
            return
            
        if action_type == "Mouse Click":
            if x is not None and y is not None:
                pyautogui.click(x, y, button=val.lower())
        elif action_type == "Mouse Down":
            if x is not None and y is not None:
                pyautogui.mouseDown(x, y, button=val.lower())
        elif action_type == "Mouse Up":
            if x is not None and y is not None:
                pyautogui.mouseUp(x, y, button=val.lower())
        elif action_type == "Mouse Move":
            if x is not None and y is not None:
                pyautogui.moveTo(x, y)
        elif action_type == "Key Press":
            if val.lower() in pyautogui.KEYBOARD_KEYS:
                pyautogui.press(val)
            elif len(val) > 1:
                pyautogui.write(val)
            elif len(val) == 1:
                pyautogui.press(val)
        elif action_type == "Key Down":
            pyautogui.keyDown(val)
        elif action_type == "Key Up":
            pyautogui.keyUp(val)

    def highlight_row(self, index):
        rows = [child for child in self.scroll_container.winfo_children() if isinstance(child, MacroStepRow)]
        for i, row in enumerate(rows):
            if i == index:
                row.configure(fg_color="#1f538d")
            else:
                row.configure(fg_color="gray15")

    def clear_row_highlights(self):
        for child in self.scroll_container.winfo_children():
            if isinstance(child, MacroStepRow):
                child.configure(fg_color="gray15")

    def _playback_loop(self):
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.0
        loop_count = 1
        max_loops = 1
        
        loop_enabled = self.loop_checkbox.get()
        if loop_enabled:
            try:
                max_loops = int(self.loop_count_entry.get().strip())
            except ValueError:
                max_loops = 1
                
        try:
            while not self.stop_playback_flag:
                self.update_status(f"Playing (Loop {loop_count}/{max_loops if loop_enabled else 1})...")
                
                for idx, action in enumerate(self.playback_actions):
                    if self.stop_playback_flag:
                        break
                    
                    self.after(0, lambda i=idx: self.highlight_row(i))
                    self.play_action(action)
                    
                if not loop_enabled:
                    break
                    
                loop_count += 1
                if max_loops > 0 and loop_count > max_loops:
                    break
                    
            if self.stop_playback_flag:
                self.update_status("Playback Stopped", error=True)
            else:
                self.update_status("Playback Finished", success=True)
        except pyautogui.FailSafeException:
            self.update_status("Stopped (Fail-safe)", error=True)
        except Exception as e:
            self.update_status(f"Error: {str(e)}", error=True)
        finally:
            self.playback_running = False
            self.after(0, self.clear_row_highlights)
            self.after(0, self.update_playback_buttons)

    def test_single_step(self, action):
        def _test():
            self.update_status(f"Testing step: {action['type']}...")
            try:
                # Pre-test delay of 0.5s to let the user move their mouse out of the way
                time.sleep(0.5)
                # Keep copy of action but force 0 delay for instant response
                test_action = action.copy()
                test_action["delay"] = 0.0
                self.play_action(test_action)
                self.update_status("Step tested successfully", success=True)
            except pyautogui.FailSafeException:
                self.update_status("Step stopped (Fail-safe)", error=True)
            except Exception as e:
                self.update_status(f"Step test error: {str(e)}", error=True)
        
        threading.Thread(target=_test, daemon=True).start()

    # --- App Cleanup ---

    def on_close(self):
        self.stop_recording()
        self.stop_playback_flag = True
        if hasattr(self, 'keyboard_listener') and self.keyboard_listener:
            self.keyboard_listener.stop()
        self.destroy()


if __name__ == "__main__":
    app = MacroMakerApp()
    app.mainloop()