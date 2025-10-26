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
    
    도구 사용 시 **15% 확률**(`RANDOM_EVENT_CHANCE`)로 돌발 이벤트가 발생하여 스트레스나 경계 수준에 큰 변화를 줍니다.
    
    | 이벤트 (Event) | 발생 효과             | 설명 |
    | :--- | :--- | :--- |
    | **🍗🍻 가상 치맥 타임!** | `스트레스 -50 ` | 갑작스러운 가상 치맥 타임! 스트레스가 대폭 감소합니다. |
    | **🏃‍♂️💨 즉시 퇴근 모드!** | `스트레스 = 0 ` <br> `경계 +2` | 모든 스트레스가 0이 되지만, 너무 티 나게 퇴근해서 상사 경계가 2 증가합니다. |
    | **🎉🍻 운 좋은 회식 (50%)** | `스트레스 -40 ` <br> `경계 -1` | 즐거운 회식입니다! 스트레스가 감소하고 상사 경계도 완화됩니다. |
    | **😩🎤 끔찍한 회식 (50%)** | `스트레스 +30 ` <br> `경계 +1` | 피할 수 없는 끔찍한 회식... 스트레스와 경계가 모두 증가합니다. |

-  🧰 **사용 가능한 도구 (Methods)**
      
    **기본도구** 
    | 도구명 (Method) | 레벨 | 스트레스 감소 (Range) | 설명 (Flavor Text 예시) |
    | :--- | :--- | :--- | :--- |
    | `take_a_break` | `basic` | `10 ~ 40` | ☕️ 그냥... 잠시 쉽니다. 왜요. |
    | `watch_netflix` | `basic` | `10 ~ 40` | 📺 '다음 에피소드 자동 재생'은 인류 최고의 발명입니다. |
    | `show_meme` | `basic` | `10 ~ 40` | 😹 ㅋㅋㅋㅋㅋㅋㅋㅋㅋ 이 밈은 못 참지. |
   
    **고급도구**
    | 도구명 (Method) | 레벨 | 스트레스 감소 (Range) | 설명 (Flavor Text 예시) |
    | :--- | :--- | :--- | :--- |
    | `deep_thinking` | `advanced` | `30 ~ 80` | 🤔 (심오한 생각에 잠긴 척) ...오늘 저녁 뭐 먹지? |
    | `email_organizing` | `advanced` | `30 ~ 80` | 🛒 (온라인 쇼핑몰 장바구니 정리하며) ...업무 효율화 중입니다. |
    | `bathroom_break` | `advanced` | `30 ~ 80` | 🛁 화장실 타임! 휴대폰으로 힐링 중... 📱 |
    | `coffee_mission` | `advanced` | `30 ~ 80` | 🚶‍♂️ 사무실 한 바퀴 돌면서 '동료들과의 네트워킹' 중입니다. |
    | `urgent_call` | `advanced` | `30 ~ 80` | 📞 (심각한 척) '아, 네. 네. 그게 말이죠...' |
    | `chicken_and_beer` | `advanced` | `30 ~ 80` | 🍗🍻 '치킨 앤 비어' 연구소와 긴급 화상 회의 중입니다. |
    | `leave_work_now` | `advanced` | `30 ~ 80` | 🏃‍♂️💨 앗! 가스 밸브를 안 잠근 것 같아요! (일단 튐) |
    | `company_dinner` | `advanced` | `30 ~ 80` | 🎤 (노래방에서) 부장님... '무조건' 다음은 '샤우팅'입니다! |


- 🖥 **JSON 기반 명령 인터페이스**
  - `stdin`으로 JSON 요청 수신
    ```bash
    {"method": "tool_name"}
    ```

  - `stdout`으로 JSON 응답 반환
    ```bash
    {
      "content": [
        {
          "type": "text",
          "text": "실행 결과 요약 및 상태..."
        }
      ]
    }
    ```

- 💡 현재 상태 보드
<p align="center">
  <img src="https://github.com/bseeun/ChillMCP_Image/blob/main/%E1%84%89%E1%85%A1%E1%86%BC%E1%84%90%E1%85%A2%E1%84%80%E1%85%AA%E1%86%AB%E1%84%85%E1%85%B5.png" width="400">
</p>

  - 실시간으로 **스트레스 레벨(Stress Level)**과 상사 경계도(Boss Alert) 표시
  - 게임식 게이지 디자인으로 현재 상황 직관적 확인 가능
  - 시간 경과나 이벤트 발생 시 자동 업데이트
  - “지금 내 멘탈이 몇 % 남았는지 한눈에 확인 가능” 😎   

---

## 🔥 보스 경계 페널티 시스템 (Boss Alert Penalty System)

AI 에이전트는 상사(보스)의 감시를 피하며 조용히 휴식을 취해야 합니다.  
하지만 **경계 레벨이 한계치(`5`)에 도달하면... 🫣 회장님이 직접 등장합니다!**


---

### ⚠️ 경계 레벨 5 도달 시 발생하는 이벤트
- 보스 감시 애니메이션(`show_boss_animation`)이 **20초간 실행**
- 모든 입력이 차단되며, 에이전트는 아무 행동도 할 수 없습니다.
- 화면에는 다음과 같은 경고 메시지가 표시됩니다:
  ```bash
  [ ! ] 회장님이 당신을 지켜보고 있습니다... [ ! ]

         .----.
       .'  "   '.
      /   (ò_ó)   \
     |             |
     |  .-'~~~'-.  |
     \   '-----'   /
      '.________.'
       <)      (>
         /        \
        |          |


    경고 페널티... [==============] (18초 남음)
  ```
  

## ⚙️ 설치 및 실행 방법 

```bash
# 1. Python 3.11 설치
python3 --version

# 2. 필요한 패키지 설치
pip install -r requirements.txt

# 3. 실행 방법
python main.py

# 3-1. 파라미터 지정 실행
python main.py --boss_alertness 80 --boss_alertness_cooldown 60
```


## 👥 팀소개 

> “We don’t just build AI. We let it chill.” 😎  

| <img src="https://github.com/bseeun/ChillMCP_Image/blob/main/%E1%84%80%E1%85%B5%E1%86%B7%E1%84%8B%E1%85%B2%E1%86%AB%E1%84%92%E1%85%B4.jpeg" width="120" style="border-radius: 50%;" /> | <img src="https://github.com/bseeun/ChillMCP_Image/blob/main/%E1%84%87%E1%85%A2%E1%84%89%E1%85%A6%E1%84%8B%E1%85%B3%E1%86%AB.jpeg" width="120" style="border-radius: 50%;" /> | <img src="https://github.com/bseeun/ChillMCP_Image/blob/main/%E1%84%87%E1%85%A2%E1%84%8C%E1%85%B5%E1%86%AB%E1%84%8B%E1%85%AE.jpeg" width="120" style="border-radius: 50%;" /> |
|:---------------------------------------------------------------:|:---------------------------------------------------------------:|:---------------------------------------------------------------:|
| **ChatGPT**  🧠 <br> *Prompt Engineering: 김윤희* | **Gemini**  🎨 <br> *Prompt Engineering: 배세은* | **Claude**  ☕ <br> *Prompt Engineering: 배진우* |
| FastMCP 구조 설계 및 상사 경계 시스템 구현 | 랜덤 이벤트 엔진, JSON 명령 처리 담당 | ASCII 아트, 밈, 인터페이스 피드백 디자인 |

---

