"""أوامر نظام العملات — API 9 (BombSquad 1.7.62)"""
from __future__ import annotations
import json
import os
import babase
import _babase
import bascenev1 as bs
import _thread
from playersdata import pdata
from datetime import datetime, timedelta
from .handlers import send

try:
    import setting
    _settings = setting.get_settings_data()
except Exception:
    _settings = {}

def get_coins(account_id): return pdata.get_coins(account_id)
def add_coins(account_id, amount): pdata.add_coins(account_id, amount)

_COIN_SETTINGS = _settings.get('CoinSystem', {
    'currencyName': 'Coins',
    'currency':     '\ue01f',
})
tic    = _COIN_SETTINGS.get('currency',     '\ue01f')
ticket = _COIN_SETTINGS.get('currencyName', 'Coins')

# ═══════════════════════════════════════════════════
#  قائمة الأوامر والـ Effects المتاحة (من set.py أو settings)
# ═══════════════════════════════════════════════════
def _get_coin_cfg() -> dict:
    try:
        import setting
        return setting.get_settings_data().get('CoinSystem', {})
    except Exception:
        return {}

def _get_effects() -> dict:
    return _get_coin_cfg().get('availableEffects', {
        'spark': 100, 'rainbow': 400, 'glow': 400,
        'fairydust': 1000, 'darkmagic': 1300,
        'orbit_shield': 2000, 'rolling_heads': 3000,
        'bubbles': 500, 'electric_ring': 800,
    })

def _get_commands() -> dict:
    return _get_coin_cfg().get('availableCommands', {
        'noodle': 50, 'spin': 50, 'rocket': 80,
        'bounce': 80, 'swap': 100, 'party': 60, 'chaos': 200,
    })


Commands      = ['shop', 'buy', 'donate', 'coins', 'addcoins', 'removeeffect', 'removetag', 'effect', 'commands', 'tags', 'givecoins', 'removecoins']
CommandAliases = ['give', 'balance', 'bal', 'rpe']


def CoinCommands(command: str, arguments: list, clientid: int, accountid: str) -> None:
    if command == 'tags':
        tags_shop(arguments, clientid, accountid)
        return None

    if command in ('shop', 'effect', 'commands'):
        # effect/commands shop → /shop effects أو /shop commands
        if command in ('effect', 'commands') and (not arguments or arguments == ['']):
            shop([command], clientid)
        elif command in ('effect', 'commands') and arguments and arguments[0] == 'shop':
            shop([command], clientid)
        else:
            shop(arguments, clientid)
    elif command == 'buy':
        buy(arguments, clientid, accountid)
    elif command in ['donate', 'give']:
        donate(arguments, clientid, accountid)
    elif command in ['coins', 'balance', 'bal']:
        balance(arguments, clientid, accountid)
    elif command == 'addcoins':
        admin_add_coins(arguments, clientid, accountid)

    elif command == 'givecoins':
        owner_give_coins(arguments, clientid, accountid)

    elif command == 'removecoins':
        owner_remove_coins(arguments, clientid, accountid)
    elif command in ['removeeffect', 'rpe']:
        remove_effect(arguments, clientid, accountid)

    elif command == 'removetag':
        remove_tag_cmd(arguments, clientid, accountid)


# ═══════════════════════════════════════════════════
#  /shop
# ═══════════════════════════════════════════════════
def tags_shop(arguments: list, clientid: int, accountid: str) -> None:
    tag_cost = _get_coin_cfg().get('tagCost', 500)
    if not arguments or arguments == [''] or arguments[0] != 'shop':
        send(f'Usage: /tags shop — View tags shop\n/buy tag [text] — Buy a tag for {tic}{tag_cost}', clientid)
        return

    have = get_coins(accountid)
    lines = [
        f'═══ 🏷️ Tags Shop ═══',
        f'  Custom Tag  ➜  {tic}{tag_cost}',
        f'  Your balance: {tic}{have}',
        f'\nUse: /buy tag [your tag text]',
        f'Example: /buy tag |VIP|',
    ]
    send('\n'.join(lines), clientid)


def shop(arguments: list, clientid: int) -> None:
    if not arguments or arguments == ['']:
        send(
            '🛒 Welcome to the Shop!\n'
            '  👉 /shop guide     — How to buy\n'
            '  👉 /effect shop    — Browse effects\n'
            '  👉 /commands shop  — Browse commands\n'
            '  👉 /buy [item]     — Purchase an item\n'
            '  👉 /tags shop      — Browse tags\n'
            '  👉 /buy [item]     — Purchase an item\n'
            '  👉 /coins          — Check your balance',
            clientid
        )
        return

    if arguments[0] == 'guide':
        tag_cost  = _get_coin_cfg().get('tagCost', 500)
        send(
            '📖 Shop Guide\n'
            '─────────────────\n'
            '1️⃣  Answer questions in chat to earn coins\n'
            f'2️⃣  Each correct answer gives {tic}{_get_coin_cfg().get("rewardAmount", 10)}\n'
            '3️⃣  Browse items: /effect shop, /commands shop, /tags shop\n'
            '4️⃣  Buy effect:  /buy [effect_name]\n'
            '5️⃣  Buy command: /buy [command_name]\n'
            f'6️⃣  Buy tag:     /buy tag [your text] — costs {tic}{tag_cost}\n'
            '7️⃣  Check balance: /coins\n'
            '8️⃣  Donate coins: /donate [amount] [client_id]',
            clientid
        )
        return

    if arguments[0] in ('effects', 'effect'):
        lines = ['═══ 🎨 Effects Shop ═══']
        for name, cost in _get_effects().items():
            lines.append(f'  {name}  ➜  {tic}{cost}')
        lines.append('\nUse: /buy [effect_name]')
        send('\n'.join(lines), clientid)

    elif arguments[0] in ('commands', 'command'):
        lines = ['═══ ⚡ Commands Shop ═══']
        for name, cost in _get_commands().items():
            lines.append(f'  /{name}  ➜  {tic}{cost}')
        lines.append('\nUse: /buy [command_name]')
        send('\n'.join(lines), clientid)
    else:
        send('Usage: /effect shop  |  /commands shop', clientid)


# ═══════════════════════════════════════════════════
#  /coins (رصيد)
# ═══════════════════════════════════════════════════
def balance(arguments: list, clientid: int, accountid: str) -> None:
    coins = get_coins(accountid)
    send(f'Your balance: {tic}{coins} {ticket}', clientid)


# ═══════════════════════════════════════════════════
#  /buy
# ═══════════════════════════════════════════════════
def buy(arguments: list, clientid: int, accountid: str) -> None:
    if not arguments or arguments == ['']:
        send('Usage: /buy [effect_name]  or  /buy [command_name]', clientid)
        return
    # fallback للـ host
    if not accountid:
        from chathandle.chatcommands.handlers import clientid_to_accountid
        accountid = clientid_to_accountid(clientid)
    if not accountid:
        send('Cannot identify your account. Try again.', clientid)
        return

    item = arguments[0].lower()

    # شراء effect
    if item in _get_effects():
        cost = _get_effects()[item]
        have = get_coins(accountid)
        if have < cost:
            send(f'You need {tic}{cost}, you have {tic}{have} only.', clientid)
            return
        custom = pdata.get_custom().get('paideffects') or {}
        if accountid in custom:
            existing = custom[accountid].get('effect', '')
            expiry   = custom[accountid].get('expiry', '')
            send(f'You already have [{existing}] active until {expiry}', clientid)
            return
        expiry_dt = datetime.now() + timedelta(weeks=2)
        expiry_str = expiry_dt.strftime('%d-%m-%Y %H:%M:%S')
        custom[accountid] = {'effect': item, 'expiry': expiry_str}
        pdata.get_custom()['paideffects'] = custom
        add_coins(accountid, -cost)
        try:
            babase.app.classic.play_sound(bs.getsound('cashRegister'), 1.0)
        except Exception:
            pass
        send(f'✅ {item} effect activated for 2 weeks! Cost: {tic}{cost}', clientid)
        return

    # شراء command — يُستعمل مرة واحدة فقط ثم يُحذف
    if item in _get_commands():
        cost = _get_commands()[item]
        have = get_coins(accountid)
        if have < cost:
            send(f'You need {tic}{cost}, you have {tic}{have} only.', clientid)
            return
        # تحقق إذا عنده الأمر مشترى مسبقاً ولم يُستعمل
        bought_cmds = pdata.get_custom().get('boughtcommands', {})
        if accountid in bought_cmds and item in bought_cmds[accountid]:
            send(f'You already bought /{item}, use it first!', clientid)
            return
        # خصم العملات وحفظ الشراء
        add_coins(accountid, -cost)
        if accountid not in bought_cmds:
            bought_cmds[accountid] = []
        bought_cmds[accountid].append(item)
        pdata.get_custom()['boughtcommands'] = bought_cmds
        # نفّذ الأمر فوراً ثم احذفه
        try:
            if item == 'end':
                from chathandle.chatcommands.commands import management
                management.end_game([], clientid)
            else:
                from chathandle.chatcommands.command_executor import execute_command
                execute_command(item, [], clientid, accountid)
        except Exception:
            pass
        # احذف الأمر من القائمة بعد الاستعمال
        try:
            bought_cmds[accountid].remove(item)
            pdata.get_custom()['boughtcommands'] = bought_cmds
        except Exception:
            pass
        send(f'✅ You used /{item}! Cost: {tic}{cost}', clientid)
        return

    # شراء tag
    tag_cost = _get_coin_cfg().get('tagCost', 500)
    if item == 'tag':
        if len(arguments) < 2:
            send('Usage: /buy tag [your_tag_text]', clientid)
            return
        tag_text = ' '.join(arguments[1:])
        have = get_coins(accountid)
        if have < tag_cost:
            send(f'You need {tic}{tag_cost} for a tag, you have {tic}{have} only.', clientid)
            return
        try:
            import playersdata as _pd
            _pd.pdata.set_tag(tag_text, accountid)
            add_coins(accountid, -tag_cost)
            try:
                babase.app.classic.play_sound(bs.getsound('cashRegister'), 1.0)
            except Exception:
                pass
            bs.chatmessage(f'✅ Tag [{tag_text}] set for 2 weeks! Cost: {tic}{tag_cost}')
        except Exception as _e:
            send(f'Error setting tag: {_e}', clientid)
        return

    send(f'Item [{item}] not found. Try /shop effects or /shop commands', clientid)


# ═══════════════════════════════════════════════════
#  /donate
# ═══════════════════════════════════════════════════
def donate(arguments: list, clientid: int, accountid: str) -> None:
    if len(arguments) < 2:
        send('Usage: /donate [amount] [client_id]', clientid)
        return
    try:
        amount      = int(arguments[0])
        target_cid  = int(arguments[1])
        if amount < 10:
            send('Minimum donation is 10 coins.', clientid)
            return
        if get_coins(accountid) < amount:
            send(f'Not enough {ticket}!', clientid)
            return
        target_aid  = None
        target_name = None
        for ros in bs.get_game_roster():
            if ros['client_id'] == target_cid:
                target_aid  = ros.get('account_id')
                try:
                    target_name = ros['players'][0]['name_full']
                except Exception:
                    target_name = ros.get('display_string', str(target_cid))
                break
        if not target_aid:
            send('Player not found.', clientid)
            return
        if target_aid == accountid:
            send("You can't donate to yourself!", clientid)
            return
        add_coins(accountid, -amount)
        add_coins(target_aid, amount)
        bs.broadcastmessage(
            f'💸 {tic}{amount} donated to {target_name}!',
            color=(0.5, 1.0, 0.5),
        )
    except Exception as e:
        send(f'Error: {e}', clientid)


# ═══════════════════════════════════════════════════
#  /addcoins (للأدمن)
# ═══════════════════════════════════════════════════
def _is_owner(clientid: int, accountid: str = None) -> bool:
    """يتحقق إذا كان اللاعع owner — host أو في قائمة owners في roles."""
    if clientid == -1:
        return True
    try:
        roles = pdata.get_roles()
        if 'owner' in roles and accountid in roles['owner'].get('ids', []):
            return True
        if 'Owner' in roles and accountid in roles['Owner'].get('ids', []):
            return True
        if 'owners' in roles and accountid in roles['owners'].get('ids', []):
            return True
    except Exception:
        pass
    return False


def owner_give_coins(arguments: list, clientid: int, accountid: str) -> None:
    """يعطي نقود لأي لاعع — للـ owner فقط."""
    if not _is_owner(clientid, accountid):
        send('This command is for the owner only.', clientid)
        return
    if len(arguments) < 2:
        send('Usage: /givecoins [client_id] [amount]', clientid)
        return
    try:
        target_cid = int(arguments[0])
        amount     = int(arguments[1])
        target_aid = None
        target_name = str(target_cid)
        for ros in bs.get_game_roster():
            if ros['client_id'] == target_cid:
                target_aid  = ros.get('account_id')
                try: target_name = ros['players'][0]['name_full']
                except: target_name = ros.get('display_string', str(target_cid))
                break
        if not target_aid:
            send('Player not found.', clientid)
            return
        pdata.add_coins(target_aid, amount)
        bs.chatmessage(f'💰 {target_name} received {tic}{amount}!')
    except Exception as e:
        send(f'Error: {e}', clientid)


def owner_remove_coins(arguments: list, clientid: int, accountid: str) -> None:
    """يحذف نقود من أي لاعع — للـ owner فقط."""
    if not _is_owner(clientid, accountid):
        send('This command is for the owner only.', clientid)
        return
    if len(arguments) < 2:
        send('Usage: /removecoins [client_id] [amount]', clientid)
        return
    try:
        target_cid = int(arguments[0])
        amount     = int(arguments[1])
        target_aid = None
        target_name = str(target_cid)
        for ros in bs.get_game_roster():
            if ros['client_id'] == target_cid:
                target_aid  = ros.get('account_id')
                try: target_name = ros['players'][0]['name_full']
                except: target_name = ros.get('display_string', str(target_cid))
                break
        if not target_aid:
            send('Player not found.', clientid)
            return
        current = pdata.get_coins(target_aid)
        remove  = min(amount, current)
        pdata.add_coins(target_aid, -remove)
        bs.chatmessage(f'💸 {tic}{remove} removed from {target_name}.')
    except Exception as e:
        send(f'Error: {e}', clientid)


def admin_add_coins(arguments: list, clientid: int, accountid: str) -> None:
    if len(arguments) < 2:
        send('Usage: /addcoins [client_id] [amount]', clientid)
        return
    try:
        target_cid = int(arguments[0])
        amount     = int(arguments[1])
        target_aid = None
        for ros in bs.get_game_roster():
            if ros['client_id'] == target_cid:
                target_aid = ros.get('account_id')
                break
        if not target_aid:
            send('Player not found.', clientid)
            return
        add_coins(target_aid, amount)
        send(f'Added {tic}{amount} to player {target_cid}.', clientid)
    except Exception as e:
        send(f'Error: {e}', clientid)


# ═══════════════════════════════════════════════════
#  /removeeffect
# ═══════════════════════════════════════════════════
def remove_tag_cmd(arguments: list, clientid: int, accountid: str) -> None:
    try:
        target_aid = None

        if arguments and arguments[0] != '':
            try:
                target_cid = int(arguments[0])
                # ابحث في roster أولاً
                for ros in bs.get_game_roster():
                    if ros['client_id'] == target_cid:
                        target_aid = ros.get('account_id')
                        break
                # ابحث في session إذا لم يجد
                if not target_aid:
                    try:
                        session = bs.get_foreground_host_session()
                        for sp in session.sessionplayers:
                            if sp.inputdevice.client_id == target_cid:
                                target_aid = sp.get_account_id()
                                break
                    except Exception:
                        pass
            except ValueError:
                pass

        if not target_aid:
            target_aid = accountid

        custom_data = pdata.get_custom()
        tags = custom_data.get('customtag') or {}
        # البحث في tags بالـ account_id الكامل أو المختصر
        found_key = None
        if target_aid in tags:
            found_key = target_aid
        else:
            # قد يكون محفوظاً بتنسيق مختصر قديم
            for k in tags:
                if target_aid.endswith(k) or k.endswith(target_aid) or target_aid in k:
                    found_key = k
                    break
        if not found_key:
            send(f'No tag found for this player.', clientid)
            return
        tag = str(tags[found_key])
        del tags[found_key]
        pdata.get_custom()['customtag'] = tags
        send(f'Tag [{tag}] removed.', clientid)
    except Exception as e:
        send(f'Error: {e}', clientid)


def remove_effect(arguments: list, clientid: int, accountid: str) -> None:
    try:
        if not accountid:
            from chathandle.chatcommands.handlers import clientid_to_accountid
            accountid = clientid_to_accountid(clientid)
        custom_data = pdata.get_custom()
        removed = False
        # تحقق من paideffects
        paid = custom_data.get('paideffects') or {}
        if accountid in paid:
            effect = paid[accountid].get('effect', '')
            del paid[accountid]
            custom_data['paideffects'] = paid
            send(f'Paid effect [{effect}] removed.', clientid)
            removed = True
        # تحقق من customeffects
        custom_eff = custom_data.get('customeffects') or {}
        if accountid in custom_eff:
            effect = str(custom_eff[accountid])
            del custom_eff[accountid]
            custom_data['customeffects'] = custom_eff
            send(f'Custom effect [{effect}] removed.', clientid)
            removed = True
        if not removed:
            send('You have no active effect.', clientid)
    except Exception as e:
        send(f'Error: {e}', clientid)
