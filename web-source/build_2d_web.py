"""2D 網頁版：沿用 3D 版的規則／物理／介面，畫面換成 Canvas 2D 俯視圖（不需 three.js）。"""
import os, re, base64, json
from PIL import Image
import io
HERE = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(HERE, 'index.html'), encoding='utf-8').read()
gfx = open(os.path.join(HERE, 'gfx2d.js'), encoding='utf-8').read()
i = src.index('const GFX = (() => {')
j = src.index('\n})();', i) + len('\n})();')
src = src[:i] + gfx + src[j:]
src = src.replace('<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>', '')
PEER_TAG = '<script src="https://cdn.jsdelivr.net/npm/peerjs@1.5.4/dist/peerjs.min.js"></script>'
assert PEER_TAG in src
PEERJS = open(os.path.join(HERE, 'peerjs.min.js'), encoding='utf-8').read().replace('</script>', '<\\/script>')
src_site_peer = PEERJS
assert 'THREE.' not in src[src.index('const GFX'):src.index('const GFX') + len(gfx)]
rep = [('<title>逆轉金幣 3D</title>', '<title>逆轉金幣 2D</title>'),
       ('REVERSE COIN BATTLE 3D', 'REVERSE COIN BATTLE 2D'),
       ('立體對戰｜專家規則', '2D 俯視對戰｜專家規則')]
for a, b in rep:
    assert a in src, a
    src = src.replace(a, b)
src = src.replace('#camBar.folded > button:not(#camFold) { display: none; }',
                  '#camBar.folded > button:not(#camFold) { display: none; }\n#camTop, #camTilt, #camRotL, #camRotR { display: none !important; }')
# 內嵌原創圖片與音效
def data_uri(img, fmt, mime, **kw):
    buf = io.BytesIO(); img.save(buf, fmt, **kw)
    return f'data:{mime};base64,' + base64.b64encode(buf.getvalue()).decode()
COINS = '/home/claude/reverse_coin/coins'
coins = {f[:-4]: data_uri(Image.open(os.path.join(COINS, f)).convert('RGBA'), 'WEBP', 'image/webp', quality=88, method=6)
         for f in sorted(os.listdir(COINS)) if f.endswith('.png')}
field = data_uri(Image.open('/home/claude/reverse_coin/field.jpg').convert('RGB'), 'JPEG', 'image/jpeg', quality=92)
MIME = {'.wav': 'audio/wav', '.ogg': 'audio/ogg', '.mp3': 'audio/mpeg'}
snd = {}
for f in sorted(os.listdir(os.path.join(HERE, 'sounds'))):
    n, e = os.path.splitext(f)
    if e in MIME:
        snd[n] = f'data:{MIME[e]};base64,' + base64.b64encode(open(os.path.join(HERE, 'sounds', f), 'rb').read()).decode()
TITLE_BG = 'data:image/jpeg;base64,' + base64.b64encode(open(os.path.join(HERE, 'title_bg.jpg'), 'rb').read()).decode()
inject = ('<script>window.RCB_ASSETS=' + json.dumps({'field': field, 'coins': coins}, separators=(',', ':')) + ';'
          'window.RCB_SOUNDS=' + json.dumps(snd, separators=(',', ':')) + ';window.RCB_TITLE_BG=' + json.dumps(TITLE_BG) + ';</script>\n')
k = src.index('<script>')
src = src[:k] + inject + src[k:]
web = src.replace("padding-left: max(8px, env(safe-area-inset-left, 0px));", "padding-left: max(16px, env(safe-area-inset-left, 0px));") \
         .replace("padding-right: max(8px, env(safe-area-inset-right, 0px));", "padding-right: max(16px, env(safe-area-inset-right, 0px));")
os.makedirs(os.path.join(HERE, 'dist'), exist_ok=True)
out = os.path.join(HERE, 'dist', '逆轉金幣2D_網頁版.html')
open(out, 'w', encoding='utf-8').write(web)
site = src.replace(PEER_TAG, '<script>' + src_site_peer + '</script>')
MQTT_TAG = '<script src="https://cdn.jsdelivr.net/npm/mqtt@5.10.1/dist/mqtt.min.js"></script>'
assert MQTT_TAG in site
site = site.replace(MQTT_TAG, '<script>' + open(os.path.join(HERE, 'mqtt.min.js'), encoding='utf-8').read().replace('</script>', '<\\/script>') + '</script>')
site = ('<!doctype html>\n<html lang="zh-Hant">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n</head>\n<body>\n' + site + '\n</body>\n</html>\n')
open(os.path.join(HERE, 'dist', 'ReverseCoin2D_site.html'), 'w', encoding='utf-8').write(site)
print(out, f'{os.path.getsize(out)/1e6:.1f} MB')
