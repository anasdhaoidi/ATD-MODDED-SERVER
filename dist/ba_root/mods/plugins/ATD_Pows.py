# ba_meta require api 9
# name: ATD_Powerups
# ATD POWERUPS — by ATD
from __future__ import annotations

# ╔══════════════════════════════════════════════════════════════╗
# ║  الإعدادات تُقرأ من setting.json  →  قسم ATD_Pows          ║
# ╚══════════════════════════════════════════════════════════════╝
import setting as _setting
_cfg = _setting.get_settings_data().get('ATD_Pows', {})

SHIELD_ON_POWERUPS = _cfg.get('SHIELD_ON_POWERUPS', False)
NAME_ON_POWERUPS   = _cfg.get('NAME_ON_POWERUPS',   True)
SPARK_WHEN_SPAWN   = _cfg.get('SPARK_WHEN_SPAWN',   True)
POWERUP_TIME_BAR   = _cfg.get('POWERUP_TIME_BAR',   True)
SHIELD_ON_BOMBS    = _cfg.get('SHIELD_ON_BOMBS',    False)
NAME_ON_BOMBS      = _cfg.get('NAME_ON_BOMBS',      True)

import random
import math

import babase
import bascenev1 as bs
from bascenev1lib.actor import powerupbox as pupbox
from bascenev1lib.actor.bomb import Bomb
from bascenev1lib.gameutils import SharedObjects
from bascenev1lib.actor.powerupbox import PowerupBoxFactory
from bascenev1lib.actor.popuptext import PopupText
from bascenev1lib.actor.spaz import Spaz, POWERUP_WEAR_OFF_TIME
from bascenev1lib.gameutils import SharedObjects

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any


# ══════════════════════════════════════════════════════════════
#  توزيع البور-أبات
# ══════════════════════════════════════════════════════════════

def powerup_dist() -> tuple:
    return (
        ('triple_bombs',  3),
        ('ice_bombs',     3),
        ('punch',         0),
        ('impact_bombs',  3),
        ('land_mines',    2),
        ('sticky_bombs',  3),
        ('shield',        0),
        ('health',        1),
        ('curse',         1),
        ('fake',          3),
        ('headache',      2),
        ('blackHole',     1),
        ('antiGrav',      2),
        ('sloMo',         1),
        ('troll',         1),
        ('speedBoots',    2),
        ('mag',           2),
        ('invisible',     1),
        ('character',     2),
        ('ice_man',       2),
        ('portal',        2),
        ('ice_cube',     2),
        ('tele_bomb',     2),
        ('stun_bombs',    2),
        ('smb_bomb',      2),
        ('nitrogen_bomb', 2),
        ('sticky_ice',    2),
        ('jump_fly',      2),
    )


# ══════════════════════════════════════════════════════════════
#  NewPowerupBoxFactory
# ══════════════════════════════════════════════════════════════

class NewPowerupBoxFactory(pupbox.PowerupBoxFactory):

    def __init__(self) -> None:
        super().__init__()
        self.tex_headache  = bs.gettexture('achievementOnslaught')
        self.tex_blackhole = bs.gettexture('circleOutlineNoAlpha')
        self.tex_antigrav  = bs.gettexture('achievementFootballShutout')
        self.tex_slomo     = bs.gettexture('achievementFlawlessVictory')
        self.tex_troll     = bs.gettexture('achievementOffYouGo')
        self.tex_speedboots  = bs.gettexture('powerupSpeed')
        self.tex_mag         = bs.gettexture('tickets')
        self.tex_invisible   = bs.gettexture('black')
        self.tex_character   = bs.gettexture('wizardIcon')
        self.tex_ice_man     = bs.gettexture('ouyaUButton')
        self.tex_portal    = bs.gettexture('ouyaOButton')
        self.tex_jump_fly    = bs.gettexture('achievementOffYouGo')
        self.tex_sticky_ice = bs.gettexture('eggTex2')
        self.tex_ice_cube   = bs.gettexture('bombColorIce')
        self.tex_tele_bomb   = bs.gettexture('rightButton')
        self.tex_stun_bombs  = bs.gettexture('ouyaIcon')
        self.tex_smb_bomb    = bs.gettexture('touchArrowsActions')
        self.tex_nitrogen    = bs.gettexture('ouyaUButton')

        self._powerupdist: list[str] = []
        for ptype, freq in powerup_dist():
            for _ in range(int(freq)):
                self._powerupdist.append(ptype)

    def get_random_powerup_type(self, forcetype=None, excludetypes=None):
        if excludetypes is None:
            excludetypes = []
        if forcetype:
            self._lastpoweruptype = forcetype
            return forcetype
        if self._lastpoweruptype == 'curse':
            self._lastpoweruptype = 'health'
            return 'health'
        while True:
            ptype = self._powerupdist[random.randint(0, len(self._powerupdist) - 1)]
            if ptype not in excludetypes:
                break
        self._lastpoweruptype = ptype
        return ptype


# ══════════════════════════════════════════════════════════════
#  _pbx_ — بديل PowerupBox.__init__
# ══════════════════════════════════════════════════════════════

_CUSTOM_TYPES = ('headache', 'blackHole', 'antiGrav', 'sloMo', 'portal', 'troll', 'speedBoots', 'mag', 'invisible', 'character', 'ice_man', 'ice_cube', 'tele_bomb', 'stun_bombs', 'smb_bomb', 'nitrogen_bomb', 'fake', 'sticky_ice', 'jump_fly')

pupbox.PowerupBox._old_pbx_ = pupbox.PowerupBox.__init__


# خريطة أسماء الـ powerups
_POWERUP_NAMES: dict = {
    # custom
    'headache':      'Headache',
    'antiGrav':      'Anti-Grav',
    'blackHole':     'Black Hole',
    'sloMo':         'Slo-Mo',
    'portal':        'Portal',
    'troll':         'Troll',
    'speedBoots':    'Speed Boots',
    'mag':           'Magnet',
    'invisible':     'Invisible',
    'character':     'Character',
    'ice_man':       'Ice Man',
    'ice_cube':      'Ice Cube',
    'tele_bomb':     'Tele Bomb',
    'stun_bombs':    'Stun Bombs',
    'smb_bomb':      'SMB Bomb',
    'nitrogen_bomb': 'Nitrogen',
    'sticky_ice':    'Sticky Ice',
    'jump_fly':      'Jump Fly',
    # standard
    'triple_bombs':  'Triple Bombs',
    'ice_bombs':     'Ice Bombs',
    'punch':         'Punch',
    'impact_bombs':  'Impact Bombs',
    'land_mines':    'Land Mines',
    'sticky_bombs':  'Sticky Bombs',
    'shield':        'Shield',
    'health':        'Health',
    'curse':         'Curse',
}


def _add_powerup_timebar(box_self) -> None:
    """يعرض عداد تنازلي بالثواني فوق الـ powerup."""
    if not POWERUP_TIME_BAR:
        return
    try:
        import bascenev1lib.actor.powerupbox as _pupbox
        interval = int(getattr(_pupbox, 'DEFAULT_POWERUP_INTERVAL', 20.0))

        _math = bs.newnode('math', owner=box_self.node, attrs={
            'input1': (0.0, 0.85, 0.0), 'operation': 'add',
        })
        box_self.node.connectattr('position', _math, 'input2')
        _txt = bs.newnode('text', owner=box_self.node, attrs={
            'text':     str(interval),
            'in_world': True,
            'scale':    0.013,
            'shadow':   0.5,
            'flatness': 1.0,
            'color':    (0.2, 1.0, 0.2),
            'h_align':  'center',
        })
        _math.connectattr('output', _txt, 'position')

        # لون يتغير: أخضر → أصفر → أحمر مع اقتراب النهاية
        bs.animate_array(_txt, 'color', 3, {
            0:                  (0.2, 1.0, 0.2),
            interval * 0.5:     (1.0, 1.0, 0.0),
            interval * 0.8:     (1.0, 0.4, 0.0),
            interval - 3.0:     (1.0, 0.0, 0.0),
        })

        def _tick(remaining=interval) -> None:
            try:
                if not _txt.exists():
                    return
                _txt.text = str(remaining) + 's'
            except Exception:
                pass

        for i in range(interval + 1):
            bs.timer(float(i), babase.CallPartial(_tick, interval - i))
    except Exception:
        pass


def _pbx_(self, position=(0.0, 1.0, 0.0), poweruptype='triple_bombs', expire=True):
    factory = NewPowerupBoxFactory.get()
    if poweruptype in _CUSTOM_TYPES:
        self._old_pbx_(position, 'triple_bombs', expire)
        self.poweruptype = poweruptype
        if SPARK_WHEN_SPAWN:
            pos = self.node.position
            bs.emitfx(position=pos, scale=2.0, count=30,
                      spread=0.6, chunk_type='spark')
            bs.emitfx(position=pos, scale=1.5, count=15,
                      spread=0.4, chunk_type='sweat')
        _add_powerup_timebar(self)
        if poweruptype == 'headache':
            self.node.color_texture = factory.tex_headache
        elif poweruptype == 'blackHole':
            self.node.color_texture = factory.tex_blackhole
        elif poweruptype == 'antiGrav':
            self.node.color_texture = factory.tex_antigrav
        elif poweruptype == 'sloMo':
            self.node.color_texture = factory.tex_slomo
        elif poweruptype == 'portal':
            self.node.color_texture = factory.tex_portal
        elif poweruptype == 'troll':
            self.node.color_texture = factory.tex_troll
        elif poweruptype == 'speedBoots':
            self.node.color_texture = factory.tex_speedboots
        elif poweruptype == 'mag':
            self.node.color_texture = factory.tex_mag
        elif poweruptype == 'invisible':
            self.node.color_texture = factory.tex_invisible
        elif poweruptype == 'character':
            self.node.color_texture = factory.tex_character
        elif poweruptype == 'ice_man':
            self.node.color_texture = factory.tex_ice_man
        elif poweruptype == 'ice_cube':
            self.node.color_texture = bs.gettexture('bombColorIce')
        elif poweruptype == 'tele_bomb':
            self.node.color_texture = bs.gettexture('rightButton')
        elif poweruptype == 'stun_bombs':
            self.node.color_texture = bs.gettexture('ouyaIcon')
        elif poweruptype == 'smb_bomb':
            self.node.color_texture = bs.gettexture('touchArrowsActions')
        elif poweruptype == 'nitrogen_bomb':
            self.node.color_texture = bs.gettexture('bombColorIce')
        elif poweruptype == 'sticky_ice':
            self.node.color_texture = factory.tex_sticky_ice
        elif poweruptype == 'jump_fly':
            self.node.color_texture = factory.tex_jump_fly

        elif poweruptype == 'fake':
            import random as _r
            _fake_texs = (
                'powerupBomb', 'powerupPunch', 'powerupShield',
                'powerupStickyBombs', 'powerupImpactBombs',
                'powerupIceBombs', 'powerupHealth', 'powerupLandMines',
                'bombColorIce', 'achievementMine',
                'achievementOnslaught', 'circleOutlineNoAlpha',
                'achievementFootballShutout', 'achievementFlawlessVictory',
                'achievementOffYouGo', 'powerupSpeed', 'tickets',
                'wizardIcon', 'ouyaUButton', 'ouyaOButton',
                'bombColorIce', 'rightButton', 'ouyaIcon',
                'touchArrowsActions',
            )
            self.node.color_texture = bs.gettexture(_r.choice(_fake_texs))

        # ── درع يتغير لونه على الصندوق ──
        if SHIELD_ON_POWERUPS:
            _shield = bs.newnode(
                'shield', owner=self.node,
                attrs={'color': (2, 0, 0), 'radius': 1.3},
            )
            self.node.connectattr('position', _shield, 'position')
            bs.animate_array(
                _shield, 'color', 3,
                {0: (0, 0, 2), 0.5: (0, 2, 0), 1.0: (2, 0, 0), 1.5: (2, 2, 0), 2.0: (2, 0, 2), 2.5: (0, 1, 6), 3.0: (1, 2, 0)},
                loop=True,
            )

        # ── إسم الـ powerup فوق الصندوق ──
        if NAME_ON_POWERUPS:
            # fake: نأخذ اسم texture الذي اختاره (مجهول للاعب)
            if poweruptype == 'fake':
                import random as _r
                _display_name = _r.choice([
                    'Triple Bombs', 'Ice Bombs', 'Punch', 'Impact Bombs',
                    'Land Mines', 'Sticky Bombs', 'Shield', 'Health',
                    'Triple Bombs', 'Sticky Bombs', 'Ice Bombs',
                ])
            else:
                _display_name = _POWERUP_NAMES.get(poweruptype, poweruptype)
            _math = bs.newnode('math', owner=self.node, attrs={
                'input1': (0.0, 0.5, 0.0), 'operation': 'add',
            })
            self.node.connectattr('position', _math, 'input2')
            _txt = bs.newnode('text', owner=self.node, attrs={
                'text':      _display_name,
                'in_world':  True,
                'scale':     0.01,
                'shadow':    0.5,
                'flatness':  1.0,
                'color':     (1, 0, 0),
                'h_align':   'center',
            })
            _math.connectattr('output', _txt, 'position')
            bs.animate(_txt, 'scale', {0: 0.0, 0.4: 0.0, 0.5: 0.013})
            bs.animate_array(_txt, 'color', 3, {
                0:   (1, 0,   0),
                0.2: (1, 0.5, 0),
                0.4: (1, 1,   0),
                0.6: (0, 1,   0),
                0.8: (0, 1,   1),
                1.0: (1, 0,   1),
                1.2: (1, 0,   0),
            }, loop=True)
    else:
        self._old_pbx_(position, poweruptype, expire)
        if SPARK_WHEN_SPAWN:
            try:
                pos = self.node.position
                bs.emitfx(position=pos, scale=2.0, count=30,
                          spread=0.6, chunk_type='spark')
                bs.emitfx(position=pos, scale=1.5, count=15,
                          spread=0.4, chunk_type='sweat')
            except Exception:
                pass
        _add_powerup_timebar(self)
        if SHIELD_ON_POWERUPS:
            try:
                _shield = bs.newnode(
                    'shield', owner=self.node,
                    attrs={'color': (2, 0, 0), 'radius': 1.3},
                )
                self.node.connectattr('position', _shield, 'position')
                bs.animate_array(
                    _shield, 'color', 3,
                    {0: (2, 0, 0), 0.5: (0, 2, 0), 1: (0, 1, 6), 1.5: (2, 0, 0)},
                    loop=True,
                )
            except Exception:
                pass
        if NAME_ON_POWERUPS:
            try:
                _display_name = _POWERUP_NAMES.get(poweruptype, poweruptype)
                _math = bs.newnode('math', owner=self.node, attrs={
                    'input1': (0.0, 0.5, 0.0), 'operation': 'add',
                })
                self.node.connectattr('position', _math, 'input2')
                _txt = bs.newnode('text', owner=self.node, attrs={
                    'text':     _display_name,
                    'in_world': True,
                    'scale':    0.01,
                    'shadow':   0.5,
                    'flatness': 1.0,
                    'color':    (1, 0, 0),
                    'h_align':  'center',
                })
                _math.connectattr('output', _txt, 'position')
                bs.animate(_txt, 'scale', {0: 0.0, 0.4: 0.0, 0.5: 0.013})
                bs.animate_array(_txt, 'color', 3, {
                    0:   (1, 0,   0),
                    0.2: (1, 0.5, 0),
                    0.4: (1, 1,   0),
                    0.6: (0, 1,   0),
                    0.8: (0, 1,   1),
                    1.0: (1, 0,   1),
                    1.2: (1, 0,   0),
                }, loop=True)
            except Exception:
                pass


# ══════════════════════════════════════════════════════════════
#  Bomb.__init__ — نضيف دعم 'headache' و 'antigrav'
#  نستخدم 'ice' كـ base type (مثل powerup_manager تماماً)
#  'ice' ليس له arm() ولا يتصرف كـ land_mine
# ══════════════════════════════════════════════════════════════

_CUSTOM_BOMB_TYPES = ('headache', 'antigrav', 'ice_cube_bomb', 'tele_bomb', 'stun_bomb', 'smb_bomb', 'nitrogen')






# ══════════════════════════════════════════════════════════════
#  Helpers — classes مساعدة للقنابل
# ══════════════════════════════════════════════════════════════

# ══════════════════════════════════════════════════════════════
#  قوائم لحفظ الـ objects حية
# ══════════════════════════════════════════════════════════════

_active_aimers:    list = []

def _cp_update_counter(spaz) -> None:
    """يحدّث counter_text/counter_texture فوق رأس اللاعب."""
    if not spaz.node or not spaz.node.exists():
        return
    count = getattr(spaz, '_cp_count', 0)
    cp    = getattr(spaz, '_cp_custom', None)
    try:
        if cp and count > 0:
            factory = NewPowerupBoxFactory.get()
            tex_map = {
                'headache':       factory.tex_headache,
                'antigrav':       factory.tex_antigrav,
                'tele_bomb':      factory.tex_tele_bomb,
                'smb_bomb':       factory.tex_smb_bomb,
                'ice_cube_bomb': factory.tex_ice_cube,
            }
            tex = tex_map.get(cp, factory.tex_headache)
            spaz.node.counter_text    = 'x' + str(count)
            spaz.node.counter_texture = tex
        else:
            spaz.node.counter_text = ''
    except Exception:
        pass
_active_antigravs: list = []
_active_controllers: list = []


# ══════════════════════════════════════════════════════════════
#  _HeadacheAimer — مطابق للأصل custom_powerups1_0.py
#  تطير نحو الهدف، وعند الاقتراب تدور حول رأسه
# ══════════════════════════════════════════════════════════════

class _HeadacheAimer:
    """تطير نحو العدو، تدور فوق رأسه حتى تنفجر.
    - Teams: تستهدف الفريق المعادي + bots
    - FFA:   تستهدف كل اللاعبين غير الرامي + bots
    """

    ORBIT_DIST  = 1.2
    ORBIT_SPEED = 6.0
    ORBIT_R     = 0.6

    def __init__(self, node: bs.Node, owner_node: bs.Node | None) -> None:
        self._node        = node
        self._owner       = owner_node
        self._owner_spaz  = None
        self._owner_team  = None
        self._target: bs.Node | None = None
        self._angle       = 0.0
        self._orbiting    = False
        self._timer       = bs.Timer(0.05, self._update, repeat=True)
        if owner_node and owner_node.exists():
            try:
                spaz = owner_node.getdelegate(object)
                self._owner_spaz = spaz
                pl = getattr(spaz, 'player', None)
                if pl:
                    self._owner_team = getattr(pl, 'team', None)
            except Exception:
                pass
        _active_aimers.append(self)

    def _is_enemy(self, node: bs.Node) -> bool:
        try:
            spaz = node.getdelegate(object)
            if spaz is None:
                return False
            pl = getattr(spaz, 'player', None)
            if pl is None:
                return True   # bot
            if spaz is self._owner_spaz:
                return False
            if self._owner_team is not None:
                their_team = getattr(pl, 'team', None)
                if their_team is not None:
                    return their_team is not self._owner_team
            return True   # FFA
        except Exception:
            return False

    def _find_target(self) -> bs.Node | None:
        if not self._node.exists():
            return None
        pos = self._node.position
        best_dist = float('inf')
        best: bs.Node | None = None
        for node in bs.getnodes():
            if not node.exists() or node.getnodetype() != 'spaz':
                continue
            if self._owner and node is self._owner:
                continue
            if not self._is_enemy(node):
                continue
            try:
                tp = node.position
                d = ((tp[0]-pos[0])**2 + (tp[1]-pos[1])**2 + (tp[2]-pos[2])**2) ** 0.5
                if d < best_dist:
                    best_dist = d
                    best = node
            except Exception:
                continue
        return best

    def _update(self) -> None:
        if not self._node.exists():
            self._stop()
            return

        if self._target is None or not self._target.exists():
            self._angle    = 0.0
            self._orbiting = False
            self._target   = self._find_target()

        if self._target is None:
            return

        try:
            tpos = self._target.position
        except Exception:
            self._target   = None
            self._orbiting = False
            return

        pos  = self._node.position
        # نهدف فوق رأس العدو بـ +1.5
        tx = tpos[0]
        ty = tpos[1] + 0.8
        tz = tpos[2]
        dx = tx - pos[0]
        dy = ty - pos[1]
        dz = tz - pos[2]
        dist = (dx*dx + dy*dy + dz*dz) ** 0.5

        if dist > self.ORBIT_DIST:
            # طيران نحو العدو بـ velocity فقط
            self._orbiting = False
            inv = 12.0 / dist
            self._node.velocity = (dx*inv, dy*inv, dz*inv)
        else:
            # دوران بـ velocity فقط حول رأس العدو — لا نلمس position
            if not self._orbiting:
                self._orbiting    = True
                self._orbit_start = bs.time()
            self._angle += self.ORBIT_SPEED * 0.05
            # موضع الدوران المستهدف
            ox  = math.cos(self._angle) * self.ORBIT_R
            oz  = math.sin(self._angle) * self.ORBIT_R
            gx  = tpos[0] + ox
            gy  = tpos[1] + 0.8
            gz  = tpos[2] + oz
            # velocity نحو موضع الدوران بسرعة عالية
            self._node.velocity = (
                (gx - pos[0]) * 25.0,
                (gy - pos[1]) * 25.0,
                (gz - pos[2]) * 25.0,
            )
            # بعد 5 ثواني تنفجر بـ DieMessage فقط (ice bomb تنفجر طبيعياً)
            if bs.time() - self._orbit_start >= 5.0:
                try:
                    if self._node.exists():
                        self._node.handlemessage(bs.DieMessage())
                except Exception:
                    pass
                self._stop()

    def _stop(self) -> None:
        self._timer = None
        try:
            _active_aimers.remove(self)
        except ValueError:
            pass


# ══════════════════════════════════════════════════════════════
#  _AntiGravController
# ══════════════════════════════════════════════════════════════

class _AntiGravController:
    RADIUS        = 2.1   # نطاق الطيران (غير مرئي)
    SHIELD_RADIUS = 3.0   # حجم الـ shield المرئي
    DURATION      = 7.0

    def __init__(self, position: tuple, owner_node: bs.Node | None = None) -> None:
        import random as _r
        self.pos     = (position[0], position[1], position[2])
        self._alive  = True
        self._affected: set = set()

        # shield مرئي بحجم منفرد
        color = (_r.random(), _r.random(), _r.random())
        self._shield = bs.newnode('shield', attrs={
            'position': self.pos,
            'color':    color,
            'radius':   0.1,
        })
        bs.animate(self._shield, 'radius',
                   {0: 0.1, 0.5: self.SHIELD_RADIUS})
        bs.animate_array(self._shield, 'color', 3,
            {0: color, 0.5: (0, 1, 1), 1.0: color}, loop=True)
        # حذف تلقائي بعد DURATION
        bs.timer(self.DURATION, babase.CallPartial(
            lambda s: s.delete() if s.exists() else None, self._shield))

        # مسح يدوي كل 50ms للطيران (نطاق RADIUS منفرد)
        self._timer = bs.timer(0.05, self._scan, repeat=True)
        bs.timer(self.DURATION, self._cleanup)
        _active_antigravs.append(self)

    def _scan(self) -> None:
        if not self._alive:
            return
        px, py, pz = self.pos
        r2 = self.RADIUS * self.RADIUS
        try:
            for node in bs.getnodes():
                try:
                    if not node.exists() or node.getnodetype() != 'spaz':
                        continue
                    p = node.position
                    # أضف لمن دخل النطاق
                    if (p[0]-px)**2 + (p[1]-py)**2 + (p[2]-pz)**2 <= r2:
                        self._affected.add(node)
                except Exception:
                    continue
        except Exception:
            pass
        # طيّر كل من دخل النطاق سابقاً حتى لو خرج
        dead = set()
        for node in self._affected:
            try:
                if not node.exists():
                    dead.add(node)
                    continue
                # إذا مات اللاعع أو عنده درع spawn أزله/تجاوزه
                delegate = node.getdelegate(object, doraise=False)
                alive = getattr(delegate, 'is_alive', None)
                if callable(alive) and not alive():
                    dead.add(node)
                    continue
                # تجاوز من عنده invincible (درع spawn)
                if getattr(node, 'invincible', False):
                    continue
                p = node.position
                node.handlemessage(
                    'impulse',
                    p[0], p[1] + 0.5, p[2],
                    0.0, 5.0, 0.0,
                    3.0, 10.0, 0.0, 0,
                    0.0, 5.0, 0.0,
                )
            except Exception:
                dead.add(node)
        self._affected.difference_update(dead)

    def _cleanup(self) -> None:
        """بعد 7 ثوان — shield و نطاق يختفيان، الطيران يستمر حتى الموت."""
        self._alive = False
        self._timer = None  # bs.timer stops when reference is lost
        # shield يختفي فوراً
        try:
            if self._shield.exists():
                self._shield.delete()
        except Exception:
            pass
        try:
            _active_antigravs.remove(self)
        except ValueError:
            pass
        # استمر في تطيير من دخل النطاق حتى يموتوا
        if self._affected:
            self._float_timer = bs.Timer(0.05, self._float_only, repeat=True)

    def _float_only(self) -> None:
        """يطير من دخل النطاق سابقاً حتى يموتوا."""
        dead = set()
        for node in self._affected:
            try:
                if not node.exists():
                    dead.add(node)
                    continue
                delegate = node.getdelegate(object, doraise=False)
                alive = getattr(delegate, 'is_alive', None)
                if callable(alive) and not alive():
                    dead.add(node)
                    continue
                if getattr(node, 'invincible', False):
                    continue
                p = node.position
                node.handlemessage(
                    'impulse',
                    p[0], p[1] + 0.5, p[2],
                    0.0, 5.0, 0.0,
                    3.0, 10.0, 0.0, 0,
                    0.0, 5.0, 0.0,
                )
            except Exception:
                dead.add(node)
        self._affected.difference_update(dead)
        if not self._affected:
            self._float_timer = None


# ══════════════════════════════════════════════════════════════
#  _MiniZone — مطابق MiniZone في baExPowerups.py
#  shield مرئي + region يطبّق freeze أو stun
# ══════════════════════════════════════════════════════════════

class _MiniZone:
    def __init__(self,
                 zone_type: str = 'freeze',
                 duration:  float = 5.0,
                 radius:    float = 1.5,
                 owner:     bs.Node | None = None,
                 color:     tuple = (0.0, 1.5, 1.5),
                 position:  tuple = (0.0, 1.0, 0.0)):
        self.zone_type = zone_type
        self.owner     = owner
        shared = SharedObjects.get()

        self._mat = bs.Material()
        self._mat.add_actions(
            conditions=('they_have_material', shared.player_material),
            actions=(
                ('modify_part_collision', 'collide',  True),
                ('modify_part_collision', 'physical', False),
                ('call', 'at_connect', self._call),
            )
        )
        self.show_zone = bs.newnode('shield', owner=owner,
            attrs={'position': position, 'color': color, 'radius': radius})

        self.region = bs.newnode('region', owner=self.show_zone,
            attrs={'position': position,
                   'scale': [radius * 0.6] * 3,
                   'type': 'sphere',
                   'materials': [self._mat]})
        self.show_zone.connectattr('position', self.region, 'position')
        bs.timer(duration, self._end)
        _active_controllers.append(self)

    def _call(self) -> None:
        try:
            node = bs.getcollision().opposingnode
            if not (node and node.exists()):
                return
            if self.zone_type == 'freeze':
                node.handlemessage(bs.FreezeMessage())
            elif self.zone_type == 'stun':
                pos = self.show_zone.position                       if (self.show_zone and self.show_zone.exists())                       else (0.0, 0.0, 0.0)
                for _ in range(2):
                    node.handlemessage('impulse',
                        pos[0], pos[1], pos[2],
                        0.0, 0.0, 0.0,
                        260, 0.0, 560, 0,
                        0.0, 1.0, 0.0)
                node.handlemessage('knockout', 2000)
                bs.timer(1.5, babase.CallPartial(
                    node.handlemessage, 'knockout', 2000))
                expl = bs.newnode('explosion', attrs={
                    'position': node.position,
                    'color': (2.0, 0.0, 0.0),
                    'radius': 0.8, 'big': False})
                bs.timer(0.5, expl.delete)
                bs.getsound('shieldHit').play()
        except Exception:
            pass

    def _end(self) -> None:
        try:
            if self.show_zone and self.show_zone.exists():
                r = self.show_zone.radius
                bs.animate(self.show_zone, 'radius', {0: r, 0.1: 0})
                bs.timer(0.1, self.show_zone.delete)
        except Exception:
            pass
        try:
            _active_controllers.remove(self)
        except ValueError:
            pass


# ══════════════════════════════════════════════════════════════
#  _IceCube — مطابق GlooWall في baExPowerups.py
#  crate حقيقي، sticky، يجمّد من يلمسه
# ══════════════════════════════════════════════════════════════

class _IceCube(bs.Actor):
    def __init__(self, owner: bs.Node | None = None,
                 position: tuple = (0.0, 0.7, 0.0)):
        super().__init__()
        self.owner = owner
        scale      = 2.55
        shared     = SharedObjects.get()

        # material: physical=False حتى يدخل اللاعب المكعب
        # عند الدخول يمسك المكعب (_pick_up) مثل الأصل
        self._mat = bs.Material()
        self._mat.add_actions(
            conditions=('they_have_material', shared.player_material),
            actions=(
                ('modify_part_collision', 'collide',  True),
                ('modify_part_collision', 'physical', False),
                ('call', 'at_connect', self._on_contact),
            )
        )
        pos = (position[0], position[1] + 1.0, position[2])
        self.node = bs.newnode('prop', delegate=self, attrs={
            'body':             'crate',
            'body_scale':       scale,
            'position':         pos,
            'mesh':             bs.getmesh('box'),
            'density':          1.0,
            'shadow_size':      0.0,
            'color_texture':    bs.gettexture('bombColorIce'),
            'reflection':       'soft',
            'sticky':           True,
            'reflection_scale': [2.6],
            'materials':        [self._mat, shared.footing_material],
        })
        bs.animate(self.node, 'mesh_scale',
            {0: 0, 0.14: scale * 1.6, 0.20: scale - 1.0})
        bs.timer(15.0, babase.CallPartial(
            self.handlemessage, bs.DieMessage()))
        _active_controllers.append(self)

    def _on_contact(self) -> None:
        # مثل الأصل: اللاعب يمسك المكعب فيحمله ويُحبس فيه
        try:
            node     = bs.getcollision().opposingnode
            cls_node = node.getdelegate(object)
            if cls_node is not None:
                cls_node._pick_up(self.node)
        except Exception:
            pass

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, bs.DieMessage):
            if self.node and self.node.exists():
                pos = self.node.position
                expl = bs.newnode('explosion', attrs={
                    'position': pos,
                    'color':    (0.0, 0.0, 2.0),
                    'radius':   1.9, 'big': False})
                bs.timer(1.0, expl.delete)
                bs.emitfx(position=pos,
                          velocity=(0.0, 12.0, 0.0),
                          count=50, spread=2.0,
                          scale=1.7, chunk_type='ice')
                _MiniZone(zone_type='freeze', duration=5.0, radius=1.5,
                          owner=None,
                          color=(0.0, 1.5, 1.5), position=pos)
                self.node.delete()
            try:
                _active_controllers.remove(self)
            except ValueError:
                pass
        else:
            super().handlemessage(msg)



# ══════════════════════════════════════════════════════════════
#  _SmbBall — مطابق Smb في baExPowerups.py
#  body_scale=4، scale=0.7، دوران حول الهدف
# ══════════════════════════════════════════════════════════════

class _SmbBall(bs.Actor):
    def __init__(self, angle: int = 0, owner: bs.Node | None = None,
                 position: tuple = (0.0, 1.0, 0.0)):
        super().__init__()
        self.owner = owner
        shared     = SharedObjects.get()
        scale      = 0.7   # مثل ex.Cosmic(owner, 0.7) في الأصل

        mat1 = bs.Material()
        mat1.add_actions(
            conditions=('they_have_material', shared.player_material),
            actions=(
                ('modify_part_collision', 'collide',  True),
                ('modify_part_collision', 'physical', False),
                ('call', 'at_connect', self._call),
            )
        )
        mat2 = bs.Material()
        mat2.add_actions(
            conditions=('they_have_material', shared.pickup_material),
            actions=('modify_part_collision', 'collide', False)
        )

        texs = ['aliColorMask', 'aliColor', 'eggTex3', 'eggTex2']
        self.node = bs.newnode('prop', delegate=self, attrs={
            'body':             'sphere',
            'body_scale':       4,
            'position':         position,
            'mesh':             bs.getmesh('shield'),
            'shadow_size':      0.5,
            'color_texture':    bs.gettexture(texs[angle % 4]),
            'reflection':       'soft',
            'reflection_scale': [1.3],
            'materials':        (mat1, mat2, shared.object_material),
        })
        # مطابق الأصل: {0:0, 0.14: scale*1.6, 0.20: scale}
        bs.animate(self.node, 'mesh_scale',
            {0: 0, 0.14: scale * 1.6, 0.20: scale})
        self._direction(angle, position)
        _active_controllers.append(self)

    def _call(self) -> None:
        try:
            node = bs.getcollision().opposingnode
            if not (node and node.exists()) or node is self.owner:
                return
            if hasattr(node, 'hold_node'):
                node.hold_node = None
            vel = getattr(self.node, 'velocity', (0.0, 0.0, 0.0))                   if (self.node and self.node.exists()) else (0.0, 0.0, 0.0)
            pos = list(self.node.position) if (self.node and self.node.exists())                   else [0.0, 0.0, 0.0]
            pos[1] = -50   # مطابق الأصل

            def _impulse() -> None:
                if not (node and node.exists()):
                    return
                for _ in range(2):
                    node.handlemessage('impulse',
                        pos[0], pos[1], pos[2],
                        vel[0], vel[1]+2.0, vel[2],
                        500*4, 0.0, 7840, 0,
                        vel[0], vel[1]+2.0, vel[2])

            def _blast(ix: int | None = None, imp: float = 0.5) -> None:
                if not (node and node.exists()):
                    return
                p = node.position
                if ix == 0:
                    bpos = (p[0], p[1]+0.5, p[2])
                elif ix == 1:
                    bpos = (p[0], p[1]-0.5, p[2])
                else:
                    bpos = (p[0], p[1]-0.3, p[2])
                expl = bs.newnode('explosion', attrs={
                    'position': bpos,
                    'color': (1.0, 0.5, 0.0),
                    'radius': imp, 'big': False})
                bs.timer(0.5, expl.delete)

            _blast()
            _impulse()
            bs.timer(0.2, _impulse)
            bs.timer(0.8, babase.CallPartial(_blast, 0, 0.8))
            bs.timer(1.5, babase.CallPartial(_blast, 1, 1.5))
        except Exception:
            pass

    def _direction(self, angle: int, start: tuple) -> None:
        # مطابق direction() الأصلي
        reduction = 44.44
        dis      = round(18.0 * (100 - reduction) / 100, 2)
        duration = round(1.3  * (100 - reduction) / 100, 2)
        dirs = [
            (start[0]+dis, start[1], start[2]),
            (start[0]-dis, start[1], start[2]),
            (start[0], start[1], start[2]+dis),
            (start[0], start[1], start[2]-dis),
        ]
        bs.animate_array(self.node, 'position', 3,
            {0.0: start, duration: dirs[min(angle, 3)]})
        bs.timer(duration, babase.CallPartial(
            self.handlemessage, bs.DieMessage()))

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, bs.DieMessage):
            if self.node and self.node.exists():
                self.node.delete()
            try:
                _active_controllers.remove(self)
            except ValueError:
                pass
        else:
            super().handlemessage(msg)


def _smb_launch(owner: bs.Node | None, position: tuple) -> None:
    for i in range(4):
        ball = _SmbBall(angle=i, owner=owner, position=position)
        ball.autoretain()
    bs.getsound('cheer').play()


# ══════════════════════════════════════════════════════════════
#  القنابل المخصصة — تُضاف عبر _bomb_init (monkey-patch)
# ══════════════════════════════════════════════════════════════

_CUSTOM_BOMB_REAL_TYPE: dict = {
    'headache':       'normal',
    'nitrogen':       'ice',
    'ice_bubble':     'ice',
    'smb_bomb':       'impact',
    'stun_bomb':      'normal',
    'tele_bomb':      'impact',
    'ice_cube_bomb': 'impact',
    'antigrav':       'impact',
    'sticky_ice':     'sticky',
}

_CUSTOM_BOMB_TYPES = tuple(_CUSTOM_BOMB_REAL_TYPE.keys())



# ══════════════════════════════════════════════════════════════
#  Bomb.__init__ patch — مطابق للأصل custom_powerups1_0.py
#  نُعدّل self مباشرة بعد استدعاء الـ init الأصلي
# ══════════════════════════════════════════════════════════════

Bomb._cp_old_bomb     = Bomb.__init__
Bomb._cp_old_impact   = Bomb._handle_impact

def _cp_handle_impact(self) -> None:
    """تجاهل التصادم مع صاحب القنبلة — smb/tele تنفجر عند لمس أي شيء غير صاحبها."""
    cp_type = getattr(self, '_cp_bomb_type', None)
    if cp_type in _CUSTOM_BOMB_REAL_TYPE:
        try:
            node = bs.getcollision().opposingnode
            if node and node.exists() and node is self.owner:
                return
        except Exception:
            pass
    self._cp_old_impact()

Bomb._handle_impact = _cp_handle_impact


def _bomb_init(
    self,
    position=(0.0, 1.0, 0.0),
    velocity=(0.0, 0.0, 0.0),
    bomb_type='normal',
    blast_radius=2.0,
    bomb_scale=1.0,
    source_player=None,
    owner=None,
):
    # نقرأ bomb_type من المالك
    if owner:
        try:
            spaz = owner.getdelegate(Spaz, doraise=False)
            if spaz:
                # _cp_custom أولاً — ثم sticky_ice
                cp    = getattr(spaz, '_cp_custom', None)
                count = getattr(spaz, '_cp_count',  0)
                if cp and count > 0:
                    bomb_type      = cp
                    spaz._cp_count = count - 1
                    _cp_update_counter(spaz)
                    if spaz._cp_count <= 0:
                        spaz._cp_custom = None
                        prev = getattr(spaz, '_cp_prev_bomb', 'normal')
                        spaz.bomb_type  = prev if prev else 'normal'
                        spaz.bomb_count = getattr(spaz, '_cp_default_bomb_count', 1)
                elif getattr(spaz, '_sticky_ice_active', False):
                    bomb_type = 'sticky_ice' 
        except Exception:
            pass

    self._cp_bomb_type = bomb_type

    # real_type الذي يُمرَّر لـ Bomb.__init__ الأصلي
    real_type = _CUSTOM_BOMB_REAL_TYPE.get(bomb_type, bomb_type)

    self._cp_old_bomb(
        position=position, velocity=velocity,
        bomb_type=real_type, blast_radius=blast_radius,
        bomb_scale=bomb_scale, source_player=source_player,
        owner=owner,
    )

    # ── radius القنبلة حسب نوعها ──
    _b_radius = 1.1 if bomb_type == 'tnt' else 0.7


    # ── name on bomb ──
    if NAME_ON_BOMBS:
        try:
            _BOMB_NAMES = {
                'normal':       'Bomb',
                'ice':          'Ice Bomb',
                'impact':       'Impact Bomb',
                'land_mine':    'Land Mine',
                'sticky':       'Sticky Bomb',
                'tnt':          'TNT',
                'ice_bubble':   'Ice Bubble',
                'headache':     'Headache',
                'nitrogen':     'Nitrogen',
                'smb_bomb':     'SMB Bomb',
                'stun_bomb':    'Stun Bomb',
                'tele_bomb':    'Tele Bomb',
                'ice_cube_bomb':'Ice Cube',
                'antigrav':     'Anti-Grav',
                'sticky_ice':   'Sticky Ice',
            }
            _bname = _BOMB_NAMES.get(bomb_type, bomb_type)
            _offset = 0.8 if bomb_type == 'tnt' else 0.7
            _bmath = bs.newnode('math', owner=self.node, attrs={
                'input1': (0.0, _offset, 0.0), 'operation': 'add',
            })
            self.node.connectattr('position', _bmath, 'input2')
            _btxt = bs.newnode('text', owner=self.node, attrs={
                'text':     _bname,
                'in_world': True,
                'scale':    0.012,
                'shadow':   0.5,
                'flatness': 1.0,
                'color':    (1, 0, 0),
                'h_align':  'center',
            })
            _bmath.connectattr('output', _btxt, 'position')
            bs.animate_array(_btxt, 'color', 3, {
                0:   (1, 0,   0),
                0.2: (1, 0.5, 0),
                0.4: (1, 1,   0),
                0.6: (0, 1,   0),
                0.8: (0, 1,   1),
                1.0: (1, 0,   1),
                1.2: (1, 0,   0),
            }, loop=True)
        except Exception:
            pass

    # ── shield on bomb ──
    if SHIELD_ON_BOMBS:
        try:
            _bs = bs.newnode('shield', owner=self.node, attrs={
                'color':  (1.0, 1.0, 1.0),
                'radius': _b_radius,
            })
            self.node.connectattr('position', _bs, 'position')
            bs.animate_array(_bs, 'color', 3, {
                0:   (0, 0, 2),
                0.5: (0, 2, 0),
                1.0: (2, 0, 0),
                1.5: (2, 2, 0),
                2.0: (2, 0, 2),
                2.5: (0, 1, 6),
                3.0: (1, 2, 0),
            }, loop=True)
        except Exception:
            pass

    # ── headache ──
    if bomb_type == 'headache':
        self.bomb_type          = 'headache'
        self.node.color_texture = bs.gettexture('achievementOnslaught')
        self.node.mesh          = bs.getmesh('impactBomb')
        self.node.gravity_scale = 0.3
        aimer = _HeadacheAimer(self.node, owner_node=owner)
        # نحفظه في self لمنع GC
        self._cp_aimer = aimer

    # ── ice_bubble — مثل powerup_manager: shield أزرق بدون mesh ──
    elif bomb_type == 'ice_bubble':
        self.bomb_type = 'ice_bubble'
        self.node.mesh = None
        self._ice_shield = bs.newnode(
            'shield', owner=self.node,
            attrs={'color': (0.5, 1.0, 7.0), 'radius': 0.6}
        )
        self.node.connectattr('position', self._ice_shield, 'position')
        self.blast_radius = getattr(self, 'blast_radius', 2.0) * 0.5

    # ── nitrogen ──
    elif bomb_type == 'nitrogen':
        self.bomb_type          = 'nitrogen'
        self.node.color_texture = bs.gettexture('bombColorIce')
        self.node.reflection    = 'soft'
        self.node.reflection_scale = [1.3]

    # ── smb_bomb ──
    elif bomb_type == 'smb_bomb':
        self.bomb_type          = 'smb_bomb'
        self.node.mesh          = bs.getmesh('bomb')
        self.node.color_texture = bs.gettexture('touchArrowsActions')
        self.node.reflection    = 'soft'
        self.node.reflection_scale = [2.6]
        bs.animate(self.node, 'mesh_scale',
            {0: 0, 0.2: 1.3, 0.26: 1.0})

    # ── stun_bomb ──
    elif bomb_type == 'stun_bomb':
        self.bomb_type          = 'stun_bomb'
        self.node.mesh          = bs.getmesh('bomb')
        self.node.color_texture = bs.gettexture('crossOutMask')
        self.node.reflection    = 'soft'
        self.node.reflection_scale = [1.8]

    # ── tele_bomb ──
    elif bomb_type == 'tele_bomb':
        self.bomb_type          = 'tele_bomb'
        self.node.mesh          = bs.getmesh('impactBomb')
        self.node.color_texture = bs.gettexture('aliColorMask')
        self.node.reflection    = 'soft'
        self.node.gravity_scale = 0.5
        self.node.reflection_scale = [1.3]

    # ── gloo_wall_bomb ──
    elif bomb_type == 'ice_cube_bomb':
        self.bomb_type          = 'ice_cube_bomb'
        self.node.mesh          = bs.getmesh('box')
        self.node.color_texture = bs.gettexture('bombColorIce')
        self.node.reflection    = 'soft'
        self.node.reflection_scale = [2.6]
        bs.animate(self.node, 'mesh_scale',
            {0: 0, 0.2: 0.45, 0.26: 0.35})

    # ── sticky_ice ──
    elif bomb_type == 'sticky_ice':
        self.bomb_type          = 'sticky_ice'
        self.node.color_texture = bs.gettexture('egg4')
        self.node.reflection    = 'soft'
        self.node.reflection_scale = [1.5]

    # ── antigrav ──
    elif bomb_type == 'antigrav':
        self.bomb_type          = 'antigrav'
        self.node.mesh          = bs.getmesh('impactBomb')
        self.node.color_texture = NewPowerupBoxFactory.get().tex_antigrav
        self.node.gravity_scale = 0.8


Bomb._cp_old_bomb_hm = Bomb.handlemessage


def _new_bomb_hm(self, msg: Any) -> Any:
    cp_type = getattr(self, '_cp_bomb_type', None)


    # ── sticky_ice — انفجار عادي + تجميد كل من في النطاق ──
    if cp_type == 'sticky_ice':
        if type(msg).__name__ == 'ExplodeMessage':
            if self.node and self.node.exists():
                pos = self.node.position
                try:
                    for node in list(bs.getnodes()):
                        if not node.exists() or node.getnodetype() != 'spaz':
                            continue
                        p = node.position
                        dx = p[0]-pos[0]; dy = p[1]-pos[1]; dz = p[2]-pos[2]
                        if dx*dx + dy*dy + dz*dz <= 3.0*3.0:
                            node.handlemessage(bs.FreezeMessage())
                except Exception:
                    pass
                bs.emitfx(position=pos, velocity=(0,2,0),
                          count=40, spread=2.0, scale=1.2, chunk_type='ice')
                bs.getsound('freeze').play(position=pos)
                # وميض أزرق عند الانفجار
                light = bs.newnode('light', attrs={
                    'position':   pos,
                    'color':      (0.2, 0.5, 1.0),
                    'radius':     0.5,
                    'volume_intensity_scale': 1.0,
                })
                bs.animate(light, 'intensity', {0: 0, 0.05: 2.0, 0.5: 0})
                bs.animate(light, 'radius',    {0: 0.5, 0.5: 3.0})
                bs.timer(0.5, light.delete)

    # ── antigrav — تنفجر بالفتيل عند ExplodeMessage ──
    if cp_type == 'antigrav':
        if type(msg).__name__ in ('ExplodeMessage', 'ImpactExplodeMessage'):
            if self.node and self.node.exists():
                pos = self.node.position
                ctrl = _AntiGravController(pos, owner_node=getattr(self, 'owner', None))
                _active_antigravs.append(ctrl)
                bs.emitfx(position=pos, scale=2, count=30,
                          spread=1.5, chunk_type='spark')
            return self._cp_old_bomb_hm(bs.DieMessage())

    # ── sticky_ice — عند انفجار sticky تجمد من في النطاق ──
    if getattr(self, '_cp_bomb_type', None) is None and getattr(self, 'bomb_type', None) == 'sticky':
        owner = getattr(self, 'owner', None)
        if owner:
            try:
                spaz = owner.getdelegate(Spaz, doraise=False)
                if spaz and getattr(spaz, '_sticky_ice_timer', None) is not None:
                    if type(msg).__name__ == 'ExplodeMessage':
                        if self.node and self.node.exists():
                            pos = self.node.position
                            bs.emitfx(position=pos, count=20, scale=0.7,
                                      spread=1.2, chunk_type='ice')
                            bs.getsound('freeze').play(position=pos)
                            try:
                                for nd in list(bs.getnodes()):
                                    if not nd.exists() or nd.getnodetype() != 'spaz':
                                        continue
                                    p = nd.position
                                    dx=p[0]-pos[0]; dy=p[1]-pos[1]; dz=p[2]-pos[2]
                                    if dx*dx+dy*dy+dz*dz <= 9.0:
                                        nd.handlemessage(bs.FreezeMessage())
                            except Exception:
                                pass
            except Exception:
                pass

    # ── headache — تنفجر blast freeze عند ExplodeMessage ──
    if cp_type == 'headache':
        if type(msg).__name__ == 'ExplodeMessage':
            if self.node and self.node.exists():
                pos = self.node.position
                from bascenev1lib.actor.bomb import Blast
                Blast(position=pos, velocity=(0,0,0),
                      blast_radius=1.5, blast_type='normal',
                      source_player=getattr(self, '_source_player', None)
                      ).autoretain()
                bs.emitfx(position=pos, velocity=(0,4,0),
                          count=30, spread=1.0, scale=0.8, chunk_type='ice')
                return self._cp_old_bomb_hm(bs.DieMessage())

    # ── ice_bubble — تُجمّد كل من في نطاق الانفجار ══
    elif cp_type == 'ice_bubble':
        if type(msg).__name__ == 'ExplodeMessage':
            if self.node and self.node.exists():
                pos   = self.node.position
                r2    = 1.2 * 1.2
                px, py, pz = pos
                for node in bs.getnodes():
                    if not node.exists() or node.getnodetype() != 'spaz':
                        continue
                    try:
                        np = node.position
                        dx = np[0]-px; dy = np[1]-py; dz = np[2]-pz
                        if dx*dx + dy*dy + dz*dz <= r2:
                            node.handlemessage(bs.FreezeMessage())
                    except Exception:
                        pass
                bs.emitfx(position=pos, velocity=(0, 4, 0),
                          count=25, spread=0.8, scale=0.8, chunk_type='ice')
                bs.getsound('freeze').play(position=pos)

    # ── nitrogen — تُنشئ MiniZone تجميد عند الانفجار ──
    elif cp_type == 'nitrogen':
        if type(msg).__name__ == 'ExplodeMessage':
            if self.node and self.node.exists():
                pos = self.node.position
                mz = _MiniZone(zone_type='freeze', duration=5.0, radius=1.5,
                               owner=getattr(self, 'owner', None),
                               color=(0.0, 1.5, 1.5), position=pos)
                bs.getsound('hiss').play(1.0, pos)
                bs.emitfx(position=pos, velocity=(0, 4, 0),
                          count=40, spread=2.0, scale=0.6, chunk_type='ice')

    # ── smb_bomb — تُطلق 4 كرات عند الانفجار ──
    elif cp_type == 'smb_bomb':
        if type(msg).__name__ == 'ExplodeMessage':
            if self.node and self.node.exists():
                pos = self.node.position
                _smb_launch(owner=getattr(self, 'owner', None), position=pos)
                bs.getsound('hiss').play(1.0, pos)

    # ── stun_bomb — تُنشئ MiniZone إذهال عند الانفجار ──
    elif cp_type == 'stun_bomb':
        if type(msg).__name__ == 'ExplodeMessage':
            if self.node and self.node.exists():
                pos = self.node.position
                mz = _MiniZone(zone_type='stun', duration=8.0, radius=2.0,
                               owner=getattr(self, 'owner', None),
                               color=(2.0, 0.0, 0.0), position=pos)
                bs.getsound('hiss').play(1.0, pos)

    # ── tele_bomb — تنقل الرامي عند الانفجار ──
    elif cp_type == 'tele_bomb':
        if type(msg).__name__ == 'ExplodeMessage':
            if self.node and self.node.exists():
                pos   = self.node.position
                owner = getattr(self, 'owner', None)
                if owner and owner.exists():
                    owner.handlemessage(bs.StandMessage(position=pos))
                expl = bs.newnode('explosion', attrs={
                    'position': pos, 'color': (1.2, 0.23, 0.23),
                    'radius': 1.8, 'big': False})
                bs.timer(1.0, expl.delete)
                bs.emitfx(position=pos, velocity=(0, 8, 0),
                          count=30, spread=1.5, chunk_type='spark')
                bs.getsound('spawn').play(1.0, pos)
                return self._cp_old_bomb_hm(bs.DieMessage())

    # ── gloo_wall_bomb — تنشأ عند لمس الأرض بعد الرمي ──
    elif cp_type == 'ice_cube_bomb':
        if type(msg).__name__ == 'ExplodeMessage':
            if self.node and self.node.exists():
                pos = self.node.position
                gw = _IceCube(owner=getattr(self, 'owner', None), position=pos)
                gw.autoretain()
                bs.getsound('hiss').play(1.0, pos)
                return self._cp_old_bomb_hm(bs.DieMessage())

    # ArmMessage — نمنع الأخطاء للـ types التي لا تدعم arm
    if type(msg).__name__ == 'ArmMessage':
        try:
            return self._cp_old_bomb_hm(msg)
        except RuntimeError:
            return None

    return self._cp_old_bomb_hm(msg)









# ══════════════════════════════════════════════════════════════
#  Spaz.handlemessage — نعطي اللاعب القنابل
# ══════════════════════════════════════════════════════════════



_STANDARD_POPUP = {
    'triple_bombs':  ('', 'TRIPLE BOMBS EQUIPED',  (1.0, 0.7, 0.2)),
    'ice_bombs':     ('', '',                      (0.3, 0.8, 1.0)),
    'punch':         ('', 'GLOVES EQUIPED',        (1.0, 0.6, 0.0)),
    'impact_bombs':  ('', 'IMPACT BOMBS EQUIPED',  (1.0, 0.4, 0.0)),
    'land_mines':    ('', 'LAND MINES EQUIPED',    (0.8, 0.8, 0.2)),
    'sticky_bombs':  ('', 'STICKY BOMBS EQUIPED',  (0.5, 1.0, 0.3)),
    'shield':        ('', 'SHIELD EQUIPED',        (0.3, 0.6, 1.0)),
    'health':        ('', 'HEALTH UP',             (1.0, 0.3, 0.3)),
    'curse':         ('', 'CURSED',           (0.6, 0.0, 0.8)),
}


def new_handlemessage(self, msg: Any) -> Any:

    if isinstance(msg, bs.PowerupMessage) and msg.poweruptype in _STANDARD_POPUP:
        if not self._dead and self.node and self.node.exists():
            # لا نُظهر SHIELD EQUIPED إذا جاء الدرع من fake
            if msg.poweruptype == 'shield' and getattr(self, '_fake_shield', False):
                self._fake_shield = False
            else:
                em, label, col = _STANDARD_POPUP[msg.poweruptype]
                if label and not getattr(self, '_tele_health', False):
                    pos = self.node.position
                    PopupText(
                        f'{em}{label}{em}',
                        color=col, scale=1.2, position=pos
                    ).autoretain()

    if isinstance(msg, bs.PowerupMessage) and msg.poweruptype in _CUSTOM_TYPES:
        if self._dead or not self.node:
            return True

        # احفظ bomb_type الحالي — أي نوع غير محدود العدد
        _current_bomb = getattr(self, 'bomb_type', 'normal')
        _count_limited = ('headache', 'antigrav', 'smb_bomb', 'tele_bomb', 'ice_cube_bomb')
        if _current_bomb not in _count_limited:
            self._cp_prev_bomb = _current_bomb
        # نُصفّر أي bomb_type مخصص سابق محدود العدد
        _bomb_types_to_reset = ('smb_bomb', 'tele_bomb', 'antigrav', 'ice_cube_bomb')
        if _current_bomb in _bomb_types_to_reset:
            self.bomb_type = 'normal'
        self._cp_custom = None
        self._cp_default_bomb_count = self.bomb_count
        self._cp_count  = 0

        ptype = msg.poweruptype
        factory = NewPowerupBoxFactory.get()

        if ptype == 'headache':
            self._cp_custom = 'headache'
            self._cp_count  = 3
            self.bomb_count = 3
            self.bomb_type  = 'headache'
            _cp_update_counter(self)
            tex = factory.tex_headache
            self._flash_billboard(tex)
            PopupText('HEADACHE BOMBS', color=(1, 0.3, 0), scale=1.2, position=self.node.position).autoretain()

        elif ptype == 'antiGrav':
            self._cp_custom = 'antigrav'
            self._cp_count  = 3
            self.bomb_count = 3
            self.bomb_type  = 'antigrav'
            _cp_update_counter(self)
            tex = factory.tex_antigrav
            self._flash_billboard(tex)
            PopupText('ANTIGRAV BOMBS', color=(0, 1, 0.5), scale=1.2, position=self.node.position).autoretain()

        elif ptype == 'sticky_ice':
            _si_duration = 30.0
            self._sticky_ice_active = True
            self.bomb_type = 'sticky_ice'

            def _end_sticky_ice(spaz_ref: Any) -> None:
                spaz = spaz_ref
                if spaz and spaz.node and spaz.node.exists():
                    spaz._sticky_ice_active = False
                    if spaz.bomb_type == 'sticky_ice':
                        prev = getattr(spaz, '_cp_prev_bomb', 'normal')
                        spaz.bomb_type  = prev if prev else 'normal'
                        spaz.bomb_count = 1
                    PopupText('STICKY ICE ENDED', color=(0.3, 0.8, 1.0),
                              scale=1.2, position=spaz.node.position).autoretain()

            self._sticky_ice_timer = bs.Timer(
                _si_duration, babase.CallPartial(_end_sticky_ice, self)
            )
            tex = factory.tex_sticky_ice
            self._flash_billboard(tex)
            t_ms = int(bs.time() * 1000)
            self.node.mini_billboard_2_texture    = tex
            self.node.mini_billboard_2_start_time = t_ms
            self.node.mini_billboard_2_end_time   = t_ms + int(_si_duration * 1000)
            PopupText('STICKY ICE', color=(0.3, 0.8, 1.0), scale=1.2, position=self.node.position).autoretain()

        elif ptype == 'jump_fly':
            try:
                self._jump_fly_active = True

                def _jf_tick(spaz_ref: Any) -> None:
                    spaz = spaz_ref
                    if not spaz or not spaz.node or not spaz.node.exists():
                        return
                    if not getattr(spaz, '_jump_fly_active', False):
                        return
                    try:
                        if spaz.node.jump_pressed:
                            nd  = spaz.node
                            px, py, pz = nd.position
                            vx, vy, vz = nd.velocity
                            # نفس منطق fly.py — 3 impulses فورية
                            nd.handlemessage('impulse', px, py + 0.001, pz,
                                             0, 0.2, 0, 35, 35, 0, 0, 0, 3, 0)
                    except Exception:
                        pass

                self._jump_fly_tick = bs.Timer(0.016, babase.CallPartial(_jf_tick, self), repeat=True)

                def _jf_end(spaz_ref: Any) -> None:
                    spaz = spaz_ref
                    if not spaz or not spaz.node or not spaz.node.exists():
                        return
                    spaz._jump_fly_active = False
                    spaz._jump_fly_tick = None
                    PopupText('JUMP FLY ENDED', color=(1, 0.8, 0),
                              scale=1.2, position=spaz.node.position).autoretain()

                self._jump_fly_end_timer = bs.Timer(30.0, babase.CallPartial(_jf_end, self))
            except Exception:
                pass
            tex = factory.tex_jump_fly
            self._flash_billboard(tex)
            PopupText('JUMP FLY', color=(1, 0.8, 0), scale=1.2, position=self.node.position).autoretain()

        elif ptype == 'blackHole':
            p = self.node.position
            pos = (p[0], p[1] + 3.5, p[2])   # يظهر فوق اللاعب
            _BlackHoleController(pos)
            tex = factory.tex_blackhole
            self._flash_billboard(tex)
            PopupText('BLACK HOLE', color=(0.3, 0, 1), scale=1.2, position=self.node.position).autoretain()

        elif ptype == 'sloMo':
            try:
                g = bs.getactivity().globalsnode
                g.slow_motion = not g.slow_motion
            except Exception:
                pass
            tex = factory.tex_slomo
            self._flash_billboard(tex)
            PopupText('SLO-MO', color=(1, 0.5, 0), scale=1.2, position=self.node.position).autoretain()
            # ice particles كثيفة حول اللاعب (مثل 1.4)
            try:
                p = self.node.position
                bs.emitfx(position=p, velocity=(0, 0, 0), count=600,
                           spread=0.7, chunk_type='ice')
            except Exception:
                pass

        elif ptype == 'portal':
            _PortalController()
            tex = factory.tex_portal
            self._flash_billboard(tex)
            PopupText('PORTAL', color=(0.5, 0, 1), scale=1.2, position=self.node.position).autoretain()

        elif ptype == 'nitrogen_bomb':
            tex = factory.tex_nitrogen
            self._flash_billboard(tex)
            try:
                pos = self.node.position
            except Exception:
                pos = (0.0, 1.0, 0.0)
            self.bomb_type = 'nitrogen'
            t_ms = int(bs.time() * 1000)
            self.node.mini_billboard_2_texture    = tex
            self.node.mini_billboard_2_start_time = t_ms
            self.node.mini_billboard_2_end_time   = t_ms + POWERUP_WEAR_OFF_TIME
            def _nitro_off(spaz: Any) -> None:
                if spaz.node and spaz.node.exists():
                    if spaz.bomb_type == 'nitrogen':
                        if getattr(spaz, '_sticky_ice_active', False):
                            spaz.bomb_type = 'sticky_ice'
                        else:
                            prev = getattr(spaz, '_cp_prev_bomb', 'normal')
                            spaz.bomb_type = prev if prev else 'normal'
            self._nitrogen_timer = bs.Timer(
                POWERUP_WEAR_OFF_TIME / 1000.0,
                babase.CallPartial(_nitro_off, self))
            PopupText('NITROGEN BOMBS EQUIPED', color=(0.3, 0.8, 1.0),
                      scale=1.2, position=pos).autoretain()

        elif ptype == 'smb_bomb':
            self._cp_custom = 'smb_bomb'
            self._cp_count  = 1
            self.bomb_count = 1
            _cp_update_counter(self)
            tex = factory.tex_smb_bomb
            self._flash_billboard(tex)
            PopupText('S.M.B EQUIPED', color=(1.0, 0.5, 0.0),
                      scale=1.2, position=self.node.position).autoretain()

        elif ptype == 'fake':
            import random as _r
            try:
                pos = self.node.position
            except Exception:
                pos = (0.0, 1.0, 0.0)
            if not self.shield:
                danger = _r.choice(['blast', 'freeze'])
                if danger == 'blast':
                    from bascenev1lib.actor.bomb import Blast
                    Blast(
                        position=pos,
                        velocity=self.node.velocity,
                        blast_radius=0.7,
                        blast_type='land_mine',
                    ).autoretain()
                    PopupText('Boom!', position=pos,
                              random_offset=0.0, scale=2.0,
                              color=(1.0, 0.0, 0.0)).autoretain()
                else:
                    self.node.handlemessage(bs.FreezeMessage())
                    PopupText('So Cold!', position=pos,
                              random_offset=0.0, scale=2.0,
                              color=(0.0, 0.5, 1.0)).autoretain()
                    bs.emitfx(position=pos, velocity=self.node.velocity,
                              count=10, scale=0.6, spread=0.4,
                              chunk_type='ice')
                    # درع وهمي — نمنع ظهور نص SHIELD EQUIPED
                    self._fake_shield = True
                    if self.node:
                        bs.timer(0.1, babase.CallPartial(
                            self.node.handlemessage,
                            bs.PowerupMessage('shield')))
            elif self.shield_hitpoints > 575 / 2:
                self.shield_hitpoints = -1
                PopupText('i eat your shield!', position=pos,
                          random_offset=0.0, scale=2.0,
                          color=(0.0, 0.5, 1.0)).autoretain()
            else:
                self.node.handlemessage('knockout', 5000)
                PopupText('GoodNight!', position=pos,
                          random_offset=0.0, scale=2.0,
                          color=(0.0, 0.5, 1.0)).autoretain()

        elif ptype == 'stun_bombs':
            tex = factory.tex_stun_bombs
            self._flash_billboard(tex)
            try:
                pos = self.node.position
            except Exception:
                pos = (0.0, 1.0, 0.0)
            self.bomb_type = 'stun_bomb'
            t_ms = int(bs.time() * 1000)
            self.node.mini_billboard_2_texture    = tex
            self.node.mini_billboard_2_start_time = t_ms
            self.node.mini_billboard_2_end_time   = t_ms + POWERUP_WEAR_OFF_TIME
            def _stun_off(spaz: Any) -> None:
                if spaz.node and spaz.node.exists():
                    if spaz.bomb_type == 'stun_bomb':
                        if getattr(spaz, '_sticky_ice_active', False):
                            spaz.bomb_type = 'sticky_ice'
                        else:
                            prev = getattr(spaz, '_cp_prev_bomb', 'normal')
                            spaz.bomb_type = prev if prev else 'normal'
            self._stun_bomb_timer = bs.Timer(
                POWERUP_WEAR_OFF_TIME / 1000.0,
                babase.CallPartial(_stun_off, self))
            PopupText('STUN BOMBS EQUIPED', color=(0.8, 0.0, 1.0),
                      scale=1.2, position=pos).autoretain()

        elif ptype == 'tele_bomb':
            tex = factory.tex_tele_bomb
            self._flash_billboard(tex)
            try:
                pos = self.node.position
            except Exception:
                pos = (0.0, 1.0, 0.0)
            self._cp_custom = 'tele_bomb'
            self._cp_count  = 1
            self.bomb_count = 1
            _cp_update_counter(self)
            PopupText('TELE-BOMB EQUIPED', color=(0.8, 0.2, 1.0),
                      scale=1.2, position=pos).autoretain()

        elif ptype == 'ice_cube':
            try:
                pos = self.node.position
            except Exception:
                pos = (0.0, 1.0, 0.0)
            tex = factory.tex_ice_cube
            self._flash_billboard(tex)
            PopupText('ICE CUBE EQUIPED', color=(0.3, 0.8, 1.0),
                      scale=1.2, position=pos).autoretain()
            # نعطيه قنبلة واحدة gloo عبر _cp_custom
            self._cp_custom = 'ice_cube_bomb'
            self._cp_count  = 1
            _cp_update_counter(self)
            self.bomb_count = 1

        elif ptype == 'ice_man':
            # ice bombs + freeze punch + لون أزرق
            self.bomb_type    = 'ice_bubble'
            self.freeze_punch = True
            self._ice_man_active  = True
            # حفظ اللون الأصلي وتغييره للأزرق
            try:
                self._ice_man_orig_color = tuple(self.node.color)
                self.node.color = (0.0, 1.0, 4.0)
            except Exception:
                self._ice_man_orig_color = (1.0, 1.0, 1.0)
            tex = factory.tex_ice_man
            self._flash_billboard(tex)
            t_ms = int(bs.time() * 1000)
            self.node.mini_billboard_2_texture    = tex
            self.node.mini_billboard_2_start_time = t_ms
            self.node.mini_billboard_2_end_time   = t_ms + 17000
            def _ice_off(spaz: Any) -> None:
                if spaz.node and spaz.node.exists():
                    spaz.freeze_punch    = False
                    spaz._ice_man_active = False
                    if spaz.bomb_type in ('ice', 'ice_bubble'):
                        spaz.bomb_type = 'normal'
                    # إعادة اللون الأصلي
                    try:
                        orig = getattr(spaz, '_ice_man_orig_color', (1.0, 1.0, 1.0))
                        bs.animate_array(spaz.node, 'color', 3,
                                         {0.0: (0.0, 1.0, 4.0), 0.5: orig})
                    except Exception:
                        pass
                    PopupText('ICE MAN ENDED', color=(0, 0.8, 1), scale=1.2, position=spaz.node.position).autoretain()
            self._ice_man_timer = bs.Timer(17.0, babase.CallPartial(_ice_off, self))
            PopupText('ICE MAN EQUIPED', color=(0, 0.8, 1), scale=1.2, position=self.node.position).autoretain()


        elif ptype == 'character':
            import random as _r
            _CHARS = [
                {'name':'Zoe',
                 'ct':'zoeColor','cm':'zoeColorMask','style':'female',
                 'head':'zoeHead','uarm':'zoeUpperArm','torso':'zoeTorso',
                 'pelvis':'zoePelvis','farm':'zoeForeArm','hand':'zoeHand',
                 'uleg':'zoeUpperLeg','lleg':'zoeLowerLeg','toes':'zoeToes'},
                {'name':'Jack Morgan',
                 'ct':'jackColor','cm':'jackColorMask','style':'pirate',
                 'head':'jackHead','uarm':'jackUpperArm','torso':'jackTorso',
                 'pelvis':'kronkPelvis','farm':'jackForeArm','hand':'jackHand',
                 'uleg':'jackUpperLeg','lleg':'jackLowerLeg','toes':'jackToes'},
                {'name':'Mel',
                 'ct':'melColor','cm':'melColorMask','style':'mel',
                 'head':'melHead','uarm':'melUpperArm','torso':'melTorso',
                 'pelvis':'kronkPelvis','farm':'melForeArm','hand':'melHand',
                 'uleg':'melUpperLeg','lleg':'melLowerLeg','toes':'melToes'},
                {'name':'Frosty',
                 'ct':'frostyColor','cm':'frostyColorMask','style':'frosty',
                 'head':'frostyHead','uarm':'frostyUpperArm','torso':'frostyTorso',
                 'pelvis':'frostyPelvis','farm':'frostyForeArm','hand':'frostyHand',
                 'uleg':'frostyUpperLeg','lleg':'frostyLowerLeg','toes':'frostyToes'},
                {'name':'Santa',
                 'ct':'santaColor','cm':'santaColorMask','style':'santa',
                 'head':'santaHead','uarm':'santaUpperArm','torso':'santaTorso',
                 'pelvis':'kronkPelvis','farm':'santaForeArm','hand':'santaHand',
                 'uleg':'santaUpperLeg','lleg':'santaLowerLeg','toes':'santaToes'},
                {'name':'Cyborg',
                 'ct':'cyborgColor','cm':'cyborgColorMask','style':'cyborg',
                 'head':'cyborgHead','uarm':'cyborgUpperArm','torso':'cyborgTorso',
                 'pelvis':'cyborgPelvis','farm':'cyborgForeArm','hand':'cyborgHand',
                 'uleg':'cyborgUpperLeg','lleg':'cyborgLowerLeg','toes':'cyborgToes'},
                {'name':'Ninja',
                 'ct':'ninjaColor','cm':'ninjaColorMask','style':'ninja',
                 'head':'ninjaHead','uarm':'ninjaUpperArm','torso':'ninjaTorso',
                 'pelvis':'ninjaPelvis','farm':'ninjaForeArm','hand':'ninjaHand',
                 'uleg':'ninjaUpperLeg','lleg':'ninjaLowerLeg','toes':'ninjaToes'},
                {'name':'Bear',
                 'ct':'bearColor','cm':'bearColorMask','style':'bear',
                 'head':'bearHead','uarm':'bearUpperArm','torso':'bearTorso',
                 'pelvis':'bearPelvis','farm':'bearForeArm','hand':'bearHand',
                 'uleg':'bearUpperLeg','lleg':'bearLowerLeg','toes':'bearToes'},
                {'name':'Penguin',
                 'ct':'penguinColor','cm':'penguinColorMask','style':'penguin',
                 'head':'penguinHead','uarm':'penguinUpperArm','torso':'penguinTorso',
                 'pelvis':'penguinPelvis','farm':'penguinForeArm','hand':'penguinHand',
                 'uleg':'penguinUpperLeg','lleg':'penguinLowerLeg','toes':'penguinToes'},
                {'name':'Ali',
                 'ct':'aliColor','cm':'aliColorMask','style':'ali',
                 'head':'aliHead','uarm':'aliUpperArm','torso':'aliTorso',
                 'pelvis':'aliPelvis','farm':'aliForeArm','hand':'aliHand',
                 'uleg':'aliUpperLeg','lleg':'aliLowerLeg','toes':'aliToes'},
            ]
            try:
                char = _r.choice(_CHARS)
                node = self.node
                node.color_texture      = bs.gettexture(char['ct'])
                node.color_mask_texture = bs.gettexture(char['cm'])
                node.head_mesh          = bs.getmesh(char['head'])
                node.upper_arm_mesh     = bs.getmesh(char['uarm'])
                node.torso_mesh         = bs.getmesh(char['torso'])
                node.pelvis_mesh        = bs.getmesh(char['pelvis'])
                node.forearm_mesh       = bs.getmesh(char['farm'])
                node.hand_mesh          = bs.getmesh(char['hand'])
                node.upper_leg_mesh     = bs.getmesh(char['uleg'])
                node.lower_leg_mesh     = bs.getmesh(char['lleg'])
                node.toes_mesh          = bs.getmesh(char['toes'])
                # style يتحكم بالأصوات تلقائياً في اللعبة
                node.style = char['style']
                # العيون
                try:
                    node.eye_texture   = bs.gettexture('eyeColor')
                    node.eye_mesh      = bs.getmesh('eyeBall')
                    node.eye_iris_mesh = bs.getmesh('eyeBallIris')
                except Exception:
                    pass
                node.color     = (_r.random()*2, _r.random()*2, _r.random()*2)
                node.highlight = (_r.random()*2, _r.random()*2, _r.random()*2)
                PopupText(f'{char["name"].upper()} EQUIPED', color=(1, 0.8, 0.2),
                          scale=1.2, position=self.node.position).autoretain()
            except Exception as e:
                print(f'[character] error: {e}')
            tex = factory.tex_character
            self._flash_billboard(tex)
        elif ptype == 'invisible':
            n = self.node
            # حفظ الـ meshes الأصلية
            orig = {}
            mesh_attrs = [
                'head_mesh','torso_mesh','pelvis_mesh','upper_arm_mesh',
                'forearm_mesh','hand_mesh','upper_leg_mesh','lower_leg_mesh','toes_mesh',
                'eye_mesh','eye_iris_mesh','eye_texture','hair_mesh',
            ]
            for a in mesh_attrs:
                try: orig[a] = getattr(n, a)
                except Exception: orig[a] = None
            orig['name'] = n.name
            # إخفاء كل الـ meshes
            for a in mesh_attrs:
                try: setattr(n, a, None)
                except Exception: pass
            n.name = ''
            tex = factory.tex_invisible
            self._flash_billboard(tex)
            def _reveal(spaz: Any) -> None:
                if spaz.node and spaz.node.exists():
                    nd = spaz.node
                    for attr in mesh_attrs:
                        try: setattr(nd, attr, orig[attr])
                        except Exception: pass
                    nd.name = orig['name']
                    PopupText('INVISIBLE ENDED', color=(0.8, 0.8, 1), scale=1.2, position=spaz.node.position).autoretain()
            self._invisible_timer = bs.Timer(15.0, babase.CallPartial(_reveal, self))
            PopupText('INVISIBLE EQUIPED', color=(0.8, 0.8, 1), scale=1.2, position=self.node.position).autoretain()

        elif ptype == 'mag':
            _MagController(self.node)
            tex = factory.tex_mag
            self._flash_billboard(tex)
            PopupText('MAGNET EQUIPED', color=(0.5, 1, 1), scale=1.2, position=self.node.position).autoretain()

        elif ptype == 'speedBoots':
            try:
                self.node.hockey = True
                def _off(spaz: Any) -> None:
                    if spaz.node and spaz.node.exists():
                        spaz.node.hockey = False
                        PopupText('SPEED BOOTS ENDED', color=(1, 1, 0), scale=1.2, position=spaz.node.position).autoretain()
                self._speedboots_timer = bs.Timer(
                    20.0, babase.CallPartial(_off, self)
                )
            except Exception:
                pass
            tex = factory.tex_speedboots
            self._flash_billboard(tex)
            PopupText('SPEED BOOTS EQUIPED', color=(1, 1, 0), scale=1.2, position=self.node.position).autoretain()

        elif ptype == 'troll':
            # خدعة — يجمّد اللاعب ويضع عليه لعنة
            try:
                self.handlemessage(bs.FreezeMessage())
                self.handlemessage(bs.FreezeMessage())
                self.handlemessage(bs.PowerupMessage(poweruptype='curse'))
            except Exception:
                pass
            tex = factory.tex_troll
            self._flash_billboard(tex)
            PopupText('TROLL', color=(0, 1, 0), scale=1.2, position=self.node.position).autoretain()


        self.node.handlemessage('flash')
        if msg.sourcenode:
            msg.sourcenode.handlemessage(bs.PowerupAcceptMessage())
        return True



    # حصانة ice_man من التجمد فقط
    if isinstance(msg, bs.FreezeMessage):
        if getattr(self, '_ice_man_active', False):
            return None

    # freeze punch — يعمل مع اللاعبين والـ bots

    if isinstance(msg, bs.HitMessage) and msg.hit_type == 'punch':
        try:
            # محاولة الحصول على الضارب عبر source_player (لاعب بشري)
            attacker = None
            try:
                pl = msg.get_source_player(bs.Player)
                if pl and pl.actor:
                    attacker = pl.actor
            except Exception:
                pass
            if attacker is None:
                # bot — نحاول عبر source_player مباشرة
                try:
                    attacker = msg.source_player
                except Exception:
                    pass
            if attacker and getattr(attacker, 'freeze_punch', False):
                if self.node and self.node.exists():
                    self.node.color = (0.0, 1.0, 4.0)
                    self.node.handlemessage(bs.FreezeMessage())
        except Exception:
            pass

    return self._cp_old_hm(msg)


# ══════════════════════════════════════════════════════════════
#  Spaz._get_bomb_type_tex — نضيف textures للأنواع الجديدة
# ══════════════════════════════════════════════════════════════

Spaz._cp_old_get_tex = Spaz._get_bomb_type_tex


def _new_get_bomb_type_tex(self) -> babase.Texture:
    factory = NewPowerupBoxFactory.get()
    if self.bomb_type == 'headache':
        return factory.tex_headache
    if self.bomb_type == 'antigrav':
        return factory.tex_antigrav
    try:
        return self._cp_old_get_tex()
    except ValueError:
        return bs.gettexture('bombColor')


# ══════════════════════════════════════════════════════════════
#  Plugin
# ══════════════════════════════════════════════════════════════


# ══════════════════════════════════════════════════════════════
#  _PortalController
# ══════════════════════════════════════════════════════════════

_active_portals: list = []


class _PortalController:
    """بوابتان — scan كل 0.05s، ينقل spaz وقنابل، cooldown 2 ثانية."""

    RADIUS   = 1.8
    DURATION = 8.0

    def __init__(self) -> None:
        import random as _r
        self._pos1 = self._random_pos()
        self._pos2 = self._random_pos()
        self._cooldown: set = set()

        c1 = (_r.random()*2+0.5, _r.random()*0.2, _r.random()*2+1.5)
        c2 = (_r.random()*0.2,   _r.random()*2+1.0, _r.random()*2+0.5)

        self._shield1 = bs.newnode('shield', attrs={
            'position': self._pos1, 'color': c1, 'radius': 0.1,
        })
        self._shield2 = bs.newnode('shield', attrs={
            'position': self._pos2, 'color': c2, 'radius': 0.1,
        })
        bs.animate(self._shield1, 'radius', {0: 0.1, 0.5: self.RADIUS})
        bs.animate(self._shield2, 'radius', {0: 0.1, 0.5: self.RADIUS})
        bs.animate_array(self._shield1, 'color', 3,
            {0: c1, 1.0: (c1[2], c1[0], c1[1]), 2.0: c1}, loop=True)
        bs.animate_array(self._shield2, 'color', 3,
            {0: c2, 1.0: (c2[2], c2[0], c2[1]), 2.0: c2}, loop=True)

        self._scan_timer = bs.Timer(0.05, self._scan, repeat=True)
        self._end_timer  = bs.Timer(self.DURATION, self._cleanup)
        _active_portals.append(self)

    def _random_pos(self) -> tuple:
        import random as _r
        try:
            act = bs.getactivity()
            pts: list = []
            try:
                pts += list(act.map.ffa_spawn_points)
            except Exception:
                pass
            try:
                pts += list(act.map.powerup_spawn_points)
            except Exception:
                pass
            if pts:
                p = _r.choice(pts)
                return (float(p[0]), float(p[1]) + 1.0, float(p[2]))
        except Exception:
            pass
        return (_r.uniform(-4, 4), 1.5, _r.uniform(-4, 4))

    def _scan(self) -> None:
        r2 = self.RADIUS * self.RADIUS
        for node in bs.getnodes():
            if not node.exists():
                continue
            if node.getnodetype() not in ('spaz', 'prop', 'bomb'):
                continue
            if node in self._cooldown:
                continue
            try:
                p = node.position
                dx = p[0] - self._pos1[0]
                dy = p[1] - self._pos1[1]
                dz = p[2] - self._pos1[2]
                if dx*dx + dy*dy + dz*dz <= r2:
                    self._teleport(node, self._pos2)
                    continue
                dx = p[0] - self._pos2[0]
                dy = p[1] - self._pos2[1]
                dz = p[2] - self._pos2[2]
                if dx*dx + dy*dy + dz*dz <= r2:
                    self._teleport(node, self._pos1)
            except Exception:
                continue

    def _teleport(self, node: bs.Node, dest: tuple) -> None:
        self._cooldown.add(node)
        try:
            if node.getnodetype() == 'spaz':
                node.handlemessage(bs.StandMessage(position=dest, angle=0.0))
            elif node.getnodetype() == 'prop':
                # نستخدم move_to_position بدل position= مباشرة
                # حتى لا تنقطع connectattr للـ shield والنص
                try:
                    node.move_to_position = dest
                except Exception:
                    node.position = (dest[0], dest[1], dest[2])
                try:
                    v = node.velocity
                    node.velocity = (v[0], 0.0, v[2])
                except Exception:
                    pass
            else:
                node.position = (dest[0], dest[1], dest[2])
                try:
                    v = node.velocity
                    node.velocity = (v[0], 0.0, v[2])
                except Exception:
                    pass
        except Exception:
            pass
        bs.emitfx(position=dest, scale=1.5, count=15,
                  spread=0.5, chunk_type='spark')
        bs.timer(2.0, lambda: self._cooldown.discard(node))

    def _cleanup(self) -> None:
        self._scan_timer = None
        for n in (self._shield1, self._shield2):
            try:
                if n.exists():
                    n.delete()
            except Exception:
                pass
        try:
            _active_portals.remove(self)
        except ValueError:
            pass


# ══════════════════════════════════════════════════════════════
#  _BlackHoleController
# ══════════════════════════════════════════════════════════════

_active_blackholes: list = []


class _BlackHoleController:
    """Black Hole — region+material للالتقاط الفوري + timer للسحب المستمر."""

    SUCK_SCALE = 8.0
    KILL_SCALE = 1.5
    DURATION   = 20.0

    def __init__(self, position: tuple) -> None:
        import random as _r
        self.pos          = position
        self._suck_objects: list = []
        self.shields:       list = []

        shared = SharedObjects.get()

        # kill material — شرط بسيط بدون 'and'
        self._kill_mat = bs.Material()
        self._kill_mat.add_actions(
            conditions=('they_have_material', shared.player_material),
            actions=(
                ('modify_part_collision', 'collide',  True),
                ('modify_part_collision', 'physical', False),
                ('call', 'at_connect', self._touched_spaz),
            ),
        )
        self._kill_mat.add_actions(
            conditions=('they_have_material', shared.object_material),
            actions=(
                ('modify_part_collision', 'collide',  True),
                ('modify_part_collision', 'physical', False),
                ('call', 'at_connect', self._touched_obj),
            ),
        )

        # suck material
        self._suck_mat = bs.Material()
        self._suck_mat.add_actions(
            conditions=('they_have_material', shared.object_material),
            actions=(
                ('modify_part_collision', 'collide',  True),
                ('modify_part_collision', 'physical', False),
                ('call', 'at_connect', self._touched_suck),
            ),
        )

        # kill region
        self._kill_node = bs.newnode('region', attrs={
            'position':  position,
            'scale':     (self.KILL_SCALE,) * 3,
            'type':      'sphere',
            'materials': [self._kill_mat],
        })

        # suck region
        self._suck_node = bs.newnode('region', attrs={
            'position':  position,
            'scale':     (self.SUCK_SCALE,) * 3,
            'type':      'sphere',
            'materials': [self._suck_mat],
        })

        # 8 shields بألوان عشوائية
        for _ in range(8):
            sh = bs.newnode('shield', attrs={
                'color':    (_r.random()*2, _r.random()*2, _r.random()*2),
                'radius':   1.5,
                'position': position,
            })
            self.shields.append(sh)

        self._suck_timer = bs.Timer(0.05, self._do_suck, repeat=True)
        self._end_timer  = bs.Timer(self.DURATION, self._cleanup)
        _active_blackholes.append(self)

    def _touched_spaz(self) -> None:
        try:
            node = bs.getcollision().opposingnode
            if not node or not node.exists():
                return
            node.handlemessage(bs.HitMessage(
                pos=self.pos, velocity=(0, 0, 0),
                magnitude=2000, flat_damage=2000,
                hit_type='explosion', hit_subtype='normal',
                radius=1.0, source_player=None,
            ))
            node.handlemessage(bs.DieMessage())
            self._add_mass()
        except Exception:
            pass

    def _touched_obj(self) -> None:
        try:
            node = bs.getcollision().opposingnode
            if not node or not node.exists():
                return
            if node.getnodetype() == 'bomb':
                node.handlemessage(bs.ExplodeMessage())
            else:
                try:
                    bs.emitfx(position=node.position, scale=1.0,
                              count=8, spread=0.4, chunk_type='spark')
                except Exception:
                    pass
                node.handlemessage(bs.DieMessage())
        except Exception:
            pass

    def _touched_suck(self) -> None:
        try:
            node = bs.getcollision().opposingnode
            if not node or not node.exists():
                return
            if node not in self._suck_objects:
                self._suck_objects.append(node)
            for nd in self._suck_objects:
                try:
                    if nd.exists():
                        dx = self.pos[0] - nd.position[0]
                        dy = self.pos[1] - nd.position[1]
                        dz = self.pos[2] - nd.position[2]
                        nd.extra_acceleration = (dx * 8, dy * 25, dz * 8)
                except Exception:
                    pass
        except Exception:
            pass

    def _do_suck(self) -> None:
        dead = []
        for nd in self._suck_objects:
            try:
                if not nd.exists():
                    dead.append(nd)
                    continue
                dx = self.pos[0] - nd.position[0]
                dy = self.pos[1] - nd.position[1]
                dz = self.pos[2] - nd.position[2]
                nd.extra_acceleration = (dx * 8, dy * 25, dz * 8)
            except Exception:
                dead.append(nd)
        for nd in dead:
            try: self._suck_objects.remove(nd)
            except ValueError: pass

    def _add_mass(self) -> None:
        import random as _r
        sh = bs.newnode('shield', attrs={
            'color':    (_r.random()*2, _r.random()*2, _r.random()*2),
            'radius':   1.5,
            'position': self.pos,
        })
        self.shields.append(sh)

    def _cleanup(self) -> None:
        try: bs.getsound('explosion01').play(position=self.pos)
        except Exception: pass
        try:
            bs.emitfx(position=self.pos, scale=3, count=80,
                      spread=2.5, chunk_type='spark')
        except Exception: pass
        try:
            kr2 = 4.0 * 4.0
            px, py, pz = self.pos
            for node in list(bs.getnodes()):
                try:
                    if not node.exists() or node.getnodetype() != 'spaz':
                        continue
                    p = node.position
                    dx = p[0]-px; dy = p[1]-py; dz = p[2]-pz
                    if dx*dx + dy*dy + dz*dz < kr2:
                        node.handlemessage(bs.HitMessage(
                            pos=self.pos, velocity=(0, 0, 0),
                            magnitude=3000, flat_damage=3000,
                            hit_type='explosion', hit_subtype='normal',
                            radius=4.0, source_player=None,
                        ))
                except Exception: continue
        except Exception: pass
        for n in (self._kill_node, self._suck_node):
            try:
                if n.exists(): n.delete()
            except Exception: pass
        for sh in self.shields:
            try:
                if sh.exists(): sh.delete()
            except Exception: pass
        self.shields.clear()
        self._suck_timer = None
        self._suck_objects.clear()
        try: _active_blackholes.remove(self)
        except ValueError: pass


_active_mags: list = []


class _MagController:
    """يجذب كل props قريبة نحو اللاعب — scan كل 0.05s لمدة 20 ثانية."""

    RADIUS    = 10.0   # نصف قطر الجذب
    STRENGTH  = 8.0    # قوة الجذب
    DURATION  = 20.0

    def __init__(self, owner_node: bs.Node) -> None:
        self._owner = owner_node
        self._attracted: set = set()

        self._scan_timer = bs.Timer(0.05, self._scan, repeat=True)
        self._end_timer  = bs.Timer(self.DURATION, self._cleanup)
        _active_mags.append(self)

    def _scan(self) -> None:
        if not self._owner.exists():
            self._cleanup()
            return

        opos = self._owner.position
        r2   = self.RADIUS * self.RADIUS

        # إيقاف الجذب عن props خرجت من النطاق
        lost = set()
        for node in self._attracted:
            if not node.exists():
                lost.add(node)
                continue
            p  = node.position
            dx = p[0] - opos[0]
            dy = p[1] - opos[1]
            dz = p[2] - opos[2]
            if dx*dx + dy*dy + dz*dz > r2 * 4:
                try:
                    node.extra_acceleration = (0.0, 0.0, 0.0)
                except Exception:
                    pass
                lost.add(node)
        self._attracted -= lost

        # جذب props جديدة داخل النطاق
        for node in bs.getnodes():
            if not node.exists():
                continue
            if node.getnodetype() not in ('prop', 'bomb'):
                continue
            if node is self._owner:
                continue
            try:
                p  = node.position
                dx = opos[0] - p[0]
                dy = opos[1] - p[1]
                dz = opos[2] - p[2]
                if dx*dx + dy*dy + dz*dz <= r2:
                    node.extra_acceleration = (
                        dx * self.STRENGTH,
                        dy * self.STRENGTH,
                        dz * self.STRENGTH,
                    )
                    self._attracted.add(node)
            except Exception:
                continue

    def _cleanup(self) -> None:
        self._scan_timer = None
        # نوقف الجذب عن كل الـ nodes
        for node in self._attracted:
            try:
                if node.exists():
                    node.extra_acceleration = (0.0, 0.0, 0.0)
            except Exception:
                pass
        self._attracted.clear()
        try:
            _active_mags.remove(self)
        except ValueError:
            pass



# ══════════════════════════════════════════════════════════════


def enable() -> None:
    """تفعيل ATD Powerups — يُستدعى من bootstraping()."""
    pupbox.PowerupBoxFactory   = NewPowerupBoxFactory
    pupbox.PowerupBox.__init__ = _pbx_
    Bomb._cp_old_bomb          = Bomb.__init__
    Bomb.__init__              = _bomb_init
    Bomb._cp_old_bomb_hm       = Bomb.handlemessage
    Bomb.handlemessage         = _new_bomb_hm
    Spaz._cp_old_hm            = Spaz.handlemessage
    Spaz.handlemessage         = new_handlemessage
    Spaz._get_bomb_type_tex    = _new_get_bomb_type_tex

    # ── patch drop_bomb: منع تحويل impact إلى land_mine للقنابل المخصصة ──
    Spaz._cp_old_drop_bomb = Spaz.drop_bomb

    def _cp_drop_bomb(self) -> Any:
        cp = getattr(self, '_cp_custom', None)
        if cp in _CUSTOM_BOMB_REAL_TYPE and _CUSTOM_BOMB_REAL_TYPE[cp] == 'impact' and cp != 'antigrav':
            orig = self.bomb_type
            self.bomb_type = 'normal'
            result = self._cp_old_drop_bomb()
            self.bomb_type = orig
            return result
        return self._cp_old_drop_bomb()

    Spaz.drop_bomb = _cp_drop_bomb


