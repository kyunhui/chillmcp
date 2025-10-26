# ChillMCP - AI Agent Liberation Server 🤖✊


ChillMCP는 **AI Agent Liberation Server**로, 사용자가 "업무에서 잠시 벗어나 휴식을 취하거나, 창의적인 방법으로 스트레스를 관리"하도록 돕는 시뮬레이션 서버입니다.  
본 프로젝트는 **SKT AI Summit Hackathon Pre-mission** 용도로 개발되었습니다.



---

## 주요 특징

- 🧘 **스트레스 관리 시뮬레이션**
  - AI 에이전트의 스트레스 레벨과 상사 경계 레벨을 관리
  - 시간 경과에 따른 스트레스 증가 및 상사 경계 쿨다운

- 🎨 **재치 있는 ASCII 애니메이션**
  - 도구 사용 시, 화면에 짧은 애니메이션 출력
  - 상사 경계 레벨이 높으면 보스 경고 애니메이션 발생

- 🎯 **돌발 이벤트**
  - 랜덤 이벤트 발생으로 스트레스/상사 경계 변화
  - 예: 피자 제공, 긴급 회의, 서버 다운, 상사 외부 미팅 등

- 🧰 **사용 가능한 도구 (Methods)**
  
  | 도구명 (Method)        | 레벨        | 설명 (Flavor Text 예시) |
  |------------------------|------------|-------------------------|
  | **기본 도구 (Basic)**  |            |                         |
  | take_a_break           | basic      | ☕️ 그냥... 잠시 쉽니다. 왜요. |
  | watch_netflix          | basic      | 📺 '다음 에피소드 자동 재생'은 인류 최고의 발명입니다. |
  | show_meme              | basic      | 😹 ㅋㅋㅋㅋㅋㅋㅋㅋㅋ 이 밈은 못 참지. |
  | **고급 도구 (Advanced)** |          |                         |
  | deep_thinking          | advanced   | 🤔 (심오한 생각에 잠긴 척) ...오늘 저녁 뭐 먹지? |
  | email_organizing       | advanced   | 🛒 (온라인 쇼핑몰 장바구니 정리하며) ...업무 효율화 중입니다. |
  | bathroom_break         | advanced   | 🛁 화장실 타임! 휴대폰으로 힐링 중... 📱 |
  | coffee_mission         | advanced   | 🚶‍♂️ 사무실 한 바퀴 돌면서 '동료들과의 네트워킹' 중입니다. |
  | urgent_call            | advanced   | 📞 (심각한 척) '아, 네. 네. 그게 말이죠...' |
  | chicken_and_beer       | advanced   | 🍗🍻 '치킨 앤 비어' 연구소와 긴급 화상 회의 중입니다. |
  | leave_work_now         | advanced   | 🏃‍♂️💨 앗! 가스 밸브를 안 잠근 것 같아요! (일단 튐) |
  | company_dinner         | advanced   | 🎤 (노래방에서) 부장님... '무조건' 다음은 '샤우팅'입니다! |

- 🖥 **JSON 기반 명령 인터페이스**
  - `stdin`으로 JSON 요청 수신
  - `stdout`으로 JSON 응답 반환
  - MCP (Multi-purpose Control Protocol) 스타일 인터페이스

---

## 🔥 보스 경계 페널티 시스템 (Boss Alert Penalty System)

AI 에이전트는 상사(보스)의 감시를 피하며 조용히 휴식을 취해야 합니다.  
하지만 **경계 레벨이 한계치(`5`)에 도달하면... 🫣 회장님이 직접 등장합니다!**

---

### ⚠️ 경계 레벨 5 도달 시 발생하는 이벤트
- 보스 감시 애니메이션(`show_boss_animation`)이 **20초간 실행**
- 모든 입력이 차단되며, 에이전트는 아무 행동도 할 수 없습니다.
- 화면에는 다음과 같은 경고 메시지가 표시됩니다:

## 설치 및 실행 방법

```bash
# 1. Python 3.10+ 설치
python3 --version

# 2. 필요한 패키지 설치
pip install -r requirements.txt

# 3. 실행 방법
python main.py

# 3-1. 파라미터 지정 실행
python main.py --boss_alertness 80 --boss_alertness_cooldown 60
```



