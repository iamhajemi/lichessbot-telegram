import subprocess
import os
import time
import sys
import shutil

def setup_config():
    """Konfigurasyon dosyasını hazırla."""
    if not os.path.exists('config.yml'):
        if os.path.exists('config.yml.default'):
            print("config.yml bulunamadı. config.yml.default'tan kopyalanıyor...")
            shutil.copy2('config.yml.default', 'config.yml')
            print("config.yml oluşturuldu. Lütfen token bilgilerinizi güncelleyin.")
            sys.exit(1)
        else:
            print("HATA: Ne config.yml ne de config.yml.default dosyası bulunamadı!")
            sys.exit(1)

def update_from_github():
    """GitHub'dan en son değişiklikleri kontrol et ve güncelle."""
    print("GitHub'dan güncellemeler kontrol ediliyor...")
    try:
        # Mevcut dizinde git repo var mı kontrol et
        if not os.path.exists('.git'):
            print("Git repo bulunamadı. Yeni repo oluşturuluyor...")
            subprocess.run(['git', 'init'], check=True)
            subprocess.run(['git', 'remote', 'add', 'origin', 'https://github.com/iamhajemi/lichessbot-telegram.git'], check=True)
            subprocess.run(['git', 'fetch', 'origin'], check=True)
            try:
                # Master branch'i kontrol et
                subprocess.run(['git', 'checkout', 'master'], check=True)
            except subprocess.CalledProcessError:
                # Master branch yoksa main'i dene
                try:
                    subprocess.run(['git', 'checkout', 'main'], check=True)
                except subprocess.CalledProcessError:
                    # Hiçbiri yoksa yeni branch oluştur
                    subprocess.run(['git', 'checkout', '-b', 'master'], check=True)
                    subprocess.run(['git', 'pull', 'origin', 'master'], check=True)
        else:
            # Remote branch'i kontrol et
            result = subprocess.run(['git', 'branch', '-r'], capture_output=True, text=True)
            if 'origin/master' in result.stdout:
                default_branch = 'master'
            elif 'origin/main' in result.stdout:
                default_branch = 'main'
            else:
                # Eğer remote branch bulunamazsa, varsayılan olarak master kullan
                default_branch = 'master'
            
            # Uzak değişiklikleri kontrol et
            subprocess.run(['git', 'fetch', 'origin'], check=True)
            try:
                # Değişiklikleri kontrol et
                changes = subprocess.run(['git', 'diff', 'HEAD', f'origin/{default_branch}', '--name-only'],
                                      capture_output=True, text=True, check=True)
                if changes.stdout.strip():
                    print("Yeni güncellemeler bulundu. İndiriliyor...")
                    # config.yml'i yedekle
                    if os.path.exists('config.yml'):
                        shutil.copy2('config.yml', 'config.yml.backup')
                    # En son değişiklikleri indir
                    subprocess.run(['git', 'pull', 'origin', default_branch], check=True)
                    # config.yml'i geri yükle
                    if os.path.exists('config.yml.backup'):
                        shutil.move('config.yml.backup', 'config.yml')
                    print("Bot başarıyla güncellendi!")
                else:
                    print("Bot zaten güncel.")
            except subprocess.CalledProcessError:
                print("Güncelleme kontrolü sırasında hata oluştu. Zorla güncelleme deneniyor...")
                # config.yml'i yedekle
                if os.path.exists('config.yml'):
                    shutil.copy2('config.yml', 'config.yml.backup')
                subprocess.run(['git', 'reset', '--hard', f'origin/{default_branch}'], check=True)
                # config.yml'i geri yükle
                if os.path.exists('config.yml.backup'):
                    shutil.move('config.yml.backup', 'config.yml')
                print("Bot başarıyla güncellendi!")
            
    except subprocess.CalledProcessError as e:
        print(f"Güncelleme sırasında hata oluştu: {e}")
        print("Bot mevcut sürümü ile devam ediyor...")

# Define paths - mevcut dizini kullan
current_dir = os.path.dirname(os.path.abspath(__file__))
bot_directory = current_dir  # Mevcut dizini kullan
venv_directory = os.path.join(current_dir, 'venv')  # Sanal ortam için mevcut dizini kullan

def create_virtualenv():
    """Create virtual environment if it doesn't exist."""
    if not os.path.exists(venv_directory):
        print("Creating virtual environment...")
        subprocess.run(['python3', '-m', 'venv', 'venv'], check=True)
        print("Virtual environment created successfully.")
        # Gerekli paketleri kur
        pip_path = os.path.join(venv_directory, 'bin', 'pip')
        print("Installing required packages...")
        subprocess.run([pip_path, 'install', '-r', 'requirements.txt'], check=True)
    else:
        print("Virtual environment already exists.")

def run_bot():
    """Run the Lichess bot with auto-restart functionality."""
    # Windows için Python yolunu düzelt
    if os.name == 'nt':  # Windows işletim sistemi kontrolü
        venv_python = os.path.join(venv_directory, 'Scripts', 'python.exe')
    else:
        venv_python = os.path.join(venv_directory, 'bin', 'python3')
    
    while True:
        try:
            # Her çalıştırmada güncelleme kontrolü yap
            update_from_github()
            
            # Bot'u çalıştır
            subprocess.run([venv_python, os.path.join(bot_directory, "lichess-bot.py")], check=True)
            print("Bot stopped unexpectedly, attempting restart in 5 seconds...")
            time.sleep(5)  # Wait before retrying
        except subprocess.CalledProcessError as e:
            print(f"Error occurred: {e}")
            print("Reconnecting in 5 seconds...")
            time.sleep(5)  # Wait before retrying

if __name__ == "__main__":
    try:
        # Konfigurasyon dosyasını kontrol et
        setup_config()
        
        # Virtual environment oluştur
        create_virtualenv()
        
        # Start the Lichess bot with auto-restart
        print("Starting the Lichess bot with auto-restart...")
        run_bot()  # Run the bot and auto-restart on disconnect
    except KeyboardInterrupt:
        print("Bot stopped manually.")
        sys.exit(0)
