## 학생 보충 자료: 코드 읽기

### 변수와 자료형

변수는 이름을 붙인 보관함입니다. `int raw = 512;`는 정수 512를 raw에 저장합니다. `float voltage = 2.5;`는 소수 값을 저장합니다. `bool detected = true;`는 참·거짓 상태를 저장합니다. UNO R3의 int는 16비트이므로 큰 시간값에는 unsigned long을 사용합니다.

### 조건과 반복

```cpp
int raw = analogRead(A0); // 입력을 한 번 읽어 보관
if (raw < 400) {          // 조건이 참일 때만 실행
  digitalWrite(9, HIGH);
} else {
  digitalWrite(9, LOW);
}
```

`=`는 대입이고 `==`는 같은지 비교합니다. `&&`는 두 조건이 모두 참, `||`는 하나 이상 참, `!`는 참·거짓을 뒤집습니다. 중괄호 안의 들여쓰기는 실행 순서를 읽기 쉽게 만듭니다.

```cpp
for (int i = 0; i < 3; i++) {
  Serial.println(i); // 0, 1, 2를 각각 한 줄씩 출력
}
```

### 함수와 반환값

`analogRead(A0)`는 읽은 값을 돌려주고 `digitalWrite(9, HIGH)`는 출력을 바꿉니다. 함수 이름 뒤 괄호 안은 인수입니다. `Serial.print`는 줄을 바꾸지 않고 `Serial.println`은 마지막에 줄바꿈을 붙입니다. Python 기록기는 이 줄바꿈을 한 기록의 끝으로 사용합니다.

### Python의 차이

Python은 중괄호 대신 들여쓰기로 묶음을 나타냅니다. 문자열은 따옴표로 감싸고, `float('2.5')`처럼 숫자로 변환해야 계산할 수 있습니다. `try/except`는 변환 실패나 포트 오류를 처리합니다.

```python
try:
    value = float('2.5')
except ValueError:
    value = None
if value is not None:
    print(value * 2)
```

### 자주 만나는 오류

| 증상 | 먼저 확인할 것 |
| --- | --- |
| 스케치 컴파일 실패 | 세미콜론, 괄호, 라이브러리, 보드 선택 |
| 업로드 실패 | 포트, 데이터 케이블, 다른 프로그램의 포트 점유 |
| Python에서 serial 모듈 없음 | 같은 Python으로 py -m pip install pyserial 실행 |
| CSV에 값이 없음 | 시리얼 속도, 출력 열 수, ERROR/TIMEOUT 메시지 |
| LED 또는 모터 때문에 재시작 | 전원 용량, 단락, 부하 배선 |

센서 코드를 서로 합칠 때는 핀과 타이머 충돌을 확인합니다. UNO R3에서 Servo 라이브러리는 Timer1을 사용하여 PWM 9·10에 영향을 줄 수 있고, tone도 일부 PWM 동작과 충돌할 수 있습니다. 이 교재의 개별 실습은 따로 실행하도록 구성했습니다.
