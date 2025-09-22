import requests
import json
import time
from datetime import datetime
from Config import *
from dotenv import load_dotenv, find_dotenv

class VKMessagesDownloader:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://api.vk.com/method/"
        self.version = "5.199"
        
    def get_messages(self, peer_id, count=200, offset=0):
        """Получение сообщений из диалога"""
        method = "messages.getHistory"
        params = {
            'access_token': self.access_token,
            'v': self.version,
            'peer_id': peer_id,
            'count': count,
            'offset': offset,
            'extended': 1
        }
        
        try:
            response = requests.get(f"{self.base_url}{method}", params=params)
            data = response.json()
            
            if 'error' in data:
                print(f"Ошибка: {data['error']['error_msg']}")
                return None
                
            return data['response']
            
        except Exception as e:
            print(f"Ошибка при запросе: {e}")
            return None
    
    def download_all_messages(self, peer_id, output_file="messages.json"):
        """Скачивание всех сообщений"""
        all_messages = []
        all_profiles = {}
        all_chats = {}
        
        offset = 0
        batch_size = 200
        
        print("Начинаем скачивание сообщений...")
        
        while True:
            print(f"Загружаем сообщения с offset {offset}...")
            
            data = self.get_messages(peer_id, batch_size, offset)
            
            if not data or 'items' not in data:
                break
                
            messages = data['items']
            if not messages:
                break
                
            all_messages.extend(messages)
            
            # Сохраняем информацию о пользователях и чатах
            if 'profiles' in data:
                for profile in data['profiles']:
                    all_profiles[profile['id']] = profile
            if 'groups' in data:
                for group in data['groups']:
                    all_profiles[-group['id']] = group
            if 'conversations' in data:
                for chat in data['conversations']:
                    all_chats[chat['peer']['id']] = chat
            
            if len(messages) < batch_size:
                break
                
            offset += batch_size
            time.sleep(0.34)  # Задержка для соблюдения лимитов API
        
        # Сохраняем в файл
        result = {
            'messages': all_messages,
            'profiles': list(all_profiles.values()),
            'chats': list(all_chats.values()),
            'export_date': datetime.now().isoformat(),
            'total_messages': len(all_messages)
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"Скачано {len(all_messages)} сообщений. Сохранено в {output_file}")
        return result

# Использование
if __name__ == "__main__":
    # Ваш access token из VK
    ACCESS_TOKEN = os.getenv('API_KEY')
    
    # ID диалога (пользователя или беседы)
    # Для пользователя: его ID
    # Для беседы: 2000000000 + ID беседы
    PEER_ID = 2504000332
    
    downloader = VKMessagesDownloader(ACCESS_TOKEN)
    downloader.download_all_messages(PEER_ID, "my_messages.json")