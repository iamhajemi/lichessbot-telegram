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

def mask_token(content):
    """Token'ı maskele"""
    # Token satırını bul ve değiştir (daha sıkı bir regex ile)
    pattern = r'(token:\s*)"[^"]*"'
    return re.sub(pattern, r'\1"xxxxxxxxxxxxx"', content)

def clean_token():
    """Git push öncesi token'ı maskele"""
    content = sys.stdin.read()
    masked_content = mask_token(content)
    if masked_content != content:  # Eğer değişiklik yapıldıysa
        print("Token maskelendi", file=sys.stderr)
    sys.stdout.write(masked_content)

def restore_token():
    """Git pull sonrası token'ı koru"""
    content = sys.stdin.read()
    current_token = get_token_from_config()
    
    if current_token and 'token: "xxxxxxxxxxxxx"' in content:
        # Maskelenmiş token'ı mevcut token ile değiştir
        pattern = r'(token:\s*)"[^"]*"'
        content = re.sub(pattern, f'\\1"{current_token}"', content)
        print("Token geri yüklendi", file=sys.stderr)
    
    sys.stdout.write(content)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        clean_token()
    else:
        restore_token() 