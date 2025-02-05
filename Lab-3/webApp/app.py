from flask import Flask, render_template, request, jsonify
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import joblib
from tensorflow.keras.models import load_model
import os

app = Flask(__name__)

# Load pre-trained models (assuming they're saved as pickle files)
linear_regression_model = joblib.load(r'C:\Users\KIIT\Documents\GitHub\AD-Lab\Lab-3\linear_regression_stock_model.pkl')
lstm_model = load_model(r'C:\Users\KIIT\Documents\GitHub\AD-Lab\Lab-3\lstm_stock_model.h5')

# Load scalers - Ensure scalers are saved and in the correct path
scaler_features = joblib.load(r'C:\Users\KIIT\Documents\GitHub\AD-Lab\Lab-3\webApp\scaler_features.pkl')  # Correct path
scaler_target = joblib.load(r'C:\Users\KIIT\Documents\GitHub\AD-Lab\Lab-3\webApp\scaler_target.pkl')  # Correct path

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get the input data from the form
        open_price = float(request.form['open_price'])
        high_price = float(request.form['high_price'])
        low_price = float(request.form['low_price'])
        volume = float(request.form['volume'])
        moving_avg = float(request.form['moving_avg'])

        # Prepare the input data as a numpy array
        input_data = np.array([[open_price, high_price, low_price, volume, moving_avg]])

        # Scale the features using the scaler
        scaled_input = scaler_features.transform(input_data)

        # Reshape for LSTM
        lstm_input = scaled_input.reshape((scaled_input.shape[0], 1, scaled_input.shape[1]))

        # Predict with Linear Regression
        lr_pred = linear_regression_model.predict(scaled_input)
        lr_pred_actual = scaler_target.inverse_transform(lr_pred)

        # Predict with LSTM
        lstm_pred = lstm_model.predict(lstm_input)
        lstm_pred_actual = scaler_target.inverse_transform(lstm_pred)

        # Convert predictions to standard float to avoid JSON serialization issues
        lr_pred_actual = float(lr_pred_actual[0][0])  # Convert from float32 to float
        lstm_pred_actual = float(lstm_pred_actual[0][0])  # Convert from float32 to float

        # Send the results and data for Chart.js back to the frontend
        return jsonify({
            'linear_regression_prediction': lr_pred_actual,
            'lstm_prediction': lstm_pred_actual,
            'chart_data': {
                'labels': ['Linear Regression', 'LSTM'],
                'datasets': [{
                    'label': 'Predicted Stock Prices',
                    'data': [lr_pred_actual, lstm_pred_actual],
                    'backgroundColor': ['rgba(0, 123, 255, 0.5)', 'rgba(255, 165, 0, 0.5)'],
                    'borderColor': ['rgba(0, 123, 255, 1)', 'rgba(255, 165, 0, 1)'],
                    'borderWidth': 1
                }]
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
