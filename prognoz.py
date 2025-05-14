import pandas as pd, joblib, matplotlib as plt
from sklearn.linear_model import LinearRegression
from IPython.core.display import display
from tabl import get_tables

tables = get_tables()

def merge_duplicate_columns(df):
    # Найдём столбцы с суффиксами _x и _y
    cols_x = [col for col in df.columns if col.endswith('_x')]
    cols_y = [col.replace('_x', '_y') for col in cols_x if col.replace('_x', '_y') in df.columns]

    for col_x, col_y in zip(cols_x, cols_y):
        # Новый столбец без суффикса будет объединением col_x и col_y
        new_col = col_x[:-2]  # Убираем суффикс _x
        
        # Объединяем значения из col_x и col_y. Если одно из значений пустое, берём другое
        df[new_col] = df[col_x].combine_first(df[col_y])
        
        # Удаляем старые столбцы
        df.drop([col_x, col_y], axis=1, inplace=True)
    
    return df

# Подготовка данных для обучения модели
def prepare_data(tables):
    df_basic = tables.table1
    df_composition = tables.table2
    df_alloys = tables.table4

    # Объединение данных
    df = pd.merge(df_basic, df_composition, on="HeatNo", how="inner")
    df = pd.merge(df, df_alloys, on="HeatNo", how="inner")
    df = merge_duplicate_columns(df)    
    # Преобразование даты
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day
    
    df_hn = df['HeatNo']
    
    # Отображение данных для проверки
    with pd.option_context("display.max_columns", None):
        display(df)

    # Замена суффиксов
    df = merge_duplicate_columns(df)

    # Отображение данных для проверки
    with pd.option_context("display.max_columns", None):
        display(df)
        
    df = df.interpolate(limit_direction='both')
    print(df.isna().sum())
    df.info()

    # Признаки (предикторы)
    X = df[['Year', 'Month', 'Day', 'TotalIngotsWeight', 
            'Cr_Last_EOP', 'Ni_Last_EOP', 'V_Last_EOP', 'W_Last_EOP',
            'Cr_LowerLimit', 'Cr_Target', 'Cr_UpperLimit',
            'Ni_LowerLimit', 'Ni_Target', 'Ni_UpperLimit',
            'Mo_LowerLimit', 'Mo_Target', 'Mo_UpperLimit',
            'V_LowerLimit', 'V_Target', 'V_UpperLimit',
            'W_LowerLimit', 'W_Target', 'W_UpperLimit',
            'LFVD_AlBloki', 'LFVD_AlGran', 'LFVD_Boksit', 'LFVD_CaO', 'LFVD_CaSi', 'LFVD_CASIfi13', 
            'LFVD_Cfi13', 'LFVD_CoMet', 'LFVD_Cu', 'LFVD_EPŽŽlindra', 'LFVD_FeAl', 'LFVD_FeB', 
            'LFVD_FeBŽica', 'LFVD_FeCrNit', 'LFVD_FeCrA', 'LFVD_FeCrC', 'LFVD_FeCrCSi', 'LFVD_FeCrC51', 
            'LFVD_FeMnA', 'LFVD_FeMnC', 'LFVD_FeMo', 'LFVD_FeNbTa', 'LFVD_FeNbTafi13', 'LFVD_FeS', 
            'LFVD_FeSi', 'LFVD_FeSiZrŽica', 'LFVD_FeTi', 'LFVD_FeTifi13', 'LFVD_FeV', 'LFVD_FeW72', 
            'LFVD_KarboritMleti', 'LFVD_MnMet', 'LFVD_NiGran', 'LFVD_NiKatode', 'LFVD_NiOksid', 
            'LFVD_OdpCu', 'LFVD_Polymox', 'LFVD_SŽica', 'LFVD_SiMet', 'LFVD_SiMn', 'LFVD_SLAGMAG65B', 
            'LFVD_KarboritZaVpih', 'LFVD_Ni90', 'LFVD_AlŽica', 'LFVD_Molyquick', 'LFVD_AlOplašèenaŽica', 
            'LFVD_BelaŽlindra', 'LFVD_Kisik', 'LFVD_KalcijevKarbid', 'LFVD_WPaketi', 'LFVD_SintŽlindra']]

    # Проверка на отсутствие нужных столбцов
    missing_columns = [col for col in X if col not in df.columns]
    if missing_columns:
        raise KeyError(f"Отсутствуют необходимые столбцы: {missing_columns}")

    # Целевые переменные
    y = df[['Cr_Final', 'Ni_Final', 'Mo_Final', 'V_Final', 'W_Final']]

    return X, y, df_hn

def prediction(X, y):
    print("Прогноз начат")
    model = LinearRegression().fit(X, y)
    print(f"Оценка R2 - прогноз:{model.score(X, y)}")
    print('intercept:', model.intercept_)
    print('slope:', model.coef_)
    y_pred = model.predict(X)
    print('predicted response:', y_pred, sep='\n')
    from sklearn.model_selection import cross_val_score
    scores = cross_val_score(model, X, y, cv=5, scoring='r2')
    print(f"Среднее значение R2: {scores.mean()}, стандартное отклонение: {scores.std()}")
    return y_pred

X, y, df_hn = prepare_data(tables)
prediction(X, y)

if __name__ == '__main__':
    print("Прогноз")