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

        btn_load = tk.Button(frame_top, text="📁 Загрузить", command=self.load_image)
        btn_load.grid(row=0, column=0, padx=5)

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

        btn_update = tk.Button(frame_top, text="🔄 Обновить", command=self.update_image)
        btn_update.grid(row=0, column=7, padx=5)

        btn_save = tk.Button(frame_top, text="💾 Сохранить", command=self.save_output)
        btn_save.grid(row=0, column=8, padx=5)

        btn_coloring = tk.Button(frame_top, text="🎨 Раскраска", command=self.generate_coloring_sheet)
        btn_coloring.grid(row=0, column=9, padx=5)

        btn_save_coloring = tk.Button(frame_top, text="💾 Сохранить раскраску", command=self.save_coloring)
        btn_save_coloring.grid(row=0, column=10, padx=5)

        info_label = tk.Label(self.root, text="ℹ️ Ширина/высота: 5–100, цветов: 2–64. Рекомендуется: 30×30 и 10–20 цветов для баланса качества и читаемости.", fg="gray")
        info_label.pack()

        self.preview_label = tk.Label(self.root)
        self.preview_label.pack(pady=10)

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
        self.color_hex_map = {}
        for i, color in enumerate(clustered_colors):
            hex_color = '#{:02X}{:02X}{:02X}'.format(*color)
            self.color_hex_map[tuple(color)] = (hex_color, abbreviations[i])

        fig, ax = plt.subplots(figsize=(grid_size[0] + 6, grid_size[1] + 3))
        ax.set_xlim(0, grid_size[0] + 6)
        ax.set_ylim(-2, grid_size[1] + 2)
        ax.axis('off')

        for y in range(grid_size[1]):
            for x in range(grid_size[0]):
                rgb = clustered_img[y, x]
                ax.add_patch(patches.Rectangle((x, grid_size[1] - y - 1), 1, 1, linewidth=0, facecolor=np.array(rgb)/255))

        start_x = grid_size[0] + 1
        for i, color in enumerate(clustered_colors):
            y_pos = grid_size[1] - i
            hex_color, label = self.color_hex_map[tuple(color)]
            ax.add_patch(patches.Rectangle((start_x, y_pos), 2, 1.5, linewidth=0.5, edgecolor="black", facecolor=np.array(color)/255))
            ax.text(start_x + 2.3, y_pos + 0.75, f"{hex_color} ({label})", fontsize=16, ha='left', va='center', color='black', fontweight='bold')

        ax.text(grid_size[0] / 2, -1.5, f"Размер: {grid_size[0]}×{grid_size[1]}, цветов: {len(clustered_colors)}",
                fontsize=30, ha='center', va='center', color='black')

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
                ax.add_patch(patches.Rectangle((x, grid_h - y - 1), 1, 1, linewidth=0.5, edgecolor='gray', facecolor=(brightness, brightness, brightness, 0.3)))
                ax.text(x + 0.5, grid_h - y - 0.5, label, fontsize=10, ha='center', va='center', color='black')

        plt.tight_layout()
        plt.savefig(self.coloring_path, dpi=150)
        plt.close()

        self.show_preview(self.coloring_path)

    def show_preview(self, path):
        img = Image.open(path)
        img.thumbnail((500, 500))
        preview_tk = ImageTk.PhotoImage(img)
        self.preview_image_ref = preview_tk
        self.preview_label.config(image=preview_tk)

    def save_output(self):
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if path:
            try:
                img = Image.open(self.output_path)
                img.save(path)
                messagebox.showinfo("Готово", f"Изображение сохранено:\n{path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить:\n{e}")

    def save_coloring(self):
        path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if path:
            try:
                img = Image.open(self.coloring_path)
                img.save(path)
                messagebox.showinfo("Готово", f"Раскраска сохранена:\n{path}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить раскраску:\n{e}")

if __name__ == '__main__':
    root = tk.Tk()
    app = PixelArtApp(root)
    root.mainloop()