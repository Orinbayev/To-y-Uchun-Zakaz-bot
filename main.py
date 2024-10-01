import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import F
from buttonnnn import admin_panel_keyboard  # Import the keyboard function

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

API_TOKEN = '7963630518:AAGmNEANYJsrHvA9A96DlXKB8LR_vXtChPU'  # Replace with your actual token
ADMIN_ID = ['6678521239', "7236785651", '6512709243']  # Replace with your actual admin ID

# Bot and dispatcher creation
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Connect to SQLite3 database
conn = sqlite3.connect('movies.db')
cursor = conn.cursor()

# Create movie table
# Create movie table with 'created_at' column
cursor.execute('''
CREATE TABLE IF NOT EXISTS movies (
    movie_id INTEGER PRIMARY KEY AUTOINCREMENT,
    code INTEGER,
    title TEXT,
    description TEXT,
    url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
conn.commit()


users_conn = sqlite3.connect('users.db')  # Create or connect to users.db
users_cursor = users_conn.cursor()

# Create users table
# Foydalanuvchilar jadvalini yaratish
users_cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
users_conn.commit()


from datetime import datetime, timedelta


# Function to add a user to users.db with start time
def add_user(user_id, username, first_name, last_name):
    try:
        users_cursor.execute('INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, start_time) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)', 
                             (user_id, username, first_name, last_name))
        users_conn.commit()
    except Exception as e:
        logging.error(f"Error adding user: {e}")


def get_total_user_count():
    users_cursor.execute('SELECT COUNT(*) FROM users')
    return users_cursor.fetchone()[0]


# Function to get user count in the last 24 hours
def get_user_count_last_24_hours():
    time_threshold = datetime.now() - timedelta(hours=24)
    users_cursor.execute('SELECT COUNT(*) FROM users WHERE start_time >= ?', (time_threshold,))
    return users_cursor.fetchone()[0]

# Function to get user count in the last month
def get_user_count_last_month():
    time_threshold = datetime.now() - timedelta(days=30)
    users_cursor.execute('SELECT COUNT(*) FROM users WHERE start_time >= ?', (time_threshold,))
    return users_cursor.fetchone()[0]



# FSM States
class AddMovieState(StatesGroup):
    code = State()
    title = State()
    description = State()
    url = State()

class DeleteMovieState(StatesGroup):
    code = State()

class UpdateMovieState(StatesGroup):
    code = State()
    title = State()
    description = State()
    url = State()


def is_admin(user_id: int) -> bool:
    return str(user_id) in ADMIN_ID



# Admin panel command handler
@dp.message(Command("admin_panel"))
async def admin_panel(message: types.Message):
    if is_admin(message.from_user.id):
        keyboard = admin_panel_keyboard()  # Get the keyboard from the imported function
        await message.answer("<b>🔧 Admin panel:</b>",parse_mode="HTML", reply_markup=keyboard)
    else:
        await message.answer("<b>❌ Sizda ushbu buyruqni bajarish huquqi yo'q.</b>", parse_mode="HTML")


# Command to get user count/
@dp.message(F.text=="📊 Statistika")
async def user_count(message: types.Message):
    if is_admin(message.from_user.id):
        count_total = get_total_user_count()
        count_24h = get_user_count_last_24_hours()
        count_1mo = get_user_count_last_month()
        await message.answer(f"<b>👨🏻‍💻 Aktiv obunachilar soni: {count_total}\n\n"
                             f"• Oxirgi 24 soatda — {count_24h} ta obunachi qo'shildi\n"
                             f"• Oxirgi 1 oyda — {count_1mo} ta obunachi qo'shildi\n\n"
                             f"📊  @ASR_Media_Bot statistikasi</b>", parse_mode="HTML")
    else:
        await message.answer("<b>❌ Sizda ushbu buyruqni bajarish huquqi yo'q.</b>", parse_mode="HTML")



# Function to add a movie
@dp.message(F.text == "To'y qo'shish")
async def add_movie(message: types.Message, state: FSMContext):
    if is_admin(message.from_user.id):
        await message.answer("<b>🔢 To'y kodini kiriting (raqamli bo'lishi kerak):</b>",parse_mode="HTML" )
        await state.set_state(AddMovieState.code)
    else:
        await message.answer("<b>❌ Sizda ushbu buyruqni bajarish huquqi yo'q.</b>", parse_mode="HTML")

# Handling input for movie code (now allows duplicates)
@dp.message(AddMovieState.code)
async def movie_code(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(code=message.text)
        await message.answer("<b>🎬 To'y nomini kiriting:</b>", parse_mode="HTML")
        await state.set_state(AddMovieState.title)
    else:
        await message.answer("<b>⚠️ Iltimos, to'g'ri raqamli kodni kiriting.</b>",parse_mode="HTML")

@dp.message(AddMovieState.title)
async def movie_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("<b>📝 To'y ta'rifini kiriting:</b>", parse_mode="HTML")
    await state.set_state(AddMovieState.description)

@dp.message(AddMovieState.description)
async def movie_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("<b>🔗 To'y URL manzilini kiriting:</b>", parse_mode="HTML")
    await state.set_state(AddMovieState.url)

@dp.message(AddMovieState.url)
async def movie_url(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    code = user_data['code']
    title = user_data['title']
    description = user_data['description']
    url = message.text

    try:
        cursor.execute('INSERT INTO movies (code, title, description, url) VALUES (?, ?, ?, ?)', (code, title, description, url))
        conn.commit()
        await message.answer(f"<b>✅ To'y muvaffaqiyatli qo'shildi: {title} (To'y kodi: {code})</b>", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Xato: {e}")

    await state.clear()

# Function to list all movies
@dp.message(F.text == "To'y ro'yxatini ko'rish")
async def list_movies(message: types.Message):
    if is_admin(message.from_user.id):
        cursor.execute('SELECT code, title, created_at FROM movies')
        movies = cursor.fetchall()
        
        if movies:
            movie_list = "\n".join([f"➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n<b>To'y kodi:</b> #{code}\n<b>To'y nomi:</b> {title}\n<b>Qo'shilgan sana:</b> {created_at}\n" for code, title, created_at in movies])
            await message.answer(f"<b>📽️Barcha To'ylar</b>:\n{movie_list}",parse_mode="HTML" )

        else:
            await message.answer("<b>🚫 Hech qanday To'y topilmadi.</b>", parse_mode="HTML")
    else:
        await message.answer("<b>❌ Sizda bu amalni bajarish huquqi yo'q.</b>", parse_mode="HTML")


# Function to delete a movie
@dp.message(F.text == "To'y o'chirish")
async def delete_movie(message: types.Message, state: FSMContext):
    if is_admin(message.from_user.id):
        await message.answer("<b>🗑️ O'chirish uchun To'y kodini kiriting (raqamli bo'lishi kerak):</b>", parse_mode="HTML")
        await state.set_state(DeleteMovieState.code)
    else:
        await message.answer("<b>❌ Sizda bu amalni bajarish huquqi yo'q.</b>", parse_mode="HTML")

@dp.message(DeleteMovieState.code)
async def confirm_delete(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        code = message.text
        cursor.execute('DELETE FROM movies WHERE code = ?', (code,))
        conn.commit()

        if cursor.rowcount > 0:
            await message.answer(f"<b>✅ To'y kodi #{code} muvaffaqiyatli o'chirildi.</b>", parse_mode="HTML")
        else:
            await message.answer("<b>🚫 Bunday To'y kodi mavjud emas.</b>",parse_mode="HTML")
    else:
        await message.answer("<b>⚠️ Iltimos, to'g'ri raqamli kodni kiriting.</b>", parse_mode="HTML")

    await state.clear()  # Clear state after deletion

# Function to update movie details
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import StateFilter

# 'O'tkazib yuborish' tugmasi uchun inline klaviatura
skip_button = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="O'tkazib yuborish", callback_data="skip")]
])

@dp.message(F.text == "To'y ma'lumotlarini yangilash")
async def update_movie(message: types.Message, state: FSMContext):
    if is_admin(message.from_user.id):
        await message.answer("<b>✏️ Yangilash uchun To'y kodini kiriting (raqamli bo'lishi kerak):</b>", parse_mode="HTML")
        await state.set_state(UpdateMovieState.code)
    else:
        await message.answer("<b>❌ Sizda bu amalni bajarish huquqi yo'q.</b>", parse_mode="HTML")

@dp.message(UpdateMovieState.code)
async def update_movie_code(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        code = message.text
        cursor.execute('SELECT title, description, url FROM movies WHERE code = ?', (code,))
        movie = cursor.fetchone()

        if movie:
            await state.update_data(code=code)
            await message.answer(
                f"<b>🔍 Joriy ma'lumotlar:\nNomi: {movie[0]}\nTa'rifi: {movie[1]}\nURL: {movie[2]}\n\nYangi nomini kiriting (yoki 'o'tkazib yuborish' tugmasini bosing):</b>", parse_mode="HTML",
                reply_markup=skip_button
            )
            await state.set_state(UpdateMovieState.title)
        else:
            await message.answer("<b>🚫 Bunday To'y kodi mavjud emas.</b>", parse_mode="HTML")
    else:
        await message.answer("<b>⚠️ Iltimos, to'g'ri raqamli kodni kiriting.</b>", parse_mode="HTML")

@dp.message(UpdateMovieState.title)
async def update_movie_title(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    code = user_data['code']
    new_title = message.text

    try:
        if new_title.lower() != "o'tkazib yuborish":
            cursor.execute('UPDATE movies SET title = ? WHERE code = ?', (new_title, code))
        
        await message.answer("<b>📝 Yangi ta'rifni kiriting (yoki 'o'tkazib yuborish' tugmasini bosing):</b>",parse_mode="HTML", reply_markup=skip_button)
        await state.set_state(UpdateMovieState.description)
    except Exception as e:
        await message.answer(f"<b>❌ Yangilashda xato: {e}</b>", parse_mode="HTML")

# Inline button handler with StateFilter
@dp.callback_query(StateFilter(UpdateMovieState.title), F.data == "skip")
@dp.callback_query(StateFilter(UpdateMovieState.description), F.data == "skip")
async def skip_update(call: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()

    if current_state == UpdateMovieState.title:
        await call.message.answer("<b>📝 Yangi ta'rifni kiriting (yoki 'o'tkazib yuborish' tugmasini bosing):</b>",parse_mode="HTML", reply_markup=skip_button)
        await state.set_state(UpdateMovieState.description)
    elif current_state == UpdateMovieState.description:
        await call.message.answer("<b>🔗 Yangi URL manzilini kiriting\nYoki Eski URL manzilini kiritng:</b>",parse_mode="HTML" )
        await state.set_state(UpdateMovieState.url)
    
    await call.answer()

@dp.message(UpdateMovieState.description)
async def update_movie_description(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    code = user_data['code']
    new_description = message.text

    if new_description.lower() != "o'tkazib yuborish":
        cursor.execute('UPDATE movies SET description = ? WHERE code = ?', (new_description, code))

    await message.answer("<b>🔗 Yangi URL manzilini kiriting\nYoki Eski URL manzilini kiritng:</b>", parse_mode="HTML" )
    await state.set_state(UpdateMovieState.url)

@dp.message(UpdateMovieState.url)
async def update_movie_url(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    code = user_data['code']
    new_url = message.text

    if new_url.lower() != "o'tkazib yuborish":
        cursor.execute('UPDATE movies SET url = ? WHERE code = ?', (new_url, code))

    conn.commit()
    await message.answer(f"<b>✅ To'y kodi #{code} muvaffaqiyatli yangilandi.</b>", parse_mode="HTML")
    await state.clear()

# Function to get a movie by its code
@dp.message(Command("start"))
async def start_command(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    # Foydalanuvchini ma'lumotlar bazasiga qo'shish
    add_user(user_id, username, first_name, last_name)

    await message.answer("<b>🎬 Qaysi To'y kodini ko'rmoqchisiz? Iltimos, To'y kodini kiriting (raqamli bo'lishi kerak).</b>", parse_mode="HTML")


@dp.message(F.text.func(lambda text: text.isdigit()))
async def get_movie_by_code(message: types.Message):
    code = message.text
    cursor.execute('SELECT title, description, url FROM movies WHERE code = ?', (code,))
    movies = cursor.fetchall()



    if movies:
        for movie in movies:
            title, description, url = movie
            
            caption_text = f"<b>To'y kodi:</b>  #{code}\n\n<b>To'y nomi:</b>  {title}\n\n<b>Ta'rifi:</b>  {description}"
            await bot.send_video(message.chat.id, video=url, caption=caption_text, parse_mode="HTML")
    else:
        await message.answer("<b>🚫 Bunday To'y topilmadi.</b>",parse_mode="HTML")

if __name__ == '__main__':
    dp.run_polling(bot)
