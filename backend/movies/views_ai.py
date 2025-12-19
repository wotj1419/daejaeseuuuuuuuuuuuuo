from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
import requests
import json

class MovieAIRecommendAPIView(APIView):
    def post(self, request):
        user_input = request.data.get('query', '').strip()
        if not user_input:
            return Response({'error': '질문을 입력해주세요.'}, status=400)

        gms_key = settings.GMS_KEY
        if not gms_key:
            return Response({'error': 'GMS API Key가 설정되지 않았습니다.'}, status=500)
        
        tmdb_api_key = settings.TMDB_API_KEY
        if not tmdb_api_key:
             return Response({'error': 'TMDB API Key가 설정되지 않았습니다.'}, status=500)

        # 시스템 프롬프트: JSON 포맷 강제
        system_prompt = (
            "당신은 영화 추천 전문가 '무비메이트'입니다. "
            "사용자의 질문이나 상황에 맞는 영화 5편을 추천해주세요. "
            "반드시 다음 JSON 포맷으로만 답변해주세요. 다른 멘트는 절대 하지 마세요. "
            "Format: "
            '[{"title": "영화제목", "reason": "추천이유"}]'
        )

        url = f"https://gms.ssafy.io/gmsapi/generativelanguage.googleapis.com/v1beta/models/gemini-2.5-pro:generateContent?key={gms_key}"
        headers = {'Content-Type': 'application/json'}
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": f"{system_prompt}\n\n사용자: {user_input}\n\n무비메이트:"
                        }
                    ]
                }
            ]
        }

        try:
            # 1. AI에게 추천 영화 목록 받기
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            
            candidates = data.get('candidates', [])
            if not candidates:
                return Response({'message': 'AI가 답변을 생성하지 못했습니다.'}, status=500)
            
            ai_text = candidates[0].get('content', {}).get('parts', [{}])[0].get('text', '')
            
            # 마크다운 코드 블록 제거 (```json ... ```)
            if "```json" in ai_text:
                ai_text = ai_text.split("```json")[1].split("```")[0]
            elif "```" in ai_text:
                 ai_text = ai_text.split("```")[1].split("```")[0]
            
            try:
                recommended_list = json.loads(ai_text.strip())
            except json.JSONDecodeError:
                # 파싱 실패 시 텍스트만 줌
                print(f"JSON Parsing Error. Raw Text: {ai_text}")
                return Response({'result': ai_text, 'movies': []})

            # 2. TMDB에서 영화 정보 검색
            results = []
            tmdb_search_url = "https://api.themoviedb.org/3/search/movie"
            
            for item in recommended_list:
                title = item.get('title')
                reason = item.get('reason')
                
                # TMDB 검색
                params = {
                    'api_key': tmdb_api_key,
                    'query': title,
                    'language': 'ko-KR',
                    'page': 1
                }
                tmdb_res = requests.get(tmdb_search_url, params=params, timeout=5)
                if tmdb_res.status_code == 200:
                    search_data = tmdb_res.json()
                    if search_data['results']:
                        movie = search_data['results'][0] # 첫 번째 결과 사용
                        movie['ai_reason'] = reason # 추천 이유 추가
                        
                        # 필요한 필드만 정리
                        results.append({
                            'tmdb_id': movie.get('id'),
                            'title': movie.get('title'),
                            'overview': movie.get('overview'),
                            'poster_path': movie.get('poster_path'),
                            'vote_average': movie.get('vote_average'),
                            'release_date': movie.get('release_date'),
                            'ai_reason': reason
                        })
            
            return Response({
                'query': user_input,
                'result': f"'{user_input}'에 대한 AI 추천 결과입니다.",
                'movies': results
            })

        except requests.exceptions.RequestException as e:
            print(f"Error calling GMS API: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response text: {e.response.text}")
            
            return Response({
                'error': 'GMS API 호출 중 오류가 발생했습니다.',
                'detail': str(e)
            }, status=500)
        except Exception as e:
            print(f"Unexpected error: {e}")
            return Response({
                'error': '서버 내부 오류가 발생했습니다.',
                'detail': str(e)
            }, status=500)
