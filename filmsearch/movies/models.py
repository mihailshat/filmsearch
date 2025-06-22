from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import datetime
from django.urls import reverse


class Genre(models.Model):
    """Модель для хранения жанров"""
    name = models.CharField(_('Название'), max_length=100)
    description = models.TextField(_('Описание'), blank=True)

    class Meta:
        verbose_name = _('Жанр')
        verbose_name_plural = _('Жанры')
        ordering = ['name']

    def __str__(self):
        return self.name


class ActorDirector(models.Model):
    """Модель для хранения информации об актерах и режиссерах"""
    full_name = models.CharField(_('Полное имя'), max_length=255)
    birth_date = models.DateField(_('Дата рождения'), null=True, blank=True)
    biography = models.TextField(_('Биография'), blank=True)
    photo_url = models.URLField(_('URL фото'), blank=True)
    
    # Добавляем ImageField и FileField
    photo_image = models.ImageField(
        _('Фото (файл)'), 
        upload_to='actors_photos/', 
        blank=True, 
        null=True,
        help_text=_('Загрузите фото актера/режиссера')
    )
    
    resume_file = models.FileField(
        _('Резюме/Биография (файл)'), 
        upload_to='actors_resumes/', 
        blank=True, 
        null=True,
        help_text=_('Загрузите файл с подробной биографией')
    )

    class Meta:
        verbose_name = _('Актер/Режиссер')
        verbose_name_plural = _('Актеры/Режиссеры')
        ordering = ['full_name']

    def __str__(self):
        return self.full_name
    
    def get_age(self):
        """
        Пример 1: Расчет возраста актера/режиссера на текущую дату
        
        В этом методе используется django.utils.timezone для получения текущей даты.
        Мы вычисляем возраст актера/режиссера, основываясь на его дате рождения.
        
        Такая функциональность может использоваться при отображении профиля 
        актера/режиссера, чтобы показать его текущий возраст без необходимости 
        обновления этой информации вручную.
        """
        if not self.birth_date:
            return None
            
        today = timezone.now().date()
        
        # Расчет возраста с учетом дня рождения в текущем году
        age = today.year - self.birth_date.year
        
        # Проверяем, был ли уже день рождения в этом году
        if (today.month, today.day) < (self.birth_date.month, self.birth_date.day):
            age -= 1
            
        return age
    
    def get_absolute_url(self):
        """
        Возвращает URL для просмотра деталей актера/режиссера.
        Используется в шаблонах для создания ссылок и редиректов после формы.
        """
        return reverse('actor_director_detail', kwargs={'pk': self.pk})


class MovieTVShowManager(models.Manager):
    """Собственный менеджер для модели MovieTVShow"""
    
    def get_queryset(self):
        """Возвращает базовый QuerySet"""
        return super().get_queryset()
    
    def movies_only(self):
        """Возвращает только фильмы"""
        return self.filter(type='movie')
    
    def tv_shows_only(self):
        """Возвращает только сериалы"""
        return self.filter(type='tv_show')
    
    def released_after(self, date):
        """Возвращает фильмы/сериалы, вышедшие после указанной даты"""
        return self.filter(release_date__gt=date)
    
    def top_rated(self, limit=10):
        """Возвращает топ фильмов/сериалов по средней оценке"""
        from django.db.models import Avg, Count
        return self.annotate(
            avg_rating=Avg('ratings__rating_value'),
            ratings_count=Count('ratings')
        ).filter(ratings_count__gt=0).order_by('-avg_rating')[:limit]
    
    def most_reviewed(self, limit=10):
        """Возвращает самые обсуждаемые фильмы/сериалы по количеству отзывов"""
        from django.db.models import Count
        return self.annotate(
            reviews_count=Count('reviews')
        ).order_by('-reviews_count')[:limit]
    
    def by_genre(self, genre_name):
        """Возвращает фильмы/сериалы определенного жанра"""
        return self.filter(genres__name__icontains=genre_name)
    
    def new_releases(self, days=30):
        """Возвращает новинки, вышедшие за последние N дней"""
        from django.utils import timezone
        date_threshold = timezone.now().date() - timezone.timedelta(days=days)
        return self.filter(release_date__gte=date_threshold).order_by('-release_date')
    
    def with_actor(self, actor_name):
        """Возвращает фильмы/сериалы с определенным актером"""
        return self.filter(
            actors_directors__full_name__icontains=actor_name,
            actor_director_roles__role='actor'
        ).distinct()


class MovieTVShow(models.Model):
    """Модель для хранения фильмов и сериалов"""
    TYPE_CHOICES = (
        ('movie', _('Фильм')),
        ('tv_show', _('Сериал')),
    )
    STATUS_CHOICES = (
        ('ongoing', _('Выходит')),
        ('finished', _('Завершен')),
        ('cancelled', _('Отменен')),
    )
    
    title = models.CharField(_('Название'), max_length=255)
    description = models.TextField(_('Описание'), blank=True)
    type = models.CharField(_('Тип'), max_length=10, choices=TYPE_CHOICES)
    release_date = models.DateField(_('Дата выхода'))
    duration = models.IntegerField(_('Продолжительность (мин)'), null=True, blank=True)
    seasons_count = models.IntegerField(_('Количество сезонов'), null=True, blank=True)
    episodes_count = models.IntegerField(_('Количество эпизодов'), null=True, blank=True)
    end_date = models.DateField(_('Дата завершения'), null=True, blank=True)
    status = models.CharField(_('Статус'), max_length=20, choices=STATUS_CHOICES, blank=True, null=True)
    age_restriction = models.CharField(_('Возрастное ограничение'), max_length=10, blank=True)
    poster_url = models.URLField(_('URL постера'), blank=True)
    
    # Добавляем ImageField для постера
    poster_image = models.ImageField(
        _('Постер (файл)'), 
        upload_to='movie_posters/', 
        blank=True, 
        null=True,
        help_text=_('Загрузите постер фильма/сериала')
    )
    
    country = models.CharField(_('Страна'), max_length=100, blank=True)
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    
    genres = models.ManyToManyField(Genre, verbose_name=_('Жанры'), related_name='movies')
    actors_directors = models.ManyToManyField(
        ActorDirector, 
        through='MovieTVShowActorDirector',
        verbose_name=_('Актеры/Режиссеры'),
        related_name='movies'
    )
    
    # Подключаем наш менеджер
    objects = MovieTVShowManager()

    class Meta:
        verbose_name = _('Фильм/Сериал')
        verbose_name_plural = _('Фильмы/Сериалы')
        ordering = ['-release_date']

    def __str__(self):
        return self.title

    def get_average_rating(self):
        ratings = self.ratings.all()
        if not ratings:
            return 0
        return sum(r.rating_value for r in ratings) / len(ratings)
    
    @property
    def average_rating(self):
        return self.get_average_rating()
    
    def days_since_release(self):
        """
        Пример 2: Расчет количества дней с момента выхода фильма/сериала
        
        Метод использует django.utils.timezone для получения текущей даты,
        а затем вычисляет разницу между текущей датой и датой выхода.
        
        Такая функциональность может использоваться для:
        - Определения "новинок" (фильмы, вышедшие менее 30 дней назад)
        - Расчета показателей популярности с учетом времени
        - Формирования специальных подборок типа "Классика" (более 10 лет) или "Новинки"
        """
        if not self.release_date:
            return None
            
        today = timezone.now().date()
        return (today - self.release_date).days
    
    def is_new_release(self):
        """Проверяет, является ли фильм/сериал новинкой (вышел менее 30 дней назад)"""
        days = self.days_since_release()
        if days is None:
            return False
        return days <= 30
    
    def clean(self):
        """Дополнительная валидация модели"""
        super().clean()
        
        if self.title and self.release_date:
            existing_movies = MovieTVShow.objects.filter(
                title__iexact=self.title,
                release_date__year=self.release_date.year
            )
            
            if self.pk:
                existing_movies = existing_movies.exclude(pk=self.pk)
            
            if existing_movies.exists():
                raise ValidationError({
                    'title': f'Фильм/сериал с названием "{self.title}" и годом выпуска {self.release_date.year} уже существует.'
                })
        
        # Валидация соответствия полей типу контента
        if self.type == 'movie':
            if not self.duration:
                raise ValidationError({
                    'duration': 'Для фильмов продолжительность обязательна'
                })
            if self.seasons_count or self.episodes_count:
                raise ValidationError({
                    'seasons_count': 'Фильмы не могут иметь сезоны',
                    'episodes_count': 'Фильмы не могут иметь эпизоды'
                })
        
        elif self.type == 'tv_show':
            if self.duration:
                raise ValidationError({
                    'duration': 'Сериалы не должны иметь общую продолжительность'
                })
            if not self.seasons_count:
                raise ValidationError({
                    'seasons_count': 'Для сериалов количество сезонов обязательно'
                })
    
    def save(self, *args, **kwargs):
        """Переопределяем save для вызова clean"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        """
        Возвращает URL для просмотра деталей фильма/сериала.
        Используется в шаблонах для создания ссылок и редиректов после формы.
        """
        return reverse('movie_detail', kwargs={'pk': self.pk})


class MovieTVShowActorDirector(models.Model):
    """Связующая модель между фильмами/сериалами и актерами/режиссерами"""
    ROLE_CHOICES = (
        ('actor', _('Актер')),
        ('director', _('Режиссер')),
    )
    
    movie_tvshow = models.ForeignKey(
        MovieTVShow, 
        on_delete=models.CASCADE, 
        verbose_name=_('Фильм/Сериал'),
        related_name='actor_director_roles'
    )
    actor_director = models.ForeignKey(
        ActorDirector, 
        on_delete=models.CASCADE, 
        verbose_name=_('Актер/Режиссер'),
        related_name='movie_roles'
    )
    role = models.CharField(_('Роль'), max_length=10, choices=ROLE_CHOICES)
    character_name = models.CharField(_('Имя персонажа'), max_length=255, blank=True)

    class Meta:
        verbose_name = _('Роль в фильме/сериале')
        verbose_name_plural = _('Роли в фильмах/сериалах')
        unique_together = ('movie_tvshow', 'actor_director', 'role')

    def __str__(self):
        return f"{self.actor_director} - {self.get_role_display()} в {self.movie_tvshow}"


class Collection(models.Model):
    """Модель для хранения подборок пользователей"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name=_('Пользователь'),
        related_name='collections',
        null=True,
        blank=True,
        help_text=_('Пользователь не указывается для системных подборок')
    )
    title = models.CharField(_('Название'), max_length=255)
    description = models.TextField(_('Описание'), blank=True)
    is_system = models.BooleanField(_('Системная подборка'), default=False, 
                                    help_text=_('Отметьте, если подборка создана системой, а не пользователем'))
    is_public = models.BooleanField(_('Публичная подборка'), default=True,
                                    help_text=_('Отметьте, если подборка должна быть видна всем пользователям'))
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    movies = models.ManyToManyField(
        MovieTVShow, 
        through='CollectionItem',
        verbose_name=_('Фильмы/Сериалы'),
        related_name='collections'
    )

    class Meta:
        verbose_name = _('Подборка')
        verbose_name_plural = _('Подборки')
        ordering = ['-created_at']

    def __str__(self):
        prefix = '[Системная] ' if self.is_system else ''
        user_suffix = f" ({self.user.username})" if self.user else ""
        return f"{prefix}{self.title}{user_suffix}"
    
    def get_items_count(self):
        """Получить количество элементов в подборке"""
        return self.items.count()
    
    def clean(self):
        """Проверяет корректность данных перед сохранением"""
        if self.is_system:
            # Системные подборки всегда публичны
            self.is_public = True
            
        if self.is_system and self.user:
            # Системные подборки не должны быть привязаны к пользователю
            raise ValidationError({'user': _('Системные подборки не должны быть привязаны к пользователю')})
            
        if not self.is_system and not self.user:
            # Пользовательские подборки должны быть привязаны к пользователю
            raise ValidationError({'user': _('Пользовательские подборки должны быть привязаны к пользователю')})
    
    def save(self, *args, **kwargs):
        """Переопределяем сохранение для автоматической корректировки полей"""
        if self.is_system:
            # Системные подборки всегда публичны
            self.is_public = True
            
        super().save(*args, **kwargs)


class CollectionItem(models.Model):
    """Связующая модель между подборками и фильмами/сериалами"""
    collection = models.ForeignKey(
        Collection, 
        on_delete=models.CASCADE, 
        verbose_name=_('Подборка'),
        related_name='items'
    )
    movie_tvshow = models.ForeignKey(
        MovieTVShow, 
        on_delete=models.CASCADE, 
        verbose_name=_('Фильм/Сериал'),
        related_name='collection_items'
    )
    added_at = models.DateTimeField(_('Дата добавления'), auto_now_add=True)

    class Meta:
        verbose_name = _('Элемент подборки')
        verbose_name_plural = _('Элементы подборок')
        unique_together = ('collection', 'movie_tvshow')

    def __str__(self):
        return f"{self.movie_tvshow.title} в {self.collection.title}"


class UserProfile(models.Model):
    """Модель для хранения профиля пользователя"""
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        verbose_name=_('Пользователь'),
        related_name='profile'
    )
    preferred_genres = models.ManyToManyField(
        Genre, 
        verbose_name=_('Предпочитаемые жанры'),
        related_name='user_profiles',
        blank=True
    )
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)

    class Meta:
        verbose_name = _('Профиль пользователя')
        verbose_name_plural = _('Профили пользователей')

    def __str__(self):
        return f"Профиль пользователя {self.user.username}"


class UserGenrePreference(models.Model):
    """Модель для хранения предпочтений пользователя по жанрам """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name=_('Пользователь'),
        related_name='genre_preferences'
    )
    genre = models.ForeignKey(
        Genre, 
        on_delete=models.CASCADE, 
        verbose_name=_('Жанр'),
        related_name='user_preferences'
    )

    class Meta:
        verbose_name = _('Предпочтение пользователя по жанру')
        verbose_name_plural = _('Предпочтения пользователей по жанрам')
        unique_together = ('user', 'genre')

    def __str__(self):
        return f"{self.user.username} - {self.genre.name}"


class Recommendation(models.Model):
    """Модель для хранения рекомендаций пользователям"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name=_('Пользователь'),
        related_name='recommendations'
    )
    movie_tvshow = models.ForeignKey(
        MovieTVShow, 
        on_delete=models.CASCADE, 
        verbose_name=_('Фильм/Сериал'),
        related_name='recommendations'
    )
    reason_code = models.CharField(_('Код причины'), max_length=50, blank=True)
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)

    class Meta:
        verbose_name = _('Рекомендация')
        verbose_name_plural = _('Рекомендации')
        unique_together = ('user', 'movie_tvshow')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.movie_tvshow.title} для {self.user.username}"


class Rating(models.Model):
    """Модель для хранения оценок фильмов/сериалов"""
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name=_('Пользователь'),
        related_name='ratings'
    )
    movie_tvshow = models.ForeignKey(
        MovieTVShow, 
        on_delete=models.CASCADE, 
        verbose_name=_('Фильм/Сериал'),
        related_name='ratings'
    )
    rating_value = models.IntegerField(_('Оценка'), choices=[(i, i) for i in range(1, 11)])
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)

    class Meta:
        verbose_name = _('Оценка')
        verbose_name_plural = _('Оценки')
        unique_together = ('user', 'movie_tvshow')

    def __str__(self):
        return f"{self.user.username}: {self.rating_value} для {self.movie_tvshow.title}"


class Review(models.Model):
    """Модель для хранения отзывов на фильмы/сериалы"""
    MODERATION_STATUS_CHOICES = (
        ('pending', _('На модерации')),
        ('approved', _('Одобрен')),
        ('rejected', _('Отклонен')),
    )
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name=_('Пользователь'),
        related_name='reviews'
    )
    movie_tvshow = models.ForeignKey(
        MovieTVShow, 
        on_delete=models.CASCADE, 
        verbose_name=_('Фильм/Сериал'),
        related_name='reviews'
    )
    review_text = models.TextField(_('Текст отзыва'))
    likes_count = models.PositiveIntegerField(_('Количество лайков'), default=0)
    dislikes_count = models.PositiveIntegerField(_('Количество дизлайков'), default=0)
    created_at = models.DateTimeField(_('Дата создания'), auto_now_add=True)
    
    # Поля модерации
    moderation_status = models.CharField(
        _('Статус модерации'), 
        max_length=20, 
        choices=MODERATION_STATUS_CHOICES, 
        default='approved',  # По умолчанию одобрен для обратной совместимости
        help_text=_('Статус модерации отзыва')
    )
    moderated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('Модератор'),
        related_name='moderated_reviews',
        help_text=_('Администратор, который модерировал отзыв')
    )
    moderated_at = models.DateTimeField(
        _('Дата модерации'),
        null=True,
        blank=True,
        help_text=_('Дата и время модерации отзыва')
    )
    rejection_reason = models.TextField(
        _('Причина отклонения'),
        blank=True,
        help_text=_('Причина отклонения отзыва администратором')
    )

    class Meta:
        verbose_name = _('Отзыв')
        verbose_name_plural = _('Отзывы')
        ordering = ['-created_at']

    def __str__(self):
        return f"Отзыв от {self.user.username} на {self.movie_tvshow.title}"
    
    def get_likes_count(self):
        """Получить количество лайков из связанной таблицы (точное значение)"""
        return self.votes.filter(vote_type='like').count()
    
    def get_dislikes_count(self):
        """Получить количество дизлайков из связанной таблицы (точное значение)"""
        return self.votes.filter(vote_type='dislike').count()
    
    def get_rating(self):
        """Рассчитать рейтинг отзыва в процентах"""
        likes = self.get_likes_count()
        dislikes = self.get_dislikes_count()
        total = likes + dislikes
        if total == 0:
            return 0
        return (likes / total) * 100
    
    def update_counts(self):
        """Обновить счетчики лайков и дизлайков"""
        self.likes_count = self.get_likes_count()
        self.dislikes_count = self.get_dislikes_count()
        self.save(update_fields=['likes_count', 'dislikes_count'])
    
    def days_since_posted(self):
        """
        Пример 3: Расчет количества дней с момента публикации отзыва
        
        Метод использует django.utils.timezone для получения текущей даты и времени,
        а затем вычисляет разницу между текущим временем и временем создания отзыва.
        
        Такая функциональность может использоваться для:
        - Отображения "свежих" отзывов 
        - Сортировки отзывов по давности
        - Выделения недавних отзывов (например, "Новый отзыв!" для отзывов менее 3 дней)
        - Анализа активности пользователей
        """
        now = timezone.now()
        time_diff = now - self.created_at
        return time_diff.days
    
    def is_fresh(self):
        """Проверяет, является ли отзыв свежим (опубликован менее 7 дней назад)"""
        return self.days_since_posted() < 7
    
    def is_approved(self):
        """Проверяет, одобрен ли отзыв"""
        return self.moderation_status == 'approved'
    
    def is_pending(self):
        """Проверяет, находится ли отзыв на модерации"""
        return self.moderation_status == 'pending'
    
    def is_rejected(self):
        """Проверяет, отклонен ли отзыв"""
        return self.moderation_status == 'rejected'
    
    def approve(self, moderator):
        """Одобрить отзыв"""
        self.moderation_status = 'approved'
        self.moderated_by = moderator
        self.moderated_at = timezone.now()
        self.rejection_reason = ''
        self.save()
    
    def reject(self, moderator, reason=''):
        """Отклонить отзыв"""
        self.moderation_status = 'rejected'
        self.moderated_by = moderator
        self.moderated_at = timezone.now()
        self.rejection_reason = reason
        self.save()
    
    def get_absolute_url(self):
        """
        Возвращает URL для просмотра отзыва.
        Поскольку отзыв отображается на странице фильма/сериала, 
        мы перенаправляем на страницу фильма/сериала с якорем на отзыв.
        """
        return reverse('movie_detail', kwargs={'pk': self.movie_tvshow.pk}) + f'#review-{self.pk}'


class ReviewVote(models.Model):
    """Модель для хранения лайков/дизлайков отзывов"""
    VOTE_CHOICES = (
        ('like', _('Нравится')),
        ('dislike', _('Не нравится')),
    )
    
    review = models.ForeignKey(
        Review, 
        on_delete=models.CASCADE, 
        verbose_name=_('Отзыв'),
        related_name='votes'
    )
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name=_('Пользователь'),
        related_name='review_votes'
    )
    vote_type = models.CharField(_('Тип оценки'), max_length=20, choices=VOTE_CHOICES)
    voted_at = models.DateTimeField(_('Дата оценки'), auto_now_add=True)

    class Meta:
        verbose_name = _('Оценка отзыва')
        verbose_name_plural = _('Оценки отзывов')
        unique_together = ('review', 'user')

    def __str__(self):
        return f"{self.user.username}: {self.get_vote_type_display()} для отзыва {self.review.id}"


class UserWatchlist(models.Model):
    """Модель для хранения списка просмотра пользователя"""
    STATUS_CHOICES = (
        ('to_watch', _('Буду смотреть')),
        ('watching', _('Смотрю')),
        ('watched', _('Просмотрено')),
    )
    
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        verbose_name=_('Пользователь'),
        related_name='watchlist'
    )
    movie_tvshow = models.ForeignKey(
        MovieTVShow, 
        on_delete=models.CASCADE, 
        verbose_name=_('Фильм/Сериал'),
        related_name='in_watchlists'
    )
    status = models.CharField(_('Статус просмотра'), max_length=20, choices=STATUS_CHOICES, default='to_watch')
    progress = models.IntegerField(_('Прогресс (эпизод)'), null=True, blank=True)
    added_at = models.DateTimeField(_('Дата добавления'), auto_now_add=True)

    class Meta:
        verbose_name = _('Элемент списка просмотра')
        verbose_name_plural = _('Элементы списка просмотра')
        unique_together = ('user', 'movie_tvshow')
        ordering = ['-added_at']

    def __str__(self):
        return f"{self.movie_tvshow.title} - {self.get_status_display()} ({self.user.username})"
