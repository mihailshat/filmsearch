from datetime import timedelta, timezone
import django_filters
from django.db.models import Q
from .models import MovieTVShow, Review, Rating, Genre, ActorDirector, MovieTVShowActorDirector

class MovieTVShowFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    description = django_filters.CharFilter(lookup_expr='icontains')
    genres = django_filters.CharFilter(field_name='genres__name', lookup_expr='icontains')
    country = django_filters.CharFilter(lookup_expr='icontains')
    year = django_filters.NumberFilter(field_name='release_date__year')
    min_rating = django_filters.NumberFilter(method='filter_min_rating')
    type = django_filters.ChoiceFilter(choices=MovieTVShow.TYPE_CHOICES)
    status = django_filters.ChoiceFilter(choices=MovieTVShow.STATUS_CHOICES)
    director = django_filters.CharFilter(field_name='director__full_name', lookup_expr='icontains')
    actors = django_filters.CharFilter(field_name='actors__full_name', lookup_expr='icontains')
    is_new = django_filters.BooleanFilter(method='filter_is_new')
    has_reviews = django_filters.BooleanFilter(method='filter_has_reviews')
    min_reviews = django_filters.NumberFilter(method='filter_min_reviews')
    min_duration = django_filters.NumberFilter(field_name='duration', lookup_expr='gte')
    max_duration = django_filters.NumberFilter(field_name='duration', lookup_expr='lte')

    class Meta:
        model = MovieTVShow
        fields = ['type', 'status', 'genres', 'country']

    def filter_min_rating(self, queryset, name, value):
        return queryset.annotate(
            avg_rating=django_filters.Avg('ratings__rating')
        ).filter(avg_rating__gte=value)

    def filter_is_new(self, queryset, name, value):
        if value:
            return queryset.filter(
                release_date__gte=timezone.now() - timedelta(days=30)
            )
        return queryset

    def filter_has_reviews(self, queryset, name, value):
        if value:
            return queryset.filter(reviews__isnull=False).distinct()
        return queryset.filter(reviews__isnull=True).distinct()

    def filter_min_reviews(self, queryset, name, value):
        return queryset.annotate(
            review_count=django_filters.Count('reviews')
        ).filter(review_count__gte=value)

class ReviewFilter(django_filters.FilterSet):
    movie = django_filters.CharFilter(field_name='movie_tvshow__title', lookup_expr='icontains')
    user = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains')
    content = django_filters.CharFilter(lookup_expr='icontains')
    min_likes = django_filters.NumberFilter(method='filter_min_likes')
    date_from = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    min_rating = django_filters.NumberFilter(field_name='rating__rating', lookup_expr='gte')
    moderation_status = django_filters.ChoiceFilter(choices=Review.MODERATION_STATUS_CHOICES)

    class Meta:
        model = Review
        fields = ['movie_tvshow', 'user', 'moderation_status']

    def filter_min_likes(self, queryset, name, value):
        return queryset.annotate(
            likes_count=django_filters.Count('votes', filter=Q(votes__vote_type='like'))
        ).filter(likes_count__gte=value)

class RatingFilter(django_filters.FilterSet):
    movie = django_filters.CharFilter(field_name='movie_tvshow__title', lookup_expr='icontains')
    user = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains')
    min_rating = django_filters.NumberFilter(field_name='rating_value', lookup_expr='gte')
    max_rating = django_filters.NumberFilter(field_name='rating_value', lookup_expr='lte')
    date_from = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    has_review = django_filters.BooleanFilter(method='filter_has_review')

    class Meta:
        model = Rating
        fields = ['movie_tvshow', 'user', 'rating_value']

    def filter_has_review(self, queryset, name, value):
        if value:
            return queryset.filter(review__isnull=False)
        return queryset.filter(review__isnull=True)

class GenreFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(lookup_expr='icontains')
    min_movies = django_filters.NumberFilter(method='filter_min_movies')
    has_movies = django_filters.BooleanFilter(method='filter_has_movies')
    movie_type = django_filters.ChoiceFilter(
        field_name='movies__type',
        choices=MovieTVShow.TYPE_CHOICES
    )

    class Meta:
        model = Genre
        fields = ['name']

    def filter_min_movies(self, queryset, name, value):
        return queryset.annotate(
            movies_count=django_filters.Count('movies')
        ).filter(movies_count__gte=value)

    def filter_has_movies(self, queryset, name, value):
        if value:
            return queryset.filter(movies__isnull=False).distinct()
        return queryset.filter(movies__isnull=True).distinct()

class ActorDirectorFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='full_name', lookup_expr='icontains')
    role = django_filters.ChoiceFilter(choices=MovieTVShowActorDirector.ROLE_CHOICES)
    min_movies = django_filters.NumberFilter(method='filter_min_movies')
    movie_type = django_filters.ChoiceFilter(
        field_name='movies__type',
        choices=MovieTVShow.TYPE_CHOICES
    )
    movie_genre = django_filters.CharFilter(
        field_name='movies__genres__name',
        lookup_expr='icontains'
    )
    is_actor = django_filters.BooleanFilter(method='filter_is_actor')
    is_director = django_filters.BooleanFilter(method='filter_is_director')

    class Meta:
        model = ActorDirector
        fields = ['role']

    def filter_min_movies(self, queryset, name, value):
        return queryset.annotate(
            movies_count=django_filters.Count('movies')
        ).filter(movies_count__gte=value)

    def filter_is_actor(self, queryset, name, value):
        if value:
            return queryset.filter(role='actor')
        return queryset.exclude(role='actor')

    def filter_is_director(self, queryset, name, value):
        if value:
            return queryset.filter(role='director')
        return queryset.exclude(role='director') 