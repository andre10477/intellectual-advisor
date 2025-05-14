import tkinter as tk
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import prognoz
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
row = None
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

def create_ml_frame(tab4):
    global entry_date_ml, entry_heat_no_ml, result_text, ml_frame

    # Создаем фрейм для ввода
    frame_input = tk.Frame(tab4)
    frame_input.pack(fill="x", padx=10, pady=10)

    # Создаем фрейм для прогноза и центруем его с левой стороны
    frame_result = tk.Frame(tab4)
    frame_result.pack(side="left", padx=10, pady=10, anchor="w")

    # Создаем контейнер для графиков, который будет расширяться
    frame_grafiki = tk.Frame(tab4)
    frame_grafiki.pack(fill="both", expand=True, padx=10, pady=10)

    # Метки и поля ввода
    label_date_ml = tk.Label(frame_input, text="Дата:", font=("Arial", 12))
    label_date_ml.pack(side="left", padx=5)
    entry_date_ml = tk.Entry(frame_input, width=15, font=("Arial", 12))
    entry_date_ml.pack(side="left", padx=5)

    label_heat_no_ml = tk.Label(frame_input, text="Номер плавки (HeatNo):", font=("Arial", 12))
    label_heat_no_ml.pack(side="left", padx=5)
    entry_heat_no_ml = tk.Entry(frame_input, width=15, font=("Arial", 12))
    entry_heat_no_ml.pack(side="left", padx=5)

    button_predict = tk.Button(frame_input, text="Прогнозировать", command=lambda: make_prediction(entry_date_ml, entry_heat_no_ml, result_text), font=("Arial", 12))
    button_predict.pack(side="left", padx=5)

    # Настраиваем текст прогноза и центрируем его с левой стороны
    result_text = tk.StringVar()
    label_result_ml = tk.Label(frame_result, textvariable=result_text, font=("Arial", 12), justify="center")
    label_result_ml.pack(pady=5)

    # Контейнер для графиков
    ml_frame = tk.Frame(tab4)
    ml_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
def make_prediction(entry_date_ml, entry_heat_no_ml, result_text):
    # Считываем входные данные с формы
    date_input = entry_date_ml.get().strip()
    heat_no_input = entry_heat_no_ml.get().strip()

    # Фильтрация данных
    filtered_data = tables.table1[
        tables.table1.apply(
            lambda row: (date_input in str(row['Date']) if date_input else True) and
                        (heat_no_input in str(row['HeatNo']) if heat_no_input else True), axis=1
        )
    ]

    if filtered_data.empty:
        result_text.set("Нет данных для прогноза.")
        return

    # Прогнозирование для каждого элемента
    X, y, df_hn = prognoz.prepare_data(tables)
    
    # Преобразуем входной номер плавки в числовой тип, если нужно
    try:
        heat_no_input = int(heat_no_input)
    except ValueError:
        result_text.set("Номер плавки должен быть числом.")
        return

    # Прогнозирование
    y_pred = prognoz.prediction(X, y)
    
    # Преобразуем массив в DataFrame и добавляем столбец 'HeatNo'
    df = pd.DataFrame(y_pred, columns=['Cr_Final', 'Ni_Final', 'Mo_Final', 'V_Final', 'W_Final'])
    df['HeatNo'] = df_hn

    # Проверка наличия плавки в df
    if heat_no_input not in df['HeatNo'].values:
        result_text.set("Плавка с указанным номером не найдена.")
        return

    # Индексируем по номеру плавки
    row = df[df['HeatNo'] == heat_no_input].iloc[0]

    # Вывод результатов прогноза
    result_text.set(f"Прогноз для Cr: {row['Cr_Final']:.2f}\n"
                    f"Прогноз для Ni: {row['Ni_Final']:.2f}\n"
                    f"Прогноз для Mo: {row['Mo_Final']:.2f}\n"
                    f"Прогноз для V: {row['V_Final']:.2f}\n"
                    f"Прогноз для W: {row['W_Final']:.2f}")

    # Построение графиков
    grafiki(row)

    
def grafiki(predictions):
    # Очищаем предыдущие графики, если они есть
    for widget in ml_frame.winfo_children():
        widget.destroy()

    # Список элементов
    elements = ['Cr', 'Ni', 'Mo', 'V', 'W']

    # Фильтруем данные
    date_input = entry_date_ml.get().strip()
    heat_no_input = entry_heat_no_ml.get().strip()

    filtered_data = tables.table2[tables.table2.apply(
        lambda row: (date_input in str(row['Date']) if date_input else True) and 
                    (heat_no_input in str(row['HeatNo']) if heat_no_input else True), axis=1
    )]

    if filtered_data.empty:
        result_text.set("Нет данных для построения графиков.")
        return

    # Создаем графики и размещаем их равномерно
    for i, element in enumerate(elements):
        fig, ax = plt.subplots(figsize=(5, 4))

        # Извлечение данных для графиков
        lower_limit = filtered_data[f'{element}_LowerLimit'].values[0]
        target = filtered_data[f'{element}_Target'].values[0]
        final = filtered_data[f'{element}_Final'].values[0]
        upper_limit = filtered_data[f'{element}_UpperLimit'].values[0]
        prediction = predictions[f'{element}_Final']  # Используем переданный predictions

        # Данные для построения графика
        labels = ['Lower Limit', 'Target', 'Final', 'Upper Limit', 'Prediction']
        values = [lower_limit, target, final, upper_limit, prediction]

        # Построение графика
        bars = ax.bar(labels, values, color=['#4C72B0', '#55A868', '#E1B066', '#C44E52', '#8172B3'])
        ax.set_title(f'График для {element}', fontweight="bold")
        ax.set_ylabel(f'Концентрация {element}', fontweight="bold")
        ax.grid(True, axis='y', linestyle='--', alpha=0.7)

        # Добавляем значения над столбцами
        for bar in bars:
            yval = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2, yval, f'{yval:.2f}', ha='center', va='bottom')

        # Вставка графика в интерфейс
        canvas = FigureCanvasTkAgg(fig, master=ml_frame)
        canvas.draw()

        # Размещение графиков в сетке
        canvas.get_tk_widget().grid(row=i // 3, column=i % 3, padx=5, pady=5, sticky="nsew")

    # Настройка адаптации контейнера под графики
    for i in range(2):  # Две строки
        ml_frame.grid_rowconfigure(i, weight=1)
    for i in range(3):  # Три столбца
        ml_frame.grid_columnconfigure(i, weight=1)
        

if __name__ == '__main__':
    print("Машинное обучение")