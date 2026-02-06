import customtkinter as ctk
import fitz  # PyMuPDF
from PIL import Image, ImageTk
from customtkinter import filedialog


INIT_LOAD_PAGE_COUNT = 5

class PDFViewer(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.current_doc_pages = []
        self.doc = None
        self.total_pages = 0
        self.title("Python PDF Pro")
        self.placeholders=[]
        #self.geometry("1000x700")

        # Configure grid layout (1x2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # --- LEFT SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="PDF Reader", font=("Roboto", 20, "bold"))
        self.logo_label.pack(pady=20, padx=10)

        self.open_button = ctk.CTkButton(self.sidebar, text="Open PDF", command=self.load_pdf)
        self.open_button.pack(pady=10, padx=20)
        
        self.appearance_label = ctk.CTkLabel(self.sidebar, text="Appearance Mode:", anchor="w")
        self.appearance_label.pack(side="bottom", padx=20, pady=(0, 10))

        # Page Indicator Label
        self.page_label = ctk.CTkLabel(self.sidebar, text="Page: 0 / 0", font=("Roboto", 16))
        self.page_label.pack(pady=20)
        
        self.appearance_mode_optionemenu = ctk.CTkOptionMenu(self.sidebar, values=["Dark", "Light", "System"],command=self.change_appearance_mode)
        self.appearance_mode_optionemenu.pack(side="bottom", padx=20, pady=10)

        # --- MAIN CONTENT AREA ---
        self.content_frame = ctk.CTkScrollableFrame(self, corner_radius=0, fg_color="transparent")
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

       
        self.content_frame.bind_all("<ButtonRelease>", lambda e: self.page_manager(), add="+")
        self.content_frame.bind_all("<Button-4>", lambda e: self.content_frame._parent_canvas.yview("scroll", -1, "units"))
        self.content_frame.bind_all("<Button-5>", lambda e: self.content_frame._parent_canvas.yview("scroll", 1, "units"))
        self.content_frame.bind_all("<Button-4>", lambda e: self.scroll_up(e), add="+")
        self.content_frame.bind_all("<Button-5>", lambda e: self.scroll_down(e), add="+")
        

        self.page_images = [] # To keep references to images so they aren't garbage collected

    def change_appearance_mode(self, new_appearance_mode: str):
        ctk.set_appearance_mode(new_appearance_mode)

    def load_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files","*.pdf")])
        self.doc = None
        for widget in self.content_frame.winfo_children():
                widget.destroy()
        self.page_images.clear()
        self.current_doc_pages = []
        self.doc = fitz.open(file_path)
        _firt_page = self.doc.load_page(0)
        self._pages = []
        w = int(_firt_page.rect.width * 1.5)
        h = int(_firt_page.rect.height * 1.5)
        print(f"hight of a page {h}")
        print(f"width of a page {w}")
        for i in range(5):
            placeholder = ctk.CTkFrame(self.content_frame, width=w, height=h, fg_color="gray20") # Use a visible color for debugging
            placeholder.pack(pady=10)
            placeholder.pack_propagate(False) # This is essential to keep the 'reserved' height
            # Optional: Add a "Loading..." label inside the placeholder
            loading_label = ctk.CTkLabel(placeholder, text=f" page {i+1} is loading...", text_color="gray50")
            loading_label.place(relx=0.5, rely=0.5, anchor="center")    
            self.placeholders.append({
                "frame": placeholder,
                "page_num": i,
                "loaded": False,
                "height": h
            })
        pages = self.doc.page_count
        self.total_pages = pages
        self.load_page(0,self.placeholders[0])
    

    def load_page(self,page_number,place_holder_dic):
        img = self.get_page_as_image(page_number)
        self.create_label_from_img(img,place_holder_dic)

    def get_page_as_image(self,page_num):
        #page = self._pages[page_num]
        page = self.doc.load_page(page_num)
        pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5)) # 1.5x zoom for clarity
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(pix.width, pix.height)) #keeping for future references !!!
        self.page_images.append(ctk_img)
        return ctk_img
    
    def create_label_from_img(self,ctk_img,place_holder_dic):
        frame : ctk.CTkFrame = place_holder_dic["frame"]
        if not frame.winfo_exists():
            print(f" window does not exist....")
        else:
            print(f" status .... {frame.grab_status()}")
            page_label = ctk.CTkLabel(frame, image=ctk_img, text="",fg_color="red")
            print(f" children elements .... {frame.children}")
            page_label.pack(expand=True, fill="both")

    def scroll_down(self,e):
        #self.page_manager()
        pass

    def scroll_up(self,e):
        #self.page_manager()
        pass

    def page_manager(self):
        if self.total_pages > 0:
            # Get the top fraction from the internal canvas
            top_frac, _ = self.content_frame._parent_canvas.yview()
            print(f" top fraction..... {top_frac}")
            # Calculate current page (clamped between 1 and total_pages)
            current_page = int(top_frac * self.total_pages) + 1
            current_page = max(1, min(current_page, self.total_pages))
            self.page_label.configure(text=f"Page: {current_page} / {self.total_pages}")

if __name__ == "__main__":
    app = PDFViewer()
    app.mainloop()