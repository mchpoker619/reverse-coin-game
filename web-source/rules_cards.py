"""圖解規則卡片（內嵌 SVG）：給 3D／2D 網頁版的規則畫面用，也輸出 PNG 給 Python 2D 版。"""
V, CY, OR, GR, RD, MG, WH, BK, DIM = '#e4ff3a', '#18e0ff', '#ff8a00', '#4ade80', '#ff4d4d', '#ff4fd8', '#ecebe4', '#17151f', '#a39fb8'


def coin(x, y, r=17, camp='O', label='', tab=0, spot=False, ring=None):
    fill, txt = (WH, BK) if camp == 'O' else (BK, WH)
    out = []
    if spot:
        import math
        for base in (tab, tab + 180):
            a0, a1 = math.radians(base - 14.8176), math.radians(base + 14.8176)
            rr = r + 6
            x0, y0, x1, y1 = x + rr * math.cos(a0), y + rr * math.sin(a0), x + rr * math.cos(a1), y + rr * math.sin(a1)
            out.append(f'<path d="M{x0:.1f} {y0:.1f} A{rr} {rr} 0 0 1 {x1:.1f} {y1:.1f}" stroke="{RD}" stroke-width="6" fill="none" stroke-linecap="round"/>')
    if ring:
        out.append(f'<circle cx="{x}" cy="{y}" r="{r + 5}" fill="none" stroke="{ring}" stroke-width="3"/>')
    import math
    tx, ty = x + (r + 2) * math.cos(math.radians(tab)), y + (r + 2) * math.sin(math.radians(tab))
    out.append(f'<g transform="rotate({tab} {tx:.1f} {ty:.1f})"><rect x="{tx - 3:.1f}" y="{ty - 5:.1f}" width="7" height="10" rx="2" fill="#9d99aa" stroke="{BK}" stroke-width="1.5"/></g>')
    out.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{BK if camp == "O" else "#5d5870"}" stroke-width="2.5"/>')
    out.append(f'<circle cx="{x}" cy="{y}" r="{r * .55:.1f}" fill="none" stroke="{"#bdb8c9" if camp == "O" else "#3b3648"}" stroke-width="2"/>')
    if label:
        out.append(f'<text x="{x}" y="{y + 4.5}" text-anchor="middle" font-size="{11 if len(label) > 3 else 13}" font-weight="900" fill="{txt}">{label}</text>')
    return ''.join(out)


def arrow(x1, y1, x2, y2, col, w=4, dash=None, head=True):
    import math
    a = math.atan2(y2 - y1, x2 - x1)
    hx, hy = x2 - 9 * math.cos(a), y2 - 9 * math.sin(a)
    d = f' stroke-dasharray="{dash}"' if dash else ''
    s = f'<line x1="{x1}" y1="{y1}" x2="{hx:.1f}" y2="{hy:.1f}" stroke="{col}" stroke-width="{w}" stroke-linecap="round"{d}/>'
    if head:
        p1 = (x2 - 12 * math.cos(a - .5), y2 - 12 * math.sin(a - .5)); p2 = (x2 - 12 * math.cos(a + .5), y2 - 12 * math.sin(a + .5))
        s += f'<path d="M{x2} {y2} L{p1[0]:.1f} {p1[1]:.1f} L{p2[0]:.1f} {p2[1]:.1f}Z" fill="{col}"/>'
    return s


def text(x, y, t, col=WH, size=12, anchor='middle', weight=800):
    return f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" fill="{col}">{t}</text>'


def tag(x, y, t, bg, fg=BK, w=None):
    w = w or (len(t) * 12 + 14)
    return f'<rect x="{x - w / 2}" y="{y - 11}" width="{w}" height="22" rx="11" fill="{bg}"/>' + text(x, y + 4.5, t, fg, 12, 'middle', 900)


CARDS = []


def card(title, svg, cap):
    CARDS.append((title, svg, cap))


# 1 組隊
card('① 組隊', coin(55, 62, camp='O', label='7000') + coin(120, 62, camp='O', label='5000') + coin(185, 62, camp='O', label='3000')
     + text(120, 112, '合計 15,000 ≤ 15,000', GR, 15) + text(120, 134, '雙值幣算 M 值＝（正＋反）÷2', DIM, 11),
     '每方一定要 3 枚、同一隊不可重複，M 值合計不能超過 15,000。')
# 2 陣營
card('② 猜拳選陣營、擲金幣先攻',
     text(46, 66, '✊', WH, 34) + text(46, 90, '猜拳', DIM, 11) + arrow(70, 58, 96, 58, V, 3)
     + coin(122, 46, 14, 'O') + coin(122, 86, 14, 'X') + text(122, 116, '勝方選邊', DIM, 11) + arrow(146, 58, 172, 58, V, 3)
     + coin(198, 58, 16, 'O') + text(198, 92, '擲金幣', DIM, 11) + text(198, 108, '決定先攻', DIM, 11),
     '先組隊再猜拳：贏的人選白（ORDER）或黑（XTREME），再擲金幣定先攻。')
# 3 後拉發射
card('③ 後拉發射（像彈弓）',
     coin(120, 72, camp='X', ring=V) + arrow(120, 52, 120, 10, CY, 4)
     + f'<line x1="120" y1="92" x2="120" y2="136" stroke="{OR}" stroke-width="8" stroke-linecap="round"/>'
     + text(150, 124, '往後拉', OR, 12, 'start') + text(150, 140, '越長越大力', DIM, 11, 'start')
     + text(90, 28, '放開發射', CY, 12, 'end')
     + f'<rect x="14" y="40" width="18" height="90" rx="5" fill="#2a2638" stroke="{DIM}"/><rect x="16" y="78" width="14" height="50" rx="4" fill="{V}"/>'
     + text(23, 34, '力量', DIM, 10),
     '點自己的金幣，按住往反方向拉，拉越長力量越大（上限 100%），放開後跑精準度。')
# 4 精準度
card('④ 精準度條',
     f'<rect x="20" y="30" width="200" height="22" rx="6" fill="#2a2638"/><rect x="113" y="30" width="14" height="22" fill="{GR}"/>'
     + f'<line x1="120" y1="24" x2="120" y2="58" stroke="{WH}" stroke-width="2"/>' + text(120, 74, 'PERFECT＝不偏', GR, 13)
     + coin(120, 124, 13, 'X') + arrow(120, 110, 120, 84, CY, 3) + arrow(120, 112, 82, 92, RD, 3, '4 3') + arrow(120, 112, 158, 92, RD, 3, '4 3')
     + text(60, 104, '最多偏 70°', RD, 11) + text(186, 104, '最多偏 70°', RD, 11),
     '停在中間綠區不偏；離開綠區至少偏 5°，越靠邊越歪（最多左右 70°）並帶弧線。')
# 5 旋轉
card('⑤ 旋轉（可在開場關閉）',
     coin(60, 110, camp='X') + f'<path d="M38 88 A30 30 0 0 1 84 86" stroke="{MG}" stroke-width="4" fill="none"/>'
     + f'<path d="M84 86 l-2 -10 l9 5z" fill="{MG}"/>' + f'<path d="M60 88 Q80 30 190 30" stroke="{CY}" stroke-width="4" fill="none" stroke-dasharray="7 5"/>'
     + text(178, 56, '右旋 → 往右彎', CY, 12) + text(180, 96, 'Z 左旋 ／ X 右旋', WH, 12) + text(180, 116, '各 3 段', DIM, 11)
     + text(180, 134, '越強，綠區越窄', MG, 11),
     '旋轉會走弧線、撞到對手會把旋轉傳過去並帶偏、撞邊框反彈角度改變。輔助線會跟著彎。')
# 6 弱點
card('⑥ 弱點（弱點）',
     coin(120, 75, 30, 'O', '', 0, spot=True) + arrow(208, 75, 160, 75, CY, 4) + text(200, 60, '打這裡', CY, 12)
     + text(40, 42, '開關側', RD, 12) + text(40, 112, '和正對面', RD, 12) + text(40, 128, '各 ±15°', DIM, 11),
     '開關（小突起）那一側和正對面是弱點。用力打中 → 金幣彈起翻面；打其他地方再大力也不會翻。')
# 7 翻面判定
card('⑦ 彈起後：顏色決定',
     coin(120, 34, 15, 'O') + f'<path d="M108 54 Q120 66 132 54" stroke="{V}" stroke-width="3" fill="none"/>' + text(120, 74, '落地 正／反 各 1/2', DIM, 11)
     + arrow(100, 80, 64, 98, RD, 3) + arrow(140, 80, 176, 98, GR, 3)
     + coin(52, 116, 13, 'X') + tag(52, 138, '換色＝OUT', RD, WH, 84)
     + coin(188, 116, 13, 'O') + tag(186, 138, '同色→OX 對決', GR, BK, 104),
     '防守方翻成對方顏色直接淘汰；仍是自己顏色就進入 OX 對決。')
# 8 OX 對決
card('⑧ OX 對決',
     coin(60, 66, 24, 'X', '5000') + text(60, 108, '攻擊方', DIM, 12) + text(120, 74, 'vs', WH, 18)
     + coin(180, 66, 24, 'O', '5000') + text(180, 108, '防守方', DIM, 12)
     + tag(120, 134, '守 ≥ 攻 → 存活（平手守方勝）', GR, BK, 220),
     '守方數值 ≥ 攻方就存活，留在停下的位置；小於就淘汰。')
# 9 雙值幣
card('⑨ 雙值幣',
     coin(64, 70, 26, 'O', '8000') + arrow(98, 70, 140, 70, V, 4) + text(119, 58, '核心翻面', V, 11)
     + coin(176, 70, 26, 'X', '4000') + text(120, 126, 'OX 對決用「翻面後」的數值', WH, 12),
     '例：烈焰獅王白面 8000 被打彈起 → 用黑面 4000 去比。')
# 10 邊框
card('⑩ 撞邊框：三種情形',
     f'<rect x="196" y="12" width="14" height="128" rx="3" fill="#6b4a2e"/>'
     + coin(46, 30, 12, 'X') + arrow(60, 30, 228, 30, RD, 4) + text(116, 22, '很快 → 飛出界', RD, 11)
     + coin(46, 76, 12, 'X') + arrow(60, 76, 190, 76, OR, 3, head=False) + arrow(190, 76, 120, 96, OR, 3) + text(110, 70, '不夠快 → 減速反彈', OR, 11)
     + coin(178, 124, 12, 'X', '', 0, spot=True) + text(98, 128, '弱點撞牆夠力 → 翻面', RD, 11),
     '垂直撞擊夠快飛出場外；不夠快就反彈；如果是自己的弱點撞牆且夠力，也會彈起翻面。')
# 11 出界與放回場
card('⑪ 防守方被撞出界',
     f'<rect x="20" y="14" width="140" height="122" rx="6" fill="none" stroke="#6b4a2e" stroke-width="6"/>'
     + coin(196, 40, 13, 'O') + arrow(182, 52, 120, 92, GR, 3, '5 4') + f'<circle cx="104" cy="104" r="30" fill="none" stroke="{GR}" stroke-width="2" stroke-dasharray="4 3"/>'
     + coin(104, 104, 13, 'O') + text(196, 76, '沒翻面', DIM, 11) + text(196, 92, '＝存活', GR, 12) + text(196, 120, '攻擊方', WH, 11) + text(196, 136, '放回場內', WH, 11),
     '沒彈起的金幣 Safe，由主人放回場內任何位置（離其他金幣至少 1 枚，方向可調整）。')
# 12 自滅
card('⑫ 自滅（攻擊方）',
     f'<rect x="150" y="14" width="12" height="122" rx="3" fill="#6b4a2e"/>'
     + coin(60, 44, 14, 'X') + arrow(76, 44, 200, 44, RD, 3) + coin(214, 44, 14, 'X') + tag(120, 66, '自己出界＝OUT', RD, WH, 120)
     + coin(60, 112, 14, 'X') + text(60, 140, '自爆換色', DIM, 11) + tag(150, 112, '翻成對方色＝OUT', RD, WH, 140),
     '自己回合自己的金幣出界（含隊友）、或自爆翻成對方顏色都淘汰；沒碰到任何金幣＝無效攻擊。')
# 13 時間
card('⑬ 限時規則',
     f'<circle cx="62" cy="62" r="34" fill="{V}" stroke="{BK}" stroke-width="4"/>' + text(62, 74, '18', BK, 32, 'middle', 900)
     + text(62, 116, '每回合 30 秒', WH, 12) + text(62, 132, '超時＝放棄換人', RD, 11)
     + f'<rect x="128" y="38" width="96" height="32" rx="16" fill="#2a2638" stroke="{DIM}"/>' + text(176, 60, '全場 8:00', WH, 15)
     + text(176, 96, '時間到比開場', WH, 12) + text(176, 112, 'M 值合計', WH, 12) + text(176, 132, '少的一方獲勝', GR, 13),
     '每回合 30 秒內要出手；全場 8 分鐘，時間到比開場三枚 M 值合計，較少的一方勝。')
# 14 勝利
card('⑭ 勝利條件',
     coin(50, 60, 16, 'O', '') + coin(94, 60, 16, 'O', '') + coin(138, 60, 16, 'O', '')
     + ''.join(f'<path d="M{x - 12} 48 L{x + 12} 72 M{x + 12} 48 L{x - 12} 72" stroke="{RD}" stroke-width="5" stroke-linecap="round"/>' for x in (50, 94, 138))
     + text(196, 68, '獲勝！', V, 20, 'middle', 900) + text(120, 112, '淘汰對手全部金幣就贏', WH, 13) + text(120, 132, '或時間到比 M 值', DIM, 11),
     '把對手的金幣全部淘汰即獲勝；兩邊同時全滅為平手。')


def svg(body):
    return (f'<svg viewBox="0 0 240 150" role="img" aria-hidden="true" font-family="Noto Sans TC, PingFang TC, Microsoft JhengHei, sans-serif">'
            f'<rect width="240" height="150" rx="10" fill="#14121c"/>{body}</svg>')


def html():
    return '<div class="rgrid">' + ''.join(
        f'<figure class="rcard">{svg(b)}<figcaption><b>{t}</b><span>{c}</span></figcaption></figure>' for t, b, c in CARDS) + '</div>'


CSS = '''.rgrid { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 10px; margin: 6px 0 10px; }
.rcard { margin: 0; background: var(--panel2); border: 1px solid var(--line); border-radius: 12px; overflow: hidden; display: grid; }
.rcard svg { display: block; width: 100%; height: auto; }
.rcard figcaption { padding: 8px 10px 10px; display: grid; gap: 3px; font-size: 13px; line-height: 1.5; color: var(--dim); }
.rcard figcaption b { color: var(--volt); font-size: 14px; }
details.rtext summary { cursor: pointer; font-weight: 800; color: var(--text); margin: 4px 0 8px; }'''

def page():
    return ('<!doctype html><html><head><meta charset="utf-8"><style>:root{--panel2:#26223a;--line:#3a3550;--dim:#a39fb8;--volt:#e4ff3a;--text:#ece9f5}'
            'body{margin:0;background:#1b1828;font-family:"Noto Sans TC",sans-serif;width:1000px;padding:12px}' + CSS.replace('minmax(230px, 1fr)', '230px') +
            '.rgrid{grid-template-columns:repeat(4,240px)}</style></head><body>' + html() + '</body></html>')


if __name__ == '__main__':
    open('/home/claude/reverse_coin_3d/dist/rules_cards.html', 'w', encoding='utf-8').write(page())
    print(len(CARDS), 'cards', len(html()), 'chars')
