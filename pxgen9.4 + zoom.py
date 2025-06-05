import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np
from sklearn.cluster import KMeans
import os
import string

class PixelArtApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎨 Пиксель-арт генератор")
        self.image_path = None
        self.output_path = "output.png"
        self.coloring_path = "coloring_sheet.png"
        self.preview_image_ref = None
        self.abbr_labels = []
        self.color_hex_map = {}
        self.setup_ui()

    def setup_ui(self):
        frame_top = tk.Frame(self.root)
        frame_top.pack(pady=10)

        tk.Button(frame_top, text="📁 Загрузить", command=self.load_image).grid(row=0, column=0, padx=5)

        tk.Label(frame_top, text="Ширина:").grid(row=0, column=1)
        self.grid_width_entry = tk.Entry(frame_top, width=5)
        self.grid_width_entry.insert(0, "50")
        self.grid_width_entry.grid(row=0, column=2)

        tk.Label(frame_top, text="Высота:").grid(row=0, column=3)
        self.grid_height_entry = tk.Entry(frame_top, width=5)
        self.grid_height_entry.insert(0, "50")
        self.grid_height_entry.grid(row=0, column=4)

        tk.Label(frame_top, text="Цветов:").grid(row=0, column=5)
        self.color_count_entry = tk.Entry(frame_top, width=5)
        self.color_count_entry.insert(0, "16")
        self.color_count_entry.grid(row=0, column=6)

        tk.Button(frame_top, text="🔄 Обновить", command=self.update_image).grid(row=0, column=7, padx=5)
        tk.Button(frame_top, text="💾 Сохранить", command=self.save_output).grid(row=0, column=8, padx=5)
        tk.Button(frame_top, text="🎨 Раскраска", command=self.generate_coloring_sheet).grid(row=0, column=9, padx=5)
        tk.Button(frame_top, text="💾 Сохранить раскраску", command=self.save_coloring).grid(row=0, column=10, padx=5)

        tk.Label(self.root, text="ℹ️ Ширина/высота: 5–100, цветов: 2–64. Рекомендуется: 30×30 и 10–20 цветов для баланса качества и читаемости.", fg="gray").pack()

        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(self.canvas_frame, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<MouseWheel>", self.zoom)
        self.canvas.bind("<ButtonPress-1>", self.pan_start)
        self.canvas.bind("<B1-Motion>", self.pan_move)

        self.zoom_factor = 1.0
        self.image_on_canvas = None
        self.image_cache = None

    def load_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.gif")])
        if file_path:
            self.image_path = file_path
            self.update_image()

    def update_image(self):
        if not self.image_path:
            messagebox.showwarning("Предупреждение", "Сначала загрузите изображение.")
            return
        try:
            grid_width = int(self.grid_width_entry.get())
            grid_height = int(self.grid_height_entry.get())
            n_colors = int(self.color_count_entry.get())
            if not (5 <= grid_width <= 100 and 5 <= grid_height <= 100 and 2 <= n_colors <= 64):
                raise ValueError("Ввод вне допустимого диапазона")
            self.generate_pixel_art((grid_width, grid_height), n_colors)
            self.show_preview(self.output_path)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Произошла ошибка:\n{e}")

    def generate_abbreviations(self, n):
        labels = []
        for letter in string.ascii_uppercase:
            for number in range(1, 100):
                labels.append(f"{letter}{number}")
                if len(labels) == n:
                    return labels
        return labels[:n]

    def generate_pixel_art(self, grid_size, n_colors=16):
        original = Image.open(self.image_path).convert("RGB")
        resized = original.resize(grid_size, Image.Resampling.NEAREST)
        pixels = np.array(resized).reshape(-1, 3)

        kmeans = KMeans(n_clusters=n_colors, random_state=0, n_init='auto').fit(pixels)
        clustered_pixels = kmeans.predict(pixels)
        clustered_colors = np.array(kmeans.cluster_centers_, dtype=np.uint8)
        clustered_img = clustered_colors[clustered_pixels].reshape((grid_size[1], grid_size[0], 3))

        abbreviations = self.generate_abbreviations(n_colors)
        self.color_hex_map = {tuple(color): (f'#{color[0]:02X}{color[1]:02X}{color[2]:02X}', abbr) for color, abbr in zip(clustered_colors, abbreviations)}

        fig, ax = plt.subplots(figsize=(grid_size[0] + 6, grid_size[1] + 3))
        ax.set_xlim(0, grid_size[0] + 6)
        ax.set_ylim(-2, grid_size[1] + 2)
        ax.axis('off')

        for y in range(grid_size[1]):
            for x in range(grid_size[0]):
                rgb = clustered_img[y, x]
                ax.add_patch(patches.Rectangle((x, grid_size[1] - y - 1), 1, 1, linewidth=0, facecolor=np.array(rgb)/255))

        for i, color in enumerate(clustered_colors):
            y_pos = grid_size[1] - i
            hex_color, label = self.color_hex_map[tuple(color)]
            ax.add_patch(patches.Rectangle((grid_size[0] + 1, y_pos), 2, 1.5, edgecolor="black", facecolor=np.array(color)/255))
            ax.text(grid_size[0] + 3.4, y_pos + 0.75, f"{hex_color} ({label})", fontsize=14, ha='left', va='center')

        ax.text(grid_size[0] / 2, -1.5, f"Размер: {grid_size[0]}×{grid_size[1]}, цветов: {len(clustered_colors)}",
                fontsize=14, ha='center', va='center', color='black')

        plt.tight_layout()
        plt.savefig(self.output_path, dpi=150)
        plt.close()

        self.clustered_img = clustered_img
        self.grid_size = grid_size
        self.original_img = original.resize(grid_size, Image.Resampling.NEAREST)

    def generate_coloring_sheet(self):
        if not hasattr(self, 'clustered_img'):
            messagebox.showerror("Ошибка", "Сначала сгенерируйте пиксель-арт.")
            return

        grid_w, grid_h = self.grid_size
        gray_img = self.original_img.convert('L')
        gray_np = np.array(gray_img)/255.0

        fig, ax = plt.subplots(figsize=(grid_w + 2, grid_h + 2))
        ax.set_xlim(0, grid_w)
        ax.set_ylim(0, grid_h)
        ax.axis('off')

        for y in range(grid_h):
            for x in range(grid_w):
                color = self.clustered_img[y, x]
                _, label = self.color_hex_map[tuple(color)]
                brightness = gray_np[y, x]
                ax.add_patch(patches.Rectangle((x, grid_h - y - 1), 1, 1, edgecolor='gray', facecolor=(brightness, brightness, brightness, 0.3)))
                ax.text(x + 0.5, grid_h - y - 0.5, label, fontsize=10, ha='center', va='center', color='black')

        plt.tight_layout()
        plt.savefig(self.coloring_path, dpi=150)
        plt.close()
        self.show_preview(self.coloring_path)

    def show_preview(self, path):
        img = Image.open(path)
        self.image_cache = img.copy()
        self.update_canvas()

    def update_canvas(self):
        if self.image_cache:
            zoomed = self.image_cache.resize((int(self.image_cache.width * self.zoom_factor), int(self.image_cache.height * self.zoom_factor)), Image.Resampling.LANCZOS)
            self.tk_img = ImageTk.PhotoImage(zoomed)
            self.canvas.delete("all")
            self.image_on_canvas = self.canvas.create_image(0, 0, anchor="nw", image=self.tk_img)
            self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def zoom(self, event):
        scale = 1.1 if event.delta > 0 else 0.9
        self.zoom_factor = max(0.1, min(5.0, self.zoom_factor * scale))
        self.update_canvas()

    def pan_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def pan_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def save_output(self):
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if path:
            try:
                Image.open(self.output_path).save(path)
                messagebox.showinfo("Готово", f"Изображение сохранено:\n{path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{e}")

    def save_coloring(self):
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if path:
            try:
                Image.open(self.coloring_path).save(path)
                messagebox.showinfo("Готово", f"Раскраска сохранена:\n{path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить раскраску:\n{e}")

if __name__ == '__main__':
    root = tk.Tk()
    app = PixelArtApp(root)
    root.mainloop()
