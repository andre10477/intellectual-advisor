import pandas as pd
import os

# Класс для загрузки и хранения таблиц из Excel-файла
class Tables:
    def __init__(self):
        # Инициализация атрибутов для всех таблиц
        self.table1 = None
        self.table2 = None
        self.table3 = None
        self.table4 = None
        self.table5 = None
        self.table6 = None
        self.table7 = None
        self.table8 = None
        self.table9 = None
        self.table10 = None

    def load(self, filepath):
        # Получаем все CSV файлы в директории
        csv_files = [f for f in os.listdir(filepath) if f.endswith('.csv')]

        # Если есть CSV файлы, загружаем их
        if csv_files:
            for csv_file in csv_files:
                # Определяем номер таблицы из имени файла (например, table1.csv -> table1)
                table_number = csv_file.split('.')[0]  # Извлекаем номер (table1)
                table_attr = table_number  # Название атрибута, например table1

                # Формируем полный путь к файлу
                file_path = os.path.join(filepath, csv_file)
                try:
                    # Загружаем CSV файл в соответствующую переменную таблицы
                    setattr(self, table_attr, pd.read_csv(file_path))
                    print(f"Загружен файл {csv_file} в {table_attr}.")
                except Exception as e:
                    print(f"Ошибка при загрузке {csv_file}: {e}")
        else:
            # Если CSV файлов нет, пытаемся загрузить данные из Excel
            try:
                self.table1 = pd.read_excel(filepath, 'Table1 (basic)', skiprows=1, engine='openpyxl')
                self.table2 = pd.read_excel(filepath, 'Table2 (limits)', skiprows=1, engine='openpyxl')
                self.table3 = pd.read_excel(filepath, 'Table3 (coefficient)', skiprows=1, engine='openpyxl')
                self.table4 = pd.read_excel(filepath, 'Table4 (rules)', skiprows=1, engine='openpyxl')
                self.table5 = pd.read_excel(filepath, 'Table5 (determinant)', skiprows=1, engine='openpyxl')
                self.table6 = pd.read_excel(filepath, 'Table6 (coefficients)', skiprows=1, engine='openpyxl')
                self.table7 = pd.read_excel(filepath, 'Table7 (classifications)', skiprows=1, engine='openpyxl')
                self.table8 = pd.read_excel(filepath, 'Table8 (relations)', skiprows=1, engine='openpyxl')
                self.table9 = pd.read_excel(filepath, 'Table9 (special)', skiprows=1, engine='openpyxl')
                self.table10 = pd.read_excel(filepath, 'Table10 (summary)', skiprows=1, engine='openpyxl')
                print("Загружены данные из Excel.")
            except Exception as e:
                print(f"Ошибка при загрузке Excel файла: {e}")
    
        # Метод для сохранения всех таблиц в CSV в директорию проекта
    def save_to_csv(self):
        # Получаем путь к текущей директории проекта
        project_dir = os.getcwd()  # Это вернет текущую рабочую директорию

        # Сохраняем каждую таблицу в CSV в директории проекта
        for i, table in enumerate([self.table1, self.table2, self.table3, self.table4, self.table5, self.table6, self.table7, self.table8, self.table9, self.table10], 1):
            output_path = os.path.join(project_dir, f'table{i}.csv')  # Создаем путь к файлу
            table.to_csv(output_path, index=False)
            print(f"Таблица {i} сохранена как {output_path}")

# Инициализация объекта для работы с таблицами
#tables = Tables('PQM - podatki za pilotni projekt (OCR12VM) - ENG.xlsx')
tables = Tables()
tables.load(filepath=os.getcwd())

def get_tables():
    return tables

if __name__ == '__main__':
    print("Таблицы")