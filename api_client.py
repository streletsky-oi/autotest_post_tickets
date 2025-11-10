import requests
import base64


class ApiClient:
    def __init__(self):
        self.base_url = 'https://ooobnalshik.helpdeskeddy.com/api/v2'
        self.email = ''
        self.token = ''
        self.session = requests.Session()

        # Basic Auth encoding
        credentials = f"{self.email}:{self.token}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        self.session.headers.update({
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json'
        })

    def create_ticket(self, ticket_data):
        """Создание нового тикета"""
        url = f"{self.base_url}/tickets"
        response = self.session.post(url, json=ticket_data)
        return response

    def get_ticket(self, ticket_id):
        """Получение тикета по ID"""
        url = f"{self.base_url}/tickets/{ticket_id}"
        response = self.session.get(url)
        return response

    def _extract_ticket_data(self, response_data):
        """Извлечение данных тикета из response (обработка формата с числовым ID)"""
        if 'data' in response_data:
            data = response_data['data']
            # Если data - словарь и первый ключ числовой, берем первый элемент
            if isinstance(data, dict) and data:
                first_key = next(iter(data))
                if first_key.isdigit():
                    return data[first_key]
            return data
        return response_data

    def get_priorities(self):
        """Получение списка приоритетов"""
        try:
            response = self.session.get(f"{self.base_url}/priorities")
            return response.json() if response.status_code == 200 else []
        except:
            return []

    def get_types(self):
        """Получение списка типов"""
        try:
            response = self.session.get(f"{self.base_url}/types")
            return response.json() if response.status_code == 200 else []
        except:
            return []

    def get_statuses(self):
        """Получение списка статусов"""
        try:
            response = self.session.get(f"{self.base_url}/statuses")
            return response.json() if response.status_code == 200 else []
        except:
            return []

    def get_departments(self):
        """Получение списка департаментов"""
        try:
            response = self.session.get(f"{self.base_url}/departments")
            return response.json() if response.status_code == 200 else []
        except:
            return []

    def get_staff_users(self):
        """Получение списка сотрудников"""
        try:
            response = self.session.get(f"{self.base_url}/staff")
            return response.json() if response.status_code == 200 else []
        except:
            return []
