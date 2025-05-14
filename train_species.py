import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.models import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D
from tensorflow.keras.models import Model

# parameters
IMG_SIZE = (224,224)
BATCH_SIZE = 32
DATASET_DIR = 'dataset/PlantVillage/processed'
NUM_CLASSES = len(os.listdir(DATASET_DIR))

base_model = MobileNetV2(weights= 'imagenet', include_top = False, input_shape=(*IMG_SIZE, 3))
base_model.trainable = False

x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(128,activation='relu')(x)

predictions = Dense(NUM_CLASSES, activation='softmax')(x)
model = Model(inputs=base_model.input,outputs=predictions)

model.complile(optimizer='adam',loss='categorical_crossentropy',metrics=['accuracy'])

train_datagen = ImageDataGenerator(
    rescale = 1./255,
    rotation_range = 20,
    width_shift_range = 0.2,
    height_shift_range = 0.2,
    shear_range = 0.2,
    zoom_range = 0.2,
    horizontal_flip = True,
    validation_split = 0.2
)

train_generator = train_datagen.flow_from_directory(
    DATASET_DIR,
    target_size = IMG_SIZE,
    batch_size = BATCH_SIZE,
    clas_mode = 'categorical',
    subset = 'training'

)

validation_generator = train_datagen.flow_from_directory(
    DATASET_DIR,
    target_size = IMG_SIZE,
    batch_size = BATCH_SIZE,
    class_mode = 'categorical',
    subset = 'training'
)
# train the model
model.fit(
    train_generator,
    epochs = 10,
    validatioin_data = validation_generator
)

# save the model

os.makedirs('models',exist_ok=True)
model.save('models/plant_disease_model.h5')