from PIL import Image
import os

input_dir = 'dataset/PlantVillage'
output_dir = 'dataset/PlantVillage/processed'
os.makedirs(output_dir,exist_ok = True)

for root , _ , files in os.walk(input_dir):
    for file in files:
        if file.endswith('.jpg','.jepg', '.png'):
            img_path = os.path.join(root, file)
            img = Image.open(img_path)
            img = img.resize((224, 224))  # Resize to 224x224
            img.save(os.path.join(output_dir, file))