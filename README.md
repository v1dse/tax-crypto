# CryptoTax API

API для обработки и отправки налоговых данных криптовалютных операций.

## Требования

- Python 3.8+
- FastAPI
- Uvicorn

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/v1dse/tax-crypto.git
cd tax-crypto
```

2. Создайте виртуальное окружение:
```bash
python -m venv venv
source venv/bin/activate  # На Windows: venv\Scripts\activate
```

3. Установите зависимости:
```bash
pip install -r requirements.txt
```

4. Создайте файл `.env` на основе `.env.example`:
```bash
cp .env.example .env
```

5. Заполните файл `.env` вашими учетными данными:
```
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
RECIPIENT_EMAIL=recipient@example.com
```

## Запуск

```bash
python main.py
```

Или через uvicorn:
```bash
uvicorn main:app --reload
```

API будет доступен на `http://localhost:8000`

## API Endpoints

- `GET /` - Проверка статуса API
- `POST /submit-form` - Отправка формы с файлами
- `GET /health` - Health check

## Документация

Интерактивная документация доступна на `http://localhost:8000/docs`

## Безопасность

⚠️ **Важно:** Не коммитьте файл `.env` с реальными учетными данными. Используйте `.env.example` как шаблон.

## Лицензия

MIT
