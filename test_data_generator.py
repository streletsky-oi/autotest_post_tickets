# utils/test_data_generator.py
from faker import Faker
from datetime import datetime, timedelta
import random

fake = Faker()


class TicketDataGenerator:
    @staticmethod
    def generate_valid_ticket_data():
        """Генерация валидных данных для создания тикета"""
        return {
            "title": f"Test Ticket {fake.random_number()}",
            "description": fake.text(max_nb_chars=200),
            "priority_id": 2,
            "department_id": 1,
            "status_id": "open"
        }

    @staticmethod
    def generate_minimal_ticket():
        """Генерация минимальных данных для создания тикета"""
        return {
            "title": f"Minimal Ticket {fake.random_number()}",
            "description": fake.text(max_nb_chars=100)
        }

    @staticmethod
    def generate_ticket_with_emails():
        """Генерация данных с email адресами"""
        return {
            "title": f"Email Test Ticket {fake.random_number()}",
            "description": fake.text(max_nb_chars=150),
            "user_email": fake.email(),
            "cc": [fake.email() for _ in range(2)],
            "bcc": [fake.email()]
        }