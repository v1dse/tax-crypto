from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime
import os
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

app = FastAPI(title="CryptoTax API")

# ================================
# НАСТРОЙКИ EMAIL (из переменных окружения)
# ================================
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "recipient@example.com")

# CORS
allowed_origins = os.getenv("ALLOWED_ORIGINS", "tax-crypto.netlify.app").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def send_email_with_attachments(
    name: str,
    email: str,
    tax_type: str,
    year: str,
    exchanges: str,
    dex: str,
    wallets: str,
    operations: str,
    files: List[UploadFile]
):
    """Отправка email с вложениями"""
    
    # Создаем письмо
    message = MIMEMultipart()
    message["From"] = SMTP_USERNAME
    message["To"] = RECIPIENT_EMAIL
    message["Subject"] = f"🔔 Новая заявка от {name}"
    
    # Тело письма
    body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; padding: 20px; background-color: #f5f5f5;">
        <div style="max-width: 600px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);">
            <h1 style="color: #7c3aed; border-bottom: 3px solid #7c3aed; padding-bottom: 10px;">
                📊 Новая заявка на разлечение криптовалютных налогов
            </h1>
            
            <div style="margin: 20px 0;">
                <h3 style="color: #333;">👤 Информация о клиенте:</h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr style="background: #f9f9f9;">
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Имя:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{name}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Email:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{email}</td>
                    </tr>
                    <tr style="background: #f9f9f9;">
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Тип:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{tax_type}</td>
                    </tr>
                    <tr>
                        <td style="padding: 10px; border: 1px solid #ddd;"><strong>Год:</strong></td>
                        <td style="padding: 10px; border: 1px solid #ddd;">{year}</td>
                    </tr>
                </table>
            </div>
            
            <div style="margin: 20px 0;">
                <h3 style="color: #333;">🏦 Платформы:</h3>
                <p><strong>Биржи (CEX):</strong> {exchanges or 'Не указано'}</p>
                <p><strong>DEX:</strong> {dex or 'Не указано'}</p>
                <p><strong>Кошельки:</strong> {wallets or 'Не указано'}</p>
            </div>
            
            <div style="margin: 20px 0;">
                <h3 style="color: #333;">💼 Операции:</h3>
                <p>{operations or 'Не указано'}</p>
            </div>
            
            <div style="margin: 20px 0;">
                <h3 style="color: #333;">📎 Файлы:</h3>
                <p>Прикреплено файлов: <strong>{len(files)}</strong></p>
            </div>
            
            <div style="margin-top: 30px; padding-top: 20px; border-top: 2px solid #eee; color: #666; font-size: 12px;">
                <p>⏰ Дата отправки: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</p>
                <p>🤖 Отправлено автоматически через CryptoTax.pl</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    message.attach(MIMEText(body, "html"))
    
    # Прикрепляем файлы
    for file in files:
        file_content = await file.read()
        
        part = MIMEBase("application", "octet-stream")
        part.set_payload(file_content)
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {file.filename}",
        )
        message.attach(part)
        
        # Сбрасываем указатель файла
        await file.seek(0)
    
    # Отправляем письмо
    try:
        await aiosmtplib.send(
            message,
            hostname=SMTP_SERVER,
            port=SMTP_PORT,
            username=SMTP_USERNAME,
            password=SMTP_PASSWORD,
            start_tls=True,
        )
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to send email: {str(e)}")


@app.get("/")
async def root():
    """Проверка работы API"""
    return {
        "status": "ok",
        "message": "CryptoTax API is running!",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/submit-form")
async def submit_form(
    name: str = Form(...),
    email: str = Form(...),
    type: str = Form(...),
    year: str = Form(...),
    exchanges: Optional[str] = Form(""),
    dex: Optional[str] = Form(""),
    wallets: Optional[str] = Form(""),
    operations: Optional[str] = Form(""),
    files: List[UploadFile] = File(default=[])
):
    """
    Прием данных формы и отправка на email
    """
    
    try:
        # Отправляем email
        await send_email_with_attachments(
            name=name,
            email=email,
            tax_type=type,
            year=year,
            exchanges=exchanges,
            dex=dex,
            wallets=wallets,
            operations=operations,
            files=files
        )
        
        return {
            "status": "success",
            "message": "Форма успешно отправлена!",
            "data": {
                "name": name,
                "email": email,
                "files_count": len(files)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка при обработке формы: {str(e)}"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)