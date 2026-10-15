import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✈️ Aviator Stats Bot\n\n"
        "Comandos disponibles:\n"
        "/registrar 1.50 - registrar un multiplicador\n"
        "/ultimos - ver los últimos registros\n"
        "/resumen - ver estadísticas descriptivas\n\n"
        "Los resultados pasados no predicen los futuros."
    )

async def registrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Uso: /registrar 1.50")
        return
    try:
        valor = float(context.args[0].replace(",", "."))
        if not 1 <= valor <= 100000:
            raise ValueError()
    except ValueError:
        await update.message.reply_text("Introduce un multiplicador válido, por ejemplo /registrar 1.50")
        return

    registros = context.application.bot_data.setdefault("registros", [])
    registros.append(valor)
    registros[:] = registros[-100:]
    await update.message.reply_text(f"Registrado: {valor:.2f}x")

async def ultimos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    registros = context.application.bot_data.get("registros", [])
    if not registros:
        await update.message.reply_text("Todavía no hay registros. Usa /registrar 1.50")
        return
    texto = "\n".join(f"{i}. {v:.2f}x" for i, v in enumerate(registros[-10:][::-1], 1))
    await update.message.reply_text("Últimos registros:\n" + texto)

async def resumen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    registros = context.application.bot_data.get("registros", [])
    if not registros:
        await update.message.reply_text("Todavía no hay datos para resumir.")
        return
    bajos = sum(v < 2 for v in registros)
    await update.message.reply_text(
        f"Registros: {len(registros)}\n"
        f"Promedio histórico: {sum(registros)/len(registros):.2f}x\n"
        f"Menores de 2x: {bajos} ({bajos/len(registros)*100:.1f}%)\n"
        "Esto describe registros ingresados; no predice la próxima ronda."
    )

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("registrar", registrar))
app.add_handler(CommandHandler("ultimos", ultimos))
app.add_handler(CommandHandler("resumen", resumen))

if __name__ == "__main__":
    if not TOKEN:
        raise RuntimeError("Falta la variable TELEGRAM_BOT_TOKEN")
    app.run_polling()
