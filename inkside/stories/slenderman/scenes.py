"""Slender Man - scenes synced to the words being spoken."""
import json
from engine import *
from lib4 import *
from engine import TW as T
from words import wt, parts

TOTAL = parts[-1][-1][2] + 1.8
def L(i): return parts[i][0][1]          # start of line i

M, A, PY = dict(hair="bob"), dict(hair="pony"), dict(hair="long")

def p(x, y, s, **kw): return place(fig(**kw), x, y, s)
def txt(t, x, y, size=90, c=K_): return [T(t, x, y, size, "marker", c)]
def woods(xs=(140, 1780), y=1040, s=1.25, seeds=(1, 2)):
    out = []
    for x, sd in zip(xs, seeds): out += place(tree(1.0, sd), x, y, s)
    return out + ground(y)

def build():
    sc = []
    # 0  Two girls. One knife. And a man who doesn't exist.
    sc.append(Scene(L(0), [
        Beat(wt(0, "two girls"), p(330, 1040, .6, expr="sinister", **M) + p(560, 1040, .6, expr="sinister", **A)),
        Beat(wt(0, "knife"), place(knife(), 1000, 420, 1.2)),
        Beat(wt(0, "a man"), place(slender(), 1600, 1060, .92)),
        Beat(wt(0, "exist"), place(qmark(150), 1760, 340)),
    ]))
    # 1-2  a picture made as a joke ... a little girl / forum / scariest fake photos
    sc.append(Scene(L(1), [
        Beat(wt(1, "picture"), place(photo(), 330, 520, 1.0)),
        Beat(wt(1, "joke"), place(laugh(), 330, 830, .8)),
        Beat(wt(1, "little girl"), p(820, 1040, .5, expr="happy", **PY)),
        Beat(wt(2, "forum"), place(monitor([], "FORUM"), 1450, 560, 1.0)),
        Beat(wt(2, "scariest"), place(ghost(), 1450, 440, .8) + place(trophy(), 1450, 980, .7)),
    ]))
    # 3-6  the two pictures, kids in the park, something behind them, the name
    sc.append(Scene(L(3), [
        Beat(wt(3, "pictures"), frame_pic(330, 300, 1260, 660, hatch=False)),
        Beat(wt(3, "kids"), p(560, 940, .38, expr="happy", hair="long") + p(760, 940, .36, expr="happy", hair="short")
                            + p(1250, 940, .38, expr="happy", hair="pony")),
        Beat(wt(3, "park"), place(tree(1.0, 21), 1490, 950, .6)),
        Beat(wt(4, "behind"), place(qmark(110), 1110, 470)),
        Beat(wt(5, "tall"), place(slender(), 960, 940, .55)),
        Beat(wt(6, "slender man"), txt("THE SLENDER MAN", 960, 190, 110, RED)),
    ]))
    # 7-8  the internet doesn't do jokes / everyone was writing / videos / games / darker
    sc.append(Scene(L(7), [
        Beat(wt(7, "joke"), place(laugh(), 330, 440, .9)),
        Beat(wt(7, "internet"), place(globe(), 330, 840, .9)),
        Beat(wt(8, "writing"), place(paper(), 760, 330)),
        Beat(wt(8, "videos"), place(play_icon(), 1200, 330, 1.1)),
        Beat(wt(8, "games"), place(gamepad(), 1620, 330)),
        Beat(wt(8, "darker"), place(slender(), 1200, 1060, .55) + txt("darker...", 1550, 900, 70, RED)),
    ]))
    # 9-11  the rules
    sc.append(Scene(L(9), [
        Beat(wt(9, "rules"), txt("THE RULES", 960, 120, 100, RED)),
        Beat(wt(10, "woods"), place(tree(1.0, 3), 1400, 1040, 1.1) + place(slender(), 1660, 1040, .78)),
        Beat(wt(10, "watches"), place(eye(), 620, 360, .8)),
        Beat(wt(10, "children"), p(480, 1040, .4, expr="scared") + p(680, 1040, .4, expr="scared", hair="long")),
        Beat(wt(11, "family"), place(house(), 1020, 1000, .6)),
        Beat(wt(11, "serve him"), txt("SERVE HIM", 900, 640, 84, RED)),
    ]))
    # 12-13  most people closed the laptop... two girls didn't
    sc.append(Scene(L(12), [
        Beat(wt(12, "most people"), p(300, 1040, .45, expr="happy") + p(520, 1040, .45, expr="happy", hair="short")
                                    + p(740, 1040, .45, expr="happy", hair="long")),
        Beat(wt(12, "laptop"), place(monitor(), 520, 400, .7)),
        Beat(wt(13, "two girls"), p(1300, 1040, .6, expr="sinister", **M) + p(1560, 1040, .6, expr="sinister", **A)
                                  + txt("DIDN'T.", 1430, 300, 110, RED)),
    ]))
    # 14-15  Morgan and Anissa, twelve, sure he was real
    sc.append(Scene(L(14), [
        Beat(wt(14, "morgan"), p(380, 1040, .62, expr="sinister", **M) + txt("MORGAN", 380, 340, 54)),
        Beat(wt(14, "anissa"), p(720, 1040, .62, expr="sinister", **A) + txt("ANISSA", 720, 340, 54)),
        Beat(wt(14, "twelve"), txt("12", 550, 200, 110, RED)),
        Beat(wt(14, "real"), place(slender(), 1400, 1060, .9)),
        Beat(wt(15, "watching"), place(eye(), 1700, 300, .5)),
        Beat(wt(15, "families"), place(house(), 1720, 1000, .45)),
    ]))
    # 16-17  the plan, for months, it had a name: Payton
    sc.append(Scene(L(16), [
        Beat(wt(16, "plan"), place(notebook("PLAN"), 560, 420, 1.1)),
        Beat(wt(16, "months"), place(calendar("MONTHS", "?", ""), 560, 900, .55)),
        Beat(wt(17, "name"), txt("TARGET:", 1350, 200, 80)),
        Beat(wt(17, "payton"), p(1350, 1040, .62, expr="happy", **PY) + place(target_ring(), 1350, 560, 1.0)),
    ]))
    # 18-19  birthday sleepover, skates, froyo, they were waiting
    sc.append(Scene(L(18), [
        Beat(wt(18, "birthday"), place(cake(), 330, 420, .8)),
        Beat(wt(18, "skates"), place(skate(), 330, 920, .9)),
        Beat(wt(18, "yogurt"), place(froyo(), 760, 920, .8)),
        Beat(wt(18, "night"), moon(760, 300, 80)),
        Beat(wt(19, "payton"), p(1300, 1040, .55, expr="happy", **PY)),
        Beat(wt(19, "waiting"), p(1560, 1040, .55, expr="sinister", **M) + p(1780, 1040, .55, expr="sinister", **A)),
    ]))
    # 20-22  to the woods, hide-and-seek, lie down, cover with leaves
    sc.append(Scene(L(20), [
        Beat(wt(20, "woods"), place(tree(1.0, 7), 200, 1040, 1.15) + place(tree(1.0, 8), 1760, 1040, 1.15)),
        Beat(wt(21, "hide"), p(760, 1040, .45, expr="happy", **M) + p(960, 1040, .45, expr="happy", **PY)
                             + p(1160, 1040, .45, expr="happy", **A) + txt("1, 2, 3...", 960, 450, 70)),
        Beat(wt(21, "nobody"), bubble("\"Nobody will find you...\"", 1250, 250, 540, 130, 50)),
    ]))
    # 23-24  under the leaves, the knife, nineteen
    sc.append(Scene(L(23), [
        Beat(wt(23, "lay there"), place(lying_fig(), 900, 1050, 1.0)),
        Beat(wt(23, "leaves"), place(leaves(7, 420), 700, 1030, 1.0)),
        Beat(wt(23, "morgan"), p(1500, 1040, .6, expr="sinister", **M)),
        Beat(wt(23, "knife"), place(knife(), 1500, 300, .9)),
        Beat(wt(24, "nineteen"), txt("19", 520, 450, 230, RED)),
    ]))
    # 25-26  walked away, deeper into the woods, the mansion
    sc.append(Scene(L(25), [
        Beat(wt(25, "walked"), p(230, 1040, .45, expr="blank", pose="walk", **M) + p(400, 1040, .45, expr="blank", pose="walk", **A)),
        Beat(wt(25, "woods"), place(tree(1.0, 11), 720, 1040, .9)),
        Beat(wt(26, "mansion"), place(mansion(), 1260, 1000, .8)),
        Beat(wt(26, "accept"), place(slender(), 1730, 1040, .5)),
    ]))
    # 27-28  she wasn't dead / the trees / the cyclist
    sc.append(Scene(L(27), [
        Beat(L(27), txt("BUT PAYTON WASN'T DEAD", 1150, 140, 84, RED)),
        Beat(wt(28, "trees"), place(tree(1.0, 13), 260, 900, 1.15)),
        Beat(wt(28, "dragged"), p(700, 900, .6, expr="scared", pose="up", **PY)),
        Beat(wt(28, "cyclist"), road(900, 1000, 1920) + place(bike(), 1500, 830, 1.0) + p(1480, 760, .5, hair="short", expr="scared")),
    ]))
    # 29-32  less than a millimeter, surgery, "did they get them?"
    sc.append(Scene(L(29), [
        Beat(wt(29, "heart"), place(anatomical_heart(), 560, 560, 1.2)),
        Beat(wt(29, "millimeter"), txt("< 1 mm", 1300, 400, 170, RED)),
        Beat(wt(31, "surgery"), place(clock(""), 1300, 700, .6)),
        Beat(L(32), bubble("\"Did they get them?\"", 1100, 950, 820, 160, 70)),
    ]))
    # 33-34  police, the highway, psychiatric hospital
    sc.append(Scene(L(33), [
        Beat(wt(33, "police"), place(police_car(), 420, 640, 1.1)),
        Beat(wt(33, "walking"), p(880, 680, .34, expr="blank", pose="walk", **M) + p(1010, 680, .34, expr="blank", pose="walk", **A)),
        Beat(wt(33, "find him"), place(slender(), 1180, 680, .3)),
        Beat(wt(33, "highway"), news("Girls, 12, stab friend 'for Slender Man'", 1540, 380, 480, -3, "Victim found alive by a cyclist", seed=2)),
        Beat(wt(34, "psychiatric"), place(hospital("none"), 1480, 1030, .55) + txt("PSYCHIATRIC HOSPITAL", 1480, 725, 44)),
    ]))
    # 35  let out ... one of them ran away
    sc.append(Scene(L(35), [
        Beat(wt(35, "years later"), place(clock(""), 330, 380, .7)),
        Beat(wt(35, "let out"), place(door_open(), 800, 1000, .9)),
        Beat(wt(35, "ran away"), p(1400, 1040, .6, expr="blank", pose="walk", **M) + txt("SHE RAN", 1400, 300, 100, RED)),
    ]))
    # 36-37  truck stop, "something really bad", Google her
    sc.append(Scene(L(36), [
        Beat(wt(36, "sleeping"), place(lying_fig(), 1250, 1040, .6) + moon(1780, 160)),
        Beat(wt(36, "truck stop"), place(truck_stop(), 520, 1010, .85)),
        Beat(wt(36, "really bad"), news("Slender Man attacker found sleeping at truck stop", 1380, 380, 560, 3, seed=4)),
        Beat(wt(37, "google"), place(search_bar("Morgan Geyser"), 1380, 760, .55)),
    ]))
    # 38  Payton survived, medicine
    sc.append(Scene(L(38), [
        Beat(wt(38, "survived"), txt("SHE SURVIVED", 1300, 160, 100, "#2E7D4F")),
        Beat(wt(38, "today"), p(600, 1050, .82, expr="happy", **PY)),
        Beat(wt(38, "medicine"), place(big_cross(), 1300, 480, 1.3)),
        Beat(wt(38, "doctors"), place(heart_shape(), 1300, 830, .8)),
    ]))
    # 39-40  never real / real enough to kill for
    sc.append(Scene(L(39), [
        Beat(wt(39, "never real"), place(slender(), 360, 1040, .8) + place(cross(220), 360, 600)),
        Beat(wt(39, "afternoon"), place(clock(""), 900, 380, .6)),
        Beat(wt(39, "joke"), place(laugh(), 900, 820, .7)),
        Beat(wt(40, "two girls"), p(1350, 1050, .5, expr="sinister", **M) + p(1580, 1050, .5, expr="sinister", **A)),
        Beat(wt(40, "kill"), txt("REAL ENOUGH", 1460, 280, 80, RED) + txt("TO KILL FOR", 1460, 400, 80, RED)),
    ]))
    # 41-42  who's to blame / subscribe
    sc.append(Scene(L(41), [
        Beat(wt(41, "blame"), place(comment_box(["The internet", "The parents", "...him?"]), 960, 160, 1.1)),
        Beat(wt(42, "subscribe"), txt("INKSIDE STORIES", 960, 840, 100) + place(subscribe_btn(), 960, 980, .8)),
    ]))
    schedule(sc, TOTAL)
    return sc


# ---------------- sound ----------------
MUSIC = "music_2"          # quiet atmosphere bed under the whole video
AMBIENCE = "drone_1"
def CUES():
    """(time, sound, gain, max seconds). Few and meaningful; no scream in this one."""
    return [
        (wt(0, "exist") + 0.3, "shadow_1", .45, 4),
        (wt(5, "tall"), "riser_2", .35, 5),
        (wt(6, "slender man"), "hit_1", .55, 4),
        (wt(10, "woods"), "wind_2", .25, 8),
        (wt(11, "serve him"), "whisper_1", .5, 3),
        (wt(19, "waiting"), "heartbeat_2", .35, 6),
        (wt(20, "woods"), "footsteps_2", .4, 5),
        (wt(21, "nobody"), "whisper_3", .45, 2),
        (wt(24, "nineteen"), "hit_2", .6, 3),
        (wt(25, "walked"), "footsteps_1", .3, 6),
        (wt(26, "mansion"), "creak_1", .4, 3),
        (wt(28, "cyclist"), "breath_2", .4, 3),
        (wt(29, "millimeter"), "heartbeat_1", .4, 6),
        (wt(33, "police"), "siren_1", .3, 5),
        (wt(35, "ran away"), "running_2", .45, 3),
        (wt(40, "kill"), "hit_3", .5, 5),
    ]
