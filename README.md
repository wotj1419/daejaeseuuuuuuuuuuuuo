## ğŸš€ ì´ˆê¸° ì„¸íŒ…

```bash
# 1. ë°±ì—”ë“œ í´ë”ë¡œ ì´ë™
cd backend

# 2. ê°€ìƒí™˜ê²½ ìƒì„± ë° ì‹¤í–‰ (Windows)
python -m venv venv
source venv/Scripts/activate  # git bash ì‚¬ìš© ì‹œ
# ë˜ëŠ”
venv\Scripts\activate         # cmd/powershell ì‚¬ìš© ì‹œ

# 3. ì˜ì¡´ì„± íŒ¨í‚¤ì§€ ì„¤ì¹˜
# ì£¼ì˜: dj-rest-authì™€ django-allauth ë²„ì „ í˜¸í™˜ì„±ì„ ìœ„í•´ ë°˜ë“œì‹œ requirements.txtë¥¼ ì‚¬ìš©í•˜ì„¸ìš”.
pip install -r requirements.txt

# 4. í™˜ê²½ ë³€ìˆ˜ ì„¤ì • (.env íŒŒì¼ ìƒì„±)
touch .env
# .env.example íŒŒì¼ì„ ë³µì‚¬í•˜ì—¬ .env íŒŒì¼ì„ ë§Œë“¤ê³  í‚¤ë¥¼ ì…ë ¥í•˜ì„¸ìš”.
cp .env.example .env
# .env ë‚´ë¶€ ë‚´ìš© ìˆ˜ì •:
# SECRET_KEY=...
# TMDB_API_KEY=...
# GMS_KEY=...

# 5. ë°ì´í„°ë² ì´ìŠ¤ ë§ˆì´ê·¸ë ˆì´ì…˜
python manage.py migrate

# 6. ì˜í™” íŒŒì¼ ë¡œë“œ
python manage.py load_movies

# 6. ì„œë²„ ì‹¤í–‰
python manage.py runserver
```


### 3. Frontend Setup (í”„ë¡ íŠ¸ì—”ë“œ ì„¤ì •)

```bash
# 1. í”„ë¡ íŠ¸ì—”ë“œ í´ë”ë¡œ ì´ë™
cd frontend

# 2. ì˜ì¡´ì„± ì„¤ì¹˜
npm install

# 3. ê°œë°œ ì„œë²„ ì‹¤í–‰
npm run dev
```

---

### 4. ë¸Œëœì¹˜ ì´ë™

git switch ë¸Œëœì¹˜ì´ë¦„

### ì˜¤ë¥˜
401: ì¸ì¦ ì•ˆ ë¨ (ë¡œê·¸ì¸Â·í† í° ë¬¸ì œ)

404: ìš”ì²­í•œ ì£¼ì†Œë‚˜ ë°ì´í„° ì—†ìŒ

500: ì„œë²„ ë‚´ë¶€ ì½”ë“œ ì˜¤ë¥˜
## Taste embedding feature (AI ÃëÇâ ¿ä¾à)

- Ãß°¡ ÀÇÁ¸¼º: `sentence-transformers`, `numpy` °¡ `backend/requirements.txt`¿¡ Æ÷ÇÔµÇ¾î ÀÖ½À´Ï´Ù. `pip install -r requirements.txt`¸¦ ´Ù½Ã ½ÇÇàÇØ ¼³Ä¡ÇÏ¼¼¿ä.
- ÀÓº£µù ¹éÇÊ: ÁÁ¾Æ¿äÇÑ ¿µÈ­ ÀÓº£µùÀ» »çÀü¿¡ Ã¤¿ì·Á¸é ¹é¿£µå °¡»óÈ¯°æ¿¡¼­ ¾Æ·¡¸¦ ½ÇÇàÇÕ´Ï´Ù.

```
cd backend
python manage.py backfill_movie_embeddings  # --force ¿É¼ÇÀ¸·Î Àç°è»ê
```

- ÃëÇâ ¿ä¾à È®ÀÎ:

```
# ÅäÅ«ÀÌ ÀÖ´Ù°í °¡Á¤ (TOKEN È¯°æ º¯¼ö)
curl -H "Authorization: Token $TOKEN" http://127.0.0.1:8000/api/accounts/me/taste/
```

- ºñ½ÁÇÑ À¯Àú ÃßÃµ (»óÀ§ 10¸í):

```
curl -H "Authorization: Token $TOKEN" "http://127.0.0.1:8000/api/accounts/me/similar-users/?k=10"
```
