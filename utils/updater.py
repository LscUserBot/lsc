import os
import sys
import shutil
import stat
import time
import subprocess
import requests
from git import Repo

def on_rm_error(func, path, exc_info):
    """Функция для обработки ошибок при удалении"""
    os.chmod(path, stat.S_IWRITE)
    func(path)

EXCLUDE_FILES = ['user.txt', 'database.db', 'zero.session']
SKIP_FILES = ['changes.txt', 'README.md']

def get_version_changes(new_version):
    try:
        changes_url = "https://raw.githubusercontent.com/ZeroUserBot/zero/main/changes.txt" 
        response = requests.get(changes_url)
        if response.status_code == 200:
            changes_text = response.text
            version_section = f"changes(version={new_version}):"

            if version_section in changes_text:
                start_idx = changes_text.index(version_section) + len(version_section)
                end_idx = changes_text.find("changes(version=", start_idx)
                if end_idx == -1:
                    return changes_text[start_idx:].strip()
                return changes_text[start_idx:end_idx].strip()
    except Exception:
        pass
    return "Информация об изменениях недоступна"

def update_bot():
    print("🚀 Запуск процесса обновления...")
    temp_dir = "temp_update"

    try:
        if os.path.exists(temp_dir):
            print("🧹 Очистка временной директории...")
            shutil.rmtree(temp_dir, onerror=on_rm_error)

        print("⏬ Загружаем обновления из репозитория...")
        Repo.clone_from("https://github.com/ZeroUserBot/zero.git",  temp_dir)

        new_version = "0.0"
        version_file = os.path.join(temp_dir, "version.txt")
        if os.path.exists(version_file):
            with open(version_file, "r") as f:
                new_version = f.read().strip()

        print("🔄 Устанавливаем обновления...")

        for root, dirs, files in os.walk(temp_dir):
            relative_path = os.path.relpath(root, temp_dir)
            dst_root = os.path.join('.', relative_path)

            if not os.path.exists(dst_root):
                os.makedirs(dst_root)

            for file in files:
                src_file = os.path.join(root, file)
                dst_file = os.path.join(dst_root, file)

                if file in SKIP_FILES:
                    print(f"📎 Пропущен системный файл: {file}")
                    continue

                if os.path.basename(dst_file) in EXCLUDE_FILES:
                    print(f"📎 Пропущен защищённый файл: {dst_file}")
                    continue

                try:
                    print(f"🔄 Копирование файла: {src_file} → {dst_file}")
                    shutil.copy2(src_file, dst_file)
                except Exception as e:
                    print(f"⚠️ Ошибка при копировании файла {src_file}: {e}")

        print("🧹 Очистка временных файлов...")
        shutil.rmtree(temp_dir, onerror=on_rm_error)

        changes = get_version_changes(new_version)
        with open("version_info.txt", "w", encoding="utf-8") as f:
            f.write(f"{new_version}\n{changes}")

        print("✅ Обновление завершено! Перезапускаем бота...")
        time.sleep(2)

        python_exec = sys.executable
        script_path = os.path.abspath("zero.py")
        subprocess.Popen([python_exec, script_path], start_new_session=True)
        sys.exit(0)

    except Exception as e:
        print(f"❌ Критическая ошибка при обновлении: {e}")
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir, onerror=on_rm_error)
            except Exception as cleanup_error:
                print(f"⚠️ Ошибка при очистке временных файлов: {cleanup_error}")
        sys.exit(1)
