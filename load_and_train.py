# this file is to load data from dataset to train the model
# downloaded and unzipped the dataset


import os
import pandas as pd
from pathlib import Path
import logging
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from PIL import Image
import numpy as np
import json


# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / 'dataset' / 'PlantVillage'
PROCESSED_PATH = BASE_DIR / 'processed_dataset' / 'PlantVillage'
CSV_DIR = BASE_DIR / 'csv runs'
CSV_OUTPUT = CSV_DIR / 'plantvillage_labels.csv'
MODELS_DIR = BASE_DIR / 'models'

# Create output directories
CSV_DIR.mkdir(exist_ok=True)
PROCESSED_PATH.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

def load_plantvillage_data():
    """Load image paths and extract species/health labels from PlantVillage dataset."""
    data = []
    for img_path in DATASET_PATH.glob('**/*.jpg'):
        folder_name = img_path.parent.name
        try:
            # Handle cases where folder name might not split cleanly
            parts = folder_name.split('_', 1)
            if len(parts) < 2:
                logger.warning(f"Skipping {folder_name}: Invalid format")
                continue
            species, health = parts
        except ValueError:
            logger.warning(f"Skipping {folder_name}: Invalid format")
            continue
        data.append({
            'image_path': str(img_path),
            'species': species,
            'health': health
        })
    df = pd.DataFrame(data)
    if df.empty:
        logger.error("No images found in dataset!")
        return None
    logger.info(f"Loaded {len(df)} images")
    df.to_csv(CSV_OUTPUT, index=False)
    logger.info(f"Saved labels to {CSV_OUTPUT}")
    return df

def preprocess_images(df):
    """Resize images to 224x224 and save to processed_dataset."""
    for _, row in df.iterrows():
        img_path = Path(row['image_path'])
        output_folder = PROCESSED_PATH / img_path.parent.name
        output_folder.mkdir(exist_ok=True)
        output_path = output_folder / img_path.name
        try:
            img = Image.open(img_path).resize((224, 224))
            img.save(output_path)
        except Exception as e:
            logger.warning(f"Failed to process {img_path}: {str(e)}")
    
    logger.info(f"Preprocessed images saved to {PROCESSED_PATH}")
    df['image_path'] = df['image_path'].str.replace(str(DATASET_PATH), str(PROCESSED_PATH))
    df.to_csv(CSV_OUTPUT, index=False)
    return df

def train_model(df, target_column, model_name):
    """Train a MobileNetV2 model for species or health classification."""
    IMG_SIZE = (224, 224)
    BATCH_SIZE = 32
    NUM_CLASSES = df[target_column].nunique()

    # Prepare data generator
    datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        shear_range=0.2,
        zoom_range=0.2,
        horizontal_flip=True,
        validation_split=0.2
    )

    # Create generators
    train_generator = datagen.flow_from_dataframe(
        df,
        x_col='image_path',
        y_col=target_column,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='training'
    )
    validation_generator = datagen.flow_from_dataframe(
        df,
        x_col='image_path',
        y_col=target_column,
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        subset='validation'
    )

    # Load MobileNetV2
    base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=(*IMG_SIZE, 3))
    base_model.trainable = False

    # Add custom layers
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation='relu')(x)
    predictions = Dense(NUM_CLASSES, activation='softmax')(x)
    model = Model(inputs=base_model.input, outputs=predictions)

    # Compile
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

    # Train
    model.fit(
        train_generator,
        epochs=10,
        validation_data=validation_generator
    )

    # Save model
    model_path = MODELS_DIR / f'{model_name}.h5'
    model.save(model_path)
    logger.info(f"Saved {model_name} to {model_path}")

    # Save labels
    labels = list(train_generator.class_indices.keys())
    with open(MODELS_DIR / f'{model_name}_labels.json', 'w') as f:
        json.dump(labels, f)
    logger.info(f"Saved {model_name} labels to {MODELS_DIR / f'{model_name}_labels.json'}")

def test_model(image_path, model_name):
    """Test a trained model on a single image."""
    model = tf.keras.models.load_model(MODELS_DIR / f'{model_name}.h5')
    with open(MODELS_DIR / f'{model_name}_labels.json') as f:
        labels = json.load(f)
    
    img = Image.open(image_path).resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    pred = model.predict(img_array)
    idx = np.argmax(pred, axis=1)[0]
    confidence = float(pred[0][idx])
    
    logger.info(f"Predicted {model_name}: {labels[idx]} (Confidence: {confidence:.2f})")
    return labels[idx], confidence

if __name__ == "__main__":
    # Load dataset
    df = load_plantvillage_data()
    if df is not None:
        # Preprocess images
        df = preprocess_images(df)
        # Train models
        train_model(df, 'species', 'plant_species_model')
        train_model(df, 'health', 'plant_health_model')
        # Test on a sample image
        test_image = df['image_path'].iloc[0]
        species, species_conf = test_model(test_image, 'plant_species_model')
        health, health_conf = test_model(test_image, 'plant_health_model')
