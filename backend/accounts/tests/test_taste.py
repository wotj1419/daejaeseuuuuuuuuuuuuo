from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import User
from accounts.taste import MIN_LIKED_FOR_TASTE, update_user_taste_profile
from movies.embedding_utils import cosine_similarity, normalize_vector
from movies.models import Genre, Movie


class EmbeddingUtilsTests(TestCase):
    def test_normalize_and_cosine(self):
        vec = [3.0, 4.0]
        normed = normalize_vector(vec)
        self.assertAlmostEqual(sum(x * x for x in normed) ** 0.5, 1.0, places=5)

        base = [1.0, 0.0]
        close = [0.9, 0.1]
        far = [0.2, 0.9]
        self.assertGreater(cosine_similarity(base, close), cosine_similarity(base, far))


class TasteApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='u1', password='pw')
        self.other = User.objects.create_user(username='u2', password='pw')
        genre = Genre.objects.create(name='SF')

        base_embeddings = [
          [1.0, 0.0],
          [0.9, 0.1],
          [0.8, 0.2],
          [0.7, 0.3],
          [0.6, 0.4],
        ]
        self.user_movies = []
        for idx, emb in enumerate(base_embeddings, start=1):
            movie = Movie.objects.create(
                tmdb_id=idx,
                title=f'm{idx}',
                original_title=f'm{idx}',
                overview='t',
                embedding=emb,
            )
            movie.genres.add(genre)
            self.user_movies.append(movie)
            self.user.favorite_movies.add(movie)

        for movie in self.user_movies:
            self.other.favorite_movies.add(movie)

        update_user_taste_profile(self.user)
        update_user_taste_profile(self.other)

    def test_taste_endpoint_shape(self):
        self.client.force_login(self.user)
        resp = self.client.get('/api/accounts/me/taste/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('taste_summary', data)
        self.assertEqual(data['liked_movies_count'], len(self.user_movies))
        self.assertTrue(isinstance(data.get('top_genres', []), list))

    def test_similar_users_endpoint(self):
        self.client.force_login(self.user)
        resp = self.client.get('/api/accounts/me/similar-users/?k=5')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn('results', data)
        # At least one similar user (u2) should appear
        results = data.get('results', [])
        self.assertGreater(len(results), 0)
        usernames = [item.get('user', {}).get('username') for item in results]
        self.assertIn(self.other.username, usernames)
        self.assertTrue(all('recommendations' in item for item in results))
        self.assertTrue(all('sample_titles' in item for item in results))
