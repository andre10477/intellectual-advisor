import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
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

# Функция для замены специальных словенских символов на обычные буквы
def slovene_to_ascii(name):
    translation_table = str.maketrans("ČŠŽčšž", "CSZcsz")
    return name.translate(translation_table)

# Создание новой вкладки
def create_steelmills_frame(tab3):
    global entry_heat_no_sm, entry_shift_head_sm, result_text_sm, steelmills_frame, master_name_var, master_name_label

    # Ввод данных для поиска по плавке и начальнику смены
    frame_input = tk.Frame(tab3)
    frame_input.pack(fill="x", padx=10, pady=10)

    label_heat_no_sm = tk.Label(frame_input, text="Номер плавки (HeatNo):", font=("Arial", 12))
    label_heat_no_sm.pack(side="left", padx=5)
    entry_heat_no_sm = tk.Entry(frame_input, width=15)
    entry_heat_no_sm.pack(side="left", padx=5)

    label_shift_head_sm = tk.Label(frame_input, text="Начальник смены:", font=("Arial", 12))
    label_shift_head_sm.pack(side="left", padx=5)
    entry_shift_head_sm = tk.Entry(frame_input, width=15)
    entry_shift_head_sm.pack(side="left", padx=5)

    # Кнопка для построения диаграммы
    button_evaluate = tk.Button(frame_input, text="Построить диаграмму", command=lambda: evaluate_steelmills(entry_heat_no_sm, entry_shift_head_sm))
    button_evaluate.pack(side="left", padx=5)

    # Имя мастера с использованием StringVar для отображения
    master_name_var = tk.StringVar()
    master_name_label = tk.Label(frame_input, textvariable=master_name_var, font=("Arial", 12))
    master_name_label.pack(side="left")

    result_text_sm = tk.StringVar()
    label_result_sm = tk.Label(tab3, textvariable=result_text_sm, font=("Arial", 12))
    label_result_sm.pack(side="top")

    # Контейнер для диаграмм и легенды
    steelmills_frame = tk.Frame(tab3)
    steelmills_frame.pack(fill="both", expand=True)

# Функция для оценки и построения диаграммы
def evaluate_steelmills(entry_heat_no_sm, entry_shift_head_sm):
    heat_no_input = entry_heat_no_sm.get().strip()
    shift_head_input = slovene_to_ascii(entry_shift_head_sm.get().strip())

    # Фильтруем данные на основе номера плавки и начальника смены из таблицы 7
    filtered_master = tables.table7[
        tables.table7.apply(
            lambda row: (heat_no_input in str(row['HeatNo']) if heat_no_input else True) and 
                        (slovene_to_ascii(row['LFVD_ShiftHead']) == shift_head_input if shift_head_input else True), axis=1
        )
    ]

    # Если не найдено данных по мастеру, отображаем сообщение и выходим
    if filtered_master.empty:
        result_text_sm.set("Нет данных для выбранного начальника смены или номера плавки.")
        return

    # Получаем имя мастера
    shift_head_name = filtered_master.iloc[0]['LFVD_ShiftHead']

    # Фильтруем данные для элементов из таблицы 2 (где хранятся лимиты и финальные значения)
    filtered_data = tables.table2[
        tables.table2.apply(
            lambda row: (heat_no_input in str(row['HeatNo']) if heat_no_input else True), axis=1
        )
    ]

    # Если не найдено данных по плавке, отображаем сообщение и выходим
    if filtered_data.empty:
        result_text_sm.set("Нет данных для построения диаграммы.")
        return

    # Очищаем предыдущие диаграммы
    for widget in steelmills_frame.winfo_children():
        widget.destroy()

    # Контейнер для графиков
    graph_frame = tk.Frame(steelmills_frame)
    graph_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    # Контейнер для легенды
    legend_frame = tk.Frame(steelmills_frame)
    legend_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    # Настраиваем веса строк и столбцов для масштабируемого размещения графиков
    steelmills_frame.grid_rowconfigure(0, weight=1)
    steelmills_frame.grid_columnconfigure(0, weight=3)  # Больше места для графиков
    steelmills_frame.grid_columnconfigure(1, weight=1)  # Меньше места для легенды

    # Массив для оценки всех элементов
    element_scores = []

    # Построение диаграммы для каждого элемента
    elements = ['Cr', 'Ni', 'Mo', 'V', 'W']
    for i, element in enumerate(elements):
        fig, ax = plt.subplots(figsize=(4.5, 3.5))  # Масштабируем размер графика

        # Получение значений из таблицы 2
        min_val = filtered_data[f'{element}_LowerLimit'].values[0]
        target = filtered_data[f'{element}_Target'].values[0]
        final_val = filtered_data[f'{element}_Final'].values[0]
        max_val = filtered_data[f'{element}_UpperLimit'].values[0]

        # Определение промежуточных значений для классификации
        target_min = (min_val + target) / 2
        target_max = (target + max_val) / 2

        # Классификация значений
        if min_val <= final_val <= target_min:
            status = 'Очень хорошо'
            color = 'green'
            score = 4
        elif target_min < final_val <= target_max:
            status = 'Хорошо'
            color = 'blue'
            score = 3
        elif target_max < final_val <= max_val:
            status = 'Плохо'
            color = 'orange'
            score = 2
        else:
            status = 'Брак'
            color = 'red'
            score = 1

        # Добавляем балл для этого элемента в список
        element_scores.append(score)

        # Построение линейного графика
        ax.plot([min_val, target, max_val], [0, 0, 0], color='black', linestyle='--')  # Линия с лимитами
        ax.plot(final_val, 0, marker='o', markersize=8, color=color)  # Точка с результатом

        # Настройка графика
        ax.set_xlim(min_val - 0.1, max_val + 0.1)  # Масштабирование по оси X
        ax.set_ylim(-1, 1)  # Фиксированный диапазон по оси Y
        ax.set_title(f'Оценка для {element}: {status}')
        ax.set_yticks([])  # Убираем ось Y

        # Вставка диаграммы в интерфейс
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=i // 3, column=i % 3, padx=5, pady=5, sticky="nsew")

    # Настройка адаптации контейнера под диаграммы
    for i in range(2):  # Две строки
        graph_frame.grid_rowconfigure(i, weight=1)
    for i in range(3):  # Три столбца
        graph_frame.grid_columnconfigure(i, weight=1)

    # Обновление легенды
    update_legend(legend_frame)

    # Средняя оценка мастера
    average_score = sum(element_scores) / len(element_scores)
    status_text = get_status_from_score(average_score)

    # Обновление метки с именем мастера и средней оценкой
    master_name_var.set(f"Мастер: {shift_head_name} | Средняя оценка: {status_text}")

# Функция для получения статуса на основе средней оценки
def get_status_from_score(score):
    if score >= 3.5:
        return "Очень хорошо"
    elif score >= 2.5:
        return "Хорошо"
    elif score >= 1.5:
        return "Плохо"
    else:
        return "Брак"

# Функция для обновления легенды
def update_legend(legend_frame):
    # Легенда
    legend = [
        ('Очень хорошо', 'green'),
        ('Хорошо', 'blue'),
        ('Плохо', 'orange'),
        ('Брак', 'red'),
    ]

    # Создание элементов легенды
    for i, (status, color) in enumerate(legend):
        color_box = tk.Label(legend_frame, text="   ", bg=color, width=2)
        color_box.grid(row=i, column=0, padx=5, pady=5, sticky="w")
        label_text = tk.Label(legend_frame, text=status)
        label_text.grid(row=i, column=1, padx=5, pady=5, sticky="w")
        
if __name__ == '__main__':
    print("Оценки сталеваров")