import logging
import sqlite3
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext # type: ignore
from aiogram.fsm.state import State, StatesGroup
from aiogram import F
from buttonss import admin_panel_keyboard, KANALLAR, Chanel_id  # Import the keyboard function

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

API_TOKEN = '7611825728:AAGrxVMKmU6TVVtASv_TCDweVvM7sHjyRr0'  # Replace with your actual token
ADMIN_ID = ['6678521239', "860717486",]  # Replace with your actual admin ID

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




from aiogram.types import CallbackQuery

# Function to check user subscription
async def check_subscription(user_id: int, bot: Bot) -> bool:
    for channel in Chanel_id:
        try:
            user_status = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if user_status.status == 'left':
                return False
        except Exception as e:
            # Handle case where bot can't check subscription (e.g., if channel is private)
            print(f"Error checking subscription for user {user_id} in {channel}: {e}")
            return False
    return True

# Command handler for "/start"
@dp.message(Command("start"))
async def start_command(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    # Check user subscription
    is_subscribed = await check_subscription(user_id, bot)
    if not is_subscribed:
        # If not subscribed, ask to subscribe
        await message.answer(
            "<b>🎬 Siz botdan foydalanish uchun quyidagi kanallarga obuna bo'lishingiz kerak:</b>",
            reply_markup=KANALLAR,  # Show your subscription inline keyboard
            parse_mode="HTML"
        )
    else:
        # If subscribed, add user to the database
        add_user(user_id, username, first_name, last_name)
        await message.answer("<b>🎬 Qaysi Kino yoki Musiqa ko'rmoqchisiz? (Kod raqamli bo'lishi kerak).</b>", parse_mode="HTML")

# Callback query handler    for the confirmation button
@dp.callback_query(lambda callback_query: callback_query.data == 'tasdiqlash')
async def confirm_subscription(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    is_subscribed = await check_subscription(user_id, bot)
    
    if not is_subscribed:
        await callback_query.message.answer(
            "<b>🎬 Siz hali ham obuna bo'lmagan ko'rinasiz. Iltimos, quyidagi kanallarga obuna bo'ling:</b>",
            reply_markup=KANALLAR,  # Show subscription inline keyboard again
            parse_mode="HTML"
        )
    else:
        # User is subscribed, handle the next action (e.g., show movie/music options)
        await callback_query.message.answer("<b>🎬 Qaysi Kino yoki Musiqa ko'rmoqchisiz? (Kod raqamli bo'lishi kerak).</b>", parse_mode="HTML")


# Admin panel command handler
@dp.message(Command("admin_panel") )
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
                             f"📊  @Xarxiluz_bot statistikasi</b>", parse_mode="HTML")
    else:
        await message.answer("<b>❌ Sizda ushbu buyruqni bajarish huquqi yo'q.</b>", parse_mode="HTML")



# Function to add a movie
@dp.message(F.text == "Kino qo'shish")
async def add_movie(message: types.Message, state: FSMContext):
    if is_admin(message.from_user.id):
        await message.answer("<b>🔢 Kino kodini kiriting (raqamli bo'lishi kerak):</b>",parse_mode="HTML" )
        await state.set_state(AddMovieState.code)
    else:
        await message.answer("<b>❌ Sizda ushbu buyruqni bajarish huquqi yo'q.</b>", parse_mode="HTML")

# Handling input for movie code (now allows duplicates)
@dp.message(AddMovieState.code)
async def movie_code(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(code=message.text)
        await message.answer("<b>🎬 Kino nomini kiriting:</b>", parse_mode="HTML")
        await state.set_state(AddMovieState.title)
    else:
        await message.answer("<b>⚠️ Iltimos, to'g'ri raqamli kodni kiriting.</b>",parse_mode="HTML")

@dp.message(AddMovieState.title)
async def movie_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("<b>📝 Kino ta'rifini kiriting:</b>", parse_mode="HTML")
    await state.set_state(AddMovieState.description)

@dp.message(AddMovieState.description)
async def movie_description(message: types.Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("<b>🔗 Kino URL manzilini kiriting:</b>", parse_mode="HTML")
    await state.set_state(AddMovieState.url)

import re

# Regular expression to check for a valid URL
URL_REGEX = r'^(https?:\/\/)?(www\.)?([a-zA-Z0-9_-]+)+\.[a-zA-Z]{2,}(:\d+)?(\/\S*)?$'

@dp.message(AddMovieState.url)
async def movie_url(message: types.Message, state: FSMContext):
    url = message.text

    # Check if the provided URL matches the regular expression
    if not re.match(URL_REGEX, url):
        await message.answer("<b>⚠️ Iltimos, to'g'ri URL manzilini kiriting.</b>", parse_mode="HTML")
        return

    # Continue if the URL is valid
    user_data = await state.get_data()
    code = user_data['code']
    title = user_data['title']
    description = user_data['description']

    try:
        cursor.execute('INSERT INTO movies (code, title, description, url) VALUES (?, ?, ?, ?)', (code, title, description, url))
        conn.commit()
        await message.answer(f"<b>✅ Kino muvaffaqiyatli qo'shildi: {title} (Kino kodi: {code})</b>", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Xato: {e}")

    await state.clear()






# Function to list all movies
@dp.message(F.text == "Kino ro'yxatini ko'rish")
async def list_movies(message: types.Message):
    if is_admin(message.from_user.id):
        cursor.execute('SELECT code, title, created_at FROM movies')
        movies = cursor.fetchall()
        
        if movies:
            movie_list = "\n".join([f"➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n<b>Kino kodi:</b> #{code}\n<b>Kino nomi:</b> {title}\n<b>Qo'shilgan sana:</b> {created_at}\n" for code, title, created_at in movies])
            await message.answer(f"<b>📽️Barcha Kinolar</b>:\n{movie_list}",parse_mode="HTML" )

        else:
            await message.answer("<b>🚫 Hech qanday Kino topilmadi.</b>", parse_mode="HTML")
    else:
        await message.answer("<b>❌ Sizda bu amalni bajarish huquqi yo'q.</b>", parse_mode="HTML")


# Function to delete a movie
@dp.message(F.text == "Kino o'chirish")
async def delete_movie(message: types.Message, state: FSMContext):
    if is_admin(message.from_user.id):
        await message.answer("<b>🗑️ O'chirish uchun Kino kodini kiriting (raqamli bo'lishi kerak):</b>", parse_mode="HTML")
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
            await message.answer(f"<b>✅ Kino kodi #{code} muvaffaqiyatli o'chirildi.</b>", parse_mode="HTML")
        else:
            await message.answer("<b>🚫 Bunday Kino kodi mavjud emas.</b>",parse_mode="HTML")
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

@dp.message(F.text == "Kino ma'lumotlarini yangilash")
async def update_movie(message: types.Message, state: FSMContext):
    if is_admin(message.from_user.id):
        await message.answer("<b>✏️ Yangilash uchun Kino kodini kiriting (raqamli bo'lishi kerak):</b>", parse_mode="HTML")
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
            await message.answer("<b>🚫 Bunday Kino kodi mavjud emas.</b>", parse_mode="HTML")
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
    await message.answer(f"<b>✅ Kino kodi #{code} muvaffaqiyatli yangilandi.</b>", parse_mode="HTML")
    await state.clear()











# Connect to SQLite3 database for music
music_conn = sqlite3.connect('music.db')
music_cursor = music_conn.cursor()

# Create music table
music_cursor.execute('''
CREATE TABLE IF NOT EXISTS music (
    music_id INTEGER PRIMARY KEY AUTOINCREMENT,
    code INTEGER,
    title TEXT,
    artist TEXT,
    url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')
music_conn.commit()



# Function to add a user to users.db with start time
def add_user(user_id, username, first_name, last_name):
    try:
        users_cursor.execute('INSERT OR IGNORE INTO users (user_id, username, first_name, last_name, start_time) VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)', 
                             (user_id, username, first_name, last_name))
        users_conn.commit()
    except Exception as e:
        logging.error(f"Error adding user: {e}")




# FSM States
class AddMusicState(StatesGroup):
    code = State()
    title = State()
    artist = State()
    url = State()

class DeleteMusicState(StatesGroup):
    code = State()

class UpdateMusicState(StatesGroup):
    code = State()
    title = State()
    artist = State()
    url = State()



# Function to add a music track
@dp.message(F.text == "Musiqa qo'shish")
async def add_music(message: types.Message, state: FSMContext):
    if is_admin(message.from_user.id):
        await message.answer("<b>🔢 Musiqa kodini kiriting (raqamli bo'lishi kerak):</b>", parse_mode="HTML")
        await state.set_state(AddMusicState.code)
    else:
        await message.answer("<b>❌ Sizda ushbu buyruqni bajarish huquqi yo'q.</b>", parse_mode="HTML")


# Handling input for music code (now allows duplicates)
@dp.message(AddMusicState.code)
async def music_code(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(code=message.text)
        await message.answer("<b>🎵 Musiqa nomini kiriting:</b>", parse_mode="HTML")
        await state.set_state(AddMusicState.title)
    else:
        await message.answer("<b>⚠️ Iltimos, to'g'ri raqamli kodni kiriting.</b>", parse_mode="HTML")


@dp.message(AddMusicState.title)
async def music_title(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("<b>🎤 Musiqachi nomini kiriting:</b>", parse_mode="HTML")
    await state.set_state(AddMusicState.artist)


@dp.message(AddMusicState.artist)
async def music_artist(message: types.Message, state: FSMContext):
    await state.update_data(artist=message.text)
    await message.answer("<b>🔗 Musiqa URL manzilini kiriting:</b>", parse_mode="HTML")
    await state.set_state(AddMusicState.url)


import re

# Regular expression to check for a valid URL
URL_REGEX = r'^(https?:\/\/)?(www\.)?([a-zA-Z0-9_-]+)+\.[a-zA-Z]{2,}(:\d+)?(\/\S*)?$'

@dp.message(AddMusicState.url)
async def music_url(message: types.Message, state: FSMContext):
    url = message.text

    # Validate the URL
    if not re.match(URL_REGEX, url):
        await message.answer("<b>⚠️ Iltimos, to'g'ri URL manzilini kiriting.</b>", parse_mode="HTML")
        return

    # Proceed if the URL is valid
    user_data = await state.get_data()
    code = user_data['code']
    title = user_data['title']
    artist = user_data['artist']

    try:
        music_cursor.execute('INSERT INTO music (code, title, artist, url) VALUES (?, ?, ?, ?)', (code, title, artist, url))
        music_conn.commit()
        await message.answer(f"<b>✅ Musiqa muvaffaqiyatli qo'shildi: {title} (Musiqa kodi: {code})</b>", parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Xato: {e}")

    await state.clear()





# Function to list all music tracks
@dp.message(F.text == "Musiqa ro'yxatini ko'rish")
async def list_music(message: types.Message):
    if is_admin(message.from_user.id):
        music_cursor.execute('SELECT code, title, artist, created_at FROM music')
        tracks = music_cursor.fetchall()

        if tracks:
            music_list = "\n".join([f"➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖➖\n<b>Musiqa kodi:</b> #{code}\n<b>Musiqa nomi:</b> {title}\n<b>Musiqachi:</b> {artist}\n<b>Qo'shilgan sana:</b> {created_at}\n" for code, title, artist, created_at in tracks])
            await message.answer(f"<b>🎶 Barcha Musiqa</b>:\n{music_list}", parse_mode="HTML")

        else:
            await message.answer("<b>🚫 Hech qanday Musiqa topilmadi.</b>", parse_mode="HTML")
    else:
        await message.answer("<b>❌ Sizda bu amalni bajarish huquqi yo'q.</b>", parse_mode="HTML")


# Function to delete a music track
@dp.message(F.text == "Musiqa o'chirish")
async def delete_music(message: types.Message, state: FSMContext):
    if is_admin(message.from_user.id):
        await message.answer("<b>🗑️ O'chirish uchun Musiqa kodini kiriting (raqamli bo'lishi kerak):</b>", parse_mode="HTML")
        await state.set_state(DeleteMusicState.code)
    else:
        await message.answer("<b>❌ Sizda bu amalni bajarish huquqi yo'q.</b>", parse_mode="HTML")


@dp.message(DeleteMusicState.code)
async def confirm_delete(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        code = message.text
        music_cursor.execute('DELETE FROM music WHERE code = ?', (code,))
        music_conn.commit()

        if music_cursor.rowcount > 0:
            await message.answer(f"<b>✅ Musiqa kodi #{code} muvaffaqiyatli o'chirildi.</b>", parse_mode="HTML")
        else:
            await message.answer("<b>🚫 Bunday Musiqa kodi mavjud emas.</b>", parse_mode="HTML")
    else:
        await message.answer("<b>⚠️ Iltimos, to'g'ri raqamli kodni kiriting.</b>", parse_mode="HTML")

    await state.clear()


# Function to update a music track
@dp.message(F.text == "Musiqa ma'lumotlarini yangilash")
async def update_music(message: types.Message, state: FSMContext):
    if is_admin(message.from_user.id):
        await message.answer("<b>🔍 Yangilanish uchun Musiqa kodini kiriting:</b>", parse_mode="HTML")
        await state.set_state(UpdateMusicState.code)
    else:
        await message.answer("<b>❌ Sizda bu amalni bajarish huquqi yo'q.</b>", parse_mode="HTML")


@dp.message(UpdateMusicState.code)
async def ask_update_details(message: types.Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(code=message.text)
        await message.answer("<b>🎵 Yangilash uchun yangi Musiqa nomini kiriting:</b>", parse_mode="HTML")
        await state.set_state(UpdateMusicState.title)
    else:
        await message.answer("<b>⚠️ Iltimos, to'g'ri raqamli kodni kiriting.</b>", parse_mode="HTML")


@dp.message(UpdateMusicState.title)
async def update_music_artist(message: types.Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("<b>🎤 Yangilash uchun yangi Musiqachi nomini kiriting:</b>", parse_mode="HTML")
    await state.set_state(UpdateMusicState.artist)


@dp.message(UpdateMusicState.artist)
async def update_music_url(message: types.Message, state: FSMContext):
    await state.update_data(artist=message.text)
    await message.answer("<b>🔗 Yangilash uchun yangi Musiqa URL manzilini kiriting:</b>", parse_mode="HTML")
    await state.set_state(UpdateMusicState.url)


@dp.message(UpdateMusicState.url)
async def update_music_confirm(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    code = user_data['code']
    title = user_data['title']
    artist = user_data['artist']
    url = message.text

    # Update music details in the database
    music_cursor.execute('UPDATE music SET title = ?, artist = ?, url = ? WHERE code = ?', (title, artist, url, code))
    music_conn.commit()

    # Check if the update was successful
    if music_cursor.rowcount > 0:
        await message.answer(f"<b>✅ Musiqa kodi #{code} muvaffaqiyatli yangilandi.</b>", parse_mode="HTML")
    else:
        await message.answer("<b>🚫 Bunday Musiqa kodi mavjud emas.</b>", parse_mode="HTML")

    # Clear the state after the operation is complete
    await state.clear()  # This replaces 'finish()'











from aiogram import types


import requests

@dp.message(F.text.func(lambda text: text.isdigit()))
async def get_content_by_code(message: types.Message):
    code = message.text
    
    # Search for Movies with the same code
    cursor.execute('SELECT title, description, url FROM movies WHERE code = ?', (code,))
    movies = cursor.fetchall()

    # Search for Music with the same code
    music_cursor.execute('SELECT title, artist, url FROM music WHERE code = ?', (code,))
    music_tracks = music_cursor.fetchall()

    # Send all matching movies
    if movies:
        for movie in movies:
            title, description, url = movie
            caption_text = f"<b>Kino kodi:</b> #{code}\n\n<b>Kino nomi:</b> {title}\n\n<b>Ta'rifi:</b> {description}"
            
            # Check if the URL is accessible
            response = requests.head(url)
            if response.status_code == 200:
                try:
                    await bot.send_video(message.chat.id, video=url, caption=caption_text, parse_mode="HTML")
                except Exception as e:
                    await message.answer(f"❌ Kino yuborishda xato: {e}")
            else:
                await message.answer("<b>🚫 Kino URL manziliga ulanishda xato yoki noto'g'ri URL.</b>", parse_mode="HTML")

    # Send all matching music tracks
    if music_tracks:
        for music in music_tracks:
            title, artist, url = music
            caption_text = f"<b>Musiqa kodi:</b> #{code}\n\n<b>Musiqa nomi:</b> {title}\n\n<b>Musiqachi:</b> {artist}"
            
            # Check if the URL is accessible
            response = requests.head(url)
            if response.status_code == 200:
                try:
                    await bot.send_audio(message.chat.id, audio=url, caption=caption_text, parse_mode="HTML")
                except Exception as e:
                    await message.answer(f"❌ Musiqa yuborishda xato: {e}")
            else:
                await message.answer("<b>🚫 Musiqa URL manziliga ulanishda xato yoki noto'g'ri URL.</b>", parse_mode="HTML")

    # If no movie or music is found
    if not movies and not music_tracks:
        await message.answer("<b>🚫 Bunday Kino yoki Musiqa kodi mavjud emas.</b>", parse_mode="HTML")





if __name__ == '__main__':
    dp.run_polling(bot)
