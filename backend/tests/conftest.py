import sys
import os
import pytest
import datetime
from unittest.mock import patch, MagicMock

# Добавляем путь к проекту
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Мокаем окружение перед импортом приложения
os.environ['DATABASE_URL'] = 'sqlite:///:memory:'

with patch('dotenv.load_dotenv'):
    with patch('flask_cors.CORS'):
        # Импортируем приложение после мокинга
        from app import app as flask_app
        from database import db
        from models import Gift

@pytest.fixture(scope='session')
def app():
    """Создаем тестовое приложение"""
    # Настраиваем для тестов
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'SQLALCHEMY_TRACK_MODIFICATIONS': False,
        'WTF_CSRF_ENABLED': False
    })
    
    # Создаем таблицы
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.drop_all()

@pytest.fixture
def client(app):
    """Тестовый клиент"""
    return app.test_client()

# ВАЖНО: Заменяем db_session на session без create_scoped_session
@pytest.fixture
def session(app):
    """Упрощенная фикстура для работы с БД"""
    with app.app_context():
        # Начинаем новую транзакцию для изоляции тестов
        db.session.begin_nested()
        
        yield db.session
        
        # Откатываем изменения после теста
        db.session.rollback()
        db.session.remove()

@pytest.fixture
def sample_gift_data():
    """Данные для создания подарка"""
    return {
        'title': 'Тестовый подарок',
        'description': 'Описание тестового подарка',
        'recipient': 'Иван Иванов',
        'price': 1500.50,
        'completed': False
    }

@pytest.fixture
def create_gift(session):  # Используем session вместо db_session
    """Фабрика для создания подарков в БД"""
    def _create_gift(**kwargs):
        default_data = {
            'title': 'Тестовый подарок',
            'description': '',
            'recipient': '',
            'price': 0.0,
            'completed': False
        }
        default_data.update(kwargs)
        
        gift = Gift(**default_data)
        session.add(gift)
        session.commit()
        return gift
    
    return _create_gift