import GiftList from '../components/GiftList'

export default function Home() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-green-50 p-4">
      <div className="max-w-4xl mx-auto">
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-red-600 mb-2">🎄 Список новогодних подарков 🎁</h1>
          <p className="text-gray-600">Составьте список подарков для своих близких</p>
        </header>
        <GiftList />
      </div>
    </div>
  )
}