import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import models
from data_loader import get_data_loaders

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

def create_model(num_classes):
    model = models.mobilenet_v2(pretrained=True)
    for param in model.features.parameters():
        param.requires_grad = False

    model.classifier[1] = nn.Sequential(
        nn.Linear(model.last_channel, 128),
        nn.ReLU(),
        nn.Dropout(0.3),
        nn.Linear(128, num_classes)
    )
    return model.to(device)

def train(model, train_loader, val_loader, epochs=10):
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.classifier.parameters(), lr=0.001)

    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item() * inputs.size(0)
            _, preds = torch.max(outputs, 1)
            correct += (preds == labels).sum().item()
            total += labels.size(0)

        epoch_loss = running_loss / total
        epoch_acc = correct / total
        print(f"Epoch {epoch+1}/{epochs} - Loss: {epoch_loss:.4f} - Accuracy: {epoch_acc:.4f}")

        # Validation
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                val_loss += loss.item() * inputs.size(0)
                _, preds = torch.max(outputs, 1)
                val_correct += (preds == labels).sum().item()
                val_total += labels.size(0)

        val_loss /= val_total
        val_acc = val_correct / val_total
        print(f"Validation - Loss: {val_loss:.4f} - Accuracy: {val_acc:.4f}")

def main():
    DATA_DIR = 'processed_dataset/plant_images_subset'  # Update path as needed
    train_loader, val_loader, classes = get_data_loaders(DATA_DIR)
    model = create_model(len(classes))
    train(model, train_loader, val_loader, epochs=10)

    # Save model and labels
    torch.save(model.state_dict(), 'models/plant_species_model.pth')
    import json
    with open('models/plant_species_labels.json', 'w') as f:
        json.dump(classes, f)

if __name__ == "__main__":
    main()
