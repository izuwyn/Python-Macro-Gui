import customtkinter as ctk

class MacroMakerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Python Macro Studio")
        self.geometry("900x500")

        # Configure grid layout (1x2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- Sidebar Frame ---
        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Macro Maker", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=20)

        self.record_btn = ctk.CTkButton(self.sidebar_frame, text="Start Recording", fg_color="#d32f2f", hover_color="#b71c1c")
        self.record_btn.grid(row=1, column=0, padx=20, pady=10)

        self.play_btn = ctk.CTkButton(self.sidebar_frame, text="Play Macro")
        self.play_btn.grid(row=2, column=0, padx=20, pady=10)

        self.save_btn = ctk.CTkButton(self.sidebar_frame, text="Save Macro", variant="outline")
        self.save_btn.grid(row=3, column=0, padx=20, pady=10)

        # --- Main Content Frame ---
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.label_main = ctk.CTkLabel(self.main_frame, text="Macro Sequence", font=ctk.CTkFont(size=16))
        self.label_main.grid(row=0, column=0, padx=20, pady=(10, 0), sticky="w")

        # Scrollable list for macro steps
        self.step_list = ctk.CTkTextbox(self.main_frame, state="disabled")
        self.step_list.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")

    def update_log(self, message):
        """Helper to add steps to the UI display"""
        self.step_list.configure(state="normal")
        self.step_list.insert("end", f"{message}\n")
        self.step_list.configure(state="disabled")

if __name__ == "__main__":
    app = MacroMakerApp()
    app.mainloop()