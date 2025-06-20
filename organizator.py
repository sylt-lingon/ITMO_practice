import tkinter as tk
from tkinter import ttk, colorchooser, messagebox
import json
import os


class RobotQueueOrganizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Организатор Chatty Queue")
        self.root.geometry("1200x800")

        # Загрузка сохранённых настроек
        self.settings_file = "settings.json"
        self.load_settings()

        # Создание виджетов
        self.create_widgets()

    def load_settings(self):
        """Загружает настройки из файла или устанавливает значения по умолчанию"""
        default_settings = {
            "bg_color": "#FFE4E1",
            "text_color": "#8B4513",
            "btn_color": "#FF69B4",
            "num_color": "#FF1493"
        }

        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r') as f:
                self.settings = json.load(f)
            # Проверяем, что все необходимые ключи есть
            for key in default_settings:
                if key not in self.settings:
                    self.settings[key] = default_settings[key]
        else:
            self.settings = default_settings
            self.save_settings()

    def save_settings(self):
        """Сохраняет текущие настройки в файл"""
        with open(self.settings_file, 'w') as f:
            json.dump(self.settings, f, indent=4)

    def create_widgets(self):
        """Создаёт интерфейс организатора"""
        # Панель навигации
        self.nav_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.nav_frame.pack(side="left", fill="y", padx=30, pady=5)

        # Кнопки навигации
        ttk.Button(self.nav_frame, text="Интерфейс очереди",
                   command=self.show_queue_interface).pack(pady=(300, 10), fill="x")
        ttk.Button(self.nav_frame, text="Настройки цветов",
                   command=self.show_settings).pack(pady=10, fill="x")
        ttk.Button(self.nav_frame, text="Выход",
                   command=self.root.quit).pack(pady=10, fill="x")

        # Основная область контента
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(side="right", fill="both", expand=True)

        # Показываем интерфейс очереди по умолчанию
        self.show_queue_interface()

    def show_queue_interface(self):
        """Показывает основной интерфейс очереди"""
        self.clear_content()

        # Основной фрейм с текущими настройками цветов
        frame = tk.Frame(self.content_frame, bg=self.settings["bg_color"])
        frame.pack(fill="both", expand=True)

        # Центральный контент
        center_frame = tk.Frame(frame, bg=self.settings["bg_color"])
        center_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Пример интерфейса очереди
        tk.Label(center_frame, text="Текущий интерфейс очереди",
                 font=("Arial", 24), bg=self.settings["bg_color"],
                 fg=self.settings["text_color"]).pack(pady=20)

        tk.Label(center_frame, text='15',
                 font=("Arial", 48, "bold"), bg=self.settings['bg_color'], fg=self.settings['num_color']).pack(pady=10)

        # Пример кнопки со стилем
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Custom.TButton", background=self.settings['btn_color'], foreground="black",
                        font=("Arial", 12, "bold"))

        style.map('Custom.TButton',
                  background=[('active', self.settings['btn_color']),
                              ('disabled', self.settings['btn_color'])],
                  foreground=[('pressed', 'black'),
                              ('active', 'black')])

        ttk.Button(center_frame, text="Пример кнопки",
                   style="Custom.TButton").pack(pady=20, ipadx=20, ipady=10)

    def show_settings(self):
        """Показывает панель настроек"""
        self.clear_content()

        frame = tk.Frame(self.content_frame)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Заголовок
        tk.Label(frame, text="Настройки внешнего вида",
                 font=("Arial", 20)).pack(pady=(140, 20))

        # Настройка цвета фона
        bg_frame = tk.Frame(frame)
        bg_frame.pack(fill="x", pady=10)
        tk.Label(bg_frame, text="Цвет фона:", font=("Arial", 12)).pack(side='left', padx=(407, 20))
        self.bg_color_btn = tk.Button(bg_frame, text="Выбрать",
                                      bg=self.settings["bg_color"],
                                      command=lambda: self.choose_color("bg_color"))
        self.bg_color_btn.pack(side="left", padx=0)

        # Настройка цвета позиции
        bg_frame = tk.Frame(frame)
        bg_frame.pack(fill="x", pady=10)
        tk.Label(bg_frame, text="Цвет номера:", font=("Arial", 12)).pack(side='left', padx=(393, 20))
        self.num_color_btn = tk.Button(bg_frame, text="Выбрать",
                                      bg=self.settings["num_color"],
                                      command=lambda: self.choose_color("num_color"))
        self.num_color_btn.pack(side="left", padx=0)

        # Настройка цвета текста
        text_frame = tk.Frame(frame)
        text_frame.pack(fill="x", pady=10)
        tk.Label(text_frame, text="Цвет текста:", font=("Arial", 12)).pack(side='left', padx=(400, 20))
        self.text_color_btn = tk.Button(text_frame, text="Выбрать",
                                        bg=self.settings["text_color"],
                                        command=lambda: self.choose_color("text_color"))
        self.text_color_btn.pack(side="left", padx=0)

        # Настройка цвета кнопок
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill="x", pady=10)
        tk.Label(btn_frame, text="Цвет кнопок:", font=("Arial", 12)).pack(side='left', padx=(400, 20))
        self.btn_color_btn = tk.Button(btn_frame, text="Выбрать",
                                       bg=self.settings["btn_color"],
                                       command=lambda: self.choose_color("btn_color"))
        self.btn_color_btn.pack(side="left", padx=0)

        # Кнопка сохранения
        ttk.Button(frame, text="Сохранить настройки",
                   command=self.save_new_settings).pack(pady=30)

        # Кнопка предпросмотра
        ttk.Button(frame, text="Предпросмотр",
                   command=self.show_queue_interface).pack(pady=10)

    def choose_color(self, color_type):
        """Открывает диалог выбора цвета"""
        color = colorchooser.askcolor(title=f"Выберите {color_type}")[1]
        if color:
            self.settings[color_type] = color
            # Обновляем кнопку выбора цвета
            if color_type == "bg_color":
                self.bg_color_btn.config(bg=color)
            elif color_type == "num_color":
                self.num_color_btn.config(bg=color)
            elif color_type == "text_color":
                self.text_color_btn.config(bg=color)
            elif color_type == "btn_color":
                self.btn_color_btn.config(bg=color)

    def save_new_settings(self):
        """Сохраняет новые настройки"""
        try:
            self.save_settings()
            messagebox.showinfo("Сохранено", "Настройки успешно сохранены!")
        except ValueError:
            messagebox.showerror("Ошибка", "Размер QR-кода должен быть числом")

    def clear_content(self):
        """Очищает основную область контента"""
        for widget in self.content_frame.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = RobotQueueOrganizer(root)
    root.mainloop()
