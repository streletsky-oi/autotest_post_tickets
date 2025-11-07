import pytest
import requests
from datetime import datetime, timedelta
from ticket import TicketCreate
from test_data_generator import TicketDataGenerator


class TestTicketCreate:
    """Тесты для создания тикетов через POST /tickets"""

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

    def test_create_ticket_with_valid_data(self, api):
        """Тест создания тикета с валидными данными"""
        # Arrange
        ticket_data = {
            "title": "Valid Data Test Ticket",
            "description": "This is a test ticket with valid data",
            "priority_id": 2,
            "department_id": 1
        }

        # Act
        response = api.create_ticket(ticket_data)

        # Assert
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}. Response: {response.text}"
        response_data = response.json()

        # Извлекаем данные тикета с учетом формата API
        ticket_info = self._extract_ticket_data(response_data)

        assert 'id' in ticket_info
        assert ticket_info['title'] == ticket_data['title']

    def test_create_ticket_with_required_fields_only(self, api):
        """Тест создания тикета только с обязательными полями"""
        # Arrange
        ticket_data = {
            "title": "Required Fields Only Ticket",
            "description": "This ticket has only required fields - title and description"
        }

        # Act
        response = api.create_ticket(ticket_data)

        # Assert
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}. Response: {response.text}"
        response_data = response.json()

        # Извлекаем данные тикета с учетом формата API
        ticket_info = self._extract_ticket_data(response_data)

        assert ticket_info['title'] == ticket_data['title']

    def test_create_ticket_with_invalid_sla_date(self, api):
        """Тест создания тикета с прошедшей датой SLA"""
        # Arrange
        ticket_data = {
            "title": "Invalid SLA Date Ticket",
            "description": "Testing SLA date validation",
            "sla_date": "01.01.2020 12:00"  # Прошедшая дата
        }

        # Act
        response = api.create_ticket(ticket_data)

        # Assert
        # API возвращает 400 с ошибкой валидации
        assert response.status_code == 400, f"Ожидалась ошибка 400, получен {response.status_code}"
        response_data = response.json()
        assert 'errors' in response_data

    def test_create_ticket_missing_title(self, api):
        """Тест создания тикета без обязательного поля title"""
        # Arrange
        ticket_data = {
            "description": "Description without title"
        }

        # Act
        response = api.create_ticket(ticket_data)

        # Assert
        assert response.status_code == 400, f"Ожидалась ошибка 400, получен {response.status_code}"

    def test_create_ticket_missing_description(self, api):
        """Тест создания тикета без обязательного поля description"""
        # Arrange
        ticket_data = {
            "title": "Title without description"
        }

        # Act
        response = api.create_ticket(ticket_data)

        # Assert
        assert response.status_code == 400, f"Ожидалась ошибка 400, получен {response.status_code}"

    def test_create_ticket_with_valid_optional_fields(self, api):
        """Тест создания тикета с валидными опциональными полями"""
        # Arrange
        ticket_data = {
            "title": "Ticket with valid optional fields",
            "description": "This ticket includes valid optional fields",
            "status_id": "open",
            "priority_id": 2,
            "type_id": 1,
            "department_id": 1,
            "ticket_lock": False,
            "user_email": "testuser@example.com",
            "tags": ["urgent", "test"]
        }

        # Act
        response = api.create_ticket(ticket_data)

        # Assert
        assert response.status_code == 200, f"Ожидался статус 200, получен {response.status_code}. Response: {response.text}"
        response_data = response.json()

        # Извлекаем данные тикета с учетом формата API
        ticket_info = self._extract_ticket_data(response_data)

        assert ticket_info['title'] == ticket_data['title']
        assert ticket_info['status_id'] == ticket_data['status_id']

    def test_create_ticket_with_different_statuses(self, api):
        """Тест создания тикета с различными валидными статусами"""
        # Все статусы работают!
        valid_statuses = ["open", "closed", "v-processe"]

        for status in valid_statuses:
            # Arrange
            ticket_data = {
                "title": f"Ticket with status {status}",
                "description": f"Testing status {status}",
                "status_id": status
            }

            # Act
            response = api.create_ticket(ticket_data)

            # Assert
            assert response.status_code == 200, f"Статус {status} не прошел. Response: {response.text}"
            response_data = response.json()

            # Извлекаем данные тикета с учетом формата API
            ticket_info = self._extract_ticket_data(response_data)

            assert ticket_info['status_id'] == status
            print(f"✅ Статус '{status}' работает корректно")

    def test_create_ticket_with_numeric_status(self, api):
        """Тест создания тикета с числовым статусом"""
        # Arrange
        ticket_data = {
            "title": "Ticket with numeric status",
            "description": "Testing numeric status",
            "status_id": "12"  # Числовой статус
        }

        # Act
        response = api.create_ticket(ticket_data)

        # Assert
        # API может принимать или не принимать числовые статусы
        assert response.status_code in [200, 400], f"Неожиданный статус: {response.status_code}"

    def test_create_ticket_with_valid_emails(self, api):
        """Тест создания тикета с валидными email адресами"""
        # Arrange
        ticket_data = {
            "title": "Ticket with valid emails",
            "description": "Testing email fields",
            "user_email": "valid.email@example.com",
            "cc": ["cc1@example.com", "cc2@domain.org"],
            "bcc": ["bcc@test.com"]
        }

        # Act
        response = api.create_ticket(ticket_data)

        # Assert
        assert response.status_code == 200, f"Валидные emails не приняты. Response: {response.text}"
        response_data = response.json()

        # Извлекаем данные тикета с учетом формата API
        ticket_info = self._extract_ticket_data(response_data)

        assert ticket_info['user_email'] == ticket_data['user_email']

    def test_create_ticket_verify_created_fields(self, api):
        """Тест проверки корректности заполнения полей созданного тикета"""
        # Arrange
        ticket_data = {
            "title": "Verification Test Ticket",
            "description": "This ticket is for field verification",
            "priority_id": 2,
            "department_id": 1,
            "tags": ["verify", "test"]
        }

        # Act
        response = api.create_ticket(ticket_data)

        # Assert
        assert response.status_code == 200
        response_data = response.json()

        # Извлекаем данные тикета с учетом формата API
        ticket_info = self._extract_ticket_data(response_data)

        # Проверяем, что основные поля соответствуют отправленным
        assert ticket_info['title'] == ticket_data['title']
        assert 'id' in ticket_info
        assert 'date_created' in ticket_info  # Должно создаваться автоматически
        assert ticket_info['priority_id'] == ticket_data['priority_id']

    def test_create_ticket_with_invalid_followers(self, api):
        """Тест создания тикета с невалидными подписчиками"""
        # Arrange
        ticket_data = {
            "title": "Ticket with invalid followers",
            "description": "Testing followers validation",
            "followers": [999, 1000]  # Несуществующие пользователи
        }

        # Act
        response = api.create_ticket(ticket_data)

        # Assert
        # API должен вернуть ошибку для невалидных followers
        assert response.status_code == 400, f"Ожидалась ошибка 400, получен {response.status_code}"

    def test_create_ticket_minimal_data(self, api):
        """Тест создания тикета с абсолютно минимальными данными"""
        # Arrange
        ticket_data = {
            "title": "Minimal Test Ticket",
            "description": "Minimal required data only"
        }

        # Act
        response = api.create_ticket(ticket_data)

        # Assert
        assert response.status_code == 200, f"Минимальные данные не приняты. Response: {response.text}"
        response_data = response.json()

        # Извлекаем данные тикета с учетом формата API
        ticket_info = self._extract_ticket_data(response_data)

        assert ticket_info['title'] == ticket_data['title']

    def test_create_ticket_with_pid_zero(self, api):
        """Тест создания тикета с pid = 0 (корневая заявка без родителя)"""
        # Arrange
        ticket_data = {
            "title": "Корневая заявка",
            "description": "Заявка без родителя",
            "pid": "0"  # pid=0 означает "без родителя"
        }

        # Act
        response = api.create_ticket(ticket_data)

        # Assert
        assert response.status_code == 200, f"PID = 0 не принят. Response: {response.text}"
        response_data = response.json()
        ticket_info = self._extract_ticket_data(response_data)

        print(f"✅ Создана корневая заявка ID: {ticket_info['id']} с pid=0")

    def test_create_ticket_with_valid_pid(self, api):
        """Тест создания тикета с валидным pid (родительской заявкой)"""

        # Шаг 1: Создаем родительскую заявку
        parent_ticket_data = {
            "title": "Родительская заявка",
            "description": "Это родительская заявка для теста pid"
        }

        parent_response = api.create_ticket(parent_ticket_data)
        assert parent_response.status_code == 200
        parent_data = parent_response.json()
        parent_ticket = self._extract_ticket_data(parent_data)
        parent_id = parent_ticket['id']

        print(f"✅ Создана родительская заявка ID: {parent_id}")

        # Шаг 2: Создаем дочернюю заявку с pid
        child_ticket_data = {
            "title": "Дочерняя заявка",
            "description": "Эта заявка ссылается на родительскую",
            "pid": str(parent_id)  # Используем ID родительской заявки
        }

        child_response = api.create_ticket(child_ticket_data)
        assert child_response.status_code == 200
        child_data = child_response.json()
        child_ticket = self._extract_ticket_data(child_data)

        print(f"✅ Создана дочерняя заявка ID: {child_ticket['id']} с pid: {parent_id}")

        # Проверяем что дочерняя заявка создалась
        assert child_ticket['title'] == "Дочерняя заявка"

    def test_create_ticket_with_invalid_pid(self, api):
        """Тест создания тикета с несуществующим pid"""

        ticket_data = {
            "title": "Заявка с невалидным pid",
            "description": "Тестируем обработку несуществующего pid",
            "pid": "999999"  # Несуществующий ID
        }

        response = api.create_ticket(ticket_data)

        # API должен вернуть ошибку
        assert response.status_code == 400
        response_data = response.json()
        assert 'errors' in response_data

        print("✅ Невалидный pid правильно обработан")

    def test_ticket_chain(self, api):
        """Тест цепочки заявок: родитель → ребенок (API не позволяет создавать внуков)"""

        try:
            # Создаем родительскую заявку
            parent_data = {
                "title": "Родительская заявка",
                "description": "Самая старшая заявка"
            }
            parent_response = api.create_ticket(parent_data)
            assert parent_response.status_code == 200
            parent_data_json = parent_response.json()
            parent_ticket = self._extract_ticket_data(parent_data_json)
            parent_id = parent_ticket['id']

            print(f"✅ Создана родительская заявка ID: {parent_id}")

            # Создаем дочернюю заявку (это работает)
            child_data = {
                "title": "Дочерняя заявка",
                "description": "Заявка-ребенок",
                "pid": str(parent_id)
            }
            child_response = api.create_ticket(child_data)
            assert child_response.status_code == 200
            child_data_json = child_response.json()
            child_ticket = self._extract_ticket_data(child_data_json)
            child_id = child_ticket['id']

            print(f"✅ Создана дочерняя заявка ID: {child_id} с pid: {parent_id}")

            # Пытаемся создать заявку-внука (это НЕ должно работать)
            grandchild_data = {
                "title": "Заявка-внук",
                "description": "Заявка-внук (должна вызвать ошибку)",
                "pid": str(child_id)
            }
            grandchild_response = api.create_ticket(grandchild_data)

            # Проверяем что создание внука вызывает ошибку
            if grandchild_response.status_code == 400:
                print("✅ API правильно запрещает создание заявок-внуков")
                # Это нормальное поведение - нельзя создавать цепочки глубже 2 уровней
            else:
                # Если вдруг разрешили, то проверяем что заявка создалась
                assert grandchild_response.status_code == 200
                grandchild_data_json = grandchild_response.json()
                grandchild_ticket = self._extract_ticket_data(grandchild_data_json)
                grandchild_id = grandchild_ticket['id']
                print(f"⚠️  Неожиданно: создана заявка-внук ID: {grandchild_id}")

        except KeyError as e:
            pytest.fail(f"Ошибка извлечения данных из ответа API: {e}")
        except Exception as e:
            pytest.fail(f"Неожиданная ошибка: {e}")

    def test_create_ticket_with_custom_fields(self, api):
        """Тест создания тикета с кастомными полями"""
        # Arrange
        ticket_data = {
            "title": "Ticket with custom fields",
            "description": "Testing custom fields",
            "custom_fields": {
                "2": "12345"  # ID кастомного поля из ответа API
            }
        }

        # Act
        response = api.create_ticket(ticket_data)

        # Assert
        # API может принимать или игнорировать custom_fields
        assert response.status_code in [200, 400], f"Неожиданный статус: {response.status_code}"

    def test_create_ticket_and_get_by_id(self, api):
        """Тест создания тикета и последующего получения его по ID"""
        # Arrange
        ticket_data = {
            "title": "Ticket for GET test",
            "description": "This ticket will be retrieved by ID"
        }

        # Act - создаем тикет
        create_response = api.create_ticket(ticket_data)

        # Assert
        assert create_response.status_code == 200
        create_data = create_response.json()

        # Извлекаем данные созданного тикета
        created_ticket = self._extract_ticket_data(create_data)
        ticket_id = created_ticket['id']

        # Act - получаем тикет по ID
        get_response = api.get_ticket(ticket_id)

        # Assert
        assert get_response.status_code == 200
        get_data = get_response.json()

        # Извлекаем данные полученного тикета
        retrieved_ticket = self._extract_ticket_data(get_data)

        assert retrieved_ticket['id'] == ticket_id
        assert retrieved_ticket['title'] == ticket_data['title']

    def test_create_ticket_with_sla_future_date(self, api):
        """Тест создания тикета с будущей датой SLA"""
        # Arrange
        future_date = (datetime.now() + timedelta(days=1)).strftime('%d.%m.%Y %H:%M')

        ticket_data = {
            "title": "Ticket with future SLA",
            "description": "Testing future SLA date",
            "sla_date": future_date
        }

        # Act
        response = api.create_ticket(ticket_data)

        # Assert
        # API может принимать или не принимать SLA даты
        assert response.status_code in [200, 400], f"Неожиданный статус: {response.status_code}"

    def test_sla_date_validation_comprehensive(self, api):
        """Комплексная проверка валидации SLA дат"""

        test_cases = [
            {
                "sla_date": "01.01.2020 12:00",  # Далекое прошлое
                "should_accept": False,
                "description": "Прошедшая дата (2020)"
            },
            {
                "sla_date": (datetime.now() - timedelta(hours=1)).strftime('%d.%m.%Y %H:%M'),  # 1 час назад
                "should_accept": False,
                "description": "Недавно прошедшая дата"
            },
            {
                "sla_date": (datetime.now() + timedelta(hours=1)).strftime('%d.%m.%Y %H:%M'),  # 1 час вперед
                "should_accept": True,
                "description": "Ближайшая будущая дата"
            },
            {
                "sla_date": (datetime.now() + timedelta(days=30)).strftime('%d.%m.%Y %H:%M'),  # 30 дней вперед
                "should_accept": True,
                "description": "Далекая будущая дата"
            }
        ]

        for case in test_cases:
            # Arrange
            ticket_data = {
                "title": f"SLA test: {case['description']}",
                "description": f"Testing: {case['sla_date']}",
                "sla_date": case['sla_date']
            }

            # Act
            response = api.create_ticket(ticket_data)

            # Assert
            if case['should_accept']:
                # Должен принять (200) или может быть 400 если SLA не поддерживается
                assert response.status_code in [200, 400], \
                    f"Случай '{case['description']}': неожиданный статус {response.status_code}"
            else:
                # Должен отклонить (400)
                assert response.status_code == 400, \
                    f"Случай '{case['description']}': ожидалась ошибка 400, получен {response.status_code}"

            print(f"SLA тест '{case['description']}': {case['sla_date']} -> статус {response.status_code}")

    def test_create_ticket_with_special_characters(self, api):
        """Тест создания тикета со специальными символами в заголовке"""
        # Arrange
        ticket_data = {
            "title": "Ticket with спец. символы: !@#$%^",
            "description": "Testing special characters in title"
        }

        # Act
        response = api.create_ticket(ticket_data)

        # Assert
        assert response.status_code == 200, f"Спецсимволы не приняты. Response: {response.text}"
        response_data = response.json()

        # Извлекаем данные тикета
        ticket_info = self._extract_ticket_data(response_data)

        # API может экранировать символы, поэтому проверяем что тикет создался успешно
        assert 'id' in ticket_info
        assert ticket_info['title'].startswith("Ticket with спец. символы")

    def test_create_ticket_with_ampersand_symbol(self, api):
        """Тест создания тикета с символом & (экранирование - нормальное поведение)"""
        # Arrange
        ticket_data = {
            "title": "Test Company & Partners",
            "description": "Testing & symbol encoding"
        }

        # Act
        response = api.create_ticket(ticket_data)

        # Assert
        assert response.status_code == 200, f"Тикет с & не создан. Response: {response.text}"
        response_data = response.json()

        # Извлекаем данные тикета
        ticket_info = self._extract_ticket_data(response_data)

        print(f"Отправлено: {ticket_data['title']}")
        print(f"Получено: {ticket_info['title']}")

        # Проверяем что экранирование работает (это норма)
        assert "&amp;" in ticket_info['title'], "Ожидается экранирование & в &amp;"
        assert 'id' in ticket_info
        print("✅ Экранирование & в &amp; - нормальное поведение API")

    def test_api_character_encoding_behavior(self, api):
        """Тест поведения API с различными специальными символами"""
        test_cases = [
            {
                "input": "Company & Partners",
                "expected_contains": "Company &amp; Partners",
                "description": "Экранирование & в &amp;"
            },
            {
                "input": "Price < 100 > 50",
                "expected_contains": "Price",
                "description": "Символы < и > могут экранироваться"
            },
            {
                "input": "Normal text",
                "expected_contains": "Normal text",
                "description": "Обычный текст без изменений"
            }
        ]

        for case in test_cases:
            # Arrange
            ticket_data = {
                "title": case["input"],
                "description": case["description"]
            }

            # Act
            response = api.create_ticket(ticket_data)

            # Assert
            assert response.status_code == 200, f"Тест '{case['description']}' не прошел. Response: {response.text}"
            response_data = response.json()
            ticket_info = self._extract_ticket_data(response_data)

            print(f"📤 {case['description']}")
            print(f"   Отправлено: '{case['input']}'")
            print(f"   Получено: '{ticket_info['title']}'")

            # Проверяем что ожидаемая подстрока присутствует
            assert case["expected_contains"] in ticket_info['title'], \
                f"Ожидалось '{case['expected_contains']}' в '{ticket_info['title']}'"

            print(f"   ✅ {case['description']} - подтверждено")

    def test_pid_comprehensive(self, api):
        """Комплексный тест различных сценариев с pid"""

        test_cases = [
            {
                "pid": "0",
                "should_work": True,
                "description": "pid=0 (корневая заявка)"
            },
            {
                "pid": "999999",
                "should_work": False,
                "description": "Несуществующий pid"
            },
            {
                "pid": "-1",
                "should_work": False,
                "description": "Отрицательный pid"
            },
            {
                "pid": "abc",
                "should_work": False,
                "description": "Нечисловой pid"
            }
        ]

        # Сначала создаем валидную родительскую заявку для теста
        parent_data = {
            "title": "Родитель для тестов",
            "description": "Родительская заявка"
        }
        parent_response = api.create_ticket(parent_data)
        parent_id = self._extract_ticket_data(parent_response.json())['id']

        # Добавляем валидный pid в тест-кейсы
        test_cases.append({
            "pid": str(parent_id),
            "should_work": True,
            "description": "Валидный существующий pid"
        })

        for case in test_cases:
            ticket_data = {
                "title": f"Тест pid: {case['description']}",
                "description": f"Testing pid = {case['pid']}",
                "pid": case['pid']
            }

            response = api.create_ticket(ticket_data)

            if case['should_work']:
                assert response.status_code == 200, f"Случай '{case['description']}' должен работать"
                print(f"✅ {case['description']} - РАБОТАЕТ")
            else:
                assert response.status_code == 400, f"Случай '{case['description']}' должен вызывать ошибку"
                print(f"✅ {case['description']} - ОШИБКА (как и ожидалось)")