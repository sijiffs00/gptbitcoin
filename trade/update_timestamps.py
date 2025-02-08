import sqlite3
from datetime import datetime
import pytz

def update_to_kst():
    """
    기존 거래 기록의 시간을 UTC에서 KST(한국 시간)로 변환하는 함수야
    """
    try:
        # 데이터베이스 연결
        conn = sqlite3.connect('trading_history.db')
        cursor = conn.cursor()

        # 모든 거래 기록 가져오기
        cursor.execute('SELECT id, timestamp FROM trades')
        records = cursor.fetchall()

        # UTC -> KST 변환 (9시간 추가)
        utc = pytz.UTC
        kst = pytz.timezone('Asia/Seoul')

        for record_id, timestamp_str in records:
            try:
                # 문자열을 datetime 객체로 변환
                utc_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                # UTC 시간 정보 추가
                utc_time = utc.localize(utc_time)
                # KST로 변환
                kst_time = utc_time.astimezone(kst)
                # 다시 문자열로 변환
                kst_str = kst_time.strftime('%Y-%m-%d %H:%M:%S')

                # 데이터베이스 업데이트
                cursor.execute('''
                UPDATE trades 
                SET timestamp = ? 
                WHERE id = ?
                ''', (kst_str, record_id))
                
                print(f"✅ ID {record_id}: {timestamp_str} → {kst_str}")

            except Exception as e:
                print(f"❌ ID {record_id} 처리 중 오류 발생: {e}")
                continue

        # 변경사항 저장
        conn.commit()
        print("\n🎉 모든 시간이 한국 시간으로 변환되었어!")

    except sqlite3.Error as e:
        print(f"❌ 데이터베이스 오류 발생: {e}")

    finally:
        if conn:
            conn.close()
            print("🔒 데이터베이스 연결을 안전하게 닫았어!")

if __name__ == '__main__':
    print("🕒 거래 기록의 시간을 한국 시간으로 변환하기 시작할게...")
    update_to_kst() 