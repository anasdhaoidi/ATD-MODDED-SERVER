from bascenev1lib.actor.playerspaz import *
import babase
import bauiv1 as bui
import bascenev1 as bs
import bascenev1lib
from bascenev1lib.actor.spazfactory import SpazFactory
import functools
import random
from typing import List, Sequence, Optional, Dict, Any
import setting
from playersdata import pdata
from stats import mystats
_settings = setting.get_settings_data()

RANK_EFFECT_MAP = {
    1: ["fairydust"],
    2: ["sweat"],
    3: ["metal"],
    4: ["iceground"],
    5: ["slime"],
}
def effect(repeat_interval=0):
    def _activator(method):
        @functools.wraps(method)
        def _inner_activator(self, *args, **kwargs):
            def _caller():
                try:
                    method(self, *args, **kwargs)
                except:
                    if self is None or not self.is_alive() or not self.node.exists():
                        self._activations = []
                    else:
                        raise
            effect_activation = bs.Timer(repeat_interval, babase.CallPartial(_caller), repeat=repeat_interval > 0)
            self._activations.append(effect_activation)
        return _inner_activator
    return _activator


def node(check_interval=0):
    def _activator(method):
        @functools.wraps(method)
        def _inner_activator(self):
            node = method(self)
            def _caller():
                if self is None or not self.is_alive() or not self.node.exists():
                    node.delete()
                    self._activations = []
            node_activation = bs.Timer(check_interval, babase.CallStrict(_caller), repeat=check_interval > 0)
            try:
                self._activations.append(node_activation)
            except AttributeError:
                pass
        return _inner_activator
    return _activator


class NewPlayerSpaz(PlayerSpaz):
    def __init__(self,
                 player: bs.Player,
                 color: Sequence[float],
                 highlight: Sequence[float],
                 character: str,
                 powerups_expire: bool = True,
                 *args,
                 **kwargs):

        super().__init__(player=player,
                         color=color,
                         highlight=highlight,
                         character=character,
                         powerups_expire=powerups_expire,
                         *args,
                         **kwargs)
        self._activations = []
        self.effects = []
        self.death_effects = []  # تُشغَّل عند الموت

        babase._asyncio._g_asyncio_event_loop.create_task(self.set_effects())

    async def set_effects(self):
        account_id = self._player._sessionplayer.get_account_id()
        custom_effects = pdata.get_custom()['customeffects']
        paid_effects   = pdata.get_custom().get('paideffects', {})

        # paid effects أولاً (مشتراة بالعملات) مع فحص الصلاحية
        if account_id in paid_effects:
            try:
                from datetime import datetime as _dt
                expiry = _dt.strptime(paid_effects[account_id]['expiry'], '%d-%m-%Y %H:%M:%S')
                if _dt.now() < expiry:
                    e = paid_effects[account_id]['effect']
                    self.effects = [e] if isinstance(e, str) else e
                else:
                    # انتهت الصلاحية — احذفه تلقائياً
                    del paid_effects[account_id]
                    pdata.get_custom()['paideffects'] = paid_effects
                    pdata.dump_cache()
            except Exception:
                pass

        if not self.effects and account_id in custom_effects:
            self.effects = [custom_effects[account_id]] if type(custom_effects[account_id]) is str else custom_effects[account_id]

        if not self.effects:
            #  check if we have any effect for his rank.
            if _settings['enablestats']:
                stats = mystats.get_cached_stats()
                if account_id in stats and _settings['enableTop5effects']:
                    rank = stats[account_id]["rank"]
                    self.effects = RANK_EFFECT_MAP[rank] if rank in RANK_EFFECT_MAP else []



        # levitate و circle_explode لكل اللاعبين دائماً عند الموت
        self.death_effects = ['circle_explode']

        if len(self.effects) == 0:
            return

        self._effect_mappings = {
            "spark": self._add_spark,
            "sparkground": self._add_sparkground,
            "sweat": self._add_sweat,
            "sweatground": self._add_sweatground,
            "distortion": self._add_distortion,
            "glow": self._add_glow,
            "shine": self._add_shine,
            "highlightshine": self._add_highlightshine,
            "scorch": self._add_scorch,
            "ice": self._add_ice,
            "iceground": self._add_iceground,
            "slime": self._add_slime,
            "metal": self._add_metal,
            "splinter": self._add_splinter,
            "rainbow": self._add_rainbow,
            "fairydust": self._add_fairydust,
            "noeffect": lambda: None,
            "fire":self._add_fire,
            "stars":self._add_stars,
            "new_rainbow":self._add_new_rainbow,
            "footprint": self._add_footprint,
            "chispitas": self._add_chispitas,
            "darkmagic": self._add_darkmagic,
            "colorfullspark": self._add_colorful_spark,
            "ring": self._add_aure,
            "brust": self._add_galactic_burst,
            "ringstars": self._add_star_ring,
            "dotted_trail": self._add_dotted_trail,
            "rolling_heads": self._add_rolling_heads,
            "orbit_stars": self._add_orbit_stars,
            "orbit_shield": self._add_orbit_shield,
            "bubbles": self._add_bubbles,
            "electric_ring": self._add_electric_ring,
        }

        for effect in self.effects:
            trigger = self._effect_mappings[effect] if effect in self._effect_mappings else lambda: None
            activity = self._activity()
            if activity:
                with activity.context:
                  trigger()

    @effect(repeat_interval=0.1)
    def _add_spark(self):
        bs.emitfx(
            position=self.node.position,
            velocity=self.node.velocity,
            count=random.randint(1, 10),
            scale=0.5,
            spread=0.2,
            chunk_type="spark",
        )


    @effect(repeat_interval=0.1)
    def _add_sparkground(self):
        bs.emitfx(
            position=self.node.position,
            velocity=self.node.velocity,
            count=random.randint(1, 5),
            scale=0.2,
            spread=0.1,
            chunk_type="spark",
            emit_type="stickers",
        )

    @effect(repeat_interval=0.04)
    def _add_sweat(self):
        velocity = 4.0
        calculate_position = lambda torso_position: torso_position - 0.25 + random.uniform(0, 0.5)
        calculate_velocity = lambda node_velocity, multiplier: random.uniform(-velocity, velocity) + node_velocity * multiplier
        position = tuple(calculate_position(coordinate)
                         for coordinate in self.node.torso_position)
        velocity = (
            calculate_velocity(self.node.velocity[0], 2),
            calculate_velocity(self.node.velocity[1], 4),
            calculate_velocity(self.node.velocity[2], 2),
        )
        bs.emitfx(
            position=position,
            velocity=velocity,
            count=10,
            scale=random.uniform(0.3, 1.4),
            spread=0.2,
            chunk_type="sweat",
        )

    @effect(repeat_interval=0.04)
    def _add_sweatground(self):
        velocity = 1.2
        calculate_position = lambda torso_position: torso_position - 0.25 + random.uniform(0, 0.5)
        calculate_velocity = lambda node_velocity, multiplier: random.uniform(-velocity, velocity) + node_velocity * multiplier
        position = tuple(calculate_position(coordinate)
                         for coordinate in self.node.torso_position)
        velocity = (
            calculate_velocity(self.node.velocity[0], 2),
            calculate_velocity(self.node.velocity[1], 4),
            calculate_velocity(self.node.velocity[2], 2),
        )
        bs.emitfx(
            position=position,
            velocity=velocity,
            count=10,
            scale=random.uniform(0.1, 1.2),
            spread=0.1,
            chunk_type="sweat",
            emit_type="stickers",
        )

    @effect(repeat_interval=1.0)
    def _add_distortion(self):
        bs.emitfx(
            position=self.node.position,
            spread=1.0,
            emit_type="distortion"
        )
        bs.emitfx(
            position=self.node.position,
            velocity=self.node.velocity,
            count=random.randint(1, 5),
            emit_type="tendrils",
            tendril_type="smoke",
        )

    @effect(repeat_interval=3.0)
    def _add_shine(self):
        shine_factor = 1.2
        dim_factor = 0.90

        default_color = self.node.color
        shiny_color = tuple(channel * shine_factor for channel in default_color)
        dimmy_color = tuple(channel * dim_factor for channel in default_color)
        animation = {
            0: default_color,
            1: dimmy_color,
            2: shiny_color,
            3: default_color,
        }
        bs.animate_array(self.node, "color", 3, animation)

    @effect(repeat_interval=9.0)
    def _add_highlightshine(self):
        shine_factor = 1.2
        dim_factor = 0.90

        default_highlight = self.node.highlight
        shiny_highlight = tuple(channel * shine_factor for channel in default_highlight)
        dimmy_highlight = tuple(channel * dim_factor for channel in default_highlight)
        animation = {
            0: default_highlight,
            3: dimmy_highlight,
            6: shiny_highlight,
            9: default_highlight,
        }
        bs.animate_array(self.node, "highlight", 3, animation)

    @effect(repeat_interval=4.0)
    def _add_rainbow(self):
    # Increase intensity by multiplying each component by a factor
        intensity_factor = 8.0
        highlight = tuple(component * intensity_factor for component in (random.random() for _ in range(3)))
    
    # Ensure the values are within the valid color range
        highlight = babase.safecolor(highlight)

        animation = {
            0: (1,0,0),
            1: (0,1,0),
            2: (1,0,1),
            3: (0,1,1),
            4: (1,0,0),
        }
        bs.animate_array(self.node, "color", 3, animation, loop=True)


    @node(check_interval=0.5)
    def _add_glow(self):
        glowing_light = bs.newnode(
            "light",
            attrs={
                "color": (1.0, 0.4, 0.5),
                "height_attenuated": False,
                "radius": 0.4}
            )
        self.node.connectattr("position", glowing_light, "position")
        bs.animate(
            glowing_light,
            "intensity",
            {0: 0.0, 1: 0.2, 2: 0.0},
            loop=True)
        return glowing_light

    @node(check_interval=0.5)
    def _add_scorch(self):
        scorcher = bs.newnode(
            "scorch",
            attrs={
                "position": self.node.position,
                "size": 1.00,
                "big": True}
            )
        self.node.connectattr("position", scorcher, "position")
        animation = {
            0: (1,0,0),
            1: (0,1,0),
            2: (1,0,1),
            3: (0,1,1),
            4: (1,0,0),
        }
        bs.animate_array(scorcher, "color", 3, animation, loop=True)
        return scorcher

    @effect(repeat_interval=0.5)
    def _add_ice(self):
        bs.emitfx(
            position=self.node.position,
            velocity=self.node.velocity,
            count=random.randint(2, 8),
            scale=0.4,
            spread=0.2,
            chunk_type="ice",
        )

    @effect(repeat_interval=0.05)
    def _add_iceground(self):
        bs.emitfx(
            position=self.node.position,
            velocity=self.node.velocity,
            count=random.randint(1, 2),
            scale=random.uniform(0, 0.5),
            spread=1.0,
            chunk_type="ice",
            emit_type="stickers",
        )


    @effect(repeat_interval=0.25)
    def _add_slime(self):
        bs.emitfx(
            position=self.node.position,
            velocity=self.node.velocity,
            count=random.randint(1, 10),
            scale=0.4,
            spread=0.2,
            chunk_type="slime",
        )


    @effect(repeat_interval=0.25)
    def _add_metal(self):
        bs.emitfx(
            position=self.node.position,
            velocity=self.node.velocity,
            count=random.randint(1, 4),
            scale=0.4,
            spread=1,
            chunk_type="metal",
        )


    @effect(repeat_interval=0.75)
    def _add_splinter(self):
        bs.emitfx(
            position=self.node.position,
            velocity=self.node.velocity,
            count=random.randint(1, 5),
            scale=0.5,
            spread=0.2,
            chunk_type="splinter",
        )


    @effect(repeat_interval=0.001)
    def _add_fairydust(self):
        velocity = 2
        calculate_position = lambda torso_position: torso_position - 0.25 + random.uniform(0, 0.5)
        calculate_velocity = lambda node_velocity, multiplier: random.uniform(-velocity, velocity) + node_velocity * multiplier
        position = tuple(calculate_position(coordinate) for coordinate in self.node.torso_position)
        velocity = (
                    calculate_velocity(self.node.velocity[0], 6),
                    calculate_velocity(self.node.velocity[1], 8),
                    calculate_velocity(self.node.velocity[2], 8),
    )
        bs.emitfx(
                position=position,
                velocity=velocity,
                count=random.randint(100,200),
                spread=8.5,
                emit_type="fairydust",
    )
    
    
    @effect(repeat_interval=0.1)
    def _add_fire(self) -> None:
        if not self.node.exists():
            self._cm_effect_timer = None
        else:
            bs.emitfx(position=self.node.position,
            scale=3,count=50*2,spread=0.3,
            chunk_type='sweat')


    @effect(repeat_interval=0.1)
    def _add_stars(self) -> None:
        def die(node: bs.Node) -> None:
            if node:
                m = node.mesh_scale
                bs.animate(node, 'mesh_scale', {0: m, 0.1: 0})
                bs.timer(0.1, node.delete)

        if not self.node.exists() or self._dead:
            self._cm_effect_timer = None
        else:
            c = 0.3
            pos_list = [
                (c, 0, 0), (0, 0, c),
                (-c, 0, 0), (0, 0, -c)]
            
            for p in pos_list:
                m= 1.5
                np = self.node.position
                pos = (np[0]+p[0], np[1]+p[1]+0.0, np[2]+p[2])
                vel = (random.uniform(-m, m), random.uniform(2, 7), random.uniform(-m, m))

                texs = ['bombStickyColor', 'aliColor', 'aliColorMask', 'eggTex3']
                tex = bs.gettexture(random.choice(texs))
                mesh = bs.getmesh('flash')
                factory = SpazFactory.get()

                mat = bs.Material()
                mat.add_actions(
                    conditions=('they_have_material', factory.punch_material),
                    actions=(
                        ('modify_part_collision', 'collide', False),
                        ('modify_part_collision', 'physical', False),
                    ))
                node = bs.newnode('prop',
                                owner=self.node,
                                attrs={'body': 'sphere',
                                       'position': pos,
                                        'velocity': vel,
                                        'mesh': mesh,
                                        'mesh_scale': 0.1,
                                        'body_scale': 0.0,
                                        'shadow_size': 0.0,
                                        'gravity_scale': 0.5,
                                        'color_texture': tex,
                                        'reflection': 'soft',
                                        'reflection_scale': [1.5],
                                        'materials': [mat]})
                light = bs.newnode('light',
                                   owner=node,
                                   attrs={
                                       'intensity': 0.3,
                                       'volume_intensity_scale': 0.5,
                                       'color': (random.uniform(0.5, 1.5),
                                                 random.uniform(0.5, 1.5),
                                                 random.uniform(0.5, 1.5)),
                                        'radius': 0.035})
                node.connectattr('position', light, 'position')
                bs.timer(0.25, babase.CallPartial(die, node))


    @effect(repeat_interval=1.2)   
    def _add_new_rainbow(self) -> None:
        animate = {
             0.0: (4.5, 0.5, 0.5),
             0.2: (4.5, 2.8, 0.8),
             0.4: (4.5, 4.5, 0.5),
             0.6: (0.5, 4.5, 0.5),
             0.8: (0.5, 4.5, 4.5),
             1.0: (0.5, 0.5, 4.5)
        }
        keys = {
             0.0: (4.5, 0.5, 0.5),
             0.2: (4.5, 2.8, 0.8),
             0.4: (4.5, 4.5, 0.5),
             0.6: (0.5, 4.5, 0.5),
             0.8: (0.5, 4.5, 4.5),
             1.0: (0.5, 0.5, 4.5),
            }.items()
        
        def _changecolor(color: Sequence[float]) -> None:
            if self.node.exists():
                self.node.color = color

        for time, color in keys:
            bs.animate_array(self.node, "highlight", 3, animate, loop=True)
            bs.timer(time, babase.CallPartial(_changecolor, color))
  
   
    @effect(repeat_interval=0.15)   
    def _add_footprint(self) -> None:
        if not self.node.exists():
            self._cm_effect_timer = None
        else:
            loc = bs.newnode('locator', owner=self.node,
              attrs={
                     'position': self.node.position,
                     'shape': 'circle',
                     'color': (random.uniform(0.5, 1.5),
                               random.uniform(0.5, 1.5),
                               random.uniform(0.5, 1.5)),
                     'size': [0.2],
                     'draw_beauty': False,
                     'additive': False})
            bs.animate(loc, 'opacity', {0: 1.0, 1.9: 0.0})
            bs.timer(2.0, loc.delete)


    @effect(repeat_interval=0.1)
    def _add_chispitas(self) -> None:
        def die(node: bs.Node) -> None:
            if node:
                m = node.mesh_scale
                bs.animate(node, 'mesh_scale', {0: m, 0.1: 0})
                bs.timer(0.1, node.delete)

        if not self.node.exists() or self._dead:
            self._cm_effect_timer = None
        else:
            c = 0.3
            pos_list = [
                (c, 0, 0), (0, 0, c),
                (-c, 0, 0), (0, 0, -c)]
            
            for p in pos_list:
                m= 1.5
                np = self.node.position
                pos = (np[0]+p[0], np[1]+p[1]+0.0, np[2]+p[2])
                vel = (random.uniform(-m, m), random.uniform(2, 7), random.uniform(-m, m))

                tex = bs.gettexture('null')
                mesh = None
                factory = SpazFactory.get()

                mat = bs.Material()
                mat.add_actions(
                    conditions=('they_have_material', factory.punch_material),
                    actions=(
                        ('modify_part_collision', 'collide', False),
                        ('modify_part_collision', 'physical', False),
                    ))
                node = bs.newnode('bomb',
                                owner=self.node,
                                attrs={'body': 'sphere',
                                       'position': pos,
                                        'velocity': vel,
                                        'mesh': mesh,
                                        'mesh_scale': 0.1,
                                        'body_scale': 0.0,
                                        'color_texture': tex,
                                        'fuse_length': 0.1,
                                        'materials': [mat]})
                light = bs.newnode('light',
                                   owner=node,
                                   attrs={
                                       'intensity': 0.2,
                                       'volume_intensity_scale': 0.4,
                                       'color': (random.uniform(0.5, 1.5),
                                                 random.uniform(0.5, 1.5),
                                                 random.uniform(0.5, 1.5)),
                                        'radius': 0.025})
                node.connectattr('position', light, 'position')
                bs.timer(0.25, babase.CallPartial(die, node)) 



    @effect(repeat_interval=0.2)
    def _add_darkmagic(self) -> None:
        def die(node: bs.Node) -> None:
            if node:
                m = node.mesh_scale
                bs.animate(node, 'mesh_scale', {0: m, 0.1: 0})
                bs.timer(0.1, node.delete)

        if not self.node.exists() or self._dead:
            self._cm_effect_timer = None
        else:
            c = 0.3
            pos_list = [
                (c, 0, 0), (0, 0, c),
                (-c, 0, 0), (0, 0, -c)]
            
            for p in pos_list:
                m= 1.5
                np = self.node.position
                pos = (np[0]+p[0], np[1]+p[1]+0.0, np[2]+p[2])
                vel = (random.uniform(-m, m), 30.0, random.uniform(-m, m))

                tex = bs.gettexture('impactBombColor')
                mesh = bs.getmesh('impactBomb')
                factory = SpazFactory.get()

                mat = bs.Material()
                mat.add_actions(
                    conditions=('they_have_material', factory.punch_material),
                    actions=(
                        ('modify_part_collision', 'collide', False),
                        ('modify_part_collision', 'physical', False),
                    ))
                node = bs.newnode('prop',
                                owner=self.node,
                                attrs={'body': 'sphere',
                                       'position': pos,
                                        'velocity': vel,
                                        'mesh': mesh,
                                        'mesh_scale': 0.4,
                                        'body_scale': 0.0,
                                        'shadow_size': 0.0,
                                        'gravity_scale': 0.5,
                                        'color_texture': tex,
                                        'reflection': 'soft',
                                        'reflection_scale': [0.0],
                                        'materials': [mat]})
                light = bs.newnode('light',
                                   owner=node,
                                   attrs={
                                       'intensity': 0.8,
                                       'volume_intensity_scale': 0.5,
                                       'color': (0.5, 0.0, 1.0),
                                       'radius': 0.035})
                node.connectattr('position', light, 'position')
                bs.timer(0.25, babase.CallPartial(die, node)) 


    def _add_aure(self) -> None:
        def anim(node: bs.Node) -> None:
            bs.animate_array(node, 'color', 3,
                {0: (1,1,0), 0.1: (0,1,0),
                 0.2: (1,0,0), 0.3: (0,0.5,1),
                 0.4: (1,0,1)}, loop=True)
            bs.animate_array(node, 'size', 1,
                {0: [1.0], 0.2: [1.5], 0.3: [1.0]}, loop=True)

        attrs = ['torso_position', 'position_center', 'position']
        for i, pos in enumerate(attrs):
            loc = bs.newnode('locator', owner=self.node,
                  attrs={'shape': 'circleOutline',
                         'color': self.node.color,
                         'opacity': 1.0,
                         'draw_beauty': True,
                         'additive': False})
            self.node.connectattr(pos, loc, 'position')
            bs.timer(0.1 * i, babase.CallPartial(anim, loc))


    def _add_galactic_burst(self) -> None:
        self._add_new_rainbow()
        self._add_fairydust()

 
    def _add_colorful_spark(self) -> None:
        self._add_spark()
        self._add_sweatground()
        self._add_new_rainbow()


    def _add_star_ring(self) -> None:
        self._add_fairydust()
        self._add_aure()


    def handlemessage(self, msg) -> None:
        """نعترض DieMessage لتشغيل death effects."""
        if isinstance(msg, bs.DieMessage):
            try:
                activity = self._activity()
                if activity and self.node and self.node.exists():
                    pos = self.node.position
                    color = tuple(self.node.color)
                    with activity.context:
                        # circle_explode
                        ring = bs.newnode('locator',
                            attrs={
                                'shape':       'circleOutline',
                                'position':    pos,
                                'color':       color,
                                'opacity':     1.0,
                                'draw_beauty': True,
                                'additive':    True,
                            })
                        bs.animate_array(ring, 'size', 1,
                                         {0: [0.0], 0.7: [100.0]})
                        bs.animate(ring, 'opacity', {0: 1, 0.6: 0})
                        bs.timer(0.7, ring.delete)
            except Exception:
                pass
        super().handlemessage(msg)

    def _add_dotted_trail(self) -> None:
        """أثر نقاط خلف اللاعب — فقط للأوامر أو من يملك role."""
        if not self.node.exists():
            return
        self._fx_last_pos = self.node.position

        def _path_tick() -> None:
            try:
                if not self.is_alive() or not self.node.exists():
                    return
                p  = self.node.position
                p2 = self._fx_last_pos
                diff = bs.Vec3(p[0] - p2[0], 0.0, p[2] - p2[2])
                if diff.length() > 0.2:
                    color = tuple(self.node.color)
                    dot = bs.newnode('locator', attrs={
                        'shape':       'circle',
                        'position':    p,
                        'color':       color,
                        'opacity':     1.0,
                        'draw_beauty': False,
                        'additive':    False,
                        'size':        [0.2],
                    })
                    bs.animate_array(dot, 'size', 1,
                                     {0: [0.2], 2.5: [0.2], 3.0: [0.0]})
                    bs.timer(3.0, dot.delete)
                    self._fx_last_pos = self.node.position
            except Exception:
                pass

        timer = bs.Timer(0.2, babase.CallPartial(_path_tick), repeat=True)
        self._activations.append(timer)


    def _add_rolling_heads(self) -> None:
        """ثلاثة رؤوس (Alien, Skull, Cyborg) تدور حول اللاعب."""
        import math as _math

        HEADS = [
            {'mesh': 'aliHead',     'tex': 'aliColor'},
            {'mesh': 'cyborgHead',  'tex': 'cyborgColor', 'color': None},
            {'mesh': 'bonesHead',   'tex': 'bonesColor',  'color': None},
        ]
        RADIUS   = 0.7   # نصف قطر الدوران
        SPEED    = 2.5   # سرعة الدوران (ثانية لدورة كاملة)
        Y_OFFSET = 0.6   # الارتفاع فوق اللاعب

        head_nodes = []
        shared = None
        try:
            from bascenev1lib.gameutils import SharedObjects
            shared = SharedObjects.get()
        except Exception:
            pass

        for i, h in enumerate(HEADS):
            try:
                mat = bs.Material()
                mat.add_actions(actions=(
                    ('modify_part_collision', 'collide', False),
                    ('modify_part_collision', 'physical', False),
                ))
                mats = [mat]
                if shared:
                    mats.append(shared.object_material)

                node_attrs = {
                    'mesh':          bs.getmesh(h['mesh']),
                    'color_texture': bs.gettexture(h['tex']),
                    'body':          'sphere',
                    'body_scale':    0.001,
                    'mesh_scale':    0.7,
                    'gravity_scale': 0.0,
                    'damping':       999,
                    'materials':     mats,
                    'shadow_size':   0.0,
                }
                node = bs.newnode('prop', owner=self.node, attrs=node_attrs)

                head_nodes.append((node, i))
            except Exception:
                pass

        t_state = {'t': 0.0}
        DT    = 0.016   # ~60fps
        TWO_PI = 2 * _math.pi

        def _tick() -> None:
            try:
                if not self.is_alive() or not self.node.exists():
                    for n, _ in head_nodes:
                        try:
                            if n.exists(): n.delete()
                        except Exception:
                            pass
                    return
                t_state['t'] += DT
                t = t_state['t']
                base = self.node.position
                count = len(head_nodes)
                for n, idx in head_nodes:
                    if not n.exists():
                        continue
                    angle = (TWO_PI * idx / count) + (t * TWO_PI / SPEED)
                    x = base[0] + RADIUS * _math.cos(angle)
                    z = base[2] + RADIUS * _math.sin(angle)
                    y = base[1] + Y_OFFSET + 0.08 * _math.sin(t * 2.5 + idx)
                    n.position = (x, y, z)
                    n.mesh_scale = 0.65 + 0.04 * _math.sin(t * 3 + idx)
            except Exception:
                pass

        timer = bs.Timer(DT, babase.CallPartial(_tick), repeat=True)
        self._activations.append(timer)


    def _add_orbit_stars(self) -> None:
        """نجوم سوداء تدور حول اللاعب."""
        import math as _math
        COUNT    = 5
        RADIUS   = 1.0
        SPEED    = 3.0
        Y_OFFSET = 0.2
        DT       = 0.016

        # نجوم المجموعة الأولى (اتجاه عادي) + الثانية (معاكسة)
        star_nodes  = []  # (node, idx, reverse)
        try:
            if not self.node or not self.node.exists():
                return
            from bascenev1lib.gameutils import SharedObjects
            shared = SharedObjects.get()
            for group, reverse in [(COUNT, False), (COUNT, True)]:
                for i in range(group):
                    mat = bs.Material()
                    mat.add_actions(actions=(
                        ('modify_part_collision', 'collide', False),
                        ('modify_part_collision', 'physical', False),
                    ))
                    node = bs.newnode('prop', owner=None, attrs={
                        'mesh':          bs.getmesh('flash'),
                        'color_texture': bs.gettexture('black'),
                        'body':          'sphere',
                        'body_scale':    0.001,
                        'mesh_scale':    0.3,
                        'gravity_scale': 0.0,
                        'damping':       999,
                        'materials':     [mat, shared.object_material],
                        'shadow_size':   0.0,
                    })
                    star_nodes.append((node, i, reverse))
        except Exception:
            pass

        t_state = {'t': 0.0}
        TWO_PI = 2 * _math.pi

        WAVE_AMP   = 0.35
        WAVE_SPEED = 2.5
        WAVE_PHASE = TWO_PI / COUNT

        def _tick() -> None:
            try:
                if not self.is_alive() or not self.node.exists():
                    for n, _, __ in star_nodes:
                        try:
                            if n.exists(): n.delete()
                        except Exception: pass
                    return
                t_state['t'] += DT
                t = t_state['t']
                base = self.node.position
                for n, idx, reverse in star_nodes:
                    if not n.exists(): continue
                    # دوران — عادي أو معاكس
                    direction = -1 if reverse else 1
                    angle = (TWO_PI * idx / COUNT) + direction * (t * TWO_PI / SPEED)
                    x = base[0] + RADIUS * _math.cos(angle)
                    z = base[2] + RADIUS * _math.sin(angle)
                    # موجة معاكسة للمجموعة الثانية
                    wave = WAVE_AMP * _math.sin(direction * t * WAVE_SPEED + idx * WAVE_PHASE)
                    y = base[1] + Y_OFFSET + wave
                    n.position = (x, y, z)
                    n.mesh_scale = 0.3 + 0.03 * abs(_math.sin(t * 2 + idx))
            except Exception:
                pass

        timer = bs.Timer(DT, babase.CallPartial(_tick), repeat=True)
        self._activations.append(timer)

    def _add_orbit_shield(self) -> None:
        """3 shields ملونة تدور حول اللاعب مع نجمة في وسط كل shield."""
        import math as _math
        COUNT    = 3
        RADIUS   = 0.75
        SPEED    = 4.0
        Y_OFFSET = 0.5
        DT       = 0.016
        TWO_PI   = 2 * _math.pi

        # زوايا البداية لكل shield (متباعدة بالتساوي)
        PHASE_OFFSETS = [0.0, TWO_PI / 3, TWO_PI * 2 / 3]
        # ألوان مختلفة لكل shield
        COLORS = [
            (0.0, 2.1),   # يبدأ من أخضر
            (2.1, 4.2),   # يبدأ من أحمر
            (4.2, 6.3),   # يبدأ من أزرق
        ]

        shields = []
        stars   = []
        try:
            if not self.node or not self.node.exists():
                return
            from bascenev1lib.gameutils import SharedObjects
            shared = SharedObjects.get()
            mat = bs.Material()
            mat.add_actions(actions=(
                ('modify_part_collision', 'collide', False),
                ('modify_part_collision', 'physical', False),
            ))
            for i in range(COUNT):
                sh = bs.newnode('shield', owner=self.node, attrs={
                    'color':  (1.0, 1.0, 1.0),
                    'radius': 0.6,
                })
                # نجمة في وسط الـ shield
                star = bs.newnode('prop', owner=None, attrs={
                    'mesh':          bs.getmesh('flash'),
                    'color_texture': bs.gettexture('white'),
                    'body':          'sphere',
                    'body_scale':    0.001,
                    'mesh_scale':    0.3,
                    'gravity_scale': 0.0,
                    'damping':       999,
                    'materials':     [mat, shared.object_material],
                    'shadow_size':   0.0,
                })
                shields.append(sh)
                stars.append(star)
        except Exception:
            return

        t_state = {'t': 0.0}

        def _tick() -> None:
            try:
                if not self.is_alive() or not self.node.exists():
                    for sh in shields:
                        try:
                            if sh.exists(): sh.delete()
                        except Exception: pass
                    for st in stars:
                        try:
                            if st.exists(): st.delete()
                        except Exception: pass
                    return
                t_state['t'] += DT
                t = t_state['t']
                base = self.node.position
                for i, (sh, st) in enumerate(zip(shields, stars)):
                    if not sh.exists(): continue
                    angle = PHASE_OFFSETS[i] + (t * TWO_PI / SPEED)
                    x = base[0] + RADIUS * _math.cos(angle)
                    z = base[2] + RADIUS * _math.sin(angle)
                    y = base[1] + Y_OFFSET + 0.15 * _math.sin(t * 2 + i)
                    sh.position = (x, y, z)
                    if st.exists():
                        st.position = (x, y, z)
                    # لون rainbow مختلف لكل shield
                    off1, off2 = COLORS[i]
                    r = 0.5 + 0.5 * _math.sin(t * 1.8 + off1)
                    g = 0.5 + 0.5 * _math.sin(t * 1.8 + off1 + 2.1)
                    b = 0.5 + 0.5 * _math.sin(t * 1.8 + off1 + 4.2)
                    sh.color = (r * 3.5, g * 3.5, b * 3.5)
            except Exception:
                pass

        timer = bs.Timer(DT, babase.CallPartial(_tick), repeat=True)
        self._activations.append(timer)


    @effect(repeat_interval=0.3)
    def _add_bubbles(self) -> None:
        """فقاعات زرقاء تظهر خلف اللاعب بأحجام مختلفة."""
        import math as _math
        import random as _r
        if not self.node.exists():
            return
        try:
            pos = self.node.position
            vel = self.node.velocity

            # حجم صغير عشوائي
            size  = _r.uniform(0.3, 0.8)
            # لون أزرق بتدرجات مختلفة
            blue  = _r.uniform(2.0, 4.0)
            green = _r.uniform(0.0, 1.0)

            sh = bs.newnode('shield', owner=None, attrs={
                'color':    (0.0, green, blue),
                'radius':   size,
                'position': (
                    pos[0] + _r.uniform(-0.4, 0.4),
                    pos[1] + _r.uniform(-0.3, 0.8),
                    pos[2] + _r.uniform(-0.4, 0.4),
                ),
            })

            # مدة البقاء عشوائية بين 0.5 و 2 ثانية
            lifetime = _r.uniform(0.5, 2.0)

            # تحريك للأعلى ببطء
            t_state = {'t': 0.0}
            start_pos = sh.position

            def _float(node=sh, sp=start_pos, lt=lifetime) -> None:
                try:
                    if not node.exists():
                        return
                    t_state['t'] += 0.05
                    t = t_state['t']
                    # طفو للأعلى
                    node.position = (
                        sp[0] + 0.05 * _math.sin(t * 3),
                        sp[1] + t * 0.4,
                        sp[2],
                    )
                    # تقليص تدريجي قبل الاختفاء
                    if t > lt * 0.7:
                        frac = (t - lt * 0.7) / (lt * 0.3)
                        try:
                            node.radius = max(0.01, size * (1.0 - frac))
                        except Exception:
                            pass
                except Exception:
                    pass

            float_timer = bs.Timer(0.05, babase.CallPartial(_float), repeat=True)
            self._activations.append(float_timer)
            bs.timer(lifetime, sh.delete)
            bs.timer(lifetime + 0.1, lambda: self._activations.remove(float_timer)
                     if float_timer in self._activations else None)
        except Exception:
            pass


    def _add_electric_ring(self) -> None:
        """حلقة كهربائية تنبض حول اللاعب مع جزيئات spark."""
        import math as _math
        if not self.node or not self.node.exists():
            return

        DT       = 0.016
        BASE_R   = 0.9   # نصف القطر الأساسي
        PULSE    = 0.25  # مقدار النبض

        try:
            ring = bs.newnode('locator', owner=self.node, attrs={
                'shape':       'circleOutline',
                'position':    self.node.position,
                'color':       (0.5, 0.8, 4.0),
                'opacity':     1.0,
                'draw_beauty': True,
                'additive':    True,
                'size':        [BASE_R * 2],
            })
            self.node.connectattr('position', ring, 'position')
        except Exception:
            return

        t_state = {'t': 0.0}
        TWO_PI = 2 * _math.pi

        def _tick() -> None:
            try:
                if not self.is_alive() or not self.node.exists():
                    try:
                        if ring.exists(): ring.delete()
                    except Exception: pass
                    return
                t_state['t'] += DT
                t = t_state['t']

                # نبض الحجم
                pulse = BASE_R + PULSE * _math.sin(t * 8.0)
                ring.size = [pulse * 2]

                # تغيير اللون بين أزرق وأبيض
                intensity = 0.7 + 0.3 * _math.sin(t * 12.0)
                ring.color = (
                    intensity * 0.3,
                    intensity * 0.8,
                    intensity * 4.0,
                )

                # spark عشوائية على الحلقة
                if t % 0.05 < DT:
                    angle = _math.uniform(0, TWO_PI) if hasattr(_math, 'uniform') else __import__('random').uniform(0, TWO_PI)
                    pos = self.node.position
                    sx = pos[0] + pulse * _math.cos(angle)
                    sz = pos[2] + pulse * _math.sin(angle)
                    sy = pos[1] + __import__('random').uniform(-0.1, 0.1)
                    bs.emitfx(
                        position=(sx, sy, sz),
                        velocity=(
                            _math.cos(angle) * 0.5,
                            __import__('random').uniform(0.5, 1.5),
                            _math.sin(angle) * 0.5,
                        ),
                        count=2,
                        scale=0.4,
                        spread=0.1,
                        chunk_type='spark',
                    )
            except Exception:
                pass

        timer = bs.Timer(DT, babase.CallPartial(_tick), repeat=True)
        self._activations.append(timer)



def apply() -> None:
    bascenev1lib.actor.playerspaz.PlayerSpaz = NewPlayerSpaz
