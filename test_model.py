import torch
from torchvision import models, transforms
from PIL import Image
import json

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
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                             std=[0.229, 0.224, 0.225])
    ])
    img = Image.open(image_path).convert('RGB')
    img_t = transform(img).unsqueeze(0).to(device)
    with torch.no_grad():
        output = model(img_t)
        _, pred = torch.max(output, 1)
    return labels[pred.item()]

def main():
    image_path = 'processed_dataset/PlantVillage_species/some_class/image.jpg'  # test image path

    # Load species model & labels
    with open('models/plant_species_labels.json') as f:
        species_labels = json.load(f)
    species_model = load_model('models/plant_species_model.pth', len(species_labels))

    species_pred = predict(image_path, species_model, species_labels)
    print(f"Predicted species: {species_pred}")

    # Similarly, load health model & labels if needed

if __name__ == "__main__":
    main()
