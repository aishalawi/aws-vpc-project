from flask import Flask, jsonify, render_template_string
import requests

app = Flask(__name__)

BACKEND_URL = "http://10.0.4.233:5000"

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>AWS Frontend</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            margin-top: 50px;
            background-color: #f0f0f0;
        }
        button {
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
        }
        button:hover {
            background-color: #45a049;
        }
        #output {
            margin-top: 20px;
            font-size: 18px;
            color: #333;
        }
    </style>
</head>
<body>
    <h2>AWS Frontend Application</h2>
    <button onclick="fetchData()">Get Message from Backend</button>
    <p id="output"></p>
    <script>
        function fetchData() {
            fetch('/api/message')
                .then(r => r.json())
                .then(data => {
                    document.getElementById('output').innerText = data.message;
                })
                .catch(error => {
                    document.getElementById('output').innerText = 'Error: ' + error;
                });
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/message')
def proxy():
    try:
        response = requests.get(f"{BACKEND_URL}/api/message")
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)