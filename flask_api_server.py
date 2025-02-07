from flask import Flask, jsonify
from flask_cors import CORS
import os
import base64

app = Flask(__name__)
CORS(app)  # Flutter 앱에서의 접근 허용

@app.route('/api/charts/<path:filename>')
def get_chart(filename):
    try:
        file_path = os.path.join('chart', filename)
        if os.path.exists(file_path):
            with open(file_path, 'rb') as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                return jsonify({
                    'success': True,
                    'image_data': encoded_image
                })
        else:
            return jsonify({
                'success': False,
                'error': 'Image not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/charts')
def list_charts():
    try:
        chart_files = [f for f in os.listdir('chart') if f.endswith('.png')]
        charts_data = []
        
        for filename in chart_files:
            file_path = os.path.join('chart', filename)
            with open(file_path, 'rb') as image_file:
                encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                charts_data.append({
                    'filename': filename,
                    'image_data': encoded_image
                })
                
        return jsonify({
            'success': True,
            'charts': charts_data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def run_server():
    app.run(host='0.0.0.0', port=8000)
