from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
import os
import base64
import boto3
from botocore.exceptions import ClientError
import sqlite3
from datetime import datetime
from trade.firebase.fcm_token_manager import FCMTokenManager
import json

app = Flask(__name__)
CORS(app)  # Flutter 앱에서의 접근 허용

# S3 클라이언트 설정
s3_client = boto3.client('s3')
BUCKET_NAME = 'aibitcoin-chart-img'
CHARTS_PREFIX = 'bitcoin_charts/'

# FCM 토큰 매니저 인스턴스 생성
fcm_manager = FCMTokenManager()

# 지갑 파일 경로 설정
WALLET_FILE_PATH = os.path.join(os.getcwd(), 'upbit_wallet.json')

def initialize_wallet_file():
    """지갑 파일이 없으면 생성하는 함수"""
    try:
        print(f"💡 지갑 파일 초기화 시도... 경로: {WALLET_FILE_PATH}")
        
        if not os.path.exists(WALLET_FILE_PATH):
            print("📝 지갑 파일이 없어서 새로 생성합니다...")
            default_data = {
                "seed": 0,
                "btc_balance": 0,
                "krw_balance": 0,
                "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            with open(WALLET_FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, indent=4, ensure_ascii=False)
            print(f"✅ 지갑 파일이 생성되었습니다: {WALLET_FILE_PATH}")
        else:
            print(f"✅ 지갑 파일이 이미 존재합니다: {WALLET_FILE_PATH}")
            
    except Exception as e:
        print(f"❌ 지갑 파일 생성/확인 중 오류 발생: {str(e)}")
        print(f"💻 현재 작업 디렉토리: {os.getcwd()}")
        print(f"🔐 파일 권한: {os.access(os.path.dirname(WALLET_FILE_PATH), os.W_OK)}")

# 서버 시작 시 지갑 파일 초기화
initialize_wallet_file()

# 루트 URL 핸들러 추가
@app.route('/')
def home():
    html_path = os.path.join(os.getcwd(), 'index.html')
    if os.path.exists(html_path):
        return send_file(html_path)
    else:
        return "API 서버가 실행 중입니다. index.html 파일이 없습니다."

@app.route('/1')
def page_1():
    html_path = os.path.join(os.getcwd(), '1.html')
    if os.path.exists(html_path):
        return send_file(html_path)
    else:
        return "1.html 파일이 없습니다."

@app.route('/2')
def page_2():
    html_path = os.path.join(os.getcwd(), '2.html')
    if os.path.exists(html_path):
        return send_file(html_path)
    else:
        return "2.html 파일이 없습니다."

@app.route('/3')
def page_3():
    html_path = os.path.join(os.getcwd(), '3.html')
    if os.path.exists(html_path):
        return send_file(html_path)
    else:
        return "3.html 파일이 없습니다."

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
        SELECT id, timestamp, img, price, decision, reason, original_reason, lookback 
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
                'img': trade[2],
                'price': trade[3],
                'decision': trade[4],
                'reason': trade[5],
                'original_reason': trade[6],
                'lookback': trade[7]
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
        SELECT id, timestamp, img, price, decision, reason, original_reason, lookback 
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
                'img': trade[2],
                'price': trade[3],
                'decision': trade[4],
                'reason': trade[5],
                'original_reason': trade[6],
                'lookback': trade[7]
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
        SELECT id, timestamp, img, price, decision, reason, original_reason, lookback 
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
                'img': trade[2],
                'price': trade[3],
                'decision': trade[4],
                'reason': trade[5],
                'original_reason': trade[6],
                'lookback': trade[7]
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

@app.route('/api/upbit_wallet')
def get_upbit_wallet_info():
    try:
        print("\n🔄 지갑 정보 요청 받음...")
        
        print(f"📂 파일 읽기 시도: {WALLET_FILE_PATH}")
        # upbit_wallet.json 파일 읽기
        with open(WALLET_FILE_PATH, 'r', encoding='utf-8') as file:
            file_content = file.read()
            print(f"📄 파일 내용: {file_content}")
            
            wallet_data = json.loads(file_content)
            print(f"💾 파싱된 데이터: {wallet_data}")
            
            # 필요한 키가 모두 있는지 확인
            required_keys = ['seed', 'btc_balance', 'krw_balance', 'last_updated']
            print(f"🔍 필수 키 확인 중... 현재 키들: {list(wallet_data.keys())}")
            
            missing_keys = [key for key in required_keys if key not in wallet_data]
            if missing_keys:
                print(f"⚠️ 누락된 키 발견: {missing_keys}")
                raise KeyError(f"필수 키 {', '.join(missing_keys)}가 없습니다")
            
            # 현재 총 자산 계산 (원화 + 비트코인)
            current_total = float(wallet_data['krw_balance'])
            if float(wallet_data['btc_balance']) > 0:
                # 비트코인 현재가 조회 (실제로는 업비트 API로 가져와야 함)
                import pyupbit
                current_price = pyupbit.get_current_price("KRW-BTC")
                if current_price:
                    current_total += float(wallet_data['btc_balance']) * current_price
            
            # 수익률 계산
            initial_seed = float(wallet_data['seed'])
            return_rate = ((current_total - initial_seed) / initial_seed * 100) if initial_seed > 0 else 0
            
            response_data = {
                'success': True,
                'wallet': {
                    'return_rate': float(return_rate),
                    'seed': float(wallet_data['seed']),
                    'btc_balance': float(wallet_data['btc_balance']),
                    'krw_balance': float(wallet_data['krw_balance']),
                    'last_updated': wallet_data['last_updated']
                }
            }
            print(f"✅ 응답 데이터 준비 완료: {response_data}")
            return jsonify(response_data)
        
    except FileNotFoundError as e:
        print(f"❌ 파일을 찾을 수 없습니다: {str(e)}")
        return jsonify({
            'success': False,
            'error': '지갑 정보를 찾을 수 없습니다.'
        }), 404
        
    except json.JSONDecodeError as e:
        print(f"❌ JSON 디코딩 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': '지갑 데이터 형식이 올바르지 않습니다.'
        }), 500
        
    except KeyError as e:
        print(f"❌ 키 에러: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'필수 데이터가 누락되었습니다: {str(e)}'
        }), 500
        
    except ValueError as e:
        print(f"❌ 값 변환 오류: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'데이터 형식이 올바르지 않습니다: {str(e)}'
        }), 500
        
    except Exception as e:
        print(f"❌ 예상치 못한 오류 발생: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def run_server():
    app.run(host='0.0.0.0', port=8000)

if __name__ == '__main__':
    run_server()
