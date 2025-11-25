import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from PIL import Image
from torchvision import transforms
import torch
from cnn import CNN
from pillow_heif import register_heif_opener
register_heif_opener()

# load model
device = "cuda" if torch.cuda.is_available() else "cpu"
class_names = ["compost", "paper", "recycle", "trash"]

model = CNN(num_classes=len(class_names)).to(device)
model.load_state_dict(torch.load("model.pth", map_location=device))
model.eval()

def getPrediction_from_image(img):
    transform = transforms.Compose([
        transforms.Resize((128, 128)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.5, 0.5, 0.5],
                             std=[0.5, 0.5, 0.5])
    ])
    img_tensor = transform(img).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(img_tensor)
        _, predicted = torch.max(outputs, 1)

    return class_names[predicted.item()]

app = Flask(__name__)
CORS(app)

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "heic", "heif"}
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024

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

    file = request.files["image"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    
    if not allowed_file(file.filename):
        return jsonify({"error": "Invalid file type"}), 400

    try:
        img = Image.open(file.stream)
        prediction = getPrediction_from_image(img)

        return jsonify({
            "category": prediction,
            "filename": file.filename
        }), 200

    except Exception:
        return jsonify({"error": "Failed to process image"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)