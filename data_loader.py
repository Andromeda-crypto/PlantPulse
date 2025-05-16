import torch
from torchvision import datasets, transforms
from torch.utils.data import DataLoader

def get_data_loaders(data_dir,batch_size=32,img_size = 224,val_split=0.2):
    transform = transforms.Compose([
        transforms.Resize((img_size, img_size)),
        transforms.RandomHorizontalFlip(),
        transforms.RandomRotation(20),
        transforms.RandomResizedCrop(img_size,scale=(0.8,1.0)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485,0.456,0.406],
                             std=[0.229,0.224,0.225])


    ])

    dataset = datasets.ImageFolder(root=data_dir,transform=transform)
    train_size = int((1 - val_split) * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(dataset,[train_size,val_size])
    train_loader = DataLoader(train_dataset,batch_size=batch_size,shuffle=True, num_workers=4)
    val_loader = DataLoader(val_dataset,batch_size=batch_size,shuffle=True,num_workers= 4)
    print("Data loaders ready. Starting training.....") # testing training 

    return train_loader, val_loader, dataset.classes