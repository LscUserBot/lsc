import os
import sys
import requests
import shutil
import stat
import time
from git import Repo

def on_rm_error(func, path, exc_info):
    """Обработчик ошибок при удалении файлов"""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def remove_readonly(func, path, _):
    """Удаление атрибута 'readonly' перед операцией"""
    os.chmod(path, stat.S_IWRITE)
    func(path)

def update_bot():
    print("🚀 Запуск процесса обновления...")
    temp_dir = "temp_update"
    
    try:
        if os.path.exists(temp_dir):
            print("🧹 Очистка временной директории...")
            shutil.rmtree(temp_dir, onerror=remove_readonly)

        print("⏬ Загружаем обновления из репозитория...")
        Repo.clone_from("https://github.com/ZeroUserBot/zero.git", temp_dir)
        
        print("🔄 Устанавливаем обновления...")
        exclude_files = ['user.txt', 'database.db', 'zero.session']
        
        for item in os.listdir(temp_dir):
            if item not in exclude_files:
                src = os.path.join(temp_dir, item)
                dst = os.path.join('.', item)
                
                try:
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
        
        print("✅ Обновление завершено! Перезапускаем бота...")
        time.sleep(2)
        os.execv(sys.executable, [sys.executable, "main.py"])
        
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