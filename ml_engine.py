import cv2
from image_utils import load_resize_image, is_image_blurry, calculate_image_features

# Placeholder for now – replace with actual ML logic later
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
    
    # Future ML-based predictions
    plant_type = classify_plant(img)  # e.g., Tomato, Mint, etc.
    health_status = diagnose_health(img, features)  # Healthy, Deficiency, etc.
    suggestions = generate_suggestions(health_status, features)

    return {
        "status": "ok",
        "plant_type": plant_type,
        "health_status": health_status,
        "features": features,
        "suggestions": suggestions
    }

def classify_plant(img):
    # Dummy classifier: add your trained model later
    return "Tomato (guess)"

def diagnose_health(img, features):
    # Basic rule-based logic
    if features.get('avg_green', 0) < 50:
        return "Possible nitrogen deficiency"
    elif features.get('contrast', 0) < 20:
        return "Low contrast – check lighting or water stress"
    return "Healthy"

def generate_suggestions(health_status, features):
    if "deficiency" in health_status:
        return [
            "Use a nitrogen-rich fertilizer",
            "Test the soil nutrient levels"
        ]
    elif "water" in health_status:
        return [
            "Ensure the plant receives adequate light",
            "Adjust watering schedule – avoid overwatering"
        ]
    else:
        return ["No immediate action needed"]




