"""Custom hooks to pull of the in-game functions."""

# ba_meta require api 9

# pylint: disable=import-error
# pylint: disable=import-outside-toplevel
# pylint: disable=protected-access

from __future__ import annotations

import _thread
import importlib
import logging
import os
import time
from datetime import datetime

import _babase
from typing import TYPE_CHECKING

import babase
import bascenev1 as bs
import _bascenev1
from baclassic._appmode import ClassicAppMode
import bauiv1 as bui
import setting
from baclassic._servermode import ServerController
from bascenev1._activitytypes import ScoreScreenActivity
from bascenev1._map import Map
from bascenev1._session import Session
from bascenev1lib.activity import dualteamscore, multiteamscore, drawscore
from bascenev1lib.activity.coopscore import CoopScoreScreen
from bascenev1lib.actor import playerspaz
from chathandle import handlechat
from features import map_fun
from features import team_balancer, afk_check, dual_team_score as newdts
from features import text_on_map, announcement
from playersdata import pdata
from serverdata import serverdata
from spazmod import modifyspaz
from stats import mystats
from tools import account
from tools import notification_manager
from tools import servercheck, logger, playlist, servercontroller

if TYPE_CHECKING:
    from typing import Any

settings = setting.get_settings_data()


# ══════════════════════════════════════════════════
#  Injection في _hooks.py
# ══════════════════════════════════════════════════

_HOOK_KEY = 'ATD_CustomHooks_v1'


def _get_hooks_path() -> str | None:
    """يبحث عن _hooks.py في كل المسارات الممكنة."""
    import glob
    env = _babase.app.env

    # 1. مسار sys المنسوخ في mods (Android/بعد أول تثبيت)
    user_sys = (env.python_directory_user + '/sys/'
                + env.engine_version + '_'
                + str(env.engine_build_number)
                + '/bascenev1/_hooks.py')
    if os.path.exists(user_sys):
        return user_sys

    # 2. ba_data مباشرة (Linux server)
    app_path = env.python_directory_app + '/bascenev1/_hooks.py'
    if os.path.exists(app_path):
        return app_path

    # 3. بحث عام في حال كان المسار مختلفاً
    for p in glob.glob(os.path.join(env.python_directory_user, '**', '_hooks.py'), recursive=True):
        return p

    return None


def _create_sys_scripts() -> str | None:
    """ينسخ كامل ba_data/python إلى mods/sys/ مثل baCheatMax."""
    import shutil
    env = _babase.app.env
    ver = env.engine_version + '_' + str(env.engine_build_number)
    src = env.python_directory_app
    dst = env.python_directory_user + '/sys/' + ver

    if src is None or dst is None:
        return None

    def _ignore(s, names):
        return ('__pycache__',)

    try:
        if os.path.exists(dst):
            shutil.rmtree(dst)
        logging.warning(f'ATD: copying {src} → {dst} ...')
        shutil.copytree(src, dst, ignore=_ignore)
        logging.warning('ATD: sys scripts created.')
        return dst + '/bascenev1/_hooks.py'
    except Exception as e:
        logging.warning(f'ATD: failed to create sys scripts: {e}')
        return None


def _ensure_writable_hooks() -> str | None:
    """يضمن وجود نسخة قابلة للكتابة من _hooks.py."""
    env = _babase.app.env
    ver = env.engine_version + '_' + str(env.engine_build_number)
    dst = env.python_directory_user + '/sys/' + ver + '/bascenev1/_hooks.py'

    # موجود وقابل للكتابة
    if os.path.exists(dst) and os.access(dst, os.W_OK):
        return dst

    # لا يوجد sys folder — ننسخ كامل ba_data مثل baCheatMax
    return _create_sys_scripts()


def _inject_hooks() -> None:
    path = _ensure_writable_hooks()
    if path is None:
        logging.warning('ATD: _hooks.py not found or not writable — chat commands disabled.')
        return

    with open(path, encoding='utf-8') as f:
        content = f.read()

    if _HOOK_KEY in content:
        return  # already injected

    key = _HOOK_KEY
    injection = (
        '    # ' + key + '\n'
        '    try:\n'
        '        _r = babase.app.atd_filter_chat(msg, client_id)\n'
        '        if _r is None:\n'
        '            return None\n'
        '        msg = _r\n'
        '    except Exception:\n'
        '        pass\n'
    )

    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'def filter_chat_message(' in line:
            for k, ln in enumerate(injection.split('\n')):
                lines.insert(i + 1 + k, ln)
            break

    with open(path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))
    logging.warning('ATD: injected chat hook into _hooks.py — restarting...')
    try:
        import babase as _ba2
        _ba2.quit(confirm=False)
    except Exception:
        try:
            import bascenev1 as _bs2
            _bs2.apptimer(2.0, _babase.quit)
        except Exception:
            pass


def filter_chat_message(msg: str, client_id: int) -> str | None:
    """Returns all in game messages or None (ignore's message)."""
    # فحص إجابات الـ quiz — لا نمنع vote words
    VOTE_WORDS = {'end', 'nv', 'dv', 'sm'}
    if msg.strip().lower() not in VOTE_WORDS and not msg.startswith('/'):
        try:
            from coinSystem import check_answer, _correct_answer
            if _correct_answer is not None:
                if check_answer(msg, client_id):
                    return None
        except Exception:
            pass
    return handlechat.filter_chat_message(msg, client_id)


# ba_meta export babase.Plugin


class modSetup(babase.Plugin):
    def on_app_running(self):
        """Runs when app is launched."""
        plus = bui.app.plus
        bootstraping()
        servercheck.checkserver().start()
        # bs.apptimer(5, account.updateOwnerIps)
        if settings["afk_remover"]['enable']:
            afk_check.checkIdle().start()
        if (settings["useV2Account"]):

            if (plus.get_v1_account_state() ==
                    'signed_in' and plus.get_v1_account_type() == 'V2'):
                logging.debug("Account V2 is active")
            else:
                logging.warning("Account V2 login require ....stay tuned.")
                bs.apptimer(3, babase.Call(logging.debug,
                                           "Starting Account V2 login process...."))
                bs.apptimer(6, account.AccountUtil)
        else:
            plus.accounts.set_primary_credentials(None)
            plus.sign_in_v1('Local')
        bs.apptimer(60, playlist.flush_playlists)
        # ربط دالة الفلتر وحقن _hooks.py
        babase.app.atd_filter_chat = filter_chat_message
        bs.apptimer(2.0, _inject_hooks)

    # it works sometimes , but it blocks shutdown so server raise runtime
    # exception,   also dump server logs
    def on_app_shutdown(self):
        print("Server shutting down , lets save cache")
        # lets try  threading here
        # _thread.start_new_thread(pdata.dump_cache, ())
        # _thread.start_new_thread(notification_manager.dump_cache, ())
        # print("Done dumping memory")


def score_screen_on_begin(func) -> None:
    """Runs when score screen is displayed."""

    def wrapper(self, *args, **kwargs):
        result = func(self, *args, **kwargs)  # execute the original method
        team_balancer.balanceTeams()
        mystats.update(self._stats)
        announcement.showScoreScreenAnnouncement()
        # مكافأة أفضل 3 لاعبين بالنقاط
        try:
            from coinSystem import reward_top_players
            reward_top_players(self._stats)
        except Exception as _e:
            logging.warning(f'reward_top_players error: {_e}')
        return result

    return wrapper


ScoreScreenActivity.on_begin = score_screen_on_begin(
    ScoreScreenActivity.on_begin)


def on_map_init(func):
    def wrapper(self, *args, **kwargs):
        func(self, *args, **kwargs)
        text_on_map.textonmap()
        modifyspaz.setTeamCharacter()

    return wrapper


Map.__init__ = on_map_init(Map.__init__)


def playerspaz_init(playerspaz: bs.Player, node: bs.Node, player: bs.Player):
    """Runs when player is spawned on map."""
    modifyspaz.main(playerspaz, node, player)


def bootstraping():
    """Bootstarps the server."""
    logging.warning("Bootstraping mods...")
    # server related

    # check for auto update stats
    _thread.start_new_thread(mystats.refreshStats, ())
    pdata.load_cache()
    # تطبيق wrap بعد تحميل spaz_effects
    try:
        import bascenev1lib.actor.playerspaz as _ps
        _ps.PlayerSpaz = wrap_player_spaz_init(_ps.PlayerSpaz)
    except Exception as _e:
        logging.warning(f"wrap_player_spaz error: {_e}")
    # تفعيل نظام العملات
    try:
        from coinSystem import enable as _coin_enable
        _coin_enable()
    except Exception as _e:
        logging.warning(f"ATD: coinSystem failed: {_e}")
    _thread.start_new_thread(pdata.dump_cache, ())
    _thread.start_new_thread(notification_manager.dump_cache, ())

    # import plugins
    if settings.get("snowfall", {}).get("enable", False):
        try:
            from plugins import snowfall
            snowfall.enable()
        except Exception as e:
            logging.warning(f"snowfall failed to load: {e}")
    if settings.get("flying_mine", {}).get("enable", False):
        try:
            from plugins import flying_mine
            flying_mine.enable()
        except Exception as e:
            logging.warning(f"flying_mine failed to load: {e}")
    if settings.get("ATD_Pows", {}).get("enable", False):
        try:
            from plugins import ATD_Pows
            ATD_Pows.enable()
        except Exception as e:
            logging.warning(f"ATD_Pows failed to load: {e}")
    if settings.get("ATD_hits", {}).get("enable", False):
        try:
            from spazmod import ATD_hits
            ATD_hits.enable()
        except Exception as e:
            logging.warning(f"ATD_hits failed to load: {e}")
    if settings["mikirogQuickTurn"]["enable"]:
        from plugins import wavedash  # pylint: disable=unused-import
    if settings["colorful_explosions"]["enable"]:
        from plugins import color_explosion
        color_explosion.enable()
    if settings["ballistica_web"]["enable"]:
        from plugins import bcs_plugin
        bcs_plugin.enable(settings["ballistica_web"]["server_password"])
    if settings["character_chooser"]["enable"]:
        from plugins import character_chooser
        character_chooser.enable()
    if settings["custom_characters"]["enable"]:
        from plugins import importcustomcharacters
        importcustomcharacters.enable()
    if settings["colorfullMap"]:
        from plugins import colorfulmaps2
    try:
        pass
        # from tools import healthcheck
        # healthcheck.main()
    except Exception as e:
        print(e)
        try:
            import subprocess
            # Install psutil package
            # Download get-pip.py
            curl_process = subprocess.Popen(
                ["curl", "-sS", "https://bootstrap.pypa.io/get-pip.py"],
                stdout=subprocess.PIPE)

            # Install pip using python3.10
            python_process = subprocess.Popen(
                ["python3.10"], stdin=curl_process.stdout)

            # Wait for the processes to finish
            curl_process.stdout.close()
            python_process.wait()

            subprocess.check_call(
                ["python3.10", "-m", "pip", "install", "psutil"])
            # restart after installation
            print("dependency installed , restarting server")
            _babase.quit()
            from tools import healthcheck
            healthcheck.main()
        except BaseException:
            logging.warning("please install psutil to enable system monitor.")

    # import features
    if settings["whitelist"]:
        pdata.load_white_list()

    import_discord_bot()
    import_games()
    import_dual_team_score()
    logger.log("Server started")


def import_discord_bot() -> None:
    """Imports the discord bot."""
    if settings["discordbot"]["enable"]:
        from features import discord_bot
        discord_bot.token = settings["discordbot"]["token"]
        discord_bot.liveStatsChannelID = settings["discordbot"][
            "liveStatsChannelID"]
        discord_bot.logsChannelID = settings["discordbot"]["logsChannelID"]
        discord_bot.liveChat = settings["discordbot"]["liveChat"]
        discord_bot.BsDataThread()
        discord_bot.init()


def import_games():
    """Imports the custom games and maps from ba_root/mods."""
    import sys

    games_dir = 'ba_root/mods/games'
    maps_dir  = 'ba_root/mods/maps'

    if os.path.isdir(games_dir):
        sys.path.append(games_dir)
        for game in os.listdir(games_dir):
            if game.endswith('.so') or game.endswith('.py'):
                try:
                    importlib.import_module('games.' + game.replace('.so', '').replace('.py', ''))
                except Exception as e:
                    logging.warning(f'Failed to import game {game}: {e}')

    if os.path.isdir(maps_dir):
        sys.path.append(maps_dir)
        for _map in os.listdir(maps_dir):
            if _map.endswith('.so') or _map.endswith('.py'):
                try:
                    importlib.import_module('maps.' + _map.replace('.so', '').replace('.py', ''))
                except Exception as e:
                    logging.warning(f'Failed to import map {_map}: {e}')


def import_dual_team_score() -> None:
    """Imports the dual team score."""
    if settings["newResultBoard"]:
        dualteamscore.TeamVictoryScoreScreenActivity = newdts.TeamVictoryScoreScreenActivity
        multiteamscore.MultiTeamScoreScreenActivity.show_player_scores = newdts.show_player_scores
        drawscore.DrawScoreScreenActivity = newdts.DrawScoreScreenActivity


org_begin = bs._activity.Activity.on_begin


def new_begin(self):
    """Runs when game is began."""
    org_begin(self)
    try:
        from bascenev1lib.tutorial import TutorialActivity
        if isinstance(self, TutorialActivity):
            return
    except Exception:
        pass
    night_mode()
    if settings["colorfullMap"]:
        map_fun.decorate_map()


bs._activity.Activity.on_begin = new_begin

org_end = bs._activity.Activity.end


def new_end(self, results: Any = None,
            delay: float = 0.0, force: bool = False):
    """Runs when game is ended."""
    activity = bs.get_foreground_host_activity()

    if isinstance(activity, CoopScoreScreen):
        team_balancer.checkToExitCoop()
    org_end(self, results, delay, force)


bs._activity.Activity.end = new_end

org_player_join = bs._activity.Activity.on_player_join


def on_player_join(self, player) -> None:
    """Runs when player joins the game."""
    team_balancer.on_player_join()
    org_player_join(self, player)


bs._activity.Activity.on_player_join = on_player_join


def night_mode() -> None:
    """Checks the time and enables night mode."""

    if settings['autoNightMode']['enable']:

        start = datetime.strptime(
            settings['autoNightMode']['startTime'], "%H:%M")
        end = datetime.strptime(settings['autoNightMode']['endTime'], "%H:%M")
        now = datetime.now()

        if now.time() > start.time() or now.time() < end.time():
            activity = bs.get_foreground_host_activity()

            activity.globalsnode.tint = (0.5, 0.7, 1.0)

            if settings['autoNightMode']['fireflies']:
                try:
                    activity.fireflies_generator(
                        20, settings['autoNightMode']["fireflies_random_color"])
                except:
                    pass


def kick_vote_started(started_by: str, started_to: str) -> None:
    """Logs the kick vote."""
    logger.log(f"{started_by} started kick vote for {started_to}.")


def on_kicked(account_id: str) -> None:
    """Runs when someone is kicked by kickvote."""
    logger.log(f"{account_id} kicked by kickvotes.")


def on_kick_vote_end():
    """Runs when kickvote is ended."""
    logger.log("Kick vote End")


def on_join_request(ip):
    servercheck.on_join_request(ip)


def shutdown(func) -> None:
    """Set the app to quit either now or at the next clean opportunity."""

    def wrapper(*args, **kwargs):
        # add screen text and tell players we are going to restart soon.
        bs.chatmessage(
            "Server will restart on next opportunity. (series end)")
        _babase.restart_scheduled = True
        bs.get_foreground_host_activity().restart_msg = bs.newnode('text',
                                                                   attrs={
                                                                       'text': "Server going to restart after this series.",
                                                                       'flatness': 1.0,
                                                                       'h_align': 'right',
                                                                       'v_attach': 'bottom',
                                                                       'h_attach': 'right',
                                                                       'scale': 0.5,
                                                                       'position': (
                                                                           -25,
                                                                           54),
                                                                       'color': (
                                                                           1,
                                                                           0.5,
                                                                           0.7)
                                                                   })
        func(*args, **kwargs)

    return wrapper


ServerController.shutdown = shutdown(ServerController.shutdown)


# on_player_request disabled - blocks local players on Android
# def on_player_request(func) -> bool: ...

def on_access_check_response(self, data):
    if data is not None:
        addr = data['address']
        port = data['port']
        if settings["ballistica_web"]["enable"]:
            bs.set_public_party_stats_url(
                f'https://bombsquad-community.web.app/server-manager/?host={addr}:{port}')

    servercontroller._access_check_response(self, data)


ServerController._access_check_response = on_access_check_response


def wrap_player_spaz_init(original_class):
    """
    Modify the __init__ method of the player_spaz.
    """

    class WrappedClass(original_class):
        def __init__(self, *args, **kwargs):
            player = args[0] if args else kwargs.get('player')
            character = args[3] if len(
                args) > 3 else kwargs.get('character', 'Spaz')

            modified_character = modifyspaz.getCharacter(player, character)
            if len(args) > 3:
                args = args[:3] + (modified_character,) + args[4:]
            else:
                kwargs['character'] = modified_character

            super().__init__(*args, **kwargs)
            playerspaz_init(self, self.node, self._player)

        def handlemessage(self, msg) -> None:
            import bascenev1 as _bs
            if isinstance(msg, _bs.DieMessage):
                super().handlemessage(msg)
            else:
                try:
                    super().handlemessage(msg)
                except Exception:
                    pass

    return WrappedClass



original_classic_app_mode_activate = ClassicAppMode.on_activate


def new_classic_app_mode_activate(*args, **kwargs):
    # Call the original function
    result = original_classic_app_mode_activate(*args, **kwargs)

    # Perform additional actions after the original function call
    on_classic_app_mode_active()

    return result
