import _babase
import _bascenev1
import babase
import bascenev1 as bs
from bascenev1lib.actor.zoomtext import ZoomText
from bascenev1lib.gameutils import SharedObjects
from playersdata import pdata
from serverdata import serverdata
from stats import mystats
from tools import playlist, logger
from .handlers import send, clientid_to_myself
import bascenev1 as _bs_chat

def clientid_to_name(clientid):
    for i in _bs_chat.get_game_roster():
        if i['client_id'] == clientid:
            try: return i['players'][0]['name_full']
            except: return i.get('display_string', str(clientid))
    return str(clientid)

def sendall(msg):
    _bs_chat.chatmessage(str(msg))

def sendchat(msg):
    _bs_chat.chatmessage(str(msg))
import setting
import os, json, time, random
import _thread

settings = setting.get_settings_data()

Commands = ['hug', 'icy', 'spaz', 'zombieall', 'boxall', 'texall', 'kickall',
    'ooh', 'spazall', 'vcl', 'acl', 'dbc', 'd_bomb_count', 'default_bomb_count',
    'dbt', 'd_bomb_type', 'default_bomb_type',
    'rocket', 'swap', 'party', ]
CommandAliases = [
    'cc', 'ccall', 'control', 'prot', 'protect', 'zoommessage', 'zm',
    'pme', 'zombie', 'rainbow', 'playsound', 'tex', 'box',
    'ac', 'exchange', 'tint', 'say', 'admincmdlist', 'vipcmdlist',
]


def ExcelCommand(command, arguments, clientid, accountid):
    if command == 'hug':
        if arguments and arguments[0] == 'all':
            hugall(arguments[1:], clientid)
        else:
            hug(arguments, clientid)
    elif command in ['control', 'exchange']:
        control(arguments, clientid)
    elif command == 'icy':
        icy(arguments, clientid)
    elif command in ['cc', 'spaz']:
        spaz(arguments, clientid)
    elif command in ['ccall', 'spazall']:
        spazall(arguments, clientid)
    elif command == 'ac':
        ac(arguments, clientid)
    elif command == 'tint':
        tint(arguments, clientid)
    elif command == 'box':
        box(arguments, clientid)
    elif command == 'boxall':
        boxall(arguments, clientid)
    elif command in ['dbc', 'd_bomb_count', 'default_bomb_count']:
        d_bomb_count(arguments, clientid)
    elif command in ['dbt', 'd_bomb_type', 'default_bomb_type']:
        d_bomb_type(arguments, clientid)
    elif command == 'kickall':
        kickall(arguments, clientid)
    elif command == 'tex':
        tex(arguments, clientid)
    elif command == 'zombie':
        zombie(arguments, clientid)
    elif command == 'zombieall':
        zombieall(arguments, clientid)
    elif command == 'texall':
        texall(arguments, clientid)
    elif command == 'say':
        server_chat(arguments, clientid)
    elif command in ['acl', 'admincmdlist']:
        acl(arguments, clientid)
    elif command == 'ooh':
        play_ooh_sound(arguments)
    elif command in ['zm', 'zoommessage']:
        zm(arguments, clientid)
    elif command == 'playsound':
        play_sound(arguments, clientid)
    elif command in ['vcl', 'vipcmdlist']:
        vcl(arguments, clientid)
    elif command in ['prot', 'protect']:
        protect_players(arguments, clientid)

    elif command == 'pme':
        stats_to_clientid(arguments, clientid, accountid)
    elif command == 'rainbow':
        rainbow(arguments, clientid)
    elif command == 'rocket':
        rocket(arguments, clientid)
    elif command == 'swap':
        swap(arguments, clientid)
    elif command == 'party':
        party(arguments, clientid)


# ── helpers ──────────────────────────────────────────────────

def _activity():
    return bs.get_foreground_host_activity()


# ── commands ─────────────────────────────────────────────────

def stats_to_clientid(arguments, clid, acid):
    activity = _activity()
    if not arguments or arguments == ['']:
        send("Using: /pme [ClientID]", clid)
        return
    cl_id = int(arguments[0])
    fname = ''
    pbid = ''
    for pla in bs.get_foreground_host_session().sessionplayers:
        if pla.inputdevice.client_id == cl_id:
            fname = pla.getname(full=True, icon=True)
    for roe in bs.get_game_roster():
        if roe['client_id'] == cl_id:
            pbid = roe['account_id']
    stats = mystats.get_stats_by_id(pbid) if pbid else None
    if stats:
        reply = (
            f"\ue048| Name: {fname}\n"
            f"\ue048| PB-ID: {stats['aid']}\n"
            f"\ue048| Rank: {stats['rank']}\n"
            f"\ue048| Score: {stats['scores']}\n"
            f"\ue048| Games: {stats['games']}\n"
            f"\ue048| Kills: {stats['kills']}\n"
            f"\ue048| Deaths: {stats['deaths']}\n"
            f"\ue048| Avg.: {stats['avg_score']}\n"
        )
        send(reply, clid)
    else:
        send("Not played any match yet.", clid)


def hug(arguments, clientid):
    players = _activity().players
    if not arguments or arguments == ['']:
        send("Using: /hug [player1Index] [player2Index]", clientid)
        return
    try:
        players[int(arguments[0])].actor.node.hold_node = players[int(arguments[1])].actor.node
    except Exception:
        pass


def hugall(arguments, clientid):
    players = _activity().players
    pairs = [(0,1),(1,0),(2,3),(3,2),(4,5),(5,4),(6,7),(7,6)]
    for a, b in pairs:
        try:
            players[a].actor.node.hold_node = players[b].actor.node
        except Exception:
            pass


def kickall(arguments, clientid):
    try:
        for i in bs.get_game_roster():
            if i['client_id'] != clientid:
                _bascenev1.disconnect_client(i['client_id'])
    except Exception:
        pass


def server_chat(arguments, clientid):
    if not arguments:
        bs.broadcastmessage('Usage: /say <text>', transient=True, clients=[clientid])
    else:
        bs.chatmessage(' '.join(arguments))


def box(arguments, clientid):
    players = _activity().players
    try:
        n = int(arguments[0])
        nd = players[n].actor.node
        nd.torso_model        = bs.getmesh('tnt')
        nd.color_mask_texture = bs.gettexture('tnt')
        nd.color_texture      = bs.gettexture('tnt')
        nd.highlight          = (1, 1, 1)
        nd.color              = (1, 1, 1)
        nd.head_model         = None
        nd.style              = 'cyborg'
    except Exception:
        send("Using: /box [PlayerID]", clientid)


def boxall(arguments, clientid):
    for i in _activity().players:
        try:
            nd = i.actor.node
            nd.torso_model        = bs.getmesh('tnt')
            nd.color_mask_texture = bs.gettexture('tnt')
            nd.color_texture      = bs.gettexture('tnt')
            nd.highlight          = (1, 1, 1)
            nd.color              = (1, 1, 1)
            nd.head_model         = None
            nd.style              = 'cyborg'
        except Exception:
            pass


def ac(arguments, clientid):
    activity = _activity()
    a = arguments
    try:
        if a[0] == 'r':
            m = float(a[1]) if len(a) > 1 else 1.3
            s = float(a[2]) if len(a) > 2 else 1000
            bs.animate_array(activity.globalsnode, 'ambient_color', 3,
                             {0: (m,0,0), s:(0,m,0), s*2:(0,0,m), s*3:(m,0,0)}, loop=True)
        else:
            activity.globalsnode.ambient_color = (float(a[0]), float(a[1]), float(a[2]))
    except Exception:
        send("Using: /ac [R] [G] [B]  or  /ac r [brightness] [speed]", clientid)


def tint(arguments, clientid):
    activity = _activity()
    a = arguments
    try:
        if a[0] == 'r':
            m = float(a[1]) if len(a) > 1 else 1.3
            s = float(a[2]) if len(a) > 2 else 1000
            bs.animate_array(activity.globalsnode, 'tint', 3,
                             {0: (m,0,0), s:(0,m,0), s*2:(0,0,m), s*3:(m,0,0)}, loop=True)
        else:
            activity.globalsnode.tint = (float(a[0]), float(a[1]), float(a[2]))
    except Exception:
        send("Using: /tint [R] [G] [B]  or  /tint r [brightness] [speed]", clientid)


def spaz(arguments, clientid):
    players = _activity().players
    _VALID = ['ali','wizard','cyborg','penguin','agent','pixie','bear','bunny']
    try:
        n    = int(arguments[0])
        name = arguments[1].lower()
        if name not in _VALID:
            send("Invalid name. Choose: " + ', '.join(_VALID), clientid)
            return
        nd = players[n].actor.node
        nd.color_texture      = bs.gettexture(name + 'Color')
        nd.color_mask_texture = bs.gettexture(name + 'ColorMask')
        nd.head_model         = bs.getmesh(name + 'Head')
        nd.torso_model        = bs.getmesh(name + 'Torso')
        nd.pelvis_model       = bs.getmesh(name + 'Pelvis')
        nd.upper_arm_model    = bs.getmesh(name + 'UpperArm')
        nd.forearm_model      = bs.getmesh(name + 'ForeArm')
        nd.hand_model         = bs.getmesh(name + 'Hand')
        nd.upper_leg_model    = bs.getmesh(name + 'UpperLeg')
        nd.lower_leg_model    = bs.getmesh(name + 'LowerLeg')
        nd.toes_model         = bs.getmesh(name + 'Toes')
        nd.style              = name
    except Exception:
        send("Using: /spaz [PlayerID] [CharacterName]", clientid)


def spazall(arguments, clientid):
    _VALID = ['ali','wizard','cyborg','penguin','agent','pixie','bear','bunny']
    try:
        name = arguments[0].lower()
        if name not in _VALID:
            send("Invalid name. Choose: " + ', '.join(_VALID), clientid)
            return
        for i in _activity().players:
            try:
                nd = i.actor.node
                nd.color_texture      = bs.gettexture(name + 'Color')
                nd.color_mask_texture = bs.gettexture(name + 'ColorMask')
                nd.head_model         = bs.getmesh(name + 'Head')
                nd.torso_model        = bs.getmesh(name + 'Torso')
                nd.pelvis_model       = bs.getmesh(name + 'Pelvis')
                nd.upper_arm_model    = bs.getmesh(name + 'UpperArm')
                nd.forearm_model      = bs.getmesh(name + 'ForeArm')
                nd.hand_model         = bs.getmesh(name + 'Hand')
                nd.upper_leg_model    = bs.getmesh(name + 'UpperLeg')
                nd.lower_leg_model    = bs.getmesh(name + 'LowerLeg')
                nd.toes_model         = bs.getmesh(name + 'Toes')
                nd.style              = name
            except Exception:
                pass
    except Exception:
        send("Using: /spazall [CharacterName]", clientid)


def zombie(arguments, clientid):
    players = _activity().players
    try:
        n  = int(arguments[0])
        nd = players[n].actor.node
        nd.color_texture      = bs.gettexture('agentColor')
        nd.color_mask_texture = bs.gettexture('pixieColorMask')
        nd.head_model         = bs.getmesh('zoeHead')
        nd.torso_model        = bs.getmesh('bonesTorso')
        nd.pelvis_model       = bs.getmesh('pixiePelvis')
        nd.upper_arm_model    = bs.getmesh('frostyUpperArm')
        nd.forearm_model      = bs.getmesh('frostyForeArm')
        nd.hand_model         = bs.getmesh('bonesHand')
        nd.upper_leg_model    = bs.getmesh('bonesUpperLeg')
        nd.lower_leg_model    = bs.getmesh('pixieLowerLeg')
        nd.toes_model         = bs.getmesh('bonesToes')
        nd.color              = (0, 1, 0)
        nd.highlight          = (0.6, 0.6, 0.6)
        nd.style              = 'spaz'
    except Exception:
        send("Using: /zombie [PlayerID]", clientid)


def zombieall(arguments, clientid):
    for i in _activity().players:
        try:
            nd = i.actor.node
            nd.color_texture      = bs.gettexture('agentColor')
            nd.color_mask_texture = bs.gettexture('pixieColorMask')
            nd.head_model         = bs.getmesh('zoeHead')
            nd.torso_model        = bs.getmesh('bonesTorso')
            nd.pelvis_model       = bs.getmesh('pixiePelvis')
            nd.upper_arm_model    = bs.getmesh('frostyUpperArm')
            nd.forearm_model      = bs.getmesh('frostyForeArm')
            nd.hand_model         = bs.getmesh('bonesHand')
            nd.upper_leg_model    = bs.getmesh('bonesUpperLeg')
            nd.lower_leg_model    = bs.getmesh('pixieLowerLeg')
            nd.toes_model         = bs.getmesh('bonesToes')
            nd.color              = (0, 1, 0)
            nd.highlight          = (0.6, 0.6, 0.6)
            nd.style              = 'spaz'
        except Exception:
            pass


def tex(arguments, clientid):
    players = _activity().players
    try:
        n     = int(arguments[0])
        tname = arguments[1]
        color = tname if tname == 'kronk' else tname + 'Color'
        players[n].actor.node.color_mask_texture = bs.gettexture(tname + 'ColorMask')
        players[n].actor.node.color_texture      = bs.gettexture(color)
    except Exception:
        send("Using: /tex [PlayerID] [texture]", clientid)


def texall(arguments, clientid):
    try:
        tname = arguments[0]
        color = tname if tname == 'kronk' else tname + 'Color'
        for i in _activity().players:
            try:
                i.actor.node.color_mask_texture = bs.gettexture(tname + 'ColorMask')
                i.actor.node.color_texture      = bs.gettexture(color)
            except Exception:
                pass
    except Exception:
        send("Using: /texall [texture]", clientid)


def control(arguments, clientid):
    players = _activity().players
    try:
        p1 = int(arguments[0])
        p2 = int(arguments[1])
        n1 = players[p1].actor.node
        n2 = players[p2].actor.node
        players[p1].actor.node = n2
        players[p2].actor.node = n1
    except Exception:
        send("Using: /exchange [PlayerID1] [PlayerID2]", clientid)


def zm(arguments, clientid):
    if not arguments:
        bs.broadcastmessage("Usage: /zm [message]", transient=True, clients=[clientid])
        return
    k = ' '.join(arguments)
    with _activity().context:
        ZoomText(
            k,
            position=(0, 180),
            maxwidth=800,
            lifespan=0.9,
            color=(0.93*1.25, 0.9*1.25, 1.0*1.25),
            trailcolor=(0.15, 0.05, 1.0, 0.0),
            flash=False,
            jitter=3.0,
        ).autoretain()


def icy(arguments, clientid):
    players = _activity().players
    try:
        p1 = int(arguments[0])
        p2 = int(arguments[1])
        players[p1].actor.node = players[p2].actor.node
    except Exception:
        send("Using: /icy [PlayerID1] [PlayerID2]", clientid)


def play_ooh_sound(arguments):
    activity = _activity()
    with activity.context:
        try:
            times = int(arguments[0]) if arguments else 1
            def _ooh(c):
                bs.getsound('ooh').play(volume=2)
                c -= 1
                if c > 0:
                    delay = int(arguments[1]) / 1000.0 if len(arguments) > 1 else 1.0
                    bs.timer(delay, babase.CallPartial(_ooh, c))
            _ooh(times)
        except Exception:
            pass


def play_sound(arguments, clientid):
    activity = _activity()
    with activity.context:
        try:
            sound_name = str(arguments[0])
            times      = int(arguments[1])   if len(arguments) > 1 else 1
            volume     = float(arguments[2]) if len(arguments) > 2 else 2.0
            delay      = int(arguments[3]) / 1000.0 if len(arguments) > 3 else 1.0
            def _play(c):
                bs.getsound(sound_name).play(volume=volume)
                c -= 1
                if c > 0:
                    bs.timer(delay, babase.CallPartial(_play, c))
            _play(times)
        except Exception:
            send("Using: /playsound [sound] [times] [volume] [delay_ms]", clientid)


def protect_players(arguments, clientid):
    activity = _activity()
    if not arguments or arguments == ['']:
        idx    = clientid_to_myself(clientid)
        player = activity.players[idx].actor
        player.node.invincible = not player.node.invincible
    elif arguments[0] == 'all':
        for i in activity.players:
            try:
                i.actor.node.invincible = not i.actor.node.invincible
            except Exception:
                pass
    else:
        try:
            player = activity.players[int(arguments[0])].actor
            player.node.invincible = not player.node.invincible
        except Exception:
            send("Using: /prot [PlayerID or 'all']", clientid)


def d_bomb_count(arguments, clientid):
    if not arguments:
        send("Usage: /dbc (clientid) (count) or /dbc all (count)", clientid)
        return
    activity = _activity()
    if arguments[0] == 'all':
        count = 2 if len(arguments) < 2 or arguments[1] == 'reset' else int(arguments[1])
        for player in activity.players:
            player.actor.set_bomb_count(count)
        sendall(f"Bomb count set to {count}")
    else:
        try:
            target_id = int(arguments[0])
            count     = 2 if len(arguments) < 2 or arguments[1] == 'reset' else int(arguments[1])
            for player in activity.players:
                if player.sessionplayer.inputdevice.client_id == target_id:
                    player.actor.set_bomb_count(count)
                    send(f"Bomb count set to {count}", clientid)
                    return
            send(f"Client {target_id} not found", clientid)
        except Exception:
            send("Usage: /dbc (clientid) (count)", clientid)


def d_bomb_type(arguments, clientid):
    if not arguments:
        send("Usage: /dbt (type) all or /dbt (type) (clientid). /dbt help", clientid)
        return
    activity = _activity()
    VALID = ['ice','impact','land_mine','normal','sticky','tnt','fly']
    if arguments[0] == 'help':
        send("types: " + ', '.join(VALID) + "\nReset: /dbt reset all", clientid)
        return
    btype = arguments[0] if arguments[0] != 'reset' else 'normal'
    if btype not in VALID:
        send("Unknown type. /dbt help", clientid)
        return
    target = arguments[1] if len(arguments) > 1 else 'all'
    if target == 'all':
        for player in activity.players:
            try: player.actor.bomb_type = btype
            except Exception: pass
        send(f"Bomb type set to {btype} for all", clientid)
    else:
        try:
            tid = int(target)
            for player in activity.players:
                if player.sessionplayer.inputdevice.client_id == tid:
                    player.actor.bomb_type = btype
                    send(f"Bomb type set to {btype}", clientid)
                    return
            send(f"Client {tid} not found", clientid)
        except Exception:
            send("Usage: /dbt (type) (clientid)", clientid)


def acl(arguments, client_id):
    admin_commands = pdata.roles_cmdlist('admin')
    if not admin_commands:
        send("Error: Admin role not found.", client_id)
        return
    msg = "\ue046 ADMIN CMDS:\n" + admin_commands
    send(msg, client_id)


def vcl(arguments, client_id):
    vip_commands = pdata.roles_cmdlist('vip')
    if not vip_commands:
        send("Error: VIP role not found.", client_id)
        return
    msg = "\ue046 VIP CMDS:\n" + vip_commands
    send(msg, client_id)


def rainbow(arguments, clientid):
    activity = _activity()
    try:
        m = float(arguments[0]) if arguments else 1.3
        s = float(arguments[1]) if len(arguments) > 1 else 1.0
        bs.animate_array(activity.globalsnode, 'tint', 3,
                         {0:(m,0,0), s:(0,m,0), s*2:(0,0,m), s*3:(m,0,0)}, loop=True)
    except Exception:
        send("Using: /rainbow [brightness] [speed]", clientid)


# ══════════════════════════════════════════════════════════
#  أوامر متعة
# ══════════════════════════════════════════════════════════

def _get_player(arguments, clientid):
    """يُرجع player من client_id أو اللاعع نفسه."""
    activity = _activity()
    if activity is None:
        return None
    players = activity.players
    if not players:
        return None

    # بدون arguments — ابحث عن اللاعع نفسه بالـ client_id
    if not arguments or arguments == [''] or arguments == []:
        for p in players:
            try:
                if p.sessionplayer.inputdevice.client_id == clientid:
                    return p
            except Exception:
                pass
        # fallback — أول لاعع
        return players[0] if players else None

    # بـ client_id
    try:
        tid = int(arguments[0])
        for p in players:
            try:
                if p.sessionplayer.inputdevice.client_id == tid:
                    return p
            except Exception:
                pass
    except Exception:
        pass
    return None


def _player_in_game(p) -> bool:
    """تحقق أن اللاعع في اللعبة وعنده node."""
    try:
        return p is not None and p.actor is not None and p.actor.node.exists()
    except Exception:
        return False


def rocket(arguments, clientid):
    """يطير اللاعب للأعلى بسرعة."""
    p = _get_player(arguments, clientid)
    if not _player_in_game(p):
        send("Not in game!", clientid); return
    try:
        nd = p.actor.node
        with _activity().context:
            for i in range(20):
                bs.timer(i * 0.05, babase.CallPartial(
                    nd.handlemessage, 'impulse',
                    nd.position[0], nd.position[1], nd.position[2],
                    0, 20, 0, 5, 10, 0, 0, 0, 20, 0
                ))
    except Exception as _e:
        send(f"/rocket error: {_e}", clientid)


def swap(arguments, clientid):
    """يبدّل موقع لاعبين."""
    activity = _activity()
    try:
        id1 = int(arguments[0])
        id2 = int(arguments[1])
        p1 = p2 = None
        for p in activity.players:
            cid = p.sessionplayer.inputdevice.client_id
            if cid == id1: p1 = p
            if cid == id2: p2 = p
        if p1 and p2:
            pos1 = tuple(p1.actor.node.position)
            pos2 = tuple(p2.actor.node.position)
            p1.actor.node.handlemessage(bs.StandMessage(pos2, 0))
            p2.actor.node.handlemessage(bs.StandMessage(pos1, 0))
        else:
            send("Players not found", clientid)
    except Exception:
        send("Usage: /swap [client_id1] [client_id2]", clientid)


def party(arguments, clientid):
    """جميع اللاعبين يحتفلون."""
    for p in _activity().players:
        try:
            p.actor.node.handlemessage('celebrate', 5.0)
        except Exception:
            pass
    bs.broadcastmessage(" PARTY TIME! ", color=(1, 0.5, 0))


