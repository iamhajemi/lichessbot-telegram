import sys
import re
import yaml

def get_token_from_config():
    """Mevcut config dosyasından token'ı al"""
    try:
        with open('config.yml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            return config.get('token', '')
    except:
        return ''

def clean_token():
    """Git push öncesi token'ı maskele"""
    content = sys.stdin.read()
    # Token satırını bul ve değiştir
    content = re.sub(r'token: ".*?"', 'token: "xxxxxxxxxxxxx"', content)
    sys.stdout.write(content)

def restore_token():
    """Git pull sonrası token'ı koru"""
    content = sys.stdin.read()
    current_token = get_token_from_config()
    
    if current_token:
        # Maskelenmiş token'ı mevcut token ile değiştir
        content = re.sub(r'token: ".*?"', f'token: "{current_token}"', content)
    
    sys.stdout.write(content)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        clean_token()
    else:
        restore_token() 