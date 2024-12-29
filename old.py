import logging 
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import sqlite3 as sq
import random
import asyncio

TOKEN = "7924804008:AAEbIaVWSJ7g64FIHZW_53ocj-d5jtqwoP4"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
db_connection = sq.connect("tasks.db")
db_cursor = db_connection.cursor()

def initialize_database():
    db_cursor.execute(
        ''' 
            CREATE TABLE IF NOT EXISTS tasks(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            status BOOLEAN DEFAULT FALSE,
            code INTERGER NOT NULL
            )
        '''
    )

    db_connection.commit()
    return ("Database initialized")

initialize_database()

def add_tasks(task_description, code):
    db_cursor.execute(
        """
            INSERT INTO tasks(description, status, code) VALUES (?, ?, ?)
        """,
        (task_description, False, code)
    )
    db_connection.commit()

    return ("Tasks have been added")

def delete_task(task_description, code):
    db_cursor.execute(
        """
        DELETE FROM tasks WHERE code = ?
        """,
        (code,)
    )
    db_connection.commit()

    return "tasks has been deleted successfully"

def list_taskDB():
    db_cursor.execute('SELECT id, description, status, code FROM tasks')
    return db_cursor.fetchall()

def close_database_connection():
    db_connection.close()
    print("Database connection closed.")


# Command to add a task
async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task_description = ' '.join(context.args)  # Get task description from command arguments
    if task_description:
        add_tasks(task_description, random.randint(1000, 10000))
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Task added: {task_description}")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Please provide a task description. Usage: /add <task>")

# Command to list tasks
async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks = list_taskDB()
    if tasks:
        task_list = "\n".join(f"{i+1}. {task[1]}" for i, task in enumerate(tasks))  # Task[1] is description
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Tasks:\n{task_list}")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No tasks yet!")

async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Shutting down...")
    close_database_connection()
    # Optionally, stop the application after cleaning up
    await context.application.stop()

# Initialize the bot
async def main(TOKEN):
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("add", add_task))
    application.add_handler(CommandHandler("list", list_tasks))
    application.add_handler(CommandHandler("shutdown", shutdown))

    # Start the bot
    await application.run_polling()

if __name__ == "__main__":
    
    if not asyncio.get_event_loop().is_running():
        asyncio.run(main(TOKEN))
    else:
        # This ensures it runs correctly in interactive environments
        loop = asyncio.get_event_loop()
        loop.create_task(main(TOKEN))