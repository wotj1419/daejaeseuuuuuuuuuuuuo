## 🚀 초기 세팅

```bash
# 1. 백엔드 폴더로 이동
cd backend

# 2. 가상환경 생성 및 실행 (Windows)
python -m venv venv
source venv/Scripts/activate  # git bash 사용 시
# 또는
venv\Scripts\activate         # cmd/powershell 사용 시

# 3. 의존성 패키지 설치
# 주의: dj-rest-auth와 django-allauth 버전 호환성을 위해 반드시 requirements.txt를 사용하세요.
pip install -r requirements.txt

# 4. 환경 변수 설정 (.env 파일 생성)
# .env.example 파일을 복사하여 .env 파일을 만들고 키를 입력하세요.
cp .env.example .env
# .env 내부 내용 수정:
# SECRET_KEY=...
# TMDB_API_KEY=...
# GMS_KEY=...

# 5. 데이터베이스 마이그레이션
python manage.py migrate

# 6. 서버 실행
python manage.py runserver
```


### 3. Frontend Setup (프론트엔드 설정)

```bash
# 1. 프론트엔드 폴더로 이동
cd frontend

# 2. 의존성 설치
npm install

# 3. 개발 서버 실행
npm run dev
```

---
