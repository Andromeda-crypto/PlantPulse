import os
import cv2
import numpy as np
from PIL import Image
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', }

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file(file):
    if file.filename == '':
        return False, "No file selected"
    if not allowed_file(file.filename):
        return False, "File type not allowed.\nUpload png, jpeg or jpg files only"
    file.seek(0,os.SEEK_END)
    if file.tell() > 5 * 1024 *1024:
        return False, "File size eceeds 5MB"
    file.seek(0)
    return True

def save_file(file,uploads):
    filename = secure_filename(file.filename)
    filepath = os.path.join(uploads,filename)
    file.save(filepath)
    return filename, filepath

def load_resize_image(filepath,size=(521,512)):
    img = cv2.imread(filepath)
    if img is None:
        return None, "Could not read image"
    img = cv2.resize(img,size)
    return img, ""

def is_image_blurry(image,threshold= 100):
    blur = cv2.Laplacian(image,cv2.CV_64F).var()
    return blur < threshold

def calculate_image_features(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    edges = cv2.Canny(img, 100, 200)
    edge_count = np.sum(edges) / 255
    edge_density = edge_count / (img.shape[0] * img.shape[1])
    brown_mask = cv2.inRange(hsv, (10, 20, 0), (40, 100, 255))
    brown_percent = np.sum(brown_mask) / (img.shape[0] * img.shape[1]) * 100
    green_mask = cv2.inRange(hsv, (35, 40, 40), (85, 255, 255))
    green_percent = np.sum(green_mask) / (img.shape[0] * img.shape[1]) * 100
    color_var = np.std(img)
    avg_color = img.mean(axis=0).mean(axis=0)
    brightness = img.mean()
    return {
        "edge_count": edge_count,
        "edge_density": edge_density,
        "brown_percent": brown_percent,
        "green_percent": green_percent,
        "color_var": color_var,
        "avg_color": avg_color,
        "brightness": brightness,
        "hsv": hsv,
        "img": img
    }

def analyze_content(features):
    is_soil = features["brown_percent"] > 60 and features["edge_count"] > 5000 and features['color_var'] > 50 and features['edge_density'] > 10
    is_plant = features['green_percent'] > 60 and features["edge_density"] > 5 and features["color_var"] < 50

    if is_plant and not is_soil:
        return "plant"
    elif is_soil and not is_plant:
        return "soil"
    elif is_soil and is_plant and features['green_percent']>40 and features["brown_percent"]> 40:
        return "Plant and Soil"
    return "Unknown"

def build_result_message(content, features):
    avg_color = features["avg_color"]
    brightness = features["brightness"]
    hsv = features["hsv"]
    img = features["img"]

    if content == "unknown":
        return "Not soil or plant–upload a soil or plant pic!"
    elif content == "soil":
        return "Soil: Wet" if avg_color[0] < 70 else "Soil: Dry"
    elif content == "plant":
        yellow_mask = cv2.inRange(hsv, (20, 40, 40), (35, 255, 255))
        yellow_percent = np.sum(yellow_mask) / (img.shape[0] * img.shape[1]) * 100
        return "Plant: Healthy" if yellow_percent < 20 else "Plant: Stressed"
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
        return result
    elif brightness < 50:
        return "Image is too dark!"
    elif brightness > 200:
        return "Too bright–reduce brightness."
    else:
        return "Balanced"

