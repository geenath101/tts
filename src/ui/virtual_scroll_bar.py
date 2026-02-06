import customtkinter as ctk

import customtkinter as ctk
import fitz
from PIL import Image
from customtkinter import filedialog

class PDFVirtualViewer(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=0)
        self.grid_rowconfigure(0, weight=1)

          # --- LEFT SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        self.logo_label = ctk.CTkLabel(self.sidebar, text="PDF Reader", font=("Roboto", 20, "bold"))
        self.logo_label.pack(pady=20, padx=10)

        self.page_label = ctk.CTkLabel(self.sidebar, text="Page: 0 / 0", font=("Roboto", 16))
        self.page_label.pack(pady=20)

        self.open_button = ctk.CTkButton(self.sidebar, text="Open PDF", command=self.load_pdf)
        self.open_button.pack(pady=10, padx=20)
        
        self.play_button = ctk.CTkButton(self.sidebar, text="Start Audio")
        self.play_button.pack(pady=10, padx=20)

        self.pause_button = ctk.CTkButton(self.sidebar, text="Pause Audio")
        self.pause_button.pack(pady=10, padx=20)

        self.appearance_label = ctk.CTkLabel(self.sidebar, text="Appearance Mode:", anchor="w")
        self.appearance_label.pack(side="bottom", padx=20, pady=(0, 10))

        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar, values=["Dark", "Light", "System"],command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.pack(side="bottom", padx=20, pady=10)

        # Page Indicator Label
        
        self.current_top_index = 0
        self.visible_count = 1   # Number of pages to show at once
        self.zoom = 1.5
        
        # 3. Main Layout
        self.content_area = ctk.CTkFrame(self)
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        # 4. The Standalone Scrollbar
        self.v_scroll = ctk.CTkScrollbar(self, command=self.on_scroll_manual)
        self.v_scroll.grid(row=0, column=2, sticky="ns", padx=(0, 5), pady=10)

        # 5. Bindings (Linux Mousewheel)
        # We bind to the whole app so scrolling works anywhere
        self.bind_all("<Button-4>", lambda e: self.nudge_scroll(-1))
        self.bind_all("<Button-5>", lambda e: self.nudge_scroll(1))
        
        # 6. Create the Reusable Pool
        self.page_widgets = []
        

    def change_appearance_mode(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def get_page_image(self, page_num):
        """Renders or retrieves the image for a specific page."""
        page = self.doc.load_page(page_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(self.zoom, self.zoom))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(pix.width, pix.height))
        return ctk_img


    def refresh_view(self):
        """Updates the images in the fixed frames based on the current index."""
        actual_page_num = self.current_top_index
        print(f" current index ..... {self.current_top_index}")
        if actual_page_num < self.total_pages:
            img = self.get_page_image(actual_page_num)
            self.page_widgets[0]["label"].configure(image=img, text="")
            self.page_widgets[0]["frame"].configure(fg_color="transparent")
        else:
            # Clear frames if we are at the very end of the PDF
            self.page_widgets[0]["label"].configure(image=None, text="")
            self.page_widgets[0]["frame"].configure(fg_color="gray10")

    def on_scroll_manual(self, *args):
        if args[0] == "moveto":
            fraction = float(args[1])
        else:
            return

        # Calculate new top page
        new_top = int(fraction * (self.total_pages - self.visible_count))
        new_top = max(0, min(self.total_pages - self.visible_count, new_top))
        self.page_label.configure(text=f"Page: {new_top + 1} / {self.total_pages}")
        # Update scrollbar thumb size and position
        thumb_size = self.visible_count / self.total_pages
        self.v_scroll.set(fraction, fraction + thumb_size)

        if new_top != self.current_top_index:
            self.current_top_index = new_top
            self.refresh_view()

    def nudge_scroll(self, direction):
        # direction: -1 for up, 1 for down
        # Move by 1 page per scroll tick
        step = 1.0 / (self.total_pages - self.visible_count)
        current_pos = self.v_scroll.get()[0]
        new_pos = max(0, min(1, current_pos + (direction * step)))
        self.on_scroll_manual("moveto", new_pos)

    def load_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files","*.pdf")])
        self.doc = fitz.open(file_path)
        self.total_pages = len(self.doc)
        self.page_height = 1000
        f = ctk.CTkFrame(self.content_area, height=self.page_height, width=600)
        f.pack(pady=10, fill="x")
        f.pack_propagate(False)
        lbl = ctk.CTkLabel(f, text="Loading...")
        lbl.place(relx=0.5, rely=0.5, anchor="center")
        self.page_widgets.append({"frame": f, "label": lbl})
        # Initial Render
        self.refresh_view()

    
       

if __name__ == "__main__":
    app = PDFVirtualViewer()
    app.mainloop()