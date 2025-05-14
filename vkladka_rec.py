import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import font
from numpy import float64
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import prognoz, joblib, prognoz_сopy
from prognoz_сopy import Model
from tabl import get_tables

# Загрузка данных таблиц
tables = get_tables()

# Глобальные переменные для значений, введенных пользователем
Cr_value = 9.71
Ni_value = 0.2
Mo_value = 0.12
V_value = 0.03
W_value = 0.01
TotalIngotsWeight_value = 49440.0

# Глобальные переменные для виджетов
entry_elements = {}
table_additives = None
columns_additives = [
    'AlBloki', 'AlGran', 'Boksit', 'CaO', 'CaSi', 'CASIfi13', 'Cfi13', 'CoMet', 'Cu', 
    'EPŽŽlindra', 'FeAl', 'FeB', 'FeBŽica', 'FeCrNit', 'FeCrA', 'FeCrC', 'FeCrCSi', 
    'FeCrC51', 'FeMnA', 'FeMnC', 'FeMo', 'FeNbTa', 'FeNbTafi13', 'FeS', 'FeSi', 
    'FeSiZrŽica', 'FeTi', 'FeTifi13', 'FeV', 'FeW72', 'KarboritMleti', 'MnMet', 'NiGran', 
    'NiKatode', 'NiOksid', 'OdpCu', 'Polymox', 'SŽica', 'SiMet', 'SiMn', 'SLAGMAG65B', 
    'KarboritZaVpih', 'Ni90', 'AlŽica', 'Molyquick', 'AlOplašèenaŽica', 'BelaŽlindra', 
    'Kisik', 'KalcijevKarbid', 'WPaketi', 'SintŽlindra'
]

elements = ['Cr', 'Ni', 'Mo', 'V', 'W']

# Загружаем лимиты из Excel (в реальном проекте укажите путь к вашему файлу)
limits_df = pd.read_excel("PQM - podatki za pilotni projekt (OCR12VM) - ENG.xlsx", sheet_name="Table2 (limits)", skiprows=1)
limits_row = limits_df.iloc[0]  # Берем первую строку с лимитами

# Функция для отображения диапазонов лимитов
def show_limits():
    limits_message = (
        f"Cr: {limits_row['Cr_LowerLimit']} - {limits_row['Cr_UpperLimit']}\n"
        f"Ni: {limits_row['Ni_LowerLimit']} - {limits_row['Ni_UpperLimit']}\n"
        f"Mo: {limits_row['Mo_LowerLimit']} - {limits_row['Mo_UpperLimit']}\n"
        f"V: {limits_row['V_LowerLimit']} - {limits_row['V_UpperLimit']}\n"
        f"W: {limits_row['W_LowerLimit']} - {limits_row['W_UpperLimit']}"
    )
    messagebox.showinfo("Element Limits", limits_message)

# Функция для создания рекомендаций
def create_recomendations(tab3):
    global table_additives
    global entry_elements  # доступ к глобальному словарю

    # Создаем фрейм для ввода веществ
    frame_input = tk.Frame(tab3)
    frame_input.pack(fill="x", padx=10, pady=10)

    # Поля ввода для элементов (явное создание каждой переменной)
    global Cr_entry, Ni_entry, Mo_entry, V_entry, W_entry, TotalIngotsWeight_entry
    Cr_entry = tk.Entry(frame_input, width=10, font=("Arial", 12))
    Ni_entry = tk.Entry(frame_input, width=10, font=("Arial", 12))
    Mo_entry = tk.Entry(frame_input, width=10, font=("Arial", 12))
    V_entry = tk.Entry(frame_input, width=10, font=("Arial", 12))
    W_entry = tk.Entry(frame_input, width=10, font=("Arial", 12))
    TotalIngotsWeight_entry = tk.Entry(frame_input, width=10, font=("Arial", 12))

    # Создаем метки для каждого элемента
    tk.Label(frame_input, text="Cr:", font=("Arial", 12)).pack(side="left", padx=5)
    Cr_entry.pack(side="left", padx=5)
    tk.Label(frame_input, text="Ni:", font=("Arial", 12)).pack(side="left", padx=5)
    Ni_entry.pack(side="left", padx=5)
    tk.Label(frame_input, text="Mo:", font=("Arial", 12)).pack(side="left", padx=5)
    Mo_entry.pack(side="left", padx=5)
    tk.Label(frame_input, text="V:", font=("Arial", 12)).pack(side="left", padx=5)
    V_entry.pack(side="left", padx=5)
    tk.Label(frame_input, text="W:", font=("Arial", 12)).pack(side="left", padx=5)
    W_entry.pack(side="left", padx=5)
    tk.Label(frame_input, text="TotalIngotsWeight:", font=("Arial", 12)).pack(side="left", padx=5)
    TotalIngotsWeight_entry.pack(side="left", padx=5)

    # Кнопка для отображения лимитов
    button_limits = tk.Button(frame_input, text="Показать лимиты", command=show_limits, font=("Arial", 12))
    button_limits.pack(side="left", padx=5)

    # Кнопка для обновления таблицы добавок
    button_update = tk.Button(frame_input, text="Обновить добавки", command=update_additives, font=("Arial", 12))
    button_update.pack(side="left", padx=5)

    # Создаем фрейм для таблицы добавок
    frame_additives = tk.Frame(tab3)
    frame_additives.pack(fill="both", expand=True, padx=10, pady=10)

    # Создаем таблицу добавок с возможностью прокрутки
    columns = ['Additive', 'Quantity']
    table_additives = tk.ttk.Treeview(frame_additives, columns=columns, show='headings')
    for col in columns:
        table_additives.heading(col, text=col)
    table_additives.pack(fill="both", expand=True)

def update_additives():
    global Cr_value, Ni_value, Mo_value, V_value, W_value, TotalIngotsWeight_value  # доступ к глобальным переменным
    
    # Очищаем таблицу добавок перед обновлением
    for row in table_additives.get_children():
        table_additives.delete(row)

    # Получаем значения из полей ввода и обновляем глобальные переменные
    Cr_value = get_float_from_entry(Cr_entry, 9.71)
    Ni_value = get_float_from_entry(Ni_entry, 0.2)
    Mo_value = get_float_from_entry(Mo_entry, 0.12)
    V_value = get_float_from_entry(V_entry, 0.03)
    W_value = get_float_from_entry(W_entry, 0.01)
    TotalIngotsWeight_value = get_float_from_entry(TotalIngotsWeight_entry, 49440)

    # Печать значений для отладки
    print(f"Input Data: Cr={Cr_value}, Ni={Ni_value}, Mo={Mo_value}, V={V_value}, W={W_value}, TotalIngotsWeight={TotalIngotsWeight_value}")

    # Загружаем модель
    md = joblib.load('steel_optimizer_model.pkl')
    predictor = Model("PQM - podatki za pilotni projekt (OCR12VM) - ENG.xlsx", md)

    # Формируем начальную композицию на основе введенных значений
    initial_composition = {
        'Cr_Last_EOP': Cr_value,
        'Ni_Last_EOP': Ni_value,
        'Mo_Last_EOP': Mo_value,
        'V_Last_EOP': V_value,
        'W_Last_EOP': W_value,
        'TotalIngotsWeight': TotalIngotsWeight_value,
    }

    # Выводим данные, которые передаются в модель
    print("Input to model:", initial_composition)

    # Предсказание на основе начальной композиции
    prediction = predictor.predict_final_parameters(initial_composition)

    # Проверяем, что вернуло предсказание
    print("Prediction data:", prediction)

    if prediction.empty:
        messagebox.showerror("Ошибка", "Прогнозирование не дало результатов. Проверьте данные и модель.")
    else:
        pd.set_option('display.max_columns', None)
        first_row = prediction.iloc[0]  # Берем первую строку
        first_row = first_row.apply(float64)
        print("Prediction Results:", first_row)

        # Очищаем таблицу добавок перед обновлением
        for row in table_additives.get_children():
            table_additives.delete(row)

        # Заполняем таблицу добавок
        additives = [
            (col, first_row[col]) for col in first_row.index
            if col.startswith("LFVD_") and first_row[col] > 0
        ]
        for item in additives:
            table_additives.insert("", "end", values=item)  # Добавляем строку в таблицу

        predicted_values = first_row[['Cr_Final', 'Ni_Final', 'Mo_Final', 'V_Final', 'W_Final']]
        print("Predicted Values:", predicted_values)

# Функция для безопасного получения числовых значений
def get_float_from_entry(entry, default_value):
    try:
        return float(entry.get())
    except ValueError:
        messagebox.showwarning("Ошибка ввода", f"Некорректное значение, использовано значение по умолчанию: {default_value}")
        return default_value














# import tkinter as tk
# from tkinter import ttk
# import pandas as pd
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import prognoz, joblib
# from prognoz import Model
# from tabl import get_tables

# # Загрузка данных таблиц
# tables = get_tables()

# # Глобальные переменные для виджетов
# entry_elements = {}
# table_additives = None
# columns_additives = [
#     'AlBloki', 'AlGran', 'Boksit', 'CaO', 'CaSi', 'CASIfi13', 'Cfi13', 'CoMet', 'Cu', 
#     'EPŽŽlindra', 'FeAl', 'FeB', 'FeBŽica', 'FeCrNit', 'FeCrA', 'FeCrC', 'FeCrCSi', 
#     'FeCrC51', 'FeMnA', 'FeMnC', 'FeMo', 'FeNbTa', 'FeNbTafi13', 'FeS', 'FeSi', 
#     'FeSiZrŽica', 'FeTi', 'FeTifi13', 'FeV', 'FeW72', 'KarboritMleti', 'MnMet', 'NiGran', 
#     'NiKatode', 'NiOksid', 'OdpCu', 'Polymox', 'SŽica', 'SiMet', 'SiMn', 'SLAGMAG65B', 
#     'KarboritZaVpih', 'Ni90', 'AlŽica', 'Molyquick', 'AlOplašèenaŽica', 'BelaŽlindra', 
#     'Kisik', 'KalcijevKarbid', 'WPaketi', 'SintŽlindra'
# ]

# elements = ['Cr', 'Ni', 'Mo', 'V', 'W']

# # Функция для создания рекомендаций
# def create_recomendations(tab3):
#     global table_additives

#     # Создаем фрейм для ввода веществ
#     frame_input = tk.Frame(tab3)
#     frame_input.pack(fill="x", padx=10, pady=10)

#     # Создаем фрейм для таблицы добавок
#     frame_additives = tk.Frame(tab3)
#     frame_additives.pack(fill="both", expand=True, padx=10, pady=10)

#     # Поля ввода для элементов
#     for element in elements:
#         label_element = tk.Label(frame_input, text=f"{element}:", font=("Arial", 12))
#         label_element.pack(side="left", padx=5)
#         entry_elements[element] = tk.Entry(frame_input, width=10, font=("Arial", 12))
#         entry_elements[element].pack(side="left", padx=5)

#     # Поле для ввода общего веса слитков
#     label_weight = tk.Label(frame_input, text="TotalIngotsWeight:", font=("Arial", 12))
#     label_weight.pack(side="left", padx=5)
#     entry_weight = tk.Entry(frame_input, width=10, font=("Arial", 12))
#     entry_weight.pack(side="left", padx=5)

#     # Кнопка для обновления таблицы добавок
#     button_update = tk.Button(frame_input, text="Обновить добавки", 
#                               command=lambda: update_additives(entry_elements, entry_weight), 
#                               font=("Arial", 12))
#     button_update.pack(side="left", padx=5)

#     # Создаем таблицу добавок с возможностью прокрутки
#     columns = ['Additive', 'Quantity']
#     table_additives = tk.ttk.Treeview(frame_additives, columns=columns, show='headings')
#     for col in columns:
#         table_additives.heading(col, text=col)
#     table_additives.pack(fill="both", expand=True)

#     # Контейнер для графиков
#     frame_grafiki = tk.Frame(tab3)
#     frame_grafiki.pack(fill="both", expand=True, padx=10, pady=10)
    
# def update_additives(entry_elements, entry_weight):
#     # Получаем значения из полей ввода
#     input_data = {}
#     for element in elements:
#         try:
#             value = float(entry_elements[element].get())  # Преобразуем в float
#         except ValueError:
#             value = 0.0  # Если значение не может быть преобразовано в float, используем 0
#         input_data[element] = value

#     # Получаем значение для TotalIngotsWeight
#     try:
#         total_weight = float(entry_weight.get())
#     except ValueError:
#         total_weight = 49440  # Значение по умолчанию, если поле пустое

#     # Печать введенных данных для отладки
#     print("Input Data:", input_data)
#     print("TotalIngotsWeight:", total_weight)

#     # Загружаем модель
#     md = joblib.load('steel_optimizer_model.pkl')
#     predictor = Model("PQM - podatki za pilotni projekt (OCR12VM) - ENG.xlsx", md)
    
#     # Используем значения по умолчанию для начальной композиции
#     initial_composition = {
#         'Cr_Last_EOP': input_data.get('Cr', 9.71),  # Используем значения из полей ввода
#         'Ni_Last_EOP': input_data.get('Ni', 0.2),
#         'Mo_Last_EOP': input_data.get('Mo', 0.12),
#         'V_Last_EOP': input_data.get('V', 0.03),
#         'W_Last_EOP': input_data.get('W', 0.01),
#         'TotalIngotsWeight': total_weight,
#     }

#     # Предсказание на основе введенных данных
#     prediction = predictor.predict_final_parameters(initial_composition)

#     # Печать результата предсказания для отладки
#     print("Prediction:", prediction)

#     if not prediction.empty:
#         pd.set_option('display.max_columns', None)
#         first_row = prediction.iloc[0]  # Берем первую строку результатов
#         first_row = first_row.apply(float)
#         print(first_row)  # Отладочный вывод для проверки данных

#         # Пример: оптимальные добавки (из первой строки)
#         additives = [
#             (col, first_row[col]) for col in first_row.index  # Используем .index для Series
#             if col.startswith("LFVD_") and first_row[col] > 0
#         ]
#         print("Additives:", additives)  # Выводим добавки для отладки

#         if additives:  # Если есть добавки
#             # Заполнение таблицы добавок
#             for item in additives:
#                 table_additives.insert("", "end", values=item)  # Добавляем строки в таблицу
#         else:
#             print("No additives to display.")

#         predicted_values = first_row[['Cr_Final', 'Ni_Final', 'Mo_Final', 'V_Final', 'W_Final']]
#         print(predicted_values)
#     else:
#         print("Prediction is empty.")
