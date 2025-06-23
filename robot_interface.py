import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import os
import requests
import json

API_URL = "http://192.168.0.104:8000"  # Адрес FastAPI-сервера


def load_settings():
    try:
        with open('settings.json', 'r') as f:
            return json.load(f)
    except:
        return {  # Значения по умолчанию
            'bg_color': '#FFE4E1',
            'text_color': '#8B4513',
            'btn_color': '#FF69B4',
            'num_color': '#FF1493'
        }

class CatQueueApp:
    def __init__(self, root):
        self.settings = load_settings()
        self.root = root
        self.root.title("Chatty Queue")
        self.root.geometry("800x600")
        self.current_frame = None
        self.qr_image_path = "qr_bot.jpg"  # Путь к QR-коду
        self.return_timer = None  # Для хранения ID таймера возврата

        # Проверяем, существует ли файл QR-кода
        if not os.path.exists(self.qr_image_path):
            messagebox.showerror("Ошибка", f"Файл QR-кода не найден: {self.qr_image_path}")
            self.root.destroy()
            return

        self.setup_ui()

    def setup_ui(self):
        self.bg_color = self.settings['bg_color']
        self.btn_color = self.settings['btn_color']
        self.text_color = self.settings['text_color']
        self.num_color = self.settings['num_color']

        # Загружаем QR-код заранее
        try:
            self.qr_image = Image.open(self.qr_image_path)
            self.qr_photo = ImageTk.PhotoImage(self.qr_image.resize((250, 250), Image.LANCZOS))
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить QR-код: {str(e)}")
            self.root.destroy()
            return

        self.show_welcome_frame()

    def clear_frame(self):
        if self.current_frame:
            if self.return_timer:
                self.root.after_cancel(self.return_timer)
                self.return_timer = None
            self.current_frame.pack_forget()
            self.current_frame.destroy()

    def schedule_return(self, delay_seconds=10):
        """Запланировать автоматический возврат на главную страницу"""
        if self.return_timer:
            self.root.after_cancel(self.return_timer)
        self.return_timer = self.root.after(delay_seconds * 1000, self.show_welcome_frame)

    def show_welcome_frame(self):
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, bg=self.bg_color)
        self.current_frame.pack(fill="both", expand=True)

        # Приветственный текст с котиком
        tk.Label(self.current_frame, text="🐱", font=("Arial", 120), bg=self.bg_color, fg=self.text_color).pack(
            pady=(120, 20))
        tk.Label(self.current_frame, text="Добро пожаловать!",
                 font=("Arial", 24, "bold"), bg=self.bg_color, fg=self.text_color).pack(pady=10)

        ttk.Button(self.current_frame, text="Занять очередь", command=self.show_name_frame,
                   style="Pink.TButton").pack(pady=30, ipadx=20, ipady=10)

        # Стиль для кнопок
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Pink.TButton", background=self.btn_color, foreground="black",
                        font=("Arial", 12, "bold"))

        style.map('Pink.TButton',
                  background=[('active', self.btn_color),
                              ('disabled', self.btn_color)],
                  foreground=[('pressed', 'black'),
                              ('active', 'black')])

    def show_name_frame(self):
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, bg=self.bg_color)
        self.current_frame.pack(fill="both", expand=True)

        tk.Label(self.current_frame, text="Как вас зовут?",
                 font=("Arial", 20), bg=self.bg_color, fg=self.text_color).pack(pady=(210, 20))

        self.name_entry = ttk.Entry(self.current_frame, font=("Arial", 14))
        self.name_entry.pack(pady=10, ipadx=50, ipady=8)

        ttk.Button(self.current_frame, text="Продолжить", command=self.show_queue_info,
                   style="Pink.TButton").pack(pady=30, ipadx=20, ipady=10)

    def show_queue_info(self):
        name = self.name_entry.get().strip()
        if not name:
            messagebox.showwarning("Ой!", "Пожалуйста, введите ваше имя")
            return

        try:
            response = requests.post(
                f"{API_URL}/join",
                json={"name": name}
            )
            if response.status_code == 200:
                data = response.json()

                self.clear_frame()
                self.current_frame = tk.Frame(self.root, bg=self.bg_color)
                self.current_frame.pack(fill="both", expand=True)

                tk.Label(self.current_frame, text=f"{name}, ваш номер:",
                         font=("Arial", 20), bg=self.bg_color, fg=self.text_color).pack(pady=(120, 20))

                tk.Label(self.current_frame, text=str(data['user_id']),
                         font=("Arial", 48, "bold"), bg=self.bg_color, fg=self.num_color).pack(pady=10)

                tk.Label(self.current_frame, text=f"Перед вами: {data['position'] - 1} человек",
                         font=("Arial", 14), bg=self.bg_color, fg=self.text_color).pack(pady=20)

                # Кнопка для перехода к QR-коду
                ttk.Button(self.current_frame, text="Узнать об окончании очереди в Telegram",
                           command=self.show_qr_frame,
                           style="Pink.TButton").pack(pady=10, ipadx=20, ipady=10)

                # Кнопка для немедленного возврата
                ttk.Button(self.current_frame, text="Вернуться на главную",
                           command=self.show_welcome_frame,
                           style="Pink.TButton").pack(pady=10, ipadx=20, ipady=10)

                # Автоматический возврат через 10 секунд
                self.schedule_return(10)

            else:
                messagebox.showerror("Ошибка", f"Сервер вернул ошибку: {response.text}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось подключиться к серверу: {e}")

    def show_qr_frame(self):
        self.clear_frame()
        self.current_frame = tk.Frame(self.root, bg=self.bg_color)
        self.current_frame.pack(fill="both", expand=True)

        tk.Label(self.current_frame, text="Отсканируйте QR-код\nчтобы подключиться к боту",
                 font=("Arial", 16), bg=self.bg_color, fg=self.text_color).pack(pady=(80, 20))

        # Показываем заранее загруженный QR-код
        tk.Label(self.current_frame, image=self.qr_photo, bg=self.bg_color).pack(pady=10)

        tk.Label(self.current_frame, text="@chatty_queue_bot",
                 font=("Arial", 14), bg=self.bg_color, fg=self.text_color).pack(pady=10)

        # Кнопка для немедленного возврата
        ttk.Button(self.current_frame, text="Вернуться на главную",
                   command=self.show_welcome_frame,
                   style="Pink.TButton").pack(pady=20, ipadx=20, ipady=10)

        # Автоматический возврат через 10 секунд
        self.schedule_return(20)


if __name__ == "__main__":
    root = tk.Tk()
    app = CatQueueApp(root)
    root.mainloop()
