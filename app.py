import cv2
import os
import csv
import re
import json
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session, jsonify
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

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


app = Flask(__name__, static_folder='static')
app.secret_key = '_my_project_secret_key_'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'Uploads')
CSV_DIR = os.path.join(BASE_DIR, 'csv runs')
DB_PATH = os.path.join(BASE_DIR, 'plantpulse.db')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


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
    return render_template('index.html')

    

@app.route('/photo', methods=['GET', 'POST'])
def photo():
    if request.method == 'POST':
        if 'photo' not in request.files:
            return jsonify({"success": False, "message": "No file part in request"}), 400
        
        file = request.files['photo']
        
        if file.filename == '':
            return jsonify({"success": False, "message": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"success": False, "message": "File type not allowed. Please upload .jpg, .png, or .jpeg"}), 400
        
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)
        if file_length > 5 * 1024 * 1024:
            return jsonify({"success": False, "message": "File too large. Maximum size is 5MB"}), 400
        
        try:
            Image.open(file).verify()
            file.seek(0)
            
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            img = cv2.imread(filepath)
            if img is None:
                os.remove(filepath)
                return jsonify({"success": False, "message": "Error: Could not read image file."}), 400
            
            img = cv2.resize(img, (512, 512))
            height, width = img.shape[:2]
            
            if height < 100 or width < 100:
                os.remove(filepath)
                return jsonify({"success": False, "message": "Error: Image is too small."}), 400
            
            blur = cv2.Laplacian(img, cv2.CV_64F).var()
            if blur < 100:
                result = "Image is blurry! Please upload a clearer image."
                return jsonify({"success": True, "message": f"Image Saved: {filename}", "filename": filename, "result": result}), 200
            
            edges = cv2.Canny(img, 100, 200)
            edge_density = np.sum(edges) / 255 / (img.shape[0] * img.shape[1])
            edge_count = np.sum(edges) / 255
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            brown_mask = cv2.inRange(hsv, (10, 20, 0), (40, 100, 255))
            brown_percent = np.sum(brown_mask) / (img.shape[0] * img.shape[1]) * 100
            green_mask = cv2.inRange(hsv, (35, 40, 40), (85, 255, 255))
            green_percent = np.sum(green_mask) / (img.shape[0] * img.shape[1]) * 100
            color_var = np.std(img)
            avg_color = img.mean(axis=0).mean(axis=0)
            
            is_soil = edge_count > 5000 and brown_percent > 60 and color_var > 50 and edge_density > 10
            is_plant = green_percent > 60 and edge_density > 5 and color_var < 50
            
            brightness = img.mean()
            content = "unknown"
            
            if is_plant and not is_soil:
                content = 'plant'
            elif is_soil and not is_plant:
                content = "soil"
            elif is_soil and is_plant and green_percent > 40 and brown_percent > 40:
                content = "Plant and Soil"
            
            result = ""
            if content == "unknown":
                result = "Not soil or plant–upload a soil or plant pic!"
            elif content == "soil":
                result = "Soil: Wet" if avg_color[0] < 70 else "Soil: Dry"
            elif content == "plant":
                yellow_mask = cv2.inRange(hsv, (20, 40, 40), (35, 255, 255))
                yellow_percent = np.sum(yellow_mask) / (img.shape[0] * img.shape[1]) * 100
                result = "Plant: Healthy" if yellow_percent < 20 else "Plant: Stressed"
            elif content == "Plant and Soil":
                yellow_mask = cv2.inRange(hsv, (20, 40, 40), (35, 255, 255))
                yellow_percent = np.sum(yellow_mask) / (img.shape[0] * img.shape[1]) * 100
                soil_status = "Wet" if avg_color[0] < 70 else "Dry"
                plant_status = "Healthy" if yellow_percent < 20 else "Stressed"
                result = f"{soil_status}, {plant_status}"
                if soil_status == "Wet" and plant_status == "Stressed":
                    result += "–Overwatered?"
                elif soil_status == "Dry" and plant_status == "Stressed":
                    result += "–Underwatered?"
            
            elif brightness < 50:
                result = "Image is too dark!"
            elif brightness > 200:
                result = "Too bright–reduce brightness."
            else:
                result = "Balanced"
            
            return jsonify({"success": True, "message": f"Image Saved: {filename}", "filename": filename, "result": result}), 200
        
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({"success": False, "message": f"Error processing image: {str(e)}"}), 500
    
    # For GET requests, just return a simple JSON message or status
    return jsonify({"message": "Please POST an image file to this endpoint"}), 200

@app.route('/Uploads/<filename>')
def serve_upload(filename):
    filename = secure_filename(filename)
    if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        logger.error(f"File not found: {filename}")
        return "File not found", 404
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/query', methods=['GET', 'POST'])
def query():
    if "username" not in session:
        return jsonify({"success": False, "error": "Unauthorized"}), 401
    
    username = session["username"]
    Data, load_error = load_latest_data(username)
    
    if load_error:
        return jsonify({"success": False, "error": load_error}), 500
    
    if request.method == 'POST':
        try:
            hour = int(request.form['hour'])
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
    
    return jsonify({"message": "Please POST an 'hour' parameter to query data."}), 200


@app.route('/zoom', methods=['GET', 'POST'])
def zoom():
    if "username" not in session:
        return jsonify({"error": "Unauthorized: Please log in to view your data."}), 401
    
    username = session["username"]
    Data, load_error = load_latest_data(username)

    if Data.empty:
        logger.warning(f"Zoom route: No data available for user {username}")
        return jsonify({"error": f"No data available - {load_error}"}), 404

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
        return redirect(url_for("login"))
    
    user_data_file = f"data/{username}.csv"
    
    if os.path.exists(user_data_file):
        Data = pd.read_csv(user_data_file)
    else:
        Data, error = load_latest_data()
        if error or Data.empty:
            return render_template('dashboard.html',
                                   error=error or "No data available",
                                   username=username,
                                   stats=None,
                                   moisture_chart=None,
                                   light_chart=None,
                                   temperature_chart=None,
                                   health_chart=None,
                                   alerts=None)
    
    stats = {
        "average_moisture": round(Data['soil_moisture'].mean(), 2),
        "average_light": round(Data['light_level'].mean(), 2),
        "average_temperature": round(Data['temperature'].mean(), 2),
    }

    moisture_chart = create_moisture_chart(Data)
    light_chart = create_light_chart(Data)
    temperature_chart = create_temperature_chart(Data)
    health_chart = create_health_chart(Data)
    alerts = generate_alerts(Data)
    
    return render_template('dashboard.html',
                           username=username,
                           stats=stats,
                           moisture_chart=moisture_chart,  # fixed typo here
                           light_chart=light_chart,
                           temperature_chart=temperature_chart,
                           health_chart=health_chart,
                           alerts=alerts)

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
    if request.method == "POST":
        data = request.get_json()
        username = data.get("username", "").strip()
        email = data.get("email", "").strip()
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


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.get_json()
        username = data.get("username", "").strip()

        if not username:
            return jsonify({"success": False, "message": "Username is required"}), 400

        users = load_users()
        if username not in users:
            return jsonify({"success": False, "message": "User not found"}), 404

        session['username'] = username
        return jsonify({"success": True, "message": "Login successful", "username": username}), 200
    return render_template('login.html')


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

if __name__ == '__main__':
    app.run(debug=True)



