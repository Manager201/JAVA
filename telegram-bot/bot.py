import os, re, math, time, uuid, shutil, logging
from datetime import datetime, timedelta
from urllib.parse import urlparse

import aiohttp, aiofiles, requests, httpx, humanize, asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ConversationHandler, CallbackQueryHandler, CallbackContext, ContextTypes, filters

from telethon import TelegramClient, events, Button
from telethon.tl.types import Document, DocumentAttributeFilename
import mimetypes

api_id = 5127578
api_hash = '048b23e17b56163581cefa5131b44bff'

client = TelegramClient('bot_session', api_id, api_hash)

# Globals
sessions = {}         # user_id -> username
login_states = {}     # user_id -> login step
file_sessions = {}    # user_id -> file data
cancel_tokens = {}    # user_id -> cancel flag

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
USERNAME, PASSWORD, RENAME, DOWNLOAD_LINK = range(4)

# Flask API URL
FLASK_API_URL = "http://192.168.1.200:5000/login"

# URL pattern for detection
URL_PATTERN = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

# Telegram file size limits
TELEGRAM_FILE_SIZE_LIMIT = 20 * 1024 * 1024  # 20 MB
TELEGRAM_MAX_FILE_SIZE = 1.5 * 1024 * 1024 * 1024  # 1.5 GB (Telegram's max file size)

# Download status tracking - replace existing with this
download_tasks = {}  # Tracks active download tasks
download_status = {}  # Tracks download status info

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

    for id_, p in context.user_data['path_map'].items():
        if p == path:
            return id_  # Return existing ID if already mapped

    uid = str(uuid.uuid4())[:8]  # short unique ID
    context.user_data['path_map'][uid] = path
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
    except Exception as e:
        print(f"Error reading folder: {e}")
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
    """Update the download progress message"""
    percent = (downloaded / total) * 100
    elapsed = time.time() - start_time
    eta = (total - downloaded) / speed if speed > 0 else 0

    progress_bar = "[" + "=" * int(percent / 5) + ">" + " " * (20 - int(percent / 5)) + "]"

    text = (
        f"⬇️ Downloading {filename}\n\n"
        f"{progress_bar} {percent:.1f}%\n\n"
        f"📊 {format_size(downloaded)} of {format_size(total)}\n"
        f"🚀 Speed: {format_speed(speed)}\n"
        f"⏳ ETA: {format_time(eta)}"
    )

    # Add cancel button if download_id is provided
    reply_markup = None
    if download_id:
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
            return  # No valid chat context

        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Error updating progress: {e}")

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
    if user_id in sessions:
        await update.message.reply_text("❌ You are already logged in. Use /logout to switch accounts.")
        return ConversationHandler.END

    # Clear any old conversation state
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
        user_folder = f"/DATA/Users/{username_val}"
        os.makedirs(user_folder, exist_ok=True)

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
        del sessions[user_id]
        await update.message.reply_text("✅ Successfully logged out!")
    else:
        await update.message.reply_text("❌ You are not logged in.")
    return ConversationHandler.END

# Fallback command: end any active conversation gracefully
async def cancel(update: Update, context: CallbackContext) -> int:
    await update.message.reply_text("⚠️ Login cancelled. Use /login to try again.")
    return ConversationHandler.END

################################
# Storage Management Handlers
################################

def get_folder_size(path):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.isfile(fp):
                total_size += os.path.getsize(fp)
    return total_size

def get_total_storage_details(username_val):
    # Path to user's folder
    user_folder = f"/DATA/Users/{username_val}"
    user_size_bytes = get_folder_size(user_folder)
    user_size_gb = user_size_bytes / (1024**3)

    # Server-wide storage
    total, used, free = shutil.disk_usage("/")
    total_gb = total / (1024**3)
    used_gb = used / (1024**3)
    free_gb = free / (1024**3)
    used_percentage = (used / total) * 100
    free_percentage = (free / total) * 100

    return (
        f"💽 *Storage details:*\n\n"
        f"*User storage details -*\n"
        f"`{username_val}` : *{user_size_gb:.2f}GB*\n\n"
        f"*Total server storage -*\n"
        f"Used: *{used_gb:.0f}GB* of *{total_gb:.0f}GB*\n"
        f"Free: *{free_gb:.0f}GB* of *{total_gb:.0f}GB*\n"
        f"Storage used: *{used_percentage:.2f}%*\n"
        f"Storage free: *{free_percentage:.2f}%*"
    )

async def storage(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id

    if user_id not in sessions:
        await update.message.reply_text("❌ Please login first using /login.")
        return ConversationHandler.END

    username_val = sessions[user_id]
    storage_details = get_total_storage_details(username_val)

    await update.message.reply_text(storage_details, parse_mode="Markdown")
    return ConversationHandler.END

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
# Myfiles setup here
################################

# Entry point for /myfiles command
async def myfiles(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id not in sessions:
        await update.message.reply_text("❌ Please login first using /login.")
        return

    username_val = sessions[user_id]
    user_folder = f"/DATA/Users/{username_val}"
    context.user_data['path_stack'] = [user_folder]  # Stack to keep track of folder history

    keyboard = list_directory_contents(user_folder, context)
    if not keyboard:
        keyboard = [[InlineKeyboardButton("📂 Folder is empty", callback_data="noop")]]

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📂 Your drive files:", reply_markup=reply_markup)


# Callback to handle folder and file navigation
async def myfiles_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "noop":
        return

    if data == "back":
        path_stack = context.user_data.get('path_stack', [])
        if len(path_stack) > 1:
            path_stack.pop()
        context.user_data['path_stack'] = path_stack
        current_path = path_stack[-1]

        keyboard = list_directory_contents(current_path, context)
        if not keyboard:
            keyboard = [[InlineKeyboardButton("📂 Folder is empty", callback_data="noop")]]
        if len(path_stack) > 1:
            keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back")])

        folder_name = os.path.basename(current_path) or "Your drive files"
        await query.edit_message_text(
            f"📂 Folder: {folder_name}" if len(path_stack) > 1 else "📂 Your drive files:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Step 4: Parse action and ID (NOT full path anymore)
    try:
        action, uid = data.split("|", 1)
    except ValueError:
        await query.edit_message_text("⚠️ Invalid action.")
        return

    path = context.user_data.get("path_map", {}).get(uid)
    if not path:
        await query.edit_message_text("❌ Path not found.")
        return

    if action == "open":
        context.user_data['path_stack'].append(path)
        keyboard = list_directory_contents(path, context)
        if not keyboard:
            keyboard = [[InlineKeyboardButton("📂 Folder is empty", callback_data="noop")]]
        keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data="back")])
        await query.edit_message_text(f"📂 Folder: {os.path.basename(path)}", reply_markup=InlineKeyboardMarkup(keyboard))

    elif action == "file":
        try:
            size = os.path.getsize(path)
            size_str = format_size(size)
        except Exception as e:
            size_str = "❌ Error reading size"

        keyboard = [
            [InlineKeyboardButton("✏️ Rename", callback_data=f"rename|{uid}")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back")]
        ]
        await query.edit_message_text(
            f"📄 File: {os.path.basename(path)}\n📦 Size: {size_str}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )



################################
# Application Setup
################################

def setup_handlers(application: Application) -> None:
    """Setup all handlers for the application"""
    application.add_error_handler(error_handler)

    # Basic commands
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))
    application.add_handler(CommandHandler('logout', logout))
    application.add_handler(CommandHandler('storage', storage))
    application.add_handler(CommandHandler('myfiles', myfiles))
    application.add_handler(CommandHandler('cancel', cancel))  # Optional but useful

    # File/folder navigation
    application.add_handler(CallbackQueryHandler(myfiles_callback, pattern="^(open|file|back|noop)"))


    # Authentication Conversation
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
        ],
        allow_reentry=True
    )
    application.add_handler(login_conv_handler)

    # File/link handling
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    application.add_handler(CallbackQueryHandler(download_button_handler, pattern="^(start_download|cancel_start)$"))
    application.add_handler(CallbackQueryHandler(cancel_active_download, pattern="^cancel_dl_active$"))

################################
# Link Download/Upload Handlers
################################

def escape_markdown(text):
    return re.sub(r'([_*`])', r'\\\1', text)

URL_PATTERN = re.compile(r"^https?://.*")

async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    # Check if user is logged in
    if user_id not in sessions:
        await update.message.reply_text("❌ Please login first using /login.")
        return

    text = update.message.text.strip()

    # Validate URL format
    if not URL_PATTERN.match(text):
        await update.message.reply_text("❌ Invalid URL. Please provide a valid link.")
        return

    url = text
    try:
        # Use aiohttp to fetch the file's headers asynchronously
        async with aiohttp.ClientSession() as session:
            async with session.head(url, allow_redirects=True) as r:
                if r.status != 200:
                    await update.message.reply_text(f"❌ Failed to fetch file info. Status code: {r.status}")
                    return

                size = int(r.headers.get("Content-Length", 0))
                content_disposition = r.headers.get("Content-Disposition", "")
                content_type = r.headers.get("Content-Type", "")

                # Try to extract filename from headers or fallback to URL
                if "filename=" in content_disposition:
                    name = content_disposition.split("filename=")[-1].strip('\"\' ')
                else:
                    name = url.split("/")[-1].split("?")[0]
                    if not name or "." not in name:
                        ext = mimetypes.guess_extension(content_type.split(";")[0].strip()) or ".bin"
                        name = f"file_{int(time.time())}{ext}"

                raw_name = name  # Use this for saving the file (safe & original)
                safe_name = escape_markdown(name)  # Use this for showing in Telegram

                # Store both names in context
                context.user_data["file_info"] = {
                    "url": url,
                    "name": safe_name,
                    "raw_name": raw_name,
                    "size": size
                }

                # Buttons
                keyboard = [
                    [InlineKeyboardButton("📤 Upload to server", callback_data="start_download")],
                    [InlineKeyboardButton("❌ Cancel", callback_data="cancel_start")]
                ]
                
                await update.message.reply_text(
                    f"📄 Filename - `{safe_name}`\n\n📦 Size - `{format_size(size)}`",
                    parse_mode="Markdown",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )

    except aiohttp.ClientError as e:
        await update.message.reply_text("❌ Failed to fetch file info due to a network error.")
        logger.error(f"AIOHTTP error: {e}")
    except Exception as e:
        await update.message.reply_text("❌ An unexpected error occurred while fetching file info.")
        logger.error(f"Unexpected error: {e}")

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
        task = asyncio.create_task(download_file_with_progress(context, query, msg.message_id, file_info))
        download_tasks[user_id] = task
        download_status[user_id] = {'active': True}

async def download_file_with_progress(context, query, message_id, file_info):
    user_id = query.from_user.id
    url = file_info.get("url", "")
    filename = file_info.get("raw_name", "").strip()
    total = file_info.get("size", 0)
    start_time = time.time()
    downloaded = 0

    # ✅ Sanitize filename
    if not filename or filename.endswith("/"):
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                head_response = await client.head(url, follow_redirects=True)
                content_disposition = head_response.headers.get("content-disposition", "")
                content_type = head_response.headers.get("content-type", "")
                if "filename=" in content_disposition:
                    filename = content_disposition.split("filename=")[-1].strip('"\' ')
                else:
                    ext = mimetypes.guess_extension(content_type.split(";")[0].strip()) or ".bin"
                    filename = f"file_{int(time.time())}{ext}"
        except Exception as e:
            filename = f"file_{int(time.time())}.bin"

    filename = os.path.basename(filename)

    # ✅ Safe path construction
    user_dir = f"/DATA/Users/{sessions[user_id]}"
    os.makedirs(user_dir, exist_ok=True)
    path = os.path.join(user_dir, filename)

    # Constants
    CHUNK_SIZE = 64 * 1024  # 64KB
    UPDATE_INTERVAL = 2     # seconds
    last_update = start_time

    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0, connect=60.0)) as client:
            with open(path, 'wb') as f:
                async with client.stream("GET", url, follow_redirects=True) as response:
                    response.raise_for_status()
                    async for chunk in response.aiter_bytes(chunk_size=CHUNK_SIZE):
                        if not download_status.get(user_id, {}).get("active"):
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
                                download_id="active",
				filename=filename
                            )
                            last_update = current_time

        await context.bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=message_id,
            text="✅ Download complete!"
        )
    except Exception as e:
        logger.error(f"Download failed: {e}")
        await context.bot.edit_message_text(
            chat_id=query.message.chat_id,
            message_id=message_id,
            text=f"❌ Error during download: {str(e)}"
        )
        if os.path.exists(path):
            os.remove(path)
    finally:
        download_tasks.pop(user_id, None)
        download_status.pop(user_id, None)


async def cancel_active_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id

    if user_id in download_status:
        download_status[user_id]['active'] = False

################################
# File Download/Upload Handlers
################################

@client.on(events.NewMessage)
async def handle_file(event):
    message = event.message
    user_id = event.sender_id

    # Ignore messages that aren't documents
    if not (message.media and message.document):
        return

    # Login check
    if user_id not in sessions:
        if user_id not in login_states:
            await event.respond("❌ You must log in first using /login to upload files.")
        return

    message = event.message
    if not (message.media and message.document):
        return

    document = message.document
    file_name = "unnamed_file"
    for attr in document.attributes:
        if isinstance(attr, DocumentAttributeFilename):
            file_name = attr.file_name
    file_size = document.size
    file_size_mb = file_size / (1024 * 1024)
    username = sessions.get(user_id, "testuser")
    download_path = os.path.join(f"/DATA/Users/{username}", file_name)

    # Save original file message in memory for future
    file_sessions[user_id] = {
        "file_name": file_name,
        "file_size": file_size,
        "file_msg": message,
        "path": download_path,
    }

    buttons = [
        [Button.inline("🚀 Upload to server", data=f"uploadfile:{user_id}")],
        [Button.inline("❌ Cancel", data=f"cancelfile:{user_id}")],
    ]
    await event.respond(
        f"📄 **Filename:** `{file_name}`\n💾 **Size:** `{file_size_mb:.2f} MB`",
        buttons=buttons
    )

@client.on(events.CallbackQuery)
async def handle_file_upload_actions(event):
    data = event.data.decode()
    user_id = event.sender_id

    # 🛑 Handle cancel both before and during upload
    if data.startswith("cancelfile:") and str(user_id) in data:
        cancel_tokens[user_id] = True

        if user_id in file_sessions:
            file_sessions.pop(user_id, None)
            await event.edit("❌ Upload cancelled before starting.")
        else:
            await event.answer("⏳ Cancelling upload...", alert=True)
        return

    # 🚀 Proceed to upload
    if data.startswith("uploadfile:") and str(user_id) in data:
        info = file_sessions.get(user_id)
        if not info:
            await event.answer("❌ No file info found.", alert=True)
            return

        await event.delete()
  
        file_msg = info["file_msg"]
        file_name = info["file_name"]
        file_size = info["file_size"]
        download_path = info["path"]

        cancel_tokens[user_id] = False
        msg = await event.respond(f"⬇️ Uploading **{file_name}**...\n")

        start_time = time.time()
        last_update = start_time

        def progress_callback(current, total):
            nonlocal last_update
            if cancel_tokens.get(user_id):
                raise Exception("Upload cancelled")

            now = time.time()
            percent = current / total * 100
            speed = current / (now - start_time + 1e-6)
            eta = (total - current) / (speed + 1e-6)
            if now - last_update > 2 or percent == 100:
                last_update = now
                bar = f"[{'=' * int(percent // 5)}{' ' * (20 - int(percent // 5))}] {percent:.1f}%"
                status = (
                    f"⬇️ Uploading **{file_name}**...\n{bar}\n\n"
                    f"📊 {current / 1e6:.2f}MB of {total / 1e6:.2f}MB\n"
                    f"🚀 Speed: {speed / 1e6:.2f}MB/s\n"
                    f"⏳ ETA: {str(timedelta(seconds=int(eta)))}"
                )
                asyncio.create_task(msg.edit(status, buttons=[
                    [Button.inline("❌ Cancel", data=f"cancelfile:{user_id}")]
                ]))

        try:
            await client.download_media(file_msg, file=download_path, progress_callback=progress_callback)
            await msg.edit(f"✅ File uploaded to server: `{download_path}`")
        except Exception as e:
            if "cancelled" in str(e).lower():
                await msg.edit("❌ Upload cancelled. Deleting file...")
                if os.path.exists(download_path):
                    os.remove(download_path)
            else:
                await msg.edit(f"❌ Upload failed: {e}")

        file_sessions.pop(user_id, None)
        cancel_tokens.pop(user_id, None)
        


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

async def run_all():
    # Start Telethon client with bot token
    await client.start(bot_token="7984121127:AAGyBslNMIkUEaEd6z2NdhqHSqFIJOGElxQ")

    # Initialize Telegram Bot API client (PTB)
    application = Application.builder().token("7984121127:AAGyBslNMIkUEaEd6z2NdhqHSqFIJOGElxQ").build()
    setup_handlers(application)

    # Start PTB components manually (without .run_polling())
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    # Run Telethon until it disconnects (blocks here)
    await client.run_until_disconnected()

if __name__ == '__main__':
    import asyncio
    asyncio.run(run_all())
