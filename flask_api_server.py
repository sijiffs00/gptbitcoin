from flask import Flask, jsonify, request
from flask_cors import CORS
import os
import base64
import boto3
from botocore.exceptions import ClientError
import sqlite3
from datetime import datetime
from trade.firebase.fcm_token_manager import FCMTokenManager

app = Flask(__name__)
CORS(app)  # Flutter 앱에서의 접근 허용

# S3 클라이언트 설정
s3_client = boto3.client('s3')
BUCKET_NAME = 'aibitcoin-chart-img'
CHARTS_PREFIX = 'bitcoin_charts/'

# FCM 토큰 매니저 인스턴스 생성
fcm_manager = FCMTokenManager()

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

@app.route('/api/trades/recent')
def get_recent_two_days_trades():
    try:
        conn = sqlite3.connect('trading_history.db')
        cursor = conn.cursor()
        
        # 오늘과 어제의 날짜를 가져오기 위한 쿼리
        cursor.execute('''
        SELECT id, timestamp, price, decision, percentage, reason, img 
        FROM trades 
        WHERE date(timestamp) >= date('now', '-1 day')
        ORDER BY timestamp DESC
        ''')
        
        trades = cursor.fetchall()
        
        # 결과를 JSON 형태로 변환
        trade_list = []
        for trade in trades:
            trade_list.append({
                'id': trade[0],
                'timestamp': trade[1],
                'img': trade[6],
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

@app.route('/api/trades/by-date')
def get_trades_by_date():
    try:
        # URL 파라미터에서 날짜 가져오기
        date = request.args.get('date')
        
        if not date:
            return jsonify({
                'success': False,
                'error': '날짜 파라미터가 필요합니다. (예: /api/trades/by-date?date=2024-03-18)'
            }), 400
            
        # 날짜 형식 검증
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return jsonify({
                'success': False,
                'error': '올바른 날짜 형식이 아닙니다. YYYY-MM-DD 형식을 사용하세요.'
            }), 400
        
        conn = sqlite3.connect('trading_history.db')
        cursor = conn.cursor()
        
        # 특정 날짜의 거래 기록 조회
        cursor.execute('''
        SELECT id, timestamp, price, decision, percentage, reason, img 
        FROM trades 
        WHERE date(timestamp) = date(?)
        ORDER BY timestamp DESC
        ''', (date,))
        
        trades = cursor.fetchall()
        
        # 결과를 JSON 형태로 변환
        trade_list = []
        for trade in trades:
            trade_list.append({
                'id': trade[0],
                'timestamp': trade[1],
                'img': trade[6],
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

@app.route('/api/fcm-token', methods=['POST'])
def update_fcm_token():
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({
                'success': False,
                'message': 'FCM 토큰이 제공되지 않았습니다.'
            }), 400
            
        # 토큰 저장
        if fcm_manager.save_token(token):
            return jsonify({
                'success': True,
                'message': 'FCM 토큰이 성공적으로 저장되었습니다.'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'FCM 토큰 저장에 실패했습니다.'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'오류가 발생했습니다: {str(e)}'
        }), 500

def run_server():
    app.run(host='0.0.0.0', port=8000)

if __name__ == '__main__':
    run_server()
