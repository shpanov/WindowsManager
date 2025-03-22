import keyboard
import pygetwindow as gw
import pyautogui
import ctypes
import json
import os
import sys
import time
import tkinter as tk
import webbrowser
from pystray import Icon, MenuItem, Menu
from PIL import Image, ImageDraw, ImageTk

# Путь для хранения данных о положении окон
SAVE_FILE = "window_positions.json"

# Функция для загрузки сохраненных данных
def load_window_positions():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r") as file:
            return json.load(file)
    return {}

# Функция для сохранения данных
def save_window_positions(data):
    with open(SAVE_FILE, "w") as file:
        json.dump(data, file)

# Функция для удаления сохраненного положения окна
def delete_window_position():
    # Получаем активное окно
    active_window = gw.getActiveWindow()
    if not active_window:
        print("Не удалось определить активное окно.")
        return

    # Удаляем положение окна, если оно сохранено
    window_positions = load_window_positions()
    if active_window.title in window_positions:
        del window_positions[active_window.title]
        save_window_positions(window_positions)
        print(f"Сохраненное положение окна '{active_window.title}' удалено.")
    else:
        print(f"Для окна '{active_window.title}' нет сохраненного положения.")

# Функция для получения высоты панели задач
def get_taskbar_height():
    user32 = ctypes.windll.user32
    rect = ctypes.wintypes.RECT()
    hwnd = user32.FindWindowW("Shell_TrayWnd", None)
    if hwnd:
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        taskbar_height = rect.bottom - rect.top
        return taskbar_height
    return 0

# Функция для перемещения активного окна в центр экрана
def center_active_window():
    # Получаем активное окно
    active_window = gw.getActiveWindow()
    if not active_window:
        print("Не удалось определить активное окно.")
        return

    # Получаем размеры экрана
    screen_width, screen_height = pyautogui.size()

    # Получаем высоту панели задач
    taskbar_height = get_taskbar_height()

    # Вычисляем координаты для центрирования окна с учетом панели задач
    new_left = (screen_width - active_window.width) // 2
    new_top = (screen_height - taskbar_height - active_window.height) // 2

    # Перемещаем окно
    active_window.moveTo(new_left, max(new_top, 0))

# Функция для сохранения положения окна вручную
def save_window_position():
    # Получаем активное окно
    active_window = gw.getActiveWindow()
    if not active_window:
        print("Не удалось определить активное окно.")
        return

    # Сохраняем положение окна
    window_positions = load_window_positions()
    window_positions[active_window.title] = {"left": active_window.left, "top": active_window.top}
    save_window_positions(window_positions)
    print(f"Положение окна '{active_window.title}' сохранено.")

# Функция для восстановления положения окна
def restore_window_position():
    # Получаем активное окно
    active_window = gw.getActiveWindow()
    if not active_window:
        print("Не удалось определить активное окно.")
        return

    # Загружаем сохраненные положения окон
    window_positions = load_window_positions()

    # Восстанавливаем положение, если оно сохранено
    if active_window.title in window_positions:
        pos = window_positions[active_window.title]
        active_window.moveTo(pos["left"], pos["top"])
        print(f"Положение окна '{active_window.title}' восстановлено.")
    else:
        print(f"Для окна '{active_window.title}' нет сохраненного положения.")

# Функция для отслеживания новых активных окон и восстановления их положения
def monitor_and_restore():
    last_window_title = None
    while True:
        active_window = gw.getActiveWindow()
        if active_window and active_window.title != last_window_title:
            last_window_title = active_window.title
            restore_window_position()
        time.sleep(0.5)  # Задержка для уменьшения нагрузки на процессор

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):  # Проверяем, запущено ли приложение из сборки
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def open_url(event):
    webbrowser.open("https://github.com/shpanov")  # Замените на нужный URL

# Функция для отображения окна "О программе"
def show_about_window():
    about_window = tk.Tk()
    about_window.title("О программе")
    about_window.geometry("560x420")
    about_window.resizable(False, False)

    about_window.iconbitmap(resource_path("logo.ico"))

    image = Image.open(resource_path("logo.ico"))  # Укажите путь к вашему изображению
    image = image.resize((150, 150))  # Изменяем размер изображения
    photo = ImageTk.PhotoImage(image)

    # Создаем холст для иконки
    canvas = tk.Canvas(about_window, width=150, height=150, highlightthickness=0)
    canvas.pack(pady=10)
    canvas.create_image(75, 75, image=photo)  # Размещаем изображение на холсте

    # Добавляем текст под иконкой
    tk.Label(about_window, text="Менеджер окон", font=("Arial", 14, "bold")).pack()
    tk.Label(about_window, text="Программа для управления окнами.", font=("Arial", 12)).pack()
    tk.Label(about_window, text="\nИспользуйте горячие клавиши для управления:\nCtrl+Alt+C — Центрирование текущего окна на экране.\nCtrl+Alt+S — Сохранение текущего положения окна для последующего восстановления.\nCtrl+Alt+R — Восстановление ранее сохраненного положения окна.\nCtrl+Alt+D — Удаление сохраненного положения окна.\nCtrl+Alt+Q — Выход из приложения.", font=("Arial", 10), justify="center").pack()
    tk.Label(about_window, text="\n\nSHPANOV Code © 2025", font=("Arial", 10)).pack()
    link_label = tk.Label(about_window, text="GitHub @SHPANOV", font=("Arial", 10), fg="blue", cursor="hand2")
    link_label.pack()
    link_label.bind("<Button-1>", open_url)  # Привязка события клика к функции open_url

    about_window.mainloop()

# Функция для создания значка в трее
def create_tray_icon():
    def quit_program(icon):
        icon.stop()
        os._exit(0)

    # Создание изображения для иконки
    icon_image = Image.new("RGBA", (128, 128), (255, 255, 255, 0))
    draw = ImageDraw.Draw(icon_image)

    # Рисуем белый квадрат с закругленными углами
    draw.rounded_rectangle((16, 16, 112, 112), radius=20, fill="white")

    # Рисуем увеличенный черный круг по центру
    draw.ellipse((40, 40, 88, 88), fill="black")

    # Создание меню трея
    menu = Menu(
        MenuItem("О программе", lambda: show_about_window()),
        MenuItem("Выход", lambda: quit_program(tray_icon))
    )

    # Создание иконки с подсказкой
    tray_icon = Icon("Window Manager", icon_image, menu=menu, title="Менеджер окон")
    tray_icon.run()

# Назначаем хоткей Ctrl+Alt+C для центрирования окна
keyboard.add_hotkey('ctrl+alt+c', center_active_window)

# Назначаем хоткей Ctrl+Alt+S для сохранения положения окна
keyboard.add_hotkey('ctrl+alt+s', save_window_position)

# Назначаем хоткей Ctrl+Alt+R для восстановления положения окна
keyboard.add_hotkey('ctrl+alt+r', restore_window_position)

# Назначаем хоткей Ctrl+Alt+D для удаления сохраненного положения окна
keyboard.add_hotkey('ctrl+alt+d', delete_window_position)

# Назначаем горячую клавишу для выхода из программы
keyboard.add_hotkey('ctrl+alt+q', lambda: os._exit(0))

print("Программа запущена.")

# Запуск мониторинга окон
import threading

threading.Thread(target=monitor_and_restore, daemon=True).start()

# Запуск значка в трее
create_tray_icon()

# Бесконечный цикл для удержания программы активной
keyboard.wait('ctrl+alt+q')