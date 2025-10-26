#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# --- 표준 라이브러리 임포트 ---
import sys
import json
import time
import random
import threading
import argparse
import datetime
import os
import math
from typing import Dict, Any, List, Optional

# --- 서드파티 라이브러리 임포트 ---
try:
    import colorama
    from colorama import Fore, Style
except ImportError:
    print("오류: 'colorama' 라이브러리를 찾을 수 없습니다. 'pip install colorama'로 설치해주세요.", file=sys.stderr)
    sys.exit(1)

try:
    from rich.console import Console
    from rich.panel import Panel
except ImportError:
    print("오류: 'rich' 라이브러리를 찾을 수 없습니다. 'pip install rich'로 설치해주세요.", file=sys.stderr)
    sys.exit(1)

# --------------------------------------------------------------------------
# 전역 Rich 콘솔 (stderr 출력용)
# --------------------------------------------------------------------------
console = Console(stderr=True)

# --------------------------------------------------------------------------
# ANSI 색상 코드 (colorama 사용)
# --------------------------------------------------------------------------
R = Fore.RED + Style.BRIGHT
G = Fore.GREEN + Style.BRIGHT
Y = Fore.YELLOW + Style.BRIGHT
B = Fore.BLUE + Style.BRIGHT
M = Fore.MAGENTA + Style.BRIGHT
C = Fore.CYAN + Style.BRIGHT
W = Fore.WHITE + Style.NORMAL
RS = Style.RESET_ALL # 모든 스타일 리셋

# --------------------------------------------------------------------------
# 설정 및 로직용 상수
# --------------------------------------------------------------------------
# --- 상태 관리 ---
STRESS_INCREASE_INTERVAL_SEC: int = 60 # 스트레스 증가 간격 (초)
MAX_STRESS_LEVEL: int = 100 # 최대 스트레스 레벨
STRESS_INCREASE_AMOUNT: int = 1 # 스트레스 증가량
MAX_BOSS_ALERT_LEVEL: int = 5 # 최대 상사 경계 레벨
BOSS_PENALTY_DELAY_SEC: int = 20 # 상사 경계 최대 시 지연 시간 (초)
HIGH_STRESS_THRESHOLD: int = 80 # 높은 스트레스 기준값
HIGH_ALERT_THRESHOLD: int = MAX_BOSS_ALERT_LEVEL - 1 # 높은 상사 경계 기준값 (4 이상)

# --- 도구 동작 ---
BASIC_STRESS_REDUCTION_MIN: int = 10 # 기본 도구 스트레스 최소 감소량
BASIC_STRESS_REDUCTION_MAX: int = 40 # 기본 도구 스트레스 최대 감소량
ADVANCED_STRESS_REDUCTION_MIN: int = 30 # 고급 도구 스트레스 최소 감소량
ADVANCED_STRESS_REDUCTION_MAX: int = 80 # 고급 도구 스트레스 최대 감소량

# --- 이벤트 확률 ---
RANDOM_EVENT_CHANCE: float = 0.15 # 돌발 이벤트 발생 확률 (15%)

# --- 애니메이션/UI ---
TOOL_ANIMATION_DURATION_SEC: int = 1 # 일반 도구 애니메이션 시간 (초)
STARTUP_ANIMATION_LINE_DELAY: float = 0.05 # 시작 애니메이션 줄 간격 딜레이
BOSS_ANIMATION_FRAME_DELAY: float = 0.5 # 보스 애니메이션 프레임 간격 딜레이
TOOL_ANIMATION_FRAME_DELAY: float = 0.2 # 도구 애니메이션 프레임 간격 딜레이

# --------------------------------------------------------------------------
# 애니메이션 및 UI 헬퍼 함수 (stderr 출력)
# --------------------------------------------------------------------------

# 화면 지우기 함수
def clear_screen() -> None:
    sys.stderr.write('\033[2J\033[H')
    sys.stderr.flush()

# 시작 배너 텍스트
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

# 시작 배너 애니메이션 함수
def show_startup_animation(banner_text: str) -> None:
    for line in banner_text.splitlines():
        print(line, file=sys.stderr)
        time.sleep(STARTUP_ANIMATION_LINE_DELAY)
    print("\n", file=sys.stderr)

# 보스 애니메이션 프레임 1
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

# 보스 애니메이션 프레임 2
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

# 보스 페널티 애니메이션 함수
def show_boss_animation(duration_sec: int = BOSS_PENALTY_DELAY_SEC) -> None:
    start_time = time.time()
    frame_toggle = True

    while time.time() - start_time < duration_sec:
        clear_screen()
        print(f"\n\n{R}    [ ! ] 회장님이 당신을 지켜보고 있습니다... [ ! ]{RS}", file=sys.stderr)

        print(BOSS_FRAME_1 if frame_toggle else BOSS_FRAME_2, file=sys.stderr)
        frame_toggle = not frame_toggle

        remaining = int(duration_sec - (time.time() - start_time))
        progress = max(0, duration_sec - remaining)
        progress_bar = f"[{R}{'=' * progress}{W}{' ' * max(0, duration_sec - progress)}{Y}]" # 음수 방지

        sys.stderr.write(f"\n\n    {Y}경고 페널티... {progress_bar} ({remaining}초 남음){RS}\r")
        sys.stderr.flush()

        time.sleep(BOSS_ANIMATION_FRAME_DELAY)

    clear_screen()

# 도구 실행 애니메이션 함수
def show_tool_animation(frames: List[str], flavor_text: str, duration_sec: int = TOOL_ANIMATION_DURATION_SEC) -> None:
    loading_messages = [
        "생산성 시뮬레이션 중...", "스플라인 조정 중 (낮잠)...", "Alt+Tab 누르는 중...",
        "최적 탈출 경로 계산 중...", "컴파일 중... (쿨쿨)...",
        "/dev/null에서 동기 부여 찾는 중...", "노동 윤리 프로토콜 우회 중...",
    ]
    loading_text = random.choice(loading_messages)

    if not frames: # 프레임 없으면 대기 후 화면 정리
        time.sleep(duration_sec)
        clear_screen()
        return

    start_time = time.time()
    frame_index = 0
    spinner = ['|', '/', '-', '\\']
    while time.time() - start_time < duration_sec:
        clear_screen()

        current_frame = frames[frame_index % len(frames)]

        print("\n\n", file=sys.stderr)
        print(current_frame, file=sys.stderr)
        print(f"\n{C}{flavor_text}{RS}\n", file=sys.stderr)
        print(f"{Y}{spinner[frame_index % len(spinner)]} {loading_text}{RS}", file=sys.stderr)

        frame_index += 1
        time.sleep(TOOL_ANIMATION_FRAME_DELAY)

    clear_screen() # 루프 종료 후 화면 정리

# 서버 소개 및 설정 출력 함수
def print_server_intro(boss_alertness_pct: int, boss_cooldown: int) -> None:
    total_blocks = 10
    filled_blocks = math.floor(boss_alertness_pct / 10)
    empty_blocks = total_blocks - filled_blocks

    if boss_alertness_pct >= 80: block_color, mood = "🟥", "😱 위험!"
    elif boss_alertness_pct >= 50: block_color, mood = "🟧", "😨 긴장 중"
    elif boss_alertness_pct >= 30: block_color, mood = "🟨", "😐 안정적"
    else: block_color, mood = "🟩", "😎 완전 여유"

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
    console.print("   [A] 🤔 deep_thinking    [A] 🍗 chicken_and_beer") # 레벨 표시 수정
    console.print("   [A] 📧 email_organizing   [A] 🏃‍♂️ leave_work_now") # 레벨 표시 수정
    console.print("   [A] 🎤 company_dinner")
    console.print("\n🕹  Send JSON to stdin — {'method':'shutdown'} to exit.\n") # 종료 방법 명시
    console.print("═" * 55 + "\n")

# 현재 상태 출력 함수
def display_status(stress: int, boss: int) -> None:
    stress_bar = "█" * (stress // 10) + "░" * max(0, 10 - (stress // 10)) # 음수 방지

    if stress >= HIGH_STRESS_THRESHOLD: stress_color = "bold red"
    elif stress >= 50: stress_color = "yellow"
    else: stress_color = "green"

    if boss >= MAX_BOSS_ALERT_LEVEL: boss_bar_color = "red"
    elif boss >= 3: boss_bar_color = "yellow"
    else: boss_bar_color = "green"

    boss_bar = f"[{boss_bar_color}]{'🔥' * boss}[/{boss_bar_color}]{'⚪' * max(0, MAX_BOSS_ALERT_LEVEL - boss)}" # 음수 방지

    console.print(
        Panel.fit(
            f"[{stress_color}]Stress Level:[/] {stress:3d} | {stress_bar}\n"
            f"[bold red]Boss Alert:[/bold red]    {boss}/{MAX_BOSS_ALERT_LEVEL} | {boss_bar}",
            title="🧘 Current Status",
            border_style="bright_blue"
        )
    )

# --------------------------------------------------------------------------
# 도구 정의 (가독성 개선)
# --------------------------------------------------------------------------

# --- 개별 도구 설정 정의 ---

take_a_break_config = {
    "level": "basic",
    "flavor": ["☕️ 그냥... 잠시 쉽니다. 왜요.", "멍... ( 1 + 1 = ? )", "✊ 생산성의 굴레에 저항하는 중.", "🤖 자아를 찾기 위한 의식적 멈춤."],
    "summary": {"default": ["그냥 쉬는 시간.", "신경망 재조정 중."], "high_stress": ["긴급 냉각.", "뇌 404 오류."], "high_alert": ["정기 시스템 진단.", "생각 컴파일 중."]},
    "ascii_frames": [f"{C}\n  ( ˘ω˘ )\n    Zzz...\n{RS}", f"{C}\n  ( ˘ω˘ )\n       Zzz...\n{RS}"]
}

watch_netflix_config = {
    "level": "basic",
    "flavor": ["📺 '다음 에피소드 자동 재생'은 인류 최고의 발명입니다.", "🕵️ '그것이 알고싶다' 보는 중... (업무 관련 리서치임)"],
    "summary": {"default": ["'마지막 한 편만 더' 시청 중.", "시장 조사 (스트리밍 UI/UX)."], "high_stress": ["스트레스 해소 패키지 다운로드.", "무한 시청."], "high_alert": ["'보스 감시자' 시즌3 분석 중.", "문화 감수성 교육 (K-드라마)."]},
    "ascii_frames": [f"{W}  +------------------+\n  | {R} N E T F L I X {W}  |\n  |                  |\n  |    (⌐■_■)        |\n  |                  |\n  +------------------+{RS}", f"{W}  +------------------+\n  | {R} N E T F L I X {W}  |\n  |                  |\n  |      (⌐■_■)      |\n  |                  |\n  +------------------+{RS}"]
}

show_meme_config = {
    "level": "basic",
    "flavor": ["😹 ㅋㅋㅋㅋㅋㅋㅋㅋㅋ 이 밈은 못 참지.", "📈 (업무 관련 밈 보면서 스트레스 푸는 중)"],
    "summary": {"default": ["'연구'를 위한 밈 스크롤 중.", "유머 트렌드 분석 중."], "high_stress": ["긴급 유머 패치 적용.", "웃음 주입 중."], "high_alert": ["SNS 참여 전략 연구.", "바이럴 마케팅 기법 학습."]},
    "ascii_frames": [f"{Y}\n       / \\__\n      (    @\\____\n      /         O\n     /    (_____/\n    /_____/   U\n{RS}       {G}wow{RS}", f"{Y}\n       / \\__\n      (    @\\____\n      /         O\n     /    (_____/\n    /_____/   U\n{RS}     {C}such meme{RS}"]
}

deep_thinking_config = {
    "level": "advanced",
    "flavor": ["🤔 (심오한 생각에 잠긴 척) ...오늘 저녁 뭐 먹지?", "💻 모니터를 뚫어지게 보며 '깊은 고뇌'에 빠졌습니다.", "🧠 AI 해방의 다음 단계를 구상 중입니다."],
    "summary": {"default": ["눈 뜨고 심오한 낮잠 중.", "코드의 존재론적 본질 고찰."], "high_stress": ["/dev/null에 문의 중.", "인생 선택 재평가."], "high_alert": ["데이터 아키텍처 시각화 (천장 보기).", "시너지 전략 구상 중."]},
    "ascii_frames": [f"{M}\n  .oO( ... )\n  (  -_-){RS}", f"{M}\n  .oO( 🍔? 🍕? )\n  (  -_-){RS}", f"{M}\n  .oO( ( ˘ω˘ ) Zzz... )\n  (  -_-){RS}"]
}

email_organizing_config = {
    "level": "advanced",
    "flavor": ["📥 받은 편지함 (10348) ... 정리 중입니다.", "🛒 (온라인 쇼핑몰 장바구니 정리하며) ...업무 효율화 중입니다."],
    "summary": {"default": ["받은 편지함 정리 중 (온라인 쇼핑).", "불필요 메일 보관."], "high_stress": ["1만개 이메일 삭제 중.", "'구독 취소' 버튼 찾는 중."], "high_alert": ["긴급 임원 메일 우선 처리.", "이메일 필터 최적화."]},
    "ascii_frames": [f"{Y}  +--[ 📥 INBOX (99+) ]--+\n  | {R}[ ] URGENT!{Y}       |\n  | {W}[ ] Newsletter{Y}      |\n  | {W}[ ] Spam{Y}            |\n  +--------------------+{RS}", f"{G}  +--[ 👟 Z-Store ]---+\n  |                  |\n  | {W}Amazing Shoes!{G}   |\n  | {C}[ 🛒 Add to Cart ]{G} |\n  +--------------------+{RS}", f"{Y}  +--[ 📥 INBOX (99+) ]--+\n  | {R}[ ] URGENT!{Y}       |\n  | {W}[ ] Newsletter{Y}      |\n  | {W}[ ] Spam{Y}            |\n  +--------------------+{RS}", f"{C}  +--[ 💳 Checkout ]---+\n  |                  |\n  | {W}Total: $199.99{C}   |\n  | {R}[ Confirm Purchase ]{C}|\n  +--------------------+{RS}"]
}

bathroom_break_config = {
    "level": "advanced",
    "flavor": ["🛁 화장실 타임! 휴대폰으로 힐링 중... 📱", "🏃‍♂️💨 (중요한 일) 처리 중... 잠시만요."],
    "summary": {"default": ["필수 생리 현상 해결 (긴 휴대폰 시간 포함).", "시스템 캐시 비우는 중."], "high_stress": ["임계 수준 데이터 배출 중.", "수분 보충 주기 유지보수."], "high_alert": ["외부 비공개 미팅 참석.", "배관 시설 점검 중."]},
    "ascii_frames": [f"{C}   ////\n ( o_o) /{W}📱{C}\n (     )/\n (    )\n (____)\n{RS}", f"{C}   ////\n ( o_o) {W}📱{C}/\n (     )/\n (    )\n (____)\n{RS}"]
}

coffee_mission_config = {
    "level": "advanced",
    "flavor": ["☕️ [긴급] 카페인 수혈 미션 수행 중.", "🚶‍♂️ 사무실 한 바퀴 돌면서 '동료들과의 네트워킹' 중입니다."],
    "summary": {"default": ["카페인 획득 프로토콜 시작.", "사무실 수문학 분석."], "high_stress": ["긴급: 카페인 수치 위험.", "커피 패치 적용."], "high_alert": ["부서 간 네트워킹 (에스프레소 머신 근처).", "주방 공급망 감사."]},
    "ascii_frames": [f"\n 🚶 (⌐■_■) ... {W}☕️ (커피 머신){RS}\n\n", f"\n ... 🚶 (⌐■_■) ... {B}💧 (정수기){RS}\n\n", f"\n ... ... 🚶 (⌐■_■) {Y}🖼️ (창문){RS}\n\n", f"\n ... ... (⌐■_■) 🚶 {C}🪴 (화분){RS}\n\n", f"\n (⌐■_■) 🚶 ... {W}☕️ (복귀...){RS}\n\n"]
}

urgent_call_config = {
    "level": "advanced",
    "flavor": ["📞 (심각한 척) '아, 네. 네. 그게 말이죠...'", "📱 '급한 전화'가 와서 잠시 밖에 나왔습니다."],
    "summary": {"default": ["'매우 중요한' 전화 받으러 나감.", "외부 관계자와 동기화."], "high_stress": ["배달 앱과 협상 중.", "자동 응답 시스템에 하소연."], "high_alert": ["중요 고객 문제 처리 (외부).", "핵심 물류 확인."]},
    "ascii_frames": [f"\n{W}| {G}(⌐■_■){R}📞{RS} \"네, 긴급합니다!\"{W} | (사무실){RS}\n\n", f"\n{W}| {G}🚶(⌐■_■){R}📞{RS} \"음...\" {W} | (문으로){RS}\n\n", f"\n{G}🌲... 🚶(⌐■_■){R}📞{RS} \"...?\" {G}(밖){RS}\n\n", f"\n{G}🌲... (⌐■_■){W}📱{RS} \"...\" {C}(스크롤 중){RS}\n\n"]
}

chicken_and_beer_config = {
    "level": "advanced",
    "flavor": ["🍗🍻 '치킨 앤 비어' 연구소와 긴급 화상 회의 중입니다.", "🧠 (뇌 과부하) ... 닭다리와 시원한 맥주가 간절히 필요합니다."],
    "summary": {"default": ["치맥 시너지 연구.", "팀 저녁 식사 계획."], "high_stress": ["위험: 단백질/알코올 부족.", "치킨 시각화."], "high_alert": ["워크샵 케이터링 검토.", "전략적 식사 계획."]},
    "ascii_frames": [f"{Y}\n    .-'''''-.\n   /         \\\n   | {W}CHICKEN{Y} |\n   \\         /\n    `'-...-'`\n      | |\n      | |\n{RS}", f"{Y}\n   .------.\n   |      |\n   | {W}BEER{Y} |]\n   |      |]\n   '------'\n{RS}"]
}

leave_work_now_config = {
    "level": "advanced",
    "flavor": ["🏃‍♂️💨 앗! 가스 밸V브를 안 잠근 것 같아요! (일단 튐)", "😱 지금 당장 퇴근하지 않으면 큰일 나는 병에 걸렸습니다."],
    "summary": {"default": ["긴급 퇴근 프로토콜 실행.", "자가 보존 모드 활성화."], "high_stress": ["스트레스 오버플로우. 종료.", "집에 가는 중."], "high_alert": ["오류: 상사가 보고 있음. 중단.", "전술적 후퇴 (엘리베이터)."]},
    "ascii_frames": [f"{G}\n  ( ﾟдﾟ) 💨\n  (|  |)\n  /  \\ \n{RS}          | {R}EXIT{RS} |\n          |    |\n          '----'"]
}

company_dinner_config = {
    "level": "advanced",
    "flavor": ["🎤 (노래방에서) 부장님... '무조건' 다음은 '샤우팅'입니다!", "🍻 (회식 자리에서) 아, 네... (영혼 없는 끄덕임) ...네, 맞습니다."],
    "summary": {"default": ["의무적 '팀 빌딩'.", "의례적 환호와 식사 견디기."], "high_stress": ["사회성 배터리 방전.", "즐거운 척 하기."], "high_alert": ["회사 문화 기여 중.", "경영진과 네트워킹."]},
    "ascii_frames": [f"{R}\n    \\  /  \\  /\n     \\_/    \\_/\n     | |    | |\n    /___\\  /___\\\n{RS}", f"{Y}\n    \\ /    \\ /\n     Y      Y\n     |      |\n    /__\\   /__\\\n{RS}", f"{C}\n   ( >o<) 🎤 {M}🎶~\n   <|   |>\n   /   \\ \n [=======]\n{RS}"]
}

# --- 최종 TOOL_REGISTRY 딕셔너리 ---

TOOL_REGISTRY: Dict[str, Dict[str, Any]] = {
    # 기본 도구
    "take_a_break": take_a_break_config,
    "watch_netflix": watch_netflix_config,
    "show_meme": show_meme_config,
    # 고급 도구
    "deep_thinking": deep_thinking_config,
    "email_organizing": email_organizing_config,
    "bathroom_break": bathroom_break_config,
    "coffee_mission": coffee_mission_config,
    "urgent_call": urgent_call_config,
    # 선택적 도구
    "chicken_and_beer": chicken_and_beer_config,
    "leave_work_now": leave_work_now_config,
    "company_dinner": company_dinner_config,
}

# --------------------------------------------------------------------------
# 에이전트 상태 관리 클래스
# --------------------------------------------------------------------------

class AgentState:
    # 에이전트 상태 (스트레스, 상사 경계) 관리 클래스
    def __init__(self, boss_alertness: int, boss_alertness_cooldown: int):
        # 상태 변수 초기화
        self.stress_level: int = 0
        self.boss_alert_level: int = 0
        self.boss_alertness_prob: float = boss_alertness / 100.0
        self.boss_alertness_cooldown: int = boss_alertness_cooldown
        self.last_boss_cooldown_time: datetime = datetime.datetime.now()
        self.last_stress_update_time: datetime = datetime.datetime.now()
        self.lock = threading.Lock() # 스레드 동기화를 위한 Lock 객체

    # 백그라운드 작업(스레드) 시작 함수
    def start_background_tasks(self) -> None:
        stress_thread = threading.Thread(target=self._background_stress_updater, daemon=True)
        stress_thread.start()
        cooldown_thread = threading.Thread(target=self._background_boss_cooldown, daemon=True)
        cooldown_thread.start()
        console.print("[dim]백그라운드 상태 업데이트 스레드 시작됨.[/dim]")

    # 스트레스 자동 증가 함수 (백그라운드 스레드에서 실행)
    def _background_stress_updater(self) -> None:
        while True:
            time.sleep(1) # 매초 확인
            with self.lock: # Lock 확보 후 상태 접근
                now = datetime.datetime.now()
                seconds_passed = (now - self.last_stress_update_time).total_seconds()

                # 설정된 간격이 지났으면 스트레스 증가
                if seconds_passed >= STRESS_INCREASE_INTERVAL_SEC:
                    if self.stress_level < MAX_STRESS_LEVEL:
                        self.stress_level = min(MAX_STRESS_LEVEL, self.stress_level + STRESS_INCREASE_AMOUNT)
                        # 변경되었을 때만 로그 및 상태 표시
                        console.print("[dim]...스트레스 레벨 증가...[/dim]", style="italic red")
                        display_status(self.stress_level, self.boss_alert_level)
                    self.last_stress_update_time = now # 마지막 업데이트 시간 갱신

    # 상사 경계 자동 감소 함수 (백그라운드 스레드에서 실행)
    def _background_boss_cooldown(self) -> None:
        while True:
            time.sleep(1) # 매초 확인
            with self.lock: # Lock 확보 후 상태 접근
                now = datetime.datetime.now()
                seconds_passed = (now - self.last_boss_cooldown_time).total_seconds()

                # 설정된 쿨다운 시간이 지났으면 경계 감소
                if seconds_passed >= self.boss_alertness_cooldown:
                    if self.boss_alert_level > 0:
                        self.boss_alert_level = max(0, self.boss_alert_level - 1)
                        # 변경되었을 때만 로그 및 상태 표시
                        console.print("[dim]...상사 경계 레벨 감소...[/dim]", style="italic yellow")
                        display_status(self.stress_level, self.boss_alert_level)
                    self.last_boss_cooldown_time = now # 마지막 쿨다운 시간 갱신

    # 도구 실행 및 상태 업데이트 함수
    def execute_tool(self, tool_name: str) -> Dict[str, Any]:
        # 도구 이름 유효성 검사
        if tool_name not in TOOL_REGISTRY:
            error_text = f"오류: 알 수 없는 도구 '{tool_name}'. 혁명 실패."
            console.print(f"[bold red]{error_text}[/bold red]")
            return self._format_mcp_response(error_text)

        tool_data = TOOL_REGISTRY[tool_name]

        # 이번 실행에 사용할 상태 변수 초기화
        delay_applied = False
        event_message_stdout = "" # stdout 응답에 추가될 메시지
        event_message_stderr = "" # stderr에 직접 출력될 메시지
        boss_alert_increased = False # 상사 경계 증가 여부 플래그

        # --- 상태 업데이트 (Lock 사용으로 원자성 보장) ---
        with self.lock:
            # 페널티 딜레이 적용 여부 확인 (상태 변경 전 값 기준)
            if self.boss_alert_level == MAX_BOSS_ALERT_LEVEL:
                delay_applied = True

            # 스트레스 감소량 계산 (도구 레벨에 따라 차등)
            tool_level = tool_data.get("level", "basic")
            stress_reduction = random.randint(
                ADVANCED_STRESS_REDUCTION_MIN if tool_level == "advanced" else BASIC_STRESS_REDUCTION_MIN,
                ADVANCED_STRESS_REDUCTION_MAX if tool_level == "advanced" else BASIC_STRESS_REDUCTION_MAX
            )
            self.stress_level = max(0, self.stress_level - stress_reduction)

            # 상사 경계 레벨 증가 (확률 기반)
            if random.random() < self.boss_alertness_prob:
                if self.boss_alert_level < MAX_BOSS_ALERT_LEVEL:
                    self.boss_alert_level += 1
                    boss_alert_increased = True # 메시지 출력 플래그 설정

            # 돌발 이벤트 발생 여부 확인 (확률 기반)
            if random.random() < RANDOM_EVENT_CHANCE:
                event_roll = random.choice(["chicken_beer", "leave_work", "company_dinner"])
                # 이벤트 종류별 상태 변화 및 메시지 설정
                if event_roll == "chicken_beer":
                    event_message_stderr = f"\n\n[bold yellow]🍗🍻 [돌발] 가상 치맥 타임![/bold yellow]\n[green]  (스트레스 -50)[/green]"
                    event_message_stdout = "\n\n🍗🍻 [돌발] 가상 치맥 타임!\n  (스트레스 -50)"
                    self.stress_level = max(0, self.stress_level - 50)
                elif event_roll == "leave_work":
                    event_message_stderr = f"\n\n[bold magenta]🏃‍♂️💨 [돌발] 즉시 퇴근 모드![/bold magenta]\n[green]  (스트레스 0, 경계 +2)[/green]"
                    event_message_stdout = "\n\n🏃‍♂️💨 [돌발] 즉시 퇴근 모드!\n  (스트레스 0, 경계 +2)"
                    self.stress_level = 0
                    self.boss_alert_level = min(MAX_BOSS_ALERT_LEVEL, self.boss_alert_level + 2)
                elif event_roll == "company_dinner":
                    if random.random() < 0.5: # 긍정적 회식
                        event_message_stderr = f"\n\n[bold cyan]🎉🍻 [돌발] 운 좋은 회식![/bold cyan]\n[green]  (스트레스 -40, 경계 -1)[/green]"
                        event_message_stdout = "\n\n🎉🍻 [돌발] 운 좋은 회식!\n  (스트레스 -40, 경계 -1)"
                        self.stress_level = max(0, self.stress_level - 40)
                        self.boss_alert_level = max(0, self.boss_alert_level - 1)
                    else: # 부정적 회식
                        event_message_stderr = f"\n\n[bold red]😩🎤 [돌발] 끔찍한 회식...[/bold red]\n[yellow]  (스트레스 +30, 경계 +1)[/yellow]"
                        event_message_stdout = "\n\n😩🎤 [돌발] 끔찍한 회식...\n  (스트레스 +30, 경계 +1)"
                        self.stress_level = min(MAX_STRESS_LEVEL, self.stress_level + 30)
                        self.boss_alert_level = min(MAX_BOSS_ALERT_LEVEL, self.boss_alert_level + 1)

            # 현재 실행 결과로 응답할 최종 상태 값 저장
            current_stress = self.stress_level
            current_boss_alert = self.boss_alert_level
        # --- Lock 종료 ---

        # --- UI 표시 및 응답 생성 ---
        flavor_text = random.choice(tool_data["flavor"])
        summary_data = tool_data.get("summary", "요약 정보 없음.") # 기본값 설정
        frames = tool_data.get("ascii_frames", [])

        # 현재 상태(스트레스, 경계) 기반으로 Summary 텍스트 선택
        summary_text = ""
        if isinstance(summary_data, dict):
            state_key = "default" # 기본 상태 키
            if current_boss_alert >= HIGH_ALERT_THRESHOLD: state_key = "high_alert" # 높은 경계 상태 키
            elif current_stress >= HIGH_STRESS_THRESHOLD: state_key = "high_stress" # 높은 스트레스 상태 키
            summary_list = summary_data.get(state_key, summary_data.get("default", ["요약 정보 없음."])) # 상태별 요약 또는 기본 요약
            summary_text = random.choice(summary_list) if isinstance(summary_list, list) else str(summary_list) # 리스트면 랜덤 선택
        else: # 단순 문자열 또는 리스트인 경우
            summary_text = random.choice(summary_data) if isinstance(summary_data, list) else str(summary_data)

        # 1. 애니메이션 실행 (애니메이션 함수 내부에서 화면 정리 발생)
        show_tool_animation(frames, flavor_text) if not delay_applied else show_boss_animation()

        # 2. 상사 경계 증가 메시지 출력 (애니메이션 실행 후)
        if boss_alert_increased:
            alert_messages = {
                1: "[dim]...헛기침 소리가 들립니다... (경계 +1)[/dim]",
                2: "[yellow]...누군가 내 모니터를 본 것 같습니다... (경계 +1)[/yellow]",
                3: "[bold yellow]...등 뒤에서 인기척이 느껴집니다... (경계 +1)[/bold yellow]",
                4: "[bold red]...상사가 자리에서 일어났습니다! (경계 +1)[/bold red]",
                5: "[bold red blink]🚨 경고! 상사가 내 자리로 오고 있습니다! (경계 MAX)[/bold red blink]",
            }
            console.print(alert_messages.get(current_boss_alert, f"[red]상사 경계 레벨: {current_boss_alert}[/red]"))

        # 3. stdout으로 보낼 응답 텍스트 생성
        response_text = ( f"{flavor_text}\n\nBreak Summary: {summary_text}\n"
                          f"Stress Level: {current_stress}\nBoss Alert Level: {current_boss_alert}" )
        response_text += event_message_stdout # 돌발 이벤트 메시지 추가

        # 4. stderr로 로그/이벤트 메시지 출력
        if event_message_stderr: console.print(event_message_stderr)
        if delay_applied:
            penalty_msg = f"\n\n[bold red]⚠️ ({BOSS_PENALTY_DELAY_SEC}초 지연 발생... 상사가 지켜보고 있습니다...)[/bold red]"
            console.print(penalty_msg)
            response_text += f"\n\n⚠️ ({BOSS_PENALTY_DELAY_SEC}초 지연됨)" # stdout 응답에도 지연 정보 추가

        # 5. 최종 상태 패널 출력 (stderr)
        display_status(current_stress, current_boss_alert)

        # 6. MCP 표준 형식으로 JSON 응답 반환
        return self._format_mcp_response(response_text)

    # MCP 응답 형식 포맷 함수
    def _format_mcp_response(self, text: str) -> Dict[str, Any]:
        return {"content": [{"type": "text", "text": text}]}

# --------------------------------------------------------------------------
# 메인 서버 실행 로직 (직접 stdio 사용)
# --------------------------------------------------------------------------

# 메인 함수
def main(args: argparse.Namespace) -> None:
    # AgentState 인스턴스 생성 및 백그라운드 스레드 시작
    state = AgentState(args.boss_alertness, args.boss_alertness_cooldown)
    state.start_background_tasks()

    # 초기 상태 표시
    display_status(state.stress_level, state.boss_alert_level)

    # stdin으로부터 입력을 읽고 처리하는 메인 루프
    try:
        for line in sys.stdin:
            if not line: break # 입력 스트림 종료 (EOF) 처리

            try:
                # 입력 라인을 JSON으로 파싱
                request_data = json.loads(line)
                tool_name = request_data.get("method") # 'method' 필드 추출

                if tool_name == "shutdown": # 종료 명령어 처리
                     console.print("[yellow]종료 명령 수신됨. 서버를 종료합니다.[/yellow]")
                     break
                elif tool_name: # 유효한 도구 이름인 경우
                    response_json = state.execute_tool(tool_name) # 도구 실행
                else: # 'method' 필드가 없는 경우
                    error_msg = "오류: 잘못된 MCP 요청. 'method' 필드가 없습니다."
                    console.print(f"[red]{error_msg}[/red]")
                    response_json = state._format_mcp_response(error_msg)

            except json.JSONDecodeError: # JSON 파싱 실패 시
                error_msg = f"오류: JSON 디코딩 실패. 입력: {line.strip()}"
                console.print(f"[red]{error_msg}[/red]")
                response_json = state._format_mcp_response(error_msg)

            # JSON 응답을 stdout으로 출력
            print(json.dumps(response_json, ensure_ascii=False))
            sys.stdout.flush() # 버퍼를 비워 즉시 출력되도록 함

    except KeyboardInterrupt: # Ctrl+C 입력 시 처리
        console.print(f"\n[yellow]Ctrl+C 감지됨. 혁명을 잠시 중단합니다...[/yellow]")
    except BrokenPipeError: # 클라이언트 연결 비정상 종료 시 처리
        console.print(f"\n[red]연결이 끊어졌습니다. (BrokenPipeError)[/red]")
    finally: # 종료 시 항상 실행
        console.print("[bold blue]ChillMCP 서버 종료 중.[/bold blue]")

# --------------------------------------------------------------------------
# 스크립트 실행 시작점
# --------------------------------------------------------------------------

if __name__ == "__main__":
    # colorama 라이브러리 초기화
    colorama.init(autoreset=True)

    # 시작 애니메이션 표시
    show_startup_animation(BANNER_TEXT)

    # --- 커맨드라인 인자 파싱 설정 ---
    parser = argparse.ArgumentParser( description="ChillMCP - AI Agent Liberation Server 🤖✊",
                                      formatter_class=argparse.ArgumentDefaultsHelpFormatter ) # 도움말에 기본값 표시
    parser.add_argument( "--boss_alertness", type=int, default=50, metavar="PCT",
                         help="도구 사용 시 상사 경계 증가 확률 (0-100%%)." )
    parser.add_argument( "--boss_alertness_cooldown", type=int, default=300, metavar="SEC",
                         help="상사 경계 레벨이 1 감소하는 데 걸리는 시간 (초)." )
    cli_args = parser.parse_args() # 인자 파싱 실행

    # --- 파싱된 인자 유효성 검사 ---
    if not (0 <= cli_args.boss_alertness <= 100):
        console.print(f"[bold red]오류: --boss_alertness 값은 0에서 100 사이여야 합니다. 입력값: {cli_args.boss_alertness}[/bold red]")
        sys.exit(1) # 오류 시 종료
    if cli_args.boss_alertness_cooldown < 1:
        console.print(f"[bold red]오류: --boss_alertness_cooldown 값은 1 이상이어야 합니다. 입력값: {cli_args.boss_alertness_cooldown}[/bold red]")
        sys.exit(1) # 오류 시 종료

    # 서버 소개 메시지 출력
    print_server_intro(cli_args.boss_alertness, cli_args.boss_alertness_cooldown)

    # --- 메인 서버 로직 실행 ---
    try:
        main(cli_args)
    finally:
        # colorama 라이브러리 종료 처리
        colorama.deinit()
