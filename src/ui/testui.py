import customtkinter as ctk

class RealTimeScrollApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("500x400")
        self.title("Scroll Position Tracker")

        # Sidebar for info
        self.sidebar = ctk.CTkFrame(self, width=150)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)

        self.pos_label = ctk.CTkLabel(self.sidebar, text="Position: 0%")
        self.pos_label.pack(pady=20)

        # Scrollable Frame
        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Add content to make it scrollable
        for i in range(100):
            ctk.CTkLabel(self.scroll_frame, text=f"PDF Content Line {i}").pack()

        # BINDING THE SCROLL EVENT
        # We bind to the canvas and the scrollbar
        self.scroll_frame._parent_canvas.bind("<Configure>", lambda e: self.update_scroll_info())
        
        # Also bind to the mousewheel to catch movement
        self.scroll_frame.bind("<B1-Motion>", lambda e: self.update_scroll_info())

    def update_scroll_info(self):
        # Get the start and end visibility (0.0 to 1.0)
        top, bottom = self.scroll_frame._parent_canvas.yview()
        
        # Calculate percentage
        percentage = int(top * 100)
        
        # Update UI
        self.pos_label.configure(text=f"Position: {percentage}%")
        
        # Example: Trigger "Load More" at 90%
        if bottom > 0.9:
            self.pos_label.configure(text="Near Bottom!", text_color="orange")

if __name__ == "__main__":
    app = RealTimeScrollApp()
    app.mainloop()