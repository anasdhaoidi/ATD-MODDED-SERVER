import setting
from playersdata import pdata
from stats import mystats

import babase
import bascenev1 as bs

sett = setting.get_settings_data()


# يحفظ الـ timers لكل لاعب لمنع GC
_tag_timers: dict = {}


def addtag(node, player):
    session_player = player.sessionplayer
    account_id = session_player.get_account_id()
    customtag_ = pdata.get_custom()
    customtag = customtag_['customtag']
    roles = pdata.get_roles()
    p_roles = pdata.get_player_roles(account_id)
    tag = None
    col = (0.5, 0.5, 1)
    if account_id in customtag:
        tag = customtag[account_id]
    elif p_roles != []:
        for role in roles:
            if role in p_roles:
                tag = roles[role]['tag']
                col = (
                    0.7, 0.7, 0.7) if 'tagcolor' not in roles[role] else \
                    roles[role]['tagcolor']
                break
    if tag:
        Tag(node, tag, col)


def addrank(node, player):
    session_player = player.sessionplayer
    account_id = session_player.get_account_id()
    rank = mystats.getRank(account_id)

    if rank:
        Rank(node, rank)


def addhp(node, spaz):
    def showHP():
        hp = spaz.hitpoints
        if spaz.node.exists():
            HitPoint(owner=node, prefix=str(int(hp)),
                     position=(0, 1.75, 0), shad=1.4)
        else:
            spaz.hptimer = None
    spaz.hptimer = bs.Timer(2, babase.CallPartial(
        showHP), repeat=True)


class Tag(object):
    def __init__(self, owner=None, tag="somthing", col=(1, 1, 1)):
        self.node = owner

        mnode = bs.newnode('math',
                           owner=self.node,
                           attrs={
                               'input1': (0, 1.5, 0),
                               'operation': 'add'
                           })
        self.node.connectattr('torso_position', mnode, 'input2')
        if '\\' in tag:
            tag = tag.replace('\\d', ('\ue048'))
            tag = tag.replace('\\c', ('\ue043'))
            tag = tag.replace('\\h', ('\ue049'))
            tag = tag.replace('\\s', ('\ue046'))
            tag = tag.replace('\\n', ('\ue04b'))
            tag = tag.replace('\\f', ('\ue04f'))
            tag = tag.replace('\\g', ('\ue027'))
            tag = tag.replace('\\i', ('\ue03a'))
            tag = tag.replace('\\m', ('\ue04d'))
            tag = tag.replace('\\t', ('\ue01f'))
            tag = tag.replace('\\bs', ('\ue01e'))
            tag = tag.replace('\\j', ('\ue010'))
            tag = tag.replace('\\e', ('\ue045'))
            tag = tag.replace('\\l', ('\ue047'))
            tag = tag.replace('\\a', ('\ue020'))
            tag = tag.replace('\\b', ('\ue00c'))

        if sett["enableTagAnimation"]:
            # موجة لونية per-character
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
            N   = len(WAVE)
            WP  = 3.0
            WD  = 0.18
            DT  = 0.016

            char_nodes = []
            CHAR_SP = 0.18  # المسافة بين الحروف في الـ in_world

            for i, ch in enumerate(tag):
                nd = bs.newnode('text',
                                owner=self.node,
                                attrs={
                                    'text':     ch,
                                    'in_world': True,
                                    'shadow':   1.0,
                                    'flatness': 1.0,
                                    'color':    (2.5, 0.0, 0.0),
                                    'scale':    0.01,
                                    'h_align':  'center',
                                })
                # كل حرف له math node خاص لتحريكه أفقياً
                base_x = CHAR_SP * (i - (len(tag)-1)*0.5)
                m_ch = bs.newnode('math',
                                  owner=self.node,
                                  attrs={
                                      'input1': (base_x, 0, 0),
                                      'operation': 'add',
                                  })
                mnode.connectattr('output', m_ch, 'input2')
                m_ch.connectattr('output', nd, 'position')
                char_nodes.append((nd, m_ch, base_x, i))

            ts = {'v': 0.0}


            import math
            WAVE_AMP  = 0.04   # ارتفاع الموجة
            WAVE_SPD  = 2.5    # سرعة الموجة
            WAVE_SEP  = 0.4    # تأخير بين الحروف

            def _tick(nodes=char_nodes, ts=ts, rb=WAVE, nc=N, wp=WP, wd=WD, dt=DT):
                try:
                    ts['v'] = (ts['v'] + dt) % wp
                    for nd, m_ch, base_x, idx in nodes:
                        if not nd.exists():
                            return
                        # موجة لونية
                        local_t = (ts['v'] + idx * wd) % wp
                        i0   = int(local_t / wp * nc) % nc
                        i1   = (i0 + 1) % nc
                        frac = (local_t / wp * nc) % 1.0
                        c0, c1 = rb[i0], rb[i1]
                        nd.color = (
                            c0[0] + (c1[0] - c0[0]) * frac,
                            c0[1] + (c1[1] - c0[1]) * frac,
                            c0[2] + (c1[2] - c0[2]) * frac,
                        )
                        # موجة مائية — تحريك y
                        wave_y = WAVE_AMP * math.sin(
                            ts['v'] * WAVE_SPD - idx * WAVE_SEP)
                        m_ch.input1 = (base_x, wave_y, 0)
                except Exception:
                    pass
            # نحفظ الـ timer في dict عالمي مع الـ node كـ key
            _tag_timers[id(self.node)] = bs.Timer(DT, babase.CallStrict(_tick), repeat=True)

        else:
            # بدون animation — نود واحد بالـ color الأصلي
            self.tag_text = bs.newnode('text',
                                       owner=self.node,
                                       attrs={
                                           'text':     tag,
                                           'in_world': True,
                                           'shadow':   1.0,
                                           'flatness': 1.0,
                                           'color':    tuple(col),
                                           'scale':    0.01,
                                           'h_align':  'center'
                                       })
            mnode.connectattr('output', self.tag_text, 'position')


class Rank(object):
    def __init__(self, owner=None, rank=99):
        self.node = owner
        mnode = bs.newnode('math',
                           owner=self.node,
                           attrs={
                               'input1': (0, 1.2, 0),
                               'operation': 'add'
                           })
        self.node.connectattr('torso_position', mnode, 'input2')
        if (rank == 1):
            rank = '' + str(rank) + ''
        elif (rank == 2):
            rank = '' + str(rank) + ''
        elif (rank == 3):
            rank = '' + str(rank) + ''
        else:
            rank = "" + str(rank) + ""

        self.rank_text = bs.newnode('text',
                                    owner=self.node,
                                    attrs={
                                        'text': rank,
                                        'in_world': True,
                                        'shadow': 1.0,
                                        'flatness': 1.0,
                                        'color': (1, 1, 1),
                                        'scale': 0.01,
                                        'h_align': 'center'
                                    })
        mnode.connectattr('output', self.rank_text, 'position')

class HitPoint(object):
    def __init__(self, position=(0, 1.5, 0), owner=None, prefix='0', shad=1.2):
        self.position = position
        self.node = owner
        m = bs.newnode('math', owner=self.node, attrs={
            'input1': self.position, 'operation': 'add'})
        self.node.connectattr('torso_position', m, 'input2')
        prefix = int(prefix) / 10
        preFix = u"\ue047" + str(prefix) + u"\ue047"
        self._Text = bs.newnode('text',
                                owner=self.node,
                                attrs={
                                    'text': preFix,
                                    'in_world': True,
                                    'shadow': shad,
                                    'flatness': 1.0,
                                    'color': (1, 1, 1) if int(
                                        prefix) >= 20 else (1.0, 0.2, 0.2),
                                    'scale': 0.01,
                                    'h_align': 'center'})
        m.connectattr('output', self._Text, 'position')

        def a():
            self._Text.delete()
            m.delete()

        self.timer = bs.Timer(2, babase.CallPartial(a))
