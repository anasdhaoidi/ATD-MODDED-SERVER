# ba_meta require api 9

from __future__ import annotations

from typing import TYPE_CHECKING

import bascenev1 as bs
from bascenev1._map import Map
from bascenev1lib.gameutils import SharedObjects
import bauiv1 as bui
from bauiv1lib import popup

if TYPE_CHECKING:
    from typing import Sequence, Any


class CustomLang:
    lang = bs.app.lang.language
    if lang == 'Spanish':
        title = 'Mina Flotante'
        mines = 'Minas'
        enable = 'Habilitar'
    else:
        title = 'Flotating Mine'
        mines = 'Mines'
        enable = 'Enable'


class ConfigNumberEdit:

    def __init__(self,
                 parent: bui.Widget,
                 position: tuple[float, float],
                 value: int,
                 config: str,
                 text: str):
        self._increment = 1
        self._minval = 1
        self._maxval = 4
        self._value = value
        self._config = config

        textscale = 1.0
        self.nametext = bui.textwidget(
            parent=parent,
            position=(position[0], position[1]),
            size=(100, 30),
            text=text,
            maxwidth=150,
            color=(0.8, 0.8, 0.8, 1.0),
            h_align='left',
            v_align='center',
            scale=textscale)
        self.valuetext = bui.textwidget(
            parent=parent,
            position=(position[0]+150, position[1]),
            size=(60, 28),
            editable=False,
            color=(0.3, 1.0, 0.3, 1.0),
            h_align='right',
            v_align='center',
            text=str(value),
            padding=2)
        self.minusbutton = bui.buttonwidget(
            parent=parent,
            position=(position[0]+240, position[1]),
            size=(28, 28),
            label='-',
            autoselect=True,
            on_activate_call=bs.Call(self._down),
            repeat=True)
        self.plusbutton = bui.buttonwidget(
            parent=parent,
            position=(position[0]+290, position[1]),
            size=(28, 28),
            label='+',
            autoselect=True,
            on_activate_call=bui.Call(self._up),
            repeat=True)

    def _up(self) -> None:
        self._value = min(self._maxval, self._value + self._increment)
        self._update_display()

    def _down(self) -> None:
        self._value = max(self._minval, self._value - self._increment)
        self._update_display()

    def _update_display(self) -> None:
        bui.textwidget(edit=self.valuetext, text=str(self._value))
        bui.app.config['Flotating Mine'][self._config] = self._value
        bui.app.config.apply_and_commit()


class FlotatingMinePopup(popup.PopupWindow):

    def __init__(self):
        uiscale = bui.app.ui_v1.uiscale
        self._transitioning_out = False
        self._width = 400
        self._height = 220
        bg_color = (0.4, 0.37, 0.49)

        # creates our _root_widget
        super().__init__(
            position=(0.0, 0.0),
            size=(self._width, self._height),
            scale=2.4 if uiscale is bui.UIScale.SMALL else 1.2,
            bg_color=bg_color)

        self._cancel_button = bui.buttonwidget(
            parent=self.root_widget,
            position=(25, self._height - 40),
            size=(50, 50),
            scale=0.58,
            label='',
            color=bg_color,
            on_activate_call=self._on_cancel_press,
            autoselect=True,
            icon=bui.gettexture('crossOut'),
            iconscale=1.2)
        bui.containerwidget(edit=self.root_widget,
                           cancel_button=self._cancel_button)

        bui.textwidget(
            parent=self.root_widget,
            position=(self._width * 0.5, self._height - 27 - 5),
            size=(0, 0),
            h_align='center',
            v_align='center',
            scale=0.8,
            text=CustomLang.title,
            maxwidth=self._width * 0.7,
            color=bui.app.ui_v1.title_color)

        ConfigNumberEdit(
            parent=self.root_widget,
            position=(self._width * 0.08, self._height * 0.52 - 5),
            value=bui.app.config['Flotating Mine']['mines'],
            config='mines',
            text=CustomLang.mines)

        bui.checkboxwidget(
            parent=self.root_widget,
            position=(self._width * 0.28, self._height * 0.18),
            size=(self._width * 0.48, 50),
            autoselect=True,
            maxwidth=self._width * 0.3,
            scale=1.0,
            textcolor=(0.8, 0.8, 0.8),
            value=bui.app.config['Flotating Mine']['enable'],
            text=CustomLang.enable,
            on_value_change_call=self.change_enable,
        )

    def change_enable(self, val: bool) -> None:
        cfg = bui.app.config
        cfg['Flotating Mine']['enable'] = val
        cfg.apply_and_commit()

    def _on_cancel_press(self) -> None:
        self._transition_out()

    def _transition_out(self) -> None:
        if not self._transitioning_out:
            self._transitioning_out = True
            bui.containerwidget(edit=self.root_widget, transition='out_scale')

    def on_popup_cancel(self) -> None:
        bui.getsound('swish').play()
        self._transition_out()


class Mine(bs.Actor):
    def __init__(self, map: str, type: int):
        super().__init__()
        shared = SharedObjects.get()
        if map == 'Big G':
            x = -0.2
            y = 0
            z = 0
            nx = 8
            nz = 6
        elif map == 'Bridgit':
            x = -0.5
            y = 1.5
            z = -2
            nx = 6
            nz = 5
        elif map == 'Courtyard':
            x = 0
            y = 1.2
            z = -2
            nx = 7
            nz = 5
        elif map == 'Crag Castle':
            x = 0.5
            y = 5
            z = -4
            nx = 8
            nz = 5
        elif map == 'Doom Shroom':
            x = 0
            y = -0.1
            z = -4
            nx = 9
            nz = 5
        elif map in ['Football Stadium', 'Hockey Stadium']:
            x = 0
            y = -2.4
            z = 0
            nx = 11
            nz = 5
        elif map == 'Happy Thoughts':
            x = -1
            y = 14
            z = -3
            nx = 15.5
            nz = 5
        elif map == 'Lake Frigid':
            x = 0.3
            y = 0
            z = -2.4
            nx = 8
            nz = 5
        elif map == 'Monkey Face':
            x = -1.5
            y = 0.8
            z = -1.5
            nx = 8
            nz = 5
        elif map == 'Rampage':
            x = 0.2
            y = 2.6
            z = -4.8
            nx = 8.5
            nz = 3.5
        elif map == 'Roundabout':
            x = -1.4
            y = 1.3
            z = -4
            nx = 6
            nz = 4.5
        elif map == 'Step Right Up':
            x = 0.2
            y = 3.1
            z = -2.6
            nx = 7
            nz = 7
        elif map == 'The Pad':
            x = 0.2
            y = 1.8
            z = -3.1
            nx = 7.2
            nz = 7.2
        elif map == 'Tower D':
            x = 0
            y = 0
            z = -1
            nx = 7
            nz = 6
        elif map == 'Tip Top':
            x = 0
            y = 6.1
            z = -1
            nx = 8
            nz = 6
        elif map == 'Zigzag':
            x = -1.5
            y = 2
            z = -1.6
            nx = 8
            nz = 3
        else:
            x = 0
            y = 0
            z = 0
            nx = 6
            nz = 5
        if type == 1:
            animate_pos = [
                (1.830634+x, 4.830635+y, 3.830636+z),
                (4.8306378+x, 4.83063588+y, -nz-0.830639+z),
                (-nx-0.422572086+x, 5.228850685+y, nz-0.803988636+z),
                (-nx-0.859406739+x, 5.429165244+y, -nz-0.588618549+z),
                (-nx-0.859406739+x, 4.429165244+y, -nz-0.588618549+z),
                (3.148493267+x, 4.429165244+y, -nz-0.588618549+z),
                (1.830377363+x, 4.228850685+y, 2.803988636+z),
                (-nx-0.422572086+x, 4.228850685+y, 2.803988636+z),
                (-nx-0.422572086+x, 4.228850685+y, 2.803988636+z),
                (1.830377363+x, 4.228850685+y, 2.803988636+z),
                (3.148493267+x, 5.429165244+y, -nz-0.588618549+z),
                (1.830377363+x, 5.228850685+y, 2.803988636+z),
                (3.148493267+x, 4.429165244+y, -nz-0.588618549+z),
                (-nx-0.422572086+x, 4.228850685+y, 2.803988636+z),
                (-nx-0.859406739+x, 5.429165244+y, -nz-0.588618549+z),
            ]
        elif type == 2:
            animate_pos = [
                (-1.830634+x, 4.830635+y, -3.830636+z),
                (-4.8306378+x, 4.83063588+y, nz+0.830639+z),
                (nx+0.422572086+x, 5.228850685+y, -2.803988636+z),
                (nx+0.859406739+x, 5.429165244+y, nz+0.588618549+z),
                (nx+0.859406739+x, 4.429165244+y, nz+0.588618549+z),
                (-3.148493267+x, 4.429165244+y, nz+0.588618549+z),
                (-1.830377363+x, 4.228850685+y, -2.803988636+z),
                (nx+0.422572086+x, 4.228850685+y, -2.803988636+z),
                (nx+0.422572086+x, 4.228850685+y, -2.803988636+z),
                (-1.830377363+x, 4.228850685+y, -2.803988636+z),
                (-3.148493267+x, 5.429165244+y, nz+0.588618549+z),
                (-1.830377363+x, 5.228850685+y, -2.803988636+z),
                (-3.148493267+x, 4.429165244+y, nz+0.588618549+z),
                (nx+0.422572086+x, 4.228850685+y, -2.803988636+z),
                (nx+0.859406739+x, 5.429165244+y, nz+0.588618549+z),
            ]
        elif type == 3:
            animate_pos = [
                (nx+0.859406739+x, 4.429165244+y, nz+0.588618549+z),
                (nx+0.859406739+x, 4.429165244+y, nz+0.588618549+z),
                (nx+0.422572086+x, 5.228850685+y, -2.803988636+z),
                (-3.148493267+x, 5.429165244+y, nz+0.588618549+z),
                (-1.830377363+x, 4.228850685+y, -2.803988636+z),
                (-3.148493267+x, 4.429165244+y, nz+0.588618549+z),
                (-1.830377363+x, 4.228850685+y, -2.803988636+z),
                (nx+0.422572086+x, 4.228850685+y, -2.803988636+z),
                (nx+0.422572086+x, 4.228850685+y, -2.803988636+z),
                (-1.830377363+x, 4.228850685+y, -2.803988636+z),
                (-3.148493267+x, 5.429165244+y, nz+0.588618549+z),
                (nx+0.859406739+x, 5.429165244+y, nz+0.588618549+z),
                (nx+0.859406739+x, 4.429165244+y, nz+0.588618549+z),
                (nx+0.422572086+x, 4.228850685+y, -2.803988636+z),
                (-4.8306378+x, 5.83063588+y, nz+0.830639+z),
            ]
        else:
            animate_pos = [
                (-nx-0.859406739+x, 4.429165244+y, -nz-0.588618549+z),
                (-nx-0.859406739+x, 4.429165244+y, -nz-0.588618549+z),
                (-nx-0.422572086+x, 6.228850685+y, 2.803988636+z),
                (3.148493267+x, 5.429165244+y, -nz-0.588618549+z),
                (1.830377363+x, 4.228850685+y, 2.803988636+z),
                (3.148493267+x, 4.429165244+y, -nz-0.588618549+z),
                (1.830377363+x, 4.228850685+y, 2.803988636+z),
                (-nx-0.422572086+x, 4.228850685+y, 2.803988636+z),
                (-nx-0.422572086+x, 4.228850685+y, 2.803988636+z),
                (1.830377363+x, 4.228850685+y, 2.803988636+z),
                (3.148493267+x, 5.429165244+y, -nz-0.588618549+z),
                (-nx-0.859406739+x, 5.429165244+y, -nz-0.588618549+z),
                (-nx-0.859406739+x, 4.429165244+y, -nz-0.588618549+z),
                (-nx-0.422572086+x, 4.228850685+y, 2.803988636+z),
                (4.8306378+x, 5.83063588+y, -nz-0.830639+z),
            ]
        self._no_collide_material = bs.Material()
        self._no_collide_material.add_actions(
            conditions=('they_have_material', self._no_collide_material),
            actions=('modify_part_collision', 'collide', False),
        )
        # منع خطأ body 3 عند التصادم مع اللاعبين
        # منع body 3 مع الـ spaz nodes
        try:
            from bascenev1lib.actor.spaz import Spaz
            spaz_mat = bs.Material()
            spaz_mat.add_actions(
                actions=(
                    ('modify_part_collision', 'collide', False),
                    ('modify_part_collision', 'physical', False),
                )
            )
            self._spaz_no_collide = spaz_mat
        except Exception:
            self._spaz_no_collide = None
        if not shared.footing_material or not shared.object_material:
            return
        self.node = bs.newnode(
            'prop',
            delegate=self,
            attrs={
                'velocity': (2.0,1.0,0),
                'sticky': False,
                'body': 'landMine',
                'mesh': bs.getmesh('landMine'),
                'mesh_scale': 3.3,
                'color_texture': bs.gettexture('logo'),
                'body_scale': 3.3,
                'reflection': 'powerup',
                'reflection_scale': [1.0],
                'density': 99999999999,
                'damping': 99999999999,
                'gravity_scale': 0.0,
                'shadow_size': 0.2,
                'materials': ([shared.footing_material,
                               shared.object_material,
                               self._no_collide_material]
                               + ([self._spaz_no_collide] if self._spaz_no_collide else []))
            })
        # text = bs.newnode(
        #   'text',
        #   attrs={
        #       'text': str(type),
        #       'in_world': True,
        #       'scale': 0.015,
        #       'shadow': 0.5,
        #       'flatness': 1.0,
        #       'h_align': 'center',
        #   }
        # )
        # self.node.connectattr('position', text, 'position')
        bs.animate_array(self.node, 'position', 3, {
            0: animate_pos[0],
            10: animate_pos[1],
            20: animate_pos[2],
            25: animate_pos[3],
            30: animate_pos[4],
            35: animate_pos[5],
            40: animate_pos[6],
            45: animate_pos[7],
            50: animate_pos[8],
            55: animate_pos[9],
            60: animate_pos[10],
            70: animate_pos[11],
            75: animate_pos[12],
            80: animate_pos[13],
            90: animate_pos[14],
            95: animate_pos[0],
            }, loop = True
        )

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, bs.OutOfBoundsMessage):
            self.node.delete()
        else:
            super().handlemessage(msg)

    def has_settings_ui(self) -> bool:
        return True

    def show_settings_ui(self, source_widget: bs.Widget | None) -> None:
        FlotatingMinePopup()

    pass


def enable() -> None:
    if 'Flotating Mine' not in bs.app.config:
        bs.app.config['Flotating Mine'] = {'enable': True, 'mines': 1}
        bs.app.config.apply_and_commit()

    Map.old_init = Map.__init__

    def __init__(self, vr_overlay_offset=None) -> None:
        self.old_init(vr_overlay_offset)
        from bascenev1lib import mainmenu
        in_game = not isinstance(
            bs.get_foreground_host_session(), mainmenu.MainMenuSession)
        if not in_game:
            return

        def path():
            mines = bs.app.config['Flotating Mine']['mines']
            if mines >= 4:
                Mine(self.name, 1).autoretain()
                Mine(self.name, 2).autoretain()
                Mine(self.name, 3).autoretain()
                Mine(self.name, 4).autoretain()
            elif mines >= 3:
                Mine(self.name, 1).autoretain()
                Mine(self.name, 2).autoretain()
                Mine(self.name, 3).autoretain()
            elif mines >= 2:
                Mine(self.name, 1).autoretain()
                Mine(self.name, 2).autoretain()
            else:
                Mine(self.name, 1).autoretain()

        if bs.app.config['Flotating Mine']['enable']:
            bs.timer(0.1, path)

    Map.__init__ = __init__
