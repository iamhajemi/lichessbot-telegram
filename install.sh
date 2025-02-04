#!/bin/bash

echo "Lichess Bot Kurulum Başlatılıyor..."

# Hata kontrolü fonksiyonu
check_error() {
    if [ $? -ne 0 ]; then
        echo "Hata: $1"
        exit 1
    fi
}

# Gerekli paketleri kur
echo "Gerekli paketler kuruluyor..."
sudo apt-get update
check_error "Paket listesi güncellenemedi"
sudo apt-get install -y python3 python3-pip python3-venv git
check_error "Gerekli paketler kurulamadı"

# Çalışma dizini oluştur
INSTALL_DIR="$HOME/lichessbot"
mkdir -p "$INSTALL_DIR"
check_error "Çalışma dizini oluşturulamadı"
cd "$INSTALL_DIR"
check_error "Çalışma dizinine geçilemedi"

# Ana bot reposunu klonla
echo "Lichess bot reposu klonlanıyor..."
if [ ! -d ".git" ]; then
    git clone https://github.com/lichess-bot-devs/lichess-bot.git .
    check_error "Bot reposu klonlanamadı"
fi

# config.yml kontrolü
if [ ! -f "config.yml" ]; then
    echo "config.yml dosyası bulunamadı. Örnek config dosyası kopyalanıyor..."
    cp config.yml.default config.yml
    check_error "config.yml oluşturulamadı"
    echo "ÖNEMLİ: config.yml dosyasını düzenlemeyi unutmayın!"
    echo "Token ve diğer ayarlarınızı config.yml dosyasına eklemeniz gerekiyor."
fi

# run.py dosyasını güncelle
echo "Bot yönetim scripti oluşturuluyor..."
cat > run.py << 'EOL'
import subprocess
import os
import time
import sys
import shutil

def update_from_github():
    """GitHub'dan en son değişiklikleri kontrol et ve güncelle."""
    print("GitHub'dan güncellemeler kontrol ediliyor...")
    try:
        # Mevcut dizinde git repo var mı kontrol et
        if not os.path.exists('.git'):
            print("Git repo bulunamadı. Yeni repo oluşturuluyor...")
            subprocess.run(['git', 'init'], check=True)
            subprocess.run(['git', 'remote', 'add', 'origin', 'https://github.com/lichess-bot-devs/lichess-bot.git'], check=True)
            # İlk kez klonlama yapılıyorsa master branch'i oluştur
            subprocess.run(['git', 'fetch', 'origin'], check=True)
            subprocess.run(['git', 'checkout', '-b', 'master', 'origin/master'], check=True)
        else:
            # Uzak değişiklikleri kontrol et
            subprocess.run(['git', 'fetch', 'origin'], check=True)
            try:
                # Değişiklikleri kontrol et
                changes = subprocess.run(['git', 'diff', 'HEAD', 'origin/master', '--name-only'],
                                      capture_output=True, text=True, check=True)
                if changes.stdout.strip():
                    print("Yeni güncellemeler bulundu. İndiriliyor...")
                    # Yerel değişiklikleri yedekle
                    subprocess.run(['git', 'stash'], check=True)
                    # En son değişiklikleri indir
                    subprocess.run(['git', 'pull', 'origin', 'master'], check=True)
                    print("Bot başarıyla güncellendi!")
                else:
                    print("Bot zaten güncel.")
            except subprocess.CalledProcessError:
                print("Güncelleme kontrolü sırasında hata oluştu. Zorla güncelleme deneniyor...")
                subprocess.run(['git', 'reset', '--hard', 'origin/master'], check=True)
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
    venv_python = os.path.join(venv_directory, 'bin', 'python3')  # Path to Python in the virtual environment
    while True:
        try:
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
        # Önce GitHub'dan güncelleme kontrolü yap
        update_from_github()
        
        # Virtual environment oluştur
        create_virtualenv()
        
        # Start the Lichess bot with auto-restart
        print("Starting the Lichess bot with auto-restart...")
        run_bot()  # Run the bot and auto-restart on disconnect
    except KeyboardInterrupt:
        print("Bot stopped manually.")
        sys.exit(0)
EOL

# Çalıştırma izni ver
chmod +x run.py

echo "Kurulum tamamlandı!"
echo "ÖNEMLİ: config.yml dosyasını düzenlemeyi unutmayın!"
echo "Bot'u başlatmak için: cd $INSTALL_DIR && python3 run.py" 