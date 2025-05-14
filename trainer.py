import prognoz
from sklearn.metrics import r2_score
from sklearn.linear_model import SGDRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import joblib
from tabl import get_tables
import numpy as np

tables = get_tables()

def train_iterative_model(X, y, batch_size=100, n_epochs=10):
    models = {}
    target_names = y
    
    for target_name in target_names:
        X_train, X_test, y_train, y_test = train_test_split(X, y[target_name], test_size=0.2, random_state=0)
        
        # Инициализируем модель для итеративного обучения
        model = SGDRegressor(max_iter=1, warm_start=True)
        
        n_samples = X_train.shape[0]
        for epoch in range(n_epochs):
            # Перемешиваем данные перед каждой эпохой
            indices = np.arange(n_samples)
            np.random.shuffle(indices)
            X_train_shuffled = X_train[indices]
            y_train_shuffled = y_train[indices]
            
            # Итеративно обучаем модель на батчах
            for start in range(0, n_samples, batch_size):
                end = start + batch_size
                X_batch = X_train_shuffled[start:end]
                y_batch = y_train_shuffled[start:end]
                
                # Дообучаем модель на каждом батче
                model.partial_fit(X_batch, y_batch)
            
            # Оценка модели после каждой эпохи
            y_pred = model.predict(X_test)
            mse = mean_squared_error(y_test, y_pred)
            print(f"Эпоха {epoch+1}/{n_epochs} для {target_name} - Средняя ошибка на тесте: {mse}, R2: {r2_score(y_test, y_pred)}")
        
        # Сохраняем модель для каждого вещества
        model_filename = f"{target_name}_model_iterative.joblib"
        joblib.dump(model, model_filename)
        models[target_name] = model
        print(f"Итеративная модель для {target_name} сохранена как {model_filename}")

    return models

# Вызов функций для подготовки данных и итеративного обучения моделей
X, y, df_hn = prognoz.prepare_data(tables)  # Здесь tables — это ваши исходные данные
# Итеративное обучение модели для каждого вещества
models = train_iterative_model(X, y)
