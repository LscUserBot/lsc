import os
import sys
import shutil
import stat
import time
import subprocess
import requests
from git import Repo

def on_rm_error(func, path, exc_info):
    os.chmod(path, stat.S_IWRITE)
    func(path)

def remove_readonly(func, path, _):
    os.chmod(path, stat.S_IWRITE)
    func(path)

EXCLUDE_DIRS = []
EXCLUDE_FILES = ['user.txt', 'database.db', 'zero.session']

def should_skip(path):
    return False

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
            shutil.rmtree(temp_dir, onerror=remove_readonly)

        print("⏬ Загружаем обновления из репозитория...")
        Repo.clone_from("https://github.com/ZeroUserBot/zero.git", temp_dir)
        
        new_version = "0.0"
        version_file = os.path.join(temp_dir, "version.txt")
        if os.path.exists(version_file):
            with open(version_file, "r") as f:
                new_version = f.read().strip()
        
        print("🔄 Устанавливаем обновления...")
        
        for item in os.listdir(temp_dir):
            src = os.path.join(temp_dir, item)
            dst = os.path.join('.', item)

            if item in EXCLUDE_FILES:
                print(f"📎 Пропущен системный файл: {item}")
                continue
            
            try:
                if item == "modules":
                    if os.path.exists(dst):
                        for module_file in os.listdir(src):
                            module_src = os.path.join(src, module_file)
                            module_dst = os.path.join(dst, module_file)
                            
                            if os.path.exists(module_dst):
                                print(f"🔄 Обновление модуля: {module_file}")
                                os.chmod(module_dst, stat.S_IWRITE)
                                if os.path.isdir(module_dst):
                                    shutil.rmtree(module_dst, onerror=on_rm_error)
                                else:
                                    os.unlink(module_dst)
                                shutil.copy2(module_src, module_dst)
                    continue
                
                if os.path.exists(dst):
                    if os.path.isdir(dst):
                        shutil.rmtree(dst, onerror=on_rm_error)
                    else:
                        os.chmod(dst, stat.S_IWRITE)
                        os.unlink(dst)

                if os.path.isdir(src):
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
                    
            except PermissionError as pe:
                print(f"⚠️ Предупреждение: Не удалось обновить {item} - {pe}")
                continue
            except Exception as e:
                print(f"⚠️ Предупреждение: Ошибка при обработке {item} - {e}")
                continue
        
        print("🧹 Очистка временных файлов...")
        shutil.rmtree(temp_dir, onerror=remove_readonly)
        
        changes = get_version_changes(new_version)
        with open("update_info.txt", "w") as f:
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
                shutil.rmtree(temp_dir, onerror=remove_readonly)
            except Exception as cleanup_error:
                print(f"⚠️ Ошибка при очистке временных файлов: {cleanup_error}")
        sys.exit(1)

if __name__ == "__main__":
    update_bot()
