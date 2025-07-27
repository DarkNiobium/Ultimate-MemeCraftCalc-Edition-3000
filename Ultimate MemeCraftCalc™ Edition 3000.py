import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import tkinter as tk
import datetime
import math
import random
import pyttsx3
import matplotlib.pyplot as plt
import numpy as np

class SmartCalculator:
    def __init__(self, root):
        self.root = root
        self.expression = ""
        self.history = []
        self.secret_mode = False
        self.speaker = pyttsx3.init()
        self.style = ttk.Style()
        self.mode = "Обычный"
        self.extra_buttons = []
        self.build_ui()

    def build_ui(self):
        self.root.title("🧠 Умный Калькулятор")

        self.display = ttk.Entry(self.root, font=("Consolas", 20), justify="right")
        self.display.grid(row=0, column=0, columnspan=5, padx=10, pady=5, sticky="nsew")

        self.status_label = ttk.Label(self.root, text="", font=("Consolas", 10), anchor="e")
        self.status_label.grid(row=1, column=0, columnspan=5, sticky="nsew")
        self.update_status()

        self.button_grid = [
            ('7', '8', '9', '/', 'C'),
            ('4', '5', '6', '*', '√'),
            ('1', '2', '3', '-', '^'),
            ('0', '.', '=', '+', '1/x'),
        ]
        self.render_buttons()

        extra_menu = ttk.Menubutton(self.root, text="⚙️ Дополнительно", bootstyle=SECONDARY)
        extra_menu.grid(row=6, column=0, columnspan=2, sticky="nsew", padx=2, pady=2)
        menu = tk.Menu(extra_menu, tearoff=0)
        extra_menu["menu"] = menu

        menu.add_command(label="🎲 Случайное число", command=self.random_number)
        menu.add_command(label="📋 Копировать результат", command=self.copy_result)
        menu.add_command(label="🔈 Озвучить", command=self.speak_result)
        menu.add_command(label="🕘 Время", command=self.show_time)
        menu.add_command(label="🗂️ Показать историю", command=self.show_history)
        menu.add_command(label="📤 Сохранить историю", command=self.save_history)
        menu.add_command(label="🔐 Режим 'Тайна'", command=self.toggle_secret)
        menu.add_command(label="📈 Построить график", command=self.plot_graph)
        menu.add_command(label="🧱 3D Модуль (будущее)", command=self.plan_3d)

        mode_menu = ttk.Menubutton(self.root, text="🧩 Режимы", bootstyle=WARNING)
        mode_menu.grid(row=6, column=2, sticky="nsew", padx=2, pady=2)
        mode = tk.Menu(mode_menu, tearoff=0)
        mode_menu["menu"] = mode
        for m in ["Обычный", "Финансовый", "2D Функции", "Тригонометрия"]:
            mode.add_command(label=m, command=lambda name=m: self.set_mode(name))

        theme_menu = ttk.Menubutton(self.root, text="🎨 Тема", bootstyle=INFO)
        theme_menu.grid(row=6, column=3, sticky="nsew", padx=2, pady=2)
        theme = tk.Menu(theme_menu, tearoff=0)
        theme_menu["menu"] = theme
        for theme_name in self.style.theme_names():
            theme.add_command(label=theme_name, command=lambda t=theme_name: self.style.theme_use(t))

        ttk.Button(self.root, text="🚪 Выход", bootstyle=DANGER, command=self.root.quit).grid(
            row=6, column=4, sticky="nsew", padx=2, pady=2)

        for i in range(7):
            self.root.rowconfigure(i, weight=1)
        for i in range(5):
            self.root.columnconfigure(i, weight=1)

        self.root.bind("<Key>", self.key_press)

    def render_buttons(self):
        for btn in self.extra_buttons:
            btn.destroy()
        self.extra_buttons.clear()

        for r, row in enumerate(self.button_grid):
            for c, char in enumerate(row):
                b = ttk.Button(self.root, text=char, command=lambda ch=char: self.click(ch))
                b.grid(row=r+2, column=c, sticky="nsew", padx=2, pady=2)
                self.extra_buttons.append(b)

        if self.mode == "Финансовый":
            extra = [("USD->UZS", "*12000"), ("EUR->UZS", "*13000"), ("BTC->USD", "*60000")]
        elif self.mode == "2D Функции":
            extra = [("x", "x"), ("sin(x)", "math.sin(x)"), ("cos(x)", "math.cos(x)")]
        elif self.mode == "Тригонометрия":
            extra = [("sin", "math.sin("), ("cos", "math.cos("), ("tan", "math.tan(")]
        else:
            extra = []

        for i, (label, code) in enumerate(extra):
            b = ttk.Button(self.root, text=label, bootstyle=INFO, command=lambda ch=code: self.click(ch))
            b.grid(row=7, column=i, sticky="nsew", padx=2, pady=2)
            self.extra_buttons.append(b)

    def plot_graph(self):
        if self.mode != "2D Функции":
            messagebox.showinfo("Только для режима 2D Функции", "Переключитесь в режим '2D Функции'.")
            return
        expr = self.display.get()
        if "x" not in expr:
            messagebox.showinfo("Ошибка", "Уравнение должно содержать переменную 'x'")
            return
        try:
            x = np.linspace(-10, 10, 400)
            y = eval(expr, {"x": x, "math": math, "np": np, "__builtins__": {}})
            plt.figure("График функции")
            plt.plot(x, y, label=f"y = {expr}")
            plt.grid(True)
            plt.legend()
            plt.show()
        except Exception as e:
            messagebox.showerror("Ошибка построения", str(e))

    def click(self, char):
        if char == "=":
            try:
                expr = self.expression.replace("%", "*0.01")
                result = eval(expr, {"__builtins__": {}}, math.__dict__)
                self.history.append(f"{self.expression} = {result}")
                self.expression = str(result)
                self.update_display()
            except:
                self.display.delete(0, tk.END)
                self.display.insert(0, "Ошибка")
                self.expression = ""
        elif char == "C":
            self.expression = ""
            self.update_display()
        elif char == "√":
            self.expression += "math.sqrt("
            self.update_display()
        elif char == "^":
            self.expression += "**"
            self.update_display()
        elif char == "1/x":
            self.expression = f"1/({self.expression})"
            self.update_display()
        else:
            self.expression += char
            self.update_display()

    def update_display(self):
        self.display.delete(0, tk.END)
        if self.secret_mode:
            self.display.insert(0, "*" * len(self.expression))
        else:
            self.display.insert(0, self.expression)

    def key_press(self, event):
        if event.char in "0123456789+-*/().%":
            self.expression += event.char
            self.update_display()
        elif event.keysym == "Return":
            self.click("=")
        elif event.keysym == "BackSpace":
            self.expression = self.expression[:-1]
            self.update_display()

    def update_status(self):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.status_label.config(text=f"{now}  |  Режим: {self.mode}")
        self.root.after(1000, self.update_status)

    def random_number(self):
        self.expression = str(random.randint(1, 999))
        self.update_display()

    def copy_result(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.display.get())

    def speak_result(self):
        text = self.display.get()
        self.speaker.say("Result is " + text)
        self.speaker.runAndWait()

    def show_time(self):
        now = datetime.datetime.now()
        messagebox.showinfo("Время", now.strftime("%H:%M:%S\n%d.%m.%Y"))

    def show_history(self):
        if not self.history:
            messagebox.showinfo("История", "Нет сохранённой истории.")
        else:
            messagebox.showinfo("История", "\n".join(self.history[-10:]))

    def save_history(self):
        try:
            with open("history.txt", "a", encoding="utf-8") as f:
                f.write("\n".join(self.history[-10:]) + "\n")
            messagebox.showinfo("Успешно", "История сохранена в history.txt")
        except:
            messagebox.showerror("Ошибка", "Не удалось сохранить.")

    def toggle_secret(self):
        self.secret_mode = not self.secret_mode
        self.update_display()

    def plan_3d(self):
        messagebox.showinfo("План 3D", "3D визуализация будет добавлена в будущем обновлении!")

    def set_mode(self, name):
        self.mode = name
        self.update_status()
        self.render_buttons()

if __name__ == "__main__":
    app = ttk.Window(themename="darkly")
    SmartCalculator(app)
    app.state("zoomed")
    app.mainloop()
