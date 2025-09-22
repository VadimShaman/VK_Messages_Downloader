import requests
import json
import time
import os
from datetime import datetime
from dotenv import load_dotenv, find_dotenv

class VKMessagesDownloader:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = "https://api.vk.com/method/"
        self.version = "5.199"
        
    def is_text_message(self, message):
        """
        Проверяет, является ли сообщение текстовым
        """
        # Пропускаем удаленные сообщения
        if message.get('deleted'):
            return False
    
        # Пропускаем сообщения с действиями (смена названия беседы и т.д.)
        if message.get('action'):
            return False
    
        # Пропускаем сообщения только с вложениями (без текста)
        if (not message.get('text') or message.get('text').strip() == ''):
            return False
    
        # Пропускаем служебные сообщения
        if message.get('out') not in [0, 1]:  # 0 - полученное, 1 - отправленное
            return False
    
        return True
        
    def get_messages_batch(self, peer_id, offset=0, count=200):
        """
        Получает batch сообщений из диалога
        """
        url = f"{self.base_url}messages.getHistory"
        params = {
            'peer_id': peer_id,
            'offset': offset,
            'count': count,
            'access_token': self.access_token,
            'v': self.version,
            'extended': 1  # Важно: получаем информацию о пользователях
        }
    
        response = requests.get(url, params=params)
        data = response.json()
    
        if 'error' in data:
            error_msg = data['error']['error_msg']
            error_code = data['error']['error_code']
            raise Exception(f"VK API Error {error_code}: {error_msg}")
    
        if 'response' not in data:
            raise Exception("Некорректный ответ от API VK")
    
        return data['response']

    def get_user_info(self, user_id, profiles, groups):
        """
        Получает информацию о пользователе/группе по ID
        """
        # Для групп ID отрицательные
        if user_id < 0:
            group_id = abs(user_id)
            for group in groups:
                if group['id'] == group_id:
                    return f"[Группа: {group.get('name', 'Unknown')}]"
            return f"[Группа: {group_id}]"
        
        # Для пользователей
        for profile in profiles:
            if profile['id'] == user_id:
                first_name = profile.get('first_name', '')
                last_name = profile.get('last_name', '')
                return f"{first_name} {last_name}"
        
        return f"[Пользователь: {user_id}]"

    def download_all_messages(self, peer_id, output_file="messages.txt"):
        """Скачивание всех сообщений и сохранение в текстовый файл"""
        all_messages = []
        all_profiles = []
        all_groups = []
        
        offset = 0
        batch_size = 200
        total_messages = 0
        
        print("Начинаем скачивание сообщений...")
        
        # Сначала получим общее количество сообщений
        try:
            initial_data = self.get_messages_batch(peer_id, 0, 1)
            if 'count' in initial_data:
                total_messages = initial_data['count']
                print(f"Всего сообщений в диалоге: {total_messages}")
        except Exception as e:
            print(f"Ошибка при получении количества сообщений: {e}")
        
        while True:
            print(f"Загружаем сообщения с offset {offset} (загружено {len(all_messages)} сообщений)...")
            
            try:
                data = self.get_messages_batch(peer_id, offset, batch_size)
                
                # Сохраняем информацию о пользователях и группах
                if 'profiles' in data:
                    all_profiles.extend(data['profiles'])
                if 'groups' in data:
                    all_groups.extend(data['groups'])
                
                messages = data.get('items', [])
                
                if not messages:
                    print("Больше нет сообщений для загрузки")
                    break
                
                # Фильтруем только текстовые сообщения
                text_messages = []
                for message in messages:
                    if self.is_text_message(message):
                        text_messages.append(message)
                
                all_messages.extend(text_messages)
                
                print(f"Загружено {len(messages)} сообщений, из них текстовых: {len(text_messages)}")
                
                # Проверяем, достигли ли конца
                if len(messages) < batch_size:
                    print("Достигнут конец истории сообщений")
                    break
                    
                offset += batch_size
                time.sleep(0.34)  # Задержка для соблюдения лимитов API
                
            except Exception as e:
                print(f"Ошибка при загрузке сообщений: {e}")
                break
        
        # Сохраняем сообщения с датой и автором
        with open(output_file, 'w', encoding='utf-8') as f:
            for message in all_messages:
                # Получаем дату сообщения
                date = datetime.fromtimestamp(message['date']).strftime('%Y-%m-%d %H:%M:%S')
                
                # Получаем информацию об авторе
                author_id = message.get('from_id', message.get('user_id', 0))
                author_name = self.get_user_info(author_id, all_profiles, all_groups)
                
                # Очищаем текст от лишних пробелов
                text = message['text'].strip().replace('\n', ' ')  # Заменяем переносы на пробелы
                
                # Записываем сообщение в формате: [Дата] Автор: Текст
                f.write(f"[{date}] {author_name}: {text}\n")
        
        print(f"Скачано {len(all_messages)} текстовых сообщений из {total_messages} всего. Сохранено в {output_file}")
        
        # Дополнительная информация для отладки
        if total_messages > 0:
            percentage = (len(all_messages) / total_messages) * 100
            print(f"Загружено {percentage:.1f}% сообщений")
        
        return all_messages

# Использование
if __name__ == "__main__":
    # Загружаем переменные окружения
    load_dotenv(find_dotenv())
    
    # Ваш access token из VK
    ACCESS_TOKEN = os.getenv('access_token')
    
    if not ACCESS_TOKEN:
        raise ValueError("Access token не найден. Убедитесь, что он указан в файле .env")
    
    # ID диалога (пользователя или беседы)
    # Для пользователя: его ID
    # Для беседы: 2000000000 + ID беседы
    PEER_ID = 504000332
    
    downloader = VKMessagesDownloader(ACCESS_TOKEN)
    messages = downloader.download_all_messages(PEER_ID, "messages.txt")