import numpy as np
class MatMulFreeLLM:
    def __init__(self, X):
        self.X = X
        self.W = np.array(np.random() * len(self.X))

    def forward(self, weights, biases, epsilon):
        Y, mean, var, R = self.rms_norm(self.X, epsilon)
        W = self.weight_quantization(weights)
        out = np.dot(Y, (W + biases))
        return out, mean, var, R

    def rms_norm(self, e, X=None):
        mean = np.mean(self.X if X is not None else X)
        sd = np.var(self.X if X is not None else X)
        R = 1.0 / np.sqrt(sd + e)
        Y = self.activation_quantization(R * ((self.X if X is None else X) - mean))
        return Y, mean, sd, R
    
    def activation_quantization(self, X=None):
        s = 127 / np.max(np.abs(self.X if X is not None else X))
        self.X = np.clip(np.round(s * (self.X if X is None else X)), -1, 1) * (1.0 / s)
        return self.X
    
    def weight_quantization(self, X = None):
        s = 1 / np.mean(np.abs(self.W))
        newW = np.clip(np.round(s * (self.X if X is not None else X)), -1, 1) * (1.0 / s)
        return newW
        
    def back(self, biases, out, dO, mean, var, r):
        dY = np.cross(dO, np.transpose(self.W))
        dX, Ybar = self.rms_back(dY, mean, var, r)
        dW = np.cross(np.transpose(dO), Ybar)
        db = sum(dO)
        return dX, dW, db
    def rms_back(self, dY, mean, var, r):
        Ybar = self.activation_quantization()
        dvar = np.sum(np.cross(np.cross(dY, (self.X - mean), np.cross(-0.5, r ** 3))))
        dmu = np.sum(-r * dY) + (np.mean(self.X-mean) * dvar)
        dX = (r * dY) + ((2 * dvar * (self.X - mean)) / len(self.X)) + (dmu / len(self.X))
        return dX, Ybar
        
        
        


