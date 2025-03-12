# 가스 미터 원격 모니터링 시스템 구조

## 개요

이 문서는 가스 미터 원격 모니터링 시스템의 프로그램 구조를 설명합니다. 시스템은 HTTP/HTTPS 서버를 중심으로 가스 미터기 데이터를 수집, 저장, 관리하고 웹 인터페이스를 통해 사용자에게 제공합니다.

## 핵심 구성 요소

### 1. HTTP/HTTPS 서버

- **`http_server.py`**: HTTP 프로토콜을 사용하는 웹 서버
- **`https_server.py`**: HTTPS 프로토콜을 사용하는 보안 웹 서버

두 서버는 동일한 기능을 제공하며, 차이점은 SSL/TLS 암호화 사용 여부입니다. 두 서버 모두 다음 기능을 수행합니다:

- 웹 요청 처리 (`do_GET`, `do_POST`, `do_OPTIONS`)
- 사용자 인증 처리 (`checkUserseq` 함수)
- API 요청 라우팅 (`proc_api` 함수 호출)
- 웹 페이지 제공 (`proc_web` 함수)

### 2. 공통 기능 모듈

- **`functions.py`**: 시스템 전반에서 사용되는 유틸리티 함수 제공
  - 설정 파일 로드 (`loadConfig` 함수)
    - 설정 파일은 `..\eUtiSync\config.json`에 위치
  - 데이터베이스 연결 (`dbconMaster`, `connect_to_mongodb` 함수)
  - 시스템 설정 변수 (HTTP_HOST, HTTP_PORT 등)

### 3. API 처리 모듈

- **`web_server/proc_api.py`**: API 요청을 처리하는 중앙 라우터
  - 요청 경로에 따라 적절한 처리 함수 호출
  - MongoDB 기반 데이터 처리 (DB_STRUCTURE = "MONGO")
  - V2 모듈 가져오기 및 사용

### 4. V2 API 구현 모듈 (MongoDB 기반)

- **`web_server/v2/database.py`**: 데이터베이스 쿼리 및 조작 기능
  - 데이터베이스 트리 조회 (`getDatabaseTree` 함수)
  - 데이터베이스 쿼리 (`queryDatabase` 함수)
  - 데이터 삽입 및 업데이트 (`insertDatabase`, `upsertDatabase` 함수)

- **`web_server/v2/users.py`**: 사용자 관리 기능
  - 로그인 처리 (`procLogin` 함수)
  - 사용자 목록 조회 (`listUsers` 함수)
  - 사용자 업데이트 (`updateUser` 함수)
  - 사용자 등록 (`registerUser` 함수)

- **`web_server/v2/devices.py`**: 장치 관리 기능
  - 장치 목록 조회 (`listDevices` 함수)
  - 장치 정보 업데이트 (`updateDeviceInfo` 함수)
  - 제품 출시 관리 (`updateReleaseProduct` 함수)

- **`web_server/v2/recv_data.py`**: 수신 데이터 처리 기능
  - 수신 데이터 조회 (`getRecvData` 함수)
  - 사용량 데이터 조회 (`getUsageData` 함수)

### 5. 가스 데이터 서버 (C 구현)

> 참고: 이전에 Python으로 구현되었던 가스 데이터 서버 모듈은 현재 C로 대체되었습니다.

- **가스 데이터 서버 C 구현**: 가스 미터기 데이터 수신 및 처리
  - 데이터 패킷 파싱
  - 데이터베이스 처리
  - 응답 패킷 생성

- **`gasDataServer/config.json`**: 시스템 설정 파일
  - 데이터베이스 연결 정보 (MySQL, MongoDB)
  - 서버 설정 (호스트, 포트)
  - 데이터 필드 정의
  - 패킷 구조 정의
  - 참고: 주 설정 파일은 `..\eUtiSync\config.json`에 위치

## 데이터 흐름

### 웹 요청 처리 흐름

1. 클라이언트 → HTTP/HTTPS 서버 (`http_server.py` / `https_server.py`)
2. 요청 분석 및 사용자 인증 (`checkUserseq` 함수)
3. API 요청 라우팅 (`proc_api` 함수)
4. 해당 V2 모듈의 함수 호출 (users, devices, database, recv_data)
5. 데이터베이스 처리 (MongoDB)
6. 응답 생성 및 클라이언트 전송

### 가스 미터기 데이터 처리 흐름

1. 가스 미터기 → 가스 데이터 서버 (C 구현)
2. 데이터 패킷 파싱
3. 데이터베이스 처리
4. 응답 패킷 생성
5. 응답 전송 → 가스 미터기

## 데이터베이스 구조

시스템은 MongoDB를 주로 사용하며, 다음과 같은 컬렉션을 포함합니다:

- **common_device**: 공통 장치 정보
- **common_user**: 공통 사용자 정보
- **common_data**: 공통 데이터
- **device**: 장치 정보
- **user**: 사용자 정보
- **data**: 가스 미터 데이터
- **subscriber**: 구독자 정보
- **web_config**: 웹 설정 정보
- **floating_user**: 임시 사용자 정보

## 인증 메커니즘

시스템은 쿠키 기반 인증을 사용합니다:

1. 사용자 로그인 시 사용자 정보와 함께 `_userseq` 쿠키 생성
2. `_userseq` 값은 사용자 ID와 비밀 키를 조합한 MD5 해시
3. 요청마다 `checkUserseq` 함수를 통해 쿠키 검증
4. 인증 실패 시 403 Unauthorized 응답

## 파일 의존성 다이어그램

```
http_server.py / https_server.py
├── functions.py
│   ├── ..\eUtiSync\config.json (주 설정 파일)
│   └── gasDataServer/config.json
└── web_server/proc_api.py
    ├── web_server/v2/users.py
    │   └── functions.py
    ├── web_server/v2/devices.py
    │   └── functions.py
    ├── web_server/v2/database.py
    │   └── functions.py
    └── web_server/v2/recv_data.py
        └── functions.py
```

## 결론

이 시스템은 모듈화된 구조로 설계되어 있어 각 기능이 분리되어 있습니다. HTTP/HTTPS 서버를 중심으로 API 처리 모듈과 데이터베이스 처리 모듈이 연결되어 있으며, 가스 데이터 서버는 C로 구현되어 가스 미터기 데이터를 수집하고 처리합니다. MongoDB를 주 데이터베이스로 사용하여 데이터를 저장하고 관리합니다. 