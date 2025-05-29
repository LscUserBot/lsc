import os
import importlib.util
import re
import random
import string
import sqlite3
from pyrogram import Client, filters, idle
from pyrogram.types import Message
from pathlib import Path
import asyncio
import psutil
import sys
import os
import sys
import time
import subprocess
import requests
import pytz
import platform
from datetime import datetime

def check_user_file():
    if not os.path.exists("user.txt"):
        print("Файл user.txt не найден, создаем новый...")
        api_id = input("Введите ваш API ID: ")
        api_hash = input("Введите ваш API HASH: ")
        
        with open("user.txt", "w") as f:
            f.write(f"{api_id}\n{api_hash}")
        return api_id, api_hash
    else:
        with open("user.txt", "r") as f:
            lines = f.readlines()
            return lines[0].strip(), lines[1].strip()
        
API_ID, API_HASH = check_user_file()

async def get_version():
    try:
        with open("version.txt", "r") as f:
            return f.read().strip()
    except:
        return "0.0"
    
async def check_version(app: Client, prefix: str):
    try:
        if not os.path.exists("version.txt"):
            error_msg = "⚠️ Не найден файл version.txt! Повторите установку юзер-бота!"
            print(error_msg)
            if app.is_initialized:
                await app.send_message("me", error_msg)
            return False

        with open("version.txt", "r") as f:
            local_version = f.read().strip()

        github_url = "https://raw.githubusercontent.com/ZeroUserBot/zero/main/version.txt"
        try:
            response = requests.get(github_url, timeout=10)
            response.raise_for_status()
            github_version = response.text.strip()

            if local_version < github_version:
                update_msg = (
                    f"🔄 Доступно обновление!\n"
                    f"<blockquote><i>{local_version} → {github_version}</i></blockquote>\n"
                    f"Используйте <code>{prefix}update</code>"
                )
                await app.send_message("me", update_msg)
                return github_version
            return True
        except requests.RequestException as e:
            print(f"⚠️ Ошибка проверки версии: {e}")
            return True
    except Exception as e:
        print(f"❌ Критическая ошибка в check_version: {e}")
        return True

def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS settings
                     (prefix TEXT, allow TEXT)''')
    
    cursor.execute("SELECT * FROM settings")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO settings VALUES (?, ?)", ('.', '[]'))
        conn.commit()
    
    conn.close()

def get_settings():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT prefix, allow FROM settings LIMIT 1")
    settings = cursor.fetchone()
    conn.close()
    return {
        'prefix': settings[0],
        'allow': eval(settings[1])
    }

def update_settings(prefix=None, allow=None):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    if prefix is not None:
        cursor.execute("UPDATE settings SET prefix = ?", (prefix,))
    if allow is not None:
        cursor.execute("UPDATE settings SET allow = ?", (str(allow),))
    
    conn.commit()
    conn.close()

async def install_libraries(message, module_name, libs_str):
    libs = [lib.strip() for lib in libs_str.split(",")]
    total_libs = len(libs)
    installed_count = 0
    results = []
    
    msg = await message.reply("🔄 Подготовка к установке библиотек...")
    
    for lib in libs:
        try:
            try:
                importlib.import_module(lib)
                results.append(f"» <code>{lib}</code> [✅ Уже установлена]")
                installed_count += 1
                continue
            except ImportError:
                pass
            
            message_parts = [
                f"❗️ Для корректной работы модуля <code>{module_name}</code> требуется установка следующих библиотек:",
                "<blockquote>" + "\n".join(results) + "\n",
                f"» <code>{lib}</code> [🔄 Установка...]</blockquote>",
                "",
                f"<blockquote><i>🔄 Начинаю установку библиотек! [{installed_count}/{total_libs}]</i></blockquote>"
            ]
            await msg.edit_text("\n".join(message_parts))
            
            process = await asyncio.create_subprocess_exec(
                sys.executable, "-m", "pip", "install", lib,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                results.append(f"» <code>{lib}</code> [✅ Успешно установлена]")
                installed_count += 1
            else:
                results.append(f"» <code>{lib}</code> [❌ Ошибка установки]")
                
        except Exception as e:
            results.append(f"» <code>{lib}</code> [❌ Ошибка: {str(e)}]")
    
    if installed_count == total_libs:
        success_message = [
            f"✅ Установка библиотек: <code>{', '.join(libs)}</code> успешно завершена!",
            f"<blockquote>🔄 Для применений нужна перезагрузка <code>{prefix}restart</code></blockquote>"
        ]
        await msg.edit_text("\n".join(success_message))
    else:
        error_message = [
            f"❗️ Для корректной работы модуля <code>{module_name}</code> требуется установка следующих библиотек:",
            "<blockquote>" + "\n".join(results) + "</blockquote>",
            "",
            "<i>Некоторые библиотеки не были установлены. Проверьте правильность названий и попробуйте установить их вручную.</i>"
        ]
        await msg.edit_text("\n".join(error_message))


init_db()
settings = get_settings()
prefix = settings['prefix']
allow = settings['allow']

app = Client(
    "zero",
    api_id=int(API_ID),
    api_hash=API_HASH,
    device_model="ZERO",
    app_version="1.0"
)

modules_help = {}
loaded_modules = {}
modules_info = {}

def generate_random_name(length=8):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(length))

def load_modules():
    modules_dir = "modules"
    if not os.path.exists(modules_dir):
        os.makedirs(modules_dir)
        return

    modules_help.clear()
    loaded_modules.clear()
    modules_info.clear()
    
    for filename in os.listdir(modules_dir):
        if filename.endswith(".py"):
            module_name = filename[:-3]
            module_path = os.path.join(modules_dir, filename)
            
            try:
                meta_data = {
                    "name": module_name,
                    "developer": "Неизвестный разработчик",
                    "description": "Нет описания",
                    "img": None,
                    "hidden": False
                }
                
                with open(module_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if line.startswith("#meta name:"):
                            meta_data["name"] = line.split(":", 1)[1].strip()
                        elif line.startswith("#meta developer:"):
                            meta_data["developer"] = line.split(":", 1)[1].strip()
                        elif line.startswith("#meta description:"):
                            meta_data["description"] = line.split(":", 1)[1].strip()
                        elif line.startswith("#meta img:"):
                            meta_data["img"] = line.split(":", 1)[1].strip()
                        elif line.startswith("#meta hidden:"):
                            meta_data["hidden"] = line.split(":", 1)[1].strip().lower() == "true"
                
                if meta_data["name"] in modules_info:
                    print(f"Модуль с именем {meta_data['name']} уже загружен, пропускаем {filename}")
                    continue
                
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                
                module.app = app
                module.prefix = prefix
                module.allow = allow
                module.modules_help = modules_help
                module.loaded_modules = loaded_modules
                module.modules_info = modules_info
                module.get_version = get_version
                module.check_version = check_version
                module.init_db = init_db
                module.get_settings = get_settings
                module.update_settings = update_settings
                module.generate_random_name = generate_random_name
                module.load_modules = load_modules
                module.install_libraries = install_libraries
                
                spec.loader.exec_module(module)
                
                loaded_modules[module_name] = module
                modules_info[meta_data["name"]] = {
                    "file_name": filename,
                    "path": module_path,
                    "developer": meta_data["developer"],
                    "description": meta_data["description"],
                    "img": meta_data["img"],
                    "hidden": meta_data["hidden"]
                }
                
                print(f"Модуль {meta_data['name']} загружен из файла {filename}")
                
            except Exception as e:
                print(f"Ошибка загрузки модуля {filename}: {e}")

async def authorize():
    try:
        print("🔧 Попытка авторизации...")
        await app.start()
        me = await app.get_me()
        print(f"✅ Авторизован как {me.first_name} (ID: {me.id})")
        version_status = await check_version(app, prefix) 
        if version_status is False:
            print("❌ Критическая ошибка версии, завершаю работу")
            await app.stop()
            return

        if me.id not in allow:
            new_allow = allow.copy()
            new_allow.append(me.id)
            update_settings(allow=new_allow)
            globals()['allow'] = new_allow
            print(f"✅ ID {me.id} добавлен в список владельцев")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка авторизации: {str(e)}")
        return False

async def main():
    os.system('cls' if os.name == 'nt' else 'clear')

    if os.path.exists("update_info.txt"):
        try:
            async with app:
                with open("update_info.txt", "r") as f:
                    lines = f.readlines()
                    chat_id = int(lines[0].strip())
                    message_id = int(lines[1].strip())
                    old_version = lines[2].strip() if len(lines) > 2 else "0.0"

                new_version = await get_version()
                changes = "Информация об изменениях недоступна"

                if os.path.exists("version_info.txt"):
                    with open("version_info.txt", "r", encoding="utf-8") as f:
                        v_lines = f.readlines()
                        if len(v_lines) >= 2 and v_lines[0].strip() == new_version:
                            changes = "\n".join(line.strip() for line in v_lines[1:]) or "Не указано"

                message_text = (
                    f"✅ Бот был успешно обновлен с <code>{old_version}</code> на <code>{new_version}</code>\n"
                    f"✏️ <blockquote><i>Изменения в версии:\n{changes}</i></blockquote>"
                )
                await app.edit_message_text(chat_id, message_id, message_text)
        except Exception as e:
            print(f"⚠️ Не удалось отправить сообщение об обновлении: {e}")
        finally:
            if os.path.exists("update_info.txt"):
                os.remove("update_info.txt")
            if os.path.exists("version_info.txt"):
                os.remove("version_info.txt")

    from utils.start import print_start
    print_start()
    print("🔄 Начинаем авторизацию...")

    if not await authorize():
        print("⚠️ Авторизация не удалась, запрашиваем данные вручную...")
        phone = input("📱 Введите номер телефона: ")
        try:
            async with app:
                sent_code = await app.send_code(phone)
                code = input("🔢 Введите код подтверждения: ")
                await app.sign_in(phone, sent_code.phone_code_hash, code)
                me = await app.get_me()
                print(f"✅ Успешная авторизация как {me.first_name}")
                if me.id not in allow:
                    new_allow = allow.copy()
                    new_allow.append(me.id)
                    update_settings(allow=new_allow)
                    globals()['allow'] = new_allow
                    print(f"✅ ID {me.id} добавлен в список владельцев")
        except Exception as e:
            print(f"❌ Критическая ошибка при входе: {str(e)}")
            return

    if os.path.exists("restart_info.txt"):
        with open("restart_info.txt", "r") as f:
            lines = f.readlines()
            chat_id = int(lines[0].strip())
            message_id = int(lines[1].strip())
        os.remove("restart_info.txt")
        try:
            async with app:
                await app.edit_message_text(chat_id, message_id, "✅ Бот успешно перезагружен!")
        except Exception as e:
            print(f"⚠️ Не удалось отредактировать сообщение: {e}")

    print("📦 Загружаем модули...")
    load_modules()
    if not modules_info:
        print("⚠️ Нет загруженных модулей!")
    else:
        print(f"✅ Загружено {len(modules_info)} модулей")

    print("🟢 Бот успешно запущен! Ожидаем команды...")
    try:
        me = await app.get_me()
        await app.send_message(me.id, 'Бот запущен!')
    except Exception as e:
        print(f"⚠️ Не удалось отправить сообщение о запуске: {e}")

    await idle()

if __name__ == "__main__":
    try:
        print("[LOG] Запуск бота...")
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("\n[INFO] Бот остановлен вручную.")
    except Exception as e:
        print(f"[ERROR] Критическая ошибка: {e}")
    finally:
        if app.is_connected:
            print("[INFO] Завершаем соединение...")
            loop.run_until_complete(app.stop())
