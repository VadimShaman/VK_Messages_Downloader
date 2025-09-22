import webbrowser

def get_simple_token():
    # Параметры для упрощенной авторизации
    client_id = 6121396  # Официальное приложение VK
    scope = 'messages,offline'  # Права доступа к сообщениям
    redirect_uri = 'https://oauth.vk.com/blank.html'
    
    # Формируем URL для авторизации
    auth_url = (
        f"https://oauth.vk.com/authorize?"
        f"client_id={client_id}&"
        f"display=page&"
        f"redirect_uri={redirect_uri}&"
        f"scope={scope}&"
        f"response_type=token"
    )
    
    print("Открываю браузер для авторизации...")
    print("Если браузер не открылся, перейдите по ссылке вручную:")
    print(auth_url)
    
    # Автоматически открываем браузер
    webbrowser.open(auth_url)
    
    print("\nПосле авторизации:")
    print("1. Браузер перенаправит на страницу с ошибкой - это нормально")
    print("2. Скопируйте token из адресной строки (часть после access_token=)")
    print("3. Вставьте token в код ниже")

get_simple_token()