import os
import hashlib
from flask import Flask, request, redirect, url_for, render_template_string

# Flask app setup
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Limit file size to 16MB

# Known ransomware file hashes (Example)

KNOWN_RANSOMWARE_HASHES = {
    "db349b97c37d22f5ea1d1841e3c89eb4",  # WannaCry MD5
    "4b13069d80a4f2e378b8d2e9cf2d26e9",  # Locky MD5
    "1e3b390339526c6b0e667f13a3bfb5ef",  # CryptoWall MD5
    "3f86d7896d8f8572a4a71d2a8c2f7069",  # Cerber MD5
    "aecf21c485fc916c57bb1e5f1f7c2c94",  # TeslaCrypt MD5
    "651b93ca4fc60c837c50f0a943c4e697",  # Petya MD5
    "c83710b8b83e97032c13e5fe75b46a7e",  # Jigsaw MD5
    "95f71dfdbb06e8bbca73eec86f22479c",  # Sodinokibi MD5
    "db349b97c37d22f5ea1d1841e3c89eb4",
    "84c82835a5d21bbcf75a61706d8ab5493176a32b",
    "aae42fa120f4fd7b981ab56b4c8f2dd48fbf673f3a9e5ebdb78b9342e0b29297",
    "4b13069d80a4f2e378b8d2e9cf2d26e9",
    "97e25c9db16e398be7b45f15785eb153ee25d94a",
    "d2b2bc3b138fa45729d2c1fa0e2d3d8f47b8b5976f885c80e0f04e84a31c814e",
    "1e3b390339526c6b0e667f13a3bfb5ef",
    "7f22b7593e9ff082f70bd8d208c621d9ffdb5ab8",
    "bb01fa47dbbf1b61fb80db81343fbeb03b8a6559f50a019bfa2d07b703f9a0e8",
    "3f86d7896d8f8572a4a71d2a8c2f7069",
    "55cf4c015bcffbf6eeb14fdbf33485f823b0e36b",
    "ca9c8c3c26fcff5f6edb243ef0ac4f4c33fd56b9ff3c3ab2f7ae1234ddf06437",
    "aecf21c485fc916c57bb1e5f1f7c2c94",
    "f732edb205b94df03212efb6df755206e487a3b4",
    "02c7ed58c75f73dbdb8126a3d13d84eb471e63d1ff07cf63f500e90e293b6d71",
    "651b93ca4fc60c837c50f0a943c4e697",
    "01c149c2ab231d21f7d47006c8b00821754f06f0",
    "c378b36d0f5a5c22e05b8e67c2de9e4b1792f5bbd9956f3e4fa2bdb06cd052f7",
    "c83710b8b83e97032c13e5fe75b46a7e",
    "f6b82cc06f3e8a891eb62f5d2386900e26f0d7b7",
    "ed8b5767606483484e61c2878a04e5f5a6b3a0e75fc313b1a3d94c8de66e72a3",
    "95f71dfdbb06e8bbca73eec86f22479c",
    "ef0e5ba4c5dcd2cb0fdfeffed502df2b7f18f417",
    "9f4fa8d61c9e3b920615eec8755fdfc3dd815b7e60352b5e509c96a2902b0c3c",
    "ed01ebfbc9eb5bbea545af4d01bf5f1071661840480439c6e5babe8e080e41aa",
    "84c82835a5d21bbcf75a61706d8ab549",
    "5ff465afaabcbf0150d1a3ab2c2e74f3a4426467",
    "ed01ebfbc9eb5bbea545af4d01bf5f1071661840480439c6e5babe8e080e41aa"



}
# Ensure the uploads directory exists
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def calculate_file_hash(file_path, algorithm="md5"):
    """Calculate the hash of a file."""
    hash_func = hashlib.new(algorithm)
    try:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hash_func.update(chunk)
        return hash_func.hexdigest()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def is_ransomware(file_path):
    """Check if the file matches known ransomware signatures."""
    file_hash = calculate_file_hash(file_path)
    if file_hash in KNOWN_RANSOMWARE_HASHES:
        return True
    return False


# Enhanced HTML template with styling
html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ransomware Detector</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f4f4f9;
            color: #333;
            font-family: Arial, sans-serif;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
        }
        .container {
            background-color: #ffffff;
            border-radius: 8px;
            padding: 30px;
            box-shadow: 0px 0px 20px rgba(0, 0, 0, 0.1);
            text-align: center;
            max-width: 500px;
            width: 100%;
        }
        .btn-primary {
            background-color: #EF233C;
            border: none;
        }
        .btn-primary:hover {
            background-color: #D90429;
        }
        .result {
            font-size: 1.2em;
            margin-top: 20px;
        }
        h1 {
            color: #2B2D42;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Ransomware Detector</h1>
        <form action="/upload" method="POST" enctype="multipart/form-data" class="mt-4">
            <div class="mb-3">
                <label for="file" class="form-label">Choose a file to upload:</label>
                <input type="file" name="file" id="file" class="form-control" required>
            </div>
            <button type="submit" class="btn btn-primary btn-lg w-100">Upload File</button>
        </form>
        {% if result %}
            <div class="result alert {% if 'WARNING' in result %}alert-danger{% else %}alert-success{% endif %}" role="alert">
                {{ result }}
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(html_template)  # Serve the HTML form as a string

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    if file:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(file_path)

        # Run ransomware detection on the uploaded file
        if is_ransomware(file_path):
            result = "<h1> <center> <br> WARNING: The uploaded file is identified as ransomware! </center> </h1>"
        else:
            result = "<h1> <center> <br> The uploaded file is clean.</center> </h1>"
       
        # Remove the file after checking (optional)
        os.remove(file_path)

        return result

if __name__ == '__main__':
    app.run(debug=True)
