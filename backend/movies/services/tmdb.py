import requests
from django.conf import settings
from ..models import Movie, Genre

class TMDBService:
    """
    TMDB API와의 통신을 전담하는 서비스 클래스입니다.
    중복된 API 호출 로직을 제거하고 중앙 집중식으로 관리합니다.
    """
    
    BASE_URL = "https://api.themoviedb.org/3"
    
    @classmethod
    def get_api_key(cls):
        """설정파일에서 API 키를 가져옵니다. 공백 등 불필요한 문자를 제거합니다."""
        key = getattr(settings, 'TMDB_API_KEY', '')
        return str(key).strip() if key else ''

    @classmethod
    def fetch_popular_movies(cls, page=1):
        """인기 영화 목록을 TMDB에서 가져옵니다."""
        api_key = cls.get_api_key()
        if not api_key:
            print("경고: TMDB_API_KEY가 설정되지 않았습니다.")
            return []

        url = f"{cls.BASE_URL}/movie/popular"
        params = {
            'api_key': api_key,
            'language': 'ko-KR',
            'page': page
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 401:
                print("오류: TMDB API 키가 유효하지 않습니다 (401 Unauthorized). .env 파일을 확인해주세요.")
                return []
            response.raise_for_status()
            data = response.json()
            return cls._format_movie_list(data.get('results', []))
        except requests.exceptions.RequestException as e:
            print(f"인기 영화 가져오기 실패: {e}")
            return []

    @classmethod
    def fetch_movie_detail(cls, tmdb_id):
        """특정 영화의 상세 정보를 TMDB에서 가져오고 DB에 저장/업데이트합니다."""
        api_key = cls.get_api_key()
        if not api_key:
            return None

        url = f"{cls.BASE_URL}/movie/{tmdb_id}"
        params = {
            'api_key': api_key,
            'language': 'ko-KR',
        }
        
        try:
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 401:
                print("오류: TMDB API 키가 유효하지 않습니다 (401 Unauthorized).")
                return None
            if response.status_code == 200:
                data = response.json()
                
                # 장르 정보 처리 (Genre 모델 연동)
                genres = []
                if 'genres' in data:
                    for g in data['genres']:
                        genre, _ = Genre.objects.get_or_create(name=g['name'])
                        genres.append(genre)

                # 영화 정보 DB 저장 (이미 존재하면 건너뛰고 없으면 생성)
                movie, created = Movie.objects.get_or_create(
                    tmdb_id=data['id'],
                    defaults={
                        'title': data['title'],
                        'original_title': data.get('original_title', ''),
                        'overview': data.get('overview', ''),
                        'release_date': data.get('release_date') or None,
                        'poster_path': data.get('poster_path', ''),
                        'backdrop_path': data.get('backdrop_path', ''),
                        'vote_average': data.get('vote_average', 0),
                        'popularity': data.get('popularity', 0),
                    }
                )
                
                if created:
                    movie.genres.set(genres)
                
                return movie
        except Exception as e:
            print(f"TMDB에서 영화 상세 정보 가져오기 실패 (ID: {tmdb_id}): {e}")
            return None
        return None

    @classmethod
    def search_movies(cls, query, page=1):
        """키워드로 영화를 검색합니다."""
        api_key = cls.get_api_key()
        if not api_key:
            return {'results': [], 'total_results': 0}

        url = f"{cls.BASE_URL}/search/movie"
        params = {
            'api_key': api_key,
            'query': query,
            'language': 'ko-KR',
            'page': page
        }
        
        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 401:
                print("오류: TMDB API 키가 유효하지 않습니다 (401 Unauthorized).")
                return {'results': [], 'total_results': 0}
            response.raise_for_status()
            data = response.json()
            return {
                'results': cls._format_movie_list(data.get('results', [])),
                'total_results': data.get('total_results', 0)
            }
        except requests.exceptions.RequestException as e:
            print(f"영화 검색 실패 (Query: {query}): {e}")
            return {'results': [], 'total_results': 0}

    @classmethod
    def fetch_movie_trailer(cls, tmdb_id, language="ko-KR"):
        """
        영화의 예고편 URL(YouTube)을 가져옵니다.
        한국어(ko-KR)로 먼저 시도하고, 결과가 없으면 영어(en-US)로 재시도합니다.
        """
        api_key = cls.get_api_key()
        if not api_key:
            return None

        url = f"{cls.BASE_URL}/movie/{tmdb_id}/videos"
        params = {
            "api_key": api_key,
            "language": language,
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 401:
                print(f"오류: TMDB API 키가 유효하지 않습니다 (401 Unauthorized). Key: {api_key[:4]}***")
                return None
            if response.status_code == 404:
                return None
                 
            response.raise_for_status()
            data = response.json()

            # YouTube Trailer 필터링
            trailers = [
                video for video in data.get("results", [])
                if video.get("site") == "YouTube" and video.get("type") == "Trailer"
            ]

            # 한국어로 찾았는데 없으면 영어로 다시 시도
            if not trailers and language == "ko-KR":
                return cls.fetch_movie_trailer(tmdb_id, language="en-US")

            if not trailers:
                return None

            youtube_key = trailers[0]["key"]
            return f"https://www.youtube.com/embed/{youtube_key}"
            
        except requests.exceptions.RequestException as e:
            print(f"예고편 가져오기 실패 (ID: {tmdb_id}, Lang: {language}): {e}")
            return None

    @staticmethod
    def _format_movie_list(raw_results):
        """TMDB 원본 데이터를 내부 통신용 포맷으로 변환합니다."""
        formatted = []
        for movie in raw_results[:20]:
            formatted.append({
                'tmdb_id': movie.get('id'),
                'title': movie.get('title'),
                'original_title': movie.get('original_title'),
                'overview': movie.get('overview', ''),
                'release_date': movie.get('release_date'),
                'poster_path': movie.get('poster_path', ''),
                'backdrop_path': movie.get('backdrop_path', ''),
                'vote_average': movie.get('vote_average', 0),
                'vote_count': movie.get('vote_count', 0),
                'popularity': movie.get('popularity', 0),
            })
        return formatted
