import cv2
import os
from flask import Flask, render_template, request, send_from_directory
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from werkzeug.utils import secure_filename
import numpy as np


app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Load data
Data = pd.read_csv('csv runs/plant_data_2025-03-10_10-47.csv')



@app.route('/')
def home():
    print("Static path:", os.path.abspath('static/style.css'))  # Debug
    return render_template('index.html')

print("Upload folder:", os.path.abspath(app.config['UPLOAD_FOLDER'])) # checking



@app.route('/photo', methods=['GET', 'POST'])
def photo():
    if request.method == 'POST':
        if 'photo' not in request.files:
            return render_template('photo.html', message="No File Uploaded!")
        file = request.files['photo']
        if file.filename == "":
            return render_template('photo.html', message="No File Selected!")
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            img = cv2.imread(filepath)
            blur = cv2.Laplacian(img,cv2.CV_64F).var()
            if blur < 100:
                result = "Image is blurry! Please upload a clearer image."
                return render_template('photo.html', message=f"Image Saved : {filename}", filename=filename,result=result)
            
            edges = cv2.Canny(img,100,200)
            edge_density = np.sum(edges)/(img.shape[0]*img.shape[1])
            edge_count = np.sum(edges)/255
            hsv = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
            brown_mask = cv2.inRange(hsv,(10,20,0),(40,100,255))
            brown_percent = np.sum(brown_mask)/(img.shape[0] * img.shape[1]) * 100
            green_mask = cv2.inRange(hsv,(35,40,40),(85,255,255))
            green_percent = np.sum(green_mask)/(img.shape[0] * img.shape[1]) * 100
            color_var = np.std(img)

            is_soil = edge_count > 5000 and brown_percent > 60 and color_var > 50 and edge_density > 10
            is_plant = green_percent > 60 and edge_density > 5 and color_var < 50
            brightness = img.mean()
            if is_plant and not is_soil:
                content = 'plant'
            elif is_soil and not is_plant:
                content = "soil"
            elif is_soil and is_plant and green_percent > 40 and brown_percent > 40:
                content = "Plant and soil"
            else:
                content = "unknown"
            

            result = ""
            if content == "unknown":
                result = "Not soil or plant–upload a soil or plant pic!"
            elif content =="soil":
                avg_color = img.mean(axis=0).mean(axis=0)
                result = "Soil : Wet" if avg_color[0] < 70 else "Soil : Dry"
            elif content =="plant":
                yellow_mask = cv2.inRange(hsv,(20,40,40) , (35,255,255))
                yellow_percent = np.sum(yellow_mask)/(img.shape[0] * img.shape[1]) * 100
                result = "Plant : Healthy" if yellow_percent<20 else "Plant : Stressed"
            elif content =="Plant and Soil":
                is_soil = edge_count > 5000 and brown_percent > 30 and color_var > 50 and edge_density>10
                yellow_mask = cv2.inRange(hsv,(20,40,40),(35,255,255))
                yellow_percent = np.sum(yellow_mask)/(img.shape[0]*img.shape[1]) * 100
                soil_status = "Wet" if avg_color[0] < 70 else  "Dry"
                plant_status = "Healthy" if yellow_percent < 20 else  "tressed"
                result = f"{soil_status} , {plant_status}"
                if soil_status == "Wet" and plant_status == "Stressed":
                    result += "–Overwatered ?"
                elif soil_status == "Dry" and plant_status == "Stressed":
                    result += "–Underwatered ?"
                
        
            elif brightness < 50:
                result = "Image is too dark! Please upload a brighter image for better analysis."
                return render_template('photo.html', message=f"IMage Saved : {filename}", filename=filename,result=result)
            elif brightness > 200:
                result = "Too bright–reduce brightness for better analysis."
                return render_template('photo.html', message=f"Image Saved : {filename}", filename=filename,result=result)
            else:
                    result =+ "Balanced"
            print("Image content:", content)
            print("Image result:", result)            
            return render_template('photo.html', message=f"Image Saved: {filename}", filename=filename,result = result)
        
        return render_template('photo.html', message="Invalid file type! Use .jpg, .png, or .jpeg")
    return render_template('photo.html', message=None)

@app.route('/uploads/<filename>')
def serve_upload(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],filename
    )



@app.route('/query', methods=['GET', 'POST'])
def query():
    if request.method == 'POST':
        hour = int(request.form['hour'])
        if 0 <= hour <= 167:
            row = Data.iloc[hour]
            result = (
                f"Hour {hour}:<br>"
                f"Soil Moisture: {row['Soilmoisture']:.2f}%<br>"
                f"Light Level: {row['Lightlevel']:.2f} lux<br>"
                f"Temperature: {row['Temperature']:.2f}°C<br>"
                f"Health: {row['Health_status']}"
            )
        else:
            result = "Error: Hour must be between 0 and 167!"
        return render_template('query.html', result=result)
    return render_template('query.html', result=None)


@app.route('/zoom', methods=['GET', 'POST'])
def zoom():
    if request.method == "POST":
        start_hour = int(request.form['start_hour'])
        end_hour = int(request.form['end_hour'])
        if 0 <= start_hour <= 167 and 0 <= end_hour <= 167 and start_hour <= end_hour:
            zoomed_data = Data.iloc[start_hour:end_hour + 1]
            fig = make_subplots(rows=3, cols=1, subplot_titles=('Soil Moisture', 'Light Level', 'Temperature'))
            fig.add_trace(go.Scatter(x=zoomed_data['Timestamp'], y=zoomed_data['Soilmoisture'], 
                                    mode='lines', name='Soil Moisture', line=dict(color='blue')), row=1, col=1)
            low_moisture = zoomed_data[zoomed_data['Health_status'] == 'Low moisture Plant needs more water']
            fig.add_trace(go.Scatter(x=low_moisture['Timestamp'], y=low_moisture['Soilmoisture'], 
                                    mode='markers', name='Low Moisture', marker=dict(color='red', size=10)), row=1, col=1)
            fig.add_trace(go.Scatter(x=zoomed_data['Timestamp'], y=zoomed_data['Lightlevel'], 
                                    mode='lines', name='Light Level', line=dict(color='orange')), row=2, col=1)
            low_light = zoomed_data[zoomed_data['Health_status'] == 'Low light Plant needs more light']
            fig.add_trace(go.Scatter(x=low_light['Timestamp'], y=low_light['Lightlevel'], 
                                    mode='markers', name='Low Light', marker=dict(color='yellow', size=10)), row=2, col=1)
            fig.add_trace(go.Scatter(x=zoomed_data['Timestamp'], y=zoomed_data['Temperature'], 
                                    mode='lines', name='Temperature', line=dict(color='red')), row=3, col=1)
            too_hot = zoomed_data[zoomed_data['Health_status'] == 'Too Hot Plant should be exposed to less heat']
            fig.add_trace(go.Scatter(x=too_hot['Timestamp'], y=too_hot['Temperature'], 
                                    mode='markers', name='Too Hot', marker=dict(color='purple', size=10)), row=3, col=1)
            fig.update_layout(height=800, width=1000, title_text="Zoomed Plant Data")
            fig.update_xaxes(title_text="Time", row=1, col=1)
            fig.update_xaxes(title_text="Time", row=2, col=1)
            fig.update_xaxes(title_text="Time", row=3, col=1)
            fig.update_yaxes(title_text="Moisture (%)", row=1, col=1)
            fig.update_yaxes(title_text="Light (lux)", row=2, col=1)
            fig.update_yaxes(title_text="Temperature (°C)", row=3, col=1)
            plot_html = fig.to_html(full_html=False)
            return render_template('zoom.html', plot_html=plot_html)
        else:
            return render_template('zoom.html', error="Invalid range—hours must be 0-167, start ≤ end!")
    return render_template('zoom.html', plot_html=None, error=None)

@app.route('/exit')
def exit():
    return "Exiting—See you next time! "

if __name__ == '__main__':
    app.run(debug=True)



