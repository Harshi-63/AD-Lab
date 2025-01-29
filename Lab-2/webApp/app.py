from flask import Flask, render_template, request, jsonify
import joblib
import numpy as np
import os
from tensorflow.keras.models import load_model
import cv2
from tensorflow.keras.applications import VGG16
from tensorflow.keras.preprocessing.image import img_to_array, load_img

app = Flask(__name__)

# Load models
cnn_model = load_model(
    r"C:\Users\KIIT\Documents\GitHub\AD-Lab\Lab-2\cnn_model.h5")
svm_sgd = joblib.load(   
    r"C:\Users\KIIT\Documents\GitHub\AD-Lab\Lab-2\svm_sgd_model.pkl")
rf = joblib.load(
    r"C:\Users\KIIT\Documents\GitHub\AD-Lab\Lab-2\random_forest_model.pkl")
logreg = joblib.load(
    r"C:\Users\KIIT\Documents\GitHub\AD-Lab\Lab-2\logreg_model.pkl")
kmeans = joblib.load(
    r"C:\Users\KIIT\Documents\GitHub\AD-Lab\Lab-2\kmeans_model.pkl")

# VGG16 model for feature extraction (without top layer)
vgg16 = VGG16(weights="imagenet", include_top=False, input_shape=(64, 64, 3))

def extract_features_from_image(image_path, target_size=(64, 64)):
    """Extract features from a single image using VGG16"""
    img = load_img(image_path, target_size=target_size)
    img_array = img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    features = vgg16.predict(img_array)
    # Use average pooling (instead of flattening all features)
    return features.mean(axis=(1, 2)).flatten()

# Image preprocessing function
def preprocess_image(image_path, target_size=(64, 64)):
    img = cv2.imread(image_path)
    img = cv2.resize(img, target_size)
    img = img / 255.0  # Normalize
    return img

# Flask route for homepage
@app.route('/')
def home():
    return render_template('index.html')

# Route to handle image upload and model prediction
@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Get the uploaded image
        file = request.files['image']
        image_path = os.path.join('uploads', file.filename)
        file.save(image_path)

        # Preprocess the image for prediction
        img = preprocess_image(image_path)

        # Extract features using VGG16 model
        img_features = extract_features_from_image(image_path)

        # Get model selection from frontend
        model_choice = request.form['model']

        result = ''
        accuracy = 0.0

        if model_choice == 'cnn':
            prediction = cnn_model.predict(np.expand_dims(img, axis=0))
            prediction_value = prediction[0]  # CNN model returns a probability
            result = 'Cat' if prediction_value < 0.5 else 'Dog'
            accuracy = round(float(prediction_value) * 100, 2) if prediction_value < 0.5 else round(float(1 - prediction_value) * 100, 2)
        elif model_choice == 'svm':
            img_flat = img_features.reshape(1, -1)  # Use features from VGG16
            prediction = svm_sgd.predict(img_flat)
            result = 'Cat' if prediction[0] == 0 else 'Dog'
            accuracy = 85.0  # Predefined accuracy value from training phase
        elif model_choice == 'rf':
            img_flat = img_features.reshape(1, -1)  # Use features from VGG16
            prediction = rf.predict(img_flat)
            result = 'Cat' if prediction[0] == 0 else 'Dog'
            accuracy = 85.0  # Predefined accuracy value from training phase
        elif model_choice == 'logreg':
            img_flat = img_features.reshape(1, -1)  # Use features from VGG16
            prediction = logreg.predict(img_flat)
            result = 'Cat' if prediction[0] == 0 else 'Dog'
            accuracy = 85.0  # Predefined accuracy value from training phase
        elif model_choice == 'kmeans':
            img_flat = img_features.reshape(1, -1)  # Use features from VGG16
            prediction = kmeans.predict(img_flat)
            result = 'Cat' if prediction[0] == 0 else 'Dog'
            accuracy = 85.0  # Predefined accuracy value from training phase
        else:
            result = 'Invalid model selected'

        return jsonify({'prediction': result, 'accuracy': accuracy})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
