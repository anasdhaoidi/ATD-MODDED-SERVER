# ba_meta require api 9

from __future__ import annotations
from typing import TYPE_CHECKING

import babase
import bauiv1 as bui
import bascenev1 as bs
from bascenev1lib.actor.spaz import Spaz

if TYPE_CHECKING:
    pass

####################################

first_damage  = (u'ARE YOU BLIND?', (1, 1, 1),    '6')
second_damage = (u'GOOD!',       (0, 1, 1),    '2')
third_damage  = (u'DAMN!',       (0.8, 0.4, 1),'3')
fourth_damage = (u'SRY NOOB',        (1, 1, 0),    '4')
five_damage   = (u'FAH!!!',      (1, 0, 0),    '5')


def custom_effects(pos: float, effect: str = None) -> None:
    if effect == '1':
        bs.emitfx(position=pos, count=3,  scale=0.1, spread=0.1, chunk_type='rock')
    elif effect == '2':
        bs.emitfx(position=pos, count=70, scale=2,   spread=0.8, chunk_type='spark')
    elif effect == '3':
        bs.emitfx(position=pos, count=6,  scale=0.3, spread=0.4, chunk_type='splinter')
    elif effect == '4':
        bs.emitfx(position=pos, count=50, scale=3.0, spread=0.9, chunk_type='ice')
    elif effect == '5':
        bs.emitfx(position=pos, count=80, scale=3.0, spread=1.5, chunk_type='metal')
    elif effect == '6':
        bs.emitfx(position=pos, count=30, scale=1.2, spread=0.8, chunk_type='slime')


def on_punched(self, damage: int) -> None:
    pos = self.node.position

    def custom_text(msg: str, color: float) -> None:
        text = bs.newnode('text', attrs={
            'text': msg,
            'color': color,
            'in_world': True,
            'h_align': 'center',
            'shadow': 0.5,
            'flatness': 1.0,
        })
        bs.animate_array(text, 'position', 3, {
            0.0: (pos[0], pos[1] + 1.2, pos[2]),
            2.0: (pos[0], pos[1] + 1.7, pos[2]),
        })
        bs.animate(text, 'opacity', {0.8: 1.0, 2.0: 0.0})
        bs.animate(text, 'scale', {0: 0, 0.1: 0.017, 0.15: 0.014, 2.0: 0.016})
        bs.timer(2.0, text.delete)

    if damage < 200:
        custom_text(first_damage[0], first_damage[1])
        custom_effects(pos, first_damage[2])
    elif damage < 500:
        custom_text(second_damage[0], second_damage[1])
        custom_effects(pos, second_damage[2])
    elif damage < 800:
        custom_text(third_damage[0], third_damage[1])
        custom_effects(pos, third_damage[2])
    elif damage < 1000:
        custom_text(fourth_damage[0], fourth_damage[1])
        custom_effects(pos, fourth_damage[2])
    else:
        custom_text(five_damage[0], five_damage[1])
        custom_effects(pos, five_damage[2])


def enable() -> None:
    """تفعيل ATD Hits — يُستدعى من bootstraping()."""
    Spaz.on_punched = on_punched
    try:
        from bascenev1lib.actor.spazbot import SpazBot
        SpazBot.on_punched = on_punched
    except Exception:
        pass
    bs.broadcastmessage(u' || WELCOME ATD || ', color=(0, 1, 0))
