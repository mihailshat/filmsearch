from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # === ОСНОВНЫЕ СТРАНИЦЫ ===
    path('', views.MovieListView.as_view(), name='movie_list'),
    path('movie/<int:pk>/', views.MovieDetailView.as_view(), name='movie_detail'),
    path('genre/<int:pk>/', views.GenreDetailView.as_view(), name='genre_detail'),
    path('genres/', views.GenreListView.as_view(), name='genre_list'),
    path('actors/', views.ActorDirectorListView.as_view(), name='actor_list'),
    path('actor/<int:pk>/', views.ActorDirectorDetailView.as_view(), name='actor_detail'),
    path('search/', views.MovieListView.as_view(template_name='movies/search_results.html'), name='search_results'),
    
    # === АВТОРИЗАЦИЯ И РЕГИСТРАЦИЯ ===
    path('register/', views.register_view, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    # === ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ ===
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('recommendations/', views.recommendations_view, name='recommendations'),
    
    # === CRUD ДЛЯ АДМИНИСТРАТОРОВ ===
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('manage-users/', views.manage_users, name='manage_users'),
    
    # Управление фильмами/сериалами (только админы)
    path('movie/add/', views.MovieTVShowCreateView.as_view(), name='movie_add'),
    path('movie/<int:pk>/edit/', views.MovieTVShowUpdateView.as_view(), name='movie_edit'),
    path('movie/<int:pk>/delete/', views.MovieTVShowDeleteView.as_view(), name='movie_delete'),
    
    # Управление жанрами (только админы)
    path('genre/add/', views.GenreCreateView.as_view(), name='genre_add'),
    path('genre/<int:pk>/edit/', views.GenreUpdateView.as_view(), name='genre_edit'),
    path('genre/<int:pk>/delete/', views.GenreDeleteView.as_view(), name='genre_delete'),

    # Генерация рекомендаций (только админы)
    path('admin/generate-recommendations/', views.generate_recommendations, name='generate_recommendations'),
    
    # === ПОДБОРКИ (ДЛЯ ВСЕХ ПОЛЬЗОВАТЕЛЕЙ) ===
    path('collections/', views.CollectionListView.as_view(), name='collection_list'),
    path('collection/<int:pk>/', views.CollectionDetailView.as_view(), name='collection_detail'),
    path('collection/add/', views.CollectionCreateView.as_view(), name='collection_add'),
    path('collection/<int:pk>/edit/', views.CollectionUpdateView.as_view(), name='collection_edit'),
    path('collection/<int:pk>/delete/', views.CollectionDeleteView.as_view(), name='collection_delete'),
    
    # Управление элементами подборок
    path('collection/<int:collection_id>/add-movie/<int:movie_id>/', views.add_to_collection, name='add_to_collection'),
    path('collection/<int:collection_id>/remove-movie/<int:movie_id>/', views.remove_from_collection, name='remove_from_collection'),
    
    # === ОТЗЫВЫ (ДЛЯ АВТОРИЗОВАННЫХ ПОЛЬЗОВАТЕЛЕЙ) ===
    path('movie/<int:movie_id>/review/add/', views.ReviewCreateView.as_view(), name='review_add'),
    path('review/<int:pk>/edit/', views.ReviewUpdateView.as_view(), name='review_edit'),
    path('review/<int:pk>/delete/', views.ReviewDeleteView.as_view(), name='review_delete'),
    
    # === РЕЙТИНГИ ===
    path('movie/<int:movie_id>/rate/', views.add_rating, name='add_rating'),
    
    # === ДЕМО И СТАТИСТИКА ===
    # path('demo/', views.demo_page, name='demo_page'),
    # path('statistics/', views.statistics_view, name='statistics'),
    # path('fresh-reviews/', views.fresh_reviews_view, name='fresh_reviews'),
    
    # === РЕКОМЕНДАЦИИ ===
    path('recommendations/', views.recommendations_view, name='recommendations'),
    
    # === PDF ОТЧЕТЫ ДЛЯ АДМИНИСТРАТОРОВ ===
    path('admin/movie/<int:movie_id>/pdf/', views.admin_movie_pdf, name='admin_movie_pdf'),
] 