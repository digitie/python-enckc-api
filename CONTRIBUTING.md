# CONTRIBUTING.md

`python-enckc-api` 프로젝트에 기여해 주셔서 감사합니다.

## 개발 환경 설정

1. 저장소 클론 및 가상환경 생성
```bash
git clone https://github.com/digitie/python-enckc-api.git
cd python-enckc-api
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

2. 개발 의존성 설치
```bash
pip install -e ".[dev,debug-ui]"
```

3. 로컬 API 키 설정
`.env.local` 파일에 발급받은 API 키를 설정합니다:
```text
ENCKC_API_KEY=YOUR_KEY_HERE
```

## 브랜치 및 PR 규칙

1. `main` 브랜치에 직접 푸시하지 않고 항상 feature 브랜치(`feat/...`, `fix/...`)를 생성합니다.
2. 모든 변경 사항에 대해 단위 테스트를 작성합니다.
3. PR 제출 전 로컬 검증을 통과해야 합니다:
```bash
python -m pytest -q
python -m ruff check .
python -m mypy src/enckc
```
