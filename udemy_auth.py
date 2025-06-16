import requests
from config import UDEMY_API_CONFIG
import base64

class UdemyAuth:
    def __init__(self):
        self.client_id = UDEMY_API_CONFIG['client_id']
        self.client_secret = UDEMY_API_CONFIG['client_secret']
        self.auth_url = UDEMY_API_CONFIG['auth_url']
        self.access_token = None
    
    def get_access_token(self):
        """Lấy access token từ Udemy API"""
        if self.access_token:
            return self.access_token
            
        # Tạo Basic Auth header
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        
        headers = {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'client_credentials'
        }
        
        try:
            response = requests.post(
                self.auth_url,
                headers=headers,
                data=data
            )
            
            if response.status_code == 200:
                self.access_token = response.json()['access_token']
                return self.access_token
            else:
                print(f"Error getting access token: {response.status_code}")
                print(response.text)
                return None
                
        except Exception as e:
            print(f"Exception while getting access token: {str(e)}")
            return None
    
    def get_auth_header(self):
        """Lấy header xác thực cho API requests"""
        token = self.get_access_token()
        if token:
            return {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
        return None

# Ví dụ sử dụng
if __name__ == "__main__":
    auth = UdemyAuth()
    token = auth.get_access_token()
    
    if token:
        print("Successfully obtained access token!")
        print(f"Token: {token[:10]}...")  # Chỉ in 10 ký tự đầu của token
    else:
        print("Failed to obtain access token. Please check your credentials.") 