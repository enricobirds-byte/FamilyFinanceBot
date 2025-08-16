import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

# Полный путь до JSON с ключом сервисного аккаунта
CREDENTIALS_FILE = "/Users/johndoe/Documents/FamilyFinanceBot/credentials.json"

# Области доступа
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

try:
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    # Попробуем вывести список всех таблиц, доступных аккаунту
    spreadsheets = client.openall()
    print("✅ Доступ к таблицам есть! Вот что видит аккаунт:")
    for s in spreadsheets:
        print(f"- {s.title}")
except Exception as e:
    print("❌ Ошибка при подключении к Google Sheets:")
    print(e)