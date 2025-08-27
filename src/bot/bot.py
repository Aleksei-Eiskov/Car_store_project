import os, asyncio, re
import httpx
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

API_URL = os.environ.get("API_URL", "http://localhost:8000")
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")

HELP = (
    "Команды:\n"
    "/health - статус API\n"
    "/brands - бренды\n"
    "/cars [параметры] - список, напр.: /cars q=tesla max_price=50000\n"
    "/car <id> - карточка по id\n"
)

def format_car(car: dict) -> str:
    return f"#{car['id']} - {car['name']} - {car['price']} € - brand_id {car.get('brand_id')}"

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет. Я демонстрационный бот для Car_store. " + HELP)

async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HELP)

async def cmd_health(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API_URL}/health", timeout=10)
        await update.message.reply_text(str(r.json()))

async def cmd_brands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API_URL}/brands", timeout=10)
        brands = r.json()
        if not brands:
            await update.message.reply_text("Брендов нет")
            return
        text = "\n".join([f"#{b['id']} - {b['name']}" for b in brands])
        await update.message.reply_text(text)

def parse_params(args):
    params = {}
    for a in args:
        if "=" in a:
            k, v = a.split("=", 1)
            params[k] = v
    return params

async def cmd_cars(update: Update, context: ContextTypes.DEFAULT_TYPE):
    params = parse_params(context.args)
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API_URL}/cars", params=params, timeout=10)
        cars = r.json()
        if not cars:
            await update.message.reply_text("Машин нет по заданным параметрам")
            return
        text = "\n".join([format_car(c) for c in cars[:20]])
        await update.message.reply_text(text)

async def cmd_car(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Нужно указать id, пример: /car 1")
        return
    car_id = context.args[0]
    if not re.fullmatch(r"\d+", car_id):
        await update.message.reply_text("id должен быть числом")
        return
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{API_URL}/cars/{car_id}", timeout=10)
        if r.status_code == 404:
            await update.message.reply_text("Не найдено")
            return
        car = r.json()
        await update.message.reply_text(format_car(car))

async def main():
    if not TELEGRAM_TOKEN:
        raise RuntimeError("TELEGRAM_TOKEN не установлен. Укажите в .env или переменных окружения.")
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("health", cmd_health))
    app.add_handler(CommandHandler("brands", cmd_brands))
    app.add_handler(CommandHandler("cars", cmd_cars))
    app.add_handler(CommandHandler("car", cmd_car))
    await app.initialize()
    await app.start()
    try:
        await asyncio.Event().wait()
    finally:
        await app.stop()
        await app.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
