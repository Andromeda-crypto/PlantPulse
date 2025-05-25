import cv2
from image_utils import load_resize_image, is_image_blurry, calculate_image_features
# later: will import ML model loaders 

def analyze_plant_image(filepath):
    img, err = load_resize_image(filepath)
    if img is None:
        return {"status": "error", "message": err}
    if is_image_blurry(img):
        return {
            "status": "blurry",
            "message": "The image is too blurry for analysis. Try uploading a clearer photo."
        }
    
    features = calculate_image_features(img)

    plant_type = classify_plant(img) # Later
    health_status = diagnose_health(img,features) # later
    suggestions = generate_suggestions(health_status,features) # later 

    return {
        "status": "ok",
        "plant_type": plant_type,
        "health_status": health_status,
        "suggestions": suggestions,
        "features": features
    }

def classify_plant(img):
    # Dummy for now, will be replaced with actual ML model
    return "Unknown Plant Type"

def diagnose_health(img,features):
    # Dummy for now, will be replaced with actual ML model
    return "health status unknown"

def generate_suggestions(health_status, features):
    # Dummy for now, will be replaced with actual ML model
    if health_status == "health status unknown":
        return "No suggestions available"
    return "Suggestions based on health status"



