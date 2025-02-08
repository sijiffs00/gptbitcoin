from flask import Flask, jsonify
from flask_cors import CORS
import os
import base64
import boto3
from botocore.exceptions import ClientError
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)  # Flutter 앱에서의 접근 허용

# S3 클라이언트 설정
s3_client = boto3.client('s3')
BUCKET_NAME = 'aibitcoin-chart-img'
CHARTS_PREFIX = 'bitcoin_charts/'

@app.route('/api/charts/<path:key>')
def get_chart(key):
    try:
        # S3에서 이미지 가져오기
        response = s3_client.get_object(
            Bucket=BUCKET_NAME,
            Key=f"{CHARTS_PREFIX}{key}"
        )
        image_data = response['Body'].read()
        encoded_image = base64.b64encode(image_data).decode('utf-8')
        
        return jsonify({
            'success': True,
            'image_data': encoded_image
        })
    except ClientError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/charts')
def list_charts():
    try:
        # S3 버킷의 이미지 목록 가져오기
        response = s3_client.list_objects_v2(
            Bucket=BUCKET_NAME,
            Prefix=CHARTS_PREFIX
        )
        
        charts_data = []
        for obj in response.get('Contents', []):
            if obj['Key'].endswith('.png'):
                # 각 이미지 데이터 가져오기
                image_response = s3_client.get_object(
                    Bucket=BUCKET_NAME,
                    Key=obj['Key']
                )
                image_data = image_response['Body'].read()
                encoded_image = base64.b64encode(image_data).decode('utf-8')
                
                # 파일 이름만 추출 (경로 제외)
                filename = obj['Key'].split('/')[-1]
                
                charts_data.append({
                    'filename': filename,
                    'image_data': encoded_image,
                    'last_modified': obj['LastModified'].isoformat()
                })
        
        return jsonify({
            'success': True,
            'charts': sorted(charts_data, key=lambda x: x['last_modified'], reverse=True)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# 새로운 API 엔드포인트: 전체 매매 기록 조회
@app.route('/api/trades')
def get_trades():
    try:
        conn = sqlite3.connect('trading_history.db')
        cursor = conn.cursor()
        
        # 최근 거래 순으로 정렬해서 모든 거래 기록 가져오기
        cursor.execute('''
        SELECT id, timestamp, price, decision, percentage, reason, img 
        FROM trades 
        ORDER BY timestamp DESC
        ''')
        
        trades = cursor.fetchall()
        
        # 결과를 JSON 형태로 변환
        trade_list = []
        for trade in trades:
            trade_list.append({
                'id': trade[0],
                'timestamp': trade[1],
                'img': trade[6],  # 새로 추가된 이미지 URL
                'price': trade[2],
                'decision': trade[3],
                'percentage': trade[4],
                'reason': trade[5]
            })
        
        return jsonify({
            'success': True,
            'trades': trade_list
        })
        
    except sqlite3.Error as e:
        return jsonify({
            'success': False,
            'error': f'데이터베이스 오류: {str(e)}'
        }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
    finally:
        if conn:
            conn.close()

# 새로운 API 엔드포인트: 최근 N개의 매매 기록 조회
@app.route('/api/trades/recent/<int:count>')
def get_recent_trades(count):
    try:
        conn = sqlite3.connect('trading_history.db')
        cursor = conn.cursor()
        
        # 최근 N개의 거래 기록만 가져오기
        cursor.execute('''
        SELECT id, timestamp, price, decision, percentage, reason 
        FROM trades 
        ORDER BY timestamp DESC
        LIMIT ?
        ''', (count,))
        
        trades = cursor.fetchall()
        
        # 결과를 JSON 형태로 변환
        trade_list = []
        for trade in trades:
            trade_list.append({
                'id': trade[0],
                'timestamp': trade[1],
                'price': trade[2],
                'decision': trade[3],
                'percentage': trade[4],
                'reason': trade[5]
            })
        
        return jsonify({
            'success': True,
            'trades': trade_list
        })
        
    except sqlite3.Error as e:
        return jsonify({
            'success': False,
            'error': f'데이터베이스 오류: {str(e)}'
        }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
        
    finally:
        if conn:
            conn.close()

def run_server():
    app.run(host='0.0.0.0', port=8000, debug=False, use_reloader=False)

if __name__ == '__main__':
    run_server()
