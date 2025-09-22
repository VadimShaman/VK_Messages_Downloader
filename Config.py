from dotenv import load_dotenv, find_dotenv
import os

class Config:
    def __init__(self, env_file='.env'):
        # Поиск и загрузка .env файла
        load_dotenv(find_dotenv(env_file))

        DATABASE_URL = os.getenv('DATABASE_URL')
        API_KEY = os.getenv('API_KEY')
        DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'  # с преобразованием типа
        PORT = int(os.getenv('PORT', '8000'))  # значение по умолчанию
        
config = Config()