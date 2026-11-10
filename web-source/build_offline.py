"""產生單機版：一個 HTML 檔，內含 three.js、原創金幣圖（202 張）與原創場地圖，完全不需網路。"""
import base64
import io
import json
import os
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, 'index.html')
THREE = os.path.join(HERE, 'package/build/three.min.js')
COINS = '/home/claude/reverse_coin/coins'
FIELD = '/home/claude/reverse_coin/field.jpg'
OUT = os.path.join(HERE, 'dist', '逆轉金幣3D_單機版.html')


def data_uri(img, fmt, mime, **kw):
    buf = io.BytesIO()
    img.save(buf, fmt, **kw)
    return f'data:{mime};base64,' + base64.b64encode(buf.getvalue()).decode()


coins = {}
for f in sorted(os.listdir(COINS)):
    if f.endswith('.png'):
        im = Image.open(os.path.join(COINS, f)).convert('RGBA')
        coins[f[:-4]] = data_uri(im, 'WEBP', 'image/webp', quality=88, method=6)
field = data_uri(Image.open(FIELD).convert('RGB'), 'JPEG', 'image/jpeg', quality=92)
TITLE_BG = 'data:image/jpeg;base64,' + base64.b64encode(open(os.path.join(HERE, 'title_bg.jpg'), 'rb').read()).decode()
assets_js = 'window.RCB_ASSETS=' + json.dumps({'field': field, 'coins': coins}, separators=(',', ':')) + ';window.RCB_TITLE_BG=' + json.dumps(TITLE_BG) + ';'
# 音效：單機版內嵌；電腦版改讀旁邊的 sounds 資料夾（可自行替換）
SOUNDS = os.path.join(HERE, 'sounds')
MIME = {'.wav': 'audio/wav', '.ogg': 'audio/ogg', '.mp3': 'audio/mpeg'}
snd = {}
for f in sorted(os.listdir(SOUNDS)):
    n, e = os.path.splitext(f)
    if e in MIME:
        snd[n] = f'data:{MIME[e]};base64,' + base64.b64encode(open(os.path.join(SOUNDS, f), 'rb').read()).decode()
sound_embed_js = 'window.RCB_SOUNDS=' + json.dumps(snd, separators=(',', ':')) + ';'
sound_dir_js = 'window.RCB_SOUND_DIR="sounds/";'


src = open(SRC, encoding='utf-8').read()
# 拿掉 Google Fonts（單機版用系統字型）
src = '\n'.join(l for l in src.split('\n') if 'fonts.googleapis.com' not in l and 'fonts.gstatic.com' not in l)
# three.js 內嵌
cdn = '<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>'
assert cdn in src
three = open(THREE, encoding='utf-8').read().replace('</script>', '<\\/script>')
PEER_TAG = '<script src="https://cdn.jsdelivr.net/npm/peerjs@1.5.4/dist/peerjs.min.js"></script>'
assert PEER_TAG in src
PEERJS = open(os.path.join(HERE, 'peerjs.min.js'), encoding='utf-8').read().replace('</script>', '<\\/script>')
src = src.replace(PEER_TAG, '<script>' + PEERJS + '</script>')
MQTT_TAG = '<script src="https://cdn.jsdelivr.net/npm/mqtt@5.10.1/dist/mqtt.min.js"></script>'
assert MQTT_TAG in src
MQTTJS = open(os.path.join(HERE, 'mqtt.min.js'), encoding='utf-8').read().replace('</script>', '<\\/script>')
src = src.replace(MQTT_TAG, '<script>' + MQTTJS + '</script>')
src = src.replace(cdn, '<script>' + three + '</script>\n<script>' + assets_js + '</script>\n<script>@@SOUND@@</script>')
# 網頁版（claude.ai 發布用：內建原創圖片＋音效，不含 <html>/<head> 外框，左右留 16px）
web = src.replace('@@SOUND@@', sound_embed_js)
web = web.replace("padding-left: max(8px, env(safe-area-inset-left, 0px));", "padding-left: max(16px, env(safe-area-inset-left, 0px));")
web = web.replace("padding-right: max(8px, env(safe-area-inset-right, 0px));", "padding-right: max(16px, env(safe-area-inset-right, 0px));")
os.makedirs(os.path.join(HERE, 'dist'), exist_ok=True)
open(os.path.join(HERE, 'dist', '逆轉金幣3D_網頁版.html'), 'w', encoding='utf-8').write(web)
# 把 <title>…<style>…</style> 移到 <head>
head_end = src.index('<div id="app">')
head, body = src[:head_end], src[head_end:]
html = ('<!doctype html>\n<html lang="zh-Hant">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
        + head + '\n</head>\n<body>\n' + body + '\n</body>\n</html>\n')
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'w', encoding='utf-8').write(html.replace('@@SOUND@@', sound_embed_js))
OUT_PC = os.path.join(HERE, 'dist', 'ReverseCoin3D_pc.html')     # 電腦版：讀 sounds 資料夾
open(OUT_PC, 'w', encoding='utf-8').write(html.replace('@@SOUND@@', sound_dir_js))
print(OUT, f'{os.path.getsize(OUT) / 1e6:.1f} MB', len(coins), 'coins')
