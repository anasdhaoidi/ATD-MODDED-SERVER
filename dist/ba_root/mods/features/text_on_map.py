# Released under the ARR License. See LICENSE for details.

""" TODO need to set coordinates of text node , move timer values to settings.json """

import random

import _babase
import setting
from stats import mystats

import babase
import bascenev1 as bs

setti = setting.get_settings_data()


class textonmap:

    def __init__(self):
        data = setti['textonmap']
        left = data['bottom left watermark']
        top = data['top watermark']
        nextMap = ""
        try:
            nextMap = bs.get_foreground_host_session().get_next_game_description().evaluate()
        except:
            pass
        try:
            top = top.replace("@IP", _babase.our_ip).replace("@PORT",
                                                             str(_babase.our_port))
        except:
            pass
        self.index = 0
        self.highlights = data['center highlights']["msg"]
        self.left_watermark(left)
        self.top_message(top)
        self.nextGame(nextMap)
        self.restart_msg()
        if hasattr(_babase, "season_ends_in_days"):
            if _babase.season_ends_in_days < 9:
                self.season_reset(_babase.season_ends_in_days)
        if setti["leaderboard"]["enable"]:
            self.leaderBoard()
        self.timer = bs.timer(8, babase.CallPartial(self.highlights_), repeat=True)

    def highlights_(self):
        if setti["textonmap"]['center highlights']["randomColor"]:
            color = ((0 + random.random() * 1.0), (0 + random.random() * 1.0),
                     (0 + random.random() * 1.0))
        else:
            color = tuple(setti["textonmap"]["center highlights"]["color"])
        node = bs.newnode('text',
                          attrs={
                              'text': self.highlights[self.index],
                              'flatness': 1.0,
                              'h_align': 'center',
                              'v_attach': 'bottom',
                              'scale': 1,
                              'position': (0, 138),
                              'color': color
                          })
        self.delt = bs.timer(7, node.delete)
        self.index = int((self.index + 1) % len(self.highlights))

    def left_watermark(self, text):
        WAVE = [
            (2.5, 0.0, 0.0),
            (2.5, 1.2, 0.0),
            (2.5, 2.5, 0.0),
            (0.0, 2.5, 0.0),
            (0.0, 2.0, 2.5),
            (0.0, 0.0, 2.5),
            (1.5, 0.0, 2.5),
            (2.5, 0.0, 0.0),
        ]
        N          = len(WAVE)
        WP         = 3.0
        WD         = 0.08
        DT         = 0.05
        SLIDE_FROM = -300
        SLIDE_DUR  = 0.45
        STAGGER    = 0.15
        X_FINAL    = 95
        Y_BASE     = -34
        LINE_H     = 28
        CHAR_W     = 13
        SCALE      = 0.2

        lines = text.split('\n')
        char_nodes = []
        global_idx = 0

        for li, line in enumerate(lines):
            y          = Y_BASE + li * LINE_H
            delay      = STAGGER * li
            line_nodes = []

            for ci, ch in enumerate(line):
                x_final = X_FINAL + ci * CHAR_W
                nd = bs.newnode('text', attrs={
                    'text':     ch,
                    'flatness': 1.0,
                    'h_align':  'left',
                    'v_attach': 'bottom',
                    'h_attach': 'left',
                    'scale':    SCALE,
                    'position': (SLIDE_FROM + ci * CHAR_W, y),
                    'big':      True,
                    'color':    (2.5, 0.0, 0.0),
                    'opacity':  0.0,
                })
                line_nodes.append((nd, x_final, y))
                char_nodes.append((nd, global_idx))
                global_idx += 1

            def _slide_line(nodes=line_nodes, delay=delay):
                def _go():
                    for nd, x_final, y in nodes:
                        try:
                            bs.animate(nd, 'opacity', {0.0: 0.0, 0.15: 1.0})
                            bs.animate_array(nd, 'position', 2, {
                                0.0:       (SLIDE_FROM, y),
                                SLIDE_DUR: (x_final, y),
                            })
                        except Exception:
                            pass
                bs.apptimer(delay, _go)
            _slide_line()

        ts = {'v': 0.0}

        def _tick(nodes=char_nodes, ts=ts, rb=WAVE, nc=N, wp=WP, wd=WD, dt=DT):
            try:
                ts['v'] = (ts['v'] + dt) % wp
                for nd, idx in nodes:
                    if not nd.exists():
                        return
                    local_t = (ts['v'] + idx * wd) % wp
                    i0 = int(local_t / wp * nc) % nc
                    i1 = (i0 + 1) % nc
                    frac = (local_t / wp * nc) % 1.0
                    c0, c1 = rb[i0], rb[i1]
                    nd.color = (
                        c0[0] + (c1[0] - c0[0]) * frac,
                        c0[1] + (c1[1] - c0[1]) * frac,
                        c0[2] + (c1[2] - c0[2]) * frac,
                    )
            except Exception:
                pass

        self._lw_timer = bs.Timer(DT, babase.CallStrict(_tick), repeat=True)

    def nextGame(self, text):
        node = bs.newnode('text',
                          attrs={
                              'text': "Next : " + text,
                              'flatness': 1.0,
                              'h_align': 'right',
                              'v_attach': 'bottom',
                              'h_attach': 'right',
                              'scale': 0.7,
                              'position': (-25, 16),
                              'color': (0.5, 0.5, 0.5)
                          })

    def season_reset(self, text):
        node = bs.newnode('text',
                          attrs={
                              'text': "Season ends in: " + str(text) + " days",
                              'flatness': 1.0,
                              'h_align': 'right',
                              'v_attach': 'bottom',
                              'h_attach': 'right',
                              'scale': 0.5,
                              'position': (-25, 34),
                              'color': (0.6, 0.5, 0.7)
                          })

    def restart_msg(self):
        if getattr(_babase, 'restart_scheduled', False):
            activity = bs.get_foreground_host_activity()
            if activity:
                 activity.restart_msg = bs.newnode(
                'text',
                attrs={
                    'text': "Server going to restart after this series.",
                    'flatness': 1.0,
                    'h_align': 'right',
                    'v_attach': 'bottom',
                    'h_attach': 'right',
                    'scale': 0.5,
                    'position': (-25, 54),
                    'color': (1, 0.5, 0.7)
                })

    def top_message(self, text):
        FINAL_Y    = 515
        SLIDE_FROM = 350    # يدخل من الأسفل
        SLIDE_DUR  = 0.5

        import math
        RAINBOW = [
            (2.5, 0.0, 0.0),
            (2.5, 1.2, 0.0),
            (2.5, 2.5, 0.0),
            (0.0, 2.5, 0.0),
            (0.0, 2.0, 2.5),
            (0.0, 0.0, 2.5),
            (1.5, 0.0, 2.5),
        ]
        N_COLORS    = len(RAINBOW)
        WAVE_PERIOD = 3.0
        WAVE_DELAY  = 0.12
        TICK_MS     = 50
        CHAR_SCALE  = 0.5
        CHAR_SP     = 32   # المسافة بين الحروف

        n_chars = len(text)
        center  = (n_chars - 1) * 0.5
        self._top_char_nodes = []

        for i, ch in enumerate(text):
            cx = CHAR_SP * (i - center)
            nd = bs.newnode('text', attrs={
                'text':     ch,
                'flatness': 1.0,
                'h_align':  'center',
                'v_attach': 'bottom',
                'h_attach': 'center',
                'scale':    CHAR_SCALE,
                'big':      True,
                'position': (cx, SLIDE_FROM),
                'color':    (2.5, 0.0, 0.0),
                'opacity':  0.0,
            })
            self._top_char_nodes.append(nd)
            def _reveal(nd=nd, cx=cx):
                try:
                    bs.animate(nd, 'opacity', {0.0: 0.0, 0.2: 1.0})
                    bs.animate_array(nd, 'position', 2, {
                        0.0:       (cx, SLIDE_FROM),
                        SLIDE_DUR: (cx, FINAL_Y),
                    })
                except Exception:
                    pass
            bs.apptimer(i * 0.03, _reveal)

        t = {'v': 0.0}
        def _tick(nodes=self._top_char_nodes, t=t):
            try:
                t['v'] = (t['v'] + TICK_MS / 1000.0) % WAVE_PERIOD
                for idx, nd in enumerate(nodes):
                    if not nd.exists():
                        continue
                    local_t = (t['v'] + idx * WAVE_DELAY) % WAVE_PERIOD
                    phase   = (local_t / WAVE_PERIOD) * N_COLORS
                    ci      = int(phase) % N_COLORS
                    ni      = (ci + 1) % N_COLORS
                    u       = phase - int(phase)
                    c1, c2  = RAINBOW[ci], RAINBOW[ni]
                    nd.color = (
                        c1[0] + (c2[0] - c1[0]) * u,
                        c1[1] + (c2[1] - c1[1]) * u,
                        c1[2] + (c2[2] - c1[2]) * u,
                    )
            except Exception:
                pass
        self._top_color_timer = bs.Timer(
            TICK_MS / 1000.0, babase.CallStrict(_tick), repeat=True)

        STAR_FINAL_X = 40
        STAR_FROM    = -150   # تدخل من اليسار
        self.ss1 = bs.newnode('image', attrs={
            'texture':  bs.gettexture('star'),
            'scale':    (100, 100),
            'position': (STAR_FROM, 115),
            'attach':   'bottomLeft',
            'opacity':  0.0,
            'color':    (1, 1, 1)
        })
        bs.animate(self.ss1, 'opacity', {0.0: 0.0, 0.2: 1.0})
        bs.animate_array(self.ss1, 'position', 2, {
            0.0:       (STAR_FROM, 115),
            SLIDE_DUR: (STAR_FINAL_X, 115),
        })
        bs.animate(self.ss1, 'rotate', {0: 0.0, 6.0: 360.0}, loop=True)
        bs.animate_array(self.ss1, 'color', 3,
                         {0: (1,1,1), 0.5: (1,0,0), 1.0: (0,0,1)}, loop=True)

    def leaderBoard(self):
        if len(mystats.top3Name) > 2:
            if setti["leaderboard"]["barsBehindName"]:
                self.ss0 = bs.newnode('image', attrs={'scale': (327, 300),
                                                      'texture': bs.gettexture(
                                                          'windowHSmallVSmall'),
                                                      'position': (-72, -165),
                                                      'attach': 'topRight',
                                                      'opacity': 1,
                                                      'color': (0.5, 0.5, 0.5)})
                self.ss1 = bs.newnode('image', attrs={'scale': (236, 34),
                                                      'texture': bs.gettexture(
                                                          'frameInset'),
                                                      'position': (-79, -95),
                                                      'attach': 'topRight',
                                                      'opacity': 1,
                                                      'color': (0, 0, 0)})
                self.ss2 = bs.newnode('image', attrs={'scale': (217, 49),
                                                      'texture': bs.gettexture(
                                                          'clayStroke'),
                                                      'position': (-79, -95),
                                                      'attach': 'topRight',
                                                      'opacity': 1,
                                                      'color': (1, 0, 0)})
                bs.animate_array(self.ss2,'color',3,{0:(0,0,2),0.5:(0,2,0),1.0:(2,0,0),1.5:(2,2,0),2.0:(2,0,2),2.5:(0,1,6),3.0:(1,2,0)},loop=True)
            self.ss2a = bs.newnode('text', attrs={
                'text': "LEADERBOARD",
                'flatness': 1.0, 'h_align': 'left', 'h_attach': 'right',
                'v_attach': 'top', 'v_align': 'center', 'position': (-180, -95),
                'scale': 0.7, 'color': (1, 1, 0)})
            bs.animate_array(self.ss2a,'color',3,{0:(0,0,2),0.5:(0,2,0),1.0:(2,0,0),1.5:(2,2,0),2.0:(2,0,2),2.5:(0,1,6),3.0:(1,2,0)},loop=True)
            self.ss1a = bs.newnode('text', attrs={
                'text': "" + mystats.top3Name[0][:10],
                'flatness': 1.0, 'h_align': 'left', 'h_attach': 'right',
                'v_attach': 'top', 'v_align': 'center',
                'position': (-180, -130), 'scale': 0.7,
                'color': (1, 1, 1)})

            self.ss1a = bs.newnode('text', attrs={
                'text': "" + mystats.top3Name[1][:10],
                'flatness': 1.0, 'h_align': 'left', 'h_attach': 'right',
                'v_attach': 'top', 'v_align': 'center',
                'position': (-180, -165), 'scale': 0.7,
                'color': (1, 1, 1)})

            self.ss1a = bs.newnode('text', attrs={
                'text': "" + mystats.top3Name[2][:10],
                'flatness': 1.0, 'h_align': 'left', 'h_attach': 'right',
                'v_attach': 'top', 'v_align': 'center',
                'position': (-180, -200), 'scale': 0.7,
                'color': (1, 1, 1)})
