import customtkinter as ctk

class MacroStepRow(ctk.CTkFrame):
    """A custom widget representing a single macro action row"""
    def __init__(self, master, action_text, timestamp, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(fg_color="gray20", height=40)
        self.grid_columnconfigure(1, weight=1)

        # Action Icon/Type (e.g., [K] for Key, [M] for Mouse)
        self.type_label = ctk.CTkLabel(self, text=action_text, font=ctk.CTkFont(weight="bold"))
        self.type_label.grid(row=0, column=0, padx=15, pady=5)

        # Details (e.g., 'Left Click at 100, 200')
        self.details_label = ctk.CTkLabel(self, text=f"Executed at {timestamp}s", text_color="gray")
        self.details_label.grid(row=0, column=1, padx=10, pady=5, sticky="w")

        # Edit Button
        self.edit_btn = ctk.CTkButton(self, text="Edit", width=60, height=24, fg_color="#3b8ed0")
        self.edit_btn.grid(row=0, column=2, padx=5)

        # Delete Button
        self.del_btn = ctk.CTkButton(self, text="X", width=30, height=24, fg_color="#a13333", hover_color="#7c2727", command=self.destroy)
        self.del_btn.grid(row=0, column=3, padx=10)

class MacroMakerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Python Macro Studio")
        self.geometry("900x600")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar_frame, text="Controls", font=ctk.CTkFont(size=20, weight="bold")).grid(row=0, column=0, padx=20, pady=20)
        
        # Add Step Button (For testing our UI)
        self.add_test_btn = ctk.CTkButton(self.sidebar_frame, text="Add Manual Step", command=self.add_dummy_step)
        self.add_test_btn.grid(row=1, column=0, padx=20, pady=10)

        # --- Main Macro List ---
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.main_frame, text="Macro Sequence", font=ctk.CTkFont(size=16)).grid(row=0, column=0, padx=20, pady=10, sticky="w")

        # The Scrollable Container for Rows
        self.scroll_container = ctk.CTkScrollableFrame(self.main_frame, label_text="Recorded Actions")
        self.scroll_container.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")

    def add_dummy_step(self):
        """Helper to test the list adding functionality"""
        new_step = MacroStepRow(self.scroll_container, action_text="MOUSE CLICK", timestamp="1.24")
        new_step.pack(fill="x", padx=5, pady=5)

if __name__ == "__main__":
    app = MacroMakerApp()
    app.mainloop()