import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw
import cv2  # OpenCV를 사용하기 위해 추가


class ImageAnnotator(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Image Annotator")
        self.geometry("800x600")

        self.canvas = tk.Canvas(self, bg='white')
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.image = None
        self.tk_image = None
        self.cap = None
        self.camera_active = False

        # Bind mouse events
        self.canvas.bind("<Button-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

        self.start_x = None
        self.start_y = None
        self.rect_ids = []

        # Load image button
        load_button = tk.Button(self, text="Load Image", command=self.load_image)
        load_button.pack()

        # Camera / Take Photo button
        self.camera_button = tk.Button(self, text="Camera", command=self.toggle_camera)
        self.camera_button.pack()

        # Save image button
        save_button = tk.Button(self, text="Save Image", command=self.save_image)
        save_button.pack()

    def load_image(self):
        if self.cap:
            self.cap.release()
            self.camera_active = False
            self.camera_button.config(text="Camera")

        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        if file_path:
            image = Image.open(file_path)
            self.display_image(image)

    def toggle_camera(self):
        if not self.camera_active:
            # 카메라 시작
            self.start_camera()
            self.camera_button.config(text="Take Photo")
        else:
            # 사진 촬영
            self.take_photo()
            self.camera_button.config(text="Camera")

    def start_camera(self):
        self.cap = cv2.VideoCapture(0)  # 기본 카메라 사용
        if not self.cap.isOpened():
            messagebox.showerror("Camera Error", "Failed to access camera.")
            return

        self.camera_active = True
        self.update_camera()

    def update_camera(self):
        if self.camera_active:
            ret, frame = self.cap.read()
            if ret:
                # OpenCV 이미지를 Tkinter에 표시하기 위해 변환
                cv2_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                self.image = Image.fromarray(cv2_image)
                self.tk_image = ImageTk.PhotoImage(self.image)
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)

            # 카메라 화면을 계속 갱신
            self.after(10, self.update_camera)

    def take_photo(self):
        if self.camera_active and self.cap:
            self.camera_active = False
            ret, frame = self.cap.read()
            if ret:
                self.cap.release()
                cv2_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                image = Image.fromarray(cv2_image)
                self.display_image(image)

    def display_image(self, image):
        self.tk_image = ImageTk.PhotoImage(image)
        self.canvas.config(width=self.tk_image.width(), height=self.tk_image.height())
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        self.image = image

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y

        # Create a new rectangle
        rect_id = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, fill='white', outline='white')
        self.rect_ids.append(rect_id)

    def on_mouse_drag(self, event):
        if self.start_x and self.start_y:
            # Update the coordinates of the last created rectangle
            self.canvas.coords(self.rect_ids[-1], self.start_x, self.start_y, event.x, event.y)

    def on_button_release(self, event):
        self.start_x = None
        self.start_y = None

    def save_image(self):
        if not self.image:
            messagebox.showwarning("Save Image", "No image loaded.")
            return

        file_path = "image.png"
        
        annotated_image = self.get_canvas_image()
        annotated_image.save(file_path)
        messagebox.showinfo("Save Image", f"Image saved as {file_path}")
            
    def get_canvas_image(self):
        self.update_idletasks()
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Create a copy of the original image
        annotated_image = self.image.copy()
        draw = ImageDraw.Draw(annotated_image)

        # Draw white filled rectangles on the image
        for rect_id in self.rect_ids:
            x1, y1, x2, y2 = self.canvas.coords(rect_id)
            draw.rectangle([x1, y1, x2, y2], fill="white", outline="white")

        return annotated_image

if __name__ == "__main__":
    app = ImageAnnotator()
    app.mainloop()
