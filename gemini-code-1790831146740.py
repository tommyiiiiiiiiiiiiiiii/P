import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from PIL import Image
from google import genai
from google.genai import types

# Set modern UI theme
ctk.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class PocketSmartAI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("PocketSmart AI: Smart Budget & Recommendation")
        self.geometry("900x700")
        self.minsize(800, 600)
        
        self.client = None
        self.image_path = None

        # --- Top Frame (API Key & Title) ---
        self.top_frame = ctk.CTkFrame(self, corner_radius=0)
        self.top_frame.pack(side="top", fill="x", pady=10)
        
        self.title_label = ctk.CTkLabel(self.top_frame, text="PocketSmart AI", font=ctk.CTkFont(size=24, weight="bold"))
        self.title_label.pack(side="left", padx=20)
        
        self.api_key_entry = ctk.CTkEntry(self.top_frame, placeholder_text="Enter Google Gemini API Key", show="*", width=250)
        self.api_key_entry.pack(side="left", padx=10)
        
        self.connect_btn = ctk.CTkButton(self.top_frame, text="Connect to AI", command=self.connect_api)
        self.connect_btn.pack(side="left", padx=10)

        # --- Tabview for Planners ---
        self.tabview = ctk.CTkTabview(self, width=850, height=300)
        self.tabview.pack(padx=20, pady=10, fill="x")
        
        self.tab_home = self.tabview.add("Home Interior")
        self.tab_party = self.tabview.add("Party Planner")
        self.tab_jewelry = self.tabview.add("Jewelry Planner")
        
        self.setup_home_tab()
        self.setup_party_tab()
        self.setup_jewelry_tab()

        # --- Output Frame ---
        self.output_frame = ctk.CTkFrame(self)
        self.output_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.output_label = ctk.CTkLabel(self.output_frame, text="AI Recommendations:", font=ctk.CTkFont(weight="bold"))
        self.output_label.pack(anchor="w", padx=10, pady=5)
        
        self.textbox = ctk.CTkTextbox(self.output_frame, wrap="word", font=ctk.CTkFont(size=14))
        self.textbox.pack(padx=10, pady=10, fill="both", expand=True)

    def connect_api(self):
        api_key = self.api_key_entry.get().strip()
        if not api_key:
            messagebox.showwarning("Warning", "Please enter your Gemini API Key")
            return
        try:
            self.client = genai.Client(api_key=api_key)
            messagebox.showinfo("Success", "Connected to Gemini AI Successfully!")
            self.connect_btn.configure(text="Connected", fg_color="green", state="disabled")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {e}")

    # ========================== HOME TAB ==========================
    def setup_home_tab(self):
        # Budget
        ctk.CTkLabel(self.tab_home, text="Total Budget ($):").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.home_budget = ctk.CTkEntry(self.tab_home, placeholder_text="e.g. 5000")
        self.home_budget.grid(row=0, column=1, padx=10, pady=10)
        
        # Room Type
        ctk.CTkLabel(self.tab_home, text="Room Type:").grid(row=0, column=2, padx=10, pady=10, sticky="e")
        self.home_room = ctk.CTkOptionMenu(self.tab_home, values=["Living Room", "Kitchen", "Bedroom", "Bathroom"])
        self.home_room.grid(row=0, column=3, padx=10, pady=10)

        # Requirements
        ctk.CTkLabel(self.tab_home, text="Requirements (comma separated):").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.home_reqs = ctk.CTkEntry(self.tab_home, placeholder_text="e.g. 2 lights, 1 sofa, 1 rug", width=300)
        self.home_reqs.grid(row=1, column=1, columnspan=3, padx=10, pady=10, sticky="w")
        
        # Button
        ctk.CTkButton(self.tab_home, text="Generate Recommendations", command=self.generate_home).grid(row=2, column=1, columnspan=2, pady=20)

    def generate_home(self):
        if not self.check_client(): return
        budget = self.home_budget.get()
        room = self.home_room.get()
        reqs = self.home_reqs.get()
        
        prompt = (f"You are PocketSmart AI, a smart budget planner. The user wants to decorate their {room} "
                  f"with a budget of ${budget}. They need: {reqs}. "
                  f"Allocate the budget appropriately and recommend cost-effective products from platforms like IKEA and Amazon. "
                  f"Format the output in a clean, readable list balancing functionality, style, and price.")
        self.run_ai_thread(prompt)

    # ========================== PARTY TAB ==========================
    def setup_party_tab(self):
        ctk.CTkLabel(self.tab_party, text="Total Budget ($):").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.party_budget = ctk.CTkEntry(self.tab_party, placeholder_text="e.g. 1000")
        self.party_budget.grid(row=0, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(self.tab_party, text="Event Type:").grid(row=0, column=2, padx=10, pady=10, sticky="e")
        self.party_event = ctk.CTkOptionMenu(self.tab_party, values=["Birthday", "Corporate", "Wedding", "House Party"])
        self.party_event.grid(row=0, column=3, padx=10, pady=10)

        ctk.CTkLabel(self.tab_party, text="Guest Count:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.party_guests = ctk.CTkEntry(self.tab_party, placeholder_text="e.g. 50")
        self.party_guests.grid(row=1, column=1, padx=10, pady=10)

        ctk.CTkButton(self.tab_party, text="Generate Party Plan", command=self.generate_party).grid(row=2, column=1, columnspan=2, pady=20)

    def generate_party(self):
        if not self.check_client(): return
        budget = self.party_budget.get()
        event = self.party_event.get()
        guests = self.party_guests.get()
        
        prompt = (f"You are PocketSmart AI, a smart event budget planner. The user is hosting a {event} "
                  f"for {guests} guests with a budget of ${budget}. "
                  f"Allocate the budget proportionally across catering, decoration, and entertainment. "
                  f"Source realistic options and services available on platforms like Swiggy, Zomato, and OYO for venues. "
                  f"Provide a structured breakdown of the costs.")
        self.run_ai_thread(prompt)

    # ========================== JEWELRY TAB ==========================
    def setup_jewelry_tab(self):
        ctk.CTkLabel(self.tab_jewelry, text="Total Budget ($):").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.jewel_budget = ctk.CTkEntry(self.tab_jewelry, placeholder_text="e.g. 200")
        self.jewel_budget.grid(row=0, column=1, padx=10, pady=10)
        
        ctk.CTkLabel(self.tab_jewelry, text="Occasion:").grid(row=0, column=2, padx=10, pady=10, sticky="e")
        self.jewel_occ = ctk.CTkOptionMenu(self.tab_jewelry, values=["Wedding", "Casual Date", "Formal Dinner", "Festival"])
        self.jewel_occ.grid(row=0, column=3, padx=10, pady=10)

        self.img_lbl = ctk.CTkLabel(self.tab_jewelry, text="Optional Outfit Image: None")
        self.img_lbl.grid(row=1, column=0, columnspan=2, padx=10, pady=10)
        
        ctk.CTkButton(self.tab_jewelry, text="Upload Image", command=self.upload_image).grid(row=1, column=2, padx=10, pady=10)
        ctk.CTkButton(self.tab_jewelry, text="Find Matching Jewelry", command=self.generate_jewelry).grid(row=2, column=1, columnspan=2, pady=20)

    def upload_image(self):
        path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if path:
            self.image_path = path
            filename = os.path.basename(path)
            self.img_lbl.configure(text=f"Outfit Image: {filename}")

    def generate_jewelry(self):
        if not self.check_client(): return
        budget = self.jewel_budget.get()
        occ = self.jewel_occ.get()
        
        prompt = (f"You are PocketSmart AI, a personal stylist. The user is attending a {occ} "
                  f"and has a jewelry budget of ${budget}. Suggest elegant, matching jewelry options "
                  f"from platforms like Amazon and Flipkart tailored to the occasion and budget.")
        
        # Pass image array along with text for Multimodal generation
        contents = [prompt]
        if self.image_path:
            try:
                img = Image.open(self.image_path)
                contents.append(img)
                prompt += " I have attached an image of my outfit. Please analyze the colors and style to recommend jewelry that matches perfectly."
            except Exception as e:
                messagebox.showerror("Image Error", f"Failed to load image: {e}")
                return

        self.run_ai_thread(contents)

    # ========================== AI EXECUTION ==========================
    def check_client(self):
        if not self.client:
            messagebox.showwarning("API Error", "Please connect to the Gemini API first.")
            return False
        return True

    def run_ai_thread(self, contents):
        # Use threading to prevent the UI from freezing during the API call
        self.textbox.delete("1.0", "end")
        self.textbox.insert("end", "Thinking... analyzing your budget and fetching recommendations...")
        
        def call_api():
            try:
                # Utilizing gemini-1.5-flash which has multimodal support and is lightning fast
                response = self.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=contents
                )
                
                # Update UI safely from thread
                self.after(0, lambda: self.textbox.delete("1.0", "end"))
                self.after(0, lambda: self.textbox.insert("end", response.text))
            except Exception as e:
                self.after(0, lambda: self.textbox.delete("1.0", "end"))
                self.after(0, lambda: messagebox.showerror("API Error", str(e)))

        threading.Thread(target=call_api, daemon=True).start()

if __name__ == "__main__":
    app = PocketSmartAI()
    app.mainloop()