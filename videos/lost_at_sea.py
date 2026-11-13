"""Would You Survive 7 Days Lost at Sea? — 16:9 long-form (~10 min). Data-driven: BEATS -> auto-split scenes."""
import os, sys, re, math, random
os.environ['FMT'] = '16x9'
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
PER_JOB = 12
WPS = 2.2          # narration speed (words / second)

# (template, params, narration)
BEATS = [
 ('sea', dict(time='sunset', boat=1, pose='scared', fear=1, hope=60), "You have ninety seconds before your sailboat disappears under the waves."),
 ('sea', dict(time='sunset', pose='scared', fear=1, hope=50), "You grab the orange life raft, a small bag, and jump. When you look back, the boat is gone."),
 ('sea', dict(time='sunset', shot='wide', hope=45), "No land. No other boats. Just water, in every direction."),
 ('title', dict(ttl='WOULD YOU SURVIVE', sub='7 DAYS LOST AT SEA', time='sunset'), "So, would you survive seven days lost at sea? Stay until the end, because what finally saves you is not what you think."),
 ('items', dict(), "Inside the bag: two liters of water, a few energy bars, a signal mirror, a tiny fishing kit, and a plastic tarp. That's it."),
 ('sea', dict(time='sunset', pose='sit', fear=0.5, mouth='wavy', hope=40), "No radio. No phone signal. No idea which way land is. All you have is time, and a few hard choices."),
 ('title', dict(ttl='DAY 1', time='day', day=1), "Day one."),
 ('sea', dict(time='day', pose='sit', sweat=1, day=1), "The sun is brutal. Your mouth is already dry, and that water bottle is right there."),
 ('choice', dict(a='DRINK NOW', b='WAIT 24 HOURS', day=1), "Do you drink now, or wait? You have three seconds."),
 ('fact', dict(big='WAIT 24 HOURS', sub='unless you are sick or injured', day=1), "Survival experts say: drink nothing in the first twenty four hours, unless you are sick or injured."),
 ('close', dict(mouth='flat', fear=0.3, time='day', day=1), "It sounds crazy. But when you stop drinking, your body switches into conservation mode. Your kidneys hold on to every drop."),
 ('close', dict(mouth='flat', fear=0.2, time='day', day=1), "Every hour, your body loses water just by breathing. Talking, moving, panicking, all of it costs water."),
 ('sea', dict(time='day', tarp=1, pose='sit', day=1), "So you rig the tarp for shade, stay still, and try not to sweat. Doing nothing is now your job."),
 ('sea', dict(time='sunset', pose='sit', day=1, water=2.0), "The sun goes down. And then comes something you did not expect."),
 ('sea', dict(time='night', pose='hug', fear=0.6, mouth='wavy', day=1, temp=1), "The cold. Even over warm seas, a wet body loses heat fast at night."),
 ('fact', dict(big='COLD KILLS FIRST', sub='exposure is faster than thirst', day=1), "In sea survival, cold and exposure kill faster than thirst. Staying dry and out of the wind matters more than food."),
 ('sea', dict(time='night', tarp=1, pose='hug', day=1), "You wring out your clothes, pull the tarp over you, and curl up in the middle of the raft."),
 ('title', dict(ttl='DAY 2', time='day', day=2), "Day two."),
 ('map', dict(miles=30, day=2), "You have drifted about thirty miles. Your boat never sent a distress signal. No one knows where you are."),
 ('sea', dict(time='day', pose='sit', sweat=1, mouth='wavy', day=2, water=1.8), "Your thirst is unbearable now. Seawater is everywhere. One small cup can't hurt, right?"),
 ('choice', dict(a='DRINK SEAWATER', b='RATION YOUR WATER', day=2), "Seawater, or your tiny supply of fresh water?"),
 ('fact', dict(big='3.5% SALT', sub='more salt than your kidneys can handle', day=2), "Seawater is about three and a half percent salt. To flush that salt out, your kidneys need more water than you just drank."),
 ('close', dict(mouth='wavy', fear=0.5, time='day', day=2), "Every sip of seawater makes you thirstier. Sailors who gave in became confused, and many never made it home."),
 ('sea', dict(time='day', bottle=1, pose='sit', day=2, water=1.5), "So you ration: a few mouthfuls of fresh water, spread across the day. Your two liters suddenly look very small."),
 ('sea', dict(time='day', tarp=1, pose='sit', day=2), "You cover every inch of skin. Sunburn makes you lose water faster, so shade is not comfort. It's survival."),
 ('sea', dict(time='day', birds=1, pose='sit', look=(0.5, -1), day=2), "Then you notice birds circling. Birds can mean land, or just fish."),
 ('sea', dict(time='day', pose='sit', bottle=1, day=2), "You tie everything to the raft. The bottle, the mirror, the kit. At sea, anything that falls overboard is gone forever."),
 ('title', dict(ttl='DAY 3', time='day', day=3), "Day three."),
 ('sea', dict(time='day', fin=1, pose='sit', look=(1, 0.5), day=3), "Something gray slices the water, ten feet from the raft."),
 ('close', dict(mouth='o', fear=1, time='day', day=3, hope=30), "A fin. Then another. They circle. Closer."),
 ('choice', dict(a='SPLASH TO SCARE THEM', b='STAY PERFECTLY STILL', day=3), "Do you splash to scare them off, or stay perfectly still?"),
 ('fact', dict(big='STAY STILL', sub='splashing looks like a struggling fish', day=3), "Splashing looks like a struggling fish. Shark attacks on people in rafts are rare. Keep your hands and feet inside."),
 ('sea', dict(time='day', fin=1, finleave=1, pose='sit', fear=0.7, day=3), "You freeze. Minutes feel like hours. And then, the fins drift away."),
 ('sea', dict(time='sunset', ship=1, pose='wave', day=3, hope=70), "That evening, you see lights on the horizon. A ship!"),
 ('choice', dict(a='WAVE AND SHOUT', b='USE THE MIRROR', day=3), "You have one chance. Wave and scream, or use the mirror?"),
 ('sea', dict(time='dusk', ship=1, pose='wave', day=3), "But the sun is already gone. A signal mirror needs sunlight. You wave until your arms burn. The ship never turns."),
 ('close', dict(mouth='wavy', fear=0.4, time='dusk', day=3, hope=25), "That one hurts. And it teaches you the hardest lesson at sea: be ready before the chance comes."),
 ('title', dict(ttl='DAY 4', time='storm', day=4), "Day four."),
 ('sea', dict(time='storm', pose='hug', fear=1, mouth='o', day=4), "Black clouds. Wind. The waves double in size."),
 ('sea', dict(time='storm', pose='hug', fear=0.8, shot='close', day=4), "The raft climbs every wave and slams down. You tie yourself to the raft with the fishing line, so you can't be thrown out."),
 ('choice', dict(a='HIDE FROM THE STORM', b='CATCH THE RAIN', day=4), "But wait. A storm means rain. And rain means fresh water. Hide, or catch it?"),
 ('sea', dict(time='storm', tarp=2, pose='sit', mouth='smile', day=4, water=1.0), "You spread the tarp like a bowl and catch every drop. The first mouthful is the best thing you have ever tasted."),
 ('fact', dict(big='+3 LITERS', sub='the storm refilled your water', day=4, water=3.0), "By morning, your bottle is full again. The storm that almost killed you just saved your life."),
 ('sea', dict(time='dawn', pose='sit', day=4), "The sea goes calm. You check the raft for leaks and squeeze out the water at the bottom. A dry raft is a warm raft."),
 ('title', dict(ttl='DAY 5', time='day', day=5), "Day five."),
 ('sea', dict(time='day', fish=1, pose='sit', look=(0, 1), day=5, water=2.6), "Your energy bars are gone. But small fish gather in the shade under the raft."),
 ('sea', dict(time='day', fish=1, rod=1, pose='aim', day=5), "With the fishing kit and a lot of patience, you catch one. Raw. Not pretty. But it's food."),
 ('fact', dict(big='WATER BEFORE FOOD', sub='digesting food uses water', day=5), "You only ate once you had water. Digesting food uses water, and you can last weeks without food, but only days without water."),
 ('sea', dict(time='dawn', pose='sit', day=5), "At dawn, you wipe the dew off the tarp with a cloth and squeeze it into the bottle. Every drop counts."),
 ('close', dict(mouth='flat', fear=0.3, time='day', day=5, hope=35), "Your lips are cracked. Your skin is burned. And your mind starts playing tricks."),
 ('title', dict(ttl='DAY 6', time='day', day=6), "Day six."),
 ('sea', dict(time='day', island=1, pose='point', look=(1, 0), day=6, hope=80), "Is that land? A green island, right there."),
 ('sea', dict(time='day', island=2, pose='sit', mouth='wavy', day=6, hope=20), "You blink. It's gone. It was never there."),
 ('close', dict(mouth='flat', fear=0.2, time='day', day=6), "Survivors say the hardest part is not the body. It's keeping hope alive."),
 ('sea', dict(time='day', pose='sit', bottle=1, day=6, hope=40), "So you build a routine. Check the water. Check the raft. Count the days. Talk out loud. Keep your mind busy."),
 ('sea', dict(time='night', pose='sit', mouth='smile', day=6, hope=50), "That night, the stars are brighter than anything you have ever seen. For the first time in days, you feel calm."),
 ('title', dict(ttl='DAY 7', time='day', day=7), "Day seven."),
 ('sea', dict(time='day', pose='hug', mouth='wavy', fear=0.4, day=7, water=0.6, hope=20), "You wake up weak. Your water is almost gone. If help doesn't come soon, nothing you learned will matter."),
 ('sea', dict(time='day', plane=1, pose='sit', look=(0.6, -1), day=7, hope=60), "A low hum. Getting louder. A plane, flying low over the water."),
 ('choice', dict(a='WAVE YOUR ARMS', b='FLASH THE MIRROR', day=7), "This time, you know exactly what to do."),
 ('sea', dict(time='day', plane=1, mirror=1, pose='aim', day=7, hope=80), "You aim the mirror at the plane. A flash of sunlight can be seen from miles away."),
 ('sea', dict(time='day', plane=2, pose='wave', mouth='smile', day=7, hope=95), "The plane banks. It turns. It circles back. They saw you."),
 ('sea', dict(time='day', rescue=1, pose='wave', mouth='smile', day=7, hope=100), "Hours later, a rescue boat pulls you out of the raft."),
 ('close', dict(mouth='flat', fear=0, time='day', day=7), "But here's the twist."),
 ('fact', dict(big='DAY 1 SAVED YOU', sub='doing nothing was the smartest move', day=7), "What saved you wasn't the mirror. It was day one. Not drinking. Not sweating. Staying out of the sun."),
 ('sea', dict(time='sunset', pose='sit', mouth='smile', day=7), "That's why you still had strength on day seven, when the plane finally came. You won the waiting game."),
 ('choice', dict(a='WHICH ONE DID', b='YOU GET WRONG?', cta=1, day=7), "So, which choice would you have gotten wrong? Tell me in the comments, and tell me where I should drop you next."),
]

def split_text(txt, maxw=9):
    sents = re.findall(r'[^.?!]+[.?!]*', txt)
    out = []
    for s in sents:
        w = s.split()
        if not w: continue
        if len(w) <= maxw: out.append(' '.join(w)); continue
        parts = re.split(r'(?<=,)\s+', s.strip())
        buf = []
        for p_ in parts:
            pw = p_.split()
            if buf and len(buf) + len(pw) > maxw:
                out.append(' '.join(buf)); buf = []
            buf += pw
            while len(buf) > maxw + 3:
                out.append(' '.join(buf[:maxw])); buf = buf[maxw:]
        if buf: out.append(' '.join(buf))
    return out

def build():
    scenes = []; state = dict(day=0, water=2.0, energy=90, hope=50, temp=0)
    styles = [0, 1, 2, 3]
    for bi, (tpl, P, txt) in enumerate(BEATS):
        for k in ('day', 'water', 'hope'):
            if k in P: state[k] = P[k]
        state['energy'] = max(15, 90 - 11 * max(0, state['day'] - 1))
        chunks = split_text(txt); boff = 0.0
        for ci, ch in enumerate(chunks):
            n = len(ch.split())
            dur = max(2.0, n / WPS + 0.45)
            if tpl == 'choice' and ci == len(chunks) - 1 and not P.get('cta'): dur += 3.0
            if tpl == 'title': dur = max(dur, 2.2)
            Q = dict(P); Q.update(state); Q['ci'] = ci; Q['boff'] = boff; Q['text'] = ch; Q['tpl'] = tpl
            Q['shot'] = P.get('shot') or ['wide', 'close', 'low', 'mid'][(bi + ci) % 4]
            fn = lambda ctx, t, d, Q=Q: SCENE(ctx, t, d, Q)
            style = styles[bi % 4] if ci == 0 else 'dissolve'
            scenes.append((dur, "", set(), (1, 1, 1), fn, 0, style)); boff += dur
    return scenes

def SCENE(ctx, t, d, Q):
    TEMPLATES[Q['tpl']](ctx, t, d, Q)
    hud(ctx, t, Q)
    caption(ctx, t, Q['text'], 0.3, d - 0.15, y=930, size=74, chunk=4)

SCENES = build()

# =================================================================== drawing (needs cairo)
if __name__ == "__main__":
    from stick import *
    HZ = 520

    SKY = {'day': [(0, (0.16, 0.34, 0.52)), (1, (0.55, 0.7, 0.8))],
           'sunset': [(0, (0.12, 0.08, 0.2)), (0.6, (0.7, 0.25, 0.2)), (1, (1.0, 0.6, 0.3))],
           'dusk': [(0, (0.05, 0.05, 0.14)), (1, (0.35, 0.18, 0.25))],
           'night': [(0, (0.01, 0.02, 0.05)), (1, (0.05, 0.08, 0.16))],
           'storm': [(0, (0.06, 0.07, 0.09)), (1, (0.2, 0.22, 0.25))],
           'dawn': [(0, (0.1, 0.14, 0.28)), (1, (0.85, 0.6, 0.55))]}
    SEA = {'day': ((0.05, 0.25, 0.38), (0.02, 0.1, 0.18)), 'sunset': ((0.35, 0.18, 0.2), (0.05, 0.05, 0.1)),
           'dusk': ((0.1, 0.1, 0.18), (0.02, 0.02, 0.06)), 'night': ((0.03, 0.06, 0.12), (0.0, 0.01, 0.03)),
           'storm': ((0.12, 0.15, 0.17), (0.03, 0.04, 0.05)), 'dawn': ((0.25, 0.25, 0.35), (0.04, 0.06, 0.12))}

    def wave_y(x, t, layer, amp):
        return HZ + 40 + layer * 130 + amp * (0.5 + layer * 0.5) * (math.sin(x / (160 + 40 * layer) + t * (1.2 - 0.15 * layer) + layer) + 0.4 * math.sin(x / 70 - t * 1.7 + layer * 2))

    def sky(ctx, t, tm):
        g = cairo.LinearGradient(0, -300, 0, HZ)
        for o, c in SKY[tm]: g.add_color_stop_rgb(o, *c)
        ctx.rectangle(-800, -800, W + 1600, HZ + 805); ctx.set_source(g); ctx.fill()
        if tm in ('night', 'dusk'):
            rnd = random.Random(3)
            for _ in range(120):
                x, y = rnd.uniform(0, W), rnd.uniform(0, HZ - 40)
                ctx.arc(x, y, rnd.uniform(0.8, 2.2), 0, 6.3); rgba(ctx, WHITE, rnd.uniform(0.3, 0.9) * (0.6 + 0.4 * math.sin(t * 2 + x))); ctx.fill()
            if tm == 'night':
                glow_dot(ctx, 1500, 170, 46, (0.9, 0.92, 1.0), 0.95)
        elif tm == 'day':
            g = cairo.RadialGradient(1480, 170, 10, 1480, 170, 420)
            g.add_color_stop_rgba(0, 1, 0.97, 0.85, 0.9); g.add_color_stop_rgba(1, 1, 0.97, 0.85, 0)
            ctx.set_source(g); ctx.paint()
            ctx.arc(1480, 170, 70, 0, 6.3); rgba(ctx, (1, 0.98, 0.9)); ctx.fill()
        elif tm in ('sunset', 'dawn'):
            g = cairo.RadialGradient(1350, HZ, 10, 1350, HZ, 700)
            g.add_color_stop_rgba(0, 1, 0.7, 0.3, 0.8); g.add_color_stop_rgba(1, 1, 0.5, 0.2, 0)
            ctx.set_source(g); ctx.paint()
            ctx.arc(1350, HZ + 10, 110, math.pi, 0); rgba(ctx, (1, 0.62, 0.3)); ctx.fill()
        elif tm == 'storm':
            for k in range(6):
                x = (k * 400 + t * 40) % (W + 600) - 300
                ctx.save(); ctx.translate(x, 120 + 60 * (k % 3)); ctx.scale(2.6, 0.7)
                ctx.arc(0, 0, 160, 0, 6.3); ctx.restore(); rgba(ctx, (0.03, 0.035, 0.045), 0.7); ctx.fill()
            if (t * 1.3) % 3.1 < 0.12:
                x = 300 + 1200 * ((int(t * 1.3 / 3.1) * 0.37) % 1)
                ctx.move_to(x, 0)
                for i in range(1, 7): ctx.line_to(x + random.Random(i + int(t)).uniform(-60, 60), i * 75)
                rgba(ctx, (0.9, 0.95, 1), 0.95); ctx.set_line_width(5); ctx.stroke()
                rgba(ctx, (0.8, 0.85, 1), 0.25); ctx.paint()

    def sea_layers(ctx, t, tm, amp, upto=4):
        top, bot = SEA[tm]
        for layer in range(upto):
            k = layer / 3
            c = tuple(top[i] + (bot[i] - top[i]) * k for i in range(3))
            ctx.move_to(-600, H + 400)
            ctx.line_to(-600, wave_y(-20, t, layer, amp))
            for x in range(-20, W + 40, 30): ctx.line_to(x, wave_y(x, t, layer, amp))
            ctx.line_to(W + 600, wave_y(W + 20, t, layer, amp)); ctx.line_to(W + 600, H + 400); ctx.close_path()
            rgba(ctx, c); ctx.fill()
            ctx.move_to(-20, wave_y(-20, t, layer, amp))
            for x in range(-20, W + 40, 30): ctx.line_to(x, wave_y(x, t, layer, amp))
            rgba(ctx, WHITE, 0.08 + 0.05 * layer); ctx.set_line_width(3); ctx.stroke()
        if tm in ('day', 'sunset', 'dawn'):   # sun glitter
            sx = 1480 if tm == 'day' else 1350
            for k in range(26):
                rnd = random.Random(k + int(t * 6))
                x = sx + rnd.uniform(-160, 160); y = HZ + 20 + rnd.uniform(0, 260)
                ctx.rectangle(x, y, rnd.uniform(20, 60), 3); rgba(ctx, (1, 0.95, 0.8), 0.35); ctx.fill()

    def raft(ctx, x, y, t, Q, s=1.0):
        ctx.save(); ctx.translate(x, y); ctx.rotate(0.06 * math.sin(t * 1.3)); ctx.scale(s, s)
        # back ring
        ctx.save(); ctx.scale(1, 0.32); ctx.arc(0, 0, 230, math.pi, 2 * math.pi); ctx.restore()
        rgba(ctx, (0.75, 0.3, 0.05)); ctx.set_line_width(46); ctx.stroke()
        if Q.get('tarp') == 1:
            ctx.move_to(-200, -10); ctx.curve_to(-120, -300, 120, -300, 200, -10)
            fill_grad(ctx, [(0, (0.95, 0.55, 0.12)), (1, (0.7, 0.3, 0.05))], 0, -300, 0, 0, 0.92); ctx.fill()
        stickman(ctx, 0, 0 + 150 * 0.62 - 10, 0.62, Q.get('pose', 'sit'), look=Q.get('look', (0, 0)), fear=Q.get('fear', 0),
                 mouth=Q.get('mouth', 'flat'), blink=blink_at(t), sweat=Q.get('sweat', 0), t=t, shadow=False,
                 rot=0)
        if Q.get('tarp') == 2:  # rain catch bowl
            ctx.move_to(-170, -150); ctx.curve_to(-90, -40, 90, -40, 170, -150)
            rgba(ctx, (0.95, 0.55, 0.12)); ctx.set_line_width(10); ctx.stroke()
            ctx.move_to(-120, -110); ctx.curve_to(-60, -60, 60, -60, 120, -110); rgba(ctx, (0.5, 0.8, 1), 0.7); ctx.set_line_width(8); ctx.stroke()
        # front ring
        ctx.save(); ctx.scale(1, 0.32); ctx.arc(0, 0, 230, 0, math.pi); ctx.restore()
        g = cairo.LinearGradient(0, -20, 0, 90)
        g.add_color_stop_rgb(0, 1, 0.6, 0.2); g.add_color_stop_rgb(1, 0.7, 0.25, 0.03)
        ctx.set_source(g); ctx.set_line_width(50); ctx.stroke()
        ctx.save(); ctx.scale(1, 0.32); ctx.arc(0, 0, 230, 0.4, 2.7); ctx.restore()
        rgba(ctx, WHITE, 0.35); ctx.set_line_width(6); ctx.stroke()
        ctx.restore()

    def boat_sink(ctx, t, x=1300):
        sink = 60 + 30 * t
        ctx.save(); ctx.translate(x, HZ + 120 + sink); ctx.rotate(-0.35)
        ctx.move_to(-260, 0); ctx.line_to(260, 0); ctx.line_to(200, 90); ctx.line_to(-220, 90); ctx.close_path()
        fill_grad(ctx, [(0, (0.9, 0.9, 0.92)), (1, (0.5, 0.52, 0.56))], 0, 0, 0, 90); ctx.fill()
        ctx.move_to(0, 0); ctx.line_to(0, -420); rgba(ctx, (0.6, 0.6, 0.62)); ctx.set_line_width(10); ctx.stroke()
        ctx.move_to(10, -400); ctx.line_to(220, -20); ctx.line_to(10, -20); ctx.close_path(); rgba(ctx, (0.92, 0.9, 0.85), 0.9); ctx.fill()
        ctx.restore()

    def ship(ctx, t, x, s=1.0, lights=True):
        ctx.save(); ctx.translate(x, HZ + 4); ctx.scale(s, s)
        ctx.move_to(-120, 0); ctx.line_to(130, 0); ctx.line_to(110, 22); ctx.line_to(-110, 22); ctx.close_path(); rgba(ctx, (0.08, 0.08, 0.1)); ctx.fill()
        ctx.rectangle(-40, -40, 70, 40); ctx.fill()
        if lights:
            for lx in (-30, 0, 20): glow_dot(ctx, lx, -20, 4, AMB, 0.8 + 0.2 * math.sin(t * 4 + lx))
        ctx.restore()

    def plane(ctx, x, y, s=1.0, rot=0.0):
        ctx.save(); ctx.translate(x, y); ctx.rotate(rot); ctx.scale(s, s)
        rr(ctx, -110, -14, 220, 28, 14); rgba(ctx, (0.85, 0.87, 0.9)); ctx.fill()
        ctx.move_to(-20, 0); ctx.line_to(30, -95); ctx.line_to(55, -95); ctx.line_to(30, 0); ctx.close_path(); ctx.fill()
        ctx.move_to(-20, 0); ctx.line_to(30, 95); ctx.line_to(55, 95); ctx.line_to(30, 0); ctx.close_path(); ctx.fill()
        ctx.move_to(-100, 0); ctx.line_to(-130, -40); ctx.line_to(-112, -40); ctx.line_to(-80, 0); ctx.close_path(); ctx.fill()
        ctx.restore()

    def fin(ctx, x, y, t, a=1.0):
        ctx.move_to(x - 40, y); ctx.curve_to(x - 20, y - 50, x + 10, y - 90, x + 30, y - 100); ctx.curve_to(x + 25, y - 60, x + 35, y - 20, x + 50, y); ctx.close_path()
        fill_grad(ctx, [(0, (0.45, 0.5, 0.55)), (1, (0.2, 0.23, 0.27))], x - 40, 0, x + 50, 0, a); ctx.fill()
        ctx.move_to(x - 70, y + 4); ctx.curve_to(x - 20, y - 6, x + 30, y - 6, x + 80, y + 4); rgba(ctx, WHITE, 0.4 * a); ctx.set_line_width(4); ctx.stroke()

    def shot_transform(ctx, t, d, Q, cx, cy):
        sh = Q['shot']; k = clamp(t / max(d, 0.1))
        if sh == 'close': z, ox, oy = 1.7 - 0.08 * k, cx, cy - 60
        elif sh == 'low': z, ox, oy = 1.3, cx + 120 - 160 * k, cy - 20
        elif sh == 'mid': z, ox, oy = 1.15 + 0.08 * k, cx - 80 * k, cy
        else: z, ox, oy = 1.0 + 0.05 * k, W / 2, H / 2
        ctx.translate(W / 2, H / 2); ctx.scale(z, z); ctx.translate(-ox, -oy)

    def T_sea(ctx, t, d, Q):
        tm = Q.get('time', 'day'); amp = 55 if tm == 'storm' else 16
        rx = 760 + 30 * math.sin(t * 0.4)
        ry = wave_y(rx, t, 1, amp) - 20
        ctx.save(); shot_transform(ctx, t, d, Q, rx, ry - 80)
        if tm == 'storm': ctx.translate(6 * math.sin(t * 13), 4 * math.cos(t * 11))
        sky(ctx, t, tm)
        if Q.get('island') == 1:
            ctx.save(); ctx.translate(1450, HZ + 2); ctx.scale(1, 0.4); ctx.arc(0, 0, 180, math.pi, 0); ctx.restore(); rgba(ctx, (0.15, 0.4, 0.2), 0.85); ctx.fill()
        if Q.get('island') == 2:
            ctx.save(); ctx.translate(1450, HZ + 2); ctx.scale(1, 0.4); ctx.arc(0, 0, 180, math.pi, 0); ctx.restore(); rgba(ctx, (0.15, 0.4, 0.2), 0.85 * max(0, 1 - t / 1.2)); ctx.fill()
        if Q.get('ship'): ship(ctx, t, 1500 + 15 * t, 1.0, True)
        if Q.get('rescue'): ship(ctx, t, 1250 - 40 * t, 2.2, False)
        sea_layers(ctx, t, tm, amp, 2)
        if Q.get('boat'): boat_sink(ctx, t)
        if Q.get('fin'):
            ff = clamp(t / 1.5) if Q.get('finleave') else 0
            for k in range(2):
                ang = t * 0.9 + k * math.pi
                fx = rx + (380 + 500 * ff) * math.cos(ang); fy = ry + 30 + 60 * math.sin(ang)
                fin(ctx, fx, fy, t, 1 - ff)
        if Q.get('fish'):
            for k in range(5):
                fx = rx - 160 + k * 70 + 20 * math.sin(t * 2 + k); fy = ry + 110 + 15 * math.cos(t * 3 + k)
                ctx.save(); ctx.translate(fx, fy); ctx.scale(1, 0.45); ctx.arc(0, 0, 24, 0, 6.3); ctx.restore(); rgba(ctx, (0.7, 0.8, 0.85), 0.45); ctx.fill()
        raft(ctx, rx, ry, t, Q)
        if Q.get('rod'):
            ctx.move_to(rx + 60, ry - 140); ctx.line_to(rx + 260, ry - 60); ctx.line_to(rx + 260, ry + 80)
            rgba(ctx, WHITE, 0.7); ctx.set_line_width(2); ctx.stroke()
        sea_layers_front = (2, 4)
        top, bot = SEA[tm]
        for layer in range(*sea_layers_front):
            k = layer / 3; c = tuple(top[i] + (bot[i] - top[i]) * k for i in range(3))
            ctx.move_to(-20, H + 400)
            for x in range(-20, W + 40, 30): ctx.line_to(x, wave_y(x, t, layer, amp) + 60)
            ctx.line_to(W + 20, H + 400); ctx.close_path(); rgba(ctx, c, 0.92); ctx.fill()
        if Q.get('birds'):
            for k in range(5):
                bx = 1100 + k * 90 + 40 * math.sin(t + k); by = 200 + 30 * math.cos(t * 1.3 + k)
                w_ = 18 * math.sin(t * 8 + k)
                ctx.move_to(bx - 22, by - w_); ctx.line_to(bx, by); ctx.line_to(bx + 22, by - w_)
                rgba(ctx, (0.08, 0.08, 0.1)); ctx.set_line_width(4); ctx.stroke()
        if Q.get('plane') == 1: plane(ctx, 1700 - 160 * t, 230 + 10 * math.sin(t), 0.9)
        if Q.get('plane') == 2: plane(ctx, 1200 + 380 * math.cos(t * 0.9), 260 + 120 * math.sin(t * 0.9), 0.9, t * 0.9 + math.pi / 2)
        if Q.get('mirror'):
            if t > 0.9:
                fl = 0.5 + 0.5 * math.sin(t * 14)
                ctx.move_to(rx + 70, ry - 230); ctx.line_to(1600 - 160 * t, 230); glow_stroke(ctx, (1, 1, 0.85), 4, 0.8 * fl)
                glow_dot(ctx, rx + 70, ry - 230, 18, (1, 1, 0.9), fl)
        if Q.get('bottle'):
            rr(ctx, rx + 130, ry - 120, 46, 110, 12); rgba(ctx, (0.6, 0.85, 1), 0.6); ctx.fill()
        if tm == 'storm':
            for k in range(70):
                rnd = random.Random(k)
                x = (rnd.uniform(0, W) + t * 300) % W; y = (rnd.uniform(0, H) + t * 1600) % H
                ctx.move_to(x, y); ctx.line_to(x - 18, y + 60); rgba(ctx, (0.75, 0.8, 0.9), 0.35); ctx.set_line_width(2); ctx.stroke()
        ctx.restore()

    def T_close(ctx, t, d, Q):
        tm = Q.get('time', 'day')
        ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(1.4, 1.4); ctx.translate(-W / 2, -H / 2 - 120)
        sky(ctx, t * 0.3, tm); sea_layers(ctx, t, tm, 16, 4)
        ctx.restore()
        rgba(ctx, (0, 0, 0), 0.35); ctx.paint()
        z = 2.4 + 0.15 * clamp(t / d)
        stickman(ctx, W / 2, 600 + 360 * z, z, 'sit', look=(0.3 * math.sin(t * 0.8), 0.1), fear=Q.get('fear', 0),
                 mouth=Q.get('mouth', 'flat'), blink=blink_at(t, 2.3), sweat=0.6 if tm == 'day' else 0, t=t, shadow=False)

    def big_text(ctx, s, y, size, col, a=1.0, spacing=0.0):
        label(ctx, s, W / 2, y, size, col, a)

    def T_title(ctx, t, d, Q):
        T_sea(ctx, t, d, dict(Q, shot='wide', pose='sit'))
        rgba(ctx, (0, 0, 0), 0.55); ctx.paint()
        p = eback(prog(t, 0.05, 0.5))
        big_text(ctx, Q['ttl'], 470, 170 * (0.6 + 0.4 * p), AMB if 'DAY' in Q['ttl'] else WHITE, clamp(p * 2))
        if Q.get('sub'): big_text(ctx, Q['sub'], 610, 70, ACC, eo(prog(t, 0.5, 0.9)))
        w = 600 * eio(prog(t, 0.3, 0.9))
        ctx.move_to(W / 2 - w / 2, 560 if not Q.get('sub') else 680); ctx.line_to(W / 2 + w / 2, 560 if not Q.get('sub') else 680)
        rgba(ctx, ACC); ctx.set_line_width(8); ctx.stroke()

    def T_choice(ctx, t, d, Q):
        T_sea(ctx, t, d, dict(Q, shot='wide', pose='sit', time='day' if Q['day'] not in (4,) else 'storm'))
        rgba(ctx, (0, 0, 0), 0.6); ctx.paint()
        for i, (k, txt, col) in enumerate((('A', Q['a'], ACC), ('B', Q['b'], (0.3, 0.7, 1.0)))):
            p = eback(prog(t, 0.1 + i * 0.15, 0.5 + i * 0.15))
            x = W / 2 + (-440 if i == 0 else 440)
            ctx.save(); ctx.translate(x, 450); ctx.scale(p, p)
            rr(ctx, -320, -190, 640, 380, 36); rgba(ctx, (0.05, 0.06, 0.08), 0.92); ctx.fill_preserve(); rgba(ctx, col); ctx.set_line_width(6); ctx.stroke()
            ctx.restore()
            if p > 0.3:
                label(ctx, k, x, 340, 90, col, clamp(p))
                label(ctx, txt, x, 500, 58 if len(txt) < 16 else 46, WHITE, clamp(p))
        if not Q.get('cta'):
            cd = d - 3.0
            if t > cd:
                left = 3 - (t - cd)
                ctx.arc(W / 2, 450, 70, -math.pi / 2, -math.pi / 2 + 2 * math.pi * (left / 3))
                rgba(ctx, AMB); ctx.set_line_width(14); ctx.stroke()
                label(ctx, str(int(math.ceil(left))), W / 2, 450, 90, WHITE)
            else:
                label(ctx, "?", W / 2, 450, 120, AMB, eo(prog(t, 0.4, 0.8)))

    def T_fact(ctx, t, d, Q):
        T_sea(ctx, t, d, dict(Q, shot='wide', pose='sit', time='day'))
        rgba(ctx, (0.01, 0.01, 0.03), 0.78); ctx.paint()
        p = eback(prog(t, 0.05, 0.45))
        ctx.save(); ctx.translate(W / 2, 430); ctx.scale(p, p)
        rr(ctx, -680, -150, 1360, 300, 30); rgba(ctx, (0.06, 0.07, 0.09), 0.95); ctx.fill_preserve(); rgba(ctx, AMB, 0.9); ctx.set_line_width(5); ctx.stroke()
        ctx.restore()
        if p > 0.4:
            label(ctx, Q['big'], W / 2, 400, 110, AMB, clamp(p))
            label(ctx, Q['sub'].upper(), W / 2, 520, 40, WHITE, eo(prog(t, 0.4, 0.8)), NORM)
        rr(ctx, W / 2 - 110, 210, 220, 54, 14); rgba(ctx, ACC); ctx.fill()
        label(ctx, "FACT", W / 2, 237, 36, WHITE)

    def T_items(ctx, t, d, Q):
        t = t + Q['boff'] * 0.6
        rgba(ctx, (0.02, 0.025, 0.04)); ctx.paint()
        names = ["2 L WATER", "ENERGY BARS", "SIGNAL MIRROR", "FISHING KIT", "TARP"]
        for i, n in enumerate(names):
            p = eback(prog(t, 0.3 + i * 0.45, 0.7 + i * 0.45))
            if p <= 0: continue
            x = 260 + i * 350; y = 430
            ctx.save(); ctx.translate(x, y); ctx.scale(p, p)
            ctx.arc(0, 0, 130, 0, 6.3); rgba(ctx, (0.08, 0.09, 0.12)); ctx.fill_preserve(); rgba(ctx, AMB, 0.8); ctx.set_line_width(4); ctx.stroke()
            if i == 0:
                rr(ctx, -30, -70, 60, 140, 16); rgba(ctx, (0.55, 0.8, 1), 0.85); ctx.fill(); rr(ctx, -16, -90, 32, 24, 6); rgba(ctx, (0.2, 0.4, 0.9)); ctx.fill()
            elif i == 1:
                for k in range(3): rr(ctx, -70 + k * 10, -40 + k * 24, 140, 36, 8); rgba(ctx, ((0.9, 0.5, 0.1), (0.8, 0.2, 0.2), (0.3, 0.6, 0.3))[k]); ctx.fill()
            elif i == 2:
                rr(ctx, -60, -60, 120, 120, 14); fill_grad(ctx, STEEL, -60, -60, 60, 60); ctx.fill(); ctx.arc(0, 0, 10, 0, 6.3); rgba(ctx, (0.1, 0.1, 0.1)); ctx.fill()
            elif i == 3:
                ctx.arc(0, 30, 40, 0, math.pi); ctx.move_to(40, 30); ctx.line_to(40, -70); rgba(ctx, (0.85, 0.85, 0.9)); ctx.set_line_width(8); ctx.stroke()
            else:
                ctx.move_to(-80, 50); ctx.line_to(-40, -60); ctx.line_to(80, -40); ctx.line_to(60, 60); ctx.close_path(); rgba(ctx, (0.95, 0.55, 0.12)); ctx.fill()
            ctx.restore()
            label(ctx, n, x, 640, 40, WHITE, clamp(p))

    def T_map(ctx, t, d, Q):
        rgba(ctx, (0.02, 0.07, 0.12)); ctx.paint()
        for x in range(0, W, 120): ctx.move_to(x, 0); ctx.line_to(x, H)
        for y in range(0, H, 120): ctx.move_to(0, y); ctx.line_to(W, y)
        rgba(ctx, CYAN, 0.07); ctx.set_line_width(2); ctx.stroke()
        ctx.move_to(0, 0); ctx.line_to(260, 0); ctx.curve_to(220, 300, 330, 500, 210, 800); ctx.line_to(240, H); ctx.line_to(0, H); ctx.close_path()
        rgba(ctx, (0.12, 0.2, 0.14)); ctx.fill()
        label(ctx, "LAND", 110, 300, 40, WHITE, 0.6, NORM)
        pts = [(560, 360), (720, 420), (880, 400), (1040, 480), (1200, 470), (1350, 540)]
        p = eio(prog(t, 0.3, d - 0.5))
        sub = poly_partial(pts, p)
        ctx.set_dash([18, 14]); draw_poly(ctx, sub); rgba(ctx, AMB); ctx.set_line_width(6); ctx.stroke(); ctx.set_dash([])
        label(ctx, "✕", 560, 360, 60, ACC); label(ctx, "BOAT SANK", 560, 290, 34, ACC, 1, NORM)
        ex, ey = sub[-1]; glow_dot(ctx, ex, ey, 14, (1, 0.55, 0.15))
        label(ctx, f"~{int(Q['miles'] * p)} MILES", ex, ey - 70, 50, AMB, clamp(p * 3), box=True)

    def hud(ctx, t, Q):
        if Q['tpl'] in ('title', 'items') or Q['day'] == 0: return
        x, y = 40, 36
        rr(ctx, x, y, 420, 170, 20); rgba(ctx, (0, 0, 0), 0.55); ctx.fill()
        label(ctx, f"DAY {Q['day']}", x + 80, y + 38, 38, AMB)
        bars = [("WATER", Q['water'] / 3.0, (0.35, 0.75, 1.0), f"{Q['water']:.1f} L"),
                ("ENERGY", Q['energy'] / 100, (0.3, 0.95, 0.5), f"{int(Q['energy'])}%"),
                ("HOPE", Q['hope'] / 100, AMB, f"{int(Q['hope'])}%")]
        for i, (n, v, c, txt) in enumerate(bars):
            yy = y + 78 + i * 32
            ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, NORM); ctx.set_font_size(20)
            ctx.move_to(x + 20, yy + 7); rgba(ctx, WHITE, 0.8); ctx.show_text(n)
            rr(ctx, x + 125, yy - 9, 200, 18, 9); rgba(ctx, (1, 1, 1), 0.12); ctx.fill()
            low = v < 0.3
            rr(ctx, x + 125, yy - 9, max(18, 200 * clamp(v)), 18, 9); rgba(ctx, ACC if low else c, 0.9 if not low else 0.6 + 0.4 * math.sin(t * 8)); ctx.fill()
            ctx.move_to(x + 335, yy + 7); rgba(ctx, WHITE); ctx.show_text(txt)

    TEMPLATES = dict(sea=T_sea, close=T_close, title=T_title, choice=T_choice, fact=T_fact, items=T_items, map=T_map)
    run(SCENES, theme='noir', fades=False)
