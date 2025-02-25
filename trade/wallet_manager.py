import json
import os
from datetime import datetime

class WalletManager:
    def __init__(self):
        # 프로젝트 루트 경로 찾기
        self.root_dir = os.path.dirname(os.path.dirname(__file__))
        self.wallet_file = os.path.join(self.root_dir, 'my_wallet.json')
        
        # 파일이 없으면 기본값으로 생성
        if not os.path.exists(self.wallet_file):
            self.initialize_wallet()
    
    def initialize_wallet(self):
        """지갑 파일을 기본값으로 초기화하는 함수"""
        data = {
            "seed": 0,
            "btc_balance": 0,
            "krw_balance": 0,
            "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.save_wallet(data)
    
    def save_wallet(self, data: dict) -> bool:
        """지갑 정보를 저장하는 함수"""
        try:
            data["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(self.wallet_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ 지갑 정보 저장 중 오류 발생: {str(e)}")
            return False
    
    def get_wallet(self) -> dict:
        """저장된 지갑 정보를 가져오는 함수"""
        try:
            if not os.path.exists(self.wallet_file):
                self.initialize_wallet()
                
            with open(self.wallet_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"❌ 지갑 정보 읽기 중 오류 발생: {str(e)}")
            return None
    
    def update_balance(self, seed=None, btc=None, krw=None) -> bool:
        """지갑 잔액을 업데이트하는 함수"""
        try:
            current_wallet = self.get_wallet()
            if current_wallet is None:
                return False
            
            if seed is not None:
                current_wallet["seed"] = seed
            if btc is not None:
                current_wallet["btc_balance"] = btc
            if krw is not None:
                current_wallet["krw_balance"] = krw
                
            return self.save_wallet(current_wallet)
        except Exception as e:
            print(f"❌ 잔액 업데이트 중 오류 발생: {str(e)}")
            return False 