from msilib.text import tables
import tkinter as tk
from tkinter import ttk
from tabl import get_tables

tables = get_tables()

# Глобальные переменные для виджетов
entry_date = None
entry_heat_no = None
tree_eaf = None
table_limits = None
table_additives = None
table_events = None
text_materials = None
predictions = {}
columns_additives = [
    'AlBloki', 'AlGran', 'Boksit', 'CaO', 'CaSi', 'CASIfi13', 'Cfi13', 'CoMet', 'Cu', 
    'EPŽŽlindra', 'FeAl', 'FeB', 'FeBŽica', 'FeCrNit', 'FeCrA', 'FeCrC', 'FeCrCSi', 
    'FeCrC51', 'FeMnA', 'FeMnC', 'FeMo', 'FeNbTa', 'FeNbTafi13', 'FeS', 'FeSi', 
    'FeSiZrŽica', 'FeTi', 'FeTifi13', 'FeV', 'FeW72', 'KarboritMleti', 'MnMet', 'NiGran', 
    'NiKatode', 'NiOksid', 'OdpCu', 'Polymox', 'SŽica', 'SiMet', 'SiMn', 'SLAGMAG65B', 
    'KarboritZaVpih', 'Ni90', 'AlŽica', 'Molyquick', 'AlOplašèenaŽica', 'BelaŽlindra', 
    'Kisik', 'KalcijevKarbid', 'WPaketi', 'SintŽlindra'
]


# Функция для поиска данных и обновления интерфейса
def search_data():
    date_input = entry_date.get().strip()
    heat_no_input = entry_heat_no.get().strip()

    # Очистка текущих данных в таблицах
    for row in tree_eaf.get_children():
        tree_eaf.delete(row)
    for row in table_limits.get_children():
        table_limits.delete(row)
    for row in table_additives.get_children():
        table_additives.delete(row)
    for row in table_events.get_children():
        table_events.delete(row)
    
    # Очистка текстового поля
    text_materials.delete(1.0, tk.END)

    # Проверка на пустые поля (дата и номер плавки)
    if not date_input and not heat_no_input:
        return  # Если оба поля пусты, ничего не искать

    # Фильтрация данных по дате и/или номеру плавки в таблице "Table1"
    filtered_data = tables.table1[ 
        tables.table1.apply(
            lambda row: (date_input in str(row['Date']) if date_input else True) and 
                        (heat_no_input in str(row['HeatNo']) if heat_no_input else True), axis=1)
    ]

    # Если найдены данные по плавке, фильтруем и другие таблицы
    if not filtered_data.empty:
        heat_nos = filtered_data['HeatNo'].tolist()  # Список подходящих HeatNo

        # Фильтрация данных по "limits" (Table2)
        filtered_limits = tables.table2[tables.table2['HeatNo'].isin(heat_nos)]

        # Фильтрация данных по "recommended additives" (Table4)
        filtered_additives = tables.table4[tables.table4['HeatNo'].isin(heat_nos)]

        # Фильтрация данных по "events" (Table3)
        filtered_events = tables.table3[tables.table3['HeatNo'].isin(heat_nos)]

        # Отображение отфильтрованных данных в таблице "EAF"
        for idx, row in filtered_data.iterrows():
            tree_eaf.insert('', tk.END, 
                            values=(row['Date'], row['HeatNo'], row['Cr_Last_EOP'], 
                                    row['Ni_Last_EOP'], row['Mo_Last_EOP'], 
                                    row['V_Last_EOP'], row['W_Last_EOP']))

        # Отображение отфильтрованных данных в таблице "Limits"
        for idx, row in filtered_limits.iterrows():
            table_limits.insert('', tk.END, values=(
                row['Ni_LowerLimit'], row['Ni_Target'],
                row['Mo_LowerLimit'], row['Mo_Target'],
                row['Cr_LowerLimit'], row['Cr_Target'],
                row['V_LowerLimit'], row['V_Target'],
                row['W_LowerLimit'], row['W_Target']
            ))

        # Отображение отфильтрованных данных в таблице "Recommended additives"
        materials_to_add = "Recommended to add:\n"
        for idx, row in filtered_additives.iterrows():
            values = [row[f'LFVD_{col}'] for col in columns_additives]  # Извлечение данных
            table_additives.insert('', tk.END, values=values)
            
            # Для текста выводим только материалы, где значение больше 0
            for col, val in zip(columns_additives, values):
                if val > 0:  # Проверка на ненулевые значения
                    materials_to_add += f"* {col}: {val}\n"
        
        # Отображаем рекомендации в текстовом поле
        text_materials.insert(tk.END, materials_to_add)

        # Отображение отфильтрованных данных в таблице "Events"
        for idx, row in filtered_events.iterrows():
            table_events.insert('', tk.END, values=(
                row['EventID'], row['LFVDHeatID'], row['EventNo'], row['EventGroupNo'],
                row['EventStart'], row['EventText'], row['HeatNo']
            ))

# Функция для создания интерфейса на первой вкладке
def create_chemistry_frame(tab1):
    global entry_date, entry_heat_no, tree_eaf, table_limits, table_additives, table_events, text_materials

    # Верхний фрейм для поиска
    frame_search = tk.Frame(tab1)
    frame_search.pack(fill="x", padx=10, pady=10)

    # Поля для ввода даты и номера плавки (HeatNo)
    label_date = tk.Label(frame_search, text="Дата:", font=("Arial", 12))
    label_date.pack(side="left", padx=5)
    entry_date = tk.Entry(frame_search, width=15)
    entry_date.pack(side="left", padx=5)
    
    label_heat_no = tk.Label(frame_search, text="Номер плавки (HeatNo):", font=("Arial", 12))
    label_heat_no.pack(side="left", padx=5)
    entry_heat_no = tk.Entry(frame_search, width=15)
    entry_heat_no.pack(side="left", padx=5)
    
    # Кнопка для поиска
    btn_search = tk.Button(frame_search, text="Найти", command=search_data)
    btn_search.pack(side="left", padx=10)
    
    # Основной фрейм для таблиц и других элементов
    frame_main = tk.Frame(tab1)
    frame_main.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Таблица "Chemistry EAF" и "Limits and Finish Data"
    frame_tables = tk.Frame(frame_main)
    frame_tables.pack(fill="both", expand=True)
    
    frame_left = tk.Frame(frame_tables)
    frame_left.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    
    label_eaf = tk.Label(frame_left, text="Chemistry EAF", font=("Arial", 12, 'bold'))
    label_eaf.pack(pady=5)
    
    columns_eaf = ['Date', 'HeatNo', 'Cr_Last_EOP', 'Ni_Last_EOP', 
                'Mo_Last_EOP', 'V_Last_EOP', 'W_Last_EOP']
    tree_eaf = ttk.Treeview(frame_left, columns=columns_eaf, show='headings', height=5)
    
    for col in columns_eaf:
        tree_eaf.heading(col, text=col)
        tree_eaf.column(col, width=80)
    
    tree_eaf.pack(fill="both", expand=True)
    
    # Правый блок с таблицей "Limits"
    frame_right = tk.Frame(frame_tables)
    frame_right.pack(side="right", fill="both", expand=True, padx=10, pady=10)
    
    label_limits = tk.Label(frame_right, text="Limits and Finish Data", font=("Arial", 12))
    label_limits.pack(pady=5)
    
    columns_limits = ['Ni_LowerLimit', 'Ni_Target', 'Mo_LowerLimit', 'Mo_Target', 
                    'Cr_LowerLimit', 'Cr_Target', 'V_LowerLimit', 'V_Target', 
                    'W_LowerLimit', 'W_Target']
    table_limits = ttk.Treeview(frame_right, columns=columns_limits, show="headings", height=5)
    
    for col in columns_limits:
        table_limits.heading(col, text=col)
        table_limits.column(col, width=90)
    
    table_limits.pack(fill="both", expand=True)
    
    # Таблица с "Recommended additives"
    frame_additives = tk.Frame(frame_main)
    frame_additives.pack(fill="both", expand=True, padx=10, pady=10)
    
    label_additives = tk.Label(frame_additives, text="Recommended Additives", font=("Arial", 12))
    label_additives.pack(pady=5)
    
    columns_additives = [
        'AlBloki', 'AlGran', 'Boksit', 'CaO', 'CaSi', 'CASIfi13', 'Cfi13', 'CoMet', 'Cu', 
        'EPŽŽlindra', 'FeAl', 'FeB', 'FeBŽica', 'FeCrNit', 'FeCrA', 'FeCrC', 'FeCrCSi', 
        'FeCrC51', 'FeMnA', 'FeMnC', 'FeMo', 'FeNbTa', 'FeNbTafi13', 'FeS', 'FeSi', 
        'FeSiZrŽica', 'FeTi', 'FeTifi13', 'FeV', 'FeW72', 'KarboritMleti', 'MnMet', 'NiGran', 
        'NiKatode', 'NiOksid', 'OdpCu', 'Polymox', 'SŽica', 'SiMet', 'SiMn', 'SLAGMAG65B', 
        'KarboritZaVpih', 'Ni90', 'AlŽica', 'Molyquick', 'AlOplašèenaŽica', 'BelaŽlindra', 
        'Kisik', 'KalcijevKarbid', 'WPaketi', 'SintŽlindra'
    ]
    table_additives = ttk.Treeview(frame_additives, columns=columns_additives, show="headings", height=5)
    
    for col in columns_additives:
        table_additives.heading(col, text=col)
        table_additives.column(col, width=90)
    
    # Создание горизонтального скроллбара
    scrollbar_x = tk.Scrollbar(frame_additives, orient="horizontal", command=table_additives.xview)
    table_additives.configure(xscrollcommand=scrollbar_x.set)
    
    # Размещение таблицы и скроллбара
    table_additives.pack(fill="both", expand=True)
    scrollbar_x.pack(fill="x", side="bottom", padx=5)
    
    # Фрейм для таблицы и текстового поля
    frame_events_and_text = tk.Frame(frame_main)
    frame_events_and_text.pack(padx=10, pady=10, fill="both", expand=True)
    
    # Фрейм для таблицы
    frame_table = tk.Frame(frame_events_and_text)
    frame_table.pack(side="left", fill="both", expand=True, padx=10)

    # Элементы для отображения таблицы
    label_events = tk.Label(frame_table, text="Events", font=("Arial", 12))
    label_events.pack(pady=5, anchor="w")

    columns_events = ['EventID', 'LFVDHeatID', 'EventNo', 'EventGroupNo', 
                      'EventStart', 'EventText', 'HeatNo']
    table_events = ttk.Treeview(frame_table, columns=columns_events, show="headings", height=5)

    # Настройка столбцов таблицы
    for col in columns_events:
        table_events.heading(col, text=col)
        table_events.column(col, width=90)

    # Размещение таблицы
    table_events.pack(pady=5, fill="both", expand=True)

    # Фрейм для текстового поля
    frame_text = tk.Frame(frame_events_and_text)
    frame_text.pack(side="right", fill="both", expand=True, padx=10)

    # Элементы для текстового поля
    label_materials = tk.Label(frame_text, text="Recommended Materials to Add", font=("Arial", 12))
    label_materials.pack(pady=5, anchor="w")

    text_materials = tk.Text(frame_text, height=8, width=50)
    text_materials.pack(pady=5, fill="both", expand=True)
    
if __name__ == '__main__':
    print("Основа")