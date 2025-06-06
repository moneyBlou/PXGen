# Pixel Art Generator 
Настольная программа, которая позволяет 
превратить любое изображение в пиксель-арт с заданным количеством 
цветов, автоматически создать цветовую палитру, а также сгенерировать 
чёрно-белую раскраску с подписями цветов по пикселям.
  
2. Пример сценария использования
  1. Пользователь загружает изображение.
  2. Устанавливает ширину/высоту сетки (например, 30x30).
  3. Задаёт количество цветов (например, 16).
  4. Нажимает 'Обновить' для генерации пиксель-арта.
  5. Сохраняет результат или создаёт раскраску.
  6. Раскраску можно распечатать и использовать вручную.
   
3. Интерфейс программы
Включает:
- Кнопки: загрузка, обновление, генерация, сохранение.
- Поля ввода: ширина, высота, количество цветов.
- Предпросмотр: отображение цветного результата или раскраски.
- Подсказка: рекомендуемые параметры и диапазоны.
  
4. Ключевые функции кода
- setup_ui: создание интерфейса.
- load_image: загрузка изображения с диска.
- update_image: считывание параметров и запуск генерации.
- generate_pixel_art: масштабирование, кластеризация и отрисовка пиксель-арта.
- generate_coloring_sheet: создание ч/б раскраски с подписями.
- show_preview: отображение изображения в окне.
- save_output / save_coloring: сохранение файлов.
- generate_abbreviations: генерация подписей цветов A1, A2, ...
  
5. Подробности алгоритма кластеризации
Используется алгоритм KMeans из sklearn для группировки всех пикселей
изображения в N кластеров.
Каждый кластерный центр представляет новый цвет.
Пиксели заменяются ближайшими центрами, получая 'основной' цвет.
Это позволяет значительно упростить палитру изображения, сохранив при этом
форму.

6. Ограничения
- Размер сетки: от 5 до 100 по ширине и высоте.
- Количество цветов: от 2 до 64.
- Только латиница для подписей.
- Изображения должны быть в RGB (без прозрачности).
  
7. Рекомендации
- Использовать чёткие и простые изображения.
- Оптимальные значения: 30x30, 10–20 цветов.
- Для печати сохранять PNG с высоким DPI (150+).
- Можно использовать результат в мозаике, вышивке, раскрасках.
  
8. Пример кода функции генерации пиксель-арта
def generate_pixel_art(self, grid_size, n_colors=16):
 original = Image.open(self.image_path).convert("RGB")
 resized = original.resize(grid_size, Image.Resampling.NEAREST)
 pixels = np.array(resized).reshape(-1, 3)
 kmeans = KMeans(n_clusters=n_colors).fit(pixels)
 clustered_colors = np.array(kmeans.cluster_centers_, dtype=np.uint8)
 clustered_img = clustered_colors[kmeans.predict(pixels)].reshape((grid_size[1],
grid_size[0], 3))
Дальнейшая визуализация и сохранение

9. Описание структуры проекта
- main.py: основной исполняемый файл с интерфейсом.
- output.png: цветной результат генерации.
- coloring_sheet.png: файл раскраски.
- requirements.txt: зависимости (numpy, pillow, sklearn, matplotlib).
- resources/: иконки, примеры, обложка и др. (необязательно).
  
10. Возможности расширения
- Экспорт в PDF с палитрой и сеткой.
- Поддержка ввода изображений через drag & drop.
- Настройка размеров предпросмотра.
- Зум и перемещение (уже тестировались).
- Вывод инструкций по каждому цвету (например: «A1 = красный, 12 раз»).
