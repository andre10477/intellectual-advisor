import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import xgboost as xgb
import joblib
from sklearn.model_selection import cross_val_score

class Model:
    def __init__(self, input_file = 'PQM - podatki za pilotni projekt (OCR12VM) - ENG.xlsx', model = None):
        self.input_file = input_file
        self.load_data()

        if (model == None):
            # Обучение модели перед запуском
            self.preprocess_data()
            self.train_model()
            self.save_model("steel_optimizer_model.pkl")
        else:
            self.model = model

    def load_data(self):
        try:
            self.data_initial = pd.read_excel(self.input_file, sheet_name='Table1 (basic)', skiprows=1)
            self.data_additives =  pd.read_excel(self.input_file, sheet_name='Table4 (alloys)', skiprows=1)
            self.data_limits = pd.read_excel(self.input_file, sheet_name='Table2 (limits)', skiprows=1)
            print("Данные успешно загружены")
        except Exception as e:
            print(f"Ошибка при загрузке данных: {e}")

    def preprocess_data(self):
        try:
            self.data_initial = self.data_initial.dropna()
            self.data_additives = self.data_additives.dropna()
            # Объединяем данные по номеру плавки (HeatNo)
            combined_data = self.data_initial.merge(self.data_additives, how='inner')
            combined_data = combined_data.interpolate(limit_direction='both')

            predictors = combined_data[[
                
                'HeatNo',

                'Cr_Last_EOP', 'Ni_Last_EOP', 'Mo_Last_EOP', 'V_Last_EOP', 'W_Last_EOP',

                'TotalIngotsWeight',

                'LFVD_AlBloki', 'LFVD_AlGran', 'LFVD_Boksit', 'LFVD_CaO', 'LFVD_CaSi', 'LFVD_CASIfi13', 
                'LFVD_Cfi13', 'LFVD_CoMet', 'LFVD_Cu', 'LFVD_EPŽŽlindra', 'LFVD_FeAl', 'LFVD_FeB', 
                'LFVD_FeBŽica', 'LFVD_FeCrNit', 'LFVD_FeCrA', 'LFVD_FeCrC', 'LFVD_FeCrCSi', 'LFVD_FeCrC51', 
                'LFVD_FeMnA', 'LFVD_FeMnC', 'LFVD_FeMo', 'LFVD_FeNbTa', 'LFVD_FeNbTafi13', 'LFVD_FeS', 
                'LFVD_FeSi', 'LFVD_FeSiZrŽica', 'LFVD_FeTi', 'LFVD_FeTifi13', 'LFVD_FeV', 'LFVD_FeW72', 
                'LFVD_KarboritMleti', 'LFVD_MnMet', 'LFVD_NiGran', 'LFVD_NiKatode', 'LFVD_NiOksid', 
                'LFVD_OdpCu', 'LFVD_Polymox', 'LFVD_SŽica', 'LFVD_SiMet', 'LFVD_SiMn', 'LFVD_SLAGMAG65B', 
                'LFVD_KarboritZaVpih', 'LFVD_Ni90', 'LFVD_AlŽica', 'LFVD_Molyquick', 'LFVD_AlOplašèenaŽica', 
                'LFVD_BelaŽlindra', 'LFVD_Kisik', 'LFVD_KalcijevKarbid', 'LFVD_WPaketi', 'LFVD_SintŽlindra'
            ]]
            targets = combined_data[['HeatNo', 'Cr_Final', 'Ni_Final', 'Mo_Final', 'V_Final', 'W_Final']]

            predictors.set_index(['HeatNo'], inplace=True)
            targets.set_index(['HeatNo'], inplace=True)

            print(targets.info())
            print(predictors.info())

            self.X = predictors
            self.y = targets

            print("Данные успешно подготовлены")
        except Exception as e:
            print(f"Ошибка при подготовке данных: {e}")

    def train_model(self):
        try:
            X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.3, random_state=0)

            params = {
                      'n_estimators': 150,
                      'max_depth': 6,
                      'learning_rate': 0.05,
                      'subsample': 0.4
                      }

            self.model = xgb.XGBRegressor(**params)
            self.model.fit(X_train, y_train)
            
            get_score(self.model, self.X, self.y)

            predictions = self.model.predict(X_test)
            mse = mean_squared_error(y_test, predictions)

            print(f"Обучение завершено.\nСреднеквадратическая ошибка (MSE): {mse:.4f}")
            print(f'Коэффициент детерминации (R²): {r2_score(y_test, predictions):.2f}')
        except Exception as e:
            print(f"Ошибка при обучении модели: {e}")

    def save_model(self, output_file):
        try:
            joblib.dump(self.model, output_file)
            print(f"Модель сохранена в файл: {output_file}")
        except Exception as e:
            print(f"Ошибка при сохранении модели: {e}")

    def predict_final_parameters(self, input_values):
        try:
            self.data_additives.drop(columns=['HeatNo'],inplace=True)
            pd.set_option('display.max_columns', None)

            initial_repeated = pd.DataFrame([input_values] * len(self.data_additives))
            combined_data = pd.concat([initial_repeated, self.data_additives], axis=1)

            # Прогнозируем значения с помощью модели
            predictions = self.model.predict(combined_data)
            combined_data['Cr_Final'] = predictions[:, 0]
            combined_data['Ni_Final'] = predictions[:, 1]
            combined_data['Mo_Final'] = predictions[:, 2]
            combined_data['V_Final'] = predictions[:, 3]
            combined_data['W_Final'] = predictions[:, 4]

            # Фильтруем по лимитам из первой строки data_limits
            limits = self.data_limits.iloc[0]
            print("лимиты")
            print(self.data_limits)
            filtered_data = combined_data[
               (combined_data['Cr_Final'].between(limits['Cr_LowerLimit'], limits['Cr_UpperLimit'])) &
               (combined_data['Ni_Final'].between(limits['Ni_LowerLimit'], limits['Ni_UpperLimit'])) &
               (combined_data['Mo_Final'].between(limits['Mo_LowerLimit'], limits['Mo_UpperLimit'])) &
               (combined_data['V_Final'].between(limits['V_LowerLimit'], limits['V_UpperLimit'])) &
               (combined_data['W_Final'].between(limits['W_LowerLimit'], limits['W_UpperLimit']))]

            # Сортируем по 5 финальным параметрам, начиная с W_Final
            sorted_data = filtered_data.sort_values(by=['W_Final', 'V_Final', 'Mo_Final', 'Ni_Final', 'Cr_Final'])
            print("Прогнозирование завершено")
            return sorted_data

        except Exception as e:
            print(f"Ошибка при прогнозировании: {e}")
            return pd.DataFrame()
        
    
def get_score(md, X, y):
        score = cross_val_score(md, X, y, cv=10)
        print(f"Оценка кросс валидации: {score}")

if __name__ == "__main__":
    trainer = Model("PQM - podatki za pilotni projekt (OCR12VM) - ENG.xlsx")
    initial_composition = {
        'Cr_Last_EOP': 9.71,
        'Ni_Last_EOP': 0.2,
        'Mo_Last_EOP': 0.12,
        'V_Last_EOP': 0.03,
        'W_Last_EOP': 0.01,
        'TotalIngotsWeight': 49440,
    }
    md = joblib.load('steel_optimizer_model.pkl')
    predictor = Model("PQM - podatki za pilotni projekt (OCR12VM) - ENG.xlsx", md)
    prediction = predictor.predict_final_parameters(initial_composition)

    if not prediction.empty:
        pd.set_option('display.max_columns', None)
        first_row = prediction.iloc[0]
        first_row = first_row.apply(float)
        print(first_row)
        additives = [
            (col, first_row[col]) for col in first_row.index
            if col.startswith("LFVD_") and first_row[col] > 0
        ]
        print(additives)
        predicted_values = first_row[['Cr_Final', 'Ni_Final', 'Mo_Final', 'V_Final', 'W_Final']]
        print(predicted_values)
