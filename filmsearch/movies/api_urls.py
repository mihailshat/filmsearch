from django.urls import path
from .api_views import (
    MovieTVShowListAPIView, MovieTVShowDetailAPIView,
    GenreListAPIView, ActorDirectorListAPIView,
    ReviewListAPIView, RecommendationListAPIView, RatingListAPIView,
    movie_statistics_api, search_movies_api
)
from .auth_api import register_api, login_api, logout_api, profile_api, collections_api, admin_dashboard_api, generate_recommendations_api, moderate_review_api, pending_reviews_api
from .homepage_api import homepage_data, search_movies, movie_detail_api

urlpatterns = [
    # Главная страница (для React)
    path('homepage/', homepage_data, name='api_homepage'),
    path('search/', search_movies, name='api_search_movies'),
    path('movie/<int:movie_id>/', movie_detail_api, name='api_movie_detail_simple'),
    
    # Авторизация 
    path('auth/register/', register_api, name='api_register'),
    path('auth/login/', login_api, name='api_login'),
    path('auth/logout/', logout_api, name='api_logout'),
    path('auth/profile/', profile_api, name='api_profile'),
    
    # Подборки 
    path('collections/', collections_api, name='api_collections'),
    
    # Админские функции 
    path('admin/dashboard/', admin_dashboard_api, name='api_admin_dashboard'),
    path('admin/generate-recommendations/', generate_recommendations_api, name='api_generate_recommendations'),
    path('admin/moderate-review/<int:review_id>/', moderate_review_api, name='api_moderate_review'),
    path('admin/pending-reviews/', pending_reviews_api, name='api_pending_reviews'),
    
    # Фильмы и сериалы
    path('movies/', MovieTVShowListAPIView.as_view(), name='api_movie_list'),
    path('movies/<int:pk>/', MovieTVShowDetailAPIView.as_view(), name='api_movie_detail'),
    path('movies/search/', search_movies_api, name='api_movie_search'),
    path('movies/statistics/', movie_statistics_api, name='api_movie_statistics'),
    
    # Поиск 
    path('search/', search_movies_api, name='api_search'),
    path('statistics/', movie_statistics_api, name='api_statistics'),
    
    # Жанры
    path('genres/', GenreListAPIView.as_view(), name='api_genre_list'),
    
    # Актеры и режиссеры
    path('actors/', ActorDirectorListAPIView.as_view(), name='api_actor_list'),
    
    # Отзывы
    path('reviews/', ReviewListAPIView.as_view(), name='api_review_list'),
    
    # Рейтинги
    path('ratings/', RatingListAPIView.as_view(), name='api_rating_list'),
    
    # Рекомендации
    path('recommendations/', RecommendationListAPIView.as_view(), name='api_recommendation_list'),
] 