from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from typing import Any, Dict, Optional, List
from .models import MovieTVShow, Genre, Review, Collection, UserProfile
from datetime import date
import re


class MovieTVShowForm(forms.ModelForm):
    """
    Форма для создания и редактирования фильмов/сериалов с улучшенной валидацией.
    
    Предоставляет комплексную валидацию данных для фильмов и сериалов,
    включая проверку соответствия полей типу контента.
    """
    
    class Meta:
        model = MovieTVShow
        fields = [
            'title', 'description', 'type', 'release_date', 'duration',
            'seasons_count', 'episodes_count', 'end_date', 'status',
            'age_restriction', 'poster_url', 'country', 'genres'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название фильма/сериала'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Описание сюжета...'
            }),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'release_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'duration': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Продолжительность в минутах'
            }),
            'seasons_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Количество сезонов'
            }),
            'episodes_count': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Общее количество эпизодов'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'age_restriction': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: 16+, 18+'
            }),
            'poster_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com/poster.jpg'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Страна производства'
            }),
            'genres': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            })
        }
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Инициализация формы с настройкой полей.
        
        Устанавливает обязательные поля и добавляет help_text.
        """
        super().__init__(*args, **kwargs)
        # Делаем некоторые поля обязательными
        self.fields['title'].required = True
        self.fields['type'].required = True
        self.fields['release_date'].required = True
        self.fields['genres'].required = True
        
        # Добавляем help_text
        self.fields['duration'].help_text = "Только для фильмов"
        self.fields['seasons_count'].help_text = "Только для сериалов"
        self.fields['episodes_count'].help_text = "Только для сериалов"
        self.fields['end_date'].help_text = "Дата завершения для сериалов"
        self.fields['status'].help_text = "Статус для сериалов"
    
    def clean_title(self) -> str:
        """
        Валидация названия.
        
        Returns:
            str: Очищенное название
            
        Raises:
            ValidationError: При нарушении правил валидации
        """
        title = self.cleaned_data.get('title')
        if not title:
            raise ValidationError("Название обязательно для заполнения")
        
        if len(title) < 2:
            raise ValidationError("Название должно содержать минимум 2 символа")
        
        if len(title) > 255:
            raise ValidationError("Название не может быть длиннее 255 символов")
        
        return title.strip()
    
    def clean_release_date(self) -> date:
        """
        Валидация даты выхода.
        
        Returns:
            date: Валидная дата выхода
            
        Raises:
            ValidationError: При нарушении правил валидации
        """
        release_date = self.cleaned_data.get('release_date')
        if not release_date:
            raise ValidationError("Дата выхода обязательна для заполнения")
        
        if release_date > date.today():
            # разрешаем будущие даты, но с предупреждением
            pass
        
        if release_date.year < 1888:  
            raise ValidationError("Дата выхода не может быть раньше 1888 года")
        
        return release_date
    
    def clean_duration(self) -> Optional[int]:
        """
        Валидация продолжительности.
        
        Returns:
            Optional[int]: Валидная продолжительность или None
            
        Raises:
            ValidationError: При нарушении правил валидации
        """
        duration = self.cleaned_data.get('duration')
        movie_type = self.cleaned_data.get('type')
        
        if movie_type == 'movie' and not duration:
            raise ValidationError("Для фильмов продолжительность обязательна")
        
        if duration and duration <= 0:
            raise ValidationError("Продолжительность должна быть положительным числом")
        
        if duration and duration > 1000:  
            raise ValidationError("Продолжительность не может превышать 1000 минут")
        
        return duration
    
    def clean_seasons_count(self) -> Optional[int]:
        """
        Валидация количества сезонов.
        
        Returns:
            Optional[int]: Валидное количество сезонов или None
            
        Raises:
            ValidationError: При нарушении правил валидации
        """
        seasons_count = self.cleaned_data.get('seasons_count')
        movie_type = self.cleaned_data.get('type')
        
        if movie_type == 'tv_show' and not seasons_count:
            raise ValidationError("Для сериалов количество сезонов обязательно")
        
        if seasons_count and seasons_count <= 0:
            raise ValidationError("Количество сезонов должно быть положительным числом")
        
        if seasons_count and seasons_count > 100:
            raise ValidationError("Количество сезонов не может превышать 100")
        
        return seasons_count
    
    def clean_episodes_count(self) -> Optional[int]:
        """
        Валидация количества эпизодов.
        
        Returns:
            Optional[int]: Валидное количество эпизодов или None
            
        Raises:
            ValidationError: При нарушении правил валидации
        """
        episodes_count = self.cleaned_data.get('episodes_count')
        seasons_count = self.cleaned_data.get('seasons_count')
        movie_type = self.cleaned_data.get('type')
        
        if movie_type == 'tv_show' and not episodes_count:
            raise ValidationError("Для сериалов количество эпизодов обязательно")
        
        if episodes_count and episodes_count <= 0:
            raise ValidationError("Количество эпизодов должно быть положительным числом")
        
        if episodes_count and seasons_count and episodes_count < seasons_count:
            raise ValidationError("Количество эпизодов не может быть меньше количества сезонов")
        
        return episodes_count
    
    def clean_end_date(self) -> Optional[date]:
        """
        Валидация даты завершения.
        
        Returns:
            Optional[date]: Валидная дата завершения или None
            
        Raises:
            ValidationError: При нарушении правил валидации
        """
        end_date = self.cleaned_data.get('end_date')
        release_date = self.cleaned_data.get('release_date')
        
        if end_date and release_date and end_date < release_date:
            raise ValidationError("Дата завершения не может быть раньше даты выхода")
        
        return end_date
    
    def clean_genres(self) -> List[Genre]:
        """
        Валидация жанров.
        
        Returns:
            List[Genre]: Список валидных жанров
            
        Raises:
            ValidationError: При нарушении правил валидации
        """
        genres = self.cleaned_data.get('genres')
        
        if not genres:
            raise ValidationError("Необходимо выбрать хотя бы один жанр")
        
        if len(genres) > 5:
            raise ValidationError("Нельзя выбрать больше 5 жанров")
        
        return genres
    
    def clean(self) -> Dict[str, Any]:
        """
        Общая валидация формы.
        
        Проверяет соответствие полей типу контента.
        
        Returns:
            Dict[str, Any]: Очищенные данные формы
            
        Raises:
            ValidationError: При нарушении правил валидации
        """
        cleaned_data = super().clean()
        movie_type = cleaned_data.get('type')
        duration = cleaned_data.get('duration')
        seasons_count = cleaned_data.get('seasons_count')
        episodes_count = cleaned_data.get('episodes_count')
        
        if movie_type == 'movie':
            if seasons_count or episodes_count:
                raise ValidationError("Фильмы не могут иметь сезоны или эпизоды")
        
        elif movie_type == 'tv_show':
            if duration:
                # предупреждение, но не ошибка
                pass
        
        return cleaned_data


class GenreForm(forms.ModelForm):
    """
    Форма для создания и редактирования жанров.
    
    Предоставляет валидацию названий жанров с проверкой уникальности.
    """
    
    class Meta:
        model = Genre
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название жанра'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Описание жанра (необязательно)'
            })
        }
    
    def clean_name(self) -> str:
        """
        Валидация названия жанра.
        
        Returns:
            str: Очищенное название жанра
            
        Raises:
            ValidationError: При нарушении правил валидации
        """
        name = self.cleaned_data.get('name')
        
        if not name:
            raise ValidationError("Название жанра обязательно")
        
        if len(name) < 2:
            raise ValidationError("Название жанра должно содержать минимум 2 символа")
        
        if len(name) > 100:
            raise ValidationError("Название жанра не может быть длиннее 100 символов")
        
        existing_genre = Genre.objects.filter(name__iexact=name)
        if self.instance.pk:
            existing_genre = existing_genre.exclude(pk=self.instance.pk)
        
        if existing_genre.exists():
            raise ValidationError(f"Жанр с названием '{name}' уже существует")
        
        return name.strip().title()  


class ReviewForm(forms.ModelForm):
    """
    Форма для создания и редактирования отзывов.
    
    Предоставляет валидацию текста отзывов с проверкой длины и разнообразия.
    """
    
    class Meta:
        model = Review
        fields = ['review_text']
        widgets = {
            'review_text': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Напишите ваш отзыв о фильме/сериале...'
            })
        }
    
    def clean_review_text(self) -> str:
        """
        Валидация текста отзыва.
        
        Returns:
            str: Очищенный текст отзыва
            
        Raises:
            ValidationError: При нарушении правил валидации
        """
        review_text = self.cleaned_data.get('review_text')
        
        if not review_text:
            raise ValidationError("Текст отзыва обязателен")
        
        if len(review_text.strip()) < 10:
            raise ValidationError("Отзыв должен содержать минимум 10 символов")
        
        if len(review_text) > 5000:
            raise ValidationError("Отзыв не может быть длиннее 5000 символов")
        
        if len(set(review_text.lower().replace(' ', ''))) < 3:
            raise ValidationError("Отзыв должен содержать разнообразные символы")
        
        return review_text.strip()


class CollectionForm(forms.ModelForm):
    """
    Форма для создания и редактирования подборок.
    
    Предоставляет валидацию данных подборок с настройкой публичности.
    """
    
    class Meta:
        model = Collection
        fields = ['title', 'description', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Название подборки'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Описание подборки (необязательно)'
            }),
            'is_public': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'title': 'Название подборки',
            'description': 'Описание',
            'is_public': 'Публичная подборка'
        }
        help_texts = {
            'is_public': 'Если отмечено, подборка будет видна всем пользователям'
        }
    
    def clean_title(self) -> str:
        """
        Валидация названия подборки.
        
        Returns:
            str: Очищенное название подборки
            
        Raises:
            ValidationError: При нарушении правил валидации
        """
        title = self.cleaned_data.get('title')
        if len(title) < 3:
            raise forms.ValidationError('Название подборки должно содержать минимум 3 символа.')
        return title


class UserProfileForm(forms.ModelForm):
    """
    Форма для редактирования профиля пользователя.
    
    Расширяет стандартную форму пользователя дополнительными полями
    для настройки предпочтений.
    """
    
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Имя'
        }),
        label='Имя'
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Фамилия'
        }),
        label='Фамилия'
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'email@example.com'
        }),
        label='Email'
    )
    
    class Meta:
        model = UserProfile
        fields = ['preferred_genres']
        widgets = {
            'preferred_genres': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'preferred_genres': 'Любимые жанры'
        }
        help_texts = {
            'preferred_genres': 'Выберите жанры для персонализации рекомендаций'
        }
    
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Инициализация формы с настройкой полей пользователя.
        """
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
    
    def save(self, commit: bool = True) -> UserProfile:
        """
        Сохранение формы с обновлением данных пользователя.
        
        Args:
            commit: Сохранять ли изменения в базе данных
            
        Returns:
            UserProfile: Обновленный профиль пользователя
        """
        profile = super().save(commit=False)
        
        if commit and self.instance and self.instance.user:
            user = self.instance.user
            user.first_name = self.cleaned_data.get('first_name', '')
            user.last_name = self.cleaned_data.get('last_name', '')
            user.email = self.cleaned_data.get('email', '')
            user.save()
            profile.save()
        
        return profile 


class CustomUserCreationForm(UserCreationForm):
    """
    Форма регистрации с расширенной валидацией.
    
    Расширяет стандартную форму создания пользователя дополнительными
    полями и валидацией.
    """
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'email@example.com'
        }),
        label='Email'
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Имя'
        }),
        label='Имя'
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Фамилия'
        }),
        label='Фамилия'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Имя пользователя'
            })
        }
    
    def clean_username(self) -> str:
        """
        Валидация имени пользователя.
        
        Returns:
            str: Очищенное имя пользователя
            
        Raises:
            ValidationError: При нарушении правил валидации
        """
        username = self.cleaned_data.get('username')
        
        if not username:
            raise ValidationError("Имя пользователя обязательно")
        
        if len(username) < 3:
            raise ValidationError("Имя пользователя должно содержать минимум 3 символа")
        
        if len(username) > 30:
            raise ValidationError("Имя пользователя не может быть длиннее 30 символов")
        
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            raise ValidationError("Имя пользователя может содержать только буквы, цифры и знак подчеркивания")
        
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("Пользователь с таким именем уже существует")
        
        return username.lower()
    
    def clean_email(self) -> str:
        """
        Валидация email.
        
        Returns:
            str: Очищенный email
            
        Raises:
            ValidationError: При нарушении правил валидации
        """
        email = self.cleaned_data.get('email')
        
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Пользователь с таким email уже существует")
        
        return email.lower()
    
    def clean_password1(self) -> str:
        """
        Валидация пароля.
        
        Returns:
            str: Очищенный пароль
            
        Raises:
            ValidationError: При нарушении правил валидации
        """
        password = self.cleaned_data.get('password1')
        
        if len(password) < 8:
            raise ValidationError("Пароль должен содержать минимум 8 символов")
        
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Пароль должен содержать хотя бы одну заглавную букву")
        
        if not re.search(r'[a-z]', password):
            raise ValidationError("Пароль должен содержать хотя бы одну строчную букву")
        
        if not re.search(r'\d', password):
            raise ValidationError("Пароль должен содержать хотя бы одну цифру")
        
        return password
    
    def clean(self) -> Dict[str, Any]:
        """
        Общая валидация формы.
        
        Returns:
            Dict[str, Any]: Очищенные данные формы
            
        Raises:
            ValidationError: При нарушении правил валидации
        """
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError("Пароли не совпадают")
        
        return cleaned_data 