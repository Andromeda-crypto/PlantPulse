import cv2
import os
import csv
import re
import json
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session, jsonify
from flask_cors import CORS
import pandas as pd
import plotly.graph_objects as go
from jinja2 import TemplateNotFound
from plotly.subplots import make_subplots
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import numpy as np
import logging
from PIL import Image
import sqlite3
from ml_engine import analyze_plant_image
from image_utils import (
    allowed_file,
    validate_file,
    save_file,
    load_resize_image,
    is_image_blurry,
    calculate_image_features,
    analyze_content,
    build_result_message,
    )



# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


app = Flask(__name__, static_folder='static')
CORS(app,supports_credentials=True) # Enable CORS for all routes
app.secret_key = '_my_project_secret_key_'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'Uploads')
CSV_DIR = os.path.join(BASE_DIR, 'csv runs')
DB_PATH = os.path.join(BASE_DIR, 'plantpulse.db')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(), 'uploads')



# Create directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CSV_DIR, exist_ok=True)

def load_latest_data(username=None):
    try:
        if username:
            filepath = f"csv runs/{username}_data.csv"
        else:
            filepath = "csv runs/latest_data.csv"
        
        if not os.path.exists(filepath):
            return None, f"No data found for {username}."
        
        data = pd.read_csv(filepath)
        return data, None
    except Exception as e:
        return None, str(e)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/home')
def user_home():
    if "username" not in session:
        return jsonify({"Error" : "User not logged in"}), 401
    return jsonify({
        "message": f"Welcome {session['username']}!",
        "status": "success"
    })


@app.route('/')
def home():
    return jsonify({"message": "Welcome to Plant Monitor API"}), 200 


@app.route('/photo', methods=['POST'])
def photo():
    if 'username' not in session:
        return jsonify({"success": False, "error": "User not logged in"}), 401

    if 'photo' not in request.files:
        return jsonify({"success": False, "error": "No file part in request."}), 400

    file = request.files['photo']
    if file.filename == '':
        return jsonify({"success": False, "error": "No file selected."}), 400

    filename = secure_filename(file.filename)

    try:
        file.stream.seek(0)
        Image.open(file.stream).verify()
        file.stream.seek(0)
    except Exception as e:
        return jsonify({"success": False, "error": "Invalid image file."}), 400

    try:
        upload_folder = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
    except Exception as e:
        return jsonify({"success": False, "error": "Failed to save image."}), 500

    return jsonify({"success": True, "filename": filename}), 200


@app.route('/uploads/<filename>')
def serve_upload(filename):
    filename = secure_filename(filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if not os.path.exists(file_path):
        logger.error(f"File not found: {filename}")
        return jsonify({"error": "File not found"}), 404
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/query', methods=['POST'])
def query():
    if "username" not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 401

    username = session["username"]
    Data, load_error = load_latest_data(username)

    if load_error:
        return jsonify({"success": False, "error": load_error}), 500

    if Data is None or Data.empty:
        return jsonify({"success": False, "error": "No data available"}), 404

    try:
        data = request.json  # Expecting JSON from React
        hour = int(data.get('hour'))
        if 0 <= hour < len(Data):
            row = Data.iloc[hour]
            result = {
                "hour": hour,
                "soil_moisture": round(row['soil_moisture'], 2),
                "light_level": round(row['light_level'], 2),
                "temperature": round(row['temperature'], 2),
                "health_status": row['health_status']
            }
            return jsonify({"success": True, "result": result}), 200
        else:
            return jsonify({"success": False, "error": f"Hour must be between 0 and {len(Data)-1}"}), 400
    except ValueError:
        return jsonify({"success": False, "error": "Hour must be a number!"}), 400
    except Exception as e:
        return jsonify({"success": False, "error": f"Unexpected error: {str(e)}"}), 500



@app.route('/zoom', methods=['GET', 'POST'])
def zoom():
    username = session.get("username")
    print("Username in session:", username) # Debugging line
    if "username" not in session:
        return jsonify({"error": "Unauthorized: Please log in to view your data."}), 401
    
    
    Data, load_error = load_latest_data(username)
    print("Data loaded:", Data) # Debugging line


    if Data is None or Data.empty:
        logger.warning(f"Zoom route: No data available for user {username}")
        return jsonify({"error": "No data available"}), 404

    logger.info(f"Received form data from {username}: {request.json}")
    try:
        start_hour = int(request.json.get('start_hour', '').strip())
        end_hour = int(request.json.get('end_hour', '').strip())
        logger.info(f"Parsed start_hour: {start_hour}, end_hour: {end_hour}")


        if not (0 <= start_hour < len(Data)) or not (0 <= end_hour < len(Data)):
            return jsonify({"error": f"Choose values between 0 and {len(Data)-1}."}), 400
        if start_hour > end_hour:
            return jsonify({"error": "Start hour must be less than or equal to end hour!"}), 400

        zoomed_data = Data.iloc[start_hour:end_hour + 1]
        if zoomed_data.empty:
            return jsonify({"error": "No data found in the selected time range."}), 404

        # Plotting
        fig = make_subplots(rows=3, cols=1, subplot_titles=('Soil Moisture', 'Light Level', 'Temperature'))

        fig.add_trace(go.Scatter(x=zoomed_data['timestamp'], y=zoomed_data['soil_moisture'],
                                 mode='lines', name='Soil Moisture', line=dict(color='blue')), row=1, col=1)
        low_moisture = zoomed_data[zoomed_data['health_status'] == 'Low moisture Plant needs more water']
        fig.add_trace(go.Scatter(x=low_moisture['timestamp'], y=low_moisture['soil_moisture'],
                                 mode='markers', name='Low Moisture', marker=dict(color='red', size=10)), row=1, col=1)



        fig.add_trace(go.Scatter(x=zoomed_data['timestamp'], y=zoomed_data['light_level'],
                                 mode='lines', name='Light Level', line=dict(color='orange')), row=2, col=1)
        low_light = zoomed_data[zoomed_data['health_status'] == 'Low light Plant needs more light']
        fig.add_trace(go.Scatter(x=low_light['timestamp'], y=low_light['light_level'],
                                 mode='markers', name='Low Light', marker=dict(color='yellow', size=10)), row=2, col=1)

        fig.add_trace(go.Scatter(x=zoomed_data['timestamp'], y=zoomed_data['temperature'],
                                 mode='lines', name='Temperature', line=dict(color='red')), row=3, col=1)
        too_hot = zoomed_data[zoomed_data['health_status'] == 'Too Hot Plant should be exposed to less heat']
        fig.add_trace(go.Scatter(x=too_hot['timestamp'], y=too_hot['temperature'],
                                 mode='markers', name='Too Hot', marker=dict(color='purple', size=10)), row=3, col=1)

        fig.update_layout(height=600, width=800, title_text="Zoomed Plant Data")
        fig.update_xaxes(title_text="Time", row=1, col=1)
        fig.update_xaxes(title_text="Time", row=2, col=1)
        fig.update_xaxes(title_text="Time", row=3, col=1)
        fig.update_yaxes(title_text="Moisture (%)", row=1, col=1)
        fig.update_yaxes(title_text="Light (lux)", row=2, col=1)
        fig.update_yaxes(title_text="Temperature (°C)", row=3, col=1)

        plot_html = fig.to_html(full_html=False)

        return jsonify({"plot_html": plot_html}), 200

    except ValueError as e:
        logger.error(f"ValueError in zoom route for {username}: {str(e)}, Form data: {request.json}")
        return jsonify({"error": f"Invalid input: {str(e)}"}), 400
    except KeyError as e:
        logger.error(f"KeyError in zoom route for {username}: {str(e)}, Form data: {request.json}")
        return jsonify({"error": f"Missing field: {str(e)}"}), 400
    except Exception as e:
        logger.error(f"Unexpected error in zoom route for {username}: {str(e)}, Form data: {request.json}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500



# personalized dashboard 
@app.route('/dashboard')
def dashboard():
    username = session.get('username')
    if not username:
        return jsonify({"success": False, "error": "User not logged in"}), 401

    user_data_file = f"data/{username}.csv"
    try:
        if os.path.exists(user_data_file):
            Data = pd.read_csv(user_data_file)
        else:
            Data, error = load_latest_data(username)
            if error or Data.empty:
                return jsonify({"success": False, "error": error or "No data available"}), 404

        stats = {
            "average_moisture": round(Data['soil_moisture'].mean(), 2),
            "average_light": round(Data['light_level'].mean(), 2),
            "average_temperature": round(Data['temperature'].mean(), 2),
        }

        return jsonify({
            "success": True,
            "username": username,
            "stats": stats,
            "alerts": generate_alerts(Data)
            # You can later include chart data too
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"Failed to load dashboard: {str(e)}"}), 500


USER_DATA_FOLDER = 'user_data'
if not os.path.exists(USER_DATA_FOLDER):
    os.makedirs(USER_DATA_FOLDER)

USERS_FILE = os.path.join(USER_DATA_FOLDER, 'users.json')

def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # Could log this error in real app
            return {}
    return {}

def save_users(users):
    try:
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=4)
    except IOError:
        # Could log or raise in real app
        pass

@app.route('/signup', methods=["GET", "POST"])
def signup():
    print("Signup route hit")
    print("Received signup POST with:", data) # debugging

    if request.method == "POST":
        data = request.get_json()
        username = data.get("username", "").strip()
        email = (data.get("email") or "").strip()
        password = data.get("password", "").strip()
        confirm_password = data.get("confirm_password", "").strip()

        if not username:
            return jsonify({"success": False, "message": "Username is required"}), 400
        elif not email:
            return jsonify({"success": False, "message": "Email is required"}), 400
        elif not password:
            return jsonify({"success": False, "message": "Password is required"}), 400
        elif confirm_password != password:
            return jsonify({"success": False, "message": "Passwords do not match"}), 400

        users = load_users()
        if username in users:
            return jsonify({"success": False, "message": "Username already exists"}), 409

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        users[username] = {"email": email, "password": hashed_password}
        save_users(users)

        session['username'] = username
        return jsonify({"success": True, "message": "Signup successful", "username": username}), 201
    return render_template('signup.html')


@app.route('/login', methods=["POST"])
def login():
    print("Login route called") # debugging line 
    data = request.get_json()
    username = data.get("username", "").strip()
    password = data.get("password", "").strip()

    if not username or not password:
        return jsonify({"success": False, "message": "Username and password are required"}), 400

    users = load_users()
    user = users.get(username)

    if not user:
        return jsonify({"success": False, "message": "User not found"}), 404
    stored_hash = user.get("password")
    if not check_password_hash(stored_hash, password):
        return jsonify({"success": False, "message": "Incorrect password"}), 401
    session['username'] = username
    return jsonify({"success": True, "message": "Login successful", "username": username}), 200



@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session.pop('username', None)
    if request.method == 'POST':
        return jsonify({'message': 'Logout successful'}), 200
    else:
        return redirect(url_for('login'))




def calculate_health_score(data):
    moisture_score = min(100, max(0, (data['soil_moisture'].mean() / 100) * 100))
    light_score = min(100, max(0, (data['light_level'].mean() / 1000) * 100))
    temp_score = min(100, max(0, (1 - abs(data['temperature'].mean() - 25) / 25) * 100))
    return round((moisture_score + light_score + temp_score) / 3, 1)

def create_moisture_chart(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['timestamp'], y=data['soil_moisture'],
                            mode='lines', name='Soil Moisture', line=dict(color='blue')))
    fig.update_layout(title='Soil Moisture Over Time', xaxis_title='Time', yaxis_title='Moisture (%)', height=300, width=600)
    return fig.to_html(full_html=False)

def create_light_chart(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['timestamp'], y=data['light_level'],
                            mode='lines', name='Light Level', line=dict(color='orange')))
    fig.update_layout(title='Light Level Over Time', xaxis_title='Time', yaxis_title='Light (lux)', height=300, width=600)
    return fig.to_html(full_html=False)

def create_temperature_chart(data):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['timestamp'], y=data['temperature'],
                            mode='lines', name='Temperature', line=dict(color='red')))
    fig.update_layout(title='Temperature Over Time', xaxis_title='Time', yaxis_title='Temperature (°C)', height=300, width=600)
    return fig.to_html(full_html=False)

def create_health_chart(data):
    health_scores = [calculate_health_score(data.iloc[max(0, i-5):i+1]) for i in range(len(data))]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['timestamp'], y=health_scores,
                            mode='lines', name='Health Score', line=dict(color='green')))
    fig.update_layout(title='Plant Health Score Over Time', xaxis_title='Time', yaxis_title='Health Score', height=300, width=600)
    return fig.to_html(full_html=False)

def generate_alerts(data):
    alerts = []
    if data['soil_moisture'].iloc[-1] < 30:
        alerts.append({
            'title': 'Low Soil Moisture',
            'message': 'Plant needs watering',
            'severity': 'warning',
            'time': data['timestamp'].iloc[-1]
        })
    if data['light_level'].iloc[-1] < 500:
        alerts.append({
            'title': 'Low Light Level',
            'message': 'Plant needs more light',
            'severity': 'warning',
            'time': data['timestamp'].iloc[-1]
        })
    if data['temperature'].iloc[-1] > 30:
        alerts.append({
            'title': 'High Temperature',
            'message': 'Plant is too hot',
            'severity': 'danger',
            'time': data['timestamp'].iloc[-1]
        })
    return alerts

@app.route('/')
def serve(path):
    if path != "" and os.path.exists("frontend/build/" + path):
        return send_from_directory('frontend/build/', path)
    else:
        return send_from_directory('frontend/build/','index.html')

    

@app.errorhandler(404)
def not_found(e):
    if os.path.exists(os.path.join(app.static_folder,'index.html')):
        return send_from_directory(app.static_folder,'index.html')
    return '404 Not Found', 404

# debugging lines 
@app.before_request
def log_request_info():
    print(f"\n-- Incoming {request.method} request ---")
    print("Path:", request.path)
    print("Headers", dict(request.headers))
    try :
        print("Body", request.get_json())
    except:
        print("NO JSON BODY")
    print("----------------------------\n")



if __name__ == '__main__':
    app.run(debug=True)



