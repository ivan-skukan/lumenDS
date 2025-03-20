import tkinter as tk
from tkinter import filedialog, messagebox
import os
import pandas as pd
from PIL import Image, ImageTk

class SkinToneAnnotator:
    def __init__(self, root):
        self.root = root
        self.root.title("Skin Tone Annotator")
        self.root.geometry("800x600")
        self.root.configure(bg="#f4f4f4")
        
        self.dataset_path = None
        self.image_files = []
        self.current_index = 0
        self.annotations = []
        self.annotation_file = "annotations.csv"  # Output file
        
        self.load_melanoma_images()
        
        # Frame for the reference image (left side)
        self.reference_frame = tk.Frame(self.root, bg="#f4f4f4")
        self.reference_frame.pack(side=tk.LEFT, padx=20)
        
        self.reference_image = self.create_skin_tone_reference_image()
        self.reference_label = tk.Label(self.reference_frame, image=self.reference_image)
        self.reference_label.pack()

        # Frame for image and image name (right side)
        self.image_frame = tk.Frame(self.root, bg="#f4f4f4")
        self.image_frame.pack(side=tk.LEFT, padx=20, pady=20)
        
        self.image_label = tk.Label(self.image_frame)
        self.image_label.pack()
        
        self.image_name_label = tk.Label(self.image_frame, text="", font=("Arial", 12, "italic"), bg="#f4f4f4")
        self.image_name_label.pack(pady=10)
        
        # Frame for buttons (below the image)
        self.buttons_frame = tk.Frame(self.root, bg="#f4f4f4")
        self.buttons_frame.pack(pady=20, side=tk.LEFT)
        
        self.tone_buttons = []
        for i in range(1, 7):  # Now only 6 levels
            btn = tk.Button(self.buttons_frame, text=str(i), width=4, height=2, font=("Arial", 12), command=lambda i=i: self.annotate(i), bg="#4CAF50", fg="white", relief="raised")
            btn.pack(side=tk.TOP, padx=5, pady=5)
            self.tone_buttons.append(btn)
        
        self.load_next_image()
        
    def create_skin_tone_reference_image(self):
        """Creates a vertical reference image with 6 skin tones and numbers them."""
        width, height = 50, 60  # Width and height for each block
        num_blocks = 6
        reference_image = Image.new('RGB', (width, height * num_blocks), color='white')
        
        # List of RGB values for 6 skin tones (you can adjust these)
        skin_tones = [
            (255, 220, 185), (255, 180, 140), (255, 150, 110), (240, 120, 85), (210, 90, 60), (170, 70, 45)
        ]
        
        # Draw each skin tone block
        for i, color in enumerate(skin_tones):
            for x in range(width):
                for y in range(i * height, (i + 1) * height):
                    reference_image.putpixel((x, y), color)
        
        # Add numbers on top of each block
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(reference_image)
        try:
            font = ImageFont.truetype("arial.ttf", 20)  # Use a font that works on most systems
        except IOError:
            font = ImageFont.load_default()  # Fallback if the default font is not available
        
        for i in range(6):
            draw.text((10, i * height + 20), str(i + 1), font=font, fill="black")
        
        reference_image = reference_image.resize((width, height * num_blocks))
        return ImageTk.PhotoImage(reference_image)
        
    def load_melanoma_images(self):
        """Loads only melanoma-positive images based on metadata."""
        metadata_path = filedialog.askopenfilename(title="Select Metadata CSV")
        if not metadata_path:
            messagebox.showerror("Error", "No metadata selected.")
            self.root.destroy()
            return
        
        df = pd.read_csv(metadata_path)
        melanoma_df = df[df['target'] == 1]  # Assuming 'target' column marks melanoma cases
        self.image_files = melanoma_df['image_name'].tolist()
        
        folder_path = filedialog.askdirectory(title="Select Image Folder")
        if not folder_path:
            messagebox.showerror("Error", "No folder selected.")
            self.root.destroy()
            return
        
        self.image_files = [os.path.join(folder_path, f + ".jpg") for f in self.image_files]
        
    def load_next_image(self):
        if self.current_index >= len(self.image_files):
            messagebox.showinfo("Done", "All images annotated!")
            self.root.quit()
            return
        
        image_path = self.image_files[self.current_index]
        image = Image.open(image_path)
        image = image.resize((300, 300))
        image = ImageTk.PhotoImage(image)
        
        self.image_label.config(image=image)
        self.image_label.image = image
        
        # Display the image name
        image_name = os.path.basename(self.image_files[self.current_index])
        self.image_name_label.config(text=f"Image: {image_name}")
        
    def annotate(self, tone):
        # Add annotation to the list
        self.annotations.append((os.path.basename(self.image_files[self.current_index]), tone))
        
        # Save annotations to file after every annotation
        self.save_annotations()

        # Move to the next image
        self.current_index += 1
        self.load_next_image()
        
    def save_annotations(self):
        # Create the CSV file if it doesn't exist yet
        if not os.path.exists(self.annotation_file):
            df = pd.DataFrame(self.annotations, columns=["image_name", "skin_tone"])
            df.to_csv(self.annotation_file, index=False)
        else:
            # Append new annotations to the existing CSV file
            df = pd.DataFrame(self.annotations, columns=["image_name", "skin_tone"])
            df.to_csv(self.annotation_file, mode='a', header=False, index=False)
        
        messagebox.showinfo("Saved", "Annotation saved successfully!")
        
if __name__ == "__main__":
    root = tk.Tk()
    app = SkinToneAnnotator(root)
    root.mainloop()
