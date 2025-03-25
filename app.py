import os
from flask import Flask, render_template, request, send_from_directory
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from werkzeug.utils import secure_filename


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
            return render_template('photo.html', message=f"Image Saved: {filename}",filename=filename)
        
        return render_template('photo.html', message="Invalid file type! Use .jpg, .png, or .jpeg")
    return render_template('photo.html', message=None)

@app.route('/uploads/<fileneame>')
def serve_upload(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER']
    )


# Keep your query and zoom routes—unchanged
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
    return "Exiting—See you next time! (close tab to stop.)"

if __name__ == '__main__':
    app.run(debug=True)



