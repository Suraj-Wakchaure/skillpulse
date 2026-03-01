from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Test route
@app.route('/')
def home():
    return jsonify({'message': 'SkillPulse Python Service is running!'})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5001))
    app.run(debug=True, port=port)