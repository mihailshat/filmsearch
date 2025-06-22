from rest_framework import generics, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Avg, Count, Q
from django.utils import timezone
from datetime import timedelta
from .models import MovieTVShow, Genre, ActorDirector, Review, Rating, Recommendation
from .serializers import (
    MovieTVShowSerializer, MovieTVShowListSerializer, MovieTVShowCreateSerializer, GenreSerializer,
    ActorDirectorSerializer, ReviewSerializer, RatingSerializer, RecommendationSerializer
)
from .filters import (
    MovieTVShowFilter, ReviewFilter, RatingFilter,
    GenreFilter, ActorDirectorFilter
)


class MovieTVShowListAPIView(generics.ListCreateAPIView):
    """API для списка фильмов/сериалов с фильтрацией и поиском"""
    queryset = MovieTVShow.objects.all()
    serializer_class = MovieTVShowSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MovieTVShowFilter
    search_fields = ['title', 'description']
    ordering_fields = ['release_date', 'title', 'created_at']
    ordering = ['-release_date']
    
    def get_serializer_class(self):
        """Возвращает разные сериализаторы для разных действий"""
        if self.request.method == 'POST':
            return MovieTVShowCreateSerializer
        return MovieTVShowListSerializer
    
    def get_queryset(self):
        """Оптимизированный queryset с аннотациями"""
        queryset = MovieTVShow.objects.prefetch_related(
            'genres',
            'reviews',
            'ratings'
        ).annotate(
            avg_rating=Avg('ratings__rating_value'),
            review_count=Count('reviews'),
            rating_count=Count('ratings')
        )

        # Фильтрация по году
        year = self.request.query_params.get('year')
        if year:
            queryset = queryset.filter(release_date__year=year)

        # Фильтрация по минимальному рейтингу
        min_rating = self.request.query_params.get('min_rating')
        if min_rating:
            queryset = queryset.filter(ratings__rating_value__gte=min_rating)

        return queryset
    
    def get_serializer_context(self):
        """Передача контекста с выделенными фильмами"""
        context = super().get_serializer_context()
        highlighted_movies = [1, 3, 5, 7] 
        context['highlighted_movies'] = highlighted_movies
        
        return context


class MovieTVShowDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """API для детального просмотра фильма/сериала"""
    queryset = MovieTVShow.objects.all()
    serializer_class = MovieTVShowSerializer
    
    def get_queryset(self):
        """Оптимизированный queryset для детального просмотра"""
        return MovieTVShow.objects.select_related().prefetch_related(
            'genres', 'reviews__user', 'ratings'
        ).annotate(
            avg_rating=Avg('ratings__rating_value'),
            reviews_count=Count('reviews'),
            ratings_count=Count('ratings')
        )
    
    def get_serializer_context(self):
        """Передача контекста"""
        context = super().get_serializer_context()
        highlighted_movies = [1, 3, 5, 7]
        context['highlighted_movies'] = highlighted_movies
        return context


class GenreListAPIView(generics.ListCreateAPIView):
    """API для списка жанров"""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = GenreFilter
    search_fields = ['name']
    
    def get_queryset(self):
        return Genre.objects.annotate(
            movies_count=Count('movies')
        ).order_by('name')


class ActorDirectorListAPIView(generics.ListCreateAPIView):
    """API для списка актеров/режиссеров"""
    queryset = ActorDirector.objects.all()
    serializer_class = ActorDirectorSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ActorDirectorFilter
    search_fields = ['full_name', 'biography']
    ordering_fields = ['full_name', 'birth_date']
    ordering = ['full_name']
    
    def get_queryset(self):
        return ActorDirector.objects.annotate(
            movies_count=Count('movies')
        )


class ReviewListAPIView(generics.ListCreateAPIView):
    """API для списка отзывов"""
    serializer_class = ReviewSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = ReviewFilter
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Queryset с предзагрузкой связанных объектов"""
        return Review.objects.select_related(
            'user', 'movie_tvshow'
        ).prefetch_related('votes')
    
    def perform_create(self, serializer):
        """Автоматически устанавливаем пользователя при создании отзыва"""
        # Для демонстрации используем первого пользователя, если не авторизован
        from django.contrib.auth.models import User
        user = self.request.user if self.request.user.is_authenticated else User.objects.first()
        serializer.save(user=user)


class RecommendationListAPIView(generics.ListAPIView):
    """API для списка рекомендаций пользователя"""
    serializer_class = RecommendationSerializer
    
    def get_queryset(self):
        """Рекомендации для текущего пользователя"""
        if self.request.user.is_authenticated:
            recommendations = Recommendation.objects.filter(
                user=self.request.user
            ).select_related('movie_tvshow').prefetch_related(
                'movie_tvshow__genres'
            ).order_by('-created_at')
            
            # Если рекомендаций нет, создаем демо-рекомендации
            if not recommendations.exists():
                from django.contrib.auth.models import User
                user = self.request.user
                
                # Берем топ-рейтинговые фильмы как рекомендации
                top_movies = MovieTVShow.objects.annotate(
                    avg_rating=Avg('ratings__rating_value'),
                    ratings_count=Count('ratings')
                ).filter(ratings_count__gte=3).order_by('-avg_rating')[:5]
                
                for movie in top_movies:
                    Recommendation.objects.get_or_create(
                        user=user,
                        movie_tvshow=movie,
                        defaults={
                            'reason_code': f'high_rating_{movie.avg_rating:.1f}' if hasattr(movie, 'avg_rating') else 'high_rating'
                        }
                    )
                
                # Обновляем queryset
                recommendations = Recommendation.objects.filter(
                    user=self.request.user
                ).select_related('movie_tvshow').prefetch_related(
                    'movie_tvshow__genres'
                ).order_by('-created_at')
            
            return recommendations
        return Recommendation.objects.none()


class RatingListAPIView(generics.ListCreateAPIView):
    """API для списка рейтингов"""
    serializer_class = RatingSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = RatingFilter
    ordering_fields = ['created_at', 'rating_value']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Queryset с предзагрузкой связанных объектов"""
        return Rating.objects.select_related(
            'user', 'movie_tvshow'
        )
    
    def perform_create(self, serializer):
        """Автоматически устанавливаем пользователя при создании рейтинга"""
        from django.contrib.auth.models import User
        user = self.request.user if self.request.user.is_authenticated else User.objects.first()
        
        # Проверяем, есть ли уже рейтинг от этого пользователя для этого фильма
        movie_tvshow = serializer.validated_data['movie_tvshow']
        existing_rating = Rating.objects.filter(user=user, movie_tvshow=movie_tvshow).first()
        
        if existing_rating:
            # Обновляем существующий рейтинг
            existing_rating.rating_value = serializer.validated_data['rating_value']
            existing_rating.save()
            # Возвращаем обновленный объект
            serializer.instance = existing_rating
        else:
            # Создаем новый рейтинг
            serializer.save(user=user)


@api_view(['GET'])
def movie_statistics_api(request):
    """API для статистики фильмов"""
    
    # Общая статистика
    total_movies = MovieTVShow.objects.filter(type='movie').count()
    total_tv_shows = MovieTVShow.objects.filter(type='tv_show').count()
    total_genres = Genre.objects.count()
    total_actors = ActorDirector.objects.count()
    
    # Топ-рейтинговые фильмы с аннотациями
    top_rated = MovieTVShow.objects.annotate(
        avg_rating=Avg('ratings__rating_value'),
        ratings_count=Count('ratings')
    ).filter(ratings_count__gte=3).order_by('-avg_rating')[:10]
    
    # Самые обсуждаемые фильмы
    most_reviewed = MovieTVShow.objects.annotate(
        reviews_count=Count('reviews')
    ).order_by('-reviews_count')[:10]
    
    # Новинки (за последние 30 дней)
    from datetime import timedelta
    
    new_releases = MovieTVShow.objects.filter(
        release_date__gte=timezone.now().date() - timedelta(days=30)
    ).order_by('-release_date')[:10]
    
    # Сериализация данных
    top_rated_data = MovieTVShowListSerializer(
        top_rated, 
        many=True, 
        context={'highlighted_movies': [1, 3, 5]}
    ).data
    
    most_reviewed_data = MovieTVShowListSerializer(
        most_reviewed, 
        many=True,
        context={'highlighted_movies': [1, 3, 5]}
    ).data
    
    new_releases_data = MovieTVShowListSerializer(
        new_releases, 
        many=True,
        context={'highlighted_movies': [1, 3, 5]}
    ).data
    
    return Response({
        'statistics': {
            'total_movies': total_movies,
            'total_tv_shows': total_tv_shows,
            'total_genres': total_genres,
            'total_actors': total_actors,
        },
        'top_rated': top_rated_data,
        'most_reviewed': most_reviewed_data,
        'new_releases': new_releases_data,
    })


@api_view(['GET'])
def search_movies_api(request):
    """API для поиска фильмов с расширенными фильтрами"""
    
    # Получаем параметры поиска
    query = request.GET.get('q', '')
    genre_ids = request.GET.getlist('genres')
    type_filter = request.GET.get('type', '')
    year = request.GET.get('year', '')
    min_rating = request.GET.get('min_rating', '')
    
    # Базовый queryset с оптимизацией
    movies = MovieTVShow.objects.select_related().prefetch_related(
        'genres', 'actors_directors'
    ).annotate(
        avg_rating=Avg('ratings__rating_value'),
        reviews_count=Count('reviews'),
        ratings_count=Count('ratings')
    )
    
    # Применяем фильтры
    if query:
        movies = movies.filter(
            Q(title__icontains=query) | 
            Q(description__icontains=query) |
            Q(actors_directors__full_name__icontains=query)
        ).distinct()
    
    if genre_ids:
        movies = movies.filter(genres__id__in=genre_ids).distinct()
    
    if type_filter:
        movies = movies.filter(type=type_filter)
    
    if year:
        movies = movies.filter(release_date__year=year)
    
    if min_rating:
        movies = movies.filter(avg_rating__gte=float(min_rating))
    
    # Сериализация с контекстом
    serializer = MovieTVShowListSerializer(
        movies[:50],  # Ограничиваем результаты
        many=True,
        context={'highlighted_movies': [1, 3, 5, 7]}
    )
    
    return Response({
        'results': serializer.data,
        'count': movies.count(),
        'filters_applied': {
            'query': query,
            'genres': genre_ids,
            'type': type_filter,
            'year': year,
            'min_rating': min_rating,
        }
    }) 