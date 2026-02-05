<INSTRUCTIONS>
# week4 프로젝트 전용 AGENTS

## Scope (week4 전용)

- 수정 범위는 `backend/`, `data/`, `frontend/`, `docs/`, `writeup.md`에 한정한다.
- 그 외 파일 `assignment.md`는 변경하지 않는다.
- 새로운 파일이 필요할 경우, 반드시 위 폴더들 내부에 생성한다.
- 불필요한 리팩터링/포맷팅은 피하고 최소 변경을 유지한다.

## API 구조 (FastAPI)

- 앱 엔트리: `backend/app/main.py`
- 라우터:
  - Notes: `backend/app/routers/notes.py`
    - `GET /notes/` 목록
    - `POST /notes/` 생성
    - `GET /notes/search/?q=` 검색(없으면 전체)
    - `GET /notes/{note_id}` 단건
  - Action Items: `backend/app/routers/action_items.py`
    - `GET /action-items/` 목록
    - `POST /action-items/` 생성
    - `PUT /action-items/{item_id}/complete` 완료 처리
- 정적 프론트엔드:
  - `/` → `frontend/index.html`
  - `/static/*` → `frontend/` 정적 파일

## DB/데이터

- SQLite 사용, 기본 경로: `./data/app.db`
- 환경변수: `DATABASE_PATH`로 경로 변경 가능
- 시드: `data/seed.sql`
  - DB 파일이 처음 생성될 때만 실행
  - 테이블: `notes`, `action_items`

## 폴더 역할

- `backend/`: FastAPI + SQLAlchemy + 서비스 로직
- `data/`: SQLite DB 파일, 시드 SQL
- `frontend/`: 순수 HTML/CSS/JS (번들링 없음)

## 변경 규칙

- API 추가/변경 시 라우터/스키마/모델의 일관성을 유지한다.
- DB 스키마 변경 시 `data/seed.sql` 동기화가 필요하면 함께 갱신한다.
- 프론트엔드 JS는 `/notes`, `/action-items` API 계약을 따른다.
  </INSTRUCTIONS>
