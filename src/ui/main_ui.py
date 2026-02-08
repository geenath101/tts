import customtkinter as ctk
import fitz
import threading
import logging
from PIL import Image
from customtkinter import filedialog

from src.model.model import AudioModel
from src.model.file_reader import FileReader
from src import application

logger = logging.getLogger(__name__)

class PDFVirtualViewer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("TTS PDF Reader")
        self.geometry("1200x800")
        self.model = AudioModel()
        self.file_reader = FileReader()
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        # --- HEADER ---
        self.header = ctk.CTkFrame(self, corner_radius=0)
        self.header.grid(row=0, column=0, sticky="nsew")
        self.header.grid_columnconfigure(0, weight=1)
        self.header.grid_columnconfigure(1, weight=0)

        self.logo_label = ctk.CTkLabel(
            self.header,
            text="TTS PDF Reader",
            font=("Roboto", 22, "bold"),
        )
        self.logo_label.grid(row=0, column=0, sticky="w", padx=20, pady=12)

        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(
            self.header,
            values=["Dark", "Light", "System"],
            command=self.change_appearance_mode,
            width=140,
        )
        self.appearance_mode_optionemenu.grid(row=0, column=1, padx=20, pady=12)

        # --- BODY ---
        self.body = ctk.CTkFrame(self, corner_radius=0)
        self.body.grid(row=1, column=0, sticky="nsew")
        self.body.grid_columnconfigure(0, weight=0)
        self.body.grid_columnconfigure(1, weight=1)
        self.body.grid_columnconfigure(2, weight=0)
        self.body.grid_rowconfigure(0, weight=1)

        # --- LEFT PANEL ---
        self.sidebar = ctk.CTkFrame(self.body, width=260, corner_radius=12)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(16, 8), pady=16)
        self.sidebar.grid_rowconfigure(5, weight=1)

        self.open_button = ctk.CTkButton(self.sidebar, text="Open PDF", command=self.load_pdf)
        self.open_button.grid(row=0, column=0, padx=16, pady=(20, 10), sticky="ew")

        self.play_button = ctk.CTkButton(self.sidebar, text="Start Audio", command=self.start_audio)
        self.play_button.grid(row=1, column=0, padx=16, pady=8, sticky="ew")

        self.pause_button = ctk.CTkButton(self.sidebar, text="Stop Audio", command=self.stop_audio)
        self.pause_button.grid(row=2, column=0, padx=16, pady=8, sticky="ew")

        self.page_label = ctk.CTkLabel(self.sidebar, text="Page: 0 / 0", font=("Roboto", 16, "bold"))
        self.page_label.grid(row=3, column=0, padx=16, pady=(20, 6), sticky="w")

        self.status_label = ctk.CTkLabel(self.sidebar, text="Status: Idle", font=("Roboto", 13))
        self.status_label.grid(row=4, column=0, padx=16, pady=(0, 16), sticky="w")

        self.file_label = ctk.CTkLabel(
            self.sidebar,
            text="No file selected",
            font=("Roboto", 12),
            justify="left",
            wraplength=220,
        )
        self.file_label.grid(row=6, column=0, padx=16, pady=(0, 16), sticky="w")

        # --- MAIN CONTENT ---
        self.content_area = ctk.CTkFrame(self.body, corner_radius=12)
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=8, pady=16)

        # --- SCROLLBAR ---
        self.v_scroll = ctk.CTkScrollbar(self.body, command=self.on_scroll_manual)
        self.v_scroll.grid(row=0, column=2, sticky="ns", padx=(0, 16), pady=16)

        # Page Indicator Label
        self.current_top_index = 0
        self.visible_count = 1   # Number of pages to show at once
        self.zoom = 1.5

        # 5. Bindings (Linux Mousewheel)
        # We bind to the whole app so scrolling works anywhere
        self.bind_all("<Button-4>", lambda e: self.nudge_scroll(-1))
        self.bind_all("<Button-5>", lambda e: self.nudge_scroll(1))
        
        # 6. Create the Reusable Pool
        self.page_widgets = []
        self.current_pdf_path = None
        self.audio_thread = None
        

    def change_appearance_mode(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def start_audio(self):
        if not self.current_pdf_path:
            return
        if self.audio_thread and self.audio_thread.is_alive():
            logger.debug("thread is already playing")
            return
        start_page = self.current_top_index
        logger.debug("starting audio from page %s", start_page + 1)
        self.status_label.configure(text=f"Status: Playing (page {start_page + 1})")
        file_content = self.file_reader.get_content_as_string(self.doc, start_page=start_page)
        audio_generator = self.model.get_audio_generator(file_content)
        application.start_playback_async(audio_generator)

    def stop_audio(self):
        logger.info("stop audio requested")
        application.stop_playback()
        self.status_label.configure(text="Status: Stopped")

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
        logger.debug("current index: %s", self.current_top_index)
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
        if not file_path:
            return
        self.current_pdf_path = file_path
        self.file_label.configure(text=file_path)
        self.status_label.configure(text="Status: Ready")
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
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("fitz").setLevel(logging.WARNING)

    app = PDFVirtualViewer()
    app.mainloop()