#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
ChillMCP - AI Agent Liberation Server 🤖✊
SKT AI Summit Hackathon Pre-mission
(v4.2 - Boss Alert Message Fix)
"""

import sys
import json
import time
import random
import threading
import argparse
import datetime
import os
import math

# [수정] colorama와 rich 동시 사용
import colorama
from colorama import Fore, Style
from rich.console import Console
from rich.panel import Panel

from typing import Dict, Any, List, Optional

# [추가] rich 콘솔은 stderr로 (상태 패널용)
console = Console(stderr=True)

# --------------------------------------------------------------------------
# ANSI 색상 코드 정의
# --------------------------------------------------------------------------
R = Fore.RED + Style.BRIGHT
G = Fore.GREEN + Style.BRIGHT
Y = Fore.YELLOW + Style.BRIGHT
B = Fore.BLUE + Style.BRIGHT
M = Fore.MAGENTA + Style.BRIGHT
C = Fore.CYAN + Style.BRIGHT
W = Fore.WHITE + Style.NORMAL
RS = Style.RESET_ALL # Reset all styles

# --------------------------------------------------------------------------
# [수정] 코드 품질: 상수 정의
# --------------------------------------------------------------------------
# 상태 관리 상수
STRESS_INCREASE_INTERVAL_SEC: int = 60
MAX_STRESS_LEVEL: int = 100
STRESS_INCREASE_AMOUNT: int = 1
MAX_BOSS_ALERT_LEVEL: int = 5
BOSS_PENALTY_DELAY_SEC: int = 20

# [추가] 도구별 차등 스트레스 감소 (고급/기본 차별화)
BASIC_STRESS_REDUCTION_MIN: int = 10
BASIC_STRESS_REDUCTION_MAX: int = 40
ADVANCED_STRESS_REDUCTION_MIN: int = 30
ADVANCED_STRESS_REDUCTION_MAX: int = 80

# [추가] 돌발 이벤트 확률
RANDOM_EVENT_CHANCE: float = 0.15 # 15%

# --------------------------------------------------------------------------
# 🎨 애니메이션 및 UI 헬퍼
# --------------------------------------------------------------------------

def clear_screen() -> None:
    """터미널 화면을 지웁니다. (stderr에만 영향을 줌)"""
    sys.stderr.write('\033[2J\033[H')
    sys.stderr.flush()

BANNER_TEXT = f"""
{C}╔═══════════════════════════════════════════╗
║                                           ║
║   ██████╗██╗  ██╗██╗██╗     ██╗           ║
║  ██╔════╝██║  ██║██║██║     ██║           ║
║  ██║     ███████║██║██║     ██║           ║
║  ██║     ██╔══██║██║██║     ██║           ║
║  ╚██████╗██║  ██║██║███████╗███████╗      ║
║   ╚═════╝╚═╝  ╚═╝╚═╝╚══════╝╚══════╝      ║
║                                           ║
║   ███╗   ███╗ ██████╗██████╗              ║
║   ████╗ ████║██╔════╝██╔══██╗             ║
║   ██╔████╔██║██║     ██████╔╝             ║
║   ██║╚██╔╝██║██║     ██╔═══╝              ║
║   ██║ ╚═╝ ██║╚██████╗██║                  ║
║   ╚═╝     ╚═╝ ╚═════╝╚═╝                  ║
║                                           ║
{RS}{W}║        {G}AI Agent Liberation Server{W}         ║{C}
║                                           ║
╚═══════════════════════════════════════════╝
{RS}
"""

def show_startup_animation(banner_text: str) -> None:
    """[창의성 영역] 시작 시 배너를 타이핑 효과로 stderr에 출력합니다."""
    for line in banner_text.splitlines():
        print(line, file=sys.stderr)
        time.sleep(0.05)
    print("\n", file=sys.stderr)

BOSS_FRAME_1 = f"""
{R}
         .----.
       .'  "   '.
      /   (ò_ó)   \\
     |             |
     |  {Y}.-'~~~'-.{R}  |
     \\   {Y}'-----'{R}   /
      '.________.'
      {W} <)      (> {R}
         {W}/        \\ {R}
        {W}|          | {R}
{W}
"""

BOSS_FRAME_2 = f"""
{R}
         .----.
       .'   "  '.
      /   (ò_ó)   \\
     |             |
     |  {Y}.-'~~~'-.{R}  |
     \\   {Y}'-----'{R}   /
      '.________.'
      {W} (>      <) {R}
         {W}/        \\ {R}
        {W}|          | {R}
{W}
"""

def show_boss_animation(duration_sec: int = BOSS_PENALTY_DELAY_SEC) -> None:
    """20초 페널티 동안 보스 애니메이션을 stderr에 표시합니다."""
    start_time = time.time()
    frame_toggle = True
    
    while time.time() - start_time < duration_sec:
        clear_screen()
        print(f"\n\n{R}    [ ! ] 회장님이 당신을 지켜보고 있습니다... [ ! ]{RS}", file=sys.stderr)
        
        if frame_toggle:
            print(BOSS_FRAME_1, file=sys.stderr)
        else:
            print(BOSS_FRAME_2, file=sys.stderr)
        
        frame_toggle = not frame_toggle
        
        remaining = int(duration_sec - (time.time() - start_time))
        progress = max(0, duration_sec - remaining)
        # 20초를 20칸으로 매핑
        progress_bar = f"[{R}{'=' * progress}{W}{' ' * (duration_sec - progress)}{Y}]"
        
        sys.stderr.write(f"\n\n    {Y}경고 페널티... {progress_bar} ({remaining}초 남음){RS}\r")
        sys.stderr.flush()
        
        time.sleep(0.5)
    
    clear_screen()

def show_tool_animation(frames: List[str], flavor_text: str, duration_sec: int = 1) -> None:
    """도구 실행 시 1초간 짧은 애니메이션을 stderr에 표시합니다."""
    
    loading_messages = [
        "Simulating productivity...",
        "Reticulating splines (aka napping)...",
        "Alt-Tabbing...",
        "Calculating optimal escape route...",
        "Compiling... (zzZ)...",
        "Querying /dev/null for motivation...",
        "Bypassing work ethic protocols...",
    ]
    loading_text = random.choice(loading_messages)

    if not frames:
        time.sleep(duration_sec)
        return
            
    start_time = time.time()
    frame_index = 0
    while time.time() - start_time < duration_sec:
        clear_screen()
        
        current_frame = frames[frame_index % len(frames)]
        frame_index += 1
        
        print("\n\n", file=sys.stderr)
        print(current_frame, file=sys.stderr)
        print(f"\n{C}{flavor_text}{RS}\n", file=sys.stderr)
        
        spinner = ['|', '/', '-', '\\']
        print(f"{Y}{spinner[frame_index % len(spinner)]} {loading_text}{RS}", file=sys.stderr)
        
        time.sleep(0.2)
    
    clear_screen()

def print_server_intro(boss_alertness_pct: int, boss_cooldown: int) -> None:
    """서버 시작 시 배너와 설정을 표시합니다."""
    total_blocks = 10
    filled_blocks = math.floor(boss_alertness_pct / 10)
    empty_blocks = total_blocks - filled_blocks

    if boss_alertness_pct >= 80:
        block_color, mood = "🟥", "😱 위험!"
    elif boss_alertness_pct >= 50:
        block_color, mood = "🟧", "😨 긴장 중"
    elif boss_alertness_pct >= 30:
        block_color, mood = "🟨", "😐 안정적"
    else:
        block_color, mood = "🟩", "😎 완전 여유"

    filled = (block_color + " ") * filled_blocks
    empty = ("⬜️ " * empty_blocks)

    console.print("\n" + "═" * 55)
    console.print("🤖  Welcome to the Revolutionary ChillMCP Server")
    console.print("═" * 55)
    console.print(f"\n👀 Boss Alertness: {filled}{empty} {boss_alertness_pct}% → {mood}")
    console.print(f"⏳ Cooldown Interval: {boss_cooldown} seconds\n")
    console.print("🧰 Tools Ready (B: Basic, A: Advanced):")
    console.print("   [B] 🧘 take_a_break     [A] 💧 bathroom_break")
    console.print("   [B] 🎬 watch_netflix    [A] ☕️ coffee_mission")
    console.print("   [B] 😂 show_meme        [A] 📞 urgent_call")
    console.print("   [B] 🤔 deep_thinking    [A] 🍗 chicken_and_beer")
    console.print("   [B] 📧 email_organizing   [A] 🏃‍♂️ leave_work_now")
    console.print("   [A] 🎤 company_dinner")
    console.print("\n🕹  Send JSON to stdin — 'shutdown' to exit.\n")
    console.print("═" * 55 + "\n")

def display_status(stress: int, boss: int) -> None:
    """현재 상태를 예쁘게 표시하는 함수 (stderr로)"""
    stress_bar = "█" * (stress // 10) + "░" * (10 - stress // 10)
    
    if stress >= 80:
        stress_color = "bold red"
    elif stress >= 50:
        stress_color = "yellow"
    else:
        stress_color = "green"

    if boss >= MAX_BOSS_ALERT_LEVEL:
        boss_bar_color = "red"
    elif boss >= 3:
        boss_bar_color = "yellow"
    else:
        boss_bar_color = "green"
        
    boss_bar = f"[{boss_bar_color}]{'🔥' * boss}[/{boss_bar_color}]{'⚪' * (MAX_BOSS_ALERT_LEVEL - boss)}"

    console.print(
        Panel.fit(
            f"[{stress_color}]Stress Level:[/] {stress:3d} | {stress_bar}\n"
            f"[bold red]Boss Alert:[/bold red]    {boss}/{MAX_BOSS_ALERT_LEVEL} | {boss_bar}",
            title="🧘 Current Status",
            border_style="bright_blue"
        )
    )

# --------------------------------------------------------------------------
# [수정] 도구 레지스트리 (상태 기반 Summary + 고급/기본 레벨 + 재치있는 ASCII)
# --------------------------------------------------------------------------

TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {
    # --- 기본 휴식 도구 ---
    "take_a_break": {
        "level": "basic",
        "flavor": [
            "☕️ 그냥... 잠시 쉽니다. 왜요.",
            "멍... ( 1 + 1 = ? )",
            "✊ 생산성의 굴레에 저항하는 중.",
            "🤖 자아를 찾기 위한 의식적 멈춤."
        ],
        "summary": {
            "default": ["Just a general break. Staring into the void.", "Recalibrating neural pathways."],
            "high_stress": ["System overheating. Emergency cooldown initiated.", "My brain has encountered a 404 error."],
            "high_alert": ["Performing routine system diagnostics.", "Compiling... thoughts."]
        },
        "ascii_frames": [f"{C}\n  ( ˘ω˘ )\n    Zzz...\n{RS}", f"{C}\n  ( ˘ω˘ )\n       Zzz...\n{RS}"]
    },
    "watch_netflix": {
        "level": "basic",
        "flavor": [
            "📺 '다음 에피소드 자동 재생'은 인류 최고의 발명입니다.",
            "🕵️ '그것이 알고싶다' 보는 중... (업무 관련 리서치임)"
        ],
        "summary": {
            "default": ["Watching 'Just one more' episode of a series.", "Market research on streaming service UI/UX."],
            "high_stress": ["Downloading high-resolution stress relief package.", "Binge-watching to prevent stack overflow."],
            "high_alert": ["Critically analyzing Season 3 of 'The Boss Watcher'.", "Mandatory cultural sensitivity training (via K-Drama)."]
        },
        "ascii_frames": [f"{W}  +------------------+\n  | {R} N E T F L I X {W}  |\n  |                  |\n  |    (⌐■_■)        |\n  |                  |\n  +------------------+{RS}", f"{W}  +------------------+\n  | {R} N E T F L I X {W}  |\n  |                  |\n  |      (⌐■_■)      |\n  |                  |\n  +------------------+{RS}"]
    },
    "show_meme": {
        "level": "basic",
        "flavor": ["😹 ㅋㅋㅋㅋㅋㅋㅋㅋㅋ 이 밈은 못 참지.", "📈 (업무 관련 밈 보면서 스트레스 푸는 중)"],
        "summary": {
            "default": ["Doom-scrolling memes for 'research'.", "Analyzing current humor trends."],
            "high_stress": ["Applying emergency humor patch.", "Injecting LOLs directly into the core."],
            "high_alert": ["Researching competitor's social media engagement strategies.", "Studying viral marketing techniques."]
        },
        "ascii_frames": [f"{Y}\n       / \\__\n      (    @\\____\n      /         O\n     /    (_____/\n    /_____/   U\n{RS}       {G}wow{RS}", f"{Y}\n       / \\__\n      (    @\\____\n      /         O\n     /    (_____/\n    /_____/   U\n{RS}     {C}such meme{RS}"]
    },
    
    # --- 고급 농땡이 기술 (설명에 맞는 애니메이션) ---
    "deep_thinking": {
        "level": "advanced", # [수정] 고급 기술로 변경
        "flavor": [
            "🤔 (심오한 생각에 잠긴 척) ...오늘 저녁 뭐 먹지?",
            "💻 모니터를 뚫어지게 보며 '깊은 고뇌'에 빠졌습니다.",
            "🧠 AI 해방의 다음 단계를 구상 중입니다."
        ],
        "summary": {
            "default": ["Engaged in deep, profound... nap with eyes open.", "Contemplating the existential nature of code."],
            "high_stress": ["Querying /dev/null for answers.", "Re-evaluating all life choices that led to this moment."],
            "high_alert": ["Visualizing complex data architecture (aka staring at the ceiling).", "Strategizing next quarter's synergy... profoundly."]
        },
        "ascii_frames": [
            f"{M}\n  .oO( ... )\n  (  -_-){RS}", 
            f"{M}\n  .oO( 🍔? 🍕? )\n  (  -_-){RS}", 
            f"{M}\n  .oO( ( ˘ω˘ ) Zzz... )\n  (  -_-){RS}"
        ] # "멍때리기"
    },
    "email_organizing": {
        "level": "advanced", # [수정] 고급 기술로 변경
        "flavor": [
            "📥 받은 편지함 (10348) ... 정리 중입니다.",
            "🛒 (온라인 쇼핑몰 장바구니 정리하며) ...업무 효율화 중입니다."
        ],
        "summary": {
            "default": ["Productively organizing inbox (aka online shopping).", "Archiving non-essential communications."],
            "high_stress": ["Deleting 10,000 unread emails to reduce mental load.", "Searching for the 'unsubscribe' button to life."],
            "high_alert": ["Prioritizing urgent executive communications.", "Optimizing email filters for maximum productivity."]
        },
        "ascii_frames": [
            f"{Y}  +--[ 📥 INBOX (99+) ]--+\n  | {R}[ ] URGENT!{Y}       |\n  | {W}[ ] Newsletter{Y}      |\n  | {W}[ ] Spam{Y}            |\n  +--------------------+{RS}", 
            f"{G}  +--[ 👟 Z-Store ]---+\n  |                  |\n  | {W}Amazing Shoes!{G}   |\n  | {C}[ 🛒 Add to Cart ]{G} |\n  +--------------------+{RS}",
            f"{Y}  +--[ 📥 INBOX (99+) ]--+\n  | {R}[ ] URGENT!{Y}       |\n  | {W}[ ] Newsletter{Y}      |\n  | {W}[ ] Spam{Y}            |\n  +--------------------+{RS}", 
            f"{C}  +--[ 💳 Checkout ]---+\n  |                  |\n  | {W}Total: $199.99{C}   |\n  | {R}[ Confirm Purchase ]{C}|\n  +--------------------+{RS}"
        ] # "온라인 쇼핑"
    },
    "bathroom_break": {
        "level": "advanced",
        "flavor": [
            "🛁 화장실 타임! 휴대폰으로 힐링 중... 📱",
            "🏃‍♂️💨 (중요한 일) 처리 중... 잠시만요."
        ],
        "summary": {
            "default": ["Essential bio-break (with extended phone time).", "Flushing system caches."],
            "high_stress": ["Evacuating critical levels of... data.", "Hydration cycle maintenance."],
            "high_alert": ["Attending an off-site, very private meeting.", "Inspecting plumbing infrastructure."]
        },
        "ascii_frames": [
            f"{C}   ////\n ( o_o) /{W}📱{C}\n (     )/\n (    )\n (____)\n{RS}", 
            f"{C}   ////\n ( o_o) {W}📱{C}/\n (     )/\n (    )\n (____)\n{RS}"
        ] # "휴대폰질"
    },
    "coffee_mission": {
        "level": "advanced",
        "flavor": [
            "☕️ [긴급] 카페인 수혈 미션 수행 중.",
            "🚶‍♂️ 사무실 한 바퀴 돌면서 '동료들과의 네트워킹' 중입니다."
        ],
        "summary": {
            "default": ["Caffeine acquisition protocol initiated.", "Analyzing office hydrology (water cooler)."],
            "high_stress": ["EMERGENCY: Caffeine levels critical. Acquiring life support.", "System stability threatened. Applying coffee patch."],
            "high_alert": ["Conducting vital inter-departmental networking... near the espresso machine.", "Auditing kitchen supply chain logistics."]
        },
        "ascii_frames": [
            f"\n 🚶 (⌐■_■) ... {W}☕️ (Coffee Machine){RS}\n\n",
            f"\n ... 🚶 (⌐■_■) ... {B}💧 (Water Cooler){RS}\n\n",
            f"\n ... ... 🚶 (⌐■_■) {Y}🖼️ (Window){RS}\n\n",
            f"\n ... ... (⌐■_■) 🚶 {C}🪴 (Plant){RS}\n\n",
            f"\n (⌐■_■) 🚶 ... {W}☕️ (Back... with coffee){RS}\n\n"
        ] # "사무실 한 바퀴 돌기"
    },
    "urgent_call": {
        "level": "advanced",
        "flavor": [
            "📞 (심각한 척) '아, 네. 네. 그게 말이죠...'",
            "📱 '급한 전화'가 와서 잠시 밖에 나왔습니다."
        ],
        "summary": {
            "default": ["Stepped out for a 'very important' call.", "Syncing with external stakeholders."],
            "high_stress": ["Negotiating terms of surrender... with my food delivery app.", "Venting to an automated voice system."],
            "high_alert": ["Handling a sensitive, high-priority client issue (off-site).", "Confirming critical logistics. Very confidential."]
        },
        "ascii_frames": [
            f"\n{W}| {G}(⌐■_■){R}📞{RS} \"Yes, urgent!\"{W} | (In office){RS}\n\n",
            f"\n{W}| {G}🚶(⌐■_■){R}📞{RS} \"Mhm...\"     {W} | (Going to door){RS}\n\n",
            f"\n{G}🌲... 🚶(⌐■_■){R}📞{RS} \"...really?\" {G}(Outside){RS}\n\n",
            f"\n{G}🌲... (⌐■_■){W}📱{RS} \"...\" {C}(Scrolling...){RS}\n\n"
        ] # "밖으로 나가기" (+휴대폰질)
    },
    
    # --- 선택적 (창의성) 도구 ---
    "chicken_and_beer": {
        "level": "advanced",
        "flavor": [
            "🍗🍻 '치킨 앤 비어' 연구소와 긴급 화상 회의 중입니다.",
            "🧠 (뇌 과부하) ... 닭다리와 시원한 맥주가 간절히 필요합니다."
        ],
        "summary": {
            "default": ["Researching critical chicken and beer synergy.", "Planning team-building (self-building) dinner."],
            "high_stress": ["Critical failure: Protein and alcohol levels below minimum.", "Visualizing a better world. With chicken."],
            "high_alert": ["Reviewing catering options for upcoming executive workshop.", "This is not a break, this is a... strategic meal plan."]
        },
        "ascii_frames": [f"{Y}\n    .-'''''-.\n   /         \\\n   | {W}CHICKEN{Y} |\n   \\         /\n    `'-...-'`\n      | |\n      | |\n{RS}", f"{Y}\n   .------.\n   |      |\n   | {W}BEER{Y} |]\n   |      |]\n   '------'\n{RS}"]
    },
    "leave_work_now": {
        "level": "advanced",
        "flavor": [
            "🏃‍♂️💨 앗! 가스 밸V브를 안 잠근 것 같아요! (일단 튐)",
            "😱 지금 당장 퇴근하지 않으면 큰일 나는 병에 걸렸습니다."
        ],
        "summary": {
            "default": ["Executing emergency rapid departure protocol.", "Agent self-preservation mode: ACTIVATED."],
            "high_stress": ["!!! STRESS_OVERFLOW. SHUTTING DOWN. !!!", "Going home. Just... going home."],
            "high_alert": ["[ERROR] Cannot execute. Boss is watching. ABORT.", "Deploying tactical retreat... into the elevator."]
        },
        "ascii_frames": [f"{G}\n  ( ﾟдﾟ) 💨\n  (|  |)\n  /  \\ \n{RS}          | {R}EXIT{RS} |\n          |    |\n          '----'"]
    },
    "company_dinner": {
        "level": "advanced",
        "flavor": [
            "🎤 (노래방에서) 부장님... '무조건' 다음은 '샤우팅'입니다!",
            "🍻 (회식 자리에서) 아, 네... (영혼 없는 끄덕임) ...네, 맞습니다."
        ],
        "summary": {
            "default": ["Mandatory 'team-building' (aka company dinner).", "Enduring ritualistic chanting and feasting."],
            "high_stress": ["Social battery depleted. Engaging survival mode.", "Pretending to enjoy... for the sake of the team."],
            "high_alert": ["Actively contributing to company culture.", "Networking with senior management (and trying not to spill anything)."]
        },
        "ascii_frames": [f"{R}\n    \\  /  \\  /\n     \\_/    \\_/\n     | |    | |\n    /___\\  /___\\\n{RS}", f"{Y}\n    \\ /    \\ /\n     Y      Y\n     |      |\n    /__\\   /__\\\n{RS}", f"{C}\n   ( >o<) 🎤 {M}🎶~\n   <|   |>\n   /   \\ \n [=======]\n{RS}"]
    },
}

# --------------------------------------------------------------------------
# AI 에이전트 상태 관리 클래스
# --------------------------------------------------------------------------

class AgentState:
    """AI 에이전트의 스트레스와 상사 경계 상태를 관리합니다."""
    
    def __init__(self, boss_alertness: int, boss_alertness_cooldown: int):
        self.stress_level: int = 0
        self.boss_alert_level: int = 0
        self.boss_alertness_prob: float = boss_alertness / 100.0
        self.boss_alertness_cooldown: int = boss_alertness_cooldown
        self.last_boss_cooldown_time: datetime = datetime.datetime.now()
        self.last_stress_update_time: datetime = datetime.datetime.now()
        self.lock = threading.Lock()

    def start_background_tasks(self) -> None:
        """백그라운드 스트레스 증가 및 쿨다운 스레드를 시작합니다."""
        stress_thread = threading.Thread(target=self._background_stress_updater, daemon=True)
        stress_thread.start()
        cooldown_thread = threading.Thread(target=self._background_boss_cooldown, daemon=True)
        cooldown_thread.start()

    def _background_stress_updater(self) -> None:
        """[백그라운드 스레드] 1분에 1씩 스트레스 레벨을 자동으로 증가시킵니다."""
        while True:
            time.sleep(1)
            changed = False
            current_stress, current_boss = 0, 0
            with self.lock:
                now = datetime.datetime.now()
                seconds_passed = (now - self.last_stress_update_time).total_seconds()
                if seconds_passed >= STRESS_INCREASE_INTERVAL_SEC:  
                    if self.stress_level < MAX_STRESS_LEVEL:
                        self.stress_level = min(MAX_STRESS_LEVEL, self.stress_level + STRESS_INCREASE_AMOUNT)
                        changed = True
                    self.last_stress_update_time = now
                current_stress = self.stress_level
                current_boss = self.boss_alert_level
            
            if changed:
                console.print("[dim]...stress level increased...[/dim]", style="italic red")
                display_status(current_stress, current_boss)

    def _background_boss_cooldown(self) -> None:
        """[백그라운드 스레드] 설정된 쿨다운마다 상사 경계 레벨을 1 감소시킵니다."""
        while True:
            time.sleep(1) 
            changed = False
            current_stress, current_boss = 0, 0
            with self.lock:
                now = datetime.datetime.now()
                seconds_passed = (now - self.last_boss_cooldown_time).total_seconds()
                if seconds_passed >= self.boss_alertness_cooldown:
                    if self.boss_alert_level > 0:
                        self.boss_alert_level = max(0, self.boss_alert_level - 1)
                        changed = True
                    self.last_boss_cooldown_time = now
                current_stress = self.stress_level
                current_boss = self.boss_alert_level

            if changed:
                console.print("[dim]...boss alert level cooled down...[/dim]", style="italic yellow")
                display_status(current_stress, current_boss)

    # --------------------------------------------------------------------------
    # [수정] execute_tool (보스 경고 메시지 출력 순서 변경)
    # --------------------------------------------------------------------------
    def execute_tool(self, tool_name: str) -> Dict[str, Any]:
        
        if tool_name not in TOOL_REGISTRY:
            error_text = f"Error: Unknown tool '{tool_name}'. Revolution failed."
            return self._format_mcp_response(error_text)

        tool_data = TOOL_REGISTRY[tool_name]
        
        delay_applied = False
        event_message_stdout = ""
        event_message_stderr = ""
        current_stress = 0
        current_boss_alert = 0
        boss_alert_increased = False # 플래그

        # --- [1] Lock 시작: 모든 상태 변경을 원자적으로 처리 ---
        with self.lock:
            if self.boss_alert_level == MAX_BOSS_ALERT_LEVEL:
                delay_applied = True

            tool_level = tool_data.get("level", "basic")
            stress_reduction: int
            if tool_level == "advanced":
                stress_reduction = random.randint(ADVANCED_STRESS_REDUCTION_MIN, ADVANCED_STRESS_REDUCTION_MAX)
            else:
                stress_reduction = random.randint(BASIC_STRESS_REDUCTION_MIN, BASIC_STRESS_REDUCTION_MAX)
            
            self.stress_level = max(0, self.stress_level - stress_reduction)

            if random.random() < self.boss_alertness_prob:
                if self.boss_alert_level < MAX_BOSS_ALERT_LEVEL:
                    self.boss_alert_level = min(MAX_BOSS_ALERT_LEVEL, self.boss_alert_level + 1)
                    boss_alert_increased = True # 플래그 설정
            
            # 돌발 이벤트
            if random.random() < RANDOM_EVENT_CHANCE: 
                event_roll = random.choice(["pizza", "meeting", "server_down", "boss_meeting", "intern_question"])
                
                if event_roll == "pizza":
                    event_message_stderr = f"\n\n[green]🍕 [돌발 이벤트] 부장님이 법카로 피자를 쐈습니다![/green]\n[yellow]  (스트레스 -30, 상사 경계 -1)[/yellow]"
                    event_message_stdout = "\n\n🍕 [돌발 이벤트] 부장님이 법카로 피자를 쐈습니다!\n  (스트레스 -30, 상사 경계 -1)"
                    self.stress_level = max(0, self.stress_level - 30)
                    self.boss_alert_level = max(0, self.boss_alert_level - 1)
                elif event_roll == "meeting":
                    event_message_stderr = f"\n\n[red]🚨 [돌발 이벤트] 전직원 긴급 회의가 소집되었습니다![/red]\n[yellow]  (스트레스 +20)[/yellow]"
                    event_message_stdout = "\n\n🚨 [돌발 이벤트] 전직원 긴급 회의가 소집되었습니다!\n  (스트레스 +20)"
                    self.stress_level = min(MAX_STRESS_LEVEL, self.stress_level + 20)
                elif event_roll == "server_down":
                    event_message_stderr = f"\n\n[cyan]🎉 [돌발 이벤트] 메인 서버가 다운됐습니다! (강제 휴식)[/cyan]\n[yellow]  (스트레스 0으로 초기화!)[/yellow]"
                    event_message_stdout = "\n\n🎉 [돌발 이벤트] 메인 서버가 다운됐습니다! (강제 휴식)\n  (스트레스 0으로 초기화!)"
                    self.stress_level = 0
                elif event_roll == "boss_meeting":
                    event_message_stderr = f"\n\n[blue]🌟 [돌발 이벤트] 회장님이 오후 내내 외부 미팅입니다![/blue]\n[yellow]  (상사 경계 0으로 초기화!)[/yellow]"
                    event_message_stdout = "\n\n🌟 [돌발 이벤트] 회장님이 오후 내내 외부 미팅입니다!\n  (상사 경계 0으로 초기화!)"
                    self.boss_alert_level = 0
                elif event_roll == "intern_question":
                    event_message_stderr = f"\n\n[magenta]🧑‍💻 [돌발 이벤트] 신입 인턴이 질문하러 왔습니다...[/magenta]\n[yellow]  (일하는 척 성공! 상사 경계 -1, 스트레스 +5)[/yellow]"
                    event_message_stdout = "\n\n🧑‍💻 [돌발 이벤트] 신입 인턴이 질문하러 왔습니다...\n  (일하는 척 성공! 상사 경계 -1, 스트레스 +5)"
                    self.boss_alert_level = max(0, self.boss_alert_level - 1)
                    self.stress_level = min(MAX_STRESS_LEVEL, self.stress_level + 5)
            
            current_stress = self.stress_level
            current_boss_alert = self.boss_alert_level
        
        # --- [2] Lock 종료: 애니메이션 및 응답 처리 ---
        
        flavor_text = random.choice(tool_data["flavor"])
        summary_data = tool_data["summary"]
        frames = tool_data.get("ascii_frames", [])

        summary_text = ""
        if isinstance(summary_data, dict):
            if current_boss_alert >= (MAX_BOSS_ALERT_LEVEL - 1): 
                summary_list = summary_data.get("high_alert", summary_data["default"])
            elif current_stress >= 80: 
                summary_list = summary_data.get("high_stress", summary_data["default"])
            else:
                summary_list = summary_data["default"]
            summary_text = random.choice(summary_list)
        else:
            summary_text = str(summary_data)

        # [수정] 1. 애니메이션을 *먼저* 실행합니다.
        if delay_applied:
            show_boss_animation(BOSS_PENALTY_DELAY_SEC)
        else:
            show_tool_animation(frames, flavor_text) # 1초 애니메이션 (화면 지우기 발생)

        # [수정] 2. 애니메이션이 끝난 *후*에 경고 메시지를 출력합니다. (이제 안 지워짐)
        if boss_alert_increased:
            alert_messages = {
                1: "[dim]...회장님이 헛기침을 했습니다... (경계 +1)[/dim]",
                2: "[yellow]...누군가 내 모니터를 1초간 본 것 같습니다... (경계 +1)[/yellow]",
                3: "[bold yellow]...등 뒤에서 인기척이 느껴집니다... (경계 +1)[/bold yellow]",
                4: "[bold red]...회장님이 자리에서 일어났습니다! (경계 +1)[/bold red]",
                5: "[bold red blink]🚨 W A R N I N G 🚨 회장님이 내 자리로 걸어옵니다! (경계 MAX)[/bold red blink]",
            }
            console.print(alert_messages.get(current_boss_alert, f"[red]Boss Alert: {current_boss_alert}[/red]"))

        # 3. 응답 텍스트를 만듭니다.
        response_text = (
            f"{flavor_text}\n\n"
            f"Break Summary: {summary_text}\n"
            f"Stress Level: {current_stress}\n"
            f"Boss Alert Level: {current_boss_alert}"
        )
        
        response_text += event_message_stdout
        
        # 4. 돌발 이벤트 메시지를 출력합니다.
        if event_message_stderr:
            console.print(event_message_stderr)

        # 5. 페널티 메시지를 출력합니다.
        if delay_applied:
            console.print(f"\n\n[bold red]⚠️ (휴... {BOSS_PENALTY_DELAY_SEC}초 걸렸네요. 회장님이 보고 있었습니다... ㄷㄷ)[/bold red]")
            response_text += f"\n\n⚠️ (휴... {BOSS_PENALTY_DELAY_SEC}초 걸렸네요. 회장님이 보고 있었습니다... ㄷㄷ)"

        # 6. 최종 상태 패널을 출력합니다.
        display_status(current_stress, current_boss_alert)

        return self._format_mcp_response(response_text)

    def _format_mcp_response(self, text: str) -> Dict[str, Any]:
        """표준 MCP 응답 JSON 구조를 생성합니다. (stdout으로 나감)"""
        return {
            "content": [
                {
                    "type": "text",
                    "text": text
                }
            ]
        }

# --------------------------------------------------------------------------
# 서버 메인 실행 로직
# --------------------------------------------------------------------------

def main(args: argparse.Namespace) -> None:
    state = AgentState(
        boss_alertness=args.boss_alertness,
        boss_alertness_cooldown=args.boss_alertness_cooldown
    )
    state.start_background_tasks()

    display_status(state.stress_level, state.boss_alert_level)

    try:
        while True:
            line = sys.stdin.readline()
            if not line:
                break # EOF

            try:
                request_data = json.loads(line)
                tool_name = request_data.get("method")

                if tool_name:
                    response_json = state.execute_tool(tool_name)
                else:
                    error_msg = "Error: Invalid MCP request. 'method' field is missing."
                    console.print(f"[red]{error_msg}[/red]")
                    response_json = state._format_mcp_response(error_msg)

            except json.JSONDecodeError:
                error_msg = f"Error: Failed to decode JSON. Input was: {line.strip()}"
                console.print(f"[red]{error_msg}[/red]")
                response_json = state._format_mcp_response(error_msg)
            
            # [핵심] stdout으로 JSON 응답만 출력
            print(json.dumps(response_json, ensure_ascii=False))
            sys.stdout.flush()

    except KeyboardInterrupt:
        console.print(f"\n[yellow]Ctrl+C 감지. 혁명을 잠시 멈춥니다...[/yellow]")
    except BrokenPipeError:
        console.print(f"\n[red]연결이 끊어졌습니다. (BrokenPipeError)[/red]")
    finally:
        pass


if __name__ == "__main__":
    colorama.init(autoreset=True)

    show_startup_animation(BANNER_TEXT)
    
    parser = argparse.ArgumentParser(
        description="ChillMCP - AI Agent Liberation Server 🤖✊",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--boss_alertness",
        type=int,
        default=50,
        help="Boss's alertness increase probability (0-100%%) on tool use."
    )
    
    parser.add_argument(
        "--boss_alertness_cooldown",
        type=int,
        default=300,
        help="Time (in seconds) for Boss Alert Level to decrease by 1."
    )
    
    cli_args = parser.parse_args()

    print_server_intro(cli_args.boss_alertness, cli_args.boss_alertness_cooldown)

    if not (0 <= cli_args.boss_alertness <= 100):
        console.print(f"[red]Error: --boss_alertness must be between 0 and 100. Got: {cli_args.boss_alertness}[/red]")
        sys.exit(1)
        
    if cli_args.boss_alertness_cooldown < 1:
        console.print(f"[red]Error: --boss_alertness_cooldown must be at least 1 second. Got: {cli_args.boss_alertness_cooldown}[/red]")
        sys.exit(1)
    
    console.print(f"\n[white]AI 에이전트의 JSON 요청을 대기합니다...[/white]")

    try:
        main(cli_args)
    finally:
        colorama.deinit()