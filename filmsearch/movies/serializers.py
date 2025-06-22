from rest_framework import serializers
from django.db.models import Avg, Count
from .models import MovieTVShow, Genre, ActorDirector, Review, Rating, Recommendation


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров"""
    movies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Genre
        fields = ['id', 'name', 'description', 'movies_count']
    
    def get_movies_count(self, obj):
        """Количество фильмов в жанре"""
        return obj.movies.count()


class ActorDirectorSerializer(serializers.ModelSerializer):
    """Сериализатор для актеров/режиссеров"""
    age = serializers.SerializerMethodField()
    movies_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ActorDirector
        fields = ['id', 'full_name', 'birth_date', 'biography', 'photo_url', 'age', 'movies_count']
    
    def get_age(self, obj):
        """Возраст актера/режиссера"""
        return obj.get_age()
    
    def get_movies_count(self, obj):
        """Количество фильмов с участием актера/режиссера"""
        return obj.movies.count()


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов"""
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
    
    def get_likes_count(self, obj):
        """Точное количество лайков"""
        return obj.get_likes_count()
    
    def get_dislikes_count(self, obj):
        """Точное количество дизлайков"""
        return obj.get_dislikes_count()
    
    def get_rating_percentage(self, obj):
        """Рейтинг отзыва в процентах"""
        return obj.get_rating()
    
    def get_is_fresh(self, obj):
        """Свежий ли отзыв (менее 7 дней)"""
        return obj.is_fresh()


class MovieTVShowSerializer(serializers.ModelSerializer):
    """Сериализатор для фильмов/сериалов с SerializerMethodField и контекстом"""
    
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
    
    def get_formatted_duration(self, obj):
        """
        Пример использования SerializerMethodField:
        Форматирование продолжительности в часы и минуты
        """
        if not obj.duration:
            return None
        
        hours = obj.duration // 60
        minutes = obj.duration % 60
        
        if hours > 0:
            return f"{hours}ч {minutes}мин"
        else:
            return f"{minutes}мин"
    
    def get_average_rating(self, obj):
        """Средний рейтинг фильма"""
        return obj.get_average_rating()
    
    def get_reviews_count(self, obj):
        """Количество отзывов"""
        return obj.reviews.count()
    
    def get_ratings_count(self, obj):
        """Количество оценок"""
        return obj.ratings.count()
    
    def get_is_new_release(self, obj):
        """Является ли новинкой"""
        return obj.is_new_release()
    
    def get_days_since_release(self, obj):
        """Дней с момента выхода"""
        return obj.days_since_release()
    
    def get_is_highlighted(self, obj):
        """
        Пример использования контекста:
        Проверяет, находится ли фильм в списке выделенных
        """
        highlighted_movies = self.context.get('highlighted_movies', [])
        return obj.id in highlighted_movies


class MovieTVShowListSerializer(MovieTVShowSerializer):
    """Упрощенный сериализатор для списка фильмов"""
    
    class Meta(MovieTVShowSerializer.Meta):
        fields = [
            'id', 'title', 'type', 'release_date', 'poster_url',
            'formatted_duration', 'average_rating', 'reviews_count',
            'is_new_release', 'is_highlighted', 'genres'
        ]


class RecommendationSerializer(serializers.ModelSerializer):
    """Сериализатор для рекомендаций"""
    movie = MovieTVShowListSerializer(source='movie_tvshow', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = Recommendation
        fields = ['id', 'user_username', 'movie', 'reason_code', 'created_at']


class RatingSerializer(serializers.ModelSerializer):
    """Сериализатор для рейтингов"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    movie_title = serializers.CharField(source='movie_tvshow.title', read_only=True)
    
    class Meta:
        model = Rating
        fields = ['id', 'movie_tvshow', 'user_username', 'movie_title', 'rating_value', 'created_at']


class MovieTVShowCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания фильмов/сериалов через API"""
    
    class Meta:
        model = MovieTVShow
        fields = [
            'title', 'description', 'type', 'release_date', 'duration',
            'seasons_count', 'episodes_count', 'end_date', 'status',
            'age_restriction', 'poster_url', 'country', 'genres'
        ]
    
    def validate(self, data):
        """Дополнительная валидация данных"""
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