import json
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import MovieTVShow, Genre, ActorDirector, Review, Rating, Collection, Recommendation
from datetime import date, timedelta

class ModelTestCase(TestCase):
    """Тесты для моделей """
    @classmethod
    def setUpTestData(cls):
        """Создание тестовых данных один раз для всего класса."""
        cls.user = User.objects.create_user(username='testuser', password='password123')
        cls.genre = Genre.objects.create(name='Тестовый Жанр')
        cls.actor = ActorDirector.objects.create(full_name='Тестовый Актер')
        
        cls.movie = MovieTVShow.objects.create(
            title='Тестовый Фильм',
            description='Описание тестового фильма для проверки функциональности приложения',
            type='movie',
            release_date=date.today() - timedelta(days=30),
            duration=120,
            country='Россия',
            age_restriction='16+',
            poster_url='https://example.com/poster.jpg'
        )
        cls.movie.genres.add(cls.genre)
        cls.movie.actors_directors.add(cls.actor)
        
        cls.review = Review.objects.create(
            movie_tvshow=cls.movie,
            user=cls.user,
            review_text='Отличный фильм! Очень понравился сюжет и актерская игра.'
        )
        
        cls.rating = Rating.objects.create(
            movie_tvshow=cls.movie,
            user=cls.user,
            rating_value=9
        )

    def test_genre_str(self):
        """Тест: строковое представление модели Genre."""
        self.assertEqual(str(self.genre), 'Тестовый Жанр')

    def test_actor_director_str(self):
        """Тест: строковое представление модели ActorDirector."""
        self.assertEqual(str(self.actor), 'Тестовый Актер')

    def test_movie_tv_show_str(self):
        """Тест: строковое представление модели MovieTVShow."""
        self.assertEqual(str(self.movie), 'Тестовый Фильм')
        
    def test_movie_average_rating(self):
        """Тест: вычисление среднего рейтинга."""
        self.assertEqual(self.movie.get_average_rating(), 9.0)

    def test_review_str(self):
        """Тест: строковое представление модели Review."""
        expected_str = f"Отзыв от {self.user.username} на {self.movie.title}"
        self.assertEqual(str(self.review), expected_str)


class APITestCase(TestCase):
    """Тесты для API эндпоинтов."""
    @classmethod
    def setUpTestData(cls):
        """Создание тестовых данных один раз для всего класса."""
        cls.admin_user = User.objects.create_superuser(username='admin', password='password123', email='admin@test.com')
        cls.regular_user = User.objects.create_user(username='user', password='password123', email='user@test.com')
        
        cls.genre = Genre.objects.create(name='Боевик')
        cls.movie = MovieTVShow.objects.create(
            title='Тестовый Боевик',
            description='Захватывающий боевик с динамичными сценами и неожиданными поворотами сюжета',
            type='movie',
            release_date=date(2023, 1, 1),
            duration=110,
            country='США',
            age_restriction='18+',
            poster_url='https://example.com/action-poster.jpg'
        )
        cls.movie.genres.add(cls.genre)
        
        # Создаем отзыв для тестирования модерации
        cls.review = Review.objects.create(
            movie_tvshow=cls.movie,
            user=cls.regular_user,
            review_text='Интересный фильм, но мог бы быть лучше.',
            moderation_status='pending'  # Отзыв на модерации
        )

    def setUp(self):
        """Настройка клиента для каждого теста."""
        self.client = Client()
        self.register_data = {
            'username': 'newuser',
            'password1': 'newpassword123!',
            'password2': 'newpassword123!',
            'email': 'newuser@test.com'
        }
        self.login_data = {'username': 'user', 'password': 'password123'}
        self.admin_login_data = {'username': 'admin', 'password': 'password123'}

    # Тесты публичных API
    def test_homepage_api(self):
        """Тест: доступность API главной страницы."""
        response = self.client.get(reverse('api_homepage'))
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('top_movies', data)
        self.assertIn('popular_genres', data)
        self.assertIn('new_releases', data)

    def test_movie_list_api(self):
        """Тест: получение списка фильмов."""
        response = self.client.get(reverse('api_movie_list'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()[0]['title'], 'Тестовый Боевик')

    def test_movie_detail_api(self):
        """Тест: получение деталей фильма."""
        response = self.client.get(reverse('api_movie_detail', kwargs={'pk': self.movie.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['title'], 'Тестовый Боевик')

    def test_search_api(self):
        """Тест: поиск по API."""
        response = self.client.get(reverse('api_search'), {'q': 'Боевик'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()['movies']) > 0)
        self.assertEqual(response.json()['movies'][0]['title'], 'Тестовый Боевик')

    # Тесты аутентификации
    def test_user_registration_api(self):
        """Тест: регистрация пользователя через API."""
        response = self.client.post(
            reverse('api_register'),
            data=json.dumps(self.register_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200) 
        self.assertTrue(response.json()['success'])
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_user_login_api(self):
        """Тест: вход пользователя через API."""
        response = self.client.post(
            reverse('api_login'),
            data=json.dumps(self.login_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertIn('_auth_user_id', self.client.session)

    # Тесты подборок (основная функция)
    def test_collections_api_get(self):
        """Тест: получение списка подборок."""
        response = self.client.get(reverse('api_collections'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertIn('collections', response.json())

    def test_collections_api_create(self):
        """Тест: создание подборки авторизованным пользователем."""
        self.client.login(username='user', password='password123')
        collection_data = {
            'title': 'Мои любимые фильмы',
            'description': 'Подборка моих любимых фильмов',
            'is_public': True
        }
        response = self.client.post(
            reverse('api_collections'),
            data=json.dumps(collection_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertTrue(Collection.objects.filter(title='Мои любимые фильмы').exists())

    def test_collections_api_unauthorized(self):
        """Тест: создание подборки без авторизации."""
        collection_data = {'title': 'Неавторизованная подборка'}
        response = self.client.post(
            reverse('api_collections'),
            data=json.dumps(collection_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
        self.assertFalse(response.json()['success'])

    # Тесты модерации (бизнес-логика)
    def test_moderate_review_api(self):
        """Тест: модерация отзыва администратором."""
        self.client.login(username='admin', password='password123')
        moderation_data = {
            'action': 'approve',
            'reason': 'Отзыв соответствует правилам'
        }
        response = self.client.post(
            reverse('api_moderate_review', kwargs={'review_id': self.review.pk}),
            data=json.dumps(moderation_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        
        # Проверяем, что статус отзыва изменился
        self.review.refresh_from_db()
        self.assertEqual(self.review.moderation_status, 'approved')

    def test_pending_reviews_api(self):
        """Тест: получение списка отзывов на модерации."""
        self.client.login(username='admin', password='password123')
        response = self.client.get(reverse('api_pending_reviews'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        self.assertIn('pending_reviews', response.json())

    # Тесты профиля пользователя
    def test_profile_api_authenticated(self):
        """Тест: доступ к профилю с аутентификацией."""
        self.client.login(username='user', password='password123')
        response = self.client.get(reverse('api_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['user']['username'], 'user')
