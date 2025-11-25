import torch
import torch.nn as nn

class CNN(nn.Module):
    def __init__(self, num_classes):
        super(CNN, self).__init__()

        # extracts the features to learn patterns 
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
            
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2)
        )

        # infer flattened dimension used to tell PyTorch the number of features being used 
        # need to make sure the shape always matches
        # make sure number of features coming out of the convolutional layers ALWAYS matches the input 
        # size expected by the fully connected layers to avoid shape mismatch errors
        with torch.no_grad():
            dummy_input = torch.zeros(1, 3, 128, 128)
            dummy_output = self.features(dummy_input)
            self.flatten_dim = dummy_output.view(1, -1).size(1)
            print(f"Inferred flatten_dim: {self.flatten_dim}") 
        
        # creates the fully connected layers 
        # decides the final class based on features
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(self.flatten_dim, 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes) # this layer maps the features to classes 
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x
