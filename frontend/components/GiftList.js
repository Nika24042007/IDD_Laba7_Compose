import { useState, useEffect } from 'react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api'

export default function GiftList() {
  const [gifts, setGifts] = useState([])
  const [newGift, setNewGift] = useState({
    title: '',
    description: '',
    recipient: '',
    price: ''
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchGifts()
  }, [])

  const fetchGifts = async () => {
    try {
      const response = await fetch(`${API_URL}/gifts`)
      const data = await response.json()
      setGifts(data)
      setLoading(false)
    } catch (error) {
      console.error('Ошибка загрузки подарков:', error)
      setLoading(false)
    }
  }

  const addGift = async (e) => {
    e.preventDefault()
    if (!newGift.title.trim()) return

    try {
      const response = await fetch(`${API_URL}/gifts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...newGift,
          price: parseFloat(newGift.price) || 0
        })
      })

      if (response.ok) {
        setNewGift({ title: '', description: '', recipient: '', price: '' })
        fetchGifts()
      }
    } catch (error) {
      console.error('Ошибка добавления подарка:', error)
    }
  }

  const toggleComplete = async (id, completed) => {
    try {
      await fetch(`${API_URL}/gifts/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ completed: !completed })
      })
      fetchGifts()
    } catch (error) {
      console.error('Ошибка обновления подарка:', error)
    }
  }

  const deleteGift = async (id) => {
    if (!confirm('Удалить этот подарок из списка?')) return
    
    try {
      await fetch(`${API_URL}/gifts/${id}`, {
        method: 'DELETE'
      })
      fetchGifts()
    } catch (error) {
      console.error('Ошибка удаления подарка:', error)
    }
  }

  const calculateTotal = () => {
    return gifts.reduce((total, gift) => total + (gift.price || 0), 0)
  }

  if (loading) return <div className="text-center py-8">Загрузка...</div>

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-2xl font-bold text-green-700 mb-4">Добавить новый подарок</h2>
        <form onSubmit={addGift} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <input
              type="text"
              placeholder="Название подарка *"
              className="border rounded-lg p-3 focus:ring-2 focus:ring-red-300 focus:outline-none"
              value={newGift.title}
              onChange={(e) => setNewGift({...newGift, title: e.target.value})}
              required
            />
            <input
              type="text"
              placeholder="Для кого (имя)"
              className="border rounded-lg p-3 focus:ring-2 focus:ring-red-300 focus:outline-none"
              value={newGift.recipient}
              onChange={(e) => setNewGift({...newGift, recipient: e.target.value})}
            />
            <input
              type="text"
              placeholder="Описание"
              className="border rounded-lg p-3 focus:ring-2 focus:ring-red-300 focus:outline-none"
              value={newGift.description}
              onChange={(e) => setNewGift({...newGift, description: e.target.value})}
            />
            <input
              type="number"
              placeholder="Цена (руб.)"
              className="border rounded-lg p-3 focus:ring-2 focus:ring-red-300 focus:outline-none"
              value={newGift.price}
              onChange={(e) => setNewGift({...newGift, price: e.target.value})}
            />
          </div>
          <button
            type="submit"
            className="bg-red-600 text-white font-bold py-3 px-6 rounded-lg hover:bg-red-700 transition duration-300 w-full"
          >
            Добавить подарок 🎅
          </button>
        </form>
      </div>

      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-blue-700">Список подарков ({gifts.length})</h2>
          <div className="text-lg font-bold text-green-600">
            Общая стоимость: {calculateTotal().toFixed(2)} руб.
          </div>
        </div>

        {gifts.length === 0 ? (
          <p className="text-gray-500 text-center py-8">Список подарков пуст. Добавьте первый подарок! 🎁</p>
        ) : (
          <div className="space-y-4">
            {gifts.map((gift) => (
              <div
                key={gift.id}
                className={`border rounded-lg p-4 transition-all duration-300 ${
                  gift.completed ? 'bg-green-50 border-green-200' : 'bg-white'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <input
                      type="checkbox"
                      checked={gift.completed}
                      onChange={() => toggleComplete(gift.id, gift.completed)}
                      className="h-5 w-5 text-red-600"
                    />
                    <div>
                      <h3 className={`font-bold text-lg ${gift.completed ? 'line-through text-gray-500' : 'text-gray-800'}`}>
                        {gift.title}
                      </h3>
                      {gift.description && (
                        <p className="text-gray-600">{gift.description}</p>
                      )}
                      <div className="flex space-x-4 mt-2 text-sm">
                        {gift.recipient && (
                          <span className="text-blue-600">👤 {gift.recipient}</span>
                        )}
                        {gift.price > 0 && (
                          <span className="text-green-600">💰 {gift.price} руб.</span>
                        )}
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => deleteGift(gift.id)}
                    className="text-red-500 hover:text-red-700 transition duration-300"
                  >
                    Удалить
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}