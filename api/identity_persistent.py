import numpy as np
import cv2
from PIL import Image
import torch
from facenet_pytorch import InceptionResnetV1, fixed_image_standardization
from torchvision.transforms import Compose, ToTensor, Resize

class FaceSimilarity:
    def __init__(self):
        self.model = InceptionResnetV1(pretrained='vggface2')
        self.transform = Compose([
            Resize((160, 160)),
            ToTensor(),
            fixed_image_standardization
        ])

    def extract_embedding(self, image_path):
        img = Image.open(image_path)
        face_cascae = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    
        )
        gray = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2GRAY)
        faces = face_cascae.detectMultiScale(gray, 1.1, 4)

        if len(faces) == 0:
            return None
        
        x, y, w, h = faces[0]
        face_img = Image.fromarray(
            np.array(img)[y:y+h, x:x+h]
        ).convert('RGB')

        x = self.transform(face_img).unsqueeze(0)

        with torch.no_grad():
            embedding = self.model(x)[0]
        
        return embedding.numpy()
    def compute_similarity(self, embedding1, embedding2, metric='cosine'):

        if metric == 'cosine':
            return np.dot(embedding1, embedding2) / (
                np.linalg.norm(embedding1) * np.linalg.norm(embedding2)
            )
        elif metric == 'euclidean':
            return np.linalg.norm(embedding1 - embedding2)
        else:
            raise ValueError("Invalid similarity metric")

def main():
    face_checker = FaceSimilarity()
    try:
        embedding1 = face_checker.extract_face_embedding('image1.jpg')
        embedding2 = face_checker.extract_face_embedding('image2.jpg')
        similarity = face_checker.compute_similarity(embedding1, embedding2)
        print(f"Face Similarity Score: {similarity}")

    except Exception as e:
        print(f"Error: {e}")