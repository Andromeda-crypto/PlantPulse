import cv2
import os
from flask import Flask, render_template, request, send_from_directory, redirect, url_for, session
import pandas as pd
import plotly.graph_objects as go
from jinja2 import TemplateNotFound
from plotly.subplots import make_subplots
from werkzeug.utils import secure_filename
import numpy as np
import logging
from PIL import Image
import sqlite3

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


app = Flask(__name__, static_folder='static')
app.secret_key = 'your_secret_key'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'Uploads')
CSV_DIR = os.path.join(BASE_DIR, 'csv runs')
DB_PATH = os.path.join(BASE_DIR, 'plantpulse.db')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Create directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CSV_DIR, exist_ok=True)

def load_latest_data():
    """Load the latest 168 readings from SQLite."""
    try:
        conn = sqlite3.connect(DB_PATH)  
        df = pd.read_sql('SELECT * FROM readings ORDER BY timestamp DESC LIMIT 168', conn)
        conn.close()
        if df.empty:
            return pd.DataFrame(), "No data in database"
        return df, None
    except Exception as e:
        return pd.DataFrame(), f"Database error: {str(e)}"

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    if "username" in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))
    

@app.route('/photo', methods=['GET', 'POST'])
def photo():
    if request.method == 'POST':
        if 'photo' not in request.files:
            return render_template('photo.html', message="No file part in request")
        file = request.files['photo']
        if file.filename == '':
            return render_template('photo.html', message="No file selected")
        if not allowed_file(file.filename):
            return render_template('photo.html', message="File type not allowed. Please upload .jpg, .png, or .jpeg")
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)
        if file_length > 5 * 1024 * 1024:
            return render_template('photo.html', message="File too large. Maximum size is 5MB")
        try:
            Image.open(file).verify()
            file.seek(0)
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            img = cv2.imread(filepath)
            if img is None:
                os.remove(filepath)
                return render_template('photo.html', message="Error: Could not read image file.")
            img = cv2.resize(img, (512, 512))
            height, width = img.shape[:2]
            if height < 100 or width < 100:
                os.remove(filepath)
                return render_template('photo.html', message="Error: Image is too small.")
            blur = cv2.Laplacian(img, cv2.CV_64F).var()
            if blur < 100:
                result = "Image is blurry! Please upload a clearer image."
                return render_template('photo.html', message=f"Image Saved: {filename}", filename=filename, result=result)
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
            return render_template('photo.html', message=f"Image Saved: {filename}", filename=filename, result=result)
        except Exception as e:
            if os.path.exists(filepath):
                os.remove(filepath)
            return render_template('photo.html', message=f"Error processing image: {str(e)}")
    try:
        return render_template('photo.html', message=None)
    except TemplateNotFound:
        logger.error("Photo template not found")
        return "Error: Photo template not found.", 500

@app.route('/Uploads/<filename>')
def serve_upload(filename):
    filename = secure_filename(filename)
    if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        logger.error(f"File not found: {filename}")
        return "File not found", 404
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/query', methods=['GET', 'POST'])
def query():
    Data, load_error = load_latest_data()
    if load_error:
        return render_template('query.html', error=load_error)
    if request.method == 'POST':
        try:
            hour = int(request.form['hour'])
            if 0 <= hour < len(Data):
                row = Data.iloc[hour]
                result = (
                    f"Hour {hour}:<br>"
                    f"Soil Moisture: {row['soil_moisture']:.2f}%<br>"
                    f"Light Level: {row['light_level']:.2f} lux<br>"
                    f"Temperature: {row['temperature']:.2f}°C<br>"
                    f"Health: {row['health_status']}"
                )
            else:
                result = f"Error: Hour must be between 0 and {len(Data)-1}!"
        except ValueError:
            result = "Error: Hour must be a number!"
        return render_template('query.html', result=result)
    try:
        return render_template('query.html', result=None)
    except TemplateNotFound:
        logger.error("Query template not found")
        return "Error: Query template not found.", 500

@app.route('/zoom', methods=['GET', 'POST'])
def zoom():
    Data, load_error = load_latest_data()
    if Data.empty:
        logger.warning("Zoom route: No data available")
        return render_template('zoom.html', error=f"Error: No data available - {load_error}")
    if request.method == 'POST':
        logger.info(f"Received form data: {request.form}")
        try:
            start_hour_str = request.form.get('start_hour', '').strip()
            end_hour_str = request.form.get('end_hour', '').strip()
            if not start_hour_str or not end_hour_str:
                raise ValueError("Start hour or end hour is missing or empty")
            start_hour = int(start_hour_str)
            end_hour = int(end_hour_str)
            logger.info(f"Parsed start_hour: {start_hour}, end_hour: {end_hour}")
            if not (0 <= start_hour < len(Data) and 0 <= end_hour < len(Data)):
                return render_template('zoom.html', error=f"Hours must be between 0 and {len(Data)-1}!")
            if start_hour > end_hour:
                return render_template('zoom.html', error="Start hour must be less than or equal to end hour!")
            zoomed_data = Data.iloc[start_hour:end_hour + 1]
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
            return render_template('zoom.html', plot_html=plot_html, error=None)
        except ValueError as e:
            logger.error(f"ValueError in zoom route: {str(e)}, Form data: {request.form}")
            return render_template('zoom.html', error=f"Invalid input: {str(e)}")
        except KeyError as e:
            logger.error(f"KeyError in zoom route: {str(e)}, Form data: {request.form}")
            return render_template('zoom.html', error=f"Form error: Missing field {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error in zoom route: {str(e)}, Form data: {request.form}")
            return render_template('zoom.html', error=f"Error generating plot: {str(e)}")
    try:
        return render_template('zoom.html', plot_html=None, error=None)
    except TemplateNotFound:
        logger.error("Zoom template not found")
        return "Error: Zoom template not found.", 500

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
        if error:
            return render_template('dashboard.html',error=error,username=username,stats=None,moisture_chart=None, light_chart=None,
                                  temperature_chart=None, health_chart=None)
        
    stats = {
        "average_moisture": round(Data('soil_moisture').mean(),2),
        "average_light": round(Data('light_level').mean(),2),
        "average_temperature": round(Data('temperature').mean(),2),

    }

    moisture_chart = create_moisture_chart(Data)
    light_chart = create_light_chart(Data)
    temperature_chart = create_temperature_chart(Data)
    health_chart = create_health_chart(Data)
    alerts = generate_alerts(Data)
    
    return render_template('dashboard.html',username=username,stats=stats,mositure_chart=moisture_chart, light_chart=light_chart,temperature_chart=temperature_chart,
                           health_chart=health_chart,alerts=alerts)


@app.route('/signup',methods=["GET", "POST"])
def signup():
    error = None
    if request.method == "POST":
        username = request.form.get("username","").strip()
        email = request.form.get('email', '').strip()
        password = request.form.get("password","").strip()
        confirm_password = request.form.get("confirm_password","").strip()

        if not username :
            error = "Username is required\nPlease enter a username"
        elif not email:
            error = "Email is required\nPlease enter an email"
        elif not password:  
            error = "Password is required\nPlease enter a password"
        elif confirm_password != password:
            error = "Passwords do not match\nPlease confirm your password"
        else:
            # TODO : Add logic to save user data to database
            session['username'] = username
            return redirect(url_for('home'))
    return render_template('signup.html', error=error)


@app.route('/login',methods= ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username  = request.form.get('username').strip()
        if username:
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Please enter a username')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username',None)
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



