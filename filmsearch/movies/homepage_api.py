from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.request import Request
from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import timedelta
from typing import Any, Dict, List, Optional
from .models import MovieTVShow, Genre, Review
from .serializers import MovieTVShowSerializer, GenreSerializer


@api_view(['GET'])
def homepage_data(request: Request) -> Response:
    """
    API endpoint для получения всех данных главной страницы.
    
    Возвращает данные для всех 3 виджетов одним запросом:
    - Топ фильмов по рейтингу
    - Популярные жанры
    - Новинки (последние 30 дней)
    
    Args:
        request: DRF Request объект
        
    Returns:
        Response: JSON с данными для главной страницы
    """
    
    # 1. Топ фильмов по рейтингу (черещ AVG)
    top_movies = MovieTVShow.objects.annotate(
        avg_rating=Avg('ratings__rating_value'),
        ratings_count=Count('ratings')
    ).filter(ratings_count__gt=0).order_by('-avg_rating')[:8]
    
    # 2. Популярные жанры (через COUNT)
    popular_genres = Genre.objects.annotate(
        movies_count=Count('movies'),
        avg_rating=Avg('movies__ratings__rating_value')
    ).filter(movies_count__gt=0).order_by('-movies_count')[:6]
    
    # 3. Новинки (последние 30 дней)
    thirty_days_ago = timezone.now().date() - timedelta(days=30)
    new_releases = MovieTVShow.objects.filter(
        release_date__gte=thirty_days_ago
    ).order_by('-release_date')[:6]
    
    # Если новинок мало, добавляем просто последние фильмы
    if new_releases.count() < 4:
        new_releases = MovieTVShow.objects.all().order_by('-release_date')[:6]
    
    # Сериализация данных
    top_movies_data: List[Dict[str, Any]] = []
    for movie in top_movies:
        movie_data = {
            'id': movie.id,
            'title': movie.title,
            'title_english': movie.title_english if hasattr(movie, 'title_english') else None,
            'poster_url': movie.poster_url,
            'poster_image': movie.poster_image.url if movie.poster_image else None,
            'release_date': movie.release_date.isoformat(),
            'type': movie.type,
            'duration': movie.duration,
            'seasons_count': movie.seasons_count,
            'country': movie.country,
            'avg_rating': round(movie.avg_rating, 1) if movie.avg_rating else None,
            'ratings_count': movie.ratings_count,
            'genres': [{'id': g.id, 'name': g.name} for g in movie.genres.all()]
        }
        top_movies_data.append(movie_data)
    
    popular_genres_data: List[Dict[str, Any]] = []
    for genre in popular_genres:
        # Получаем примеры фильмов этого жанра
        example_movies = genre.movies.all()[:4]
        genre_data = {
            'id': genre.id,
            'name': genre.name,
            'movies_count': genre.movies_count,
            'avg_rating': round(genre.avg_rating, 1) if genre.avg_rating else None,
            'example_movies': [
                {
                    'id': m.id,
                    'title': m.title,
                    'poster_url': m.poster_url,
                    'poster_image': m.poster_image.url if m.poster_image else None
                } for m in example_movies
            ]
        }
        popular_genres_data.append(genre_data)
    
    new_releases_data: List[Dict[str, Any]] = []
    for movie in new_releases:
        # Вычисляем is_new_release
        days_since_release = (timezone.now().date() - movie.release_date).days
        is_new_release = days_since_release <= 30
        
        movie_data = {
            'id': movie.id,
            'title': movie.title,
            'title_english': movie.title_english if hasattr(movie, 'title_english') else None,
            'poster_url': movie.poster_url,
            'poster_image': movie.poster_image.url if movie.poster_image else None,
            'release_date': movie.release_date.isoformat(),
            'type': movie.type,
            'duration': movie.duration,
            'seasons_count': movie.seasons_count,
            'country': movie.country,
            'is_new_release': is_new_release,
            'genres': [{'id': g.id, 'name': g.name} for g in movie.genres.all()]
        }
        new_releases_data.append(movie_data)
    
    return Response({
        'top_movies': top_movies_data,
        'popular_genres': popular_genres_data,
        'new_releases': new_releases_data
    })


@api_view(['GET'])
def search_movies(request: Request) -> Response:
    """
    API endpoint для поиска фильмов.
    
    Поддерживает поиск по названию, описанию, жанрам.
    Возвращает ограниченный список результатов (до 20 фильмов).
    
    Args:
        request: DRF Request объект
        
    Returns:
        Response: JSON с результатами поиска
    """
    query = request.GET.get('q', '').strip()
    
    if not query:
        return Response({'movies': [], 'total_count': 0})
    
    movies = MovieTVShow.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query) |
        Q(genres__name__icontains=query)
    ).distinct().order_by('-release_date')
    
    # Ограничиваем результаты
    movies = movies[:20]
    
    results: List[Dict[str, Any]] = []
    for movie in movies:
        movie_data = {
            'id': movie.id,
            'title': movie.title,
            'title_english': movie.title_english if hasattr(movie, 'title_english') else None,
            'description': movie.description[:150] + '...' if len(movie.description) > 150 else movie.description,
            'poster_url': movie.poster_url,
            'poster_image': movie.poster_image.url if movie.poster_image else None,
            'release_date': movie.release_date.isoformat(),
            'type': movie.type,
            'country': movie.country,
            'genres': [{'id': g.id, 'name': g.name} for g in movie.genres.all()]
        }
        results.append(movie_data)
    
    return Response({
        'movies': results,
        'total_count': len(results),
        'query': query
    })


@api_view(['GET'])
def movie_detail_api(request: Request, movie_id: int) -> Response:
    """
    API endpoint для получения детальной информации о фильме.
    
    Возвращает полную информацию о фильме включая:
    - Основные данные фильма
    - Средний рейтинг и количество оценок
    - Последние одобренные отзывы
    - Жанры
    
    Args:
        request: DRF Request объект
        movie_id: int — ID фильма
        
    Returns:
        Response: JSON с детальной информацией о фильме или ошибка 404
    """
    try:
        movie = MovieTVShow.objects.get(id=movie_id)
        
        # Получаем рейтинг
        avg_rating = movie.ratings.aggregate(avg=Avg('rating_value'))['avg']
        ratings_count = movie.ratings.count()
        
        # Получаем отзывы
        reviews = movie.reviews.filter(moderation_status='approved').order_by('-created_at')[:5]
        reviews_data: List[Dict[str, Any]] = []
        for review in reviews:
            reviews_data.append({
                'id': review.id,
                'user': review.user.username,
                'text': review.review_text[:200] + '...' if len(review.review_text) > 200 else review.review_text,
                'created_at': review.created_at.isoformat(),
                'likes_count': review.likes_count,
                'dislikes_count': review.dislikes_count
            })
        
        movie_data = {
            'id': movie.id,
            'title': movie.title,
            'title_english': movie.title_english if hasattr(movie, 'title_english') else None,
            'description': movie.description,
            'poster_url': movie.poster_url,
            'poster_image': movie.poster_image.url if movie.poster_image else None,
            'release_date': movie.release_date.isoformat(),
            'type': movie.type,
            'duration': movie.duration,
            'seasons_count': movie.seasons_count,
            'episodes_count': movie.episodes_count,
            'country': movie.country,
            'status': movie.status,
            'age_restriction': movie.age_restriction,
            'avg_rating': round(avg_rating, 1) if avg_rating else None,
            'ratings_count': ratings_count,
            'genres': [{'id': g.id, 'name': g.name} for g in movie.genres.all()],
            'reviews': reviews_data,
            'reviews_count': movie.reviews.count()
        }
        
        return Response(movie_data)
        
    except MovieTVShow.DoesNotExist:
        return Response({'error': 'Movie not found'}, status=404) 