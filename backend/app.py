from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import sys
from werkzeug.utils import secure_filename
from PIL import Image
from torchvision import transforms
import torch
from cnn import CNN
from pillow_heif import register_heif_opener
register_heif_opener()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# load trained model
device = 'cuda' if torch.cuda.is_available() else 'cpu'
class_names = ["compost", "paper", "recycle", "trash"]

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model.pth")

model = CNN(num_classes=len(class_names)).to(device)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.eval()

def getPrediction(filePath):

    input_image = Image.open(filePath)
    
    transform = transforms.Compose([
        transforms.Resize((128, 128)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5], 
                            std=[0.5, 0.5, 0.5])
    ])

    # transform PIL to tensor 
    img_tensor = transform(input_image).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(img_tensor)
        _, predicted = torch.max(outputs, 1)
    
    return class_names[predicted.item()]

# Flask setup
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'heic', 'heif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

os.makedirs(UPLOAD_FOLDER, exist_ok = True)

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/", methods=["GET"])
def getMessage():
    return jsonify({"message": "Hello from Flask"})

@app.route("/api/classify", methods=["POST"])
def classify_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400
    
    file = request.files['image']

    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"})
    
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        prediction = getPrediction(filepath)

        result = {
            "category": prediction,
            "filename": filename 
        }

        return jsonify(result), 200
    
    return jsonify({"error": "Failed to process image"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)