import cv2
img = cv2.imread('uploads/wet-ground-pot-closeup-macro-260nw-527370445.jpg')
print(img.shape)
avg_color =  img.mean(axis=0).mean(axis=0)
print("Avg_RGB : ",avg_color)