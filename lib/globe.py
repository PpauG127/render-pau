import numpy as np, math, cairo
from PIL import Image, ImageFilter
import os
ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')
CACHE = os.path.join(ASSETS, 'cache'); os.makedirs(CACHE, exist_ok=True)
P = lambda n: os.path.join(CACHE, n)
TW, TH = 4096, 2048

def _fbm(h, w, seed, octaves=6, base=4):
    rng = np.random.default_rng(seed); out = np.zeros((h, w), np.float32); amp = 1; tot = 0
    for o in range(octaves):
        sh, sw = base * 2 ** o, base * 2 ** o * 2
        r = rng.random((sh, sw)).astype(np.float32)
        r3 = np.concatenate([r, r, r], 1)
        im = Image.fromarray((r3 * 255).astype(np.uint8)).resize((3 * w, h), Image.BICUBIC)
        out += np.asarray(im, np.float32)[:, w:2 * w] / 255 * amp; tot += amp; amp *= 0.5
    return out / tot

def build():
    if os.path.exists(P('tex.npy')):
        return np.load(P('tex.npy')), np.load(P('cloud.npy')), np.load(P('ocean.npy'))
    land_im = Image.open(os.path.join(ASSETS, 'land.png'))
    land = np.asarray(land_im, np.float32) / 255
    coast = np.asarray(land_im.filter(ImageFilter.GaussianBlur(10)), np.float32) / 255
    lat = np.linspace(90, -90, TH, dtype=np.float32)[:, None] * np.ones((1, TW), np.float32)
    lon = np.linspace(-180, 180, TW, dtype=np.float32)[None, :] * np.ones((TH, 1), np.float32)
    pf = np.clip(np.cos(np.radians(lat)) * 3, 0, 1)
    n1 = 0.5 + (_fbm(TH, TW, 1) - 0.5) * pf; n2 = 0.5 + (_fbm(TH, TW, 2) - 0.5) * pf
    deep = np.array([0.02, 0.09, 0.26], np.float32); shallow = np.array([0.04, 0.30, 0.50], np.float32)
    oc = deep + (shallow - deep) * (np.clip(coast * 1.4, 0, 1)[..., None] * 0.8)
    oc *= (0.9 + 0.2 * n1)[..., None]
    g1 = np.array([0.13, 0.33, 0.12], np.float32); g2 = np.array([0.24, 0.40, 0.16], np.float32)
    des = np.array([0.80, 0.66, 0.42], np.float32); tun = np.array([0.42, 0.40, 0.32], np.float32)
    ice = np.array([0.94, 0.96, 1.0], np.float32)
    al = np.abs(lat)
    lc = g1 + (g2 - g1) * n2[..., None]
    dw = np.exp(-((al - 24) / 9) ** 2) * np.clip((n1 - 0.35) * 3, 0, 1)
    sah = np.exp(-((lat - 23) / 8) ** 2) * np.exp(-((lon - 22) / 38) ** 4)
    aus = np.exp(-((lat + 25) / 7) ** 2) * np.exp(-((lon - 132) / 12) ** 4)
    dw = np.clip(np.maximum(dw, np.maximum(sah, aus) * (0.75 + 0.25 * n2)), 0, 1)
    lc = lc + (des - lc) * dw[..., None]
    tw_ = np.clip((al - 55) / 10, 0, 1)
    lc = lc + (tun - lc) * tw_[..., None]
    iw = np.clip((al - 68) / 4, 0, 1)
    iw = np.maximum(iw, ((lat > 60) & (lon > -60) & (lon < -20)).astype(np.float32))
    lc = lc + (ice - lc) * iw[..., None]
    lc *= (0.85 + 0.3 * n1)[..., None]
    tex = oc + (lc - oc) * land[..., None]
    seaice = np.clip((lat - 78) / 6 + (n1 - 0.5) * 0.8, 0, 1)[..., None]
    tex = tex + (ice * 0.92 - tex) * seaice
    c = _fbm(TH, TW, 5, octaves=7, base=3)
    cloud = np.clip((c - 0.52) * 3.2, 0, 0.85) * np.clip(np.cos(np.radians(lat)) * 2.5, 0, 1)
    pw = np.clip((np.abs(lat[:, :1]) - 72) / 10, 0, 1)[..., None]
    tex = tex * (1 - pw) + tex.mean(axis=1, keepdims=True) * pw
    tex = tex.astype(np.float32); cloud = cloud.astype(np.float32); ocean = (1 - land).astype(np.float32)
    np.save(P('tex.npy'), tex); np.save(P('cloud.npy'), cloud); np.save(P('ocean.npy'), ocean)
    return tex, cloud, ocean

TEX, CLOUD, OCEAN = build()
_grid = {}

def globe_surface(R, lon0, lat0, cshift=0.0, light=(-0.55, 0.5, 0.67), night=0.07):
    R = int(R); S = 2 * R
    if R not in _grid:
        ys, xs = np.mgrid[0:S, 0:S].astype(np.float32)
        u = (xs + 0.5 - R) / R; v = -(ys + 0.5 - R) / R
        rr = u * u + v * v
        z = np.sqrt(np.clip(1 - rr, 0, 1))
        alpha = np.clip(R - np.sqrt(rr) * R + 0.5, 0, 1)
        _grid[R] = (u, v, z, alpha)
    u, v, z, alpha = _grid[R]
    p0 = math.radians(lat0)
    lat = np.arcsin(np.clip(z * math.sin(p0) + v * math.cos(p0), -1, 1))
    lon = math.radians(lon0) + np.arctan2(u, z * math.cos(p0) - v * math.sin(p0))
    ix = (((lon / (2 * math.pi) + 0.5) % 1.0) * TW).astype(np.int32) % TW
    iy = np.clip(((0.5 - lat / math.pi) * TH).astype(np.int32), 0, TH - 1)
    col = TEX[iy, ix]
    cl = CLOUD[iy, (ix + int(cshift * TW)) % TW][..., None]
    oc = OCEAN[iy, ix][..., None]
    col = col * (1 - cl) + 0.97 * cl
    L = np.array(light, np.float32); L /= np.linalg.norm(L)
    diff = np.clip(u * L[0] + v * L[1] + z * L[2], 0, 1)[..., None]
    shade = night + (1 - night) * diff
    Hh = L + np.array([0, 0, 1], np.float32); Hh /= np.linalg.norm(Hh)
    sp = np.clip(u * Hh[0] + v * Hh[1] + z * Hh[2], 0, 1) ** 140
    rgb = col * shade + (sp[..., None] * 0.3 * oc * (1 - cl))
    rim = ((1 - z) ** 3)[..., None]
    rgb = rgb + np.array([0.25, 0.55, 1.0], np.float32) * rim * (0.25 + 0.6 * diff)
    rgb = np.clip(rgb, 0, 1)
    a = alpha[..., None]
    out = np.empty((S, S, 4), np.uint8)
    out[..., 0] = (rgb[..., 2:3] * a * 255)[..., 0]
    out[..., 1] = (rgb[..., 1:2] * a * 255)[..., 0]
    out[..., 2] = (rgb[..., 0:1] * a * 255)[..., 0]
    out[..., 3] = (a * 255)[..., 0]
    surf = cairo.ImageSurface.create_for_data(memoryview(out), cairo.FORMAT_ARGB32, S, S, S * 4)
    return surf, out

def draw_globe(ctx, cx, cy, R, lon0, lat0, cshift=0.0, light=(-0.55, 0.5, 0.67), a=1.0, glow=True):
    if R < 2: return
    if glow:
        g = cairo.RadialGradient(cx, cy, R * 0.95, cx, cy, R * 1.22)
        g.add_color_stop_rgba(0, 0.3, 0.65, 1.0, 0.55 * a)
        g.add_color_stop_rgba(1, 0.3, 0.65, 1.0, 0)
        ctx.set_source(g); ctx.arc(cx, cy, R * 1.22, 0, 6.2832); ctx.fill()
    s, _buf = globe_surface(R, lon0, lat0, cshift, light)
    ctx.set_source_surface(s, cx - int(R), cy - int(R))
    ctx.paint_with_alpha(a)

def project(lat, lon, cx, cy, R, lon0, lat0):
    f, l = math.radians(lat), math.radians(lon - lon0); f0 = math.radians(lat0)
    x = math.cos(f) * math.sin(l)
    y = math.cos(f0) * math.sin(f) - math.sin(f0) * math.cos(f) * math.cos(l)
    vis = math.sin(f0) * math.sin(f) + math.cos(f0) * math.cos(f) * math.cos(l) > 0
    return cx + R * x, cy - R * y, vis
