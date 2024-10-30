import numpy as np
import os
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import LabelEncoder
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
from PIL import Image

class NaiveBayes:
    def __init__(self):
        self.path = '../'

    def sep_classes(self, X, y):
        separated = {}
        for i in range(len(X)):
            feature_vals = X[i]
            c_name = y[i]
            if c_name not in separated:
                separated[c_name] = []
            separated[c_name].append(feature_vals)
        
        return separated
    
    def info(self, X):
        for feature in zip(*X):
            yield {
                'std': np.std(feature),
                'mean': np.mean(feature)
            }

    def gaussian(self, x, mean, std):
        exp = np.exp(-((x-mean)**2 / (2*std**2)))
        return exp / (np.sqrt(2*np.pi)*std)
    
    def fit(self, x, y):
        separated = self.sep_classes(x, y)
        self.class_summary = {}
        
        for class_name, feature_vals in separated.items():
            self.class_summary[class_name] = {
                'prior': len(feature_vals)/len(x),
                'summary': [i for i in self.info(feature_vals)]
            }
        return self.class_summary
    
    def predict(self, X):
        MAPs = []

        for row in X:
            joint_probs = {}

            for class_name, features in self.class_summary.items():
                total_features = min(len(features['summary']), len(row))
                prob = 1

                for idx in range(total_features):
                    feature = row[idx]
                    mean = features['summary'][idx]['mean']
                    stdev = features['summary'][idx]['std']
                    normal = self.gaussian(feature, mean, stdev)
                    prob *= normal
                prior = features['prior']
                joint_probs[class_name] = prior * prob
            MAP = max(joint_probs, key=joint_probs.get)
            print(MAP)
            MAPs.append("person" if MAP >= 0.50 else "object")
            
        return MAPs

    def accuracy(self, y_test, y_real):
        corr = 0

        for y_t, y_p in zip(y_test, y_real):
            if y_t == y_p:
                corr += 1
        return corr / len(y_test)

    def train(self):
        image_dir = '../images'
        image_labels = []
        image_data = []

        batch_size = 100  # Process images in batches of 100
        num_negative = 0

        for filename in os.listdir(image_dir):
            if filename.endswith('.jpg') or filename.endswith('.png'):
                image_path = os.path.join(image_dir, filename)
                image = Image.open(image_path).resize((64, 64))  # Resize images to reduce memory usage
                image_data.append(np.array(image).flatten())
                image_labels.append('person')

                if len(image_data) == batch_size:
                    negative_data = np.random.randint(0, 256, size=(batch_size, image_data[0].size))
                    image_data.extend(negative_data.tolist())
                    image_labels.extend(['no_person'] * batch_size)
                    num_negative += batch_size

                    X_train, X_test, y_train, y_test = train_test_split(image_data, image_labels, test_size=0.2, random_state=42)
                    le = LabelEncoder()
                    y_train = le.fit_transform(y_train)
                    y_test = le.transform(y_test)

                    
                    self.fit(X_train, y_train)

                    y_pred = self.predict(X_test)
                    accuracy = accuracy_score(y_test, y_pred)

                    print(f"Batch complete. Accuracy: {accuracy:.2f}")

                    image_data = []
                    image_labels = []

            if image_data:
                X_train, X_test, y_train, y_test = train_test_split(image_data, image_labels, test_size=0.2, random_state=42)
                le = LabelEncoder()
                y_train = le.fit_transform(y_train)
                y_test = le.transform(y_test)


                self.fit(X_train, y_train)
                X_train, y_train = shuffle(X_train, y_train)
                X_test, y_test = shuffle(X_test, y_test)
                y_pred = self.predict(X_test)
                accuracy = self.accuracy(y_test, y_pred)

                print(f"Final batch complete. Accuracy: {accuracy:.2f}")

