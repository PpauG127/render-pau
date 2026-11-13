"""Would You Survive 1 Minute on Every Planet? — 16:9 long-form, 10 locations."""
import os, sys, math, random
os.environ['FMT'] = '16x9'
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
import storyplan as SP
PER_JOB = 12
SP.DANGER |= {'boil', 'boils', 'boiling', 'crushed', 'crush', 'acid', 'melt', 'freeze', 'frozen', 'storm', 'dead', 'die',
              'faint', 'pass', 'burn', 'burning', 'hotter', 'colder', 'radiation', 'falling', 'fall', 'lightning', 'deadly', 'hell', 'unconscious'}
SP.GOOD |= {'twist', 'float', 'floating', 'bounce', 'earth', 'heart', 'diamonds', 'rings', 'jump', 'saved', 'home', 'airship'}

# planet look-up: sky top/bottom, ground colors, sun size, fx
L = {
 'moon':    dict(name='THE MOON', sky=((0, 0, 0), (0.02, 0.02, 0.04)), g=((0.55, 0.55, 0.57), (0.3, 0.3, 0.32)), sun=26, stars=1, earth=1, craters=1, temp='250°F / -208°F', grav='0.17 g'),
 'mars':    dict(name='MARS', sky=((0.45, 0.25, 0.18), (0.85, 0.6, 0.45)), g=((0.75, 0.35, 0.18), (0.45, 0.18, 0.1)), sun=22, dust=1, temp='-85°F', grav='0.38 g'),
 'mercury': dict(name='MERCURY', sky=((0, 0, 0), (0.05, 0.03, 0.02)), g=((0.55, 0.5, 0.45), (0.3, 0.27, 0.24)), sun=150, stars=1, craters=1, heat=1, temp='800°F', grav='0.38 g'),
 'venus':   dict(name='VENUS', sky=((0.55, 0.35, 0.1), (0.95, 0.7, 0.3)), g=((0.5, 0.3, 0.12), (0.25, 0.12, 0.05)), sun=0, haze=1, heat=1, lava=1, temp='867°F', grav='0.9 g'),
 'jupiter': dict(name='JUPITER', bands=((0.85, 0.7, 0.55), (0.65, 0.4, 0.25), (0.95, 0.88, 0.75), (0.55, 0.3, 0.2)), temp='-166°F', grav='2.4 g'),
 'saturn':  dict(name='SATURN', bands=((0.9, 0.82, 0.6), (0.8, 0.68, 0.45), (0.95, 0.9, 0.72), (0.7, 0.58, 0.38)), rings=1, temp='-220°F', grav='1.1 g'),
 'uranus':  dict(name='URANUS', bands=((0.6, 0.85, 0.88), (0.5, 0.78, 0.82), (0.7, 0.9, 0.92), (0.45, 0.72, 0.78)), temp='-320°F', grav='0.9 g'),
 'neptune': dict(name='NEPTUNE', bands=((0.2, 0.35, 0.85), (0.15, 0.25, 0.7), (0.3, 0.45, 0.95), (0.1, 0.2, 0.6)), wind=1, temp='-330°F', grav='1.1 g'),
 'pluto':   dict(name='PLUTO', sky=((0, 0, 0.01), (0.02, 0.03, 0.06)), g=((0.92, 0.88, 0.85), (0.65, 0.6, 0.62)), sun=6, stars=1, ice=1, temp='-375°F', grav='0.06 g'),
 'titan':   dict(name='TITAN (SATURN MOON)', sky=((0.45, 0.3, 0.1), (0.8, 0.55, 0.25)), g=((0.35, 0.25, 0.15), (0.2, 0.14, 0.08)), sun=0, haze=1, lakes=1, temp='-290°F', grav='0.14 g'),
 'sun':     dict(name='THE SUN', bands=((1, 0.85, 0.3), (1, 0.6, 0.15), (1, 0.95, 0.6), (0.95, 0.45, 0.1)), temp='10,000°F', grav='28 g'),
 'vclouds': dict(name='VENUS · 31 MILES UP', sky=((0.85, 0.7, 0.45), (1.0, 0.88, 0.62)), temp='32-122°F', grav='0.9 g', clouds=1),
}

BEATS = [
 ('land', dict(p='moon', pose='scared', fear=1, emote='!'), "You have one minute. No spaceship. No second chances. Just you, and a planet that wants you dead."),
 ('travel', dict(p='moon'), "So, would you survive one minute on every planet? Let's find out. And the place you survive longest will surprise you."),
 ('title', dict(p='moon', ttl='THE MOON'), "First stop, the Moon."),
 ('land', dict(p='moon', pose='jump', hop=1, helmet=1, mouth='smile'), "Good news: your suit works. And with only a sixth of Earth's gravity, you can jump six times higher."),
 ('land', dict(p='moon', pose='idle', helmet=1, look=(0.6, -0.8)), "In the sun, the ground hits 250 degrees Fahrenheit. In the shade, minus 208."),
 ('choice', dict(p='moon', a='TAKE THE HELMET OFF', b='KEEP IT ON'), "Your visor is fogging up. Take off the helmet for a second?"),
 ('land', dict(p='moon', pose='scared', fear=1, mouth='o', emote='!'), "No air means no pressure. The saliva on your tongue starts to boil. In about fifteen seconds, you pass out."),
 ('fact', dict(big='~15 SECONDS', sub='of consciousness in a vacuum'), "That's how long your brain lasts without oxygen in a vacuum. Keep the helmet on."),
 ('travel', dict(p='mars'), "Next, the planet everyone wants to live on."),
 ('title', dict(p='mars', ttl='MARS'), "Mars."),
 ('land', dict(p='mars', pose='idle', helmet=1, look=(1, 0)), "It looks like a desert on Earth. But the air is less than one percent as thick as ours, and it's mostly carbon dioxide."),
 ('land', dict(p='mars', pose='hug', shiver=1, helmet=1, frost=0.5), "And it's cold. The average is minus 85 degrees Fahrenheit."),
 ('land', dict(p='mars', storm=1, pose='scared', helmet=1, fear=1), "Then the sky turns brown. A dust storm. Some of them swallow the entire planet for weeks."),
 ('close', dict(p='mars', mouth='wavy', fear=0.7, helmet=1), "Without your suit, the air is so thin that your saliva and tears would boil. Mars would knock you out in seconds."),
 ('travel', dict(p='mercury'), "Now, the planet closest to the Sun."),
 ('title', dict(p='mercury', ttl='MERCURY'), "Mercury."),
 ('land', dict(p='mercury', pose='scared', sweat=1, helmet=1, fear=0.7), "The Sun looks three times bigger than at home. The ground hits 800 degrees Fahrenheit, hot enough to melt lead."),
 ('choice', dict(p='mercury', a='RUN TO THE SHADE', b='WAIT FOR NIGHT'), "Run for the shadows, or wait for night?"),
 ('land', dict(p='mercury', night=1, pose='hug', frost=1, helmet=1, shiver=1), "Careful. Mercury has almost no air to hold heat. At night it drops to minus 290. From oven to freezer."),
 ('fact', dict(big='1,000°F+ SWING', sub='between Mercury day and night'), "That's a swing of more than a thousand degrees between day and night."),
 ('travel', dict(p='venus'), "But Mercury is not the hottest planet. That title goes to its neighbor."),
 ('title', dict(p='venus', ttl='VENUS'), "Venus."),
 ('land', dict(p='venus', pose='scared', fear=1, helmet=1, sweat=1), "Welcome to hell. 867 degrees Fahrenheit, day and night, everywhere."),
 ('land', dict(p='venus', pose='brace', fear=1, helmet=1, squash=1), "The air is so thick it crushes you like being three thousand feet under the ocean."),
 ('land', dict(p='venus', pose='scared', fear=1, helmet=1, acid=1), "And the clouds above you? Sulfuric acid."),
 ('fact', dict(big='~2 HOURS', sub='the longest any probe has survived there'), "The toughest probes ever sent there lasted about two hours before Venus destroyed them. Remember this planet. We'll come back to it."),
 ('travel', dict(p='jupiter'), "Next, the giant."),
 ('title', dict(p='jupiter', ttl='JUPITER'), "Jupiter."),
 ('gas', dict(p='jupiter', fear=1, emote='!'), "Here's the problem. There is no ground. You step out, and you start falling."),
 ('gas', dict(p='jupiter', fear=1, lightning=1), "Through clouds of ammonia, through lightning storms, pulled down by gravity more than twice as strong as Earth's."),
 ('orbit', dict(p='jupiter', spot=1), "Below you swirls the Great Red Spot, a storm bigger than the whole Earth."),
 ('gas', dict(p='jupiter', fear=1, deep=1), "The deeper you fall, the hotter and heavier the air gets, until it crushes you. You never hit the bottom."),
 ('travel', dict(p='saturn'), "Saturn is next."),
 ('title', dict(p='saturn', ttl='SATURN'), "Saturn."),
 ('orbit', dict(p='saturn'), "Fun fact: Saturn is so light that if you found a bathtub big enough, it would float."),
 ('gas', dict(p='saturn', fear=0.6, wind=1), "But you're falling again. Winds here blow over a thousand miles per hour, and it's minus 220 degrees."),
 ('choice', dict(p='saturn', a='GRAB A RING ROCK', b='KEEP FALLING'), "Could you grab one of the rings on the way down?"),
 ('fact', dict(big='ICE & ROCK', sub='the rings are billions of chunks'), "The rings are billions of chunks of ice and rock, some as small as dust, some as big as houses. Grab one, and it spins you like a toy."),
 ('travel', dict(p='titan'), "But wait. Before we leave Saturn, there's a moon you need to see."),
 ('title', dict(p='titan', ttl='TITAN'), "Titan, Saturn's biggest moon."),
 ('land', dict(p='titan', pose='idle', helmet=1, look=(1, 0.3)), "It has lakes and rivers, and even rain. But it's not water. It's liquid methane, at minus 290 degrees."),
 ('land', dict(p='titan', pose='relief', helmet=1, mouth='smile'), "Here's the crazy part. The air is thicker than Earth's, so you wouldn't need a pressure suit. Just warm clothes and an oxygen mask."),
 ('land', dict(p='titan', pose='jump', hop=2, wings=1, helmet=1, mouth='smile'), "And with thick air and weak gravity, scientists say you could strap on wings and fly by flapping your arms."),
 ('choice', dict(p='titan', a='FLY OVER THE LAKES', b='STAY ON THE GROUND'), "Would you try it? Fly over a lake of methane?"),
 ('fact', dict(p='titan', big='THICKER AIR THAN EARTH', sub="titan's air is about 1.5 times earth's pressure"), "Titan's air pressure is about one and a half times Earth's. Just don't fall in. Those lakes would freeze you instantly."),
 ('travel', dict(p='uranus'), "Far, far out, the strangest planet of all."),
 ('title', dict(p='uranus', ttl='URANUS'), "Uranus."),
 ('orbit', dict(p='uranus', tilt=1), "It spins on its side, like a ball rolling around the Sun. Each pole gets about forty two years of sunlight, then forty two years of darkness."),
 ('gas', dict(p='uranus', fear=0.8, frost=1), "Its air drops to around minus 320 degrees. Your suit's heaters fight a losing battle."),
 ('travel', dict(p='neptune'), "And then, the windiest place we know."),
 ('title', dict(p='neptune', ttl='NEPTUNE'), "Neptune."),
 ('gas', dict(p='neptune', fear=1, wind=2, emote='!'), "Winds of more than thirteen hundred miles per hour. Faster than a fighter jet. Nothing could hold on."),
 ('close', dict(p='neptune', mouth='o', fear=1, helmet=1), "You'd be thrown around the planet before you could even scream."),
 ('travel', dict(p='pluto'), "One last stop, at the edge of the solar system."),
 ('title', dict(p='pluto', ttl='PLUTO'), "Pluto."),
 ('land', dict(p='pluto', pose='hug', frost=1, helmet=1, shiver=1), "Minus 375 degrees. The Sun is just a bright star in the sky."),
 ('land', dict(p='pluto', pose='jump', hop=2, helmet=1, mouth='smile', heart=1), "But look down. You are standing on a giant heart-shaped plain of frozen nitrogen. And with tiny gravity, one jump sends you flying."),
 ('fact', dict(big='-375°F', sub='colder than anything on Earth'), "Pluto is so far away that sunlight takes hours to reach it."),
 ('travel', dict(p='sun'), "And what about the Sun itself? Just for fun."),
 ('orbit', dict(p='sun'), "Its surface is about ten thousand degrees Fahrenheit. Your spaceship would melt long before you arrived."),
 ('close', dict(p='sun', mouth='o', fear=1, sweat=1), "Okay. Bad idea. Let's turn around."),
 ('choice', dict(p='sun', a='MARS', b='THE MOON'), "So, out of everything you've seen, where would you last the longest? Mars? The Moon?"),
 ('close', dict(p='vclouds', mouth='flat', fear=0, helmet=1), "Here's the twist."),
 ('travel', dict(p='venus'), "Remember Venus? The planet we called hell?"),
 ('land', dict(p='vclouds', airship=1, pose='idle', helmet=1, mouth='smile'), "Fly thirty one miles above its surface, and everything changes. The pressure is about the same as on Earth."),
 ('land', dict(p='vclouds', airship=1, pose='relief', helmet=1, mouth='smile'), "The temperature is about the same as a hot day at home. NASA has even studied floating airships up here."),
 ('fact', dict(big='MOST EARTH-LIKE', sub='Venus clouds at about 31 miles up'), "The most Earth-like place in the solar system, outside Earth, is floating in the clouds of hell. You'd still need oxygen and protection from the acid. But you'd survive."),
 ('choice', dict(p='vclouds', a='WHICH PLANET', b='WOULD YOU VISIT?', cta=1), "So, which planet would you visit first? Tell me in the comments. And where should I send you next?"),
]
SCENES = SP.build(BEATS, wps=2.0, state=dict(p='moon'), cut_tpls=('land', 'gas', 'close'), react_tpls=('land', 'gas'))
TOTAL = sum(x[0] for x in SCENES)

# =================================================================== drawing
if __name__ == "__main__":
    from story import *
    HZ = 640

    def starfield(ctx, t, n=160, a=1.0, speed=0.0):
        rnd = random.Random(9)
        for _ in range(n):
            x = (rnd.uniform(0, W) - speed * t * rnd.uniform(0.5, 2)) % W; y = rnd.uniform(0, H)
            ctx.arc(x, y, rnd.uniform(0.8, 2.4), 0, 6.3); rgba(ctx, WHITE, a * rnd.uniform(0.3, 1) * (0.7 + 0.3 * math.sin(t * 2 + x)))
            ctx.fill()

    def planet(ctx, x, y, r, P, t, a=1.0, spot=False, tilt=False):
        if r < 2: return
        bands = P.get('bands')
        base = bands[0] if bands else P.get('g', ((0.6, 0.6, 0.6), (0.3, 0.3, 0.3)))[0]
        if P.get('rings'):
            ctx.save(); ctx.translate(x, y); ctx.rotate(-0.25); ctx.scale(1, 0.28)
            for k, al in ((1.9, 0.5), (1.65, 0.7), (1.45, 0.4)):
                ctx.arc(0, 0, r * k, math.pi, 2 * math.pi); rgba(ctx, (0.9, 0.82, 0.6), al * a); ctx.set_line_width(r * 0.16); ctx.stroke()
            ctx.restore()
        g = cairo.RadialGradient(x - r * 0.35, y - r * 0.35, r * 0.1, x, y, r)
        g.add_color_stop_rgba(0, min(1, base[0] + 0.2), min(1, base[1] + 0.2), min(1, base[2] + 0.2), a)
        g.add_color_stop_rgba(1, base[0] * 0.5, base[1] * 0.5, base[2] * 0.5, a)
        ctx.arc(x, y, r, 0, 6.3); ctx.set_source(g); ctx.fill()
        ctx.save(); ctx.arc(x, y, r, 0, 6.3); ctx.clip()
        if tilt: ctx.translate(x, y); ctx.rotate(1.45); ctx.translate(-x, -y)
        if bands:
            for i in range(14):
                yy = y - r + i * 2 * r / 14
                ctx.move_to(x - r, yy)
                for xx in range(int(x - r), int(x + r) + 10, 20):
                    ctx.line_to(xx, yy + 6 * math.sin(xx / 40 + t + i))
                ctx.line_to(x + r, yy + 2 * r / 14 + 4); ctx.line_to(x - r, yy + 2 * r / 14 + 4); ctx.close_path()
                rgba(ctx, bands[i % len(bands)], 0.55 * a); ctx.fill()
        if P.get('craters'):
            rnd = random.Random(4)
            for _ in range(14):
                cx_, cy_, cr = x + rnd.uniform(-r, r), y + rnd.uniform(-r, r), rnd.uniform(r * 0.04, r * 0.15)
                ctx.arc(cx_, cy_, cr, 0, 6.3); rgba(ctx, (0, 0, 0), 0.18 * a); ctx.fill()
        if spot:
            ctx.save(); ctx.translate(x + r * 0.3, y + r * 0.25); ctx.rotate(t * 0.3); ctx.scale(1, 0.55)
            for k in range(4):
                ctx.arc(0, 0, r * (0.22 - k * 0.045), 0, 6.3); rgba(ctx, (0.75 - k * 0.05, 0.25, 0.15), 0.6 * a); ctx.fill()
            ctx.restore()
        if P.get('ice'):
            ctx.save(); ctx.translate(x + r * 0.15, y + r * 0.2); ctx.scale(r / 260, r / 260)
            ctx.move_to(0, 60); ctx.curve_to(-120, -20, -60, -110, 0, -50); ctx.curve_to(60, -110, 120, -20, 0, 60)
            rgba(ctx, (1, 0.95, 0.9), 0.75 * a); ctx.fill(); ctx.restore()
        ctx.restore()
        sh = cairo.LinearGradient(x - r, y, x + r, y)
        sh.add_color_stop_rgba(0, 0, 0, 0, 0); sh.add_color_stop_rgba(0.6, 0, 0, 0, 0.1 * a); sh.add_color_stop_rgba(1, 0, 0, 0.02, 0.75 * a)
        ctx.arc(x, y, r, 0, 6.3); ctx.set_source(sh); ctx.fill()
        if P.get('rings'):
            ctx.save(); ctx.translate(x, y); ctx.rotate(-0.25); ctx.scale(1, 0.28)
            for k, al in ((1.9, 0.5), (1.65, 0.7), (1.45, 0.4)):
                ctx.arc(0, 0, r * k, 0, math.pi); rgba(ctx, (0.9, 0.82, 0.6), al * a); ctx.set_line_width(r * 0.16); ctx.stroke()
            ctx.restore()

    def rocket(ctx, x, y, s, t, ang=0.0):
        ctx.save(); ctx.translate(x, y); ctx.rotate(ang); ctx.scale(s, s)
        for k in range(3):
            q = (t * 8 + k / 3) % 1
            glow_dot(ctx, -120 - 70 * q, 0, 26 * (1 - q) + 6, (1, 0.6 - 0.3 * q, 0.15), 1 - q)
        ctx.move_to(-110, -36); ctx.line_to(60, -36); ctx.curve_to(120, -36, 150, -10, 160, 0); ctx.curve_to(150, 10, 120, 36, 60, 36); ctx.line_to(-110, 36); ctx.close_path()
        fill_grad(ctx, [(0, (0.95, 0.96, 1)), (0.5, (0.75, 0.78, 0.84)), (1, (0.45, 0.48, 0.55))], 0, -36, 0, 36); ctx.fill()
        for sy in (-1, 1):
            ctx.move_to(-110, sy * 36); ctx.line_to(-150, sy * 80); ctx.line_to(-70, sy * 36); ctx.close_path(); rgba(ctx, ACC); ctx.fill()
        ctx.arc(70, 0, 16, 0, 6.3); rgba(ctx, (0.3, 0.6, 1)); ctx.fill_preserve(); rgba(ctx, WHITE); ctx.set_line_width(4); ctx.stroke()
        ctx.restore()

    def shot_transform(ctx, t, d, Q, cx, cy):
        sh = Q['shot']; k = clamp(t / max(d, 0.1))
        if sh == 'close': z, ox, oy = 1.7 - 0.08 * k, cx, cy - 60
        elif sh == 'low': z, ox, oy = 1.3, cx + 120 - 160 * k, cy - 20
        elif sh == 'mid': z, ox, oy = 1.15 + 0.08 * k, cx - 80 * k, cy
        elif sh == 'dutch':
            ctx.translate(W / 2, H / 2); ctx.rotate(0.07 - 0.03 * k); ctx.translate(-W / 2, -H / 2)
            z, ox, oy = 1.35, cx + 40, cy - 40
        else: z, ox, oy = 1.0 + 0.05 * k, W / 2, H / 2
        ctx.translate(W / 2, H / 2); ctx.scale(z, z); ctx.translate(-ox, -oy)

    def ridge(ctx, y0, amp, seed, col, a=1.0, freq=1.0):
        rnd = random.Random(seed); ph = [rnd.uniform(0, 6) for _ in range(3)]
        ctx.move_to(-800, H + 600); ctx.line_to(-800, y0)
        for x in range(-800, W + 820, 20):
            yy = y0 - amp * (0.5 * math.sin(x / 260 * freq + ph[0]) + 0.3 * math.sin(x / 110 * freq + ph[1]) + 0.2 * math.sin(x / 47 * freq + ph[2]))
            ctx.line_to(x, yy)
        ctx.line_to(W + 820, H + 600); ctx.close_path(); rgba(ctx, col, a); ctx.fill()

    def T_land(ctx, t, d, Q):
        P = L[Q['p']]; night = Q.get('night')
        sx_ = W / 2 + 40 * math.sin(t * 0.5)
        hop = abs(math.sin(t * (1.6 if Q.get('hop') == 1 else 1.1))) * (260 if Q.get('hop') == 1 else 380) if Q.get('hop') else 0
        sy_ = 900 - hop
        ctx.save(); shot_transform(ctx, t, d, Q, sx_, sy_ - 250)
        top, bot = P.get('sky', ((0, 0, 0), (0, 0, 0)))
        if night: top, bot = (0, 0, 0.01), (0.02, 0.02, 0.05)
        g = cairo.LinearGradient(0, -400, 0, HZ + 100); g.add_color_stop_rgb(0, *top); g.add_color_stop_rgb(1, *bot)
        ctx.rectangle(-900, -900, W + 1800, HZ + 1100); ctx.set_source(g); ctx.fill()
        if P.get('stars') or night: starfield(ctx, t)
        if P.get('earth'): planet(ctx, 1500, 210, 70, dict(bands=((0.2, 0.45, 0.9), (0.95, 0.97, 1), (0.2, 0.55, 0.3))), t)
        if P.get('sun') and not night:
            sr = P['sun']
            gg = cairo.RadialGradient(1450, 230, sr * 0.5, 1450, 230, sr * 6)
            gg.add_color_stop_rgba(0, 1, 0.95, 0.8, 0.9); gg.add_color_stop_rgba(1, 1, 0.9, 0.7, 0)
            ctx.set_source(gg); ctx.paint(); ctx.arc(1450, 230, sr, 0, 6.3); rgba(ctx, (1, 0.98, 0.92)); ctx.fill()
        if P.get('clouds'):
            for k in range(9):
                cx_ = (k * 300 - t * 60 * (1 + k % 3)) % (W + 600) - 300; cy_ = 200 + (k * 97) % 600
                ctx.save(); ctx.translate(cx_, cy_); ctx.scale(2.4, 0.6); ctx.arc(0, 0, 120, 0, 6.3); ctx.restore()
                rgba(ctx, (1, 0.95, 0.8), 0.35); ctx.fill()
        else:
            gc = P.get('g', ((0.5, 0.5, 0.5), (0.3, 0.3, 0.3)))
            far = tuple(c * 0.6 + b * 0.4 for c, b in zip(gc[1], bot))
            ridge(ctx, HZ - 40, 90, 1, far, 1, 0.6)
            ridge(ctx, HZ + 60, 60, 2, gc[1])
            ridge(ctx, 820, 30, 3, gc[0])
            if P.get('craters'):
                rnd = random.Random(7)
                for _ in range(7):
                    cx_, cy_, cr = rnd.uniform(0, W), rnd.uniform(860, 1060), rnd.uniform(40, 140)
                    ctx.save(); ctx.translate(cx_, cy_); ctx.scale(1, 0.25); ctx.arc(0, 0, cr, 0, 6.3); ctx.restore()
                    rgba(ctx, (0, 0, 0), 0.25); ctx.fill()
            if P.get('ice') and Q.get('heart'):
                ctx.save(); ctx.translate(W / 2, 1000); ctx.scale(3.2, 0.7)
                ctx.move_to(0, 60); ctx.curve_to(-120, -20, -60, -110, 0, -50); ctx.curve_to(60, -110, 120, -20, 0, 60); ctx.restore()
                rgba(ctx, (1, 0.97, 0.95), 0.8); ctx.fill()
            if P.get('lava'):
                for k in range(5):
                    ctx.move_to(100 + k * 380, 1080); ctx.curve_to(200 + k * 380, 950, 160 + k * 380, 880, 260 + k * 380, 830)
                    rgba(ctx, (1, 0.45, 0.1), 0.6 + 0.3 * math.sin(t * 3 + k)); ctx.set_line_width(10); ctx.stroke()
            if P.get('heat') and not night:
                for k in range(10):
                    y = 760 + k * 30
                    ctx.move_to(-20, y)
                    for x in range(0, W + 40, 40): ctx.line_to(x, y + 5 * math.sin(x / 50 + t * 8 + k))
                    rgba(ctx, (1, 0.7, 0.4), 0.08); ctx.set_line_width(4); ctx.stroke()
                rgba(ctx, (1, 0.35, 0.1), 0.12); ctx.paint()
        if Q.get('airship'):
            ax, ay = W / 2 + 330, 420 + 15 * math.sin(t)
            ctx.save(); ctx.translate(ax, ay); ctx.scale(1, 0.42); ctx.arc(0, 0, 300, 0, 6.3); ctx.restore()
            fill_grad(ctx, [(0, (0.98, 0.98, 1)), (1, (0.65, 0.68, 0.75))], 0, ay - 130, 0, ay + 130); ctx.fill()
            rr(ctx, ax - 110, ay + 120, 220, 70, 18); rgba(ctx, (0.3, 0.32, 0.38)); ctx.fill()
            for k in range(4): rr(ctx, ax - 90 + k * 50, ay + 135, 34, 30, 6); rgba(ctx, AMB, 0.8); ctx.fill()
            sy_ = ay + 190 + 150 * 0.62
        if P.get('lakes'):
            for k, (lx, ly, lw) in enumerate(((300, 930, 260), (1500, 960, 340), (900, 1040, 200))):
                ctx.save(); ctx.translate(lx, ly); ctx.scale(1, 0.22); ctx.arc(0, 0, lw, 0, 6.3); ctx.restore()
                rgba(ctx, (0.12, 0.08, 0.04), 0.85); ctx.fill()
                ctx.save(); ctx.translate(lx, ly); ctx.scale(1, 0.22); ctx.arc(0, 0, lw * (0.6 + 0.1 * math.sin(t * 2 + k)), 3.6, 5.4); ctx.restore()
                rgba(ctx, (1, 0.8, 0.5), 0.25); ctx.set_line_width(3); ctx.stroke()
        if Q.get('wings'):
            fl = math.sin(t * 9)
            for sgn in (-1, 1):
                ctx.move_to(sx_, sy_ - 260); ctx.curve_to(sx_ + sgn * 120, sy_ - 330 - 80 * fl, sx_ + sgn * 260, sy_ - 300 - 120 * fl, sx_ + sgn * 330, sy_ - 260 - 140 * fl)
                ctx.line_to(sx_ + sgn * 120, sy_ - 200); ctx.close_path()
                fill_grad(ctx, [(0, (1, 0.6, 0.15)), (1, (0.85, 0.3, 0.05))], sx_ - 330, 0, sx_ + 330, 0, 0.9); ctx.fill()
        # character
        shadow_y = 900
        if not P.get('clouds'):
            sc = max(0.3, 1 - hop / 500)
            ctx.save(); ctx.translate(sx_, shadow_y + 8); ctx.scale(1, 0.18); ctx.arc(0, 0, 100 * sc, 0, 6.3); ctx.restore(); rgba(ctx, (0, 0, 0), 0.4); ctx.fill()
        pose = Q.get('pose', 'idle')
        if pose == 'idle': pose = lerp_pose('idle', 'point', 0.3 * (0.5 + 0.5 * math.sin(t * 1.5)))
        stickman(ctx, sx_ if not Q.get('airship') else W / 2 + 330, sy_ if not Q.get('airship') else sy_ + 70, 0.95 if not Q.get('airship') else 0.55, pose,
                 look=Q.get('look', (math.sin(t * 1.2), 0.2)), fear=Q.get('fear', 0), mouth=Q.get('mouth', 'flat'), blink=blink_at(t),
                 sweat=Q.get('sweat', 0), t=t, shadow=False, tilt=0.12 * math.sin(t * 1.9), emote=Q.get('emote'),
                 shiver=Q.get('shiver', 0), helmet=bool(Q.get('helmet')), frost=Q.get('frost', 0),
                 squash=0.12 + 0.05 * math.sin(t * 5) if Q.get('squash') else 0.0, rot=-0.15 if Q.get('storm') else 0.0)
        # foreground effects
        if P.get('dust') or Q.get('storm'):
            n = 160 if Q.get('storm') else 40
            for k in range(n):
                rnd = random.Random(k)
                x = (rnd.uniform(0, W) + t * (900 if Q.get('storm') else 120) * rnd.uniform(0.6, 1.4)) % (W + 400) - 200
                y = rnd.uniform(100, H)
                ctx.arc(x, y, rnd.uniform(2, 6), 0, 6.3); rgba(ctx, (0.85, 0.5, 0.3), 0.5); ctx.fill()
            if Q.get('storm'): rgba(ctx, (0.55, 0.28, 0.15), 0.35 + 0.15 * math.sin(t * 2)); ctx.paint()
        if P.get('haze'):
            for k in range(5):
                y = 200 + k * 150 + 20 * math.sin(t + k)
                gg = cairo.LinearGradient(0, y - 120, 0, y + 120)
                gg.add_color_stop_rgba(0, 1, 0.7, 0.3, 0); gg.add_color_stop_rgba(0.5, 1, 0.7, 0.3, 0.18); gg.add_color_stop_rgba(1, 1, 0.7, 0.3, 0)
                ctx.set_source(gg); ctx.rectangle(-900, y - 120, W + 1800, 240); ctx.fill()
            if (t * 1.1) % 2.7 < 0.1: rgba(ctx, (1, 0.95, 0.8), 0.35); ctx.paint()
        if Q.get('acid'):
            for k in range(60):
                rnd = random.Random(k); x = (rnd.uniform(0, W) + t * 80) % W; y = (rnd.uniform(0, H) + t * 700) % H
                ctx.move_to(x, y); ctx.line_to(x - 6, y + 34); rgba(ctx, (0.8, 1, 0.3), 0.55); ctx.set_line_width(3); ctx.stroke()
        ctx.restore()

    def T_gas(ctx, t, d, Q):
        P = L[Q['p']]; bands = P['bands']
        spd = 900 if not Q.get('deep') else 1500
        ctx.save(); shot_transform(ctx, t, d, Q, W / 2, H / 2)
        for i in range(-2, 12):
            y = (i * 140 - t * spd) % (14 * 140) - 280
            ctx.move_to(-900, y)
            for x in range(-900, W + 920, 40): ctx.line_to(x, y + 30 * math.sin(x / 200 + i + t * (3 if P.get('wind') else 1)))
            ctx.line_to(W + 920, y + 200); ctx.line_to(-900, y + 200); ctx.close_path()
            c = bands[i % len(bands)]
            if Q.get('deep'): c = tuple(min(1, v * 0.6 + 0.35 * (j == 0)) for j, v in enumerate(c))
            rgba(ctx, c, 0.95); ctx.fill()
        if Q.get('wind') or P.get('wind'):
            for k in range(50):
                rnd = random.Random(k); x = (rnd.uniform(0, W) + t * 2600 * rnd.uniform(0.6, 1.3)) % (W + 600) - 300; y = rnd.uniform(0, H)
                ctx.move_to(x, y); ctx.line_to(x - 220, y); rgba(ctx, WHITE, 0.35); ctx.set_line_width(3); ctx.stroke()
        if Q.get('lightning') and (t * 1.5) % 1.7 < 0.12:
            x = 400 + 1100 * ((int(t * 1.5 / 1.7) * 0.41) % 1)
            ctx.move_to(x, 0)
            for i in range(1, 8): ctx.line_to(x + random.Random(i + int(t)).uniform(-70, 70), i * 150)
            rgba(ctx, (0.9, 0.95, 1)); ctx.set_line_width(6); ctx.stroke(); rgba(ctx, (0.8, 0.85, 1), 0.3); ctx.paint()
        if Q.get('deep'): rgba(ctx, (0.6, 0.1, 0.05), 0.3 + 0.2 * clamp(t / d)); ctx.paint()
        if Q.get('frost'): rgba(ctx, (0.6, 0.9, 1), 0.2); ctx.paint()
        fx = W / 2 + 120 * math.sin(t * 1.3); fy = H / 2 - 40 + 40 * math.sin(t * 2.1)
        stickman(ctx, fx, fy + 200, 0.85, 'scared', look=(0, -1), fear=Q.get('fear', 1), mouth='o', t=t, shadow=False,
                 rot=0.6 * math.sin(t * 2.4) + (t * 3 if Q.get('wind') == 2 else 0), helmet=True, emote=Q.get('emote'),
                 frost=1 if Q.get('frost') else 0, shiver=1 if Q.get('frost') else 0, tilt=0.2 * math.sin(t * 4))
        ctx.restore()

    def T_orbit(ctx, t, d, Q):
        P = L[Q['p']]
        rgba(ctx, (0, 0, 0.01)); ctx.paint(); starfield(ctx, t, 220)
        z = 1 + 0.12 * clamp(t / d)
        if Q['p'] == 'sun':
            gg = cairo.RadialGradient(W / 2 + 120, H / 2 + 40, 300 * z, W / 2 + 120, H / 2 + 40, 900 * z)
            gg.add_color_stop_rgba(0, 1, 0.7, 0.2, 0.9); gg.add_color_stop_rgba(1, 1, 0.4, 0.1, 0); ctx.set_source(gg); ctx.paint()
        planet(ctx, W / 2 + 120, H / 2 + 40, 380 * z, P, t, spot=Q.get('spot'), tilt=Q.get('tilt'))
        if Q['p'] == 'sun': rgba(ctx, (1, 0.6, 0.2), 0.15 + 0.08 * math.sin(t * 7)); ctx.paint()
        if Q.get('tilt'):
            ctx.save(); ctx.translate(W / 2 + 120, H / 2 + 40); ctx.rotate(1.45); ctx.scale(0.25, 1)
            ctx.arc(0, 0, 560 * z, 0, 6.3); ctx.restore(); rgba(ctx, (0.7, 0.9, 1), 0.35); ctx.set_line_width(5); ctx.stroke()
            ctx.arc(W / 2 + 120, H / 2 + 40, 470 * z, -0.4 + t * 0.6, 0.6 + t * 0.6); glow_stroke(ctx, AMB, 5, 0.8)
        if P.get('rings') and t > 0.5:
            label(ctx, "WOULD FLOAT IN WATER", 420, 860, 46, AMB, eo(prog(t, 0.6, 1.0)), box=True)
        rocket(ctx, 260 + 120 * t, 300 + 30 * math.sin(t), 0.6, t, 0.2)

    def T_travel(ctx, t, d, Q):
        P = L[Q['p']]
        rgba(ctx, (0, 0, 0.01)); ctx.paint()
        for k in range(120):
            rnd = random.Random(k); y = rnd.uniform(0, H); x = (rnd.uniform(0, W) - t * 2400 * rnd.uniform(0.4, 1.4)) % (W + 400)
            ctx.move_to(x, y); ctx.line_to(x + 160 * rnd.uniform(0.4, 1.4), y); rgba(ctx, (0.7, 0.85, 1), rnd.uniform(0.3, 0.9)); ctx.set_line_width(2); ctx.stroke()
        pr = eio(clamp(t / d))
        planet(ctx, W + 300 - 900 * pr, H / 2 + 60, 120 + 300 * pr, P, t)
        rocket(ctx, 520 + 60 * math.sin(t * 2), H / 2 + 30 * math.sin(t * 3), 1.2, t, 0.05 * math.sin(t * 2))

    def T_title(ctx, t, d, Q):
        P = L[Q['p']]
        rgba(ctx, (0, 0, 0.01)); ctx.paint(); starfield(ctx, t, 220)
        p = eback(prog(t, 0.05, 0.6))
        planet(ctx, W / 2, H / 2 + 120, 330 * (0.6 + 0.4 * p), P, t)
        rgba(ctx, (0, 0, 0), 0.35); ctx.paint()
        label(ctx, Q['ttl'], W / 2, 330, 170 * (0.6 + 0.4 * p), WHITE, clamp(p * 2))
        info = f"{P['temp']}   ·   GRAVITY {P['grav']}"
        label(ctx, info, W / 2, 470, 46, AMB, eo(prog(t, 0.5, 0.9)), box=True)

    def T_choice(ctx, t, d, Q):
        T_land(ctx, t, d, dict(Q, shot='wide', pose='idle', helmet=1)) if 'sky' in L[Q['p']] or L[Q['p']].get('clouds') else T_gas(ctx, t, d, dict(Q, shot='wide', fear=0.5))
        rgba(ctx, (0, 0, 0), 0.62); ctx.paint()
        for i, (k, txt, col) in enumerate((('A', Q['a'], ACC), ('B', Q['b'], (0.3, 0.7, 1.0)))):
            p = eback(prog(t, 0.1 + i * 0.15, 0.5 + i * 0.15)); x = W / 2 + (-440 if i == 0 else 440)
            ctx.save(); ctx.translate(x, 450); ctx.scale(max(p, 0.01), max(p, 0.01))
            rr(ctx, -320, -190, 640, 380, 36); rgba(ctx, (0.05, 0.06, 0.08), 0.92); ctx.fill_preserve(); rgba(ctx, col); ctx.set_line_width(6); ctx.stroke()
            ctx.restore()
            if p > 0.3:
                label(ctx, k, x, 340, 90, col, clamp(p)); label(ctx, txt, x, 500, 52 if len(txt) < 18 else 42, WHITE, clamp(p))
        if not Q.get('cta'):
            cd = d - 3.0
            if t > cd:
                left = 3 - (t - cd)
                ctx.arc(W / 2, 450, 70, -math.pi / 2, -math.pi / 2 + 2 * math.pi * (left / 3)); rgba(ctx, AMB); ctx.set_line_width(14); ctx.stroke()
                label(ctx, str(int(math.ceil(left))), W / 2, 450, 90, WHITE)
            else:
                label(ctx, "?", W / 2, 450, 120, AMB, eo(prog(t, 0.4, 0.8)))

    def T_fact(ctx, t, d, Q):
        rgba(ctx, (0, 0, 0.01)); ctx.paint(); starfield(ctx, t, 200, 0.6)
        planet(ctx, W - 200, H - 150, 260, L[Q['p']], t, 0.6)
        p = eback(prog(t, 0.05, 0.45))
        ctx.save(); ctx.translate(W / 2, 430); ctx.scale(max(p, 0.01), max(p, 0.01))
        rr(ctx, -680, -150, 1360, 300, 30); rgba(ctx, (0.06, 0.07, 0.09), 0.95); ctx.fill_preserve(); rgba(ctx, AMB, 0.9); ctx.set_line_width(5); ctx.stroke()
        ctx.restore()
        if p > 0.4:
            label(ctx, Q['big'], W / 2, 400, 110, AMB, clamp(p)); label(ctx, Q['sub'].upper(), W / 2, 520, 40, WHITE, eo(prog(t, 0.4, 0.8)), NORM)
        rr(ctx, W / 2 - 110, 210, 220, 54, 14); rgba(ctx, ACC); ctx.fill(); label(ctx, "FACT", W / 2, 237, 36, WHITE)

    def T_close(ctx, t, d, Q, snap=None):
        P = L[Q['p']]
        if 'bands' in P:
            T_gas(ctx, t * 0.5, d, dict(Q, shot='wide')); rgba(ctx, (0, 0, 0), 0.25); ctx.paint()
        else:
            ctx.save(); ctx.translate(W / 2, H / 2); ctx.scale(1.3, 1.3); ctx.translate(-W / 2, -H / 2 - 120)
            T_land(ctx, t * 0.3, d, dict(Q, shot='wide', pose='idle', helmet=0, emote=None, airship=0, hop=0)); ctx.restore()
            rgba(ctx, (0, 0, 0), 0.3); ctx.paint()
        z = 2.3 + 0.15 * clamp(t / d); sq = 0.0
        if snap is not None: z *= 1.25 - 0.25 * eo(clamp(snap / 0.25)); sq = 0.18 * max(0, 1 - snap / 0.2)
        dart = (1.0 if math.sin(t * 2.1) > 0.3 else -0.8, 0.15 * math.sin(t * 3))
        stickman(ctx, W / 2, 620 + 360 * z, z, 'idle', look=dart, fear=Q.get('fear', 0), mouth=Q.get('mouth', 'flat'),
                 blink=blink_at(t, 2.3), t=t, shadow=False, tilt=0.1 * math.sin(t * 1.4), squash=sq, emote=Q.get('emote'),
                 helmet=True, frost=Q.get('frost', 0), shiver=Q.get('shiver', 0), sweat=Q.get('sweat', 0))

    def hud(ctx, t, Q):
        if Q['tpl'] in ('title', 'travel', 'fact'): return
        P = L[Q['p']]
        rr(ctx, 40, 36, 470, 150, 20); rgba(ctx, (0, 0, 0), 0.55); ctx.fill()
        label(ctx, P['name'], 40 + 235, 36 + 38, 36, AMB)
        ctx.select_font_face(FONT, cairo.FONT_SLANT_NORMAL, NORM); ctx.set_font_size(24)
        for i, (k, v) in enumerate((("TEMP", P['temp']), ("GRAVITY", P['grav']))):
            ctx.move_to(64, 36 + 92 + i * 36); rgba(ctx, WHITE, 0.75); ctx.show_text(k)
            ctx.move_to(220, 36 + 92 + i * 36); rgba(ctx, ACC if 'F' in v and ('-' in v or int(''.join(c for c in v.split('°')[0] if c.isdigit()) or 0) > 150) and k == "TEMP" else WHITE); ctx.show_text(v)
        # 60-second survival timer per planet
        sec = max(0, 60 - int((Q['start'] + t - FIRST.get(Q['p'], 0)) * 0.9))
        rr(ctx, W - 300, 36, 260, 100, 20); rgba(ctx, (0, 0, 0), 0.55); ctx.fill_preserve(); rgba(ctx, ACC, 0.5 + 0.5 * math.sin(t * 6) if sec < 15 else 0.4); ctx.set_line_width(4); ctx.stroke()
        label(ctx, f"0:{sec:02d}", W - 170, 86, 66, ACC if sec < 15 else WHITE)

    FIRST = {}
    for dur, _, _, _, fn, _, _ in SCENES:
        Q = fn.__defaults__[0]
        FIRST.setdefault(Q['p'], Q['start'])

    install(dict(land=T_land, gas=T_gas, orbit=T_orbit, travel=T_travel, title=T_title, choice=T_choice, fact=T_fact, close=T_close), hud, TOTAL)
    run(SCENES, theme='noir', fades=False)
