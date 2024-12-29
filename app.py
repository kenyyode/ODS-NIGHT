import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import sqlite3 as sq
import random
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("Token")

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

def update_tasks_done(id):
    db_cursor.execute(
        """
        UPDATE tasks 
        SET status = True
        WHERE id = ?;

        """,
        (id,)

    )
    db_connection.commit()
    return "tasks status update successfully"


def delete_task(id):
    db_cursor.execute(
        """
        DELETE FROM tasks WHERE id = ?
        """,
        (id,)
    )
    db_connection.commit()

    return "tasks has been deleted successfully"

def list_taskDB():
    db_cursor.execute('''

        SELECT id, description, 
                      CASE 
                      WHEN status = 0 THEN "Pending"
                      WHEN status = 1 THEN "Done"
                      END AS status, code FROM tasks
            '''
                      )
    return db_cursor.fetchall()

async def start(update, context):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="welcome to my bot")

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
        task_list = "\n".join(f"{i+1}. {task[1]} | Status: {task[2]} ID: {task[0]}" for i, task in enumerate(tasks))  # Task[1] is description
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Tasks:\n{task_list}")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="No tasks yet!")

async def delete_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    task_todelete = context.args[0]
    delete_task(task_todelete)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Task deleted")

async def update_task(update: Update, context: ContextTypes.DEFAULT_TYPE): 
    task_to_update = context.args[0]
    update_tasks_done(task_to_update)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Task update sucessful")

# Initialize the bot
async def main(TOKEN):
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("add", add_task))
    application.add_handler(CommandHandler("list", list_tasks))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler('delete', delete_tasks))
    application.add_handler(CommandHandler("done", update_task))

    # Start the bot
    await application.run_polling()

if __name__ == "__main__":
    import nest_asyncio
    import asyncio

    nest_asyncio.apply()  # Allow nested event loops

    try:
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main(TOKEN))
    except Exception as e:
        print(f"An error occurred: {e}")




