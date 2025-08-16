import os
from dotenv import load_dotenv
import json
import tempfile
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# -----------------------------
# 1. Загружаем переменные из .env
# -----------------------------
load_dotenv()

def ensure_credentials_file():
    value = os.getenv("GOOGLE_CREDENTIALS_JSON", "").strip()
    if not value:
        raise ValueError("GOOGLE_CREDENTIALS_JSON пуст. Укажи путь к файлу или вставь JSON-ключ целиком в переменную.")
    if os.path.isfile(value):
        return value
    if value.startswith("{"):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        tmp.write(value.encode("utf-8"))
        tmp.flush()
        return tmp.name
    raise ValueError("GOOGLE_CREDENTIALS_JSON не похож ни на путь к файлу, ни на JSON.")

TOKEN = os.getenv("TELEGRAM_TOKEN")
CREDENTIALS_FILE = ensure_credentials_file()
SPREADSHEET_NAME = os.getenv("SPREADSHEET_NAME")

if not TOKEN or not CREDENTIALS_FILE or not SPREADSHEET_NAME:
    print("❌ Проверьте .env: TELEGRAM_TOKEN, GOOGLE_CREDENTIALS_JSON, SPREADSHEET_NAME должны быть заполнены")
    exit(1)

# -----------------------------
# 2. Подключение к Google Sheets
# -----------------------------
try:
    scope = ["https://spreadsheets.google.com/feeds",
             "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    sheet = client.open(SPREADSHEET_NAME).sheet1
except Exception as e:
    print("❌ Не удалось получить доступ к таблице. Проверьте права доступа и client_email в Google Sheets")
    print(e)
    exit(1)

# -----------------------------
# 3. Команды бота
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот для учета доходов и расходов.\n"
        "Команды:\n"
        "/addincome <сумма> - добавить доход\n"
        "/addexpense <сумма> - добавить расход\n"
        "/balance - показать баланс"
    )

async def add_income(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(context.args[0])
        sheet.append_row(["Доход", amount])
        await update.message.reply_text(f"✅ Добавлен доход: {amount}")
    except:
        await update.message.reply_text("❌ Используй: /addincome 1000")

async def add_expense(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        amount = float(context.args[0])
        sheet.append_row(["Расход", amount])
        await update.message.reply_text(f"✅ Добавлен расход: {amount}")
    except:
        await update.message.reply_text("❌ Используй: /addexpense 500")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    records = sheet.get_all_records()
    income = sum(r['Amount'] for r in records if r['Type'] == "Доход")
    expense = sum(r['Amount'] for r in records if r['Type'] == "Расход")
    await update.message.reply_text(
        f"💰 Баланс:\nДоход: {income}\nРасход: {expense}\nИтого: {income - expense}"
    )

# -----------------------------
# 4. Запуск бота
# -----------------------------
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("addincome", add_income))
app.add_handler(CommandHandler("addexpense", add_expense))
app.add_handler(CommandHandler("balance", balance))

print("✅ Бот запущен...")
app.run_polling()