from utils.imports import *
from utils.func import *

#meta name: System
#meta developer: @zxcsolomka
#meta description: Системные модули
#meta img: https://i.pinimg.com/736x/1e/57/41/1e5741cd9716634b91d34923d4afad55.jpg

start_time = time.time()
system = platform.system()

@app.on_message(filters.command("ping", prefix) & filters.user(allow))
async def ping(client, message):
    starts_time = time.time()
    await message.edit("<emoji id=5445284980978621387>🚀</emoji>")
    ends_time = time.time()
    ping_time = (ends_time - starts_time) * 1000
    moscow_timezone = pytz.timezone('Europe/Moscow')
    current_time = datetime.now(moscow_timezone)
    formatted_time = current_time.strftime('%d.%m.%Y %H:%M:%S')
    end_time = time.time() - start_time
    hours, rem = divmod(end_time, 3600)
    minutes, seconds = divmod(rem, 60)

    await message.edit(f"<b><emoji id=5445284980978621387>🚀</emoji> PING: <code>{ping_time:.2f} ms</code>\n<emoji id=6037268453759389862>⏲️</emoji> Аптайм: <code>{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}</code></b>")   

@app.on_message(filters.command('info', prefixes=prefix) & filters.user(allow))
async def info_command(client: Client, message: Message):
    await message.delete()

    try:
        current_version = await get_version()
        version_check = await check_version(client, prefix)
        
        moscow_timezone = pytz.timezone('Europe/Moscow')
        current_time = datetime.now(moscow_timezone)
        formatted_time = current_time.strftime('%d.%m.%Y %H:%M:%S')

        me = await client.get_me()
        owner_name = me.first_name
        if me.last_name:
            owner_name += " " + me.last_name

        try:
            cpu_usage = f'{psutil.cpu_percent()}%'
            ram_usage = f'{psutil.virtual_memory().used / (1024 * 1024):.2f} MB'
        except:
            cpu_usage = ram_usage = 'Неизвестно'

        uptime = time.time() - start_time
        hours, rem = divmod(uptime, 3600)
        minutes, seconds = divmod(rem, 60)

        if system == "Windows":
            platform_info = f"<emoji id=5469825590884310445>🚫</emoji> Windows {platform.release()} ({platform.version()})"
        elif system == "Linux":
            if "termux" in sys.argv[0]:
                platform_info = f"<emoji id=5465488910865932234>🤖</emoji> Termux"
            elif "p3droid" in sys.argv[0]:
                platform_info = f"<emoji id=5465488910865932234>🤖</emoji> Pydroid3"
            else:
                platform_info = f"<emoji id=5462990382360962124>🤓</emoji> Linux"
        else:
            platform_info = f"<emoji id=5873121512445187130>❓</emoji> Unknown"

        version_line = f"<emoji id=5229120758734659539>😘</emoji> <b>zero v.{current_version}</b>"
        
        if isinstance(version_check, str):
            update_notice = (
                f"\n<blockquote><i>Доступно обновление: {current_version} → {version_check}</i></blockquote>"
            )
        else:
            update_notice = ""

        info_text = f"""
{version_line}{update_notice}

<emoji id=6035084557378654059>👤</emoji> Владелец: <b>{owner_name}</b>
<emoji id=6039404727542747508>⌨️</emoji> Префикс: «{prefix}»
<emoji id=6037268453759389862>⏲️</emoji> Аптайм: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}

<emoji id=5920515922505765329>⚡️</emoji> CPU: <i>~{cpu_usage}</i>
<emoji id=5938492039971737551>💼</emoji> RAM: <i>~{ram_usage}</i>

<emoji id=5884330496619450755>☁️</emoji> Платформа: {platform_info}
<emoji id=5983150113483134607>⏰️</emoji> Время: <b>{formatted_time}</b> MSK

<emoji id=6028338546736107668>⭐️</emoji> Команды: <code>{prefix}help</code>
        """

        photo_path = "zero.jpg"
        if os.path.exists(photo_path):
            await client.send_photo(
                chat_id=message.chat.id,
                photo=photo_path,
                caption=info_text
            )
        else:
            await client.send_message(
                chat_id=message.chat.id,
                text=info_text
            )

    except Exception as e:
        error_msg = f"⚠️ Ошибка в команде info: {str(e)}"
        print(error_msg)
        await client.send_message(message.chat.id, error_msg)

@app.on_message(filters.command("help", prefix) & filters.user(allow))
async def modules_help_command(client: Client, message: Message):
    args = message.text.split(maxsplit=1)
    
    if len(args) > 1:
        module_query = args[1].strip().lower()
        exact_match = None
        partial_matches = []
        
        for name in modules_info:
            if module_query == name.lower():
                exact_match = name
                break
            elif module_query in name.lower():
                partial_matches.append(name)
        
        if exact_match:
            module_info = modules_info[exact_match]
            commands = modules_help.get(exact_match, {})
            
            name_format = "<b>{}</b>" if module_info.get("name", "").lower() == "system" else "<code>{}</code>"
            formatted_name = name_format.format(exact_match)
            
            response = (
                f"🐊 Помощь по модулю {formatted_name}:\n\n"
                f"📁 Путь до модуля: <code>./modules/{module_info['file_name']}</code>\n"
                f"💠 Автор модуля: {module_info['developer']}\n"
                f"✍️ Описание модуля: {module_info['description']}\n\n"
                f"💫 Команды модуля:\n"
            )
            
            for cmd, desc in commands.items():
                response += f"» <code>{prefix}{cmd}</code> - {desc}\n"
            
            try:
                if module_info["img"]:
                    await message.delete()
                    await message.reply_photo(module_info["img"], caption=response)
                else:
                    await message.edit_text(response)
            except:
                await message.edit_text(response)
        elif partial_matches:
            response = "😓 Модуль с таким названием не был найден, но найдены совпадения:\n\n"
            response += "\n".join([f"» <code>{prefix}mhelp {match}</code>" for match in partial_matches])
            await message.edit_text(response)
        else:
            await message.edit_text("❌ Модуль не найден")
    else:
        total_modules = len(modules_info)
        hidden_modules = sum(1 for info in modules_info.values() if info["hidden"])
        
        response = f"🐊 {total_modules} модулей загружено, {hidden_modules} из них скрыто:\n\n"
        
        system_modules = []
        other_modules = []
        
        for module_name, info in modules_info.items():
            if info["hidden"]:
                continue
                
            if info.get("name", "").lower() == "System":
                system_modules.append((module_name, info))
            else:
                other_modules.append((module_name, info))
        
        for module_name, info in system_modules:
            commands = modules_help.get(module_name, {})
            command_list = "|".join([f"{cmd}" for cmd in commands.keys()])
            response += f"» <b>{module_name}</b>: ({command_list})\n"
        
        for module_name, info in other_modules:
            commands = modules_help.get(module_name, {})
            command_list = "|".join([f"{cmd}" for cmd in commands.keys()])
            response += f"» {module_name}: ({command_list})\n"
        
        await message.edit_text(response)

@app.on_message(filters.command("lm", prefixes=prefix) & filters.user(allow))
async def load_module(client: Client, message: Message):
    if not message.reply_to_message or not message.reply_to_message.document:
        await message.edit_text("❌ Ответьте на сообщение с файлом модуля (.py)")
        return
    
    document = message.reply_to_message.document
    if not document.file_name.endswith(".py"):
        await message.edit_text("❌ Файл должен быть с расширением .py")
        return
    
    temp_path = await message.reply_to_message.download()
    
    meta_data = {
        "name": document.file_name[:-3],
        "developer": "Неизвестный разработчик",
        "description": "Нет описания",
        "img": None,
        "hidden": False,
        "libs": None
    }
    
    with open(temp_path, "r", encoding="utf-8") as f:
        content = f.read()
        for line in content.split('\n'):
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
            elif line.startswith("#meta libs:"):
                meta_data["libs"] = line.split(":", 1)[1].strip()
    
    if meta_data["name"] in modules_info:
        os.remove(temp_path)
        await message.edit_text(f"❌ Модуль с названием <code>{meta_data['name']}</code> уже установлен!")
        return
    
    modules_dir = "modules"
    if not os.path.exists(modules_dir):
        os.makedirs(modules_dir)
    
    new_filename = document.file_name
    name_changed = False
    
    if os.path.exists(os.path.join(modules_dir, document.file_name)):
        name_changed = True
        file_ext = document.file_name.split(".")[-1]
        new_filename = f"{generate_random_name()}.{file_ext}"
    
    new_path = os.path.join(modules_dir, new_filename)
    os.rename(temp_path, new_path)
    
    load_modules()
    
    response = (
        f"✅ Установлен модуль <code>{meta_data['name']}</code>\n"
        f"💠 Разработчик: {meta_data['developer']}\n"
        f"✍️ Описание: {meta_data['description']}"
    )
    
    if name_changed:
        response += f"\n⚠️ <i>Файл с названием <code>{document.file_name}</code> уже был, поэтому название файла было изменено на <code>{new_filename}</code></i>"
    
    try:
        if meta_data["img"]:
            await message.delete()
            msg = await message.reply_photo(meta_data["img"], caption=response)
        else:
            msg = await message.edit_text(response)
    except Exception as e:
        print(f"Ошибка при отправке фото: {e}")
        msg = await message.edit_text(response)
    
    if meta_data["libs"]:
        await install_libraries(msg, meta_data["name"], meta_data["libs"])

@app.on_message(filters.command("um", prefixes=prefix) & filters.user(allow))
async def download_module(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit_text("❌ Укажите название модуля")
        return
    
    user_input = message.command[1].strip()
    modules_dir = "modules"
    
    filepath_by_filename = os.path.join(modules_dir, f"{user_input}.py")
    file_exists = os.path.exists(filepath_by_filename)
    
    matches = []
    for mod_name, info in modules_info.items():
        if user_input.lower() == mod_name.lower():
            matches = [(mod_name, info)]
            break
        elif user_input.lower() in mod_name.lower():
            matches.append((mod_name, info))
    
    if file_exists and not matches:
        await message.reply_document(
            filepath_by_filename,
            caption=f"✅ Модуль <code>{user_input}</code> выгружен"
        )
    elif not file_exists and len(matches) == 1:
        mod_name, info = matches[0]
        await message.reply_document(
            info["path"],
            caption=f"✅ Модуль <code>{mod_name}</code> выгружен"
        )
    elif file_exists and len(matches) == 1:
        mod_name, info = matches[0]
        if os.path.normpath(info["path"]) == os.path.normpath(filepath_by_filename):
            await message.reply_document(
                info["path"],
                caption=f"✅ Модуль <code>{mod_name}</code> выгружен"
            )
        else:
            await message.edit_text(
                f"⚠️ Найдено нечеткое совпадение: <code>{mod_name}</code>\n"
                f"Вы действительно хотите выгрузить этот модуль?\n\n"
                f"Да — <code>{prefix}um {mod_name}</code>"
            )
    elif len(matches) > 1:
        help_text = "🔎 Точных совпадений не найдено! Выберите нужный вариант:\n\n"
        help_text += "\n".join([
            f"▫️ <code>{mod_name}</code> (Имя файла: <code>{info['file_name']}</code>)" 
            for mod_name, info in matches
        ])
        await message.edit_text(help_text)
    else:
        await message.edit_text("❌ Модуль не найден")


@app.on_message(filters.command("dm", prefixes=prefix) & filters.user(allow))
async def delete_module(client: Client, message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.edit_text("❗ Укажите имя модуля или файла.")
        return

    user_input = args[1].strip()

    for mod_name, info in modules_info.items():
        if (user_input.lower() == mod_name.lower() and 
            (info.get("name", "").lower() == "system" or info["file_name"] == "1.py")):
            await message.edit_text("❌ Этот модуль нельзя выгрузить!")
            return
        if (f"{user_input}.py".lower() == info["file_name"].lower() and 
            (info.get("name", "").lower() == "system" or info["file_name"] == "1.py")):
            await message.edit_text("❌ Этот модуль нельзя выгрузить!")
            return

    deleted = False
    deleted_name = None

    filepath_by_filename = os.path.join("modules", f"{user_input}.py")
    if os.path.exists(filepath_by_filename):
        with open(filepath_by_filename, "r", encoding="utf-8") as f:
            content = f.read()
            if "#meta name: System" in content or filepath_by_filename.endswith("1.py"):
                await message.edit_text("❌ Этот модуль нельзя выгрузить!")
                return

        for mod_name, info in modules_info.items():
            if info["file_name"] == f"{user_input}.py":
                deleted_name = mod_name
                break
        
        if not deleted_name:
            deleted_name = user_input
        
        os.remove(filepath_by_filename)
        deleted = True

    if not deleted and user_input in modules_info:
        file_path = modules_info[user_input]["path"]
        if os.path.exists(file_path):
            os.remove(file_path)
            deleted_name = user_input
            deleted = True

    if not deleted:
        matches = []
        for mod_name in modules_info.keys():
            if user_input.lower() in mod_name.lower():
                matches.append(mod_name)

        if len(matches) == 0:
            await message.edit_text("❌ Не найден ни модуль, ни файл с таким именем.")
            return
        elif len(matches) == 1:
            confirm_text = (
                f"⚠️ Найдено нечеткое совпадение: <code>{matches[0]}</code>\n"
                f"Вы действительно хотите удалить этот модуль?\n\n"
                f"Да — <code>{prefix}dm {matches[0]}</code>"
            )
            await message.edit_text(confirm_text)
            return
        else:
            help_text = "🔎 Точных совпадений не найдено! Выберите нужный вариант:\n\n"
            help_text += "\n".join([f"▫️ <code>{mod}</code>" for mod in matches])
            await message.edit_text(help_text)
            return

    if deleted:
        if deleted_name in modules_info:
            del modules_info[deleted_name]
        
        load_modules()
        
        await message.edit_text(f"✅ Модуль <code>{deleted_name}</code> успешно удалён\n<blockquote><i>Начинаю перезагрузку...</blockquote></i>")
        os.execv(sys.executable, [sys.executable] + sys.argv)
    else:
        await message.edit_text("❌ Не удалось удалить модуль")


@app.on_message(filters.command("restart", prefix) & filters.user(allow))
async def restart_bot(client: Client, message: Message):
    await message.edit_text("🔄 Полная перезагрузка бота...")
    
    restart_info = {
        "chat_id": message.chat.id,
        "message_id": message.id
    }
    
    with open("restart_info.txt", "w") as f:
        f.write(f"{restart_info['chat_id']}\n{restart_info['message_id']}")
    
    os.execv(sys.executable, [sys.executable] + sys.argv)

@app.on_message(filters.command("setprefix", prefix) & filters.user(allow))
async def set_prefix(client: Client, message: Message):
    if len(message.command) < 2:
        await message.edit_text("❌ Укажите новый префикс")
        return
    
    new_prefix = message.command[1]
    if len(new_prefix) < 1 or len(new_prefix) > 3:
        await message.edit_text("❌ Префикс должен быть от 1 до 3 символов")
        return
    
    update_settings(prefix=new_prefix)
    globals()['prefix'] = new_prefix
    await message.edit_text(f"✅ Префикс изменен на <code>{new_prefix}</code>\n<blockquote><i>Начинаю перезагрузку...</blockquote></i>")
    os.execv(sys.executable, [sys.executable] + sys.argv)

@app.on_message(filters.command("addowner", prefix) & filters.user(allow))
async def add_owner(client: Client, message: Message):
    if not message.reply_to_message and len(message.command) < 2:
        await message.edit_text("❌ Укажите пользователя (ответом, ID или @username)")
        return
    try:
        if message.reply_to_message:
            user = message.reply_to_message.from_user
            user_id = user.id
            user_name = user.first_name or user.username or str(user.id)
        else:
            user_input = message.command[1]
            if user_input.startswith("@"):
                user = await client.get_users(user_input)
                user_name = user.first_name or user.username
            else:
                user = await client.get_users(int(user_input))
                user_name = user.first_name or str(user.id)
            user_id = user.id

        if user_id in allow:
            await message.edit_text("❌ Этот пользователь уже является владельцем")
            return

        new_allow = allow.copy()
        new_allow.append(user_id)
        update_settings(allow=new_allow)
        globals()['allow'] = new_allow
        await message.edit_text(f"✅ Пользователь {user_name}[{user_id}] добавлен в владельцы")
        load_modules()
    except Exception as e:
        await message.edit_text(f"❌ Ошибка: {e}")

@app.on_message(filters.command("delowner", prefix) & filters.user(allow))
async def del_owner(client: Client, message: Message):
    if not message.reply_to_message and len(message.command) < 2:
        await message.edit_text("❌ Укажите пользователя (ответом или ID)")
        return

    try:
        if message.reply_to_message:
            user_id = message.reply_to_message.from_user.id
        else:
            user_input = message.command[1]
            if user_input.startswith("@"):
                user = await client.get_users(user_input)
                user_id = user.id
            else:
                user_id = int(user_input)

        if user_id not in allow:
            await message.edit_text("❌ Этот пользователь не является владельцем")
            return

        new_allow = [uid for uid in allow if uid != user_id]
        update_settings(allow=new_allow)
        globals()['allow'] = new_allow
        await message.edit_text(f"✅ Пользователь [{user_id}] удален из владельцев")

    except Exception as e:
        await message.edit_text(f"❌ Ошибка: {e}")


@app.on_message(filters.command("update", prefix) & filters.user(allow))
async def update_bot(client: Client, message: Message):
    if not os.path.exists("utils/updater.py"):
        await message.edit_text("❌ Файл обновления не найден!")
        return
    
    await message.edit_text("🔄 Подготовка к обновлению...")
    
    with open("update_info.txt", "w") as f:
        f.write(f"{message.chat.id}\n{message.id}")
    
    try:
        os.execv(sys.executable, [sys.executable, "utils/updater.py"])
    except Exception as e:
        await message.edit_text(f"❌ Ошибка запуска обновления: {e}")
        if os.path.exists("update_info.txt"):
            os.remove("update_info.txt")

@app.on_message(filters.command("im", prefixes=prefix) & filters.user(allow) & filters.reply)
async def info_module(client: Client, message: Message):
    reply = message.reply_to_message
    if not reply.document or not reply.document.file_name.endswith(".py"):
        await message.edit_text("❌ Ответьте на файл модуля с расширением .py")
        return
    
    temp_path = await reply.download()
    
    meta_data = {
        "name": reply.document.file_name[:-3],
        "developer": "Неизвестный разработчик",
        "description": "Нет описания",
        "img": None,
        "libs": None,
        "commands": {}
    }
    
    with open(temp_path, "r", encoding="utf-8") as f:
        content = f.read()
        for line in content.split('\n'):
            if line.startswith("#meta name:"):
                meta_data["name"] = line.split(":", 1)[1].strip()
            elif line.startswith("#meta developer:"):
                meta_data["developer"] = line.split(":", 1)[1].strip()
            elif line.startswith("#meta description:"):
                meta_data["description"] = line.split(":", 1)[1].strip()
            elif line.startswith("#meta img:"):
                meta_data["img"] = line.split(":", 1)[1].strip()
            elif line.startswith("#meta libs:"):
                meta_data["libs"] = line.split(":", 1)[1].strip()
            elif line.startswith("modules_help[") and "]" in line:
                try:
                    module_name = line.split("['")[1].split("']")[0]
                    if module_name == meta_data["name"]:
                        commands_section = content.split("modules_help[")[1].split("] = {")[1].split("}")[0]
                        for cmd_line in commands_section.split('\n'):
                            if '": ' in cmd_line:
                                cmd = cmd_line.split('"')[1]
                                desc = cmd_line.split('": "')[1].split('"')[0]
                                meta_data["commands"][cmd] = desc
                except:
                    pass
    
    os.remove(temp_path)
    
    response = f"🐊 Информация о модуле <code>{meta_data['name']}</code>:\n\n"
    
    if meta_data["libs"]:
        response += f"📚 Необходимы библиотеки: <code>{meta_data['libs']}</code>\n"
    
    response += (
        f"💠 Автор модуля: {meta_data['developer']}\n"
        f"✍️ Описание модуля: {meta_data['description']}\n\n"
    )
    
    if meta_data["commands"]:
        response += "💫 Команды модуля:\n"
        for cmd, desc in meta_data["commands"].items():
            response += f"» <code>{prefix}{cmd}</code> - {desc}\n"
    
    try:
        if meta_data["img"]:
            await message.delete()
            await message.reply_photo(meta_data["img"], caption=response)
        else:
            await message.edit_text(response)
    except Exception as e:
        print(f"Ошибка при отправке фото: {e}")
        await message.edit_text(response)

modules_help['System'] = {
  "ping": "Узнать пинг",
  "info": "Информация о боте",
  "lm": "Установить модуль",
  "dm": "Удалить модуль",
  "um": "Выгрузить модуль файлом",
  "im": "Информация о модуле по файлу",
  "help": "Помощь по модулям",
  "setprefix": "сменить префикс",
  "addowner": "Добавить пользователя в управление ботом",
  "delowner": "Исключить пользователя в управление ботом",
  "update": "Обновить бота",
  "restart": "Перезапустить бота",
}