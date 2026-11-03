# AL_WARD_v200 — تصميم جديد كامل ("Rose Noir") مع الإبقاء على كل منطق Supabase
import os
import json
import math
from datetime import datetime, timezone
import requests

from kivy.app import App
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.graphics import (
    Color, RoundedRectangle, Ellipse, Rectangle, Line, Triangle,
    StencilPush, StencilPop, StencilUse, StencilUnUse,
    PushMatrix, PopMatrix, Rotate,
)
from kivy.graphics.texture import Texture
from kivy.properties import StringProperty, ListProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.screenmanager import Screen, ScreenManager, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.image import Image, AsyncImage
from kivy.utils import get_color_from_hex

try:
    import arabic_reshaper
    from bidi.algorithm import get_display
    def ar(text):
        return get_display(arabic_reshaper.reshape(str(text)))
except Exception:
    def ar(text):
        return str(text)

SUPABASE_URL = "https://enupzygislseoowiqbzf.supabase.co"
SUPABASE_KEY = "sb_publishable_5tSTskZO2kWeUOTg1H-6vA_WPeS7AHm"

FONT_CANDIDATES = [
    "/storage/emulated/0/Download/NotoNaskhArabic-VariableFont_wght.ttf",
    "/storage/emulated/0/Download/NotoNaskhArabic-Regular.ttf",
    "/storage/emulated/0/Download/NotoNaskhArabicUI-Regular.ttf",
    "/storage/emulated/0/Download/NotoSansArabic-Regular.ttf",
    "/system/fonts/NotoNaskhArabic-Regular.ttf",
    "/system/fonts/NotoNaskhArabicUI-Regular.ttf",
    "/system/fonts/NotoSansArabic-Regular.ttf",
    "/system/fonts/NotoSansArabicUI-Regular.ttf",
]
FONT_PATH = next((p for p in FONT_CANDIDATES if os.path.exists(p)), "Roboto")

DATA_FILE = os.path.join(os.path.dirname(__file__), "alward_data.json")
DEFAULT_DATA = {
    "username": "mohsen12",
    "status": "...",
    "join": "2025/09/16",
    "avatar": "",
}



# ═══════════════════════════════════════════════════════════════
#  الثيم الجديد — "Rose Noir"
# ═══════════════════════════════════════════════════════════════
def hexa(h, a=1.0):
    c = list(get_color_from_hex(h))
    c[3] = a
    return tuple(c)


BG = hexa("#07050D")
BG_TOP = hexa("#1D1131")
PANEL = hexa("#120D1D")
CARD = hexa("#1A1328")
CARD2 = hexa("#251C38")
FIELD = hexa("#140E21")
BORDER = (1, 1, 1, .08)
ACCENT = hexa("#F2517F")
ACCENT_END = hexa("#B8337E")
GOLD = hexa("#E8C27A")
VIOLET = hexa("#6B3FA0")
HERO_A = hexa("#4B2A7A")
HERO_B = hexa("#B8337E")
TEXT = hexa("#F6F0F8")
MUTED = hexa("#9A8FAE")
GREEN = hexa("#2FD38A")
RED = hexa("#7E3035")
BLUE = hexa("#4A2F73")
WHITE = (1, 1, 1, 1)
DANGER_FILL = (1, .36, .45, .12)
DANGER_BORDER = (1, .36, .45, .38)
DANGER_TXT = hexa("#FF7A8C")
AVATAR_COLORS = [
    hexa("#C2416B"), hexa("#7C4DBA"), hexa("#2E8B9A"),
    hexa("#D9822B"), hexa("#4A6FD8"), hexa("#2FA27A"),
]

Window.clearcolor = BG

_TEX = {}


def gradient(name, stops, vertical=False, steps=48):
    """يرسم تدرجاً لونياً كـ Texture (أفقي أو عمودي من الأسفل للأعلى)."""
    if name in _TEX:
        return _TEX[name]
    pix = bytearray()
    for i in range(steps):
        t = i / (steps - 1)
        seg = t * (len(stops) - 1)
        k = min(int(seg), len(stops) - 2)
        f = seg - k
        a, b = stops[k], stops[k + 1]
        for c in range(4):
            pix.append(int(255 * (a[c] + (b[c] - a[c]) * f)))
    size = (1, steps) if vertical else (steps, 1)
    tex = Texture.create(size=size, colorfmt="rgba")
    tex.blit_buffer(bytes(pix), colorfmt="rgba", bufferfmt="ubyte")
    tex.mag_filter = "linear"
    tex.min_filter = "linear"
    _TEX[name] = tex
    return tex


def accent_tex():
    return gradient("accent", [ACCENT, ACCENT_END])


def paint_background(w):
    """خلفية الشاشة: تدرج بنفسجي داكن مع توهجات وردية وبنفسجية ناعمة."""
    layers = []
    with w.canvas.before:
        Color(1, 1, 1, 1)
        bg = Rectangle(texture=gradient("bg", [BG, BG_TOP], vertical=True),
                       pos=w.pos, size=w.size)
        for which, col in enumerate((ACCENT, VIOLET)):
            for i in range(6):
                Color(col[0], col[1], col[2], .032)
                layers.append((which, i, Ellipse()))

    def sync(*_):
        bg.pos, bg.size = w.pos, w.size
        for which, i, e in layers:
            base = w.width * (.95 if which == 0 else 1.25)
            r = base * (1 - i * .15) / 2
            if which == 0:
                cx, cy = w.right - w.width * .08, w.top - w.width * .10
            else:
                cx, cy = w.x + w.width * .05, w.y + w.height * .12
            e.pos = (cx - r, cy - r)
            e.size = (2 * r, 2 * r)

    w.bind(pos=sync, size=sync)
    sync()


def _rr(x, y, w, h, r):
    r = max(.5, min(r, w / 2.0, h / 2.0))
    return (x, y, max(w, 1), max(h, 1), r)


class Card(BoxLayout):
    """بطاقة بحواف دائرية وإطار خفيف. تقبل تدرجاً لونياً اختيارياً."""

    def __init__(self, fill=CARD, border=BORDER, radius=18, texture=None, **kw):
        super().__init__(**kw)
        self._radius = dp(radius)
        with self.canvas.before:
            self._fillc = Color(*(WHITE if texture is not None else fill))
            shape_kw = {"texture": texture} if texture is not None else {}
            self._shape = RoundedRectangle(
                pos=self.pos, size=self.size,
                radius=[self._radius], **shape_kw)
            if border:
                Color(*border)
                self._line = Line(
                    rounded_rectangle=_rr(self.x, self.y, self.width, self.height, self._radius),
                    width=1)
            else:
                self._line = None
        self._base_fill = fill
        self._has_tex = texture is not None
        self.bind(pos=self._sync_card, size=self._sync_card)

    def _sync_card(self, *_):
        self._shape.pos = self.pos
        self._shape.size = self.size
        if self._line is not None:
            self._line.rounded_rectangle = _rr(
                self.x, self.y, self.width, self.height, self._radius)

    def set_pressed(self, down):
        if self._has_tex or self._fillc is None:
            return
        if down:
            c = self._base_fill
            self._fillc.rgba = (min(1, c[0] + .06), min(1, c[1] + .06),
                                min(1, c[2] + .08), c[3])
        else:
            self._fillc.rgba = self._base_fill


class ListRow(ButtonBehavior, Card):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(state=lambda *_: self.set_pressed(self.state == "down"))


class GoldButton(Button):
    """الزر الرئيسي: تدرج وردي مع توهج خفيف."""

    def __init__(self, **kwargs):
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", (0, 0, 0, 0))
        kwargs.setdefault("color", WHITE)
        kwargs.setdefault("font_name", FONT_PATH)
        kwargs.setdefault("font_size", "15sp")
        if isinstance(kwargs.get("text"), str):
            kwargs["text"] = ar(kwargs["text"])
        super().__init__(**kwargs)
        with self.canvas.before:
            Color(ACCENT[0], ACCENT[1], ACCENT[2], .22)
            self.glow = RoundedRectangle(radius=[dp(20)])
            self.tint = Color(1, 1, 1, 1)
            self.shape = RoundedRectangle(texture=accent_tex(), radius=[dp(16)])
        self.bind(pos=self.sync, size=self.sync,
                  state=self._press, disabled=self._press)
        self.sync()

    def _press(self, *_):
        if self.disabled:
            self.tint.rgba = (1, 1, 1, .45)
        elif self.state == "down":
            self.tint.rgba = (.82, .82, .82, 1)
        else:
            self.tint.rgba = (1, 1, 1, 1)

    def sync(self, *_):
        self.shape.pos = self.pos
        self.shape.size = self.size
        self.glow.pos = (self.x - dp(3), self.y - dp(5))
        self.glow.size = (self.width + dp(6), self.height + dp(6))


class DarkButton(Button):
    """الزر الثانوي: بطاقة داكنة بإطار رفيع. يقبل fill / border مخصصين."""

    def __init__(self, **kwargs):
        fill = kwargs.pop("fill", CARD2)
        border = kwargs.pop("border", BORDER)
        kwargs.setdefault("background_normal", "")
        kwargs.setdefault("background_down", "")
        kwargs.setdefault("background_color", (0, 0, 0, 0))
        kwargs.setdefault("color", TEXT)
        kwargs.setdefault("font_name", FONT_PATH)
        kwargs.setdefault("font_size", "15sp")
        if isinstance(kwargs.get("text"), str):
            kwargs["text"] = ar(kwargs["text"])
        super().__init__(**kwargs)
        self._base = fill
        with self.canvas.before:
            self._fillc = Color(*fill)
            self.shape = RoundedRectangle(radius=[dp(16)])
            Color(*border)
            self.outline = Line(rounded_rectangle=(0, 0, 1, 1, dp(16)), width=1)
        self.bind(pos=self.sync, size=self.sync, state=self._press)
        self.sync()

    def _press(self, *_):
        c = self._base
        if self.state == "down":
            self._fillc.rgba = (min(1, c[0] + .07), min(1, c[1] + .07),
                                min(1, c[2] + .09), min(1, c[3] + .1))
        else:
            self._fillc.rgba = c

    def sync(self, *_):
        self.shape.pos = self.pos
        self.shape.size = self.size
        self.outline.rounded_rectangle = _rr(
            self.x, self.y, self.width, self.height, dp(16))


# ───────────────────────── الأيقونات (مرسومة بالكود) ─────────────────────────
def _arc(cx, cy, rx, ry, a0, a1, n=20):
    pts = []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        pts += [cx + rx * math.cos(a), cy + ry * math.sin(a)]
    return pts


class Icon(Widget):
    kind = StringProperty("chat")
    color = ListProperty([1, 1, 1, 1])
    bg = ListProperty([0, 0, 0, 0])

    def __init__(self, kind="chat", color=TEXT, bg=CARD2, **kw):
        super().__init__(**kw)
        self.kind = kind
        self.color = list(color)
        self.bg = list(bg)
        self.bind(pos=self.redraw, size=self.redraw,
                  kind=self.redraw, color=self.redraw)
        self.redraw()

    def redraw(self, *_):
        self.canvas.clear()
        s = min(self.width, self.height) * .27
        if s <= 0:
            return
        cx, cy = self.center
        w = max(dp(1.5), s * .2)
        fn = getattr(self, "_i_" + self.kind, None)
        if fn is None:
            return
        with self.canvas:
            Color(*self.color)
            fn(cx, cy, s, w)

    def _i_back(self, cx, cy, s, w):
        Line(points=[cx - s * .3, cy + s * .6, cx + s * .3, cy, cx - s * .3, cy - s * .6],
             width=w, cap="round", joint="round")

    def _i_chev(self, cx, cy, s, w):
        Line(points=[cx + s * .3, cy + s * .6, cx - s * .3, cy, cx + s * .3, cy - s * .6],
             width=w, cap="round", joint="round")

    def _i_more(self, cx, cy, s, w):
        r = w * .95
        for dy in (-.62, 0, .62):
            Ellipse(pos=(cx - r, cy + dy * s - r), size=(2 * r, 2 * r))

    def _i_plus(self, cx, cy, s, w):
        Line(points=[cx - s * .8, cy, cx + s * .8, cy], width=w, cap="round")
        Line(points=[cx, cy - s * .8, cx, cy + s * .8], width=w, cap="round")

    def _i_send(self, cx, cy, s, w):
        tip = (cx - s * .85, cy)
        tr = (cx + s * .75, cy + s * .75)
        br = (cx + s * .75, cy - s * .75)
        mid = (cx + s * .3, cy)
        Triangle(points=[*tip, *tr, *mid])
        Triangle(points=[*tip, *mid, *br])

    def _i_chat(self, cx, cy, s, w):
        Line(rounded_rectangle=(cx - s, cy - s * .4, 2 * s, 1.3 * s, s * .42), width=w)
        Line(points=[cx - s * .35, cy - s * .4, cx - s * .65, cy - s * .95, cx + s * .1, cy - s * .4],
             width=w, joint="round", cap="round")

    def _i_user(self, cx, cy, s, w):
        cy = cy - s * .13
        Line(circle=(cx, cy + s * .62, s * .35), width=w)
        Line(points=_arc(cx, cy - s * .7, s * .85, s * .85, 0, 180), width=w, cap="round")

    def _i_users(self, cx, cy, s, w):
        cy = cy - s * .1
        Line(circle=(cx + s * .3, cy + s * .55, s * .3), width=w)
        Line(points=_arc(cx + s * .3, cy - s * .45, s * .75, s * .75, 0, 180), width=w, cap="round")
        Line(circle=(cx - s * .5, cy + s * .6, s * .24), width=w)
        Line(points=_arc(cx - s * .5, cy - s * .3, s * .55, s * .6, 90, 180), width=w, cap="round")

    def _i_sliders(self, cx, cy, s, w):
        for dy, kx in ((.62, -.35), (0, .4), (-.62, -.1)):
            Line(points=[cx - s, cy + dy * s, cx + s, cy + dy * s], width=w, cap="round")
            Ellipse(pos=(cx + kx * s - s * .24, cy + dy * s - s * .24), size=(s * .48, s * .48))

    def _i_shield(self, cx, cy, s, w):
        Line(points=[cx, cy + s, cx + s * .8, cy + s * .62, cx + s * .8, cy - s * .1,
                     cx, cy - s, cx - s * .8, cy - s * .1, cx - s * .8, cy + s * .62],
             width=w, close=True, joint="round")

    def _i_block(self, cx, cy, s, w):
        Line(circle=(cx, cy, s * .9), width=w)
        d = s * .64
        Line(points=[cx - d, cy + d, cx + d, cy - d], width=w, cap="round")

    def _i_bell(self, cx, cy, s, w):
        pts = _arc(cx, cy + s * .1, s * .7, s * .8, 0, 180)
        pts += [cx - s * .7, cy - s * .5, cx + s * .7, cy - s * .5]
        Line(points=pts, width=w, close=True, joint="round")
        Ellipse(pos=(cx - s * .2, cy - s * .95), size=(s * .4, s * .4))

    def _i_moon(self, cx, cy, s, w):
        Line(circle=(cx, cy, s * .9), width=w)
        Ellipse(pos=(cx - s * .9, cy - s * .9), size=(s * 1.8, s * 1.8),
                angle_start=0, angle_end=180)

    def _i_image(self, cx, cy, s, w):
        Line(rounded_rectangle=(cx - s, cy - s * .75, 2 * s, 1.5 * s, s * .25), width=w)
        Line(points=[cx - s * .8, cy - s * .5, cx - s * .2, cy + s * .1,
                     cx + s * .2, cy - s * .3, cx + s * .5, cy, cx + s * .8, cy - s * .3],
             width=w, joint="round", cap="round")
        Ellipse(pos=(cx + s * .35, cy + s * .22), size=(s * .3, s * .3))

    def _i_info(self, cx, cy, s, w):
        Line(circle=(cx, cy, s * .9), width=w)
        Line(points=[cx, cy - s * .1, cx, cy - s * .45], width=w, cap="round")
        Ellipse(pos=(cx - w * .8, cy + s * .25), size=(w * 1.6, w * 1.6))

    def _i_eye(self, cx, cy, s, w):
        Line(ellipse=(cx - s, cy - s * .55, 2 * s, 1.1 * s), width=w)
        Ellipse(pos=(cx - s * .27, cy - s * .27), size=(s * .54, s * .54))

    def _i_flag(self, cx, cy, s, w):
        Line(points=[cx - s * .6, cy - s, cx - s * .6, cy + s], width=w, cap="round")
        Line(points=[cx - s * .6, cy + s, cx + s * .8, cy + s * .55, cx - s * .6, cy + s * .1],
             width=w, joint="round")


class IconChip(Widget):
    """دائرة بأيقونة بداخلها (غير تفاعلية)."""

    def __init__(self, kind="info", color=TEXT, bg=None, grad=False, **kw):
        kw.setdefault("size_hint", (None, None))
        kw.setdefault("size", (dp(44), dp(44)))
        super().__init__(**kw)
        self.grad = grad
        with self.canvas.before:
            if grad:
                Color(ACCENT[0], ACCENT[1], ACCENT[2], .25)
                self._glow = Ellipse()
                Color(1, 1, 1, 1)
                self._bg = Ellipse(texture=accent_tex())
            else:
                Color(*(bg if bg else (0, 0, 0, 0)))
                self._bg = Ellipse()
        self.icon = Icon(kind, color, bg=(bg if bg else CARD2))
        self.add_widget(self.icon)
        self.bind(pos=self._sync, size=self._sync)
        self._sync()

    def _sync(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size
        if self.grad:
            self._glow.pos = (self.x - dp(3), self.y - dp(4))
            self._glow.size = (self.width + dp(6), self.height + dp(6))
        self.icon.pos = self.pos
        self.icon.size = self.size


class IconButton(ButtonBehavior, IconChip):
    def __init__(self, kind="info", color=TEXT, **kw):
        super().__init__(kind=kind, color=color, **kw)


def anchor(widget, width=None, height=None):
    """يضع عنصراً بحجم ثابت في وسط خانة (لمحاذاته عمودياً داخل الصفوف)."""
    box = AnchorLayout(size_hint=(None, 1), width=width or widget.width)
    box.add_widget(widget)
    return box


# ───────────────────────── الشعار: وردة مرسومة ─────────────────────────
class RoseLogo(Widget):
    def __init__(self, **kw):
        kw.setdefault("size_hint", (None, None))
        kw.setdefault("size", (dp(96), dp(96)))
        super().__init__(**kw)
        self.bind(pos=self.redraw, size=self.redraw)
        self.redraw()

    def redraw(self, *_):
        self.canvas.clear()
        cx, cy = self.center
        r = min(self.size) / 2.0
        with self.canvas:
            for i in range(5):
                Color(ACCENT[0], ACCENT[1], ACCENT[2], .035)
                rr = r * (1 - i * .09)
                Ellipse(pos=(cx - rr, cy - rr), size=(2 * rr, 2 * rr))
            layers = [
                (6, 0, hexa("#8E2A66", .92), .27, .78, .06),
                (6, 30, hexa("#B8337E", .92), .24, .66, .05),
                (5, 12, hexa("#F2517F", .95), .20, .52, .04),
                (5, 48, hexa("#FF7FA3", .95), .15, .38, .03),
            ]
            for count, offset, col, wk, hk, gap in layers:
                for k in range(count):
                    PushMatrix()
                    Rotate(angle=offset + k * (360.0 / count), origin=(cx, cy))
                    Color(*col)
                    Ellipse(pos=(cx - r * wk, cy + r * gap),
                            size=(r * wk * 2, r * hk))
                    PopMatrix()
            Color(hexa("#FFD3E0")[0], hexa("#FFD3E0")[1], hexa("#FFD3E0")[2], 1)
            c = r * .13
            Ellipse(pos=(cx - c, cy - c), size=(2 * c, 2 * c))


# ───────────────────────── الصورة الشخصية الدائرية ─────────────────────────
def make_image(cls, source):
    try:
        return cls(source=source, size_hint=(None, None), fit_mode="cover")
    except Exception:
        return cls(source=source, size_hint=(None, None),
                   allow_stretch=True, keep_ratio=False)


class CircularAvatar(FloatLayout):
    """صورة دائرية بإطار متدرج. تدعم الصور المحلية والروابط."""

    def __init__(self, source="", size=110, ring=True, initial="", **kwargs):
        if isinstance(size, (int, float)):
            size = (dp(size), dp(size))
        kwargs.setdefault("size_hint", (None, None))
        super().__init__(size=size, **kwargs)
        self.initial = str(initial or "?")[:1].upper()
        self.ring = ring
        self.inset = dp(3.5) if ring else dp(1)
        src = str(source or "")
        is_url = src.startswith("http")
        self.source = src if (src and (is_url or os.path.exists(src))) else ""

        self.image = None
        self.placeholder = None
        self.initial_label = None

        if self.source:
            self.image = make_image(AsyncImage if is_url else Image, self.source)
            self.add_widget(self.image)
        else:
            col = AVATAR_COLORS[ord(self.initial[0]) % len(AVATAR_COLORS)]
            self.placeholder = Widget(size_hint=(None, None))
            with self.placeholder.canvas:
                Color(*col)
                self.placeholder_shape = Ellipse()
            self.add_widget(self.placeholder)
            self.initial_label = Label(
                text=self.initial,
                font_name=FONT_PATH,
                font_size="30sp",
                color=WHITE,
                size_hint=(None, None),
                halign="center",
                valign="middle",
            )
            self.add_widget(self.initial_label)

        with self.canvas.before:
            if ring:
                Color(1, 1, 1, 1)
                self.ring_shape = Ellipse(
                    texture=gradient("ring", [ACCENT, GOLD], vertical=True))
            StencilPush()
            self.clip_shape = Ellipse()
            StencilUse()

        with self.canvas.after:
            StencilUnUse()
            self.clip_shape2 = Ellipse()
            StencilPop()

        self.bind(pos=self.sync, size=self.sync)
        self.sync()

    def sync(self, *_):
        inner_pos = (self.x + self.inset, self.y + self.inset)
        inner_size = (
            max(dp(1), self.width - 2 * self.inset),
            max(dp(1), self.height - 2 * self.inset),
        )
        self.clip_shape.pos = inner_pos
        self.clip_shape.size = inner_size
        self.clip_shape2.pos = inner_pos
        self.clip_shape2.size = inner_size
        if self.image is not None:
            self.image.pos = inner_pos
            self.image.size = inner_size
        if self.placeholder is not None:
            self.placeholder.pos = inner_pos
            self.placeholder.size = inner_size
            self.placeholder_shape.pos = inner_pos
            self.placeholder_shape.size = inner_size
        if self.initial_label is not None:
            self.initial_label.pos = inner_pos
            self.initial_label.size = inner_size
            self.initial_label.text_size = inner_size
            self.initial_label.font_size = max(dp(12), inner_size[0] * .42)
        if hasattr(self, "ring_shape"):
            self.ring_shape.pos = self.pos
            self.ring_shape.size = self.size


# ───────────────────────── حقل الإدخال ─────────────────────────
class FieldBox(BoxLayout):
    """حقل نص بحواف دائرية وإطار يضيء عند التركيز. النص الفعلي في self.input"""

    def __init__(self, hint="", password=False, height=54, draw=True, **kw):
        kw.setdefault("size_hint_y", None)
        super().__init__(height=dp(height), padding=[dp(4), 0], **kw)
        self.input = TextInput(
            hint_text=ar(hint) if hint else "",
            password=password,
            multiline=False,
            font_name=FONT_PATH,
            font_size="15sp",
            background_normal="",
            background_active="",
            background_color=(0, 0, 0, 0),
            foreground_color=TEXT,
            hint_text_color=MUTED,
            cursor_color=ACCENT,
            selection_color=(ACCENT[0], ACCENT[1], ACCENT[2], .35),
            halign="right",
            padding=[dp(14), dp(14), dp(14), dp(10)],
        )
        self.add_widget(self.input)
        self._draw = draw
        self.input.bind(size=self._pad, focus=self._focus)
        if draw:
            with self.canvas.before:
                Color(*FIELD)
                self._bg = RoundedRectangle(radius=[dp(16)])
                self._bc = Color(*BORDER)
                self._ln = Line(rounded_rectangle=(0, 0, 1, 1, dp(16)), width=1)
            self.bind(pos=self._sync, size=self._sync)
            self._sync()

    def _pad(self, *_):
        ti = self.input
        ph = max(dp(6), (ti.height - ti.line_height) / 2.0)
        ti.padding = [dp(14), ph, dp(14), ph]

    def _focus(self, _w, focused):
        if not self._draw:
            return
        self._bc.rgba = ACCENT if focused else BORDER
        self._ln.width = 1.6 if focused else 1

    def _sync(self, *_):
        self._bg.pos = self.pos
        self._bg.size = self.size
        self._ln.rounded_rectangle = _rr(self.x, self.y, self.width, self.height, dp(16))


# ───────────────────────── النوافذ المنبثقة ─────────────────────────
class StyledPopup(Popup):
    def __init__(self, **kw):
        kw.setdefault("background", "")
        kw["background_color"] = (0, 0, 0, 0)
        kw.setdefault("separator_color", ACCENT)
        kw.setdefault("separator_height", dp(2))
        kw.setdefault("title_font", FONT_PATH)
        kw.setdefault("title_color", TEXT)
        kw.setdefault("title_size", "17sp")
        kw.setdefault("title_align", "center")
        kw.setdefault("overlay_color", (0, 0, 0, .74))
        super().__init__(**kw)
        with self.canvas.before:
            Color(*CARD)
            self._r = RoundedRectangle(pos=self.pos, size=self.size, radius=[dp(24)])
            Color(*BORDER)
            self._l = Line(rounded_rectangle=_rr(self.x, self.y, self.width, self.height, dp(24)),
                           width=1)
        self.bind(pos=self._sync_pop, size=self._sync_pop)

    def _sync_pop(self, *_):
        self._r.pos = self.pos
        self._r.size = self.size
        self._l.rounded_rectangle = _rr(self.x, self.y, self.width, self.height, dp(24))


# ───────────────────────── صف الإعدادات ─────────────────────────
class ActionRow(ButtonBehavior, Card):
    def __init__(self, title, subtitle="", icon="info", **kwargs):
        kwargs.setdefault("size_hint_y", None)
        kwargs.setdefault("height", dp(72))
        super().__init__(orientation="horizontal", spacing=dp(12),
                         padding=[dp(14), dp(10)], fill=CARD, **kwargs)
        self.bind(state=lambda *_: self.set_pressed(self.state == "down"))
        chev = Icon("chev", MUTED, size_hint=(None, None), size=(dp(26), dp(26)))
        self.add_widget(anchor(chev, dp(26)))
        col = BoxLayout(orientation="vertical", padding=[0, dp(6)])
        t = Label(text=ar(title), font_name=FONT_PATH, font_size=dp(16), color=TEXT,
                  halign="right", valign="middle")
        t.bind(size=lambda w, v: setattr(w, "text_size", v))
        col.add_widget(t)
        if subtitle:
            sub = Label(text=ar(subtitle), font_name=FONT_PATH, font_size=dp(12),
                        color=MUTED, halign="right", valign="middle")
            sub.bind(size=lambda w, v: setattr(w, "text_size", v))
            col.add_widget(sub)
        self.add_widget(col)
        chip = IconChip(icon, color=ACCENT, bg=(ACCENT[0], ACCENT[1], ACCENT[2], .16))
        self.add_widget(anchor(chip, dp(44)))


class NavItem(ButtonBehavior, BoxLayout):
    """عنصر شريط التنقل السفلي: أيقونة + نص، والنشط يظهر بكبسولة وردية."""

    def __init__(self, title, kind, active=False, **kw):
        super().__init__(orientation="vertical", padding=[0, dp(7), 0, dp(4)],
                         spacing=dp(1), **kw)
        col = ACCENT if active else MUTED
        if active:
            with self.canvas.before:
                Color(ACCENT[0], ACCENT[1], ACCENT[2], .16)
                self._pill = RoundedRectangle(radius=[dp(18)])
            self.bind(pos=self._sync_pill, size=self._sync_pill)
            self._sync_pill()
        holder = AnchorLayout(size_hint_y=None, height=dp(28))
        holder.add_widget(Icon(kind, col, size_hint=(None, None), size=(dp(36), dp(36))))
        self.add_widget(holder)
        self.add_widget(Label(
            text=ar(title), font_name=FONT_PATH, font_size="11sp",
            color=col, size_hint_y=None, height=dp(16)))

    def _sync_pill(self, *_):
        self._pill.pos = (self.x + dp(2), self.y + dp(2))
        self._pill.size = (max(1, self.width - dp(4)), max(1, self.height - dp(4)))


def load_local():
    data = dict(DEFAULT_DATA)
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data.update(json.load(f))
    except Exception:
        pass
    return data


def save_local(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as exc:
        print("Local save error:", exc)


def headers(token=None):
    h = {"apikey": SUPABASE_KEY, "Content-Type": "application/json"}
    if token:
        h["Authorization"] = "Bearer " + token
    return h


class BaseScreen(Screen):
    def app(self):
        return App.get_running_app()

    def go(self, name):
        self.manager.current = name



class LoginScreen(BaseScreen):
    def login(self):
        username = self.ids.username.text.strip()
        password = self.ids.password.text
        if not username or not password:
            self.app().error("اكتب اسم المستخدم وكلمة المرور.")
            return
        self.ids.login_btn.disabled = True
        try:
            r = requests.post(
                SUPABASE_URL + "/auth/v1/token?grant_type=password",
                headers=headers(),
                json={"email": username.lower() + "@alward.app", "password": password},
                timeout=20,
            )
            data = r.json()
            if r.status_code != 200:
                self.app().error(
                    data.get("msg") or data.get("message") or
                    data.get("error_description") or "فشل تسجيل الدخول."
                )
                return
            app = self.app()
            app.token = data["access_token"]
            app.user_id = data["user"]["id"]
            app.username = username
            app.local["username"] = username
            save_local(app.local)
            app.ensure_profile()
            app.start_presence()
            self.manager.current = "home"
        except Exception as exc:
            self.app().error("تعذر الاتصال بالخادم.\n" + str(exc))
        finally:
            self.ids.login_btn.disabled = False

    def create_account(self):
        self.go("signup")


class SignupScreen(BaseScreen):
    def create(self):
        username = self.ids.username.text.strip()
        password = self.ids.password.text
        confirm = self.ids.confirm.text
        if len(username) < 3 or " " in username:
            self.app().error("اسم المستخدم يجب أن يكون 3 أحرف على الأقل وبدون مسافات.")
            return
        if len(password) < 6:
            self.app().error("كلمة المرور يجب أن تكون 6 أحرف على الأقل.")
            return
        if password != confirm:
            self.app().error("كلمتا المرور غير متطابقتين.")
            return
        try:
            r = requests.post(
                SUPABASE_URL + "/auth/v1/signup",
                headers=headers(),
                json={
                    "email": username.lower() + "@alward.app",
                    "password": password,
                    "data": {"username": username},
                },
                timeout=20,
            )
            data = r.json()
            if r.status_code not in (200, 201):
                self.app().error(
                    data.get("msg") or data.get("message") or
                    data.get("error_description") or "تعذر إنشاء الحساب."
                )
                return
            self.app().notice("تم إنشاء الحساب. سجل الدخول الآن.")
            self.manager.current = "login"
            self.manager.get_screen("login").ids.username.text = username
        except Exception as exc:
            self.app().error("تعذر الاتصال بالخادم.\n" + str(exc))


class HomeScreen(BaseScreen):
    def on_pre_enter(self, *_):
        self.load_chats()

    def filter_chats(self, text):
        query = (text or '').strip().lower()
        for item in getattr(self, '_chat_items', []):
            name = item.get('name', '').lower()
            preview = item.get('preview', '').lower()
            item['widget'].height = dp(82) if (not query or query in name or query in preview) else 0
            item['widget'].opacity = 1 if (not query or query in name or query in preview) else 0

    def load_chats(self):
        box = self.ids.chat_list
        box.clear_widgets()
        self._chat_items = []
        app = self.app()
        if not app.token:
            self.go('login')
            return
        try:
            r = requests.get(
                SUPABASE_URL + '/rest/v1/profiles?select=id,username,last_seen,avatar_url&order=username.asc',
                headers=headers(app.token), timeout=20,
            )
            if r.status_code != 200:
                app.error('تعذر تحميل المستخدمين.\n' + r.text)
                return

            users = [u for u in r.json() if str(u.get('id')) != str(app.user_id)]
            if not users:
                box.add_widget(app.label(
                    'لا يوجد مستخدمون آخرون حالياً.', 17, MUTED,
                    size_hint_y=None, height=dp(100)
                ))
                return

            for user in users:
                name = user.get('username') or 'مستخدم'
                online = app.is_online(user.get('last_seen'))
                preview, tm = 'ابدأ محادثة جديدة', ''

                try:
                    cid = self.find_conversation(user['id'])
                    if cid:
                        mr = requests.get(
                            SUPABASE_URL + '/rest/v1/messages?select=content,created_at&conversation_id=eq.'
                            + str(cid) + '&order=created_at.desc&limit=1',
                            headers=headers(app.token), timeout=10,
                        )
                        if mr.status_code == 200 and mr.json():
                            last = mr.json()[0]
                            preview = str(last.get('content', ''))[:55] or 'رسالة وسائط'
                            created = str(last.get('created_at', ''))
                            tm = created.split('T')[1][:5] if 'T' in created else ''
                except Exception as exc:
                    print('Preview error:', exc)

                row = self.make_chat_row(
                    name, preview, tm, online, user.get('avatar_url', ''), user['id']
                )
                box.add_widget(row)
                self._chat_items.append({
                    'widget': row, 'name': name, 'preview': preview
                })
        except Exception as exc:
            app.error('تعذر الاتصال بالخادم.\n' + str(exc))

    def find_conversation(self, other_id):
        app = self.app()
        r = requests.get(
            SUPABASE_URL + '/rest/v1/conversation_members?select=conversation_id&user_id=eq.'
            + str(app.user_id),
            headers=headers(app.token), timeout=12,
        )
        if r.status_code != 200:
            return None
        for item in r.json():
            cid = item.get('conversation_id')
            if not cid:
                continue
            m = requests.get(
                SUPABASE_URL + '/rest/v1/conversation_members?select=user_id&conversation_id=eq.'
                + str(cid),
                headers=headers(app.token), timeout=12,
            )
            if m.status_code != 200:
                continue
            ids = [str(x.get('user_id')) for x in m.json()]
            if str(other_id) in ids:
                return cid
        return None


    def make_chat_row(self, name, preview, tm, online, avatar_url, uid):
        app = self.app()
        row = ListRow(
            size_hint_y=None, height=dp(82), spacing=dp(10),
            padding=[dp(12), dp(8), dp(12), dp(8)], fill=CARD,
        )

        # يسار: الوقت + الحالة
        left = BoxLayout(orientation="vertical", size_hint_x=None,
                         width=dp(64), padding=[0, dp(8)])
        left.add_widget(app.label(tm, 11, MUTED, halign="left"))
        left.add_widget(app.label(
            "متصل" if online else "غير متصل", 10,
            GREEN if online else MUTED, halign="left"))
        row.add_widget(left)

        # الوسط: الاسم + آخر رسالة
        txt = BoxLayout(orientation="vertical", spacing=dp(2), padding=[0, dp(10)])
        txt.add_widget(app.label(name, 17, TEXT, halign="right", shorten=True))
        fresh = preview == "ابدأ محادثة جديدة"
        txt.add_widget(app.label(
            preview, 13, MUTED if fresh else hexa("#CFC4DE"),
            halign="right", shorten=True))
        row.add_widget(txt)

        # يمين: الصورة + نقطة الاتصال
        holder = FloatLayout(size_hint_x=None, width=dp(58))
        avatar = CircularAvatar(
            source=avatar_url or "", size=(dp(56), dp(56)), ring=online,
            initial=name, size_hint=(None, None),
            pos_hint={"center_x": .5, "center_y": .5})
        holder.add_widget(avatar)
        dot = Widget(size_hint=(None, None), size=(dp(15), dp(15)),
                     pos_hint={"right": 1, "y": .04})
        with dot.canvas:
            Color(*CARD)
            ring_c = Ellipse(pos=dot.pos, size=dot.size)
            Color(*(GREEN if online else MUTED))
            dot_c = Ellipse(pos=dot.pos, size=dot.size)

        def sync_dot(w, *_):
            ring_c.pos, ring_c.size = w.pos, w.size
            dot_c.pos = (w.x + dp(2.5), w.y + dp(2.5))
            dot_c.size = (w.width - dp(5), w.height - dp(5))

        dot.bind(pos=sync_dot, size=sync_dot)
        holder.add_widget(dot)
        row.add_widget(holder)

        row.bind(on_release=lambda *_: self.open_chat(uid, name))
        return row

    def open_chat(self, uid, name):
        chat = self.manager.get_screen('chat')
        chat.other_user_id = uid
        chat.other_username = name
        chat.open_real_chat()
        self.go('chat')


class ChatScreen(BaseScreen):
    other_user_id = None
    other_username = ""
    chat_id = None
    refresh_event = None

    def on_pre_leave(self, *_):
        self.stop_refresh()

    def stop_refresh(self):
        if self.refresh_event:
            self.refresh_event.cancel()
            self.refresh_event = None

    def open_real_chat(self):
        app = self.app()
        self.ids.title.text = self.other_username
        try:
            self.chat_id = self.find_conversation()
            if not self.chat_id:
                self.chat_id = self.create_conversation()
            if not self.chat_id:
                app.error("تعذر فتح المحادثة. تحقق من صلاحيات Supabase.")
                return
            self.load_messages()
            self.stop_refresh()
            self.refresh_event = Clock.schedule_interval(
                lambda dt: self.load_messages(), 3
            )
        except Exception as exc:
            app.error("خطأ في المحادثة.\n" + str(exc))

    def find_conversation(self):
        app = self.app()
        r = requests.get(
            SUPABASE_URL + "/rest/v1/conversation_members?select=conversation_id&user_id=eq."
            + str(app.user_id),
            headers=headers(app.token), timeout=12,
        )
        if r.status_code != 200:
            return None
        for item in r.json():
            cid = item.get("conversation_id")
            if not cid:
                continue
            m = requests.get(
                SUPABASE_URL + "/rest/v1/conversation_members?select=user_id&conversation_id=eq."
                + str(cid),
                headers=headers(app.token), timeout=12,
            )
            if m.status_code != 200:
                continue
            ids = [str(x.get("user_id")) for x in m.json()]
            if str(self.other_user_id) in ids:
                return cid
        return None

    def create_conversation(self):
        app = self.app()
        r = requests.post(
            SUPABASE_URL + "/rest/v1/rpc/create_private_conversation",
            headers=headers(app.token),
            json={"other_user_id": self.other_user_id},
            timeout=15,
        )
        if r.status_code not in (200, 201):
            print("Create conversation error:", r.text)
            return None
        data = r.json()
        if isinstance(data, str):
            return data
        if isinstance(data, dict):
            return data.get("create_private_conversation") or data.get("id")
        if isinstance(data, list) and data:
            return data[0] if isinstance(data[0], str) else data[0].get("id")
        return None

    def load_messages(self):
        app = self.app()
        if not self.chat_id or not app.token:
            return
        try:
            r = requests.get(
                SUPABASE_URL + "/rest/v1/messages?select=*&conversation_id=eq."
                + str(self.chat_id) + "&order=created_at.asc",
                headers=headers(app.token), timeout=15,
            )
            if r.status_code != 200:
                print("Load messages:", r.text)
                return
            self.render_messages(r.json())
        except Exception as exc:
            print("Load messages exception:", exc)


    def render_messages(self, messages):
        box = self.ids.messages
        box.clear_widgets()
        app = self.app()

        # فقاعات: عرض طبيعي للرسائل القصيرة، ولفّ تلقائي للطويلة.
        max_width = min(dp(340), Window.width * .76)
        horizontal_pad = dp(10)
        bubble_pad_x = dp(15)
        bubble_pad_y = dp(9)

        for msg in messages:
            content = str(msg.get("content", "")).strip()
            if not content:
                continue

            mine = str(msg.get("sender_id")) == str(app.user_id)
            created = str(msg.get("created_at", ""))
            tm = created.split("T", 1)[1][:5] if "T" in created else ""

            row = BoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                size_hint_x=1,
                spacing=dp(4),
                padding=[horizontal_pad, dp(3), horizontal_pad, dp(3)],
            )

            char_width = dp(8.8)
            estimated = max(dp(78), min(max_width, len(content) * char_width + bubble_pad_x * 2))
            if "\n" in content:
                estimated = min(max_width, max(estimated, dp(120)))
            if mine and tm:
                estimated = min(max_width, max(estimated, dp(138)))

            bubble = BoxLayout(
                orientation="vertical",
                size_hint=(None, None),
                width=estimated,
                padding=[bubble_pad_x, bubble_pad_y, bubble_pad_x, dp(6)],
                spacing=dp(1),
            )

            with bubble.canvas.before:
                if mine:
                    Color(1, 1, 1, 1)
                    shape = RoundedRectangle(
                        pos=bubble.pos, size=bubble.size,
                        radius=[dp(20), dp(20), dp(5), dp(20)],
                        texture=accent_tex())
                else:
                    Color(*CARD2)
                    shape = RoundedRectangle(
                        pos=bubble.pos, size=bubble.size,
                        radius=[dp(20), dp(20), dp(20), dp(5)])
            bubble.bind(
                pos=lambda w, *_a, s=shape: setattr(s, "pos", w.pos),
                size=lambda w, *_a, s=shape: setattr(s, "size", w.size),
            )

            text_width = max(dp(35), estimated - bubble_pad_x * 2)
            msg_label = Label(
                text=ar(content),
                font_name=FONT_PATH,
                font_size=dp(16),
                color=WHITE if mine else TEXT,
                halign="right",
                valign="middle",
                size_hint=(1, None),
                text_size=(text_width, None),
            )
            msg_label.bind(texture_size=lambda w, *_: setattr(w, "height", max(dp(24), w.texture_size[1])))
            msg_label.height = max(dp(24), msg_label.texture_size[1])
            bubble.add_widget(msg_label)

            if tm:
                meta_row = BoxLayout(
                    orientation="horizontal",
                    size_hint=(1, None),
                    height=dp(18),
                    spacing=dp(4),
                )
                if mine:
                    meta_row.add_widget(Label(
                        text=ar("تمت القراءة"),
                        font_name=FONT_PATH,
                        font_size="10sp",
                        color=(1, 1, 1, .82),
                        halign="left",
                        valign="middle",
                        size_hint_x=None,
                        width=dp(66),
                        text_size=(dp(66), dp(18)),
                        shorten=True,
                        shorten_from="right",
                    ))
                else:
                    meta_row.add_widget(Widget())

                meta_row.add_widget(Label(
                    text=tm,
                    font_name=FONT_PATH,
                    font_size="10sp",
                    color=(1, 1, 1, .78) if mine else MUTED,
                    halign="right",
                    valign="middle",
                    size_hint_x=None,
                    width=dp(48),
                    text_size=(dp(48), dp(18)),
                ))
                bubble.add_widget(meta_row)

            bubble.height = max(dp(50), msg_label.height + dp(15) + (dp(18) if tm else 0))
            row.height = bubble.height + dp(6)

            if mine:
                row.add_widget(Widget())
                row.add_widget(bubble)
            else:
                row.add_widget(bubble)
                row.add_widget(Widget())

            box.add_widget(row)

        Clock.schedule_once(lambda dt: setattr(self.ids.scroll, "scroll_y", 0), .1)

    def send(self):
        text = self.ids.message.text.strip()
        if not text or not self.chat_id:
            return
        app = self.app()
        try:
            r = requests.post(
                SUPABASE_URL + "/rest/v1/messages",
                headers={**headers(app.token), "Prefer": "return=representation"},
                json={
                    "conversation_id": self.chat_id,
                    "sender_id": app.user_id,
                    "content": text,
                },
                timeout=15,
            )
            if r.status_code not in (200, 201):
                app.error("تعذر إرسال الرسالة.\n" + r.text)
                return
            self.ids.message.text = ""
            self.load_messages()
        except Exception as exc:
            app.error("خطأ أثناء الإرسال.\n" + str(exc))

    def chat_actions(self):
        app = self.app()
        box = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(8))
        block = DarkButton(text="حظر المستخدم", size_hint_y=None, height=dp(52))
        report = DarkButton(text="إبلاغ عن المستخدم", size_hint_y=None, height=dp(52))
        cancel = GoldButton(text="إلغاء", size_hint_y=None, height=dp(52))
        box.add_widget(block); box.add_widget(report); box.add_widget(cancel)
        pop = StyledPopup(title=ar("إجراءات المحادثة"), content=box, size_hint=(.9, .42))

        def do_block(*_):
            try:
                r = requests.post(
                    SUPABASE_URL + "/rest/v1/blocked_users",
                    headers={**headers(app.token), "Prefer": "return=minimal"},
                    json={"user_id": app.user_id, "blocked_user_id": self.other_user_id},
                    timeout=15
                )
                if r.status_code in (200, 201):
                    pop.dismiss()
                    app.notice("تم حظر المستخدم.")
                else:
                    app.error("تعذر تنفيذ الحظر.\n" + r.text)
            except Exception as exc:
                app.error("تعذر الاتصال بالخادم.\n" + str(exc))

        def do_report(*_):
            pop.dismiss()
            report_screen = self.manager.get_screen("report")
            report_screen.target_user_id = self.other_user_id
            self.go("report")

        block.bind(on_release=do_block)
        report.bind(on_release=do_report)
        cancel.bind(on_release=pop.dismiss)
        pop.open()

    def pick_media(self, kind):
        chooser = FileChooserListView(
            path="/storage/emulated/0",
            filters=["*.png", "*.jpg", "*.jpeg", "*.webp", "*.mp4", "*.mov", "*.mkv", "*.*"]
        )
        box = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(8))
        buttons = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        box.add_widget(chooser); box.add_widget(buttons)
        cancel = DarkButton(text="إلغاء")
        choose = GoldButton(text="اختيار")
        buttons.add_widget(cancel); buttons.add_widget(choose)
        pop = StyledPopup(title=ar("اختيار " + kind), content=box, size_hint=(.95, .88))
        cancel.bind(on_release=pop.dismiss)

        def picked(*_):
            if chooser.selection:
                path = chooser.selection[0]
                # Keep the existing messages table untouched: media becomes
                # an explicit message until a Storage bucket/attachment schema
                # is configured for the project.
                self.ids.message.text = f"[{kind}] {os.path.basename(path)}"
                pop.dismiss()

        choose.bind(on_release=picked)
        pop.open()

    def voice_info(self):
        self.app().notice("واجهة التسجيل الصوتي جاهزة. ربط التخزين والتسجيل يحتاج إعداد Media/Storage في المشروع.")

    def back(self):
        self.stop_refresh()
        self.go("home")


class ProfileScreen(BaseScreen):
    def on_pre_enter(self, *_):
        self.refresh()

    def refresh(self):
        app = self.app()
        username = app.username or app.local.get("username", "mohsen12")
        status_value = app.local.get("status", "...")

        self.ids.profile_name.text = username
        self.ids.info_username.text = username
        self.ids.status.text = ar(status_value)
        self.ids.join.text = app.local.get("join", "2025/09/16")

        # Keep one avatar instance. Repositioning is always relative to the
        # hero card, so it can never fall into the edit/action row.
        avatar = self.ids.profile_avatar
        src = str(app.local.get("avatar", ""))
        if src and os.path.exists(src):
            # Recreate only the image widget; the avatar's geometry remains.
            avatar.source = src
            if avatar.image is None:
                avatar.image = make_image(Image, src)
                avatar.add_widget(avatar.image)
            else:
                avatar.image.source = src
        else:
            if avatar.image is not None:
                avatar.remove_widget(avatar.image)
                avatar.image = None
            avatar.source = ""
            avatar.initial = (str(username)[:1] or "?").upper()
            if avatar.initial_label is not None:
                avatar.initial_label.text = avatar.initial
            if avatar.placeholder is None:
                avatar.placeholder = Widget(size_hint=(None, None))
                with avatar.placeholder.canvas:
                    Color(*BLUE)
                    avatar.placeholder_shape = Ellipse()
                avatar.add_widget(avatar.placeholder, index=len(avatar.children))
        avatar.sync()

    def _place_profile_avatar(self):
        hero = self.ids.profile_hero
        avatar = self.ids.profile_avatar
        avatar.pos = ((hero.width - avatar.width) / 2, dp(25))
        camera = self.ids.profile_camera
        camera.pos = (avatar.x + avatar.width - dp(12), avatar.y + dp(2))

    def edit_name(self):
        app = self.app()
        box = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
        inp = TextInput(
            text=self.ids.profile_name.text, multiline=False,
            font_name=FONT_PATH, size_hint_y=None, height=dp(50),
            background_normal="", background_color=CARD,
            foreground_color=TEXT, hint_text_color=MUTED,
            halign="right"
        )
        ok = GoldButton(text="حفظ الاسم", size_hint_y=None, height=dp(50))
        cancel = DarkButton(text="إلغاء", size_hint_y=None, height=dp(50))
        box.add_widget(inp); box.add_widget(ok); box.add_widget(cancel)
        pop = StyledPopup(
            title=ar("تعديل اسم المستخدم"), content=box,
            size_hint=(.9, .42), auto_dismiss=False
        )

        def save_name(*_):
            value = inp.text.strip()
            if len(value) < 3 or " " in value:
                app.error("اسم المستخدم يجب أن يكون 3 أحرف على الأقل وبدون مسافات.")
                return
            try:
                r = requests.patch(
                    SUPABASE_URL + "/rest/v1/profiles?id=eq." + str(app.user_id),
                    headers={**headers(app.token), "Prefer": "return=minimal"},
                    json={"username": value}, timeout=15
                )
                if r.status_code not in (200, 204):
                    app.error("تعذر حفظ الاسم في قاعدة البيانات.\n" + r.text)
                    return
            except Exception as exc:
                app.error("تعذر الاتصال بالخادم.\n" + str(exc))
                return
            app.local["username"] = value
            app.username = value
            save_local(app.local)
            self.refresh()
            pop.dismiss()

        ok.bind(on_release=save_name)
        cancel.bind(on_release=pop.dismiss)
        pop.open()

    def edit_status(self):
        app = self.app()
        box = BoxLayout(orientation="vertical", padding=dp(14), spacing=dp(10))
        inp = TextInput(
            text=app.local.get("status", "..."), multiline=False,
            font_name=FONT_PATH, size_hint_y=None, height=dp(50),
            background_normal="", background_color=CARD,
            foreground_color=TEXT, hint_text_color=MUTED, halign="right"
        )
        ok = GoldButton(text="حفظ الحالة", size_hint_y=None, height=dp(50))
        cancel = DarkButton(text="إلغاء", size_hint_y=None, height=dp(50))
        box.add_widget(inp); box.add_widget(ok); box.add_widget(cancel)
        pop = StyledPopup(
            title=ar("تغيير الحالة الشخصية"), content=box,
            size_hint=(.9, .42), auto_dismiss=False
        )

        def save_status(*_):
            value = inp.text.strip() or "..."
            app.local["status"] = value
            save_local(app.local)
            self.refresh()
            pop.dismiss()

        ok.bind(on_release=save_status)
        cancel.bind(on_release=pop.dismiss)
        pop.open()

    def choose_photo(self):
        chooser = FileChooserListView(
            path="/storage/emulated/0",
            filters=["*.png", "*.jpg", "*.jpeg", "*.webp"]
        )
        box = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(8))
        buttons = BoxLayout(size_hint_y=None, height=dp(50), spacing=dp(8))
        box.add_widget(chooser); box.add_widget(buttons)
        pop = StyledPopup(
            title=ar("اختيار الصورة الشخصية"),
            content=box, size_hint=(.95, .88), auto_dismiss=False
        )
        cancel = DarkButton(text="إلغاء")
        choose = GoldButton(text="اختيار الصورة")
        buttons.add_widget(cancel); buttons.add_widget(choose)
        cancel.bind(on_release=pop.dismiss)

        def picked(*_):
            if chooser.selection:
                self.app().local["avatar"] = chooser.selection[0]
                save_local(self.app().local)
                self.refresh()
                pop.dismiss()

        choose.bind(on_release=picked)
        pop.open()


class UsersScreen(BaseScreen):
    def on_pre_enter(self, *_):
        self.load_users()


    def make_user_row(self, user):
        app = self.app()
        uid = user.get("id")
        name = user.get("username") or "مستخدم"
        online = app.is_online(user.get("last_seen"))
        avatar_url = user.get("avatar_url") or ""

        row = ListRow(
            size_hint_y=None, height=dp(84), spacing=dp(10),
            padding=[dp(12), dp(8), dp(12), dp(8)], fill=CARD,
        )
        row.add_widget(anchor(
            Icon("chev", MUTED, size_hint=(None, None), size=(dp(26), dp(26))), dp(26)))

        info = BoxLayout(orientation="vertical", spacing=dp(1), padding=[0, dp(12)])
        info.add_widget(app.label(name, 18, TEXT, halign="right", shorten=True))
        info.add_widget(app.label(
            "متصل الآن" if online else "غير متصل", 12,
            GREEN if online else MUTED, halign="right"))
        row.add_widget(info)

        holder = FloatLayout(size_hint_x=None, width=dp(62))
        avatar = CircularAvatar(
            source=avatar_url, size=(dp(60), dp(60)), ring=online,
            initial=name, size_hint=(None, None),
            pos_hint={"center_x": .5, "center_y": .5})
        holder.add_widget(avatar)
        dot = Widget(size_hint=(None, None), size=(dp(16), dp(16)),
                     pos_hint={"right": 1, "y": .03})
        with dot.canvas:
            Color(*CARD)
            ring_c = Ellipse(pos=dot.pos, size=dot.size)
            Color(*(GREEN if online else MUTED))
            dot_c = Ellipse(pos=dot.pos, size=dot.size)

        def sync_dot(w, *_):
            ring_c.pos, ring_c.size = w.pos, w.size
            dot_c.pos = (w.x + dp(2.5), w.y + dp(2.5))
            dot_c.size = (w.width - dp(5), w.height - dp(5))

        dot.bind(pos=sync_dot, size=sync_dot)
        holder.add_widget(dot)
        row.add_widget(holder)

        row.bind(on_release=lambda *_: self.open_chat(uid, name))
        return row

    def load_users(self):
        box = self.ids.users_list
        box.clear_widgets()
        app = self.app()
        if not app.token:
            self.go("login")
            return
        try:
            r = requests.get(
                SUPABASE_URL + "/rest/v1/profiles?select=id,username,last_seen,avatar_url&order=username.asc",
                headers=headers(app.token), timeout=20,
            )
            if r.status_code != 200:
                app.error("تعذر تحميل المستخدمين.\n" + r.text)
                return

            users = [
                user for user in r.json()
                if str(user.get("id")) != str(app.user_id)
            ]
            if not users:
                box.add_widget(app.label(
                    "لا يوجد مستخدمون آخرون حالياً.", 17, MUTED,
                    size_hint_y=None, height=dp(100)
                ))
                return

            for user in users:
                box.add_widget(self.make_user_row(user))

        except Exception as exc:
            app.error("تعذر الاتصال بالخادم.\n" + str(exc))

    def open_chat(self, uid, name):
        chat = self.manager.get_screen("chat")
        chat.other_user_id = uid
        chat.other_username = name
        chat.open_real_chat()
        self.go("chat")


class BlockedUsersScreen(BaseScreen):
    def on_pre_enter(self, *_):
        self.load_blocked()

    def load_blocked(self):
        box = self.ids.blocked_list
        box.clear_widgets()
        app = self.app()
        if not app.token:
            self.go("login")
            return
        try:
            r = requests.get(
                SUPABASE_URL + "/rest/v1/blocked_users?select=id,blocked_user_id,blocked_profile:profiles!blocked_users_blocked_user_id_fkey(id,username)&user_id=eq."
                + str(app.user_id),
                headers=headers(app.token), timeout=15
            )
            if r.status_code != 200:
                box.add_widget(app.label(
                    "لا توجد قائمة حظر جاهزة في قاعدة البيانات حالياً.",
                    15, MUTED, size_hint_y=None, height=dp(80)
                ))
                return
            rows = r.json()
            if not rows:
                box.add_widget(app.label(
                    "قائمة المحظورين فارغة.", 16, MUTED,
                    size_hint_y=None, height=dp(80)
                ))
                return
            for row in rows:
                profile = row.get("blocked_profile") or {}
                name = profile.get("username", "مستخدم")
                b = ActionRow(name, "اضغط لإلغاء الحظر", icon="block")
                b.bind(on_release=lambda _, uid=row.get("blocked_user_id"): self.unblock(uid))
                box.add_widget(b)
        except Exception as exc:
            box.add_widget(app.label(
                "تعذر تحميل قائمة الحظر.", 15, MUTED,
                size_hint_y=None, height=dp(80)
            ))
            print("Blocked users:", exc)

    def unblock(self, uid):
        app = self.app()
        if not uid:
            return
        try:
            r = requests.delete(
                SUPABASE_URL + "/rest/v1/blocked_users?user_id=eq."
                + str(app.user_id) + "&blocked_user_id=eq." + str(uid),
                headers=headers(app.token), timeout=15
            )
            if r.status_code in (200, 204):
                self.load_blocked()
            else:
                app.error("تعذر إلغاء الحظر.\n" + r.text)
        except Exception as exc:
            app.error("تعذر الاتصال بالخادم.\n" + str(exc))


class ReportScreen(BaseScreen):
    def submit(self, reason):
        app = self.app()
        target = getattr(self, "target_user_id", None)
        if not target or not app.token:
            app.error("لا يوجد مستخدم للإبلاغ عنه.")
            return
        try:
            r = requests.post(
                SUPABASE_URL + "/rest/v1/reports",
                headers={**headers(app.token), "Prefer": "return=minimal"},
                json={
                    "reporter_id": app.user_id,
                    "reported_user_id": target,
                    "reason": reason,
                },
                timeout=15
            )
            if r.status_code in (200, 201):
                app.notice("تم إرسال البلاغ.")
                self.go("chat")
            else:
                app.error("تعذر إرسال البلاغ.\n" + r.text)
        except Exception as exc:
            app.error("تعذر الاتصال بالخادم.\n" + str(exc))


class PrivacyScreen(BaseScreen):
    def back(self):
        self.go("settings")



class SettingsScreen(BaseScreen):
    def logout(self):
        self.app().logout()

    def users(self):
        self.go("users")

    def profile(self):
        self.go("profile")

    def blocked(self):
        self.go("blocked")

    def privacy(self):
        self.go("privacy")

    def report(self, target_user_id):
        screen = self.manager.get_screen("report")
        screen.target_user_id = target_user_id
        self.go("report")

class ALWardApp(App):
    def build(self):
        self.title = "AL WARD"
        self.token = None
        self.user_id = None
        self.username = None
        self.presence_event = None
        self.local = load_local()

        sm = ScreenManager(transition=FadeTransition(duration=.12))
        sm.add_widget(self.make_login())
        sm.add_widget(self.make_signup())
        sm.add_widget(self.make_home())
        sm.add_widget(self.make_chat())
        sm.add_widget(self.make_profile())
        sm.add_widget(self.make_users())
        sm.add_widget(self.make_settings())
        sm.add_widget(self.make_blocked())
        sm.add_widget(self.make_privacy())
        sm.add_widget(self.make_report())
        sm.current = "login"
        return sm


    # ───────────────────────── أساسيات التصميم ─────────────────────────
    def base_root(self):
        root = BoxLayout(
            orientation="vertical",
            padding=[dp(14), dp(12), dp(14), dp(10)],
            spacing=dp(10),
        )
        paint_background(root)
        return root

    def panel(self):
        root = self.base_root()
        root.add_widget(Widget())
        return root

    def label(self, text, size=16, color=TEXT, **kwargs):
        kwargs.setdefault("font_name", FONT_PATH)
        kwargs.setdefault("font_size", dp(size))
        kwargs.setdefault("color", color)
        kwargs.setdefault("halign", "center")
        kwargs.setdefault("valign", "middle")
        lbl = Label(text=ar(text), **kwargs)
        if kwargs["halign"] != "center" and "text_size" not in kwargs:
            lbl.bind(size=lambda w, v: setattr(w, "text_size", v))
        return lbl

    def field(self, hint, password=False, height=54):
        box = FieldBox(hint=hint, password=password, height=height)
        return box, box.input

    def auth_card(self, height):
        return Card(
            orientation="vertical", size_hint_y=None, height=dp(height),
            padding=[dp(18), dp(18)], spacing=dp(10), fill=CARD, radius=26,
        )

    # ───────────────────────── تسجيل الدخول / إنشاء حساب ─────────────────────────
    def make_login(self):
        s = LoginScreen(name="login")
        root = self.panel()

        logo_row = AnchorLayout(size_hint_y=None, height=dp(104))
        logo_row.add_widget(RoseLogo(size=(dp(100), dp(100))))
        root.add_widget(logo_row)
        root.add_widget(self.label("AL WARD", 32, TEXT, size_hint_y=None, height=dp(48)))
        root.add_widget(self.label("تواصل بأناقة", 14, MUTED, size_hint_y=None, height=dp(26)))
        root.add_widget(Widget(size_hint_y=None, height=dp(6)))

        card = self.auth_card(372)
        card.add_widget(self.label("تسجيل الدخول", 21, TEXT, size_hint_y=None, height=dp(34)))
        card.add_widget(self.label("ادخل إلى حسابك للمتابعة", 13, MUTED,
                                   size_hint_y=None, height=dp(22)))
        ubox, u = self.field("اسم المستخدم")
        pbox, p = self.field("كلمة المرور", password=True)
        s.ids.username = u
        s.ids.password = p
        card.add_widget(ubox)
        card.add_widget(pbox)

        login = GoldButton(text="تسجيل الدخول", size_hint_y=None, height=dp(54))
        login.bind(on_release=lambda *_: s.login())
        s.ids.login_btn = login
        create = DarkButton(text="إنشاء حساب جديد", size_hint_y=None, height=dp(50))
        create.bind(on_release=lambda *_: s.create_account())
        card.add_widget(login)
        card.add_widget(create)
        root.add_widget(card)
        root.add_widget(Widget())
        s.add_widget(root)
        return s

    def make_signup(self):
        s = SignupScreen(name="signup")
        root = self.panel()

        logo_row = AnchorLayout(size_hint_y=None, height=dp(76))
        logo_row.add_widget(RoseLogo(size=(dp(72), dp(72))))
        root.add_widget(logo_row)
        root.add_widget(self.label("AL WARD", 26, TEXT, size_hint_y=None, height=dp(38)))
        root.add_widget(Widget(size_hint_y=None, height=dp(4)))

        card = self.auth_card(398)
        card.add_widget(self.label("إنشاء حساب جديد", 21, TEXT, size_hint_y=None, height=dp(34)))
        card.add_widget(self.label("انضم إلى AL WARD في ثوانٍ", 13, MUTED,
                                   size_hint_y=None, height=dp(22)))
        fields = []
        for hint, password in [
            ("اسم المستخدم", False),
            ("كلمة المرور", True),
            ("تأكيد كلمة المرور", True),
        ]:
            box, t = self.field(hint, password=password)
            fields.append(t)
            card.add_widget(box)
        s.ids.username, s.ids.password, s.ids.confirm = fields

        create = GoldButton(text="إنشاء الحساب", size_hint_y=None, height=dp(54))
        create.bind(on_release=lambda *_: s.create())
        back = DarkButton(text="العودة لتسجيل الدخول", size_hint_y=None, height=dp(48))
        back.bind(on_release=lambda *_: s.go("login"))
        card.add_widget(create)
        card.add_widget(back)
        root.add_widget(card)
        root.add_widget(Widget())
        s.add_widget(root)
        return s

    # ───────────────────────── الرئيسية ─────────────────────────
    def make_home(self):
        s = HomeScreen(name='home')
        root = self.base_root()

        top = BoxLayout(size_hint_y=None, height=dp(66), spacing=dp(10))
        settings = IconButton("sliders", color=TEXT, bg=CARD2)
        settings.bind(on_release=lambda *_: self.goto('settings'))
        top.add_widget(anchor(settings, dp(44)))
        top.add_widget(Widget())
        titles = BoxLayout(orientation="vertical", size_hint_x=None,
                           width=dp(150), padding=[0, dp(8)])
        titles.add_widget(self.label("AL WARD", 24, TEXT, halign="right"))
        titles.add_widget(self.label("محادثاتك الخاصة", 12, MUTED, halign="right"))
        top.add_widget(titles)
        top.add_widget(anchor(RoseLogo(size=(dp(50), dp(50))), dp(50)))
        root.add_widget(top)

        sbox, search = self.field('البحث في المحادثات...', height=50)
        search.bind(text=lambda w, value: s.filter_chats(value))
        root.add_widget(sbox)

        tabs = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        tabs.add_widget(DarkButton(text='المفضلة', font_size='13sp'))
        tabs.add_widget(DarkButton(text='غير مقروءة', font_size='13sp'))
        tabs.add_widget(GoldButton(text='الكل', font_size='13sp'))
        root.add_widget(tabs)

        scroll = ScrollView(do_scroll_x=False, bar_width=dp(3),
                            bar_color=(ACCENT[0], ACCENT[1], ACCENT[2], .5))
        box = BoxLayout(orientation='vertical', size_hint_y=None,
                        spacing=dp(8), padding=[0, dp(2), 0, dp(6)])
        box.bind(minimum_height=box.setter('height'))
        s.ids.chat_list = box
        scroll.add_widget(box)
        root.add_widget(scroll)
        root.add_widget(self.bottom_nav('home'))
        s.add_widget(root)
        return s

    # ───────────────────────── المحادثة ─────────────────────────
    def make_chat(self):
        s = ChatScreen(name="chat")
        root = self.base_root()

        top = Card(size_hint_y=None, height=dp(66), padding=[dp(10), dp(8)],
                   spacing=dp(8), fill=PANEL, radius=22)
        more = IconButton("more", color=TEXT, bg=CARD2)
        more.bind(on_release=lambda *_: s.chat_actions())
        top.add_widget(anchor(more, dp(44)))

        title_box = BoxLayout(orientation="vertical", padding=[0, dp(6)])
        s.ids.title = self.label("المحادثة", 19, TEXT, halign="right")
        title_box.add_widget(s.ids.title)
        title_box.add_widget(self.label("محادثة خاصة", 12, MUTED, halign="right"))
        top.add_widget(title_box)

        back = IconButton("back", color=TEXT, bg=CARD2)
        back.bind(on_release=lambda *_: s.back())
        top.add_widget(anchor(back, dp(44)))
        root.add_widget(top)

        scroll = ScrollView(do_scroll_x=False, bar_width=dp(3),
                            bar_color=(ACCENT[0], ACCENT[1], ACCENT[2], .5))
        box = BoxLayout(orientation="vertical", size_hint_y=None,
                        spacing=dp(4), padding=[0, dp(8)])
        box.bind(minimum_height=box.setter("height"))
        s.ids.messages = box
        s.ids.scroll = scroll
        scroll.add_widget(box)
        root.add_widget(scroll)

        # شريط الوسائط (يظهر عند الضغط على +)
        media_row = BoxLayout(size_hint_y=None, height=0, spacing=dp(8))
        media_row.opacity = 0
        media_row.disabled = True
        for label_text, kind in (("صوت", None), ("ملف", "ملف"),
                                 ("فيديو", "فيديو"), ("صورة", "صورة")):
            b = DarkButton(text=label_text, font_size="13sp")
            if kind is None:
                b.bind(on_release=lambda *_: s.voice_info())
            else:
                b.bind(on_release=lambda _, k=kind: s.pick_media(k))
            media_row.add_widget(b)
        root.add_widget(media_row)

        def toggle_media(*_):
            show = media_row.height == 0
            media_row.height = dp(42) if show else 0
            media_row.opacity = 1 if show else 0
            media_row.disabled = not show

        bar = Card(size_hint_y=None, height=dp(62), padding=[dp(8), dp(8)],
                   spacing=dp(8), fill=PANEL, radius=31)
        send = IconButton("send", color=WHITE, grad=True, size=(dp(46), dp(46)))
        send.bind(on_release=lambda *_: s.send())
        bar.add_widget(anchor(send, dp(46)))
        fbox = FieldBox(hint="اكتب رسالة...", height=46, draw=False)
        fbox.size_hint_y = 1
        inp = fbox.input
        inp.bind(on_text_validate=lambda *_: s.send())
        s.ids.message = inp
        bar.add_widget(fbox)
        plus = IconButton("plus", color=ACCENT, bg=(ACCENT[0], ACCENT[1], ACCENT[2], .14),
                          size=(dp(44), dp(44)))
        plus.bind(on_release=toggle_media)
        bar.add_widget(anchor(plus, dp(44)))
        root.add_widget(bar)

        s.add_widget(root)
        return s

    # ───────────────────────── الملف الشخصي ─────────────────────────
    def make_profile(self):
        s = ProfileScreen(name="profile")
        root = self.base_root()
        root.add_widget(self.header("الملف الشخصي", lambda: s.go("home")))

        scroll = ScrollView(do_scroll_x=False, bar_width=dp(3),
                            bar_color=(ACCENT[0], ACCENT[1], ACCENT[2], .5))
        page = BoxLayout(orientation="vertical", size_hint_y=None,
                         spacing=dp(12), padding=[0, dp(4), 0, dp(14)])
        page.bind(minimum_height=page.setter("height"))

        hero = Card(orientation="vertical", size_hint_y=None, height=dp(310),
                    padding=[dp(14), dp(18), dp(14), dp(14)], spacing=dp(6),
                    radius=30, texture=gradient("hero", [HERO_A, HERO_B]),
                    border=(1, 1, 1, .14))
        s.ids.profile_hero = hero

        avatar_row = AnchorLayout(size_hint_y=None, height=dp(132))
        avatar = CircularAvatar(size=(dp(120), dp(120)), ring=True,
                                initial=self.local.get("username", "mohsen12"),
                                size_hint=(None, None))
        avatar_row.add_widget(avatar)
        s.ids.profile_avatar = avatar
        hero.add_widget(avatar_row)

        name = self.label(self.local.get("username", "mohsen12"), 25, WHITE,
                          size_hint_y=None, height=dp(40))
        s.ids.profile_name = name
        hero.add_widget(name)
        online = self.label("متصل الآن", 13, hexa("#9CF5CB"),
                            size_hint_y=None, height=dp(22))
        s.ids.online = online
        hero.add_widget(online)

        camera = GoldButton(text="تغيير الصورة", size_hint=(None, None),
                            size=(dp(176), dp(42)))
        camera.bind(on_release=lambda *_: s.choose_photo())
        s.ids.profile_camera = camera
        cam_row = AnchorLayout(size_hint_y=None, height=dp(48))
        cam_row.add_widget(camera)
        hero.add_widget(cam_row)
        page.add_widget(hero)

        # الحالة (اضغط للتعديل)
        status_card = ListRow(orientation="vertical", size_hint_y=None, height=dp(80),
                              padding=[dp(18), dp(12)], spacing=dp(2), fill=CARD, radius=20)
        status_card.add_widget(self.label("الحالة الشخصية", 12, MUTED, halign="right",
                                          size_hint_y=None, height=dp(20)))
        status = self.label(self.local.get("status", "..."), 16, TEXT, halign="right")
        s.ids.status = status
        status_card.add_widget(status)
        status_card.bind(on_release=lambda *_: s.edit_status())
        page.add_widget(status_card)

        # اسم المستخدم + تاريخ الانضمام
        info_row = BoxLayout(size_hint_y=None, height=dp(88), spacing=dp(10))

        def stat(caption, value_widget):
            c = Card(orientation="vertical", padding=[dp(16), dp(12)], spacing=dp(4),
                     fill=CARD, radius=20)
            c.add_widget(self.label(caption, 12, MUTED, halign="right",
                                    size_hint_y=None, height=dp(20)))
            c.add_widget(value_widget)
            return c

        info_name = self.label(self.local.get("username", "mohsen12"), 17, TEXT, halign="right")
        s.ids.info_username = info_name
        date = self.label(self.local.get("join", "2025/09/16"), 17, TEXT, halign="right")
        s.ids.join = date
        info_row.add_widget(stat("تاريخ الانضمام", date))
        info_row.add_widget(stat("اسم المستخدم", info_name))
        page.add_widget(info_row)

        edit = GoldButton(text="تعديل اسم المستخدم", size_hint_y=None, height=dp(54))
        edit.bind(on_release=lambda *_: s.edit_name())
        page.add_widget(edit)
        actions = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        photo_btn = DarkButton(text="تغيير الصورة")
        status_btn = DarkButton(text="تغيير الحالة")
        photo_btn.bind(on_release=lambda *_: s.choose_photo())
        status_btn.bind(on_release=lambda *_: s.edit_status())
        actions.add_widget(status_btn)
        actions.add_widget(photo_btn)
        page.add_widget(actions)

        scroll.add_widget(page)
        root.add_widget(scroll)
        root.add_widget(self.bottom_nav("profile"))
        s.add_widget(root)
        return s

    # ───────────────────────── المحظورون / الخصوصية / الإبلاغ ─────────────────────────
    def make_blocked(self):
        s = BlockedUsersScreen(name="blocked")
        root = self.base_root()
        root.add_widget(self.header("المستخدمون المحظورون", lambda: s.go("settings")))
        scroll = ScrollView(do_scroll_x=False, bar_width=dp(3))
        box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8))
        box.bind(minimum_height=box.setter("height"))
        s.ids.blocked_list = box
        scroll.add_widget(box)
        root.add_widget(scroll)
        s.add_widget(root)
        return s

    def make_privacy(self):
        s = PrivacyScreen(name="privacy")
        root = self.base_root()
        root.add_widget(self.header("الخصوصية والأمان", lambda: s.go("settings")))
        scroll = ScrollView(do_scroll_x=False, bar_width=dp(3))
        box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8))
        box.bind(minimum_height=box.setter("height"))
        for title, sub, icon in [
            ("آخر ظهور", "التحكم بظهور وقت اتصالك", "eye"),
            ("الصورة الشخصية", "من يستطيع رؤية صورتك", "user"),
            ("الحالة", "من يستطيع رؤية حالتك", "info"),
            ("إيصالات القراءة", "إظهار حالة قراءة الرسائل", "shield"),
        ]:
            box.add_widget(ActionRow(title, sub, icon=icon))
        note = self.label(
            "ملاحظة: حفظ خيارات الخصوصية يحتاج أعمدة إعدادات في profiles أو جدول preferences.",
            13, MUTED, halign="right", size_hint_y=None, height=dp(70))
        box.add_widget(note)
        scroll.add_widget(box)
        root.add_widget(scroll)
        s.add_widget(root)
        return s

    def make_report(self):
        s = ReportScreen(name="report")
        root = self.base_root()
        root.add_widget(self.header("الإبلاغ", lambda: s.go("chat")))
        intro = Card(orientation="horizontal", size_hint_y=None, height=dp(70),
                     padding=[dp(16), dp(10)], spacing=dp(12), fill=CARD, radius=20)
        intro.add_widget(self.label("اختر سبب الإبلاغ عن المستخدم", 16, TEXT, halign="right"))
        intro.add_widget(anchor(
            IconChip("flag", color=ACCENT, bg=(ACCENT[0], ACCENT[1], ACCENT[2], .16)), dp(44)))
        root.add_widget(intro)
        for reason in ["إساءة أو مضايقة", "محتوى مزعج", "انتحال شخصية", "محتوى غير مناسب", "سبب آخر"]:
            b = DarkButton(text=reason, size_hint_y=None, height=dp(54))
            b.bind(on_release=lambda _, r=reason: s.submit(r))
            root.add_widget(b)
        root.add_widget(Widget())
        s.add_widget(root)
        return s

    # ───────────────────────── المستخدمون / الإعدادات ─────────────────────────
    def make_users(self):
        s = UsersScreen(name="users")
        root = self.base_root()
        root.add_widget(self.header("المستخدمون", lambda: s.go("home")))
        scroll = ScrollView(do_scroll_x=False, bar_width=dp(3),
                            bar_color=(ACCENT[0], ACCENT[1], ACCENT[2], .5))
        box = BoxLayout(orientation="vertical", size_hint_y=None,
                        spacing=dp(8), padding=[0, dp(2), 0, dp(6)])
        box.bind(minimum_height=box.setter("height"))
        s.ids.users_list = box
        scroll.add_widget(box)
        root.add_widget(scroll)
        root.add_widget(self.bottom_nav("users"))
        s.add_widget(root)
        return s

    def make_settings(self):
        s = SettingsScreen(name="settings")
        root = self.base_root()
        root.add_widget(self.header("الإعدادات", lambda: s.go("home")))

        scroll = ScrollView(do_scroll_x=False, bar_width=dp(3))
        box = BoxLayout(
            orientation="vertical", size_hint_y=None, spacing=dp(8),
            padding=[0, dp(2), 0, dp(12)]
        )
        box.bind(minimum_height=box.setter("height"))

        sections = [
            ("الحساب", "تعديل الملف الشخصي والصورة والحالة", "user", lambda *_: s.profile()),
            ("الخصوصية والأمان", "آخر ظهور، إيصالات القراءة والحظر", "shield", lambda *_: s.privacy()),
            ("المستخدمون المحظورون", "عرض وإلغاء حظر المستخدمين", "block", lambda *_: s.blocked()),
            ("الإشعارات", "تنبيهات الرسائل والتحديثات", "bell", lambda *_: self.notice("إعدادات الإشعارات قيد الربط بالنظام.")),
            ("المظهر", "الوضع الداكن وحجم الواجهة", "moon", lambda *_: self.notice("المظهر الداكن مفعل حالياً.")),
            ("المحادثات والوسائط", "الصور والفيديو والملفات والرسائل", "image", lambda *_: self.notice("واجهة الوسائط مضافة، وربط التخزين يتم عبر Storage.")),
            ("حول AL WARD", "نسخة التطبيق ومعلومات المشروع", "info", lambda *_: self.notice("AL WARD — تطبيق دردشة عربي.")),
        ]

        for title, sub, icon, callback in sections:
            b = ActionRow(title, sub, icon=icon)
            b.bind(on_release=callback)
            box.add_widget(b)

        logout = DarkButton(
            text="تسجيل الخروج", size_hint_y=None, height=dp(56),
            fill=DANGER_FILL, border=DANGER_BORDER, color=DANGER_TXT,
            font_size="16sp"
        )
        logout.bind(on_release=lambda *_: s.logout())
        box.add_widget(Widget(size_hint_y=None, height=dp(6)))
        box.add_widget(logout)

        scroll.add_widget(box)
        root.add_widget(scroll)
        root.add_widget(self.bottom_nav("settings"))
        s.add_widget(root)
        return s

    # ───────────────────────── الترويسة والتنقل السفلي ─────────────────────────
    def header(self, title, back):
        box = BoxLayout(size_hint_y=None, height=dp(58), spacing=dp(8))
        box.add_widget(Widget(size_hint_x=None, width=dp(44)))
        box.add_widget(self.label(title, 21, TEXT))
        b = IconButton("back", color=TEXT, bg=CARD2)
        b.bind(on_release=lambda *_: back())
        box.add_widget(anchor(b, dp(44)))
        return box

    def bottom_nav(self, active):
        nav = Card(size_hint_y=None, height=dp(68), spacing=dp(4),
                   padding=[dp(6), dp(5)], fill=PANEL, radius=26)
        # من اليسار لليمين: الإعدادات، الملف، المستخدمون، المحادثات (الرئيسية أقصى اليمين)
        items = [
            ('الإعدادات', 'settings', 'sliders'),
            ('الملف الشخصي', 'profile', 'user'),
            ('المستخدمون', 'users', 'users'),
            ('المحادثات', 'home', 'chat'),
        ]
        for title, target, icon in items:
            item = NavItem(title, icon, active=(target == active))
            item.bind(on_release=lambda _, t=target: self.goto(t))
            nav.add_widget(item)
        return nav

    def goto(self, target):
        self.root.current = target

    def ensure_profile(self):
        if not self.token or not self.user_id:
            return
        try:
            requests.post(
                SUPABASE_URL + "/rest/v1/profiles?on_conflict=id",
                headers={
                    **headers(self.token),
                    "Prefer": "resolution=merge-duplicates,return=minimal",
                },
                json={"id": self.user_id, "username": self.username},
                timeout=15,
            )
        except Exception as exc:
            print("Profile ensure error:", exc)

    def is_online(self, last_seen):
        if not last_seen:
            return False
        try:
            seen = datetime.fromisoformat(
                str(last_seen).replace("Z", "+00:00")
            )
            if seen.tzinfo is None:
                seen = seen.replace(tzinfo=timezone.utc)
            age = (
                datetime.now(timezone.utc) -
                seen.astimezone(timezone.utc)
            ).total_seconds()
            return 0 <= age <= 120
        except Exception:
            return False

    def start_presence(self):
        self.stop_presence()
        self.update_presence()
        self.presence_event = Clock.schedule_interval(
            lambda dt: self.update_presence(), 60
        )

    def stop_presence(self):
        if self.presence_event:
            self.presence_event.cancel()
            self.presence_event = None

    def update_presence(self):
        if not self.token or not self.user_id:
            return
        try:
            requests.patch(
                SUPABASE_URL + "/rest/v1/profiles?id=eq." + str(self.user_id),
                headers={
                    **headers(self.token),
                    "Prefer": "return=minimal",
                },
                json={"last_seen": datetime.now(timezone.utc).isoformat()},
                timeout=12,
            )
        except Exception as exc:
            print("Presence error:", exc)

    def logout(self):
        self.stop_presence()
        self.token = None
        self.user_id = None
        self.username = None
        self.root.current = "login"

    def error(self, message):
        self.popup(message, "حصل خطأ")

    def notice(self, message):
        self.popup(message, "AL WARD")

    def popup(self, message, title):
        box = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(14))
        lbl = self.label(str(message), 15, TEXT)
        lbl.bind(size=lambda w, v: setattr(w, "text_size", v))
        box.add_widget(lbl)
        ok = GoldButton(text="حسناً", size_hint_y=None, height=dp(48))
        box.add_widget(ok)
        pop = StyledPopup(
            title=ar(title), content=box,
            size_hint=(.90, .42), auto_dismiss=False
        )
        ok.bind(on_release=pop.dismiss)
        pop.open()


if __name__ == "__main__":
    ALWardApp().run()
