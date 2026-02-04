import customtkinter as ctk
import fitz  # PyMuPDF
from PIL import Image, ImageTk
from customtkinter import filedialog


INIT_LOAD_PAGE_COUNT = 20

class PDFViewer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.current_doc_pages = []
        self.doc = None

        self.title("Python PDF Pro")
        self.geometry("1000x700")

        # Configure grid layout (1x2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="PDF Reader", font=("Roboto", 20, "bold"))
        self.logo_label.pack(pady=20, padx=10)

        self.open_button = ctk.CTkButton(self.sidebar, text="Open PDF", command=self.inital_load)
        self.open_button.pack(pady=10, padx=20)
        
        self.appearance_label = ctk.CTkLabel(self.sidebar, text="Appearance Mode:", anchor="w")
        self.appearance_label.pack(side="bottom", padx=20, pady=(0, 10))
        
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar, values=["Dark", "Light", "System"],
                                                               command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.pack(side="bottom", padx=20, pady=10)

        # --- MAIN CONTENT AREA ---
        self.content_frame = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.content_frame.bind("<Configure>", lambda e: self.update_scroll_info(), add="+")
        # Also bind to the mousewheel to catch movement
        self.content_frame.bind_all("<MouseWheel>", lambda e: self.update_scroll_info(), add="+")

        
        self.page_images = [] # To keep references to images so they aren't garbage collected

    def change_appearance_mode(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def inital_load(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files","*.pdf")])
        self.doc = None
        for widget in self.content_frame.winfo_children():
                widget.destroy()
        self.page_images.clear()
        self.current_doc_pages = []
        self.doc = fitz.open(file_path)
        pages = self.doc.page_count
        if pages < INIT_LOAD_PAGE_COUNT:
            load_count = pages
        else:
            load_count = INIT_LOAD_PAGE_COUNT
        self.load_pdf(load_count)

    def load_pdf(self,load_count):
        for page_num in range(load_count):
            page = self.doc.load_page(page_num)
            
            # Convert page to an image (Pixmap)
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)) # 1.5x zoom for clarity
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            
            # Convert PIL image to CTkImage for high-DPI scaling
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(pix.width, pix.height))
            self.page_images.append(ctk_img)
            
            # Create a label to display the page
            page_label = ctk.CTkLabel(self.content_frame, image=ctk_img, text="")
            page_label.pack(pady=10)

    def update_scroll_info(self):
        # Get the start and end visibility (0.0 to 1.0)
        top, bottom = self.content_frame._parent_canvas.yview()
        
        # Calculate percentage
        percentage = int(top * 100)
        print(f"value ..... {percentage}")
        self.update()
        
        # Update UI
        #self.pos_label.configure(text=f"Position: {percentage}%")
        
        # Example: Trigger "Load More" at 90%
        #if bottom > 0.9:
        #    self.pos_label.configure(text="Near Bottom!", text_color="orange")

if __name__ == "__main__":
    app = PDFViewer()
    app.mainloop()