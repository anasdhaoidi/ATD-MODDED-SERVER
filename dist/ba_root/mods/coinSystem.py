"""نظام العملات والأسئلة — API 9 (BombSquad 1.7.62)"""
from __future__ import annotations
import os
import json
import random
import logging
import babase
import bascenev1 as bs

# ═══════════════════════════════════════════════
#  إعدادات
# ═══════════════════════════════════════════════
def _get_settings() -> dict:
    try:
        import setting
        return setting.get_settings_data().get('CoinSystem', {})
    except Exception:
        return {}

_BANK_PATH: str = ''

def _coin_cfg(key: str, default=None):
    return _get_settings().get(key, default)

def _get_bank_path() -> str:
    global _BANK_PATH
    if not _BANK_PATH:
        try:
            # Android و Linux
            user_dir = babase.app.env.python_directory_user
            _BANK_PATH = user_dir + '/bank.json'
        except Exception:
            # fallback مسار ثابت
            _BANK_PATH = 'ba_root/mods/bank.json'
    return _BANK_PATH

# ═══════════════════════════════════════════════
#  قائمة الأسئلة
# ═══════════════════════════════════════════════
QUESTIONS: dict = {
    'What is the capital of France?':          ['paris'],
    'How many sides does a triangle have?':    ['3', 'three'],
    'What color is the sky?':                  ['blue'],
    'add':                                     [None],
    'multiply':                                [None],
}

def _get_questions() -> dict:
    q = _get_settings().get('questions', {})
    return q if q else QUESTIONS

# ═══════════════════════════════════════════════
#  حالة الجولة الحالية
# ═══════════════════════════════════════════════
_correct_answer: list[str] | None = None
_answered_by:    str | None       = None
_question_timer: bs.AppTimer | None = None


# ═══════════════════════════════════════════════
#  العملات
# ═══════════════════════════════════════════════
def add_coins(account_id: str, amount: int) -> None:
    import _thread
    try:
        from playersdata import pdata
        custom = pdata.get_custom()
        custom.setdefault('coins', {})
        custom['coins'].setdefault(account_id, 0)
        custom['coins'][account_id] += amount
        _thread.start_new_thread(pdata.dump_cache, ())
    except Exception as _e:
        logging.warning(f'ATD: add_coins error: {_e}')
    if amount > 0:
        try:
            bs.getsound('cashRegister').play()
        except Exception:
            pass


def get_coins(account_id: str) -> int:
    try:
        from playersdata import pdata
        custom = pdata.get_custom()
        return custom.get('coins', {}).get(account_id, 0)
    except Exception:
        return 0


def set_coins(account_id: str, amount: int) -> None:
    """تعيين رصيد مباشر."""
    try:
        from playersdata import pdata
        custom = pdata.get_custom()
        if 'coins' not in custom:
            custom['coins'] = {}
        custom['coins'][account_id] = amount
        pdata.dump_cache()
    except Exception as _e:
        logging.warning(f'ATD: set_coins error: {_e}')


# ═══════════════════════════════════════════════
#  الأسئلة
# ═══════════════════════════════════════════════
def ask_question() -> None:
    global _correct_answer, _answered_by
    _answered_by = None

    questions = _get_questions()
    keys = list(questions.keys())
    question = random.choice(keys)
    _correct_answer = questions[question]

    if question == 'add':
        a = random.randint(100, 999)
        b = random.randint(10, 99)
        _correct_answer = [str(a + b)]
        question = f'❓ What is {a} + {b}?'
    elif question == 'multiply':
        a = random.randint(10, 99)
        b = random.choice([2, 3, 5, 10])
        _correct_answer = [str(a * b)]
        question = f'❓ What is {a} × {b}?'
    else:
        question = f'❓ {question}'

    tic    = _coin_cfg('currency', '\ue01f')
    reward = _coin_cfg('rewardAmount', 10)
    bs.chatmessage(f'{question}  ➜  First correct answer wins {tic}{reward}!')


def check_answer(msg: str, client_id: int) -> bool:
    """يُستدعى من filter_chat — يُرجع True إذا كانت إجابة صحيحة."""
    global _answered_by
    if _correct_answer is None:
        return False
    if msg.strip().lower() not in [a.lower() for a in _correct_answer if a]:
        return False
    if _answered_by is not None:
        bs.broadcastmessage(
            f'Already answered by {_answered_by}!',
            color=(1, 0.3, 0.3),
        )
        return True

    # ابحث عن اسم اللاعع و account_id
    player_name = str(client_id)
    account_id  = None
    try:
        for ros in bs.get_game_roster():
            if ros['client_id'] == client_id:
                try:
                    player_name = ros['players'][0]['name_full']
                except Exception:
                    player_name = ros.get('display_string', str(client_id))
                account_id = ros.get('account_id')
                break
        # إذا لم يُجد في roster (host) ابحث في session
        if account_id is None:
            try:
                session = bs.get_foreground_host_session()
                for sp in session.sessionplayers:
                    if sp.inputdevice.client_id == client_id:
                        account_id = sp.get_account_id()
                        player_name = sp.getname(full=True, icon=True)
                        break
            except Exception:
                pass
    except Exception:
        pass

    _answered_by = player_name
    reward = _coin_cfg('rewardAmount', 10)
    tic    = _coin_cfg('currency', '\ue01f')

    # رسالة chat تظهر للجميع
    bs.chatmessage(f'✅ {player_name} answered correctly and won {tic}{reward}!')
    if account_id:
        add_coins(account_id, reward)
    return True


# ═══════════════════════════════════════════════
#  تفعيل النظام
# ═══════════════════════════════════════════════
def enable() -> None:
    global _question_timer
    if not _coin_cfg('enable', True):
        return
    # تأكد من وجود coins في custom.json
    try:
        from playersdata import pdata
        custom = pdata.get_custom()
        if 'coins' not in custom:
            custom['coins'] = {}
            logging.warning('ATD: Initialized coins in custom.json')
    except Exception as _e:
        logging.warning(f'ATD: coins init error: {_e}')
    if _coin_cfg('askQuestions', True):
        delay = _coin_cfg('questionDelay', 60)
        _question_timer = bs.AppTimer(delay, ask_question, repeat=True)
        logging.warning('ATD: Coin system loaded.')


# ═══════════════════════════════════════════════
#  مكافأة أفضل 3 لاعبين كل minigame
# ═══════════════════════════════════════════════
def reward_top_players(stats) -> None:
    """يعطي نقود لأفضل 3 لاعبين بالـ score كل نهاية minigame."""
    try:
        if stats is None:
            return
        REWARDS = [20, 15, 10]
        tic = _coin_cfg('currency', '')

        # جلب records وترتيبها تنازلياً بالـ score
        records = list(stats.get_records().values())

        # فحص عدد اللاعبين — يجب أن يكون 2 على الأقل
        active = [r for r in records if getattr(r, 'player', None) and r.player.exists()]
        if len(active) < 2:
            bs.chatmessage('⚠️ Not enough players to award coins!')
            return

        records.sort(key=lambda r: r.accumscore if hasattr(r, 'accumscore') else 0, reverse=True)

        for i, rec in enumerate(records[:3]):
            if i >= len(REWARDS):
                break
            try:
                reward = REWARDS[i]
                player = getattr(rec, 'player', None)
                if player is None or not player.exists():
                    continue
                account_id = player.get_account_id()
                if not account_id:
                    continue
                name = player.getname(full=True, icon=False)
                add_coins(account_id, reward)
                bs.chatmessage(f'🏆 #{i+1} {name} earned {tic}{reward} coins!')
            except Exception:
                continue
    except Exception as _e:
        import logging
        logging.warning(f'reward_top_players error: {_e}')
