import os, re, math, time, uuid, shutil, logging
from datetime import datetime, timedelta
from urllib.parse import urlparse
import json
import aiohttp, aiofiles, requests, httpx, humanize, asyncio
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, CallbackContext, ContextTypes, filters, filters as ptb_filters
from telegram.constants import ParseMode
from telegram.ext import CallbackQueryHandler
import subprocess
import tempfile
import py7zr
import rarfile
import zipfile
import tarfile
from pathlib import Path
from collections import defaultdict
user_locks = defaultdict(asyncio.Lock)

file_session_lock = asyncio.Lock()
from pyrogram import Client, filters as pyro_filters, types
from pyrogram.types import InlineKeyboardButton as PyroInlineButton, InlineKeyboardMarkup as PyroInlineMarkup
import mimetypes

# File to store user sessions
RESTORE_USERS_FILE = "restore_users.json"

def load_restore_users():
    """Load persisted user sessions from restore_users.json."""
    if os.path.exists(RESTORE_USERS_FILE):
        try:
            with open(RESTORE_USERS_FILE, "r") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading restore_users: {e}")
            return {}
    return {}

def save_restore_users(data):
    """Save user sessions to restore_users.json."""
    try:
        with open(RESTORE_USERS_FILE, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logger.error(f"Error saving restore_users: {e}")

def restore_sessions(application):
    """Restore user sessions from restore_users.json on bot startup."""
    global sessions
    restore_data = load_restore_users()
    for user_id, user_data in restore_data.items():
        user_id = int(user_id)  # Ensure user_id is an integer
        sessions[user_id] = user_data["username"]
        # Store credentials in application.bot_data for access in handlers
        application.bot_data.setdefault('user_credentials', {})[user_id] = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        logger.info(f"Restored session for user_id: {user_id}, username: {user_data['username']}")

api_id = 5127578
api_hash = '048b23e17b56163581cefa5131b44bff'
BROADCAST_ADMIN_ID = 1074000261  # your ID
broadcast_mode = {}  # user_id -> waiting (True/False)
broadcast_last_message_id = {}  # user_id -> message_id


app = Client(
    name="my_session",
    api_id=api_id,
    api_hash=api_hash,
    bot_token="7984121127:AAGyBslNMIkUEaEd6z2NdhqHSqFIJOGElxQ"
)

# Globals
sessions = {}         # user_id -> username
login_states = {}     # user_id -> login step
file_sessions = {}    # user_id -> file data
cancel_tokens = {}    # user_id -> cancel flag
bot_start_time = time.time()
upload_tasks = {}  # user_id -> {upload_token: asyncio.Task}

################################
# Configuration and Constants
################################

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
# Conversation states
USERNAME, PASSWORD, RENAME, DOWNLOAD_LINK, MOVE_FOLDER = range(5)
CHANGING_PASSWORD, NEW_FOLDER = range(1, 3)

# Flask API URL
FLASK_API_URL = "http://192.168.1.200:5000/login"

# URL pattern for detection
URL_PATTERN = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

IST = pytz.timezone('Asia/Kolkata')

# Telegram file size limits
TELEGRAM_FILE_SIZE_LIMIT = 20 * 1024 * 1024  # 20 MB
TELEGRAM_MAX_FILE_SIZE = 1.5 * 1024 * 1024 * 1024  # 1.5 GB (Telegram's max file size)

# Download status tracking - replace existing with this
download_tasks = {}  # Tracks active download tasks
download_status = {}  # Tracks download status info
cancel_upload = {}
################################
# Helper Functions
################################

def format_size(bytes):
    """Convert bytes to human-readable format"""
    if bytes == 0:
        return "0B"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(bytes, 1024)))
    p = math.pow(1024, i)
    s = round(bytes / p, 2)
    return f"{s}{units[i]}"

def register_path(context, path):
    if 'path_map' not in context.user_data:
        context.user_data['path_map'] = {}

    # Normalize path to avoid duplicates
    normalized_path = os.path.abspath(path)
    for id_, p in context.user_data['path_map'].items():
        if os.path.abspath(p) == normalized_path:
            logger.debug(f"Path already registered: {normalized_path} with id {id_}")
            return id_

    uid = str(uuid.uuid4())[:8]
    context.user_data['path_map'][uid] = normalized_path
    logger.debug(f"Registered path: {normalized_path} with id {uid}")
    return uid

def list_directory_contents(path, context):
    buttons = []
    try:
        items = os.listdir(path)
        items.sort()
        for item in items:
            full_path = os.path.join(path, item)
            uid = register_path(context, full_path)
            if os.path.isdir(full_path):
                buttons.append([InlineKeyboardButton(f"📁 {item}", callback_data=f"open|{uid}")])
            else:
                buttons.append([InlineKeyboardButton(f"💾 {item}", callback_data=f"file|{uid}")])
        logger.debug(f"Listed directory contents for {path}: {items}")
    except Exception as e:
        logger.error(f"Error reading folder {path}: {e}")
    return buttons


def format_speed(bytes_per_sec):
    """Convert bytes per second to human-readable format"""
    return format_size(bytes_per_sec) + "/s"

def format_time(seconds):
    """Convert seconds to human-readable time format"""
    return str(timedelta(seconds=int(seconds)))

async def update_download_progress(update: Update, context: CallbackContext, message_id: int, 
                                 downloaded: int, total: int, speed: float, start_time: float,
                                 download_id: str = None, filename: str = "unknown"):
    """Update the progress message for downloads or uploads"""
    percent = (downloaded / total) * 100 if total > 0 else 0
    elapsed = time.time() - start_time
    eta = (total - downloaded) / speed if speed > 0 else 0

    progress_bar = "[" + "=" * int(percent / 5) + ">" + " " * (20 - int(percent / 5)) + "]"

    # Determine if this is an upload or download
    action = "Uploading to Telegram" if download_id and "server_upload" in download_id else "Downloading to server"
    text = (
        f"{'⬆️' if 'Uploading' in action else '⬇️'} {action} `{filename}`\n\n"
        f"{progress_bar} {percent:.1f}%\n\n"
        f"📊 {format_size(downloaded)} of {format_size(total)}\n"
        f"🚀 Speed: {format_speed(speed)}\n"
        f"⏳ ETA: {format_time(eta)}"
    )

    # Add cancel button only for downloads
    reply_markup = None
    if download_id and "server_upload" not in download_id:
        keyboard = [
            [InlineKeyboardButton("❌ Cancel Download", callback_data="cancel_dl_active")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        if update.message:
            chat_id = update.message.chat_id
        elif update.callback_query:
            chat_id = update.callback_query.message.chat_id
        else:
            logger.error("No valid chat context for progress update")
            return

        logger.debug(f"Editing message {message_id} in chat {chat_id} for {action.lower()}")
        try:
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=message_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.warning(f"Failed to edit message {message_id}: {e}. Sending new message.")
            new_msg = await context.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
            # Update message_id for future updates
            global msg
            msg.id = new_msg.message_id
    except Exception as e:
        logger.error(f"Error updating progress: {e}") 

async def update_extraction_progress(context, chat_id, message_id, extracted, total, start_time, filename):
    """Update extraction progress message."""
    percent = (extracted / total * 100) if total > 0 else 0
    elapsed = time.time() - start_time
    speed = extracted / elapsed if elapsed > 0 else 0
    eta = (total - extracted) / speed if speed > 0 else 0

    progress_bar = "[" + "=" * int(percent / 5) + ">" + " " * (20 - int(percent / 5)) + "]"

    text = (
        f"📤 Extracting `{filename}`\n\n"
        f"{progress_bar} {percent:.1f}%\n\n"
        f"📊 {format_size(extracted)} of {format_size(total)}\n"
        f"🚀 Speed: {format_speed(speed)}\n"
        f"⏳ ETA: {format_time(eta)}"
    )

    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error updating extraction progress: {e}")

async def update_compression_progress(context, chat_id, message_id, compressed, total, start_time, filename):
    """Update compression progress message."""
    percent = (compressed / total * 100) if total > 0 else 0
    elapsed = time.time() - start_time
    speed = compressed / elapsed if elapsed > 0 else 0
    eta = (total - compressed) / speed if speed > 0 else 0

    progress_bar = "[" + "=" * int(percent / 5) + ">" + " " * (20 - int(percent / 5)) + "]"

    text = (
        f"🔒 Compressing `{filename}`\n\n"
        f"{progress_bar} {percent:.1f}%\n\n"
        f"📊 {format_size(compressed)} of {format_size(total)}\n"
        f"🚀 Speed: {format_speed(speed)}\n"
        f"⏳ ETA: {format_time(eta)}"
    )

    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error updating compression progress: {e}")

async def compress_file(context, chat_id, file_path, output_path, format_type):
    """Compress a file with progress feedback."""
    file_name = os.path.basename(file_path)
    total_size = os.path.getsize(file_path)
    compressed_size = 0
    start_time = time.time()
    last_update = start_time

    try:
        logger.info(f"Compressing {file_name} to {output_path} with format {format_type}")
        msg = await context.bot.send_message(chat_id, f"🔒 Compressing `{file_name}`...", parse_mode="Markdown")
        
        if format_type == "zip":
            with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                zf.write(file_path, os.path.basename(file_path))
                compressed_size = os.path.getsize(output_path)
                await update_compression_progress(context, chat_id, msg.message_id, compressed_size, total_size, start_time, file_name)
        elif format_type == "rar":
            result = subprocess.run(
                ["rar", "a", output_path, file_path],
                check=True,
                capture_output=True,
                text=True
            )
            logger.debug(f"RAR compression output: {result.stdout}")
            compressed_size = os.path.getsize(output_path)
            await update_compression_progress(context, chat_id, msg.message_id, compressed_size, total_size, start_time, file_name)
        elif format_type == "7z":
            with py7zr.SevenZipFile(output_path, 'w') as szf:
                szf.write(file_path, os.path.basename(file_path))
                compressed_size = os.path.getsize(output_path)
                await update_compression_progress(context, chat_id, msg.message_id, compressed_size, total_size, start_time, file_name)
        elif format_type in ("tar.gz", "tar.bz2"):
            mode = 'w:gz' if format_type == "tar.gz" else 'w:bz2'
            with tarfile.open(output_path, mode) as tf:
                tf.add(file_path, arcname=os.path.basename(file_path))
                compressed_size = os.path.getsize(output_path)
                await update_compression_progress(context, chat_id, msg.message_id, compressed_size, total_size, start_time, file_name)
        else:
            logger.error(f"Unsupported compression format: {format_type}")
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=msg.message_id,
                text=f"❌ Unsupported compression format: {format_type}",
                parse_mode="Markdown"
            )
            return

        logger.info(f"Compression completed: {file_name} -> {output_path}")
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg.message_id,
            text=f"✅ Compression of `{file_name}` completed successfully!",
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Compression failed for {file_name}: {str(e)}")
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=msg.message_id,
            text=f"❌ Compression failed: {str(e)}",
            parse_mode="Markdown"
        )
        if os.path.exists(output_path):
            os.remove(output_path)
################################
# Authentication Handlers
################################

# States
USERNAME, PASSWORD = range(2)

async def start(update: Update, context: CallbackContext) -> int:
    user_first_name = update.message.from_user.first_name
    await update.message.reply_text(
        f"Hi {user_first_name}, Welcome to LucianGateway bot!\n\n"
        "I can upload files, download direct links, show storage details, and list your files.\n"
        "Use /login to start."
    )
    return ConversationHandler.END

async def login(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id

    # Check if user is already logged in
    if user_id in sessions:
        await update.message.reply_text("❌ You are already logged in. Use /logout to switch accounts.")
        return ConversationHandler.END

    # Ensure broadcast settings remain enabled for the specific user ID
    if user_id == 1074000261:
        if str(user_id) not in broadcast_settings:
            broadcast_settings[str(user_id)] = {"receive_updates": True}
            save_broadcast_settings(broadcast_settings)

    context.user_data.clear()
    await update.message.reply_text("📌 Step 1: Please enter your username:")
    return USERNAME

async def username(update: Update, context: CallbackContext) -> int:
    context.user_data['username'] = update.message.text.strip()
    await update.message.reply_text("📌 Step 2: Please enter your password:")
    return PASSWORD

async def password(update: Update, context: CallbackContext) -> int:
    username_val = context.user_data.get('username')
    password_val = update.message.text.strip()

    response = requests.post(FLASK_API_URL, json={"username": username_val, "password": password_val})
    if response.status_code == 200:
        user_id = update.message.from_user.id
        sessions[user_id] = username_val
        # Store credentials in application.bot_data
        context.application.bot_data.setdefault('user_credentials', {})[user_id] = {
            "username": username_val,
            "password": password_val
        }

        user_folder = f"/DATA/Users/{username_val}"
        os.makedirs(user_folder, exist_ok=True)

        # Save user session to restore_users.json
        restore_data = load_restore_users()
        restore_data[str(user_id)] = {
            "username": username_val,
            "password": password_val
        }
        save_restore_users(restore_data)

        # Initialize broadcast settings for the user
        user_key = str(user_id)
        if user_key not in broadcast_settings:
            # Set receive_updates to True for all users by default (1074000261 is already handled)
            broadcast_settings[user_key] = {"receive_updates": True}
            save_broadcast_settings(broadcast_settings)

        await update.message.reply_text(
            f"✅ Login successful! Welcome, {username_val}.\n"
            "You can now upload files, check storage with /storage, or view your files with /myfiles."
        )
    else:
        await update.message.reply_text("❌ Invalid credentials. Please try again using /login.")

    return ConversationHandler.END
async def logout(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    if user_id in sessions:
        # Remove from sessions
        del sessions[user_id]
        
        # Remove from restore_users.json
        restore_data = load_restore_users()
        restore_data.pop(str(user_id), None)
        save_restore_users(restore_data)
        
        await update.message.reply_text("✅ Successfully logged out!")
    else:
        await update.message.reply_text("❌ You are not logged in.")
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("⚠️ Login cancelled. Use /login to try again.")
    return ConversationHandler.END

# Function to save broadcast settings
def save_broadcast_settings(settings):
    """Save the broadcast settings to a file or database (implementation needed)."""
    pass  # Implement actual saving mechanism

################################
# Storage Management Handlers
################################
def get_total_storage_details(username_val):
    """Retrieve user and server storage details in a formatted manner."""
    user_folder = f"/DATA/Users/{username_val}"
    user_size_bytes = get_folder_size(user_folder)
    user_size = format_size(user_size_bytes)

    total, used, free = shutil.disk_usage("/")
    total_hr = format_size(total)
    used_hr = format_size(used)
    free_hr = format_size(free)
    used_percentage = (used / total) * 100
    free_percentage = (free / total) * 100

    return (
        f"💽 *Storage details:*\n\n"
        f"*User storage details -*\n"
        f"`{username_val}` : *{user_size}*\n\n"
        f"*Total server storage -*\n"
        f"Used: *{used_hr}* of *{total_hr}*\n"
        f"Free: *{free_hr}* of *{total_hr}*\n"
        f"Storage used: *{used_percentage:.2f}%*\n"
        f"Storage free: *{free_percentage:.2f}%*"
    )

def get_folder_size(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)
    return total_size

async def storage(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in sessions:
        await update.message.reply_text("❌ Please login first using /login.")
        return

    username = sessions[user_id]
    # Access password from bot_data instead of user_data
    password = context.application.bot_data.get('user_credentials', {}).get(user_id, {}).get('password')
    if not password:
        await update.message.reply_text("❌ Session error. Please login again using /login.")
        return

    username_val = sessions[user_id]
    storage_details = get_total_storage_details(username_val)

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔁 Refresh", callback_data="refresh_storage"),
            InlineKeyboardButton("❌ Close", callback_data="close_storage")
        ]
    ])

    sent = await update.message.reply_text(
        storage_details,
        parse_mode="Markdown",
        reply_markup=keyboard
    )

    # ✅ Save both user and bot message IDs
    context.user_data["storage_user_msg_id"] = update.message.message_id
    context.user_data["storage_bot_msg_id"] = sent.message_id

    return ConversationHandler.END

def strip_markdown(text):
    return re.sub(r'[*`_]', '', text).strip()
async def refresh_storage(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    if user_id not in sessions:
        await query.edit_message_text("❌ Please login again to view storage.")
        return

    username_val = sessions[user_id]
    new_text = get_total_storage_details(username_val).strip()
    current_text = query.message.text.strip()

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔁 Refresh", callback_data="refresh_storage"),
            InlineKeyboardButton("❌ Close", callback_data="close_storage")
        ]
    ])

async def close_storage(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # Delete the bot's message (the one with buttons)
    try:
        await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
    except:
        pass

    # Also try to delete the user's original /storage command
    user_msg_id = context.user_data.get("storage_user_msg_id")
    if user_msg_id:
        try:
            await context.bot.delete_message(chat_id=query.message.chat_id, message_id=user_msg_id)
        except:
            pass


################################
# Help function
################################

async def help_command(update: Update, context: CallbackContext) -> None:
    help_text = """\
🧑‍💻 *Account Commands*

`/login` – Login to your account.  
`/logout` – Logout from your current session.

📦 *File Handling*

Send a direct download link (`http/https`) – The bot will fetch file info and let you upload it to the server.

Send a file directly – The bot will save it to your storage.

💽 *Storage*

`/storage` – View your personal storage usage and total server storage details.

📁 *File List*

`/myfiles` - View your personal files and rename or delete then accordingly.

🚫 *Cancel Tasks*

Cancel ongoing downloads using the cancel button when prompted.

ℹ️ *Other*

`/help` – Show this help message.

📝 *Note:* You must be logged in to use most features. Use `/login` if you haven’t already.
"""
    await update.message.reply_text(help_text, parse_mode="Markdown")

################################
# Account setup
################################

async def accounts(update: Update, context: CallbackContext):
    user = update.message.from_user
    user_id = user.id
    full_name = f"{user.first_name} {user.last_name}".strip() if user.last_name else user.first_name

    if user_id not in sessions:
        await update.message.reply_text("❌ You are not logged in. Use /login first.")
        return ConversationHandler.END

    username = sessions[user_id]
    password = context.user_data.get('password', '****')
    
    uptime = str(timedelta(seconds=int(time.time() - bot_start_time)))
    bot_start_datetime = datetime.fromtimestamp(bot_start_time, tz=IST).strftime("%d-%m-%Y %I:%M %p")

    text = (
        f"*User Details -*\n"
        f"👤 *User ID:* `{user_id}`\n"
        f"📛 *Name:* `{full_name}`\n\n"
        f"*Account Details -*\n"
        f"*Username:* `{username}`\n"
        f"*Password:* `{password}`\n\n"
        f"*Membership:* Free user\n"
        f"*Billing:* 0$, free limit\n\n"
        f"*Bot Uptime:* `{uptime}`\n"
        f"*Bot Started at:* `{bot_start_datetime}`"
    )

    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔒 Change Password", callback_data="change_pw")]])
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.MARKDOWN)

async def handle_change_pw_prompt(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("🔑 Enter new password:")
    return CHANGING_PASSWORD

async def handle_new_password(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    new_password = update.message.text.strip()

    username = sessions.get(user_id)
    if not username:
        await update.message.reply_text("❌ You're not logged in.")
        return ConversationHandler.END

    # Modify USERS dictionary in auth_server.py
    auth_path = "auth_server.py"
    try:
        with open(auth_path, 'r') as file:
            lines = file.readlines()

        new_lines = []
        for line in lines:
            if f'"{username}":' in line:
                new_line = f'    "{username}": "{new_password}",\n'
                new_lines.append(new_line)
            else:
                new_lines.append(line)

        with open(auth_path, 'w') as file:
            file.writelines(new_lines)

        subprocess.run(["sudo", "/bin/systemctl", "restart", "auth_server.service"])

        context.user_data['password'] = new_password
        await update.message.reply_text("✅ Password updated successfully!\n🔄 Please re-login with your new password.")
        del sessions[user_id]  # Force re-login
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to update password: {e}")

    return ConversationHandler.END

################################
# Myfiles setup here
################################

async def myfiles(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = None
    chat = None

    if update.message:
        user = update.message.from_user
        chat = update.message.chat
    elif update.callback_query:
        user = update.callback_query.from_user
        chat = update.callback_query.message.chat

    if user is None or chat is None:
        logger.error("User or chat not found in update during myfiles()")
        return

    user_id = user.id
    if user_id not in sessions:
        await context.bot.send_message(chat_id=chat.id, text="❌ Please login first using /login.")
        return

    username_val = sessions[user_id]
    user_folder = f"/DATA/Users/{username_val}"
    context.user_data['path_stack'] = [user_folder]

    keyboard = [[InlineKeyboardButton("🆕 New Folder", callback_data="new_folder")]]
    folder_buttons = list_directory_contents(user_folder, context)

    if not folder_buttons:
        folder_buttons = [[InlineKeyboardButton("📂 Folder is empty", callback_data="noop")]]
    keyboard += folder_buttons
    keyboard.append([InlineKeyboardButton("🔄 Refresh", callback_data="refresh")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(chat_id=chat.id, text="📂 Your drive files:", reply_markup=reply_markup)

async def show_extraction_folder_menu(update, context):
    query = update.callback_query
    path_stack = context.user_data.get("move_path_stack", [])
    current_path = path_stack[-1] if path_stack else None

    if not current_path or not os.path.exists(current_path):
        await query.edit_message_text("❌ Directory not found.")
        return

    items = [d for d in os.listdir(current_path) if os.path.isdir(os.path.join(current_path, d))]
    keyboard = []

    for folder in sorted(items):
        full_path = os.path.join(current_path, folder)
        uid = register_path(context, full_path)
        keyboard.append([InlineKeyboardButton(f"📁 {folder}", callback_data=f"extract_nav|{uid}")])

    if len(path_stack) > 1:
        keyboard.insert(0, [InlineKeyboardButton("⬅️ Back", callback_data="extract_nav_back")])

    if not items:
        keyboard.append([InlineKeyboardButton("📂 Directory is empty", callback_data="noop")])
    keyboard.append([InlineKeyboardButton("📤 Extract Here", callback_data="extract_execute")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text("📂 Select a folder to extract into:", reply_markup=reply_markup)

async def show_move_folder_menu(update, context):
    query = update.callback_query
    path_stack = context.user_data.get("move_path_stack", [])
    current_path = path_stack[-1] if path_stack else None

    if not current_path or not os.path.exists(current_path):
        await query.edit_message_text("❌ Directory not found.")
        return

    items = [d for d in os.listdir(current_path) if os.path.isdir(os.path.join(current_path, d))]
    keyboard = []

    for folder in sorted(items):
        full_path = os.path.join(current_path, folder)
        uid = register_path(context, full_path)
        keyboard.append([InlineKeyboardButton(f"📁 {folder}", callback_data=f"move_nav|{uid}")])

    if len(path_stack) > 1:
        keyboard.insert(0, [InlineKeyboardButton("⬅️ Back", callback_data="move_nav_back")])

    if not items:
        keyboard.append([InlineKeyboardButton("📂 Directory is empty", callback_data="noop")])

    keyboard.append([InlineKeyboardButton("📤 Move Here", callback_data="move_execute")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_text("📂 Select a folder to move into:", reply_markup=reply_markup)


async def myfiles_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    user_id = query.from_user.id
    if user_id not in sessions:
        await query.edit_message_text("❌ Please login first using /login.")
        return

    username_val = sessions[user_id]
    main_directory = f"/DATA/Users/{username_val}"

    if data == "noop":
        return

    if data == "back":
        path_stack = context.user_data.get('path_stack', [])
        if len(path_stack) > 1:
            path_stack.pop()
        current_path = path_stack[-1] if path_stack else main_directory
        context.user_data['path_stack'] = path_stack

        keyboard = list_directory_contents(current_path, context)
        if not keyboard:
            keyboard = [[InlineKeyboardButton("📂 Folder is empty", callback_data="noop")]]

        current_uid = next((k for k, v in context.user_data.get("path_map", {}).items() if v == current_path), None)
        if current_path == main_directory:
            keyboard.insert(0, [InlineKeyboardButton("🆕 New Folder", callback_data="new_folder")])
        else:
            if current_uid:
                keyboard.append([
                    InlineKeyboardButton("✏️ Rename Folder", callback_data=f"rename_folder|{current_uid}"),
                    InlineKeyboardButton("🚚 Move Folder", callback_data=f"move_folder|{current_uid}")
                ])
                keyboard.append([
                    InlineKeyboardButton("🚮 Delete This Folder", callback_data=f"delete_folder|{current_uid}"),
                    InlineKeyboardButton("🆕 New Folder", callback_data="new_folder")
                ])
            if len(path_stack) > 1:
                keyboard.insert(0, [InlineKeyboardButton("⬅️ Back", callback_data="back")])

        keyboard.append([InlineKeyboardButton("🔄 Refresh", callback_data="refresh")])

        await query.edit_message_text(
            text=f"📂 Folder: {os.path.basename(current_path)}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if data.startswith("extract_nav|"):
        _, uid = data.split("|", 1)
        path = context.user_data.get("path_map", {}).get(uid)
        if not path or not os.path.isdir(path):
            await query.edit_message_text("❌ Folder not found.")
            return
        context.user_data["move_path_stack"].append(path)
        await show_extraction_folder_menu(update, context)
        return

    if data == "extract_nav_back":
        if len(context.user_data.get("move_path_stack", [])) > 1:
            context.user_data["move_path_stack"].pop()
        await show_extraction_folder_menu(update, context)
        return

    if data == "extract_execute":
        uid = context.user_data.get("pending_extract_uid")
        extract_mode = context.user_data.get("extract_mode", "flat")
        if not uid:
            await query.edit_message_text("❌ No file selected for extraction.")
            return

        archive_path = context.user_data.get("path_map", {}).get(uid)
        target_dir = context.user_data["move_path_stack"][-1]

        if extract_mode == "folder":
            base_name = os.path.splitext(os.path.basename(archive_path))[0]
            target_dir = os.path.join(target_dir, base_name)

        os.makedirs(target_dir, exist_ok=True)
        subprocess.run(["sudo", "chmod", "-R", "777", target_dir], check=False)

        await extract_archive(context, query.message.chat_id, archive_path, target_dir)
        return

    if data.startswith("move_nav|"):
        _, uid = data.split("|", 1)
        path = context.user_data.get("path_map", {}).get(uid)
        if not path or not os.path.isdir(path):
            await query.edit_message_text("❌ Folder not found.")
            return
        context.user_data["move_path_stack"].append(path)
        await show_move_folder_menu(update, context)
        return

    if data == "move_nav_back":
        if len(context.user_data.get("move_path_stack", [])) > 1:
            context.user_data["move_path_stack"].pop()
        await show_move_folder_menu(update, context)
        return

    if data == "move_execute":
        source_path = context.user_data.get("move_file_path")
        dest_path = context.user_data["move_path_stack"][-1]
        if not source_path or not os.path.exists(source_path):
            await query.edit_message_text("❌ Source file not found.")
            return
        try:
            shutil.move(source_path, dest_path)
            await query.edit_message_text("✅ File moved successfully.")
        except Exception as e:
            await query.edit_message_text(f"❌ Move failed: {e}")
        return

    if data == "refresh":
        path_stack = context.user_data.get('path_stack', [])
        if not path_stack:
            await query.edit_message_text("❌ No current folder selected.")
            return

        current_path = path_stack[-1]
        keyboard = list_directory_contents(current_path, context)
        if not keyboard:
            keyboard = [[InlineKeyboardButton("📂 Folder is empty", callback_data="noop")]]

        current_uid = next((k for k, v in context.user_data.get("path_map", {}).items() if v == current_path), None)
        if current_path == main_directory:
            keyboard.insert(0, [InlineKeyboardButton("🆕 New Folder", callback_data="new_folder")])
        else:
            if current_uid:
                keyboard.append([
                    InlineKeyboardButton("✏️ Rename Folder", callback_data=f"rename_folder|{current_uid}"),
                    InlineKeyboardButton("🚚 Move Folder", callback_data=f"move_folder|{current_uid}")
                ])
                keyboard.append([
                    InlineKeyboardButton("🚮 Delete This Folder", callback_data=f"delete_folder|{current_uid}"),
                    InlineKeyboardButton("🆕 New Folder", callback_data="new_folder")
                ])
            if len(path_stack) > 1:
                keyboard.insert(0, [InlineKeyboardButton("⬅️ Back", callback_data="back")])

        keyboard.append([InlineKeyboardButton("🔄 Refresh", callback_data="refresh")])

        await query.edit_message_text(
            text=f"📂 Folder: {os.path.basename(current_path)}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    if data == "confirm_delete":
        try:
            path = context.user_data.get("confirm_delete_path")
            item_type = context.user_data.get("confirm_delete_type")
            if not path or not is_safe_to_delete(path, username_val):
                await query.edit_message_text("❌ Unsafe or unauthorized deletion attempt blocked.")
                return

            result = subprocess.run(
                ["sudo", "rm", "-rf", path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            if result.returncode != 0:
                raise Exception(result.stderr.decode())

            context.user_data.pop("confirm_delete_path", None)
            context.user_data.pop("confirm_delete_type", None)

            path_stack = context.user_data.get('path_stack', [])
            if len(path_stack) > 1:
                path_stack.pop()
            current_path = path_stack[-1] if path_stack else main_directory
            context.user_data['path_stack'] = path_stack

            keyboard = list_directory_contents(current_path, context)
            if not keyboard:
                keyboard = [[InlineKeyboardButton("📂 Folder is empty", callback_data="noop")]]

            current_uid = next((k for k, v in context.user_data.get("path_map", {}).items() if v == current_path), None)
            if current_path == main_directory:
                keyboard.insert(0, [InlineKeyboardButton("🆕 New Folder", callback_data="new_folder")])
            else:
                if current_uid:
                    keyboard.append([
                        InlineKeyboardButton("✏️ Rename Folder", callback_data=f"rename_folder|{current_uid}"),
                        InlineKeyboardButton("🚚 Move Folder", callback_data=f"move_folder|{current_uid}")
                    ])
                    keyboard.append([
                        InlineKeyboardButton("🚮 Delete This Folder", callback_data=f"delete_folder|{current_uid}"),
                        InlineKeyboardButton("🆕 New Folder", callback_data="new_folder")
                    ])
                if len(path_stack) > 1:
                    keyboard.insert(0, [InlineKeyboardButton("⬅️ Back", callback_data="back")])

            keyboard.append([InlineKeyboardButton("🔄 Refresh", callback_data="refresh")])

            await query.edit_message_text(
                text="✅ File or folder deleted successfully.\n\n📂 Folder refreshed.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            await query.edit_message_text(f"❌ Error deleting file: {str(e)}")
        return

    if data == "cancel_delete":
        path_stack = context.user_data.get("path_stack", [])
        if not path_stack:
            await query.edit_message_text("❌ Cannot restore previous menu.")
            return

        current_path = path_stack[-1]
        keyboard = list_directory_contents(current_path, context)
        if not keyboard:
            keyboard = [[InlineKeyboardButton("📂 Folder is empty", callback_data="noop")]]

        current_uid = next((k for k, v in context.user_data.get("path_map", {}).items() if v == current_path), None)
        if current_path == main_directory:
            keyboard.insert(0, [InlineKeyboardButton("🆕 New Folder", callback_data="new_folder")])
        else:
            if current_uid:
                keyboard.append([
                    InlineKeyboardButton("✏️ Rename Folder", callback_data=f"rename_folder|{current_uid}"),
                    InlineKeyboardButton("🚚 Move Folder", callback_data=f"move_folder|{current_uid}")
                ])
                keyboard.append([
                    InlineKeyboardButton("🚮 Delete This Folder", callback_data=f"delete_folder|{current_uid}"),
                    InlineKeyboardButton("🆕 New Folder", callback_data="new_folder")
                ])
            if len(path_stack) > 1:
                keyboard.insert(0, [InlineKeyboardButton("⬅️ Back", callback_data="back")])

        keyboard.append([InlineKeyboardButton("🔄 Refresh", callback_data="refresh")])

        await query.edit_message_text(
            text=f"📂 Folder: {os.path.basename(current_path)}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Parse action and uid
    try:
        action, uid = data.split("|", 1)
    except ValueError:
        await query.edit_message_text("⚠️ Invalid action.")
        return

    path = context.user_data.get("path_map", {}).get(uid)
    if not path or not os.path.exists(path):
        await query.edit_message_text("❌ Path not found.")
        return

    if action == "open":
        context.user_data['path_stack'].append(path)
        current_path = path
        keyboard = list_directory_contents(current_path, context)
        if not keyboard:
            keyboard = [[InlineKeyboardButton("📂 Folder is empty", callback_data="noop")]]

        current_uid = next((k for k, v in context.user_data.get("path_map", {}).items() if v == current_path), None)
        if current_path == main_directory:
            keyboard.insert(0, [InlineKeyboardButton("🆕 New Folder", callback_data="new_folder")])
        else:
            if current_uid:
                keyboard.append([
                    InlineKeyboardButton("✏️ Rename Folder", callback_data=f"rename_folder|{current_uid}"),
                    InlineKeyboardButton("🚚 Move Folder", callback_data=f"move_folder|{current_uid}")
                ])
                keyboard.append([
                    InlineKeyboardButton("🚮 Delete This Folder", callback_data=f"delete_folder|{current_uid}"),
                    InlineKeyboardButton("🆕 New Folder", callback_data="new_folder")
                ])
            if len(context.user_data.get("path_stack", [])) > 1:
                keyboard.insert(0, [InlineKeyboardButton("⬅️ Back", callback_data="back")])

        keyboard.append([InlineKeyboardButton("🔄 Refresh", callback_data="refresh")])

        await query.edit_message_text(
            text=f"📂 Folder: {os.path.basename(current_path)}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    elif action == "file":
        try:
            size_str = format_size(os.path.getsize(path))
        except Exception:
            size_str = "Unknown size"

        # Check if file is compressed
        compressed_extensions = ['.zip', '.rar', '.7z', '.tar.gz', '.tar.bz2']
        is_compressed = any(path.lower().endswith(ext) for ext in compressed_extensions)

        keyboard = [
            [InlineKeyboardButton("⬅️ Back", callback_data="back")],
            [
                InlineKeyboardButton("📥 Download", callback_data=f"download_file|{uid}"),
                InlineKeyboardButton("✏️ Rename", callback_data=f"rename|{uid}")
            ],
            [
                InlineKeyboardButton("🚚 Move", callback_data=f"move_file|{uid}"),
                InlineKeyboardButton("🗑️ Delete", callback_data=f"delete_file|{uid}")
            ]
        ]
        if is_compressed:
            keyboard.append([
                InlineKeyboardButton("📤 Extract", callback_data=f"extract|{uid}"),
                InlineKeyboardButton("📂 Extract to Folder", callback_data=f"extract_to_folder|{uid}")
            ])
        else:
            keyboard.append([InlineKeyboardButton("🔒 Compress", callback_data=f"compress|{uid}")])

        await query.edit_message_text(
            text=f"📄 File: {os.path.basename(path)}\n📦 Size: {size_str}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    elif action == "download_file":
        if not os.path.isfile(path):
            await query.edit_message_text("❌ File not found.")
            return

        logger.info(f"User {user_id} downloading file: {path}")
        file_name = os.path.basename(path)
        file_size = os.path.getsize(path)
        chat_id = query.message.chat_id

        # Setup cancel token and upload task tracking
        upload_token = f"upload_{uuid.uuid4().hex}"
        upload_tasks.setdefault(user_id, {})[upload_token] = None  # Placeholder for task
        logger.info(f"Generated upload token: {upload_token}")

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("❌ Cancel Upload", callback_data=f"cancel_uploading|{upload_token}")]
        ])

        # Initial uploading message
        msg = await context.bot.send_message(
            chat_id=chat_id,
            text=f"⬆️ Uploading `{file_name}`...\n[                    ] 0.0%\n\n📊 0MB of {file_size/1024/1024:.2f}MB\n🚀 Speed: 0MB/s\n⏳ ETA: 00:00:00",
            parse_mode="Markdown",
            reply_markup=keyboard
        )

        start_time = time.time()
        last_update = start_time

        # Use a new Pyrogram client instance for this operation
        async with Client("temp_session", api_id=api_id, api_hash=api_hash, bot_token="7984121127:AAGyBslNMIkUEaEd6z2NdhqHSqFIJOGElxQ") as temp_client:
            async def progress_callback(current, total):
                nonlocal last_update
                now = time.time()

                if upload_token not in upload_tasks.get(user_id, {}):
                    raise asyncio.CancelledError("Upload cancelled")

                # Update progress only when necessary
                if now - last_update > 2 or current == total:
                    percent = (current / total) * 100 if total else 0
                    bar_length = 20
                    filled_length = int(bar_length * percent // 100)
                    progress_bar = "[" + "=" * filled_length + ">" + " " * (bar_length - filled_length - 1) + "]"
                    uploaded_mb = current / 1024 / 1024
                    total_mb = total / 1024 / 1024
                    speed = current / (now - start_time + 1e-6)
                    eta = (total - current) / (speed + 1e-6)
                    eta_formatted = str(timedelta(seconds=int(eta)))

                    text = (
                        f"⬆️ Uploading to Telegram `{file_name}`\n\n"
                        f"{progress_bar} {percent:.1f}%\n\n"
                        f"📊 {uploaded_mb:.2f}MB of {total_mb:.2f}MB\n"
                        f"🚀 Speed: {speed / 1024:.2f}KB/s\n"
                        f"⏳ ETA: {eta_formatted}"
                    )
                    try:
                        await msg.edit_text(text, parse_mode="Markdown", reply_markup=keyboard)
                    except Exception as e:
                        logger.warning(f"Failed to update progress message: {e}")
                    last_update = now

            try:
                # Perform the upload using the temporary Pyrogram client
                task = asyncio.create_task(
                    temp_client.send_document(
                        chat_id=chat_id,
                        document=path,
                        caption=f"📄 {file_name}",
                        progress=progress_callback
                    )
                )
                # Assign the task to the upload_tasks dictionary
                upload_tasks[user_id][upload_token] = task
                await task
                logger.info(f"Upload completed for file: {file_name}")
                await msg.delete()

            except asyncio.CancelledError:
                logger.info(f"Upload cancelled for token: {upload_token}")
                try:
                    await msg.edit_text("❌ Upload cancelled by user.", parse_mode="Markdown")
                except Exception as e:
                    logger.warning(f"Failed to update message on cancellation: {e}")
            except Exception as e:
                logger.error(f"Upload interrupted for user {user_id}: {e}")
                try:
                    await msg.edit_text(f"❌ Upload failed: {str(e)}", parse_mode="Markdown")
                except Exception as e:
                    logger.warning(f"Failed to update message on error: {e}")
            finally:
                # Clean up the upload task from the dictionary
                upload_tasks.get(user_id, {}).pop(upload_token, None)
                if user_id in upload_tasks and not upload_tasks[user_id]:
                    upload_tasks.pop(user_id, None)


    elif action == "move_file":
        if not os.path.isfile(path):
            await query.edit_message_text("❌ File not found.")
            return
        context.user_data["move_file_uid"] = uid
        context.user_data["move_file_path"] = path
        context.user_data["current_mode"] = "move_file"
        context.user_data["move_path_stack"] = [main_directory]

        await query.edit_message_text(
            f"📄 Moving file: {os.path.basename(path)}\n\nSelect a target folder to move to:"
        )
        await show_move_folder_menu(update, context)
        return

    elif action == "compress":
        if not os.path.isfile(path):
            await query.edit_message_text("❌ File not found.")
            return
        context.user_data["compress_uid"] = uid
        keyboard = [
            [
                InlineKeyboardButton("ZIP", callback_data=f"compress_format|{uid}|zip"),
                InlineKeyboardButton("RAR", callback_data=f"compress_format|{uid}|rar")
            ],
            [
                InlineKeyboardButton("7Z", callback_data=f"compress_format|{uid}|7z"),
                InlineKeyboardButton("TAR.GZ", callback_data=f"compress_format|{uid}|tar.gz")
            ],
            [
                InlineKeyboardButton("TAR.BZ2", callback_data=f"compress_format|{uid}|tar.bz2"),
                InlineKeyboardButton("❌ Cancel", callback_data="cancel_compress")
            ]
        ]
        await query.edit_message_text(
            text=f"📄 File: {os.path.basename(path)}\n\nSelect compression format:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    elif action == "compress_format":
        try:
            _, uid, format_type = data.split("|", 2)
        except ValueError:
            logger.error(f"Invalid compress_format callback data: {data}")
            await query.edit_message_text("❌ Invalid compression request.")
            return

        # Retrieve path from path_map
        path_map = context.user_data.get("path_map", {})
        logger.debug(f"Path map contents: {path_map}")
        path = path_map.get(uid)
        if not path:
            logger.error(f"Path not found in path_map for uid: {uid}")
            await query.edit_message_text("❌ Path not found in path map.")
            return

        # Verify file existence and type
        if not os.path.exists(path):
            logger.error(f"File does not exist: {path}")
            await query.edit_message_text(f"❌ File not found: {os.path.basename(path)}")
            return
        if not os.path.isfile(path):
            logger.error(f"Path is not a file: {path}")
            await query.edit_message_text(f"❌ Selected item is not a file: {os.path.basename(path)}")
            return

        # Get parent directory and ensure permissions
        parent_dir = os.path.dirname(path)
        try:
            ensure_folder_permissions(parent_dir)
        except Exception as e:
            logger.error(f"Failed to set permissions for {parent_dir}: {e}")
            await query.edit_message_text("❌ Permission error while accessing directory.")
            return

        # Generate compressed file path
        base_name = os.path.splitext(os.path.basename(path))[0]
        extension = format_type if format_type in ["zip", "rar", "7z"] else f"tar.{format_type.split('.')[-1]}"
        compressed_path = os.path.join(parent_dir, f"{base_name}.{extension}")

        # Check if compressed file already exists
        if os.path.exists(compressed_path):
            await query.edit_message_text(
                f"⚠️ A file named `{os.path.basename(compressed_path)}` already exists.",
                parse_mode="Markdown"
            )
            return

        # Log compression attempt
        logger.info(f"Starting compression: {path} to {compressed_path} as {format_type}")

        # Perform compression
        await compress_file(context, query.message.chat_id, path, compressed_path, format_type)

        # Update path_map with the new compressed file
        new_uid = register_path(context, compressed_path)
        logger.info(f"Registered new compressed file: {compressed_path} with uid: {new_uid}")

        # Refresh the file list to show the new compressed file
        context.user_data['path_stack'] = [parent_dir]
        keyboard = list_directory_contents(parent_dir, context)
        if not keyboard:
            keyboard = [[InlineKeyboardButton("📂 Folder is empty", callback_data="noop")]]
        keyboard.insert(0, [InlineKeyboardButton("🆕 New Folder", callback_data="new_folder")])
        if parent_dir != main_directory:
            current_uid = next((k for k, v in path_map.items() if v == parent_dir), None)
            if current_uid:
                keyboard.append([
                    InlineKeyboardButton("✏️ Rename Folder", callback_data=f"rename_folder|{current_uid}"),
                    InlineKeyboardButton("🚚 Move Folder", callback_data=f"move_folder|{current_uid}")
                ])
                keyboard.append([
                    InlineKeyboardButton("🚮 Delete This Folder", callback_data=f"delete_folder|{current_uid}"),
                    InlineKeyboardButton("🆕 New Folder", callback_data="new_folder")
                ])
            keyboard.insert(0, [InlineKeyboardButton("⬅️ Back", callback_data="back")])
        keyboard.append([InlineKeyboardButton("🔄 Refresh", callback_data="refresh")])

        await query.edit_message_text(
            text=f"📂 Folder: {os.path.basename(parent_dir)}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    elif action == "cancel_compress":
        await query.edit_message_text("❌ Compression cancelled.")
        return

    elif action == "extract":
        context.user_data["pending_extract_uid"] = uid
        context.user_data["extract_mode"] = "flat"
        context.user_data["move_path_stack"] = [main_directory]

        await query.edit_message_text("📂 Select a folder to extract into (or extract here if none):")
        await show_extraction_folder_menu(update, context)
        return

    elif action == "extract_to_folder":
        context.user_data["pending_extract_uid"] = uid
        context.user_data["extract_mode"] = "folder"
        context.user_data["move_path_stack"] = [main_directory]

        await query.edit_message_text("📂 Select a folder to extract into (or extract here if none):")
        await show_extraction_folder_menu(update, context)
        return

    elif action == "extract_to_folder":
        if not os.path.isfile(path):
            await query.edit_message_text("❌ File not found.")
            return
        parent_dir = os.path.dirname(path)
        if not is_safe_to_delete(parent_dir, username_val):
            await query.edit_message_text("❌ Cannot extract to unauthorized location.")
            return
        base_name = os.path.splitext(os.path.basename(path))[0]
        extraction_dir = os.path.join(parent_dir, base_name)
        context.user_data["extract_uid"] = uid
        context.user_data["extract_mode"] = "folder"
        context.user_data["extract_dir"] = extraction_dir
        if os.path.exists(extraction_dir):
            keyboard = [
                [InlineKeyboardButton("✅ Yes, overwrite", callback_data=f"overwrite_extract|{uid}"),
                 InlineKeyboardButton("❌ No, skip", callback_data=f"skip_extract|{uid}")]
            ]
            await query.edit_message_text(
                text=f"⚠️ Folder `{base_name}` already exists. Do you want to overwrite it?",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await extract_archive(context, query.message.chat_id, path, extraction_dir)
        return

    elif action == "overwrite_extract":
        if not os.path.exists(path):
            await query.edit_message_text("❌ File not found.")
            return
        mode = context.user_data.get("extract_mode")
        if mode == "parent":
            extraction_dir = os.path.dirname(path)
        elif mode == "folder":
            extraction_dir = context.user_data.get("extract_dir")
        else:
            await query.edit_message_text("❌ Invalid extraction mode.")
            return
        if not is_safe_to_delete(extraction_dir, username_val):
            await query.edit_message_text("❌ Cannot extract to unauthorized location.")
            return
        if mode == "folder" and os.path.exists(extraction_dir):
            shutil.rmtree(extraction_dir)
        await extract_archive(context, query.message.chat_id, path, extraction_dir, overwrite=True)
        context.user_data.pop("extract_conflict", None)
        context.user_data.pop("extract_dir", None)
        return

    elif action == "skip_extract":
        context.user_data.pop("extract_conflict", None)
        context.user_data.pop("extract_dir", None)
        await query.edit_message_text("❌ Extraction cancelled.")
        return

    elif action in ["delete_file", "delete_folder"]:
        confirm_type = "file" if action == "delete_file" else "folder"
        context.user_data["confirm_delete_path"] = path
        context.user_data["confirm_delete_type"] = confirm_type
        filename = os.path.basename(path)
        keyboard = [
            [InlineKeyboardButton("✅ Yes, delete", callback_data="confirm_delete"),
             InlineKeyboardButton("❌ No, go back", callback_data="cancel_delete")]
        ]
        await query.edit_message_text(
            text=f"⚠️ Do you really want to delete `{filename}`?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

async def cancel_uploading(update: Update, context: CallbackContext):
    query = update.callback_query
    try:
        await query.answer()
    except Exception as e:
        logger.warning(f"Failed to answer callback query: {e}")

    try:
        upload_token = query.data.split('|')[1]
    except IndexError:
        logger.error("Invalid cancel_uploading callback data format")
        await query.edit_message_text("❌ Error: Invalid cancellation request.")
        return

    user_id = query.from_user.id
    task = upload_tasks.get(user_id, {}).get(upload_token)
    if not task:
        logger.warning(f"Upload token {upload_token} not found in upload_tasks")
        await query.edit_message_text("❌ No active upload found for this token.")
        return

    task.cancel()
    logger.info(f"Upload cancellation requested for token: {upload_token}")

    try:
        await query.edit_message_text("⏳ Cancelling upload...", parse_mode="Markdown")
    except Exception as e:
        logger.warning(f"Failed to edit message during cancel: {e}")

#####New Folder###########
##########################

async def start_new_folder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    if user_id not in sessions:
        await query.message.reply_text("❌ Please login first using /login.")
        return ConversationHandler.END

    try:
        await context.bot.delete_message(query.message.chat_id, query.message.message_id)
    except Exception:
        pass  # Ignore errors if message is already deleted

    path_stack = context.user_data.get('path_stack', [])
    if not path_stack:
        await query.message.reply_text("❌ No current folder selected.")
        return ConversationHandler.END

    context.user_data['new_folder_path'] = path_stack[-1]
    await query.message.reply_text("📂 Please enter the name of the new folder:")
    return NEW_FOLDER

async def handle_new_folder_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in sessions:
        await update.message.reply_text("❌ Please login first using /login.")
        return ConversationHandler.END

    folder_name = update.message.text.strip()
    # Sanitize folder name to prevent invalid characters
    folder_name = re.sub(r'[<>:"/\\|?*]', '', folder_name)
    if not folder_name:
        await update.message.reply_text("❌ Invalid folder name. Please enter a valid name.")
        return NEW_FOLDER

    username_val = sessions[user_id]
    user_folder = context.user_data.get('new_folder_path', f"/DATA/Users/{username_val}")
    new_folder_path = os.path.join(user_folder, folder_name)

    try:
        if os.path.exists(new_folder_path):
            creation_time = os.path.getctime(new_folder_path)
            formatted_creation_time = datetime.fromtimestamp(creation_time, tz=IST).strftime("%d-%m-%Y %I:%M %p")

            keyboard = [[InlineKeyboardButton("❌ Cancel", callback_data="cancel_new_folder")]]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(
                f"The destination already contains a folder named {folder_name}\n"
                f"Date created - {formatted_creation_time}\n\n"
                "📂 Please enter a different folder name or cancel the process:",
                reply_markup=reply_markup
            )
            return NEW_FOLDER

        os.makedirs(new_folder_path)
        await update.message.reply_text(f"✅ Folder '{folder_name}' created successfully.")

        # Refresh the current folder instead of resetting to main directory
        current_path = user_folder
        path_stack = context.user_data.get('path_stack', [])
        if current_path not in path_stack:
            path_stack.append(current_path)
        context.user_data['path_stack'] = path_stack

        keyboard = list_directory_contents(current_path, context)
        if not keyboard:
            keyboard = [[InlineKeyboardButton("📂 Folder is empty", callback_data="noop")]]

        main_directory = f"/DATA/Users/{username_val}"
        current_uid = next((k for k, v in context.user_data.get("path_map", {}).items() if v == current_path), None)
        if current_path == main_directory:
            keyboard.insert(0, [InlineKeyboardButton("🆕 New Folder", callback_data="new_folder")])
        else:
            if current_uid:
                keyboard.append([
                    InlineKeyboardButton("✏️ Rename Folder", callback_data=f"rename_folder|{current_uid}"),
                    InlineKeyboardButton("🚚 Move Folder", callback_data=f"move_folder|{current_uid}")
                ])
                keyboard.append([
                    InlineKeyboardButton("🚮 Delete This Folder", callback_data=f"delete_folder|{current_uid}"),
                    InlineKeyboardButton("🆕 New Folder", callback_data="new_folder")
                ])
            if len(path_stack) > 1:
                keyboard.insert(0, [InlineKeyboardButton("⬅️ Back", callback_data="back")])

        keyboard.append([InlineKeyboardButton("🔄 Refresh", callback_data="refresh")])

        await context.bot.send_message(
            chat_id=update.message.chat_id,
            text=f"📂 Folder: {os.path.basename(current_path)}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except PermissionError:
        await update.message.reply_text(f"❌ Permission denied: Cannot create folder '{folder_name}'.")
    except OSError as e:
        await update.message.reply_text(f"❌ OS Error: {str(e)}")
    except Exception as e:
        await update.message.reply_text(f"❌ Unexpected error: {str(e)}")

    return ConversationHandler.END

async def cancel_new_folder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query is None or query.from_user is None or query.message is None:
        logger.error("CallbackQuery, from_user, or message was None in cancel_new_folder")
        return ConversationHandler.END

    await query.answer()

    user_id = query.from_user.id
    chat_id = query.message.chat.id 

    await myfiles(update, context)

    return ConversationHandler.END

########Refresh###########
##########################

    if data == "refresh":
        path_stack = context.user_data.get('path_stack', [])
        if not path_stack:
            return

        current_path = path_stack[-1]
        keyboard = list_directory_contents(current_path, context)

        if not keyboard:
            keyboard = [[InlineKeyboardButton("📂 Folder is empty", callback_data="noop")]]

        user_id = query.from_user.id
        username_val = sessions.get(user_id)
        main_directory = f"/DATA/Users/{username_val}"
        
        if current_path == main_directory:
            keyboard.insert(0, [InlineKeyboardButton("🆕 New Folder", callback_data="new_folder")])

        if len(path_stack) > 1:
            keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back")])

        current_uid = next((k for k, v in context.user_data.get("path_map", {}).items() if v == current_path), None)
        if current_uid:
            keyboard.append([InlineKeyboardButton("🚮 Delete This Folder", callback_data=f"delete_folder|{current_uid}")])

        keyboard.append([InlineKeyboardButton("🔄 Refresh", callback_data="refresh")])

        await query.edit_message_text(
            text=f"📂 Folder: {os.path.basename(current_path)}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

#########Delete###########
##########################

    if data == "confirm_delete":
        try:
            path = context.user_data.get("confirm_delete_path")
            item_type = context.user_data.get("confirm_delete_type")
            user_id = query.from_user.id
            username_val = sessions.get(user_id)

            if not is_safe_to_delete(path, username_val):
                await query.edit_message_text("❌ Unsafe or unauthorized deletion attempt blocked.")
                return

            # 🔥 Force delete via sudo rm
            result = subprocess.run(
                ["sudo", "rm", "-rf", path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            if result.returncode != 0:
                raise Exception(result.stderr.decode())

            # Clean context
            context.user_data.pop("confirm_delete_path", None)
            context.user_data.pop("confirm_delete_type", None)

            # Back to parent
            path_stack = context.user_data.get('path_stack', [])
            if len(path_stack) > 1:
                path_stack.pop()
            current_path = path_stack[-1] if path_stack else f"/DATA/Users/{username_val}"
            context.user_data['path_stack'] = path_stack

            keyboard = list_directory_contents(current_path, context)
            if not keyboard:
                keyboard = [[InlineKeyboardButton("📂 Folder is empty", callback_data="noop")]]

            if len(path_stack) > 1:
                keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back")])

            current_uid = next((k for k, v in context.user_data.get("path_map", {}).items() if v == current_path), None)
            if current_uid:
                keyboard.append([InlineKeyboardButton("🚮 Delete This Folder", callback_data=f"delete_folder|{current_uid}")])
 
            keyboard.append([InlineKeyboardButton("🔄 Refresh", callback_data="refresh")])

            await query.edit_message_text(
                text="✅ File or folder deleted successfully.\n\n📂 Folder: {os.path.basename(current_path)}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            await query.edit_message_text(f"❌ Error deleting file: {str(e)}")
        return

    elif data == "cancel_delete":
        # Restore previous folder view exactly how it was before delete prompt
        path_stack = context.user_data.get("path_stack", [])
        if not path_stack:
            await query.edit_message_text("❌ Cannot restore previous menu.")
            return

        current_path = path_stack[-1]

        # Generate fresh keyboard options to include delete button
        keyboard = list_directory_contents(current_path, context)
        if not keyboard:
            keyboard = [[InlineKeyboardButton("📂 Folder is empty", callback_data="noop")]]

        if len(path_stack) > 1:
            keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back")])

        current_uid = next((k for k, v in context.user_data.get("path_map", {}).items() if v == current_path), None)
        if current_uid:
            keyboard.append([InlineKeyboardButton("🚮 Delete This Folder", callback_data=f"delete_folder|{current_uid}")])

        keyboard.append([InlineKeyboardButton("🔄 Refresh", callback_data="refresh")])

        await query.edit_message_text(
            text=f"📂 Folder: {os.path.basename(current_path)}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return


    try:
        action, uid = data.split("|", 1)
    except ValueError:
        await query.edit_message_text("⚠️ Invalid action.")
        return

    path = context.user_data.get("path_map", {}).get(uid)
    if not path or not os.path.exists(path):
        await query.edit_message_text("❌ Path not found.")
        return

    if action == "open":
        context.user_data['path_stack'].append(path)
        current_path = path
        keyboard = list_directory_contents(current_path, context)
        if not keyboard:
            keyboard = [[InlineKeyboardButton("📂 Folder is empty", callback_data="noop")]]

        path_stack = context.user_data.get("path_stack", [])
        if len(path_stack) > 1:
            keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back")])

        current_uid = next((k for k, v in context.user_data.get("path_map", {}).items() if v == current_path), None)
        if current_uid:
            keyboard.append([InlineKeyboardButton("🚮 Delete This Folder", callback_data=f"delete_folder|{current_uid}")])

        keyboard.append([InlineKeyboardButton("🔄 Refresh", callback_data="refresh")])
        await query.edit_message_text(
            text=f"📂 Folder: {os.path.basename(current_path)}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    elif action == "file":
        try:
            size_str = format_size(os.path.getsize(path))
        except Exception:
            size_str = "Unknown size"

        # Check if file is compressed
        compressed_extensions = ['.zip', '.rar', '.7z', '.tar.gz', '.tar.bz2']
        is_compressed = any(path.lower().endswith(ext) for ext in compressed_extensions)

        keyboard = []
        if is_compressed:
            keyboard = [
                [InlineKeyboardButton("⬅️ Back", callback_data="back")],
                [
                    InlineKeyboardButton("✏️ Rename", callback_data=f"rename|{uid}"),
                    InlineKeyboardButton("🚚 Move", callback_data=f"move_file|{uid}")
                ],
                [
                    InlineKeyboardButton("🗑️ Delete", callback_data=f"delete_file|{uid}"),
                    InlineKeyboardButton("📤 Extract", callback_data=f"extract|{uid}")
                ],
                [InlineKeyboardButton("📂 Extract to Folder", callback_data=f"extract_to_folder|{uid}")]
            ]
        else:
            keyboard = [
                [InlineKeyboardButton("⬅️ Back", callback_data="back")],
                [
                    InlineKeyboardButton("✏️ Rename", callback_data=f"rename|{uid}"),
                    InlineKeyboardButton("🚚 Move", callback_data=f"move_file|{uid}")
                ],
                [
                    InlineKeyboardButton("🗑️ Delete", callback_data=f"delete_file|{uid}"),
                    InlineKeyboardButton("🔒 Compress", callback_data=f"compress|{uid}")
                ]
            ]

        await query.edit_message_text(
            text=f"📄 File: {os.path.basename(path)}\n📦 Size: {size_str}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    elif action in ["delete_file", "delete_folder"]:
        confirm_type = "file" if action == "delete_file" else "folder"
        context.user_data["confirm_delete_path"] = path
        context.user_data["confirm_delete_type"] = confirm_type

        filename = os.path.basename(path)
        keyboard = [
            [InlineKeyboardButton("✅ Yes, delete", callback_data="confirm_delete"),
             InlineKeyboardButton("❌ No, go back", callback_data="cancel_delete")]
        ]
        await query.edit_message_text(
            text=f"⚠️ Do you really want to delete `{filename}`?",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

def is_safe_to_delete(path, username_val):
    """Ensure path is within /DATA/Users/{username} and not the root folder."""
    root_dir = os.path.abspath(f"/DATA/Users/{username_val}")
    target_path = os.path.abspath(path)

    # Block root or anything above it
    if target_path == root_dir:
        return False

    # Block anything outside the user's folder
    if not target_path.startswith(root_dir + os.sep):
        return False

    return True

########Extraction########
##########################

async def extract_archive(context, chat_id, file_path, extraction_dir, overwrite=False):
    user_id = chat_id
    async with user_locks[user_id]:
        file_name = os.path.basename(file_path)
        ext = Path(file_path).suffix.lower()
        start_time = time.time()

        try:
            os.makedirs(extraction_dir, exist_ok=True)
            subprocess.run(["sudo", "chmod", "-R", "777", extraction_dir], check=False)

            msg = await context.bot.send_message(chat_id, f"📤 Extracting `{file_name}`...", parse_mode="Markdown")

            # -------- ZIP ----------
            if ext == '.zip':
                with zipfile.ZipFile(file_path, 'r') as zf:
                    if not overwrite:
                        for info in zf.infolist():
                            target_path = os.path.join(extraction_dir, info.filename)
                            if os.path.exists(target_path):
                                os.remove(target_path)
                    total_size = sum(info.file_size for info in zf.infolist())
                    extracted_size = 0
                    last_update = start_time

                    for info in zf.infolist():
                        zf.extract(info, extraction_dir)
                        extracted_size += info.file_size
                        if time.time() - last_update >= 2:
                            await update_extraction_progress(context, chat_id, msg.message_id, extracted_size, total_size, start_time, file_name)
                            last_update = time.time()

            # -------- RAR using unrar CLI ----------
            elif ext == '.rar':
                result = subprocess.run(["unrar", "x", "-o+", file_path, extraction_dir], capture_output=True, text=True)
                if result.returncode != 0:
                    raise Exception(result.stderr)

            # -------- 7Z ----------
            elif ext == '.7z':
                with py7zr.SevenZipFile(file_path, 'r') as szf:
                    if not overwrite:
                        for finfo in szf.files:
                            target_path = os.path.join(extraction_dir, finfo.filename)
                            if os.path.exists(target_path):
                                os.remove(target_path)
                    szf.extractall(extraction_dir)

            # -------- TAR ----------
            elif ext in ('.tar.gz', '.tar.bz2'):
                mode = 'r:gz' if ext == '.tar.gz' else 'r:bz2'
                with tarfile.open(file_path, mode) as tf:
                    if not overwrite:
                        for info in tf.getmembers():
                            target_path = os.path.join(extraction_dir, info.name)
                            if os.path.exists(target_path):
                                os.remove(target_path)
                    tf.extractall(extraction_dir)

            else:
                await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=f"❌ Unsupported archive format: {ext}")
                return True

            await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=f"✅ Extraction of `{file_name}` completed successfully!")
            return True

        except Exception as e:
            await context.bot.edit_message_text(chat_id=chat_id, message_id=msg.message_id, text=f"❌ Extraction failed: {str(e)}")
            return True

#########Rename###########
##########################

async def start_rename(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    await query.answer()

    try:
        action, uid = query.data.split("|", 1)
    except ValueError:
        await query.edit_message_text("⚠️ Invalid rename request.")
        return ConversationHandler.END

    path = context.user_data.get("path_map", {}).get(uid)
    if not path or not os.path.exists(path):
        await query.edit_message_text("❌ File or folder not found.")
        return ConversationHandler.END

    context.user_data["rename_uid"] = uid
    context.user_data["is_folder"] = action == "rename_folder"
    item_type = "folder" if action == "rename_folder" else "file"
    escaped_name = escape_markdown(os.path.basename(path))
    await query.edit_message_text(
        f"📄 Current {item_type}: `{escaped_name}`\n\n"
        f"✏️ Enter the new name {'(without extension)' if item_type == 'folder' else '(e.g., `newfile.mp4`)'}:",
        parse_mode="Markdown"
    )
    return RENAME

async def handle_rename_input(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    new_name = update.message.text.strip()

    # Block command-like messages
    if new_name.startswith("/"):
        await update.message.reply_text(
            "⚠️ Please enter a *valid name* like `newfolder` or `movie.mp4`, not a command.",
            parse_mode="Markdown"
        )
        return RENAME

    uid = context.user_data.get("rename_uid")
    if not uid or "path_map" not in context.user_data:
        await update.message.reply_text("❌ Rename session expired. Please try again.")
        return ConversationHandler.END

    old_path = context.user_data["path_map"].get(uid)
    if not old_path or not os.path.exists(old_path):
        await update.message.reply_text("❌ Original file or folder not found.")
        return ConversationHandler.END

    dir_path = os.path.dirname(old_path)
    old_filename = os.path.basename(old_path)
    is_folder = context.user_data.get("is_folder", False)

    # Handle file renaming (preserve extension if omitted)
    if not is_folder:
        if "." not in new_name:
            ext = os.path.splitext(old_filename)[-1]
            new_name += ext

    new_path = os.path.join(dir_path, new_name)

    if os.path.exists(new_path):
        await update.message.reply_text("⚠️ A file or folder with that name already exists. Try a different name.")
        return RENAME

    try:
        os.rename(old_path, new_path)
        context.user_data["path_map"][uid] = new_path
        item_type = "folder" if is_folder else "file"
        await update.message.reply_text(f"✅ {item_type.capitalize()} renamed successfully to `{new_name}`", parse_mode="Markdown")

        await myfiles(update, context)

    except Exception as e:
        await update.message.reply_text(f"❌ Failed to rename: {str(e)}")

    return ConversationHandler.END

#######Move files#########
##########################

async def start_move_folder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    try:
        _, uid = query.data.split("|", 1)
    except ValueError:
        await query.edit_message_text("⚠️ Invalid move request.")
        return ConversationHandler.END

    path = context.user_data.get("path_map", {}).get(uid)
    if not path or not os.path.exists(path) or not os.path.isdir(path):
        await query.edit_message_text("❌ Folder not found.")
        return ConversationHandler.END

    context.user_data["move_folder_uid"] = uid
    context.user_data["move_folder_path"] = path
    context.user_data["current_mode"] = "move_folder"
    base_path = f"/DATA/Users/{sessions[query.from_user.id]}"
    context.user_data["move_path_stack"] = [base_path]

    await query.edit_message_text(
        f"📂 Moving folder: {os.path.basename(path)}\n\nSelect a target folder to move to:"
    )
    await show_move_folder_menu(update, context)
    return MOVE_FOLDER

async def show_move_folder_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query if update.callback_query else None
    if query:
        await query.answer()
        chat_id = query.message.chat_id
    else:
        chat_id = update.message.chat_id

    user_id = update.message.from_user.id if update.message else query.from_user.id
    if user_id not in sessions:
        await context.bot.send_message(chat_id, "❌ Please login first using /login.")
        return

    path_stack = context.user_data.get("move_path_stack", [])
    if not path_stack:
        await context.bot.send_message(chat_id, "❌ Cannot navigate folders.")
        return

    current_path = path_stack[-1]
    if not os.path.exists(current_path):
        await context.bot.send_message(chat_id, f"❌ Error: Folder `{current_path}` does not exist.")
        return

    keyboard = []
    for folder in sorted(os.listdir(current_path)):
        full_path = os.path.join(current_path, folder)
        if os.path.isdir(full_path) and folder.strip():
            uid = register_path(context, full_path)
            keyboard.append([InlineKeyboardButton(f"📁 {folder}", callback_data=f"navigate_move|{uid}")])

    keyboard.append([InlineKeyboardButton("🚚 Move Here", callback_data="move_here")])
    if len(path_stack) > 1:
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="navigate_move_back")])

    mode = context.user_data.get("current_mode")
    item_type = "file" if mode == "move_file" else "folder"
    source_path = context.user_data.get(f"move_{item_type}_path", current_path)
    text = f"📂 Folder: `{os.path.basename(current_path)}`\n\nSelect a folder to move `{os.path.basename(source_path)}` to."
    if query:
        await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def navigate_move_folder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        logger.error("❌ Callback query missing in navigate_move_folder.")
        return

    await query.answer()
    user_id = query.from_user.id
    action, uid = query.data.split("|", 1)

    if action != "navigate_move":
        await query.edit_message_text("❌ Invalid action.")
        return

    new_path = context.user_data.get("path_map", {}).get(uid)
    if not new_path or not os.path.exists(new_path):
        await query.edit_message_text("❌ Folder not found.")
        return

    user_base_dir = os.path.abspath(f"/DATA/Users/{sessions[user_id]}")
    if not os.path.abspath(new_path).startswith(user_base_dir):
        await query.edit_message_text("❌ Access denied.")
        return

    context.user_data["move_path_stack"].append(new_path)
    await show_move_folder_menu(update, context)

async def navigate_move_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    path_stack = context.user_data.get("move_path_stack", [])
    if len(path_stack) > 1:
        path_stack.pop()
    current_path = path_stack[-1] if path_stack else None

    if not current_path or not os.path.exists(current_path):
        await query.edit_message_text("❌ Path not found.")
        return

    await show_move_folder_menu(update, context)

async def move_here(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    mode = context.user_data.get("current_mode")
    if mode == "move_folder":
        source_path = context.user_data.get("move_folder_path")
        uid = context.user_data.get("move_folder_uid")
    elif mode == "move_file":
        source_path = context.user_data.get("move_file_path")
        uid = context.user_data.get("move_file_uid")
    else:
        await query.edit_message_text("❌ Invalid move mode.")
        return ConversationHandler.END

    if not source_path or not uid or not os.path.exists(source_path):
        await query.edit_message_text("❌ Source not found.")
        return ConversationHandler.END

    target_path = context.user_data.get("move_path_stack", [])[-1]
    if not target_path or not os.path.exists(target_path):
        await query.edit_message_text("❌ Target folder not found.")
        return ConversationHandler.END

    # Prevent moving into itself (for folders)
    if os.path.isdir(source_path) and os.path.abspath(target_path).startswith(os.path.abspath(source_path)):
        await query.edit_message_text("❌ Cannot move a folder into itself or its subdirectories.")
        return MOVE_FOLDER

    new_path = os.path.join(target_path, os.path.basename(source_path))
    if os.path.exists(new_path):
        await query.edit_message_text("⚠️ A file or folder with that name already exists in the target location.")
        return MOVE_FOLDER

    try:
        shutil.move(source_path, new_path)
        context.user_data["path_map"][uid] = new_path
        item_type = "file" if mode == "move_file" else "folder"
        await query.edit_message_text(
            f"✅ {item_type.capitalize()} moved successfully to `{os.path.basename(target_path)}`",
            parse_mode="Markdown"
        )
        await myfiles(update, context)
    except Exception as e:
        await query.edit_message_text(f"❌ Failed to move {item_type}: {str(e)}")

    return ConversationHandler.END

################################
# Settings
################################

BROADCAST_SETTINGS_FILE = "broadcast_settings.json"

def load_broadcast_settings():
    if os.path.exists(BROADCAST_SETTINGS_FILE):
        with open(BROADCAST_SETTINGS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_broadcast_settings(data):
    with open(BROADCAST_SETTINGS_FILE, "w") as f:
        json.dump(data, f)

broadcast_settings = load_broadcast_settings()

async def settings(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    user_key = str(user_id)

    # Skip the login check for user_id 1074000261
    if user_id != 1074000261 and user_key not in broadcast_settings:
        await update.message.reply_text(
            "🔒 One-time login is required by any of your accounts to unlock settings. Please use /login to proceed."
        )
        return

    # Initialize broadcast settings for the user if not already set
    if user_key not in broadcast_settings:
        broadcast_settings[user_key] = {"receive_updates": user_id == 1074000261}
        save_broadcast_settings(broadcast_settings)

    broadcast_pref = broadcast_settings[user_key].get("receive_updates", user_id == 1074000261)
    updates_status = "ON" if broadcast_pref else "OFF"

    keyboard = []
    text = "⚙️ *Bot Settings:*"

    if user_id in sessions:
        # Logged-in user: Show both default download and bot updates options
        default_info = context.user_data.get("default_download", {"enabled": False})
        status = "ON" if default_info.get("enabled") else "OFF"
        keyboard.append([InlineKeyboardButton(f"📥 Default Download Location: {status}", callback_data="toggle_default_dl")])
        text += "\n\nManage your download location and bot update preferences."
    else:
        # Logged-out user: Show only bot updates option
        text += "\n\nYou are not logged in. Log in with /login to manage download locations."

    keyboard.append([InlineKeyboardButton(f"🤖 Receive Bot Updates: {updates_status}", callback_data="toggle_receive_updates")])

    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
DEFAULTS_FILE = "default_paths.json"

def load_default_settings():
    if os.path.exists(DEFAULTS_FILE):
        with open(DEFAULTS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_default_settings(data):
    with open(DEFAULTS_FILE, "w") as f:
        json.dump(data, f)

default_settings = load_default_settings()

async def handle_toggle_default_dl(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user_key = str(user_id)

    # Load current user status
    user_setting = default_settings.get(user_key, {"enabled": False})

    if user_setting["enabled"]:
        # Toggle OFF
        default_settings[user_key] = {"enabled": False, "path": None}
        save_default_settings(default_settings)

        context.user_data["default_download"] = {"enabled": False}
        await query.edit_message_text(
            "⚙️ Here you can change bot settings:\n\nDefault Download Location: OFF",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("📥 Default Download Location: OFF", callback_data="toggle_default_dl")]
            ])
        )
    else:
        # Toggle ON flow - pick folder
        context.user_data["setting_default_path"] = True
        context.user_data["current_mode"] = "set_default" 
        base_path = f"/DATA/Users/{sessions[user_id]}"
        context.user_data["path_stack"] = [base_path]

        await query.edit_message_text("📂 Select a folder to set as your default download location.")
        await show_download_folder_menu(update, context)

async def handle_toggle_receive_updates(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    user_key = str(user_id)

    # Ensure broadcast settings are initialized
    if user_key not in broadcast_settings:
        broadcast_settings[user_key] = {"receive_updates": user_id == 1074000261}
        save_broadcast_settings(broadcast_settings)

    # Toggle broadcast preference
    current_pref = broadcast_settings[user_key].get("receive_updates", user_id == 1074000261)
    new_pref = not current_pref
    broadcast_settings[user_key] = {"receive_updates": new_pref}
    save_broadcast_settings(broadcast_settings)

    # Prepare updated settings UI
    updates_status = "ON" if new_pref else "OFF"
    keyboard = []
    text = "⚙️ *Bot Settings:*"

    if user_id in sessions:
        # Logged-in user: Show both options
        default_info = context.user_data.get("default_download", {"enabled": False})
        status = "ON" if default_info.get("enabled") else "OFF"
        keyboard.append([InlineKeyboardButton(f"📥 Default Download Location: {status}", callback_data="toggle_default_dl")])
        text += "\n\nManage your download location and bot update preferences."
    else:
        # Logged-out user: Show only bot updates option
        text += "\n\nYou are not logged in. Log in with /login to manage download locations."

    keyboard.append([InlineKeyboardButton(f"🤖 Receive Bot Updates: {updates_status}", callback_data="toggle_receive_updates")])

    await query.edit_message_text(
        text,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def broadcast_command(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id != BROADCAST_ADMIN_ID:
        await update.message.reply_text("❌ You are not authorized to use this command.")
        return ConversationHandler.END

    # Terminate any ongoing conversation
    context.user_data.clear()  # Clear user_data to reset conversation state
    broadcast_mode[user_id] = True

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Cancel Broadcast", callback_data="cancel_broadcast")]
    ])

    await update.message.reply_text(
        "📣 *Broadcast Mode Activated!*\n\nSend the message you want to broadcast.\n"
        "_You can send text, photos, videos, gifs, or files._",
        parse_mode="Markdown",
        reply_markup=keyboard
    )
    return ConversationHandler.END  # Ensure the handler ends any conversation

async def cancel_broadcast(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if broadcast_mode.get(user_id):
        broadcast_mode.pop(user_id)
        await query.edit_message_text("❌ Broadcast cancelled.")

async def handle_broadcast_message(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id

    if user_id != BROADCAST_ADMIN_ID or not broadcast_mode.get(user_id):
        return

    # Track last broadcast message
    broadcast_last_message_id[user_id] = update.message.message_id
    broadcast_mode.pop(user_id, None)

    message = update.message
    sent_count = 0
    failed_count = 0

    for target_id, prefs in broadcast_settings.items():
        if prefs.get("receive_updates"):
            try:
                await message.copy(chat_id=int(target_id))
                sent_count += 1
            except:
                failed_count += 1

    await update.message.reply_text(
        f"✅ Broadcast sent to {sent_count} user(s).\n❌ Failed to send to {failed_count}."
    )

################################
# Application Setup
################################
def setup_handlers(application: Application) -> None:
    """Setup all handlers for the application."""
    # Restore sessions on startup
    restore_sessions(application)

    application.add_error_handler(error_handler)

    # Basic commands
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('logout', logout))
    application.add_handler(CommandHandler('storage', storage))
    application.add_handler(CommandHandler('myfiles', myfiles))
    application.add_handler(CommandHandler('cancel', cancel))
    application.add_handler(CommandHandler("account", accounts))
    application.add_handler(CommandHandler("settings", settings))
    # Move broadcast handler here to take precedence
    application.add_handler(CommandHandler("broadcast", broadcast_command))
    application.add_handler(CommandHandler("link", link_handler))

    # New Folder Conversation Handler
    new_folder_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_new_folder, pattern="^new_folder$")],
        states={
            NEW_FOLDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_new_folder_input)],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            CallbackQueryHandler(cancel_new_folder, pattern="^cancel_new_folder$"),
        ],
        allow_reentry=True
    )
    application.add_handler(new_folder_conv)

    # Rename Conversation Handler (for both files and folders)
    rename_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_rename, pattern=r"^(rename|rename_folder)\|")],
        states={
            RENAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_rename_input)],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            CommandHandler('start', start),
            CommandHandler('logout', logout),
            CommandHandler('help', help_command),
        ],
        allow_reentry=True
    )
    application.add_handler(rename_conv)

    # Move Folder Conversation Handler
    move_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_move_folder, pattern=r"^move_folder\|")],
        states={
            MOVE_FOLDER: [
                CallbackQueryHandler(navigate_move_folder, pattern=r"^navigate_move\|"),
                CallbackQueryHandler(navigate_move_back, pattern="^navigate_move_back$"),
                CallbackQueryHandler(move_here, pattern="^move_here$")
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            CommandHandler('start', start),
            CommandHandler('logout', logout),
            CommandHandler('help', help_command),
        ],
        allow_reentry=True
    )
    application.add_handler(move_conv)

    # Static and common callback interactions (main menu, file ops)
    application.add_handler(CallbackQueryHandler(
        myfiles_callback,
        pattern=r"^(open\|.*|file\|.*|download_file\|.*|back|noop|refresh|delete_file\|.*|delete_folder\|.*|confirm_delete|cancel_delete|move_file\|.*|extract\|.*|extract_to_folder\|.*|overwrite_extract\|.*|skip_extract|compress\|.*|compress_format\|.*|cancel_compress|new_folder)$"
    ))

    # Dynamic extract and move navigation/actions
    application.add_handler(CallbackQueryHandler(
        myfiles_callback,
        pattern=r"^(extract_nav\|.*|extract_nav_back|extract_execute|move_nav\|.*|move_nav_back|move_execute)$"
    ))


    # Login Conversation Handler
    login_conv_handler = ConversationHandler(
        entry_points=[CommandHandler('login', login)],
        states={
            USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, username)],
            PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, password)],
        },
        fallbacks=[
            CommandHandler('cancel', cancel),
            CommandHandler('start', start),
            CommandHandler('help', help_command),
            CommandHandler('myfiles', myfiles),
            CommandHandler('logout', logout),
            CommandHandler('login', login),
            # Removed broadcast fallback since it's handled at a higher level
            MessageHandler(filters.Regex(r'^/.*') & ~filters.Regex(r'^/(cancel)$'), lambda update, context: ConversationHandler.END),
        ],
        allow_reentry=True
    )
    application.add_handler(login_conv_handler)

    # Password change conversation
    pw_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(handle_change_pw_prompt, pattern="^change_pw$")],
        states={
            CHANGING_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_new_password)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    application.add_handler(pw_conv)

    application.add_handler(MessageHandler(filters.ALL & filters.User(user_id=BROADCAST_ADMIN_ID), handle_broadcast_message))

    # File/link message handler (always last)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, link_handler))

    # Download button callbacks
    application.add_handler(CallbackQueryHandler(download_button_handler, pattern="^(start_download|cancel_start)$"))
    application.add_handler(CallbackQueryHandler(cancel_active_download, pattern="^cancel_dl_active$"))

    application.add_handler(CallbackQueryHandler(navigate_folder, pattern="^navigate\\|.*$"))
    application.add_handler(CallbackQueryHandler(show_download_folder_menu, pattern="^open_download_menu$"))
    application.add_handler(CallbackQueryHandler(set_download_location, pattern="^download_here$"))
    application.add_handler(CallbackQueryHandler(handle_toggle_default_dl, pattern="^toggle_default_dl$"))
    application.add_handler(CallbackQueryHandler(navigate_back, pattern="^navigate_back$"))
    application.add_handler(CallbackQueryHandler(handle_toggle_receive_updates, pattern="^toggle_receive_updates$"))
    application.add_handler(CallbackQueryHandler(cancel_broadcast, pattern="^cancel_broadcast$"))
    application.add_handler(CallbackQueryHandler(refresh_storage, pattern="^refresh_storage$"))
    application.add_handler(CallbackQueryHandler(close_storage, pattern="^close_storage$"))
    application.add_handler(CallbackQueryHandler(cancel_uploading, pattern="^cancel_uploading\\|"))
    application.add_handler(CallbackQueryHandler(navigate_move_folder, pattern="^navigate_move\\|.*$"))
    application.add_handler(CallbackQueryHandler(navigate_move_back, pattern="^navigate_move_back$"))
    application.add_handler(CallbackQueryHandler(move_here, pattern="^move_here$"))

################################
# Link Download/Upload Handlers
################################

def escape_markdown(text):
    return re.sub(r'([_*`])', r'\\\1', text)

URL_PATTERN = re.compile(r"^https?://.*")

def sanitize_callback_data(data):
    return data.replace('"', "").replace("'", "").replace("\n", "").replace(".", "_").strip()

async def link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text.strip()
    
    if user_id not in sessions:
        await update.message.reply_text("❌ Please login first using /login.")
        return

    if text == "/link":
        await update.message.reply_text(
            "📌 To use this feature, send a valid link after the command.\n\n"
            "✅ Example:\n"
            "`/link https://example.com/file.zip`\n\n"
            "This will start the link processing and present download options. "
            "Please provide a proper link to continue.",
            parse_mode="Markdown"
        )
        return

    if not text.startswith("/link "):
        return

    url = text[6:].strip()
    
    if not URL_PATTERN.match(url):
        await update.message.reply_text("❌ Invalid URL. Please provide a valid link.")
        return

    context.user_data["link_url"] = url
    await handle_link(update, context)

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_key = str(user_id)
    
    if user_key in default_settings:
        context.user_data["default_download"] = default_settings[user_key]
        
    if user_id not in sessions:
        await update.message.reply_text("❌ Please login first using /login.")
        return

    url = context.user_data.get("link_url")
    if not url:
        url = update.message.text.strip()[6:].strip()

    try:
        previous_message_id = context.user_data.get("last_option_msg_id")
        if previous_message_id:
            try:
                await context.bot.delete_message(update.message.chat_id, previous_message_id)
            except Exception:
                pass

        async with aiohttp.ClientSession() as session:
            async with session.head(url, allow_redirects=True) as r:
                if r.status != 200:
                    logger.error(f"Failed to fetch file info - Status code: {r.status}")
                    await update.message.reply_text(f"❌ Failed to fetch file info. Status code: {r.status}")
                    return

                logger.info(f"Headers received: {r.headers}")
                size = r.headers.get("Content-Length")
                content_disposition = r.headers.get("Content-Disposition", "")
                content_type = r.headers.get("Content-Type", "")

                if not size:
                    logger.error("❌ Missing Content-Length header.")
                    await update.message.reply_text("❌ Error: File size not available.")
                    return

                size = int(size)
                if "filename=" in content_disposition:
                    name = content_disposition.split("filename=")[-1].strip('\"\' ')
                else:
                    name = url.split("/")[-1].split("?")[0]
                    if not name or "." not in name:
                        ext = mimetypes.guess_extension(content_type.split(";")[0].strip()) or ".bin"
                        name = f"file_{int(time.time())}{ext}"

                logger.info(f"Detected filename: {name}")
                raw_name = name
                safe_name = sanitize_callback_data(name)
                context.user_data["file_info"] = {
                    "url": url,
                    "name": safe_name,
                    "raw_name": raw_name,
                    "size": size
                }

                default_dl = context.user_data.get("default_download", {})
                default_path = default_dl.get("path")
                if default_dl.get("enabled") and default_path and os.path.exists(default_path):
                    context.user_data["file_info"]["download_path"] = default_path
                    keyboard = [
                        [InlineKeyboardButton("📤 Start Download", callback_data="start_download")],
                        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_start")]
                    ]
                    msg = await context.bot.send_message(
                        chat_id=update.message.chat_id,
                        text=(
                            f"📄 Filename - `{escape_markdown(raw_name)}`\n\n"
                            f"📦 Size - `{format_size(size)}`\n"
                            f"📂 Using your *default download location*"
                        ),
                        parse_mode="Markdown",
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                    context.user_data["last_option_msg_id"] = msg.message_id
                    return

                base_path = f"/DATA/Users/{sessions[user_id]}"
                context.user_data["current_mode"] = "download"
                context.user_data["path_stack"] = [base_path]
                await show_download_folder_menu(update, context)

    except aiohttp.ClientError as e:
        logger.error(f"❌ Network error while fetching file info: {e}")
        await update.message.reply_text("❌ Failed to fetch file info due to a network error.")
    except Exception as e:
        error_details = traceback.format_exc()
        logger.error(f"❌ Unexpected error while fetching file info: {e}\nDetails: {error_details}")
        await update.message.reply_text(f"❌ Error fetching file info: {str(e)}")

async def show_download_folder_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query if update.callback_query else None
    if query:
        await query.answer()
        chat_id = query.message.chat_id
    else:
        chat_id = update.message.chat_id

    user_id = update.message.from_user.id if update.message else query.from_user.id

    if user_id not in sessions:
        await context.bot.send_message(chat_id, "❌ Please login first using /login.")
        return

    path_stack = context.user_data.get("path_stack", [])
    if not path_stack:
        await context.bot.send_message(chat_id, "❌ Cannot navigate folders.")
        return

    current_path = path_stack[-1]
    if not os.path.exists(current_path):
        await context.bot.send_message(chat_id, f"❌ Error: Folder `{current_path}` does not exist.")
        return

    keyboard = []
    for folder in sorted(os.listdir(current_path)):
        full_path = os.path.join(current_path, folder)
        if os.path.isdir(full_path) and folder.strip():
            uid = register_path(context, full_path)
            keyboard.append([InlineKeyboardButton(f"📁 {folder}", callback_data=f"navigate|{uid}")])

    for file in sorted(os.listdir(current_path)):
        full_path = os.path.join(current_path, file)
        if os.path.isfile(full_path):
            keyboard.append([InlineKeyboardButton(f"📄 {file}", callback_data="noop")])

    mode = context.user_data.get("current_mode")

    # Show relevant buttons
    if mode in ["download", "set_default"]:
        keyboard.append([InlineKeyboardButton("📥 Download Here", callback_data="download_here")])

    if len(path_stack) > 1:
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="navigate_back")])


    text = f"📂 Folder: `{os.path.basename(current_path)}`\n\n_Select a folder or choose where to download._"

    if query:
        await query.edit_message_text(text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    else:
        await context.bot.send_message(chat_id=chat_id, text=text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

async def navigate_folder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        logger.error("❌ Callback query missing in navigate_folder.")
        return

    await query.answer()
    user_id = query.from_user.id
    action, uid = query.data.split("|", 1)

    if action != "navigate":
        await query.edit_message_text("❌ Invalid action.")
        return

    new_path = context.user_data.get("path_map", {}).get(uid)
    if not new_path or not os.path.exists(new_path):
        await query.edit_message_text("❌ Folder not found.")
        return

    # ✅ Security check
    user_base_dir = os.path.abspath(f"/DATA/Users/{sessions[user_id]}")
    if not os.path.abspath(new_path).startswith(user_base_dir):
        await query.edit_message_text("❌ Access denied.")
        return

    # ✅ Update stack
    context.user_data["path_stack"].append(new_path)

    # ✅ Route based on current mode
    mode = context.user_data.get("current_mode")
    if mode == "set_default" or context.user_data.get("setting_default_path"):
        context.user_data["current_mode"] = "set_default"
        await show_download_folder_menu(update, context)
    elif mode == "download":
        context.user_data["current_mode"] = "download"
        await show_download_folder_menu(update, context)
    else:
        # fallback to myfiles
        context.user_data["current_mode"] = "myfiles"
        await myfiles_callback(update, context)

async def navigate_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    path_stack = context.user_data.get("path_stack", [])
    if len(path_stack) > 1:
        path_stack.pop()
    current_path = path_stack[-1] if path_stack else None

    if not current_path or not os.path.exists(current_path):
        await query.edit_message_text("❌ Path not found.")
        return

    mode = context.user_data.get("current_mode")
    if mode in ["download", "set_default"]:
        await show_download_folder_menu(update, context)
    else:
        await myfiles_callback(update, context)

async def set_download_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    current_path = context.user_data["path_stack"][-1]

    if context.user_data.get("setting_default_path"):
        # ✅ Save as persistent default download location
        context.user_data["default_download"] = {
            "enabled": True,
            "path": current_path
        }

        user_key = str(user_id)
        default_settings[user_key] = {
            "enabled": True,
            "path": current_path
        }
        save_default_settings(default_settings)

        context.user_data.pop("setting_default_path", None)

        # 🔁 Update settings UI
        keyboard = [
            [InlineKeyboardButton("Default Download Location: ON", callback_data="toggle_default_dl")]
        ]
        await query.edit_message_text(
            "✅ Default download location has been set.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # 🔁 Else — use selected folder for this download only
    file_info = context.user_data.get("file_info", {})
    file_info["download_path"] = current_path
    context.user_data["file_info"] = file_info

    safe_name = escape_markdown(file_info.get("raw_name", "file"))
    await query.edit_message_text(
        f"✅ Download location updated to `{current_path}`\n\n⬇️ Ready to download `{safe_name}`.",
        parse_mode="Markdown"
    )

    keyboard = [
        [InlineKeyboardButton("📤 Start Download", callback_data="start_download")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_start")]
    ]

    msg = await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=(
            f"📄 Filename - `{safe_name}`\n"
            f"📦 Size - `{format_size(file_info.get('size', 0))}`"
        ),
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    context.user_data["last_option_msg_id"] = msg.message_id

async def download_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    data = query.data
    file_info = context.user_data.get("file_info")

    if data == "cancel_start":
        await query.edit_message_text("❌ Process cancelled.")
        return

    if data == "start_download":
        if not file_info:
            await query.edit_message_text("❌ Session expired. Please send the link again.")
            return
        
        safe_name = escape_markdown(file_info['raw_name'])
        msg = await query.edit_message_text(
            f"⬇️ Downloading {safe_name}...",
            parse_mode="Markdown"
        )
        
        # ✅ Generate a unique key for each file being downloaded
        download_id = f"{user_id}_{file_info['raw_name']}"
        
        # ✅ Store separate progress tracking for each download
        download_status[download_id] = {'active': True}
        
        # ✅ Start downloading in parallel
        task = asyncio.create_task(download_file_with_progress(context, query, msg.message_id, file_info, download_id))
        download_tasks[download_id] = task

def ensure_folder_permissions(folder_path):
    """Ensure bot has full access to write files inside any folder."""
    try:
        # Ensure folder exists
        os.makedirs(folder_path, exist_ok=True)
        
        # Check current ownership
        folder_info = os.stat(folder_path)
        owner_id = folder_info.st_uid
        owner_name = subprocess.run(
            ["id", "-nu", str(owner_id)], 
            capture_output=True, 
            text=True
        ).stdout.strip()

        # Change ownership to lucian_knight if needed
        if owner_name != "lucian_knight":
            logger.info(f"Changing ownership of {folder_path} to lucian_knight")
            subprocess.run(
                ["sudo", "chown", "-R", "lucian_knight:lucian_knight", folder_path], 
                check=True
            )
        
        # Set permissions to allow writing
        subprocess.run(
            ["sudo", "chmod", "-R", "755", folder_path], 
            check=True
        )
        logger.info(f"Permissions set for {folder_path}")
    except Exception as e:
        logger.error(f"Failed to set permissions for {folder_path}: {e}")
        raise

async def download_file_with_progress(context, query, message_id, file_info, download_id):
    user_id = query.from_user.id
    url = file_info.get("url", "")
    filename = file_info.get("raw_name", "").strip()
    total = file_info.get("size", 0)
    start_time = time.time()
    downloaded = 0

    # ✅ Get the correct download path within user directory
    base_dir = f"/DATA/Users/{sessions[user_id]}"
    download_path = file_info.get("download_path", base_dir)

    # ✅ Ensure folder exists before modifying permissions
    os.makedirs(download_path, exist_ok=True)

    # ✅ Fix folder permissions before downloading
    ensure_folder_permissions(download_path)

    path = os.path.join(download_path, filename)  # ✅ Correct file path

    CHUNK_SIZE = 64 * 1024  # 64KB
    UPDATE_INTERVAL = 2     # seconds
    last_update = start_time

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=60.0)) as client:
            with open(path, 'wb') as f:
                async with client.stream("GET", url, follow_redirects=True) as response:
                    response.raise_for_status()
                    async for chunk in response.aiter_bytes(chunk_size=CHUNK_SIZE):
                        if not download_status.get(download_id, {}).get("active"):
                            await context.bot.edit_message_text(
                                chat_id=query.message.chat_id,
                                message_id=message_id,
                                text="❌ Download cancelled. Deleting file..."
                            )
                            if os.path.exists(path):
                                os.remove(path)
                            return

                        f.write(chunk)
                        downloaded += len(chunk)

                        current_time = time.time()
                        if current_time - last_update >= UPDATE_INTERVAL or downloaded == total:
                            speed = downloaded / (current_time - start_time)
                            await update_download_progress(
                                update=query,
                                context=context,
                                message_id=message_id,
                                downloaded=downloaded,
                                total=total,
                                speed=speed,
                                start_time=start_time,
                                filename=filename,
                                download_id=download_id
                            )
                            last_update = current_time

        await context.bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=message_id,
            text=f"✅ Download complete! `{filename}`"
        )
    except Exception as e:
        logger.error(f"❌ Download failed: {e}")
        await context.bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=message_id,
            text=f"❌ Error during download: {str(e)}"
        )
        if os.path.exists(path):
            os.remove(path)
    finally:
        download_tasks.pop(download_id, None)
        download_status.pop(download_id, None)

async def cancel_active_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    # ✅ Extract the correct file ID
    file_info = context.user_data.get("file_info")
    if not file_info:
        await query.edit_message_text("❌ No active downloads to cancel.")
        return
    
    download_id = f"{user_id}_{file_info['raw_name']}"

    if download_id in download_status:
        download_status[download_id]['active'] = False
        await query.edit_message_text(f"❌ Download for `{file_info['raw_name']}` cancelled.")

################################
# File Download/Upload Handlers
################################

@app.on_message(pyro_filters.document)
async def handle_file(client: Client, message: types.Message):
    user_id = message.from_user.id
    logger.info(f"Received document from user {user_id}")

    # Login check
    if user_id not in sessions:
        logger.info(f"User {user_id} not logged in")
        if user_id not in login_states:
            await message.reply("❌ You must log in first using /login to upload files.")
        return

    document = message.document
    file_name = document.file_name or "unnamed_file"
    file_size = document.file_size
    file_size_mb = file_size / (1024 * 1024)
    username = sessions.get(user_id, "testuser")
    logger.info(f"Processing file: {file_name}, size: {file_size_mb:.2f} MB, for user: {username}")

    # Ensure user directory exists and has correct permissions
    user_dir = f"/DATA/Users/{username}"
    try:
        ensure_folder_permissions(user_dir)
        logger.info(f"Permissions set for {user_dir}")
    except Exception as e:
        logger.error(f"Failed to set permissions for {user_dir}: {str(e)}")
        await message.reply(f"❌ Failed to set directory permissions: {str(e)}")
        return

    # Prevent file overwrite
    base_name, ext = os.path.splitext(file_name)
    download_path = os.path.join(user_dir, file_name)
    if os.path.exists(download_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{base_name}_{timestamp}{ext}"
        download_path = os.path.join(user_dir, file_name)
        logger.info(f"File exists, using new name: {file_name}")

    # Save file info
    file_sessions[user_id] = {
        "file_name": file_name,
        "file_size": file_size,
        "file_msg": message,
        "path": download_path,
    }
    logger.info(f"Stored file session for user {user_id}: {file_name}")

    buttons = [
        [PyroInlineButton("🚀 Upload to server", callback_data=f"uploadfile:{user_id}")],
        [PyroInlineButton("❌ Cancel", callback_data=f"cancelfile:{user_id}")],
    ]
    await message.reply(
        f"📄 **Filename:** `{file_name}`\n💾 **Size:** `{file_size_mb:.2f} MB`",
        reply_markup=PyroInlineMarkup(buttons)
    )
    logger.info(f"Sent reply with buttons for file: {file_name}")

@app.on_callback_query(pyro_filters.regex(r"^(uploadfile|cancelfile):"))
async def handle_file_upload_actions(client: Client, callback_query: types.CallbackQuery):
    data = callback_query.data
    user_id = callback_query.from_user.id
    logger.info(f"Callback query received from user {user_id}: {data}")

    # Handle cancellation
    if data.startswith("cancelfile:") and str(user_id) in data:
        cancel_tokens[user_id] = True
        if user_id in file_sessions:
            file_sessions.pop(user_id, None)
            await callback_query.message.edit_text("❌ Upload cancelled.")
            logger.info(f"Upload cancelled for user {user_id}")
        if user_id in upload_tasks:
            for token, task in upload_tasks[user_id].items():
                task.cancel()
            await callback_query.answer("⏳ Cancelling upload...")
            logger.info(f"Cancelling active upload tasks for user {user_id}")
        return

    # Handle upload
    if data.startswith("uploadfile:") and str(user_id) in data:
        info = file_sessions.get(user_id)
        if not info:
            await callback_query.answer("❌ No file info found.", show_alert=True)
            logger.warning(f"No file session found for user {user_id}")
            return

        file_msg = info["file_msg"]
        file_name = info["file_name"]
        file_size = info["file_size"]
        download_path = info["path"]
        logger.info(f"Starting upload for file: {file_name}, path: {download_path}")

        cancel_tokens[user_id] = False
        upload_token = f"upload_{uuid.uuid4().hex}"
        upload_tasks.setdefault(user_id, {})[upload_token] = None

        buttons = [[PyroInlineButton("❌ Cancel", callback_data=f"cancelfile:{user_id}")]]
        msg = await callback_query.message.reply(
            f"⬆️ Uploading **{file_name}**...\n[                    ] 0.0%\n\n📊 0MB of {file_size/1024/1024:.2f}MB\n🚀 Speed: 0MB/s\n⏳ ETA: 00:00:00",
            reply_markup=PyroInlineMarkup(buttons)
        )
        logger.info(f"Sent upload progress message for {file_name}")

        start_time = time.time()
        last_update = start_time

        async def progress_callback(current, total):
            nonlocal last_update
            now = time.time()

            if cancel_tokens.get(user_id):
                raise asyncio.CancelledError("Upload cancelled")

            if now - last_update > 2 or current == total:
                percent = (current / total) * 100 if total else 0
                bar_length = 20
                filled_length = int(bar_length * percent // 100)
                progress_bar = "[" + "=" * filled_length + ">" + " " * (bar_length - filled_length - 1) + "]"
                uploaded_mb = current / 1024 / 1024
                total_mb = total / 1024 / 1024
                speed = current / (now - start_time + 1e-6)
                eta = (total - current) / (speed + 1e-6)
                eta_formatted = str(timedelta(seconds=int(eta)))

                status = (
                    f"⬆️ Uploading **{file_name}**...\n"
                    f"{progress_bar} {percent:.1f}%\n\n"
                    f"📊 {uploaded_mb:.2f}MB of {total_mb:.2f}MB\n"
                    f"🚀 Speed: {speed / 1024:.2f}KB/s\n"
                    f"⏳ ETA: {eta_formatted}"
                )
                try:
                    await msg.edit_text(status, reply_markup=PyroInlineMarkup(buttons))
                    logger.debug(f"Updated progress for {file_name}: {percent:.1f}%")
                except Exception as e:
                    logger.warning(f"Failed to update progress: {e}")
                last_update = now

        try:
            task = asyncio.create_task(
                client.download_media(file_msg.document.file_id, file_path=download_path, progress=progress_callback)
            )
            upload_tasks[user_id][upload_token] = task
            await task
            await msg.edit_text(f"✅ File uploaded to server: `{download_path}`")
            logger.info(f"Upload completed for {file_name}")
        except asyncio.CancelledError:
            await msg.edit_text("❌ Upload cancelled. Deleting file...")
            if os.path.exists(download_path):
                os.remove(download_path)
            logger.info(f"Upload cancelled for {file_name}")
        except Exception as e:
            await msg.edit_text(f"❌ Upload failed: {str(e)}")
            logger.error(f"Upload failed for {file_name}: {str(e)}")
        finally:
            file_sessions.pop(user_id, None)
            cancel_tokens.pop(user_id, None)
            upload_tasks.get(user_id, {}).pop(upload_token, None)
            if user_id in upload_tasks and not upload_tasks[user_id]:
                upload_tasks.pop(user_id, None)
            logger.info(f"Cleaned up session for user {user_id}")

################################
# Error Handler
################################

async def error_handler(update: Update, context: CallbackContext) -> None:
    """Log errors caused by updates."""
    logger.error('Update "%s" caused error "%s"', update, context.error)
    if update.callback_query:
        await update.callback_query.answer("An error occurred. Please try again.")
    elif update.message:
        await update.message.reply_text("❌ An error occurred. Please try again.")

################################
# Main Function
################################
bot_id = None

async def init_bot_id():
    global bot_id
    async with app:
        me = await app.get_me()
        bot_id = me.id
    logger.info(f"Bot ID initialized: {bot_id}")

async def run_all():
    global bot_id
    # Create a single event loop for both Pyrogram and PTB
    loop = asyncio.get_event_loop()

    try:
        # Initialize Pyrogram client
        logger.info("Starting Pyrogram client...")
        await app.start()
        me = await app.get_me()
        bot_id = me.id
        logger.info(f"Pyrogram client started successfully. Bot ID: {bot_id}")

        # Initialize PTB application
        logger.info("Starting PTB application...")
        application = Application.builder().token("7984121127:AAGyBslNMIkUEaEd6z2NdhqHSqFIJOGElxQ").build()
        setup_handlers(application)

        await application.initialize()
        await application.start()
        await application.updater.start_polling()
        logger.info("PTB application started successfully.")

        # Keep the bot running until interrupted
        await asyncio.Event().wait()

    except Exception as e:
        logger.error(f"Error in run_all: {str(e)}", exc_info=True)
        raise

    finally:
        # Ensure cleanup for both PTB and Pyrogram
        try:
            if 'application' in locals():
                await application.updater.stop()
                await application.stop()
                await application.shutdown()
                logger.info("PTB application stopped.")
        except Exception as e:
            logger.error(f"Error stopping PTB: {str(e)}")

        try:
            await app.stop()
            logger.info("Pyrogram client stopped.")
        except Exception as e:
            logger.error(f"Error stopping Pyrogram: {str(e)}")

if __name__ == '__main__':
    import asyncio
    asyncio.run(run_all())