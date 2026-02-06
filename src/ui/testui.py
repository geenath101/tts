import customtkinter as ctk
import fitz  # PyMuPDF
from PIL import Image
from tkinter import filedialog

class PDFVirtualViewer(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # 1. The Virtual State
        self.total_pages = 950
        self.current_top_index = 0
        self.visible_count = 10  # How many pages we show at once
        self.page_height = 800   # Fixed height for placeholders
        
        # 2. Main Layout
        self.content_area = ctk.CTkFrame(self)
        self.content_area.pack(side="left", fill="both", expand=True)
        
        # 3. The Standalone Scrollbar
        self.v_scroll = ctk.CTkScrollbar(self, command=self.on_scroll_manual)
        self.v_scroll.pack(side="right", fill="y")
        
        # 4. Create the Reusable Pool
        self.page_widgets = []
        for i in range(self.visible_count):
            f = ctk.CTkFrame(self.content_area, height=60, width=600)
            f.pack(pady=5, fill="x")
            f.pack_propagate(False)
            
            lbl = ctk.CTkLabel(f, text="...")
            lbl.place(relx=0.5, rely=0.5, anchor="center")
            
            self.page_widgets.append({"frame": f, "label": lbl})

        self.content_area.bind("<Button-4>", lambda e: self.nudge_scroll(-1))
        self.content_area.bind("<Button-5>", lambda e: self.nudge_scroll(1))

    def on_scroll_manual(self, *args):
        # args[1] is the fraction (0.0 to 1.0)
        fraction = float(args[1])

        # Calculate which page should be at the top
        new_top = int(fraction * (self.total_pages - self.visible_count))

        if new_top != self.current_top_index:
            self.current_top_index = new_top
            self.refresh_view()

    def refresh_view(self):
        for i in range(self.visible_count):
            actual_page_num = self.current_top_index + i
            if actual_page_num < self.total_pages:
                # Update the label with a new image
                self.update_page_image(actual_page_num, self.page_widgets[i])


    def nudge_scroll(self, direction):
    # Calculate how much 1 "scroll click" represents in percentage
        step = 1.0 / self.total_pages
        current_pos = self.v_scroll.get()[0]
        new_pos = max(0, min(1, current_pos + (direction * step)))

        # Set the scrollbar and trigger the update
        self.v_scroll.set(new_pos, new_pos + (self.visible_count / self.total_pages))
        self.on_scroll_manual("moveto", new_pos)
    
if __name__ == "__main__":
    app = PDFVirtualViewer()
    app.mainloop()