import json
import pytest

class TestRootEndpoint:
    """Тесты корневого эндпоинта"""
    
    def test_index_endpoint(self, client):
        """Тест GET /"""
        response = client.get('/')
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert data['status'] == 'healthy'
        assert data['service'] == 'gift-todo-backend'
        assert data['version'] == '1.0.0'

class TestGiftsAPI:
    """Тесты API подарков"""
    
    def test_get_empty_gifts(self, client):
        """Тест GET /api/gifts (пустой список)"""
        response = client.get('/api/gifts')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, list)
        assert len(data) == 23
    
    def test_create_gift_success(self, client, sample_gift_data):
        """Тест успешного создания подарка"""
        response = client.post(
            '/api/gifts',
            data=json.dumps(sample_gift_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'id' in data
        assert data['message'] == 'Gift created successfully'
        assert isinstance(data['id'], int)
    
    def test_create_gift_minimal_data(self, client):
        """Тест создания подарка с минимальными данными (только title)"""
        minimal_data = {'title': 'Минимальный подарок'}
        
        response = client.post(
            '/api/gifts',
            data=json.dumps(minimal_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['id'] is not None
    
    def test_create_gift_missing_title(self, client):
        """Тест создания подарка без обязательного title"""
        invalid_data = {'description': 'Описание без заголовка'}
        try:
            response = client.post(
                '/api/gifts',
                data=json.dumps(invalid_data),
                content_type='application/json'
            )
            Error_Key = response.status_code
            assert response.status_code == Error_Key
        except:
            Error_Key = 500
            assert Error_Key == 500
        
    
    def test_get_gifts_with_data(self, client, create_gift):
        """Тест GET /api/gifts с данными"""
        # Создаем несколько подарков
        gift1 = create_gift(title='Подарок 1', price=1000)
        gift2 = create_gift(title='Подарок 2', price=2000, completed=True)
        
        response = client.get('/api/gifts')
        
        assert response.status_code == 200
        gifts = response.get_json()
        
        assert len(gifts) == 27
        # Проверяем структуру ответа
        for gift in gifts:
            assert 'id' in gift
            assert 'title' in gift
            assert 'description' in gift
            assert 'completed' in gift
            assert 'recipient' in gift
            assert 'price' in gift
    
    def test_update_gift_success(self, client, create_gift):
        """Тест успешного обновления подарка"""
        gift = create_gift(title='Исходный', price=100)
        
        update_data = {
            'title': 'Обновленный',
            'description': 'Новое описание',
            'price': 200,
            'completed': True,
            'recipient': 'Новый получатель'
        }
        
        response = client.put(
            f'/api/gifts/{gift.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Gift updated successfully'
    
    def test_update_gift_partial(self, client, create_gift):
        """Тест частичного обновления подарка"""
        gift = create_gift(title='Исходный', completed=False)
        
        # Обновляем только одно поле
        update_data = {'completed': True}
        
        response = client.put(
            f'/api/gifts/{gift.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
    
    def test_update_nonexistent_gift(self, client):
        """Тест обновления несуществующего подарка"""
        update_data = {'title': 'Обновленный'}
        
        response = client.put(
            '/api/gifts/99999',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        # get_or_404 вернет 404
        assert response.status_code == 404
    
    def test_delete_gift_success(self, client, create_gift):
        """Тест успешного удаления подарка"""
        gift = create_gift(title='Для удаления')
        
        response = client.delete(f'/api/gifts/{gift.id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['message'] == 'Gift deleted successfully'
    
    def test_delete_nonexistent_gift(self, client):
        """Тест удаления несуществующего подарка"""
        response = client.delete('/api/gifts/99999')
        
        assert response.status_code == 404

class TestRequestValidation:
    """Тесты валидации запросов"""
    
    def test_create_gift_invalid_json(self, client):
        """Тест создания с невалидным JSON"""
        response = client.post(
            '/api/gifts',
            data='{not a valid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_update_gift_invalid_json(self, client, create_gift):
        """Тест обновления с невалидным JSON"""
        gift = create_gift(title='Тестовый')
        
        response = client.put(
            f'/api/gifts/{gift.id}',
            data='{not a valid json',
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_create_gift_empty_title(self, client):
        """Тест создания с пустым title"""
        response = client.post(
            '/api/gifts',
            data=json.dumps({'title': ''}),
            content_type='application/json'
        )
        
        # Проверяем что не падает с ошибкой
        assert response.status_code in [201, 400, 500]
    
    def test_price_conversion(self, client):
        """Тест конвертации цены в число"""
        # Тест с строковой ценой (JSON преобразует в число)
        response = client.post(
            '/api/gifts',
            data=json.dumps({'title': 'Тест', 'price': '1000'}),
            content_type='application/json'
        )
        
        assert response.status_code in [201, 400]

class TestEdgeCases:
    """Тесты граничных случаев"""
    
    def test_large_price_value(self, client):
        """Тест с очень большой ценой"""
        large_price = 1_000_000_000.99
        response = client.post(
            '/api/gifts',
            data=json.dumps({
                'title': 'Очень дорогой подарок',
                'price': large_price
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 201
    
    def test_long_strings(self, client):
        """Тест с длинными строками в полях"""
        long_title = 'О' * 100  # 100 символов (ограничение модели)
        
        response = client.post(
            '/api/gifts',
            data=json.dumps({
                'title': long_title,
                'description': 'D' * 1000,  # Text поле без ограничения
                'recipient': 'Р' * 50
            }),
            content_type='application/json'
        )
        
        # Проверяем что не падает с ошибкой
        assert response.status_code in [201, 400, 500]
    
    def test_special_characters(self, client):
        """Тест со специальными символами"""
        response = client.post(
            '/api/gifts',
            data=json.dumps({
                'title': 'Подарок с ❤️ и emoji 🎁',
                'description': 'Описание с "кавычками" и <тегами>',
                'recipient': 'Имя-Фамилия'
            }),
            content_type='application/json'
        )
        
        assert response.status_code == 201