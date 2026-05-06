# Wish list ToDo
## Структура
<pre>
APP-TODO/
├── backend/                   # Flask бэкенд-сервер
│   ├── app.py                 # Основной файл приложения Flask (роуты API)
│   ├── models.py              # Модели SQLAlchemy для таблицы gifts
│   ├── database.py            # Конфигурация подключения к БД
│   ├── requirements.txt       # Зависимости Python (Flask, SQLAlchemy, psycopg2)
│   ├── .env.example           # Переменные окружения (DATABASE_URL)
│   
├── frontend/                 # Next.js фронтенд-приложение
│   ├── package.json          # Зависимости Node.js и скрипты
│   ├── next.config.js        # Конфигурация Next.js
│   ├── package-lock.json
│   ├── postcss.config.js
│   ├── tailwind.config.js
│   ├── .env.local            # Переменные окружения (NEXT_PUBLIC_API_URL)
│   ├── pages/                # Страницы Next.js
│   │   ├── _app.js           # Главный компонент приложения
│   │   ├── index.js          # Главная страница со списком подарков
│   │   └── api/
│   │       └── gifts.js      # Прокси-роут для API (опционально)
│   ├── components/           # React компоненты
│   │   └── GiftList.js       # Компонент списка подарков (логика и UI)
│   └── styles/               # Стили
│       └── globals.css       # Глобальные CSS стили (Tailwind)
│
└── README.md                 # Эта инструкция
</pre>

## Настройка базы данных
sudo -u postgres psql

CREATE DATABASE giftdb;
CREATE USER giftuser WITH PASSWORD 'giftpassword';
GRANT ALL PRIVILEGES ON DATABASE giftdb TO giftuser;

\q

## Запуск backend
cd backend

python3 -m venv venv
source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt

echo "DATABASE_URL=postgresql://giftuser:giftpassword@localhost:5432/giftdb" > .env
echo "FLASK_ENV=development" >> .env

python app.py

## Запуск Frontend
cd frontend

npm install

echo "NEXT_PUBLIC_API_URL=http://localhost:5000/api" > .env.local

npm run dev

## Запуск Docker Compose
docker compose up -d --build

## Остановка Docker Compose
docker compose down
