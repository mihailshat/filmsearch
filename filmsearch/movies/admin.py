from django.contrib import admin, messages
from django.db.models import Count, Avg
from django.utils.html import format_html, mark_safe
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.template.loader import render_to_string
from django.contrib.admin.views.decorators import staff_member_required
from django.conf import settings
import weasyprint
from .models import (
    Genre, ActorDirector, MovieTVShow, MovieTVShowActorDirector,
    Collection, CollectionItem, UserProfile, UserGenrePreference, Recommendation,
    Rating, Review, ReviewVote, UserWatchlist
)
from django.utils import timezone


class MovieTVShowInline(admin.TabularInline):
    """Встроенное отображение фильмов/сериалов для жанров"""
    model = MovieTVShow.genres.through
    extra = 0
    verbose_name = 'Фильм/Сериал'
    verbose_name_plural = 'Фильмы/Сериалы'
    raw_id_fields = ('movietvshow',)
    readonly_fields = ('get_title', 'get_type', 'get_release_date')
    
    def get_title(self, obj):
        return obj.movietvshow.title
    get_title.short_description = 'Название'
    
    def get_type(self, obj):
        return obj.movietvshow.get_type_display()
    get_type.short_description = 'Тип'
    
    def get_release_date(self, obj):
        return obj.movietvshow.release_date
    get_release_date.short_description = 'Дата выхода'
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Админ-панель для модели Genre"""
    list_display = ('name', 'movies_count', 'show_movies_link')
    search_fields = ('name', 'description')
    list_per_page = 20
    inlines = [MovieTVShowInline]
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(movies_count_val=Count('movies'))
        return qs
    
    @admin.display(description='Количество фильмов/сериалов', ordering='movies_count_val')
    def movies_count(self, obj):
        return obj.movies.count()
    
    @admin.display(description='Фильмы/Сериалы')
    def show_movies_link(self, obj):
        url = reverse('admin:movies_movietvshow_changelist') + f'?genres__id__exact={obj.id}'
        return format_html('<a href="{}">Показать фильмы</a>', url)


class MovieTVShowActorDirectorInline(admin.TabularInline):
    """Встроенное отображение ролей в фильмах/сериалах"""
    model = MovieTVShowActorDirector
    extra = 0
    verbose_name = 'Роль в фильме/сериале'
    verbose_name_plural = 'Роли в фильмах/сериалах'
    raw_id_fields = ('movie_tvshow',)
    readonly_fields = ('get_movie_title', 'get_movie_type', 'get_release_date')
    fields = ('movie_tvshow', 'get_movie_title', 'get_movie_type', 'get_release_date', 'role', 'character_name')
    
    def get_movie_title(self, obj):
        return obj.movie_tvshow.title if obj.movie_tvshow else '-'
    get_movie_title.short_description = 'Название'
    
    def get_movie_type(self, obj):
        return obj.movie_tvshow.get_type_display() if obj.movie_tvshow else '-'
    get_movie_type.short_description = 'Тип'
    
    def get_release_date(self, obj):
        return obj.movie_tvshow.release_date if obj.movie_tvshow else '-'
    get_release_date.short_description = 'Дата выхода'


@admin.register(ActorDirector)
class ActorDirectorAdmin(admin.ModelAdmin):
    """Админ-панель для модели ActorDirector"""
    list_display = ('full_name', 'birth_date', 'photo_display', 'resume_display', 'has_photo_file', 'has_resume_file', 'movies_count', 'show_movies_link')
    list_filter = ('birth_date', 'movie_roles__role')
    search_fields = ('full_name', 'biography')
    readonly_fields = ('photo_preview', 'photo_full', 'photo_file_preview', 'resume_file_info')
    fieldsets = (
        ('Основная информация', {
            'fields': ('full_name', 'birth_date', 'biography'),
        }),
        ('Фото (URL)', {
            'fields': ('photo_url', 'photo_preview'),
            'classes': ('collapse',),
        }),
        ('Фото (файл)', {
            'fields': ('photo_image', 'photo_file_preview'),
        }),
        ('Резюме/Биография (файл)', {
            'fields': ('resume_file', 'resume_file_info'),
        }),
        ('Полное фото', {
            'fields': ('photo_full',),
            'classes': ('collapse',),
        }),
    )
    inlines = [MovieTVShowActorDirectorInline]
    list_per_page = 20
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(movies_count_val=Count('movies'))
        return qs
    
    @admin.display(description='Фото')
    def photo_preview(self, obj):
        """Предпросмотр фото в форме редактирования (приоритет файлу, затем URL)"""
        if obj.photo_image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.photo_image.url)
        elif obj.photo_url:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', obj.photo_url)
        return '-'
    
    @admin.display(description='Фото')
    def photo_display(self, obj):
        """Отображение фото в списке (приоритет файлу, затем URL)"""
        if obj.photo_image:
            return format_html('<img src="{}" width="40" height="40" style="object-fit: cover; border-radius: 4px;" title="Файл: {}" />', 
                            obj.photo_image.url, obj.photo_image.name.split('/')[-1])
        elif obj.photo_url:
            return format_html('<img src="{}" width="40" height="40" style="object-fit: cover; border-radius: 4px;" title="URL" />', 
                            obj.photo_url)
        return '-'
    
    @admin.display(description='Резюме')  
    def resume_display(self, obj):
        """Отображение информации о резюме в списке"""
        if obj.resume_file:
            file_size_mb = obj.resume_file.size / (1024 * 1024) 
            file_name = obj.resume_file.name.split('/')[-1]
            display_name = file_name[:20] + '...' if len(file_name) > 20 else file_name
            
            return format_html(
                '<a href="{}" target="_blank" title="Размер: {} МБ">📄 {}</a>', 
                obj.resume_file.url, 
                f'{file_size_mb:.1f}',  
                display_name
            )
        return '-'
    
    @admin.display(description='Полное фото')
    def photo_full(self, obj):
        """Полное фото в форме редактирования (приоритет файлу, затем URL)"""
        if obj.photo_image:
            return format_html('<img src="{}" width="300" />', obj.photo_image.url)
        elif obj.photo_url:
            return format_html('<img src="{}" width="300" />', obj.photo_url)
        return '-'
    
    @admin.display(description='Количество фильмов/сериалов', ordering='movies_count_val')
    def movies_count(self, obj):
        return obj.movies.count()
    
    @admin.display(description='Фильмы/Сериалы')
    def show_movies_link(self, obj):
        url = reverse('admin:movies_movietvshow_changelist') + f'?actors_directors__id__exact={obj.id}'
        return format_html('<a href="{}">Показать фильмы</a>', url)
    
    @admin.display(description='Фото файл', boolean=True)
    def has_photo_file(self, obj):
        return bool(obj.photo_image)
    
    @admin.display(description='Резюме файл', boolean=True)
    def has_resume_file(self, obj):
        return bool(obj.resume_file)
    
    @admin.display(description='Предпросмотр фото файла')
    def photo_file_preview(self, obj):
        if obj.photo_image:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: cover;" />', obj.photo_image.url)
        return '-'
    
    @admin.display(description='Информация о файле резюме')
    def resume_file_info(self, obj):
        if obj.resume_file:
            file_size = obj.resume_file.size
            file_size_mb = file_size / (1024 * 1024)
            return format_html(
                '<p><strong>Файл:</strong> {}<br><strong>Размер:</strong> {} МБ<br><a href="{}" target="_blank">📄 Скачать</a></p>',
                obj.resume_file.name.split('/')[-1],
                f'{file_size_mb:.2f}',  
                obj.resume_file.url
            )
        return '-'


class MovieTVShowGenreInline(admin.TabularInline):
    """Встроенное отображение жанров"""
    model = MovieTVShow.genres.through
    extra = 0
    verbose_name = 'Жанр'
    verbose_name_plural = 'Жанры'


class MovieTVShowActorDirectorInlineForMovie(admin.TabularInline):
    """Встроенное отображение актеров/режиссеров"""
    model = MovieTVShowActorDirector
    extra = 0
    verbose_name = 'Актер/Режиссер'
    verbose_name_plural = 'Актеры/Режиссеры'
    raw_id_fields = ('actor_director',)
    fields = ('actor_director', 'role', 'character_name', 'get_photo')
    readonly_fields = ('get_photo',)
    
    def get_photo(self, obj):
        if obj.actor_director:
            if obj.actor_director.photo_image:
                return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', 
                                obj.actor_director.photo_image.url)
            elif obj.actor_director.photo_url:
                return format_html('<img src="{}" width="50" height="50" style="object-fit: cover;" />', 
                                obj.actor_director.photo_url)
        return '-'
    get_photo.short_description = 'Фото'


class RatingInline(admin.TabularInline):
    """Встроенное отображение оценок"""
    model = Rating
    extra = 0
    verbose_name = 'Оценка'
    verbose_name_plural = 'Оценки'
    raw_id_fields = ('user',)
    readonly_fields = ('created_at',)
    fields = ('user', 'rating_value', 'created_at')


class ReviewInline(admin.TabularInline):
    """Встроенное отображение отзывов"""
    model = Review
    extra = 0
    verbose_name = 'Отзыв'
    verbose_name_plural = 'Отзывы'
    raw_id_fields = ('user',)
    readonly_fields = ('created_at', 'likes_count', 'dislikes_count')
    fields = ('user', 'review_text', 'likes_count', 'dislikes_count', 'created_at')


class UserWatchlistInline(admin.TabularInline):
    """Встроенное отображение списка просмотра"""
    model = UserWatchlist
    extra = 0
    verbose_name = 'Список просмотра'
    verbose_name_plural = 'Списки просмотра'
    raw_id_fields = ('user',)
    readonly_fields = ('added_at',)
    fields = ('user', 'status', 'progress', 'added_at')


class CollectionItemInlineForMovie(admin.TabularInline):
    """Встроенное отображение подборок для фильма/сериала"""
    model = CollectionItem
    extra = 0
    verbose_name = 'Подборка'
    verbose_name_plural = 'Подборки'
    raw_id_fields = ('collection',)
    readonly_fields = ('added_at', 'get_collection_type')
    fields = ('collection', 'get_collection_type', 'added_at')
    
    def get_collection_type(self, obj):
        if obj.collection and obj.collection.is_system:
            return 'Системная'
        return 'Пользовательская'
    get_collection_type.short_description = 'Тип подборки'


class CollectionItemInline(admin.TabularInline):
    """Встроенное отображение элементов подборки"""
    model = CollectionItem
    extra = 0
    verbose_name = 'Фильм/Сериал'
    verbose_name_plural = 'Фильмы/Сериалы'
    raw_id_fields = ('movie_tvshow',)
    readonly_fields = ('added_at', 'get_movie_type', 'get_rating', 'get_poster')
    fields = ('movie_tvshow', 'get_movie_type', 'get_rating', 'get_poster', 'added_at')
    
    def get_movie_type(self, obj):
        return obj.movie_tvshow.get_type_display() if obj.movie_tvshow else '-'
    get_movie_type.short_description = 'Тип'
    
    def get_rating(self, obj):
        if hasattr(obj.movie_tvshow, 'average_rating'):
            avg = obj.movie_tvshow.average_rating
            if avg > 0:
                return f"{avg:.1f}/10"
        return '-'
    get_rating.short_description = 'Рейтинг'
    
    def get_poster(self, obj):
        if obj.movie_tvshow:
            if obj.movie_tvshow.poster_image:
                return format_html('<img src="{}" width="50" height="70" style="object-fit: cover;" />', 
                                obj.movie_tvshow.poster_image.url)
            elif obj.movie_tvshow.poster_url:
                return format_html('<img src="{}" width="50" height="70" style="object-fit: cover;" />', 
                                obj.movie_tvshow.poster_url)
        return '-'
    get_poster.short_description = 'Постер'


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    """Админ-панель для модели Collection"""
    list_display = ('title', 'get_user_display', 'is_system', 'is_public', 'created_at', 'items_count', 'show_items_link')
    list_filter = ('is_system', 'is_public', 'created_at')
    search_fields = ('title', 'description', 'user__username')
    raw_id_fields = ('user',)
    inlines = [CollectionItemInline]
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 20
    
    def get_fieldsets(self, request, obj=None):
        """Динамически определяем набор полей в зависимости от типа подборки"""
        if obj and obj.is_system:
            # системная - не показываем пользователя и всегда публичны
            return (
                ('Основная информация', {
                    'fields': ('title', 'description', 'is_system')
                }),
                ('Даты', {
                    'fields': ('created_at', 'updated_at'),
                    'classes': ('collapse',),
                }),
            )
        else:
            # пользовательская - показываем всё
            return (
                ('Основная информация', {
                    'fields': ('title', 'user', 'description')
                }),
                ('Настройки', {
                    'fields': ('is_system', 'is_public')
                }),
                ('Даты', {
                    'fields': ('created_at', 'updated_at'),
                    'classes': ('collapse',),
                }),
            )
    
    def get_readonly_fields(self, request, obj=None):
        """Динамически определяем поля только для чтения"""
        readonly_fields = list(self.readonly_fields)
        if obj and obj.is_system:
            # системная - поле публичности только для чтения
            readonly_fields.append('is_public')
        return readonly_fields
    
    def add_view(self, request, form_url='', extra_context=None):
        """Настройка контекста для создания новой подборки"""
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False  
        extra_context['title'] = 'Добавить подборку'
        return super().add_view(request, form_url, extra_context)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Настройка контекста для редактирования подборки"""
        extra_context = extra_context or {}
        obj = self.get_object(request, object_id)
        if obj and obj.is_system:
            extra_context['title'] = f'Системная подборка: {obj.title}'
        return super().change_view(request, object_id, form_url, extra_context)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(items_count_val=Count('items'))
        return qs
    
    @admin.display(description='Пользователь')
    def get_user_display(self, obj):
        if obj.is_system:
            return '-'
        elif obj.user:
            return obj.user.username
        return 'Не указан'
    
    @admin.display(description='Количество элементов', ordering='items_count_val')
    def items_count(self, obj):
        return obj.get_items_count()
    
    @admin.display(description='Фильмы/Сериалы')
    def show_items_link(self, obj):
        url = reverse('admin:movies_movietvshow_changelist') + f'?collections__id__exact={obj.id}'
        return format_html('<a href="{}">Показать фильмы</a>', url)
    
    def save_model(self, request, obj, form, change):
        """Переопределяем сохранение для автоматической корректировки полей"""
        if obj.is_system:
            obj.is_public = True
            obj.user = None
        super().save_model(request, obj, form, change)


@admin.register(CollectionItem)
class CollectionItemAdmin(admin.ModelAdmin):
    """Админ-панель для модели CollectionItem"""
    list_display = ('movie_tvshow', 'get_movie_type', 'collection', 'get_collection_type', 'added_at')
    list_filter = ('added_at', 'collection__is_system', 'movie_tvshow__type')
    search_fields = ('movie_tvshow__title', 'collection__title')
    raw_id_fields = ('movie_tvshow', 'collection')
    date_hierarchy = 'added_at'
    readonly_fields = ('added_at',)
    list_per_page = 30
    
    def get_movie_type(self, obj):
        return obj.movie_tvshow.get_type_display() if obj.movie_tvshow else '-'
    get_movie_type.short_description = 'Тип'
    
    def get_collection_type(self, obj):
        if obj.collection and obj.collection.is_system:
            return 'Системная'
        return 'Пользовательская'
    get_collection_type.short_description = 'Тип подборки'


class PreferredGenresInline(admin.TabularInline):
    """Встроенное отображение предпочитаемых жанров"""
    model = UserProfile.preferred_genres.through
    extra = 0
    verbose_name = 'Предпочитаемый жанр'
    verbose_name_plural = 'Предпочитаемые жанры'


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Админ-панель для модели UserProfile"""
    list_display = ('user', 'get_preferred_genres', 'created_at', 'updated_at')
    filter_horizontal = ('preferred_genres',)
    raw_id_fields = ('user',)
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at')
    exclude = ('preferred_genres',)
    inlines = [PreferredGenresInline]
    
    @admin.display(description='Предпочитаемые жанры')
    def get_preferred_genres(self, obj):
        genres = [genre.name for genre in obj.preferred_genres.all()[:5]]
        if len(genres) > 0:
            return ', '.join(genres)
        return 'Не указаны'


@admin.register(UserGenrePreference)
class UserGenrePreferenceAdmin(admin.ModelAdmin):
    """Админ-панель для устаревшей модели UserGenrePreference"""
    list_display = ('user', 'genre')
    list_filter = ('genre',)
    search_fields = ('user__username', 'genre__name')
    raw_id_fields = ('user',)


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    """Админ-панель для модели Recommendation"""
    list_display = ('user', 'movie_tvshow', 'get_movie_type', 'get_genres', 'reason_code', 'created_at')
    list_filter = ('created_at', 'reason_code', 'movie_tvshow__type', 'movie_tvshow__genres')
    search_fields = ('user__username', 'movie_tvshow__title')
    raw_id_fields = ('user', 'movie_tvshow')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    list_per_page = 20
    
    def get_movie_type(self, obj):
        return obj.movie_tvshow.get_type_display() if obj.movie_tvshow else '-'
    get_movie_type.short_description = 'Тип'
    
    def get_genres(self, obj):
        if obj.movie_tvshow:
            genres = [genre.name for genre in obj.movie_tvshow.genres.all()[:3]]
            if len(genres) > 0:
                return ', '.join(genres)
        return '-'
    get_genres.short_description = 'Жанры'


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """Админ-панель для модели Rating"""
    list_display = ('user', 'movie_tvshow', 'get_movie_type', 'rating_value', 'created_at')
    list_filter = ('rating_value', 'created_at', 'movie_tvshow__type')
    search_fields = ('user__username', 'movie_tvshow__title')
    raw_id_fields = ('user', 'movie_tvshow')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    list_per_page = 20
    
    def get_movie_type(self, obj):
        return obj.movie_tvshow.get_type_display() if obj.movie_tvshow else '-'
    get_movie_type.short_description = 'Тип'


class ReviewVoteInline(admin.TabularInline):
    """Встроенное отображение оценок отзывов"""
    model = ReviewVote
    extra = 0
    verbose_name = 'Оценка отзыва'
    verbose_name_plural = 'Оценки отзыва'
    raw_id_fields = ('user',)
    readonly_fields = ('voted_at',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    """Админ-панель для модели Review"""
    list_display = ('user', 'movie_tvshow', 'get_movie_type', 'short_text', 
                'moderation_status', 'moderated_by', 'created_at', 'likes_count', 'dislikes_count', 'rating_percent')
    list_filter = ('moderation_status', 'created_at', 'movie_tvshow__type', 'moderated_by')
    search_fields = ('user__username', 'movie_tvshow__title', 'review_text')
    raw_id_fields = ('user', 'movie_tvshow', 'moderated_by')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'likes_count', 'dislikes_count', 'moderated_at')
    inlines = [ReviewVoteInline]
    list_per_page = 20
    actions = ['approve_reviews', 'reject_reviews']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'movie_tvshow', 'review_text')
        }),
        ('Модерация', {
            'fields': ('moderation_status', 'moderated_by', 'moderated_at', 'rejection_reason')
        }),
        ('Статистика', {
            'fields': ('likes_count', 'dislikes_count')
        }),
        ('Даты', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )
    
    def get_movie_type(self, obj):
        return obj.movie_tvshow.get_type_display() if obj.movie_tvshow else '-'
    get_movie_type.short_description = 'Тип'
    
    @admin.display(description='Текст отзыва')
    def short_text(self, obj):
        if len(obj.review_text) > 50:
            return obj.review_text[:50] + '...'
        return obj.review_text
    
    @admin.display(description='Лайки')
    def likes_count(self, obj):
        return obj.get_likes_count()
    
    @admin.display(description='Дизлайки')
    def dislikes_count(self, obj):
        return obj.get_dislikes_count()
    
    @admin.display(description='Рейтинг (%)')
    def rating_percent(self, obj):
        rating = obj.get_rating()
        return format_html('<span style="color: #{};">{}%</span>', 
                        self.get_rating_color(rating), f'{rating:.1f}')
    
    def get_rating_color(self, rating):
        """Возвращает цвет в зависимости от рейтинга"""
        if rating >= 80:
            return '2e7d32'  # зеленый
        elif rating >= 60:
            return '1976d2'  # синий
        elif rating >= 40:
            return 'ffa000'  # оранжевый
        else:
            return 'c62828'  # красный
    
    @admin.action(description='Одобрить выбранные отзывы')
    def approve_reviews(self, request, queryset):
        """Массовое одобрение отзывов"""
        updated = 0
        for review in queryset:
            if review.moderation_status != 'approved':
                review.approve(request.user)
                updated += 1
        
        self.message_user(
            request,
            f'Одобрено отзывов: {updated}',
            messages.SUCCESS
        )
    
    @admin.action(description='Отклонить выбранные отзывы')
    def reject_reviews(self, request, queryset):
        """Массовое отклонение отзывов"""
        updated = 0
        for review in queryset:
            if review.moderation_status != 'rejected':
                review.reject(request.user, 'Массовое отклонение администратором')
                updated += 1
        
        self.message_user(
            request,
            f'Отклонено отзывов: {updated}',
            messages.WARNING
        )


@admin.register(ReviewVote)
class ReviewVoteAdmin(admin.ModelAdmin):
    """Админ-панель для модели ReviewVote"""
    list_display = ('user', 'review', 'get_review_movie', 'vote_type', 'voted_at')
    list_filter = ('vote_type', 'voted_at')
    search_fields = ('user__username', 'review__review_text', 'review__movie_tvshow__title')
    raw_id_fields = ('user', 'review')
    date_hierarchy = 'voted_at'
    readonly_fields = ('voted_at',)
    list_per_page = 20
    
    def get_review_movie(self, obj):
        if obj.review and obj.review.movie_tvshow:
            return obj.review.movie_tvshow.title
        return '-'
    get_review_movie.short_description = 'Фильм/Сериал'


@admin.register(UserWatchlist)
class UserWatchlistAdmin(admin.ModelAdmin):
    """Админ-панель для модели UserWatchlist"""
    list_display = ('user', 'movie_tvshow', 'get_movie_type', 'status', 'progress', 'added_at')
    list_filter = ('status', 'added_at', 'movie_tvshow__type')
    search_fields = ('user__username', 'movie_tvshow__title')
    raw_id_fields = ('user', 'movie_tvshow')
    date_hierarchy = 'added_at'
    readonly_fields = ('added_at',)
    list_per_page = 20
    
    def get_movie_type(self, obj):
        return obj.movie_tvshow.get_type_display() if obj.movie_tvshow else '-'
    get_movie_type.short_description = 'Тип'


@admin.register(MovieTVShow)
class MovieTVShowAdmin(admin.ModelAdmin):
    """Админ-панель для модели MovieTVShow"""
    list_display = ('title', 'type', 'poster_display', 'release_date', 'status', 'get_genres_display', 
                'country', 'average_rating_display', 'ratings_count', 'reviews_count', 
                'movie_pdf_report')
    list_filter = ('type', 'status', 'release_date', 'genres', 'country', 'age_restriction')
    search_fields = ('title', 'description', 'country')
    date_hierarchy = 'release_date'
    readonly_fields = ('created_at', 'updated_at', 'average_rating_display', 'poster_preview', 
                    'poster_large', 'poster_file_preview', 'ratings_count', 'reviews_count')
    filter_horizontal = ('genres',)
    list_display_links = ('title',)
    list_per_page = 20
    actions = ['generate_movies_summary_pdf', 'mark_as_finished', 'mark_as_ongoing']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'type', 'release_date', 'age_restriction', 'country')
        }),
        ('Постер (URL)', {
            'fields': ('poster_url', 'poster_preview'),
            'classes': ('collapse',),
        }),
        ('Постер (файл)', {
            'fields': ('poster_image', 'poster_file_preview'),
        }),
        ('Медиаконтент', {
            'fields': ('poster_large',),
            'classes': ('collapse',),
        }),
        ('Детали фильма', {
            'fields': ('duration',),
            'classes': ('collapse',),
        }),
        ('Детали сериала', {
            'fields': ('seasons_count', 'episodes_count', 'end_date', 'status'),
            'classes': ('collapse',),
        }),
        ('Категории', {
            'fields': ('genres',),
        }),
        ('Статистика', {
            'fields': ('average_rating_display', 'ratings_count', 'reviews_count'),
            'classes': ('collapse',),
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    inlines = [MovieTVShowActorDirectorInlineForMovie, MovieTVShowGenreInline, 
            RatingInline, ReviewInline, UserWatchlistInline, CollectionItemInlineForMovie]
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related(
            'genres', 'ratings', 'reviews', 'actors_directors'
        ).annotate(
            ratings_count_val=Count('ratings', distinct=True),
            reviews_count_val=Count('reviews', distinct=True)
        )
    
    @admin.display(description='Жанры')
    def get_genres_display(self, obj):
        return ', '.join([genre.name for genre in obj.genres.all()[:3]])
    
    @admin.display(description='Средняя оценка')
    def average_rating_display(self, obj):
        avg = obj.average_rating
        if avg > 0:
            return format_html('<span style="color: #{};">{}/10</span>', 
                            self.get_rating_color(avg), f'{avg:.1f}')
        return 'Нет оценок'
    
    def get_rating_color(self, rating):
        """Возвращает цвет в зависимости от рейтинга"""
        if rating >= 8:
            return '2e7d32'  # зеленый
        elif rating >= 6:
            return '1976d2'  # синий
        elif rating >= 4:
            return 'ffa000'  # оранжевый
        else:
            return 'c62828'  # красный
    
    @admin.display(description='Количество оценок', ordering='ratings_count_val')
    def ratings_count(self, obj):
        return obj.ratings.count()
    
    @admin.display(description='Количество отзывов', ordering='reviews_count_val')
    def reviews_count(self, obj):
        return obj.reviews.count()
    
    @admin.display(description='Постер')
    def poster_preview(self, obj):
        """Предпросмотр постера в форме редактирования (приоритет файлу, затем URL)"""
        if obj.poster_image:
            return format_html('<img src="{}" width="100" height="140" style="object-fit: cover;" />', obj.poster_image.url)
        elif obj.poster_url:
            return format_html('<img src="{}" width="100" />', obj.poster_url)
        return '-'
    
    @admin.display(description='Постер')
    def poster_display(self, obj):
        """Отображение постера в списке (приоритет файлу, затем URL)"""
        if obj.poster_image:
            return format_html('<img src="{}" width="40" height="60" style="object-fit: cover; border-radius: 4px;" title="Файл: {}" />', 
                             obj.poster_image.url, obj.poster_image.name.split('/')[-1])
        elif obj.poster_url:
            return format_html('<img src="{}" width="40" height="60" style="object-fit: cover; border-radius: 4px;" title="URL" />', 
                             obj.poster_url)
        return '-'
    
    @admin.display(description='Полный постер')
    def poster_large(self, obj):
        """Полный постер в форме редактирования (приоритет файлу, затем URL)"""
        if obj.poster_image:
            return format_html('<img src="{}" width="300" />', obj.poster_image.url)
        elif obj.poster_url:
            return format_html('<img src="{}" width="300" />', obj.poster_url)
        return '-'
    
    @admin.display(description='Предпросмотр файла постера')
    def poster_file_preview(self, obj):
        if obj.poster_image:
            return format_html('<img src="{}" width="100" height="140" style="object-fit: cover;" />', obj.poster_image.url)
        return '-'
    
    @admin.display(description='PDF отчет')
    def movie_pdf_report(self, obj):
        """Генерирует ссылку на PDF отчет о фильме"""
        url = reverse('admin_movie_pdf', args=[obj.id])
        return mark_safe(f'<a href="{url}" target="_blank">📄 PDF отчет</a>')
    
    @admin.action(description='Сгенерировать сводный PDF отчет по выбранным фильмам')
    def generate_movies_summary_pdf(self, request, queryset):
        """Генерирует сводный PDF отчет по выбранным фильмам"""
        movies = queryset.select_related().prefetch_related('genres', 'reviews', 'ratings')
        
        context = {
            'movies': movies,
            'total_movies': movies.count(),
            'report_date': timezone.now(),
        }
        
        # рендерим HTML шаблон
        html = render_to_string('admin/movies/movies_summary_pdf.html', context)
        
        # создаем HTTP ответ с PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'filename=movies_summary_report_{timezone.now().strftime("%Y%m%d_%H%M")}.pdf'
        
        # генерация PDF с помощью WeasyPrint
        weasyprint.HTML(string=html).write_pdf(response)
        
        return response
    
    @admin.action(description='Отметить выбранные сериалы как завершенные')
    def mark_as_finished(self, request, queryset):
        """Массово отмечает сериалы как завершенные"""
        tv_shows = queryset.filter(type='tv_show')
        updated = tv_shows.update(status='finished')
        
        self.message_user(
            request,
            f'Отмечено как завершенные: {updated} сериалов',
            messages.SUCCESS
        )
    
    @admin.action(description='Отметить выбранные сериалы как выходящие')
    def mark_as_ongoing(self, request, queryset):
        """Массово отмечает сериалы как выходящие"""
        tv_shows = queryset.filter(type='tv_show')
        updated = tv_shows.update(status='ongoing')
        
        self.message_user(
            request,
            f'Отмечено как выходящие: {updated} сериалов',
            messages.SUCCESS
        )


@staff_member_required
def admin_movie_pdf(request, movie_id):
    """Генерация PDF отчета о фильме для администраторов"""
    from django.shortcuts import get_object_or_404
    
    movie = get_object_or_404(MovieTVShow, id=movie_id)
    
    # получаем допданные
    reviews = movie.reviews.select_related('user').order_by('-created_at')[:10]
    ratings = movie.ratings.select_related('user').order_by('-created_at')[:10]
    actors = movie.actors_directors.filter(movie_roles__role='actor')[:10]
    directors = movie.actors_directors.filter(movie_roles__role='director')[:5]
    
    context = {
        'movie': movie,
        'reviews': reviews,
        'ratings': ratings,
        'actors': actors,
        'directors': directors,
        'reviews_count': movie.reviews.count(),
        'ratings_count': movie.ratings.count(),
        'average_rating': movie.ratings.aggregate(avg=Avg('rating_value'))['avg'] or 0,
    }
    
    # рендерим HTML шаблон
    html = render_to_string('admin/movies/movie_pdf_report.html', context)
    
    # создаем HTTP ответ с PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=movie_report_{movie.id}_{movie.title[:20]}.pdf'
    
    # генерация PDF с помощью WeasyPrint
    weasyprint.HTML(string=html).write_pdf(response)
    
    return response
