import tkinter as tk
from tkinter import ttk
from vkladka_ocenki import create_steelmills_frame
from vkladka_mo import create_ml_frame
from vkladka_osnova import create_chemistry_frame
from vkladka_rec import create_recomendations 

# Основной цикл приложения
root = tk.Tk()
root.title("Цифровой советчик")
root.geometry("1600x900")

# Вкладки
tab_control = ttk.Notebook(root)
tab1 = ttk.Frame(tab_control)
tab_control.add(tab1, text="Аналитические таблицы")

tab_control.pack(expand=1, fill="both")

# Создание интерфейса на вкладке
create_chemistry_frame(tab1)

# Вторая вкладка: Машинное обучение
tab2 = ttk.Frame(tab_control)
tab_control.add(tab2, text="Машинное обучение")

tab_control.pack(expand=1, fill="both")

# Создание интерфейса на вкладке с машинным обучением
create_ml_frame(tab2)

# Третья вкладка: Машинное обучение
tab3 = ttk.Frame(tab_control)
tab_control.add(tab3, text="Рекомендательная подсистема")
tab_control.pack(expand=1, fill="both")
create_recomendations(tab3)

# Добавляем вкладку в приложение
tab4 = ttk.Frame(tab_control)
tab_control.add(tab4, text="Оценка сталеваров")
create_steelmills_frame(tab4)

# Запуск главного цикла приложения
root.mainloop()