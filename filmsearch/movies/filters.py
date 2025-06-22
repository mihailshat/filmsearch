from datetime import timedelta, timezone
import django_filters
from django.db.models import Q, QuerySet, Avg, Count
from typing import Any, Optional
from .models import MovieTVShow, Review, Rating, Genre, ActorDirector, MovieTVShowActorDirector

class MovieTVShowFilter(django_filters.FilterSet):
    """
    Фильтр для фильмов и сериалов.
    
    Предоставляет комплексную фильтрацию по различным параметрам:
    - Текстовый поиск (название, описание, жанры, страна)
    - Временные фильтры (год выпуска, новинки)
    - Рейтинговые фильтры (минимальный рейтинг, количество отзывов)
    - Тип и статус контента
    - Участники (актеры, режиссеры)
    - Продолжительность
    """
    title = django_filters.CharFilter(label='Название содержит', lookup_expr='icontains')
    description = django_filters.CharFilter(label='Описание содержит', lookup_expr='icontains')
    genres = django_filters.CharFilter(label='Жанры Название содержит', field_name='genres__name', lookup_expr='icontains')
    country = django_filters.CharFilter(label='Страна содержит', lookup_expr='icontains')
    year = django_filters.NumberFilter(label='Год выпуска', field_name='release_date__year')
    min_rating = django_filters.NumberFilter(label='Минимальный рейтинг', method='filter_min_rating')
    type = django_filters.ChoiceFilter(label='Тип', choices=MovieTVShow.TYPE_CHOICES)
    status = django_filters.ChoiceFilter(label='Статус', choices=MovieTVShow.STATUS_CHOICES)
    director = django_filters.CharFilter(label='Режиссер содержит', field_name='director__full_name', lookup_expr='icontains')
    actors = django_filters.CharFilter(label='Актеры содержат', field_name='actors__full_name', lookup_expr='icontains')
    is_new = django_filters.BooleanFilter(label='Новинки', method='filter_is_new')
    has_reviews = django_filters.BooleanFilter(label='Есть отзывы', method='filter_has_reviews')
    min_reviews = django_filters.NumberFilter(label='Минимум отзывов', method='filter_min_reviews')
    min_duration = django_filters.NumberFilter(label='Продолжительность от (мин)', field_name='duration', lookup_expr='gte')
    max_duration = django_filters.NumberFilter(label='Продолжительность до (мин)', field_name='duration', lookup_expr='lte')

    class Meta:
        model = MovieTVShow
        fields = [
            'title', 'description', 'type', 'status', 'genres', 'country', 'year', 'director', 'actors',
            'min_rating', 'is_new', 'has_reviews', 'min_reviews', 'min_duration', 'max_duration'
        ]

    def filter_min_rating(self, queryset: QuerySet, name: str, value: Any) -> QuerySet:
        """
        Фильтрация по минимальному рейтингу.
        
        Args:
            queryset: Исходный queryset
            name: Имя поля фильтра
            value: Значение минимального рейтинга
            
        Returns:
            QuerySet: Отфильтрованный queryset
        """
        return queryset.annotate(
            avg_rating=Avg('ratings__rating_value')
        ).filter(avg_rating__gte=value)

    def filter_is_new(self, queryset: QuerySet, name: str, value: bool) -> QuerySet:
        """
        Фильтрация новинок (за последние 30 дней).
        
        Args:
            queryset: Исходный queryset
            name: Имя поля фильтра
            value: True для новинок, False для всех
            
        Returns:
            QuerySet: Отфильтрованный queryset
        """
        if value:
            return queryset.filter(
                release_date__gte=timezone.now() - timedelta(days=30)
            )
        return queryset

    def filter_has_reviews(self, queryset: QuerySet, name: str, value: bool) -> QuerySet:
        """
        Фильтрация по наличию отзывов.
        
        Args:
            queryset: Исходный queryset
            name: Имя поля фильтра
            value: True для фильмов с отзывами, False для фильмов без отзывов
            
        Returns:
            QuerySet: Отфильтрованный queryset
        """
        if value:
            return queryset.filter(reviews__isnull=False).distinct()
        return queryset.filter(reviews__isnull=True).distinct()

    def filter_min_reviews(self, queryset: QuerySet, name: str, value: int) -> QuerySet:
        """
        Фильтрация по минимальному количеству отзывов.
        
        Args:
            queryset: Исходный queryset
            name: Имя поля фильтра
            value: Минимальное количество отзывов
            
        Returns:
            QuerySet: Отфильтрованный queryset
        """
        return queryset.annotate(
            review_count=Count('reviews')
        ).filter(review_count__gte=value)

class ReviewFilter(django_filters.FilterSet):
    """
    Фильтр для отзывов.
    
    Предоставляет фильтрацию по:
    - Фильму/сериалу
    - Пользователю
    - Содержанию отзыва
    - Количеству лайков
    - Дате создания
    - Рейтингу
    - Статусу модерации
    """
    movie = django_filters.CharFilter(label='Фильм содержит', field_name='movie_tvshow__title', lookup_expr='icontains')
    user = django_filters.CharFilter(label='Пользователь содержит', field_name='user__username', lookup_expr='icontains')
    content = django_filters.CharFilter(label='Текст отзыва содержит', lookup_expr='icontains')
    min_likes = django_filters.NumberFilter(label='Минимум лайков', method='filter_min_likes')
    date_from = django_filters.DateFilter(label='Дата создания от', field_name='created_at', lookup_expr='gte')
    date_to = django_filters.DateFilter(label='Дата создания до', field_name='created_at', lookup_expr='lte')
    min_rating = django_filters.NumberFilter(label='Рейтинг в отзыве от', field_name='rating__rating_value', lookup_expr='gte')
    moderation_status = django_filters.ChoiceFilter(label='Статус модерации', choices=Review.MODERATION_STATUS_CHOICES)

    class Meta:
        model = Review
        fields = ['movie', 'user', 'content', 'min_likes', 'date_from', 'date_to', 'min_rating', 'moderation_status']

    def filter_min_likes(self, queryset: QuerySet, name: str, value: int) -> QuerySet:
        """
        Фильтрация по минимальному количеству лайков.
        
        Args:
            queryset: Исходный queryset
            name: Имя поля фильтра
            value: Минимальное количество лайков
            
        Returns:
            QuerySet: Отфильтрованный queryset
        """
        return queryset.annotate(
            likes_count=Count('votes', filter=Q(votes__vote_type='like'))
        ).filter(likes_count__gte=value)

class RatingFilter(django_filters.FilterSet):
    """
    Фильтр для рейтингов.
    
    Предоставляет фильтрацию по:
    - Фильму/сериалу
    - Пользователю
    - Значению рейтинга (мин/макс)
    - Дате создания
    - Наличию отзыва
    """
    movie = django_filters.CharFilter(label='Фильм содержит', field_name='movie_tvshow__title', lookup_expr='icontains')
    user = django_filters.CharFilter(label='Пользователь содержит', field_name='user__username', lookup_expr='icontains')
    min_rating = django_filters.NumberFilter(label='Рейтинг от', field_name='rating_value', lookup_expr='gte')
    max_rating = django_filters.NumberFilter(label='Рейтинг до', field_name='rating_value', lookup_expr='lte')
    date_from = django_filters.DateFilter(label='Дата оценки от', field_name='created_at', lookup_expr='gte')
    date_to = django_filters.DateFilter(label='Дата оценки до', field_name='created_at', lookup_expr='lte')
    has_review = django_filters.BooleanFilter(label='Есть связанный отзыв', method='filter_has_review')

    class Meta:
        model = Rating
        fields = ['movie', 'user', 'min_rating', 'max_rating', 'date_from', 'date_to', 'has_review']

    def filter_has_review(self, queryset: QuerySet, name: str, value: bool) -> QuerySet:
        """
        Фильтрация по наличию отзыва к рейтингу.
        
        Args:
            queryset: Исходный queryset
            name: Имя поля фильтра
            value: True для рейтингов с отзывами, False для рейтингов без отзывов
            
        Returns:
            QuerySet: Отфильтрованный queryset
        """
        if value:
            return queryset.filter(review__isnull=False)
        return queryset.filter(review__isnull=True)

class GenreFilter(django_filters.FilterSet):
    """
    Фильтр для жанров.
    
    Предоставляет фильтрацию по:
    - Названию жанра
    - Минимальному количеству фильмов
    - Наличию фильмов
    - Типу контента (фильм/сериал)
    """
    name = django_filters.CharFilter(label='Название содержит', lookup_expr='icontains')
    min_movies = django_filters.NumberFilter(label='Минимум фильмов в жанре', method='filter_min_movies')
    has_movies = django_filters.BooleanFilter(label='Есть фильмы', method='filter_has_movies')
    movie_type = django_filters.ChoiceFilter(
        label='Тип контента',
        field_name='movies__type',
        choices=MovieTVShow.TYPE_CHOICES
    )

    class Meta:
        model = Genre
        fields = ['name', 'min_movies', 'has_movies', 'movie_type']

    def filter_min_movies(self, queryset: QuerySet, name: str, value: int) -> QuerySet:
        """
        Фильтрация по минимальному количеству фильмов в жанре.
        
        Args:
            queryset: Исходный queryset
            name: Имя поля фильтра
            value: Минимальное количество фильмов
            
        Returns:
            QuerySet: Отфильтрованный queryset
        """
        return queryset.annotate(
            movies_count=Count('movies')
        ).filter(movies_count__gte=value)

    def filter_has_movies(self, queryset: QuerySet, name: str, value: bool) -> QuerySet:
        """
        Фильтрация по наличию фильмов в жанре.
        
        Args:
            queryset: Исходный queryset
            name: Имя поля фильтра
            value: True для жанров с фильмами, False для пустых жанров
            
        Returns:
            QuerySet: Отфильтрованный queryset
        """
        if value:
            return queryset.filter(movies__isnull=False).distinct()
        return queryset.filter(movies__isnull=True).distinct()

class ActorDirectorFilter(django_filters.FilterSet):
    """
    Фильтр для актеров и режиссеров.
    
    Предоставляет фильтрацию по:
    - Имени
    - Роли (актер/режиссер)
    - Минимальному количеству фильмов
    - Типу контента
    - Жанру фильмов
    - Специфическим ролям (только актеры/только режиссеры)
    """
    name = django_filters.CharFilter(label='Имя содержит', field_name='full_name', lookup_expr='icontains')
    role = django_filters.ChoiceFilter(label='Роль в фильме', choices=MovieTVShowActorDirector.ROLE_CHOICES)
    min_movies = django_filters.NumberFilter(label='Минимум фильмов', method='filter_min_movies')
    movie_type = django_filters.ChoiceFilter(
        label='Тип контента',
        field_name='movies__type',
        choices=MovieTVShow.TYPE_CHOICES
    )
    movie_genre = django_filters.CharFilter(
        label='Жанр фильма содержит',
        field_name='movies__genres__name',
        lookup_expr='icontains'
    )
    is_actor = django_filters.BooleanFilter(label='Является актером', method='filter_is_actor')
    is_director = django_filters.BooleanFilter(label='Является режиссером', method='filter_is_director')

    class Meta:
        model = ActorDirector
        fields = ['name', 'role', 'min_movies', 'movie_type', 'movie_genre', 'is_actor', 'is_director']

    def filter_min_movies(self, queryset: QuerySet, name: str, value: int) -> QuerySet:
        """
        Фильтрация по минимальному количеству фильмов у актера/режиссера.
        
        Args:
            queryset: Исходный queryset
            name: Имя поля фильтра
            value: Минимальное количество фильмов
            
        Returns:
            QuerySet: Отфильтрованный queryset
        """
        return queryset.annotate(
            movies_count=Count('movies')
        ).filter(movies_count__gte=value)

    def filter_is_actor(self, queryset: QuerySet, name: str, value: bool) -> QuerySet:
        """
        Фильтрация только актеров.
        
        Args:
            queryset: Исходный queryset
            name: Имя поля фильтра
            value: True для актеров, False для исключения актеров
            
        Returns:
            QuerySet: Отфильтрованный queryset
        """
        if value:
            return queryset.filter(role='actor')
        return queryset.exclude(role='actor')

    def filter_is_director(self, queryset: QuerySet, name: str, value: bool) -> QuerySet:
        """
        Фильтрация только режиссеров.
        
        Args:
            queryset: Исходный queryset
            name: Имя поля фильтра
            value: True для режиссеров, False для исключения режиссеров
            
        Returns:
            QuerySet: Отфильтрованный queryset
        """
        if value:
            return queryset.filter(role='director')
        return queryset.exclude(role='director') 