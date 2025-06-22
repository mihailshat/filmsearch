"""
URL конфигурация для приложения movies.

Определяет маршруты для всех страниц приложения, включая:
- Основные страницы (списки фильмов, детали)
- Авторизация и регистрация
- Профиль пользователя
- CRUD операции для администраторов
- Подборки фильмов
- Отзывы и рейтинги
- Рекомендации
- PDF отчеты
"""

from django.urls import path
from django.contrib.auth import views as auth_views
from typing import List
from django.urls.resolvers import URLPattern
from . import views

# Список URL паттернов для приложения movies
urlpatterns: List[URLPattern] = [
    # === ОСНОВНЫЕ СТРАНИЦЫ ===
    # Главная страница со списком фильмов
    path('', views.MovieListView.as_view(), name='movie_list'),
    # Детальная страница фильма/сериала
    path('movie/<int:pk>/', views.MovieDetailView.as_view(), name='movie_detail'),
    # Детальная страница жанра
    path('genre/<int:pk>/', views.GenreDetailView.as_view(), name='genre_detail'),
    # Список всех жанров
    path('genres/', views.GenreListView.as_view(), name='genre_list'),
    # Список актеров и режиссеров
    path('actors/', views.ActorDirectorListView.as_view(), name='actor_list'),
    # Детальная страница актера/режиссера
    path('actor/<int:pk>/', views.ActorDirectorDetailView.as_view(), name='actor_detail'),
    # Результаты поиска
    path('search/', views.MovieListView.as_view(template_name='movies/search_results.html'), name='search_results'),
    
    # === АВТОРИЗАЦИЯ И РЕГИСТРАЦИЯ ===
    # Регистрация нового пользователя
    path('register/', views.register_view, name='register'),
    # Вход в систему
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    # Выход из системы
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # === ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ ===
    # Просмотр профиля пользователя
    path('profile/', views.profile_view, name='profile'),
    # Редактирование профиля
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    # Персональные рекомендации
    path('recommendations/', views.recommendations_view, name='recommendations'),
    
    # === CRUD ДЛЯ АДМИНИСТРАТОРОВ ===
    # Админ-панель
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    # Управление пользователями
    path('manage-users/', views.manage_users, name='manage_users'),
    
    # Управление фильмами/сериалами (только админы)
    # Добавление нового фильма/сериала
    path('movie/add/', views.MovieTVShowCreateView.as_view(), name='movie_add'),
    # Редактирование фильма/сериала
    path('movie/<int:pk>/edit/', views.MovieTVShowUpdateView.as_view(), name='movie_edit'),
    # Удаление фильма/сериала
    path('movie/<int:pk>/delete/', views.MovieTVShowDeleteView.as_view(), name='movie_delete'),
    
    # Управление жанрами (только админы)
    # Добавление нового жанра
    path('genre/add/', views.GenreCreateView.as_view(), name='genre_add'),
    # Редактирование жанра
    path('genre/<int:pk>/edit/', views.GenreUpdateView.as_view(), name='genre_edit'),
    # Удаление жанра
    path('genre/<int:pk>/delete/', views.GenreDeleteView.as_view(), name='genre_delete'),

    # Генерация рекомендаций (только админы)
    path('admin/generate-recommendations/', views.generate_recommendations, name='generate_recommendations'),
    
    # === ПОДБОРКИ (ДЛЯ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ) ===
    # Список подборок
    path('collections/', views.CollectionListView.as_view(), name='collection_list'),
    # Детальная страница подборки
    path('collection/<int:pk>/', views.CollectionDetailView.as_view(), name='collection_detail'),
    # Создание новой подборки
    path('collection/add/', views.CollectionCreateView.as_view(), name='collection_add'),
    # Редактирование подборки
    path('collection/<int:pk>/edit/', views.CollectionUpdateView.as_view(), name='collection_edit'),
    # Удаление подборки
    path('collection/<int:pk>/delete/', views.CollectionDeleteView.as_view(), name='collection_delete'),
    
    # Управление элементами подборок
    # Добавление фильма в подборку
    path('collection/<int:collection_id>/add-movie/<int:movie_id>/', views.add_to_collection, name='add_to_collection'),
    # Удаление фильма из подборки
    path('collection/<int:collection_id>/remove-movie/<int:movie_id>/', views.remove_from_collection, name='remove_from_collection'),
    
    # === ОТЗЫВЫ (ДЛЯ АВТОРИЗОВАННЫХ ПОЛЬЗОВАТЕЛЕЙ) ===
    # Добавление отзыва к фильму
    path('movie/<int:movie_id>/review/add/', views.ReviewCreateView.as_view(), name='review_add'),
    # Редактирование отзыва
    path('review/<int:pk>/edit/', views.ReviewUpdateView.as_view(), name='review_edit'),
    # Удаление отзыва
    path('review/<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='review_delete'),
    
    # === РЕЙТИНГИ ===
    # Добавление оценки фильму
    path('movie/<int:movie_id>/rate/', views.add_rating, name='add_rating'),
    
    # === ДЕМО И СТАТИСТИКА ===
    # Закомментированные маршруты для демо-функций
    # path('demo/', views.demo_page, name='demo_page'),
    # path('statistics/', views.statistics_view, name='statistics'),
    # path('fresh-reviews/', views.fresh_reviews_view, name='fresh_reviews'),
    
    # === РЕКОМЕНДАЦИИ ===
    # Персональные рекомендации (дублирует выше)
    path('recommendations/', views.recommendations_view, name='recommendations'),
    
    # === PDF ОТЧЕТЫ ДЛЯ АДМИНИСТРАТОРОВ ===
    # Генерация PDF отчета по фильму
    path('admin/movie/<int:movie_id>/pdf/', views.admin_movie_pdf, name='admin_movie_pdf'),
] 