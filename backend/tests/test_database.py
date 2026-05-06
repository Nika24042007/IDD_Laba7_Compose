import pytest
from models import Gift

class TestDatabase:
    """Тесты базы данных"""
    
    def test_db_initialization(self, app):
        """Тест инициализации базы данных"""
        with app.app_context():
            # Проверяем что таблица существует
            from sqlalchemy import inspect
            inspector = inspect(app.extensions['sqlalchemy'].engine)
            tables = inspector.get_table_names()
            
            assert 'gifts' in tables
    
    def test_session_rollback(self, session):
        """Тест отката транзакции"""
        # Создаем подарок
        gift = Gift(title='Подарок для отката')
        session.add(gift)
        session.flush()  # Но не коммитим
        
        # Откатываем
        session.rollback()
        
        # Проверяем что подарок не сохранился
        gifts = session.query(Gift).all()
        assert len(gifts) == 0
    
    def test_multiple_gifts_creation(self, session):
        """Тест создания нескольких подарков"""
        
        gifts = [
            Gift(title=f'Подарок {i}', price=i * 100)
            for i in range(1, 6)
        ]
        
        session.add_all(gifts)
        session.commit()
        
        saved_gifts = session.query(Gift).all()
        assert len(saved_gifts) == 5
        
        for i, gift in enumerate(saved_gifts, 1):
            assert gift.title == f'Подарок {i}'
            assert gift.price == i * 100
    
    def test_gift_query_filters(self, session, create_gift):
        """Тест фильтров запросов"""
        # Создаем подарки с разными статусами
        create_gift(title='Не выполнен', completed=False)
        create_gift(title='Выполнен', completed=True)
        
        # Фильтруем по completed
        completed_gifts = session.query(Gift).filter(Gift.completed == True).all()
        not_completed_gifts = session.query(Gift).filter(Gift.completed == False).all()
        
        assert len(completed_gifts) == 1
        assert completed_gifts[0].title == 'Выполнен'
        
        assert len(not_completed_gifts) == 6
        assert not_completed_gifts[0].title == 'Подарок 1'