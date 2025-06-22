from rest_framework import serializers
from django.db.models import Avg, Count
from typing import Any, Dict, Optional, List
from .models import MovieTVShow, Genre, ActorDirector, Review, Rating, Recommendation


class GenreSerializer(serializers.ModelSerializer):
    """
    Сериализатор для жанров.
    
    Предоставляет данные о жанрах с количеством фильмов в каждом жанре.
    """
    movies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Genre
        fields = ['id', 'name', 'description', 'movies_count']
    
    def get_movies_count(self, obj: Genre) -> int:
        """
        Количество фильмов в жанре.
        
        Args:
            obj: Объект жанра
            
        Returns:
            int: Количество фильмов в данном жанре
        """
        return obj.movies.count()


class ActorDirectorSerializer(serializers.ModelSerializer):
    """
    Сериализатор для актеров/режиссеров.
    
    Предоставляет данные об актерах и режиссерах с возрастом и количеством фильмов.
    """
    age = serializers.SerializerMethodField()
    movies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ActorDirector
        fields = ['id', 'full_name', 'birth_date', 'biography', 'photo_url', 'age', 'movies_count']
    
    def get_age(self, obj: ActorDirector) -> Optional[int]:
        """
        Возраст актера/режиссера.
        
        Args:
            obj: Объект актера/режиссера
            
        Returns:
            Optional[int]: Возраст или None, если дата рождения не указана
        """
        return obj.get_age()
    
    def get_movies_count(self, obj: ActorDirector) -> int:
        """
        Количество фильмов с участием актера/режиссера.
        
        Args:
            obj: Объект актера/режиссера
            
        Returns:
            int: Количество фильмов с участием данного актера/режиссера
        """
        return obj.movies.count()


class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для отзывов.
    
    Предоставляет данные об отзывах с дополнительной информацией о лайках,
    рейтинге и свежести отзыва.
    """
    user_username = serializers.CharField(source='user.username', read_only=True)
    movie_title = serializers.CharField(source='movie_tvshow.title', read_only=True)
    likes_count = serializers.SerializerMethodField()
    dislikes_count = serializers.SerializerMethodField()
    rating_percentage = serializers.SerializerMethodField()
    is_fresh = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = ['id', 'movie_tvshow', 'user_username', 'movie_title', 'review_text', 
                 'likes_count', 'dislikes_count', 'rating_percentage', 
                 'is_fresh', 'created_at']
    
    def get_likes_count(self, obj: Review) -> int:
        """
        Точное количество лайков.
        
        Args:
            obj: Объект отзыва
            
        Returns:
            int: Количество лайков отзыва
        """
        return obj.get_likes_count()
    
    def get_dislikes_count(self, obj: Review) -> int:
        """
        Точное количество дизлайков.
        
        Args:
            obj: Объект отзыва
            
        Returns:
            int: Количество дизлайков отзыва
        """
        return obj.get_dislikes_count()
    
    def get_rating_percentage(self, obj: Review) -> float:
        """
        Рейтинг отзыва в процентах.
        
        Args:
            obj: Объект отзыва
            
        Returns:
            float: Рейтинг отзыва в процентах
        """
        return obj.get_rating()
    
    def get_is_fresh(self, obj: Review) -> bool:
        """
        Свежий ли отзыв (менее 7 дней).
        
        Args:
            obj: Объект отзыва
            
        Returns:
            bool: True если отзыв свежий, False в противном случае
        """
        return obj.is_fresh()


class MovieTVShowSerializer(serializers.ModelSerializer):
    """
    Сериализатор для фильмов/сериалов с SerializerMethodField и контекстом.
    
    Предоставляет полную информацию о фильме/сериале с дополнительными
    вычисляемыми полями и вложенными сериализаторами.
    """
    
    formatted_duration = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    reviews_count = serializers.SerializerMethodField()
    ratings_count = serializers.SerializerMethodField()
    is_new_release = serializers.SerializerMethodField()
    days_since_release = serializers.SerializerMethodField()
    is_highlighted = serializers.SerializerMethodField()
    
    genres = GenreSerializer(many=True, read_only=True)
    actors_directors = ActorDirectorSerializer(many=True, read_only=True)
    
    class Meta:
        model = MovieTVShow
        fields = [
            'id', 'title', 'description', 'type', 'release_date', 'duration',
            'seasons_count', 'episodes_count', 'end_date', 'status',
            'age_restriction', 'poster_url', 'country', 'created_at', 'updated_at',
            'formatted_duration', 'average_rating', 'reviews_count', 'ratings_count',
            'is_new_release', 'days_since_release', 'is_highlighted',
            'genres', 'actors_directors'
        ]
    
    def get_formatted_duration(self, obj: MovieTVShow) -> Optional[str]:
        """
        Пример использования SerializerMethodField:
        Форматирование продолжительности в часы и минуты.
        
        Args:
            obj: Объект фильма/сериала
            
        Returns:
            Optional[str]: Отформатированная продолжительность или None
        """
        if not obj.duration:
            return None
        
        hours = obj.duration // 60
        minutes = obj.duration % 60
        
        if hours > 0:
            return f"{hours}ч {minutes}мин"
        else:
            return f"{minutes}мин"
    
    def get_average_rating(self, obj: MovieTVShow) -> float:
        """
        Средний рейтинг фильма.
        
        Args:
            obj: Объект фильма/сериала
            
        Returns:
            float: Средний рейтинг фильма/сериала
        """
        return obj.get_average_rating()
    
    def get_reviews_count(self, obj: MovieTVShow) -> int:
        """
        Количество отзывов.
        
        Args:
            obj: Объект фильма/сериала
            
        Returns:
            int: Количество отзывов на фильм/сериал
        """
        return obj.reviews.count()
    
    def get_ratings_count(self, obj: MovieTVShow) -> int:
        """
        Количество оценок.
        
        Args:
            obj: Объект фильма/сериала
            
        Returns:
            int: Количество оценок фильма/сериала
        """
        return obj.ratings.count()
    
    def get_is_new_release(self, obj: MovieTVShow) -> bool:
        """
        Является ли новинкой.
        
        Args:
            obj: Объект фильма/сериала
            
        Returns:
            bool: True если фильм/сериал новинка, False в противном случае
        """
        return obj.is_new_release()
    
    def get_days_since_release(self, obj: MovieTVShow) -> Optional[int]:
        """
        Дней с момента выхода.
        
        Args:
            obj: Объект фильма/сериала
            
        Returns:
            Optional[int]: Количество дней с момента выхода или None
        """
        return obj.days_since_release()
    
    def get_is_highlighted(self, obj: MovieTVShow) -> bool:
        """
        Пример использования контекста:
        Проверяет, находится ли фильм в списке выделенных.
        
        Args:
            obj: Объект фильма/сериала
            
        Returns:
            bool: True если фильм выделен, False в противном случае
        """
        highlighted_movies = self.context.get('highlighted_movies', [])
        return obj.id in highlighted_movies


class MovieTVShowListSerializer(MovieTVShowSerializer):
    """
    Упрощенный сериализатор для списка фильмов.
    
    Предоставляет сокращенную информацию о фильмах/сериалах
    для использования в списках и каталогах.
    """
    
    class Meta(MovieTVShowSerializer.Meta):
        fields = [
            'id', 'title', 'type', 'release_date', 'poster_url',
            'formatted_duration', 'average_rating', 'reviews_count',
            'is_new_release', 'is_highlighted', 'genres'
        ]


class RecommendationSerializer(serializers.ModelSerializer):
    """
    Сериализатор для рекомендаций.
    
    Предоставляет информацию о рекомендациях с данными о фильме и пользователе.
    """
    movie = MovieTVShowListSerializer(source='movie_tvshow', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Recommendation
        fields = ['id', 'user_username', 'movie', 'reason_code', 'created_at']


class RatingSerializer(serializers.ModelSerializer):
    """
    Сериализатор для рейтингов.
    
    Предоставляет информацию об оценках фильмов/сериалов с данными о пользователе.
    """
    user_username = serializers.CharField(source='user.username', read_only=True)
    movie_title = serializers.CharField(source='movie_tvshow.title', read_only=True)
    
    class Meta:
        model = Rating
        fields = ['id', 'movie_tvshow', 'user_username', 'movie_title', 'rating_value', 'created_at']


class MovieTVShowCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания фильмов/сериалов через API.
    
    Предоставляет валидацию и обработку данных при создании новых фильмов/сериалов.
    """
    
    class Meta:
        model = MovieTVShow
        fields = [
            'title', 'description', 'type', 'release_date', 'duration',
            'seasons_count', 'episodes_count', 'end_date', 'status',
            'age_restriction', 'poster_url', 'country', 'genres'
        ]
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Дополнительная валидация данных.
        
        Проверяет соответствие полей типу контента (фильм/сериал).
        
        Args:
            data: Данные для валидации
            
        Returns:
            Dict[str, Any]: Валидированные данные
            
        Raises:
            serializers.ValidationError: При нарушении правил валидации
        """
        # Проверяем соответствие полей типу контента
        if data.get('type') == 'movie':
            if not data.get('duration'):
                raise serializers.ValidationError({
                    'duration': 'Для фильмов продолжительность обязательна'
                })
            if data.get('seasons_count') or data.get('episodes_count'):
                raise serializers.ValidationError({
                    'seasons_count': 'Фильмы не могут иметь сезоны',
                    'episodes_count': 'Фильмы не могут иметь эпизоды'
                })
        
        elif data.get('type') == 'tv_show':
            if data.get('duration'):
                raise serializers.ValidationError({
                    'duration': 'Сериалы не должны иметь общую продолжительность'
                })
            if not data.get('seasons_count'):
                raise serializers.ValidationError({
                    'seasons_count': 'Для сериалов количество сезонов обязательно'
                })
        
        return data 