import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk, ImageDraw, ImageFont
import numpy as np
import os
import math

class TrueColorArtGenerator:
    def __init__(self, root):
        self.root = root
        self.root.title("pixel")
        self.root.geometry("1200x900")

        # Setup UI
        self.setup_ui()

        # Simplified emoji palette with widely supported emojis
        self.emoji_palette = self.create_emoji_palette()

        # ASCII characters by density
        self.ascii_chars = "@%#*+=-:. "

        # Font setup
        self.font_path = self.find_font()

        # Current images
        self.image = None
        self.art_image = None

    def create_emoji_palette(self):
        """Create a simplified emoji palette with widely supported emojis."""
        return {
            'red': ["🟥", "🔴", "❤️", "🍎", "🍓"],
            'orange': ["🟧", "🟠", "🧡", "🥕", "🍊"],
            'yellow': ["🟨", "🟡", "💛", "🌟", "🍋"],
            'green': ["🟩", "🟢", "💚", "🌳", "🥝"],
            'blue': ["🟦", "🔵", "💙", "🌊", "🦋"],
            'purple': ["🟪", "🟣", "💜", "🍇", "🔮"],
            'brown': ["🟫", "🟤", "🤎", "🪵", "🍫"],
            'black': ["⬛", "⚫", "🖤", "♠️", "📷"],
            'white': ["⬜", "⚪", "🤍", "☁️", "📄"]
        }

    def find_font(self):
        """Find a font that supports ASCII and preferably emojis."""
        fonts = [
            "Courier New",            # Monospace, ASCII-friendly
            "Consolas",
            "Liberation Mono",
            "DejaVu Sans Mono",
            "NotoEmoji-Regular.ttf",  # Emoji support, place in script directory
            "seguiemj.ttf"            # Windows emoji font
        ]
        for font in fonts:
            try:
                ImageFont.truetype(font, 12)
                self.status_label.config(text=f"Using font: {font}")
                return font
            except:
                continue
        self.status_label.config(text="Warning: No suitable font found, using default (ASCII will be colored, emojis may not render)")
        return None

    def setup_ui(self):
        # Main container
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel - controls and original image
        self.left_frame = ttk.Frame(self.main_frame, width=400)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Right panel - output
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Setup UI components
        self.setup_controls()
        self.setup_image_display()
        self.setup_art_display()

        # Status label for font and processing feedback
        self.status_label = ttk.Label(self.left_frame, text="Ready", font=("Arial", 10))
        self.status_label.pack(pady=5)

    def setup_controls(self):
        """Create control widgets."""
        control_frame = ttk.Frame(self.left_frame)
        control_frame.pack(fill=tk.X, pady=5)

        # Load button
        ttk.Button(control_frame, text="Load Image", command=self.load_image).pack(fill=tk.X, pady=5)

        # Output mode selection
        self.output_mode = tk.StringVar(value="hybrid")
        mode_frame = ttk.Frame(control_frame)
        mode_frame.pack(fill=tk.X, pady=5)
        ttk.Label(mode_frame, text="Mode:").pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text="Emoji", variable=self.output_mode, value="emoji").pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text="ASCII", variable=self.output_mode, value="ascii").pack(side=tk.LEFT)
        ttk.Radiobutton(mode_frame, text="Hybrid", variable=self.output_mode, value="hybrid").pack(side=tk.LEFT)

        # Size controls
        ttk.Label(control_frame, text="Output Width:").pack(anchor=tk.W)
        self.width_slider = ttk.Scale(control_frame, from_=20, to=200, value=80, orient=tk.HORIZONTAL)
        self.width_slider.pack(fill=tk.X, pady=5)

        # Font size control
        ttk.Label(control_frame, text="Font Size:").pack(anchor=tk.W)
        self.font_slider = ttk.Scale(control_frame, from_=6, to=24, value=12, orient=tk.HORIZONTAL)
        self.font_slider.pack(fill=tk.X, pady=5)

        # Aspect ratio checkbox
        self.keep_aspect = tk.BooleanVar(value=True)
        ttk.Checkbutton(control_frame, text="Maintain Aspect Ratio", variable=self.keep_aspect).pack(anchor=tk.W)

        # Generate button
        ttk.Button(control_frame, text="Generate Art", command=self.generate_art).pack(fill=tk.X, pady=10)

        # Save button
        ttk.Button(control_frame, text="Save Art", command=self.save_art).pack(fill=tk.X, pady=5)

    def setup_image_display(self):
        """Setup original image display."""
        frame = ttk.Frame(self.left_frame)
        frame.pack(fill=tk.BOTH, expand=True, pady=10)
        ttk.Label(frame, text="Original Image").pack()

        self.canvas = tk.Canvas(frame, bg='white', bd=0, highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

    def setup_art_display(self):
        """Setup art display with scrollbars."""
        frame = ttk.Frame(self.right_frame)
        frame.pack(fill=tk.BOTH, expand=True, pady=10)
        ttk.Label(frame, text="Generated Art").pack()

        self.art_canvas = tk.Canvas(frame, bg='white', bd=0, highlightthickness=0)
        self.scroll_x = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.art_canvas.xview)
        self.scroll_y = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.art_canvas.yview)
        self.art_canvas.configure(xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)

        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        self.art_canvas.pack(fill=tk.BOTH, expand=True)

    def load_image(self):
        """Load an image file."""
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
        if file_path:
            try:
                self.image = Image.open(file_path)
                self.display_image()
                self.status_label.config(text="Image loaded successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Couldn't load image: {e}")
                self.status_label.config(text="Error loading image")

    def display_image(self):
        """Display the original image."""
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width() or 400
        canvas_height = self.canvas.winfo_height() or 300

        img = self.image.copy()
        img.thumbnail((canvas_width, canvas_height))

        self.photo = ImageTk.PhotoImage(img)
        self.canvas.create_image(canvas_width//2, canvas_height//2, image=self.photo, anchor=tk.CENTER)

    def get_best_emoji(self, r, g, b):
        """Find the best emoji for the given RGB color."""
        def color_distance(c1, c2):
            r1, g1, b1 = c1
            r2, g2, b2 = c2
            return math.sqrt((r1-r2)**2 + (g1-g2)**2 + (b1-b2)**2)

        emoji_colors = {
            'red': (255, 0, 0),
            'orange': (255, 165, 0),
            'yellow': (255, 255, 0),
            'green': (0, 128, 0),
            'blue': (0, 0, 255),
            'purple': (128, 0, 128),
            'brown': (165, 42, 42),
            'black': (0, 0, 0),
            'white': (255, 255, 255)
        }

        closest_family = min(emoji_colors.keys(), key=lambda k: color_distance((r, g, b), emoji_colors[k]))
        brightness = (0.299*r + 0.587*g + 0.114*b)/255
        emoji_options = self.emoji_palette[closest_family]
        index = int(brightness * (len(emoji_options)-1))
        return emoji_options[index]

    def get_ascii_char(self, brightness):
        """Get ASCII character based on brightness."""
        idx = min(int(brightness * (len(self.ascii_chars)-1)), len(self.ascii_chars)-1)
        return self.ascii_chars[idx]

    def generate_art(self):
        """Generate the art from the loaded image."""
        if not hasattr(self, 'image'):
            messagebox.showwarning("Warning", "Please load an image first!")
            self.status_label.config(text="No image loaded")
            return

        try:
            self.status_label.config(text="Generating art...")
            self.root.update()

            output_width = int(self.width_slider.get())
            font_size = int(self.font_slider.get())
            mode = self.output_mode.get()

            # Calculate output dimensions
            if self.keep_aspect.get():
                aspect = self.image.height / self.image.width
                output_height = int(output_width * aspect)
            else:
                output_height = output_width

            # Resize source image
            img = self.image.resize((output_width, output_height), Image.LANCZOS)
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Create output image
            art_width = output_width * font_size
            art_height = output_height * font_size
            art_img = Image.new('RGB', (art_width, art_height), 'white')
            draw = ImageDraw.Draw(art_img)

            # Load font
            try:
                font = ImageFont.truetype(self.font_path, font_size)
            except:
                font = ImageFont.load_default()
                self.status_label.config(text="Warning: Using default font, ASCII will be colored, emojis may not render")

            # Process each pixel
            pixels = img.load()
            for y in range(output_height):
                for x in range(output_width):
                    r, g, b = pixels[x, y]
                    brightness = (0.299*r + 0.587*g + 0.114*b)/255

                    # Select character based on mode
                    if mode == "emoji":
                        char = self.get_best_emoji(r, g, b)
                    elif mode == "ascii":
                        char = self.get_ascii_char(brightness)
                    else:  # hybrid
                        if brightness > 0.7 or brightness < 0.3:
                            char = self.get_best_emoji(r, g, b)
                        else:
                            char = self.get_ascii_char(brightness)

                    # Draw with original pixel color
                    draw.text(
                        (x*font_size, y*font_size),
                        char,
                        fill=(r, g, b),  # Ensure true color for ASCII and emojis
                        font=font
                    )

            # Display the result
            self.display_art(art_img)
            self.art_image = art_img
            self.status_label.config(text="Art generated successfully, ASCII colored with true colors")

        except Exception as e:
            messagebox.showerror("Error", f"Art generation failed: {e}")
            self.status_label.config(text="Error generating art")

    def display_art(self, art_img):
        """Display the generated art."""
        self.art_canvas.delete("all")
        self.art_photo = ImageTk.PhotoImage(art_img)
        self.art_canvas.create_image(0, 0, image=self.art_photo, anchor=tk.NW)
        self.art_canvas.config(scrollregion=self.art_canvas.bbox("all"))

    def save_art(self):
        """Save the generated art."""
        if not hasattr(self, 'art_image'):
            messagebox.showwarning("Warning", "Generate art first!")
            self.status_label.config(text="No art to save")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[
                ("PNG Image", "*.png"),
                ("JPEG Image", "*.jpg"),
                ("HTML File", "*.html"),
                ("Text File", "*.txt")
            ]
        )

        if file_path:
            try:
                ext = os.path.splitext(file_path)[1].lower()
                if ext == '.html':
                    self.save_as_html(file_path)
                elif ext == '.txt':
                    self.save_as_text(file_path)
                else:
                    self.art_image.save(file_path)
                messagebox.showinfo("Success", "Art saved successfully!")
                self.status_label.config(text="Art saved successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Couldn't save file: {e}")
                self.status_label.config(text="Error saving art")

    def save_as_html(self, file_path):
        """Save as colored HTML document."""
        output_width, output_height = self.art_image.size
        pixels = self.art_image.load()
        font_size = int(self.font_slider.get())
        chars_wide = output_width // font_size
        chars_high = output_height // font_size

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Color Art</title>
    <style>
        body {{
            background: #222;
            color: white;
            font-family: monospace;
            font-size: {font_size}px;
            line-height: 1;
            white-space: pre;
            padding: 20px;
        }}
    </style>
</head>
<body>
"""
        for y in range(0, output_height, font_size):
            line = ""
            for x in range(0, output_width, font_size):
                center_x = min(x + font_size//2, output_width-1)
                center_y = min(y + font_size//2, output_height-1)
                r, g, b = pixels[center_x, center_y]
                hex_color = f"#{r:02x}{g:02x}{b:02x}"
                char = self.get_char_for_cell(x, y, font_size, output_width, output_height, pixels)
                line += f'<span style="color:{hex_color}">{char}</span>'
            html += line + "\n"

        html += "</body>\n</html>"
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html)

    def get_char_for_cell(self, x, y, font_size, max_x, max_y, pixels):
        """Get the appropriate character for a cell."""
        center_x = min(x + font_size//2, max_x-1)
        center_y = min(y + font_size//2, max_y-1)
        r, g, b = pixels[center_x, center_y]
        brightness = (0.299*r + 0.587*g + 0.114*b)/255

        if self.output_mode.get() == "emoji":
            return self.get_best_emoji(r, g, b)
        elif self.output_mode.get() == "ascii":
            return self.get_ascii_char(brightness)
        else:  # hybrid
            if brightness > 0.7 or brightness < 0.3:
                return self.get_best_emoji(r, g, b)
            else:
                return self.get_ascii_char(brightness)

    def save_as_text(self, file_path):
        """Save as plain text (ASCII only)."""
        if self.output_mode.get() == "emoji":
            messagebox.showwarning("Warning", "Cannot save emoji art as plain text!")
            self.status_label.config(text="Cannot save emoji as text")
            return

        output_width, output_height = self.art_image.size
        pixels = self.art_image.load()
        font_size = int(self.font_slider.get())

        text = []
        for y in range(0, output_height, font_size):
            line = []
            for x in range(0, output_width, font_size):
                center_x = min(x + font_size//2, output_width-1)
                center_y = min(y + font_size//2, output_height-1)
                r, g, b = pixels[center_x, center_y]
                brightness = (0.299*r + 0.587*g + 0.114*b)/255
                line.append(self.get_ascii_char(brightness))
            text.append("".join(line))

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(text))

if __name__ == "__main__":
    root = tk.Tk()
    app = TrueColorArtGenerator(root)
    root.mainloop()