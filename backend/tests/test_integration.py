import json
import pytest

class TestIntegration:
    """Интеграционные тесты"""
    
    def test_full_crud_cycle(self, client):
        """Полный цикл CRUD операций"""
        # 1. CREATE
        create_data = {
            'title': 'Интеграционный тест',
            'description': 'Подарок для интеграционного теста',
            'price': 1500,
            'recipient': 'Тестовый получатель'
        }
        
        create_response = client.post(
            '/api/gifts',
            data=json.dumps(create_data),
            content_type='application/json'
        )
        assert create_response.status_code == 201
        gift_id = create_response.get_json()['id']
        
        # 2. READ (проверяем что создался)
        get_response = client.get('/api/gifts')
        assert get_response.status_code == 200
        gifts = get_response.get_json()
        
        # Ищем созданный подарок
        created_gift = next((g for g in gifts if g['id'] == gift_id), None)
        assert created_gift is not None
        assert created_gift['title'] == create_data['title']
        assert created_gift['price'] == create_data['price']
        
        # 3. UPDATE
        update_data = {
            'title': 'Обновленный интеграционный тест',
            'completed': True,
            'price': 2000
        }
        
        update_response = client.put(
            f'/api/gifts/{gift_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        assert update_response.status_code == 200
        
        # 4. READ (проверяем обновление)
        get_response = client.get('/api/gifts')
        updated_gift = next((g for g in get_response.get_json() if g['id'] == gift_id), None)
        assert updated_gift['title'] == update_data['title']
        assert updated_gift['completed'] == update_data['completed']
        assert updated_gift['price'] == update_data['price']
        
        # 5. DELETE
        delete_response = client.delete(f'/api/gifts/{gift_id}')
        assert delete_response.status_code == 200
        
        # 6. READ (проверяем удаление)
        final_response = client.get('/api/gifts')
        final_gifts = final_response.get_json()
        deleted_gift = next((g for g in final_gifts if g['id'] == gift_id), None)
        assert deleted_gift is None
    
    def test_concurrent_operations(self, client, create_gift):
        """Тест нескольких операций подряд"""
        # Создаем несколько подарков
        for i in range(3):
            response = client.post(
                '/api/gifts',
                data=json.dumps({'title': f'Подарок {i+1}'}),
                content_type='application/json'
            )
            assert response.status_code == 201
        
        # Получаем все
        response = client.get('/api/gifts')
        assert response.status_code == 200
        gifts = response.get_json()
        assert len(gifts) == 10
        
        # Обновляем первый
        if gifts:
            update_response = client.put(
                f'/api/gifts/{gifts[0]["id"]}',
                data=json.dumps({'completed': True}),
                content_type='application/json'
            )
            assert update_response.status_code == 200
        
        # Удаляем последний
        if gifts:
            delete_response = client.delete(f'/api/gifts/{gifts[-1]["id"]}')
            assert delete_response.status_code == 200
    
    def test_error_handling_integration(self, client):
        """Тест обработки ошибок"""
        # Попытка обновить несуществующий
        response = client.put(
            '/api/gifts/999999',
            data=json.dumps({'title': 'Тест'}),
            content_type='application/json'
        )
        assert response.status_code == 404
        
        # Попытка удалить несуществующий
        response = client.delete('/api/gifts/999999')
        assert response.status_code == 404