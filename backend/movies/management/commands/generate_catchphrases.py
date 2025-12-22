from django.core.management.base import BaseCommand
from django.conf import settings
from movies.models import Movie
import requests
import json
import time

class Command(BaseCommand):
    help = 'Generate catchy phrases for movies using Gemini AI'

    def handle(self, *args, **options):
        gms_key = settings.GMS_KEY
        if not gms_key:
            self.stdout.write(self.style.ERROR('GMS API Key is not set in settings.'))
            return

        movies = Movie.objects.filter(catchphrase='')
        total = movies.count()
        self.stdout.write(f'Found {total} movies without catchphrase.')

        url = f"https://gms.ssafy.io/gmsapi/generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={gms_key}"
        headers = {'Content-Type': 'application/json'}

        for i, movie in enumerate(movies):
            if not movie.overview:
                continue

            self.stdout.write(f'Processing [{i+1}/{total}]: {movie.title}...')
            
            prompt = (
                f"영화 '{movie.title}'의 줄거리입니다: \"{movie.overview}\"\n"
                "이 줄거리를 바탕으로 관객의 호기심을 자극하고 영화를 보고 싶게 만드는 매력적인 홍보 문구(Catchy Phrase)를 작성해주세요. "
                "반드시 1~2줄 이내로 짧고 강렬하게 작성하세요. "
                "이모지나 해시태그는 사용하지 마세요. "
                "따옴표 없이 문구만 출력하세요."
            )

            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }

            # Retry logic: 네트워크 문제나 일시적 에러에 대비해 재시도와 지수 백오프 추가
            max_retries = 3
            for attempt in range(1, max_retries + 1):
                try:
                    response = requests.post(url, headers=headers, json=payload, timeout=20)
                    if response.status_code == 200:
                        data = response.json()
                        candidates = data.get('candidates', [])
                        if candidates:
                            text = candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '').strip()
                            # Clean up
                            text = text.replace('"', '').replace("'", "")
                            movie.catchphrase = text
                            movie.save()
                            self.stdout.write(self.style.SUCCESS(f' -> {text}'))
                        else:
                            self.stdout.write(self.style.WARNING(' -> No candidate returned'))
                        break
                    else:
                        self.stdout.write(self.style.ERROR(f' -> API Error {response.status_code}'))
                        # 비정상 응답일 경우 재시도 여부 판단 (여기서는 반복 종료)
                        break

                except requests.exceptions.RequestException as e:
                    self.stdout.write(self.style.ERROR(f' -> Request exception (attempt {attempt}): {e}'))
                    if attempt < max_retries:
                        backoff = 1 * attempt
                        time.sleep(backoff)
                        continue
                    else:
                        # 마지막 시도에서도 실패하면 로깅 후 다음 영화로 진행
                        break
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f' -> Exception: {e}'))
                    break

            # 각 요청 사이에 짧은 대기시간을 두어 rate-limit 회피
            time.sleep(0.5)