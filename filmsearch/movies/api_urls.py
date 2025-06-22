"""
URL конфигурация для API приложения movies.

Определяет REST API маршруты для всех функций приложения, включая:
- Главная страница и поиск
- Авторизация и профиль пользователя
- Подборки фильмов
- Административные функции
- CRUD операции для всех моделей
- Статистика и рекомендации
"""

from django.urls import path
from typing import List
from django.urls.resolvers import URLPattern
from . import api_views
from .api_views import (
    MovieTVShowListAPIView, MovieTVShowDetailAPIView,
    GenreListAPIView, ActorDirectorListAPIView,
    ReviewListAPIView, RecommendationListAPIView, RatingListAPIView,
    movie_statistics_api, search_movies_api
)
from .auth_api import register_api, login_api, logout_api, profile_api, collections_api, admin_dashboard_api, generate_recommendations_api, moderate_review_api, pending_reviews_api
from .homepage_api import homepage_data, search_movies, movie_detail_api

# Список URL паттернов для API приложения movies
urlpatterns: List[URLPattern] = [
    # === КОРНЕВОЙ ЭНДПОИНТ API ===
    path('', api_views.api_root, name='api-root'),

    # === ГЛАВНАЯ СТРАНИЦА И ПОИСК ===
    # Данные для главной страницы (для React)
    path('homepage/', homepage_data, name='api_homepage'),
    # Поиск фильмов (упрощенный)
    path('search/', search_movies, name='api_search_movies'),
    # Детальная информация о фильме (упрощенная)
    path('movie/<int:movie_id>/', movie_detail_api, name='api_movie_detail_simple'),
    
    # === АВТОРИЗАЦИЯ И ПРОФИЛЬ ===
    # Регистрация пользователя
    path('auth/register/', register_api, name='api_register'),
    # Вход в систему
    path('auth/login/', login_api, name='api_login'),
    # Выход из системы
    path('auth/logout/', logout_api, name='api_logout'),
    # Профиль пользователя
    path('auth/profile/', profile_api, name='api_profile'),
    
    # === ПОДБОРКИ ===
    # Управление подборками (GET/POST)
    path('collections/', collections_api, name='api_collections'),
    
    # === АДМИНИСТРАТИВНЫЕ ФУНКЦИИ ===
    # Админ-панель с статистикой
    path('admin/dashboard/', admin_dashboard_api, name='api_admin_dashboard'),
    # Генерация рекомендаций
    path('admin/generate-recommendations/', generate_recommendations_api, name='api_generate_recommendations'),
    # Модерация отзывов
    path('admin/moderate-review/<int:review_id>/', moderate_review_api, name='api_moderate_review'),
    # Список отзывов на модерации
    path('admin/pending-reviews/', pending_reviews_api, name='api_pending_reviews'),
    
    # === ФИЛЬМЫ И СЕРИАЛЫ ===
    # Список фильмов/сериалов (с фильтрацией)
    path('movies/', MovieTVShowListAPIView.as_view(), name='api_movie_list'),
    # Детальная информация о фильме/сериале
    path('movies/<int:pk>/', MovieTVShowDetailAPIView.as_view(), name='api_movie_detail'),
    # Поиск фильмов (расширенный)
    path('movies/search/', search_movies_api, name='api_movie_search'),
    # Статистика фильмов
    path('movies/statistics/', movie_statistics_api, name='api_movie_statistics'),
    
    # === ПОИСК И СТАТИСТИКА ===
    # Поиск фильмов (альтернативный маршрут)
    path('search/', search_movies_api, name='api_search'),
    # Статистика (альтернативный маршрут)
    path('statistics/', movie_statistics_api, name='api_statistics'),
    
    # === ЖАНРЫ ===
    # Список жанров
    path('genres/', GenreListAPIView.as_view(), name='api_genre_list'),
    
    # === АКТЕРЫ И РЕЖИССЕРЫ ===
    # Список актеров и режиссеров
    path('actors/', ActorDirectorListAPIView.as_view(), name='api_actor_list'),
    
    # === ОТЗЫВЫ ===
    # Список отзывов
    path('reviews/', ReviewListAPIView.as_view(), name='api_review_list'),
    
    # === РЕЙТИНГИ ===
    # Список рейтингов
    path('ratings/', RatingListAPIView.as_view(), name='api_rating_list'),
    
    # === РЕКОМЕНДАЦИИ ===
    # Персональные рекомендации
    path('recommendations/', RecommendationListAPIView.as_view(), name='api_recommendation_list'),
] 