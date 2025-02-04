import sys
import re

def clean_token():
    """Git push öncesi token'ı maskele"""
    content = sys.stdin.read()
    # Token satırını bul ve değiştir
    content = re.sub(r'token: ".*?"', 'token: "xxxxxxxxxxxxx"', content)
    sys.stdout.write(content)

def restore_token():
    """Git pull sonrası token'ı koru"""
    content = sys.stdin.read()
    # Eğer maskelenmiş token varsa, orijinal token'ı koru
    if 'token: "xxxxxxxxxxxxx"' in content:
        try:
            with open('config.yml', 'r') as f:
                original = f.read()
                original_token = re.search(r'token: "(.*?)"', original)
                if original_token:
                    content = content.replace('token: "xxxxxxxxxxxxx"', f'token: "{original_token.group(1)}"')
        except FileNotFoundError:
            pass
    sys.stdout.write(content)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "clean":
        clean_token()
    else:
        restore_token() 