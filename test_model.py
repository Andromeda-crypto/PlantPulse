import torch
from torchvision import models, transforms
from PIL import Image
import json
import os

from train_species import create_model

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def load_model(model_path, num_classes):
    model = models.mobilenet_v2(pretrained=False)
    model.classifier[1] = torch.nn.Sequential(
        torch.nn.Linear(model.last_channel, 128),
        torch.nn.ReLU(),
        torch.nn.Dropout(0.3),
        torch.nn.Linear(128, num_classes)
    )
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.eval()
    return model.to(device)

def predict(image_path, model, labels):
    model.eval()
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])
    img = Image.open(image_path).convert('RGB')
    img = transform(img).unsqueeze(0).to(device)
    with torch.no_grad():
        outputs = model(img)
        _, pred = torch.max(outputs, 1)
    return labels[pred.item()]

def main():  
    with open('models/plant_species_labels.json') as f:
        species_labels = json.load(f)
    model = create_model(len(species_labels))
    model.load_state_dict(torch.load('models/plant_species_model.pth', map_location=torch.device('cpu')))
    model.to(device)
    model.eval()
    base_test_dir = 'processed_dataset/plant_images_subset'
    correct_count = 0
    total_count = 0

    for class_name in os.listdir(base_test_dir):
        class_dir = os.path.join(base_test_dir,class_name)
        if os.path.isdir(class_dir):
            for filename in os.listdir(class_dir):
                if filename.lower().endswith(('.jpg','.jpeg','.png')):
                    image_path = os.path.join(class_dir,filename)
                    species_pred = predict(image_path,model,species_labels)
                    is_correct = (species_pred == class_name)
                    total_count += 1
                    correct_count = int(is_correct)
                    print(f"{class_name}/{filename} -> Predicted : {species_pred} -> ✅ if is_correct else ❌")

    accuracy = (correct_count/total_count) if total_count > 0 else 0
    print(f"\nOverall Accuracy : {accuracy:.2%}")

       
    

if __name__ == "__main__":
    main()
