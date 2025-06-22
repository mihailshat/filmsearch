from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import MovieTVShow, Genre, Review, Collection, UserProfile
from datetime import date
import re


class MovieTVShowForm(forms.ModelForm):
    """Форма для создания и редактирования фильмов/сериалов с улучшенной валидацией"""
    
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
    
    def __init__(self, *args, **kwargs):
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
    
    def clean_title(self):
        """Валидация названия"""
        title = self.cleaned_data.get('title')
        if not title:
            raise ValidationError("Название обязательно для заполнения")
        
        if len(title) < 2:
            raise ValidationError("Название должно содержать минимум 2 символа")
        
        if len(title) > 255:
            raise ValidationError("Название не может быть длиннее 255 символов")
        
        return title.strip()
    
    def clean_release_date(self):
        """Валидация даты выхода"""
        release_date = self.cleaned_data.get('release_date')
        if not release_date:
            raise ValidationError("Дата выхода обязательна для заполнения")
        
        if release_date > date.today():
            # разрешаем будущие даты, но с предупреждением
            pass
        
        if release_date.year < 1888:  
            raise ValidationError("Дата выхода не может быть раньше 1888 года")
        
        return release_date
    
    def clean_duration(self):
        """Валидация продолжительности"""
        duration = self.cleaned_data.get('duration')
        movie_type = self.cleaned_data.get('type')
        
        if movie_type == 'movie' and not duration:
            raise ValidationError("Для фильмов продолжительность обязательна")
        
        if duration and duration <= 0:
            raise ValidationError("Продолжительность должна быть положительным числом")
        
        if duration and duration > 1000:  
            raise ValidationError("Продолжительность не может превышать 1000 минут")
        
        return duration
    
    def clean_seasons_count(self):
        """Валидация количества сезонов"""
        seasons_count = self.cleaned_data.get('seasons_count')
        movie_type = self.cleaned_data.get('type')
        
        if movie_type == 'tv_show' and not seasons_count:
            raise ValidationError("Для сериалов количество сезонов обязательно")
        
        if seasons_count and seasons_count <= 0:
            raise ValidationError("Количество сезонов должно быть положительным числом")
        
        if seasons_count and seasons_count > 100:
            raise ValidationError("Количество сезонов не может превышать 100")
        
        return seasons_count
    
    def clean_episodes_count(self):
        """Валидация количества эпизодов"""
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
    
    def clean_end_date(self):
        """Валидация даты завершения"""
        end_date = self.cleaned_data.get('end_date')
        release_date = self.cleaned_data.get('release_date')
        
        if end_date and release_date and end_date < release_date:
            raise ValidationError("Дата завершения не может быть раньше даты выхода")
        
        return end_date
    
    def clean_genres(self):
        """Валидация жанров"""
        genres = self.cleaned_data.get('genres')
        
        if not genres:
            raise ValidationError("Необходимо выбрать хотя бы один жанр")
        
        if len(genres) > 5:
            raise ValidationError("Нельзя выбрать больше 5 жанров")
        
        return genres
    
    def clean(self):
        """Общая валидация формы"""
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
    """Форма для создания и редактирования жанров"""
    
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
    
    def clean_name(self):
        """Валидация названия жанра"""
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
    """Форма для создания и редактирования отзывов"""
    
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
    
    def clean_review_text(self):
        """Валидация текста отзыва"""
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
    """Форма для создания и редактирования подборок"""
    
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
    
    def clean_title(self):
        title = self.cleaned_data.get('title')
        if len(title) < 3:
            raise forms.ValidationError('Название подборки должно содержать минимум 3 символа.')
        return title


class UserProfileForm(forms.ModelForm):
    """Форма для редактирования профиля пользователя"""
    
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
        required=False,
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
            'preferred_genres': 'Предпочитаемые жанры'
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['first_name'].initial = user.first_name
            self.fields['last_name'].initial = user.last_name
            self.fields['email'].initial = user.email
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        
        if commit:
            # Сохраняем данные пользователя
            user = profile.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            user.save()
            
            # Сохраняем профиль
            profile.save()
            self.save_m2m()
        
        return profile 


class CustomUserCreationForm(UserCreationForm):
    """Форма регистрации с расширенной валидацией"""
    
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
    
    def clean_username(self):
        """Валидация имени пользователя"""
        username = self.cleaned_data.get('username')
        
        if not username:
            raise ValidationError("Имя пользователя обязательно")
        
        if len(username) < 3:
            raise ValidationError("Имя пользователя должно содержать минимум 3 символа")
        
        if len(username) > 30:
            raise ValidationError("Имя пользователя не может быть длиннее 30 символов")
        
        if not re.match(r'^[\w.@+-]+$', username):
            raise ValidationError("Имя пользователя может содержать только буквы, цифры и символы @/./+/-/_")
        
        if User.objects.filter(username=username).exists():
            raise ValidationError("Пользователь с таким именем уже существует")
        
        return username
    
    def clean_email(self):
        """Валидация email"""
        email = self.cleaned_data.get('email')
        
        if not email:
            raise ValidationError("Email обязателен")
        
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            raise ValidationError("Введите корректный email адрес")
        
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким email уже существует")
        
        return email
    
    def clean_password1(self):
        """Валидация пароля"""
        password = self.cleaned_data.get('password1')
        
        if not password:
            raise ValidationError("Пароль обязателен")
        
        if len(password) < 8:
            raise ValidationError("Пароль должен содержать минимум 8 символов")
        
        if not re.search(r'\d', password):
            raise ValidationError("Пароль должен содержать хотя бы одну цифру")
        
        if not re.search(r'[a-zA-Z]', password):
            raise ValidationError("Пароль должен содержать хотя бы одну букву")
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            raise ValidationError("Пароль должен содержать хотя бы один специальный символ")
        
        return password
    
    def clean(self):
        """Общая валидация формы"""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError("Пароли не совпадают")
        
        return cleaned_data 