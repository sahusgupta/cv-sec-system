import numpy as np

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
            MAPs.append(MAP)
        return MAPs

    def accuracy(self, y_test, y_real):
        corr = 0

        for y_t, y_p in zip(y_test, y_real):
            if y_t == y_p:
                corr += 1
        return corr / len(y_test)

import os
from sklearn.naive_bayes import GaussianNB
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from PIL import Image
import numpy as np

# 1. Prepare the data
image_dir = '../images'
image_labels = []
image_data = []

for filename in os.listdir(image_dir):
    if filename.endswith('.jpg') or filename.endswith('.png'):
        image_path = os.path.join(image_dir, filename)
        image = Image.open(image_path)
        image_data.append(np.array(image).flatten())
        image_labels.append('person')

# Create negative samples (non-person images)
num_negative = len(image_data)
negative_data = np.random.randint(0, 256, size=(num_negative, image_data[0].size))
image_data.extend(negative_data.tolist())
image_labels.extend(['no_person'] * num_negative)

# 2. Encode the labels
le = LabelEncoder()
y = le.fit_transform(image_labels)

# 3. Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(image_data, y, test_size=0.2, random_state=42)

# 4. Train the Naive Bayes classifier
clf = NaiveBayes()
clf.fit(X_train, y_train)

# 5. Evaluate the classifier
y_pred = clf.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(accuracy)