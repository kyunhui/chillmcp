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

- 🧰 **기본 / 고급 도구**
  - 기본(Basic) : take_a_break, watch_netflix, show_meme 등
  - 고급(Advanced) : deep_thinking, email_organizing, urgent_call 등
  - 각 도구별 ASCII 애니메이션과 재치있는 Flavor Text 제공

- 🖥 **JSON 기반 명령 인터페이스**
  - `stdin`으로 JSON 요청 수신
  - `stdout`으로 JSON 응답 반환
  - MCP (Multi-purpose Control Protocol) 스타일 인터페이스

---

## 설치 방법

```bash
# 1. Python 3.10+ 설치
python3 --version

# 2. 필요한 패키지 설치
pip install -r requirements.txt

