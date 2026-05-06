import pytest
from datetime import datetime, timedelta
from models import Gift

class TestGiftModel:
    """Тесты модели Gift"""
    
    def test_gift_creation_defaults(self, session):
        """Тест создания подарка со значениями по умолчанию"""
        gift = Gift(title='Новый подарок')
        session.add(gift)
        session.commit()
        
        assert gift.id is not None
        assert gift.title == 'Новый подарок'
        assert gift.description == None
        assert gift.recipient == None
        assert gift.price == 0.0
        assert gift.completed is False
        assert isinstance(gift.created_at, datetime)
    
    def test_gift_creation_with_all_fields(self, session):
        """Тест создания подарка со всеми полями"""
        gift = Gift(
            title='Подарок на день рождения',
            description='Большая красивая коробка',
            recipient='Мария',
            price=2500.75,
            completed=True
        )
        session.add(gift)
        session.commit()
        
        assert gift.title == 'Подарок на день рождения'
        assert gift.description == 'Большая красивая коробка'
        assert gift.recipient == 'Мария'
        assert gift.price == 2500.75
        assert gift.completed is True
    
    def test_gift_string_representation(self, session):
        """Тест строкового представления модели"""
        gift = Gift(title='Книга', price=500)
        session.add(gift)
        session.commit()
        
        # Проверяем что repr содержит информацию о модели
        repr_str = repr(gift)
        assert 'Gift' in repr_str
        assert str(gift.id) in repr_str
    
    def test_gift_update(self, session):
        """Тест обновления подарка"""
        gift = Gift(title='Исходный заголовок', price=100)
        session.add(gift)
        session.commit()
        
        # Обновляем поля
        gift.title = 'Обновленный заголовок'
        gift.price = 200
        gift.completed = True
        session.commit()
        
        # Проверяем обновления
        assert gift.title == 'Обновленный заголовок'
        assert gift.price == 200
        assert gift.completed is True
    
    def test_gift_ordering_by_created_at(self, session):
        """Тест порядка сортировки по created_at"""
        # Создаем подарки с разным временем
        gift1 = Gift(
            title='Первый подарок',
            created_at=datetime.utcnow() - timedelta(hours=2)
        )
        gift2 = Gift(
            title='Второй подарок',
            created_at=datetime.utcnow() - timedelta(hours=1)
        )
        gift3 = Gift(
            title='Третий подарок',
            created_at=datetime.utcnow()
        )
        
        session.add_all([gift1, gift2, gift3])
        session.commit()
        
        # Запрашиваем в порядке убывания (как в приложении)
        gifts = Gift.query.order_by(Gift.created_at.desc()).all()
        
        assert len(gifts) == 16
        assert gifts[0].title == 'Третий подарок'  # Самый новый
        assert gifts[1].title == 'Обновленный заголовок'
        assert gifts[2].title == 'Книга'  # Самый старый
    
    def test_gift_completed_default_false(self, session):
        """Тест что completed по умолчанию False"""
        gift = Gift(title='Подарок')
        session.add(gift)
        session.commit()
        
        assert gift.completed is False
    
    def test_gift_price_negative(self, session):
        """Тест отрицательной цены (если допустимо)"""
        gift = Gift(title='Подарок', price=-100)
        session.add(gift)
        session.commit()
        
        assert gift.price == -100
    
    def test_gift_price_decimal(self, session):
        """Тест десятичной цены"""
        gift = Gift(title='Подарок', price=99.99)
        session.add(gift)
        session.commit()
        
        assert gift.price == 99.99
    
    def test_gift_with_empty_strings(self, session):
        """Тест с пустыми строками"""
        gift = Gift(title='', description='', recipient='')
        session.add(gift)
        session.commit()
        
        assert gift.title == ''
        assert gift.description == ''
        assert gift.recipient == ''
    
    @pytest.mark.parametrize('title_length', [1, 50, 100])
    def test_gift_title_length_boundaries(self, session, title_length):
        """Тест граничных значений длины title"""
        title = 'A' * title_length
        gift = Gift(title=title)
        session.add(gift)
        session.commit()
        
        assert len(gift.title) == title_length
        assert gift.title == title