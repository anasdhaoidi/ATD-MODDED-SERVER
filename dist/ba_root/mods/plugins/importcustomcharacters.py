"""Module to update `setting.json`."""

# ba_meta require api 9
# (see https://ballistica.net/wiki/meta-tag-system)

from __future__ import annotations

import json
import os

import _babase
from typing import TYPE_CHECKING

from bascenev1lib.actor.spazappearance import Appearance

if TYPE_CHECKING:
    pass


def register_character(name: str, char: dict) -> None:
    """Registers the character in the game."""
    t = Appearance(name.split(".")[0])
    t.color_texture = char['color_texture']
    t.color_mask_texture = char['color_mask']
    t.default_color = (0.6, 0.6, 0.6)
    t.default_highlight = (0, 1, 0)
    t.icon_texture = char['icon_texture']
    t.icon_mask_texture = char['icon_mask_texture']
    t.head_mesh = char['head']
    def _mesh(char, *keys):
        for k in keys:
            v = char.get(k)
            if v and str(v).strip():
                return str(v)
        return None

    t.color_texture      = char.get('color_texture', '')
    t.color_mask_texture = char.get('color_mask_texture', char.get('color_mask', ''))
    t.head_mesh      = _mesh(char, 'head_mesh', 'head')
    t.torso_mesh     = _mesh(char, 'torso_mesh', 'torso')
    t.pelvis_mesh    = _mesh(char, 'pelvis_mesh', 'pelvis')
    t.upper_arm_mesh = _mesh(char, 'upper_arm_mesh', 'upper_arm')
    t.forearm_mesh   = _mesh(char, 'forearm_mesh', 'forearm')
    t.hand_mesh      = _mesh(char, 'hand_mesh', 'hand')
    t.upper_leg_mesh = _mesh(char, 'upper_leg_mesh', 'upper_leg')
    t.lower_leg_mesh = _mesh(char, 'lower_leg_mesh', 'lower_leg')
    toes = _mesh(char, 'toes_mesh', 'toes_model', 'toes')
    if toes:
        t.toes_mesh = toes
    t.jump_sounds    = char.get('jump_sounds',   [])
    t.attack_sounds  = char.get('attack_sounds', [])
    t.impact_sounds  = char.get('impact_sounds', [])
    t.death_sounds   = char.get('death_sounds',  [])
    t.pickup_sounds  = char.get('pickup_sounds', [])
    t.fall_sounds    = char.get('fall_sounds',   [])
    t.style          = char.get('style', 'spaz')


def enable() -> None:
    path = os.path.join(_babase.env()["python_directory_user"],
                        "custom_characters" + os.sep)

    if not os.path.isdir(path):
        os.makedirs(path)

    files = os.listdir(path)

    for file in files:
        if file.endswith(".json"):
            with open(path + file) as json_file:
                character = json.load(json_file)
                register_character(file, character)
