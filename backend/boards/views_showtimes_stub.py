import datetime
import urllib.parse
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView


class ShowtimesView(APIView):
    """
    Best-effort showtimes fetcher (placeholder).
    Replace _mock_showtimes with real crawling logic per brand.
    """

    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def get(self, request):
        title = request.query_params.get('title') or ''
        brand = request.query_params.get('brand') or ''
        place_url = request.query_params.get('place_url') or ''
        today = datetime.date.today().strftime('%Y-%m-%d')

        brand_key = self._detect_brand(title, brand, place_url)
        movies = self._mock_movies_with_showtimes(brand_key, title, today)
        booking_url = self._booking_url(brand_key, place_url or title)

        return Response({
            'title': title,
            'brand': brand_key,
            'date': today,
            'movies': movies,
            'booking_url': booking_url,
            'note': '현재는 크롤링 대체용 임시 데이터입니다. 실제 소스 연결 필요.',
        })

    def _detect_brand(self, title: str, brand: str, place_url: str) -> str:
        text = f'{title} {brand} {place_url}'.lower()
        if 'cgv' in text:
            return 'CGV'
        if '롯데' in text or 'lotte' in text:
            return '롯데시네마'
        if '메가박스' in text or 'megabox' in text:
            return '메가박스'
        return brand or '기타'

    def _booking_url(self, brand: str, place_url: str) -> str:
        """
        Simplified brand booking link.
        - 롯데시네마: https://www.lottecinema.co.kr/NLCHS/Ticketing
        - CGV: https://cgv.co.kr/cnm/movieBook
        - 메가박스: 기본 예약 페이지
        - 그 외: place_url이나 빈 값
        """
        brand_roots = {
            'CGV': 'https://cgv.co.kr/cnm/movieBook',
            '롯데시네마': 'https://www.lottecinema.co.kr/NLCHS/Ticketing',
            '메가박스': 'https://www.megabox.co.kr/booking',
        }
        if brand in brand_roots:
            return brand_roots[brand]
        return place_url or ''

    def _mock_movies_with_showtimes(self, brand: str, title: str, date: str):
        # Create 3 fake movies; if a theater title is given, prepend it.
        movie_titles = [f'{title} 특별 상영', '듄: 파트2', '시민덕희', '위키드'][:3]
        base_times = ['10:00', '13:10', '16:20', '19:30', '22:00']
        halls = {
            'CGV': ['1관(레이저)', '2관', '3관(IMAX)'],
            '롯데시네마': ['1관(Super)', '2관', '3관'],
            '메가박스': ['MX관', '컴포트관', '일반관'],
            '기타': ['상영관 A', '상영관 B'],
        }
        chosen_halls = halls.get(brand, halls['기타'])

        movies = []
        for movie_idx, m_title in enumerate(movie_titles):
            show_list = []
            for idx, t in enumerate(base_times):
                show_list.append({
                    'time': t,
                    'hall': chosen_halls[(movie_idx + idx) % len(chosen_halls)],
                    'date': date,
                })
            movies.append({'title': m_title, 'showtimes': show_list})
        return movies
