from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils import timezone
from django.urls import reverse, reverse_lazy
from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponseForbidden, Http404
from .models import MovieTVShow, ActorDirector, Review, Genre, Collection, UserProfile, Rating, Recommendation
from django.db.models import Avg, Count, Sum, Max, Min, F, ExpressionWrapper, FloatField, Q
from .forms import MovieTVShowForm, GenreForm, ReviewForm, CollectionForm, UserProfileForm, CustomUserCreationForm
from .admin import admin_movie_pdf

def is_admin(user):
    """Проверяет, является ли пользователь администратором"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)

def is_regular_user(user):
    """Проверяет, является ли пользователь обычным зарегистрированным пользователем"""
    return user.is_authenticated


def register_view(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Создаем профиль пользователя
            UserProfile.objects.create(user=user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Аккаунт создан для {username}! Теперь вы можете войти.')
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile_view(request):
    """Профиль пользователя"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # статистика 
    user_reviews = Review.objects.filter(user=request.user)
    user_ratings = Rating.objects.filter(user=request.user)
    user_recommendations = Recommendation.objects.filter(user=request.user)
    
    context = {
        'profile': profile,
        'reviews_count': user_reviews.count(),
        'ratings_count': user_ratings.count(),
        'recommendations_count': user_recommendations.count(),
        'recent_reviews': user_reviews[:5],
        'recent_ratings': user_ratings[:5],
        'is_admin': is_admin(request.user),
    }
    return render(request, 'movies/profile.html', context)

@login_required
def profile_edit_view(request):
    """Редактирование профиля пользователя"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile, user=request.user)
    
    context = {
        'form': form,
        'profile': profile,
    }
    return render(request, 'movies/profile_edit.html', context)


class AdminRequiredMixin(UserPassesTestMixin):
    """Миксин для проверки прав администратора"""
    def test_func(self):
        return is_admin(self.request.user)
    
    def handle_no_permission(self):
        messages.error(self.request, 'У вас нет прав для выполнения этого действия.')
        return redirect('movie_list')

class MovieTVShowCreateView(AdminRequiredMixin, CreateView):
    """Создание фильма/сериала (только для админов)"""
    model = MovieTVShow
    form_class = MovieTVShowForm
    template_name = 'movies/movie_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить фильм/сериал'
        context['submit_text'] = 'Создать'
        context['is_admin_action'] = True
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'{form.instance.get_type_display()} "{form.instance.title}" успешно создан!')
        return response

class MovieTVShowUpdateView(AdminRequiredMixin, UpdateView):
    """Редактирование фильма/сериала (только для админов)"""
    model = MovieTVShow
    form_class = MovieTVShowForm
    template_name = 'movies/movie_form.html'
    
    def get_queryset(self):
        return MovieTVShow.objects.select_related().prefetch_related('genres')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактировать {self.object.get_type_display().lower()}'
        context['submit_text'] = 'Сохранить изменения'
        context['is_edit'] = True
        context['is_admin_action'] = True
        return context

class MovieTVShowDeleteView(AdminRequiredMixin, DeleteView):
    """Удаление фильма/сериала (только для админов)"""
    model = MovieTVShow
    template_name = 'movies/movie_confirm_delete.html'
    success_url = reverse_lazy('movie_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin_action'] = True
        return context
    
    def delete(self, request, *args, **kwargs):
        movie = self.get_object()
        movie_title = movie.title
        movie_type = movie.get_type_display()
        
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'{movie_type} "{movie_title}" успешно удален!')
        return response


class GenreCreateView(AdminRequiredMixin, CreateView):
    """Создание жанра (только для админов)"""
    model = Genre
    form_class = GenreForm
    template_name = 'movies/genre_form.html'
    success_url = reverse_lazy('genre_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавить жанр'
        context['submit_text'] = 'Создать жанр'
        context['is_admin_action'] = True
        return context

class GenreUpdateView(AdminRequiredMixin, UpdateView):
    """Редактирование жанра (только для админов)"""
    model = Genre
    form_class = GenreForm
    template_name = 'movies/genre_form.html'
    success_url = reverse_lazy('genre_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактировать жанр "{self.object.name}"'
        context['submit_text'] = 'Сохранить изменения'
        context['is_edit'] = True
        context['is_admin_action'] = True
        return context

class GenreDeleteView(AdminRequiredMixin, DeleteView):
    """Удаление жанра (только для админов)"""
    model = Genre
    template_name = 'movies/genre_confirm_delete.html'
    success_url = reverse_lazy('genre_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin_action'] = True
        return context


class CollectionListView(ListView):
    """Список подборок"""
    model = Collection
    template_name = 'movies/collection_list.html'
    context_object_name = 'collections'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Collection.objects.annotate(
            items_count=Count('items')
        ).order_by('-created_at')
        
        # Показываем публичные подборки и подборки текущего пользователя
        if self.request.user.is_authenticated:
            queryset = queryset.filter(
                Q(is_public=True) | Q(user=self.request.user)
            )
        else:
            queryset = queryset.filter(is_public=True)
        
        return queryset

class CollectionDetailView(DetailView):
    """Детальный просмотр подборки"""
    model = Collection
    template_name = 'movies/collection_detail.html'
    context_object_name = 'collection'
    
    def get_queryset(self):
        return Collection.objects.prefetch_related('items__movie_tvshow__genres')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        collection = self.object
        
        # Проверяем права доступа
        if not collection.is_public and collection.user != self.request.user:
            if not is_admin(self.request.user):
                raise Http404("Подборка не найдена")
        
        context['can_edit'] = (
            self.request.user == collection.user or 
            is_admin(self.request.user)
        )
        return context

class CollectionCreateView(LoginRequiredMixin, CreateView):
    """Создание подборки (для авторизованных пользователей)"""
    model = Collection
    form_class = CollectionForm
    template_name = 'movies/collection_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Создать подборку'
        context['submit_text'] = 'Создать'
        return context
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.is_system = False
        response = super().form_valid(form)
        messages.success(self.request, f'Подборка "{form.instance.title}" успешно создана!')
        return response

class CollectionUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование подборки (автор или админ)"""
    model = Collection
    form_class = CollectionForm
    template_name = 'movies/collection_form.html'
    
    def get_queryset(self):
        # Пользователь может редактировать только свои подборки, админ - любые
        if is_admin(self.request.user):
            return Collection.objects.all()
        return Collection.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f'Редактировать подборку "{self.object.title}"'
        context['submit_text'] = 'Сохранить изменения'
        context['is_edit'] = True
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Подборка "{form.instance.title}" успешно обновлена!')
        return response

class CollectionDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление подборки (автор или админ)"""
    model = Collection
    template_name = 'movies/collection_confirm_delete.html'
    success_url = reverse_lazy('collection_list')
    
    def get_queryset(self):
        # Пользователь может удалять только свои подборки, админ - любые
        if is_admin(self.request.user):
            return Collection.objects.all()
        return Collection.objects.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        collection = self.get_object()
        collection_title = collection.title
        
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Подборка "{collection_title}" успешно удалена!')
        return response


class ReviewCreateView(LoginRequiredMixin, CreateView):
    """Создание отзыва (для авторизованных пользователей)"""
    model = Review
    form_class = ReviewForm
    template_name = 'movies/review_form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie_id = self.kwargs.get('movie_id')
        context['movie'] = get_object_or_404(MovieTVShow, pk=movie_id)
        return context
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        movie_id = self.kwargs.get('movie_id')
        form.instance.movie_tvshow = get_object_or_404(MovieTVShow, pk=movie_id)
        
        existing_review = Review.objects.filter(
            user=self.request.user,
            movie_tvshow=form.instance.movie_tvshow
        ).first()
        
        if existing_review:
            messages.error(self.request, 'Вы уже оставили отзыв на этот фильм/сериал.')
            return redirect('movie_detail', pk=movie_id)
        
        response = super().form_valid(form)
        messages.success(self.request, 'Ваш отзыв успешно добавлен!')
        return response

class ReviewUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование отзыва (автор или админ)"""
    model = Review
    form_class = ReviewForm
    template_name = 'movies/review_form.html'
    
    def get_queryset(self):
        if is_admin(self.request.user):
            return Review.objects.all()
        return Review.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['movie'] = self.object.movie_tvshow
        context['is_edit'] = True
        return context

class ReviewDeleteView(LoginRequiredMixin, DeleteView):
    """Удаление отзыва (автор или админ)"""
    model = Review
    template_name = 'movies/review_confirm_delete.html'
    
    def get_queryset(self):
        if is_admin(self.request.user):
            return Review.objects.all()
        return Review.objects.filter(user=self.request.user)
    
    def get_success_url(self):
        return reverse('movie_detail', kwargs={'pk': self.object.movie_tvshow.pk})
    
    def delete(self, request, *args, **kwargs):
        review = self.get_object()
        movie = review.movie_tvshow
        
        response = super().delete(request, *args, **kwargs)
        messages.success(request, 'Отзыв успешно удален!')
        return response


@login_required
def add_rating(request, movie_id):
    """Добавление/обновление рейтинга"""
    if request.method == 'POST':
        movie = get_object_or_404(MovieTVShow, pk=movie_id)
        rating_value = request.POST.get('rating_value')
        
        if rating_value and 1 <= int(rating_value) <= 10:
            rating, created = Rating.objects.update_or_create(
                user=request.user,
                movie_tvshow=movie,
                defaults={'rating_value': int(rating_value)}
            )
            
            action = 'добавлена' if created else 'обновлена'
            messages.success(request, f'Ваша оценка {action}!')
        else:
            messages.error(request, 'Некорректная оценка. Выберите от 1 до 10.')
    
    return redirect('movie_detail', pk=movie_id)


@login_required
def recommendations_view(request):
    """Персональные рекомендации пользователя"""
    recommendations = Recommendation.objects.filter(
        user=request.user
    ).select_related('movie_tvshow').prefetch_related(
        'movie_tvshow__genres'
    ).order_by('-created_at')
    
    context = {
        'recommendations': recommendations,
        'user': request.user,
    }
    return render(request, 'movies/recommendations.html', context)

@user_passes_test(is_admin)
def generate_recommendations(request):
    """Генерация рекомендаций (только для админов)"""
    if request.method == 'POST':
        users = User.objects.filter(is_active=True)
        
        for user in users:
            # Получаем любимые жанры пользователя на основе его оценок
            user_ratings = Rating.objects.filter(user=user, rating_value__gte=8)
            favorite_genres = Genre.objects.filter(
                movies__ratings__in=user_ratings
            ).annotate(
                avg_rating=Avg('movies__ratings__rating_value')
            ).order_by('-avg_rating')[:3]
            
            # Находим фильмы этих жанров, которые пользователь еще не оценивал
            for genre in favorite_genres:
                recommended_movies = MovieTVShow.objects.filter(
                    genres=genre
                ).exclude(
                    ratings__user=user
                ).annotate(
                    avg_rating=Avg('ratings__rating_value')
                ).filter(avg_rating__gte=7).order_by('-avg_rating')[:2]
                
                for movie in recommended_movies:
                    Recommendation.objects.get_or_create(
                        user=user,
                        movie_tvshow=movie,
                        defaults={'reason_code': f'genre_{genre.name}'}
                    )
        
        messages.success(request, 'Рекомендации успешно сгенерированы для всех пользователей!')
    
    return redirect('admin_dashboard')


@user_passes_test(is_admin)
def admin_dashboard(request):
    """Панель администратора"""
    # Статистика
    stats = {
        'total_movies': MovieTVShow.objects.filter(type='movie').count(),
        'total_tv_shows': MovieTVShow.objects.filter(type='tv_show').count(),
        'total_users': User.objects.filter(is_active=True).count(),
        'total_reviews': Review.objects.count(),
        'total_ratings': Rating.objects.count(),
        'total_genres': Genre.objects.count(),
    }
    
    # Последние добавленные фильмы
    recent_movies = MovieTVShow.objects.order_by('-created_at')[:5]
    
    # Последние отзывы
    recent_reviews = Review.objects.select_related(
        'user', 'movie_tvshow'
    ).order_by('-created_at')[:5]
    
    # Топ пользователей по активности
    active_users = User.objects.annotate(
        reviews_count=Count('reviews'),
        ratings_count=Count('ratings')
    ).order_by('-reviews_count', '-ratings_count')[:5]
    
    # === ДЕМОНСТРАЦИЯ values() ===
    # Получаем краткую информацию о фильмах для экспорта/отчетов
    movies_summary = MovieTVShow.objects.values(
        'title', 'type', 'release_date', 'country'
    ).order_by('-created_at')[:10]
    
    # Получаем информацию о жанрах с количеством фильмов
    genres_info = Genre.objects.values(
        'name', 'description'
    ).annotate(
        movies_count=Count('movies')
    ).order_by('-movies_count')[:5]
    
    # === ДЕМОНСТРАЦИЯ values_list() ===
    # Получаем только названия активных пользователей для быстрого списка
    active_usernames = User.objects.filter(
        is_active=True
    ).values_list('username', flat=True).order_by('username')[:10]
    
    # Получаем пары (название фильма, тип) для отчетов
    movie_type_pairs = MovieTVShow.objects.values_list(
        'title', 'type'
    ).order_by('-created_at')[:10]
    
    # Получаем ID всех жанров для массовых операций
    genre_ids = Genre.objects.values_list('id', flat=True)
    
    context = {
        'stats': stats,
        'recent_movies': recent_movies,
        'recent_reviews': recent_reviews,
        'active_users': active_users,
        'movies_summary': list(movies_summary),
        'genres_info': list(genres_info), 
        'active_usernames': list(active_usernames),
        'movie_type_pairs': list(movie_type_pairs),
        'total_genre_ids': len(genre_ids),
    }
    
    return render(request, 'movies/admin_dashboard.html', context)


def is_superuser(user):
    """Проверяет, является ли пользователь суперпользователем"""
    return user.is_authenticated and user.is_superuser


@user_passes_test(is_superuser)
def manage_users(request):
    """Управление пользователями (только для суперпользователей)"""
    
    users = User.objects.annotate(
        reviews_count=Count('review'),
        ratings_count=Count('rating')
    ).order_by('username')
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        
        try:
            user = User.objects.get(id=user_id)
            
            if action == 'make_admin':
                user.is_staff = True
                user.save()
                messages.success(request, f'Пользователь {user.username} назначен администратором!')
                
            elif action == 'remove_admin':
                if user.is_superuser:
                    messages.error(request, 'Нельзя снять права с суперпользователя!')
                else:
                    user.is_staff = False
                    user.save()
                    messages.success(request, f'У пользователя {user.username} сняты права администратора!')
                    
            elif action == 'toggle_active':
                user.is_active = not user.is_active
                user.save()
                status = 'активирован' if user.is_active else 'деактивирован'
                messages.success(request, f'Пользователь {user.username} {status}!')
                
        except User.DoesNotExist:
            messages.error(request, 'Пользователь не найден!')
        
        return redirect('manage_users')
    
    context = {
        'users': users,
        'total_users': users.count(),
        'admin_users': users.filter(is_staff=True).count(),
        'superusers': users.filter(is_superuser=True).count(),
        'active_users': users.filter(is_active=True).count(),
    }
    
    return render(request, 'movies/manage_users.html', context)


class MovieListView(ListView):
    model = MovieTVShow
    template_name = 'movies/movie_list.html'
    context_object_name = 'movies'
    paginate_by = 10
    
    def get_queryset(self):
        """Оптимизированный запрос с использованием select_related и prefetch_related"""
        queryset = MovieTVShow.objects.select_related().prefetch_related(
            'genres', 'actors_directors'
        ).annotate(
            avg_rating=Avg('ratings__rating_value'),
            reviews_count=Count('reviews')
        )
        
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__contains=search_query) |
                Q(description__contains=search_query) |
                Q(country__contains=search_query)
            )
        
        genre_filter = self.request.GET.get('genre')
        if genre_filter:
            queryset = queryset.filter(
                genres__name__contains=genre_filter 
            ).distinct()
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['new_releases'] = MovieTVShow.objects.select_related().prefetch_related(
            'genres'
        ).filter(
            release_date__gte=timezone.now().date() - timezone.timedelta(days=30)
        ).order_by('-release_date')[:5]
        
        context['is_admin'] = is_admin(self.request.user)
        context['is_authenticated'] = self.request.user.is_authenticated
        
        return context

class MovieDetailView(DetailView):
    model = MovieTVShow
    template_name = 'movies/movie_detail.html'
    context_object_name = 'movie'
    
    def get_queryset(self):
        return MovieTVShow.objects.select_related().prefetch_related(
            'genres', 'actors_directors', 'reviews__user', 'ratings'
        ).annotate(
            avg_rating=Avg('ratings__rating_value'),
            reviews_count=Count('reviews')
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        movie = self.object
        
        reviews = movie.reviews.select_related('user').order_by('-created_at')
        context['reviews'] = reviews
        
        user_review = None
        user_rating = None
        
        if self.request.user.is_authenticated:
            user_review = reviews.filter(user=self.request.user).first()
            user_rating = movie.ratings.filter(user=self.request.user).first()
        
        context['user_review'] = user_review
        context['user_rating'] = user_rating
        context['is_admin'] = is_admin(self.request.user)
        context['is_authenticated'] = self.request.user.is_authenticated
        context['can_review'] = (
            self.request.user.is_authenticated and 
            not user_review
        )
        
        return context

class ActorDirectorListView(ListView):
    """Список актеров и режиссеров"""
    model = ActorDirector
    template_name = 'movies/actor_list.html'
    context_object_name = 'actors'
    paginate_by = 20
    
    def get_queryset(self):
        return ActorDirector.objects.annotate(
            movies_count=Count('movies')
        ).order_by('name')

class ActorDirectorDetailView(DetailView):
    model = ActorDirector
    template_name = 'movies/actor_director_detail.html'
    context_object_name = 'person'
    
    def get_queryset(self):
        return ActorDirector.objects.prefetch_related('movies__genres')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        person = self.object
        
        movies = person.movies.select_related().prefetch_related('genres').annotate(
            avg_rating=Avg('ratings__rating_value'),
            reviews_count=Count('reviews')
        ).order_by('-release_date')
        
        context['movies'] = movies
        return context


def statistics_view(request):
    """Статистика сайта"""
    stats = {
        'total_movies': MovieTVShow.objects.filter(type='movie').count(),
        'total_tv_shows': MovieTVShow.objects.filter(type='tv_show').count(),
        'total_users': User.objects.filter(is_active=True).count(),
        'total_reviews': Review.objects.count(),
        'total_ratings': Rating.objects.count(),
        'total_genres': Genre.objects.count(),
        'total_actors': ActorDirector.objects.count(),
        'total_collections': Collection.objects.count(),
    }
    
    # Топ жанров по количеству фильмов
    top_genres = Genre.objects.annotate(
        movies_count=Count('movies')
    ).order_by('-movies_count')[:10]
    
    # Топ фильмов по рейтингу
    top_movies = MovieTVShow.objects.annotate(
        avg_rating=Avg('ratings__rating_value'),
        ratings_count=Count('ratings')
    ).filter(ratings_count__gte=3).order_by('-avg_rating')[:10]
    
    # Получаем статистику по жанрам как словари (только нужные поля)
    genres_data = Genre.objects.values(
        'name', 'description'
    ).annotate(
        movies_count=Count('movies')
    ).order_by('-movies_count')[:10]
    
    # Получаем базовую информацию о фильмах для экспорта
    movies_export_data = MovieTVShow.objects.values(
        'title', 'type', 'release_date', 'country'
    ).order_by('-release_date')[:20]
    
    # Получаем только названия жанров для быстрой обработки
    genre_names = Genre.objects.values_list(
        'name', flat=True
    ).order_by('name')
    
    # Получаем пары (название фильма, год) для отчетов
    movie_titles_years = MovieTVShow.objects.values_list(
        'title', 'release_date__year'
    ).order_by('-release_date')[:15]
    
    # Получаем ID активных пользователей для массовых операций
    active_user_ids = User.objects.filter(
        is_active=True
    ).values_list('id', flat=True)
    
    context = {
        'stats': stats,
        'top_genres': top_genres,
        'top_movies': top_movies,
        'genres_data': list(genres_data),
        'movies_export_data': list(movies_export_data),
        'genre_names': list(genre_names),
        'movie_titles_years': list(movie_titles_years),
        'active_users_count': len(active_user_ids),
    }
    
    return render(request, 'movies/statistics.html', context)


def demo_page(request):
    """Демонстрационная страница всех возможностей"""
    context = {
        'total_movies': MovieTVShow.objects.count(),
        'total_genres': Genre.objects.count(),
        'total_reviews': Review.objects.count(),
        'is_admin': is_admin(request.user) if request.user.is_authenticated else False,
        'is_authenticated': request.user.is_authenticated,
    }
    
    return render(request, 'movies/demo.html', context)

@login_required
def add_to_collection(request, collection_id, movie_id):
    """Добавление фильма в подборку"""
    collection = get_object_or_404(Collection, pk=collection_id)
    movie = get_object_or_404(MovieTVShow, pk=movie_id)
    
    # Проверяем права доступа
    if collection.user != request.user and not is_admin(request.user):
        messages.error(request, 'У вас нет прав для редактирования этой подборки.')
        return redirect('collection_detail', pk=collection_id)
    
    # Проверяем, нет ли уже этого фильма в подборке
    if collection.items.filter(movie_tvshow=movie).exists():
        messages.warning(request, f'"{movie.title}" уже есть в подборке.')
    else:
        from .models import CollectionItem
        CollectionItem.objects.create(
            collection=collection,
            movie_tvshow=movie,
            added_by=request.user
        )
        messages.success(request, f'"{movie.title}" добавлен в подборку "{collection.title}"!')
    
    return redirect('collection_detail', pk=collection_id)

@login_required
def remove_from_collection(request, collection_id, movie_id):
    """Удаление фильма из подборки"""
    collection = get_object_or_404(Collection, pk=collection_id)
    movie = get_object_or_404(MovieTVShow, pk=movie_id)
    
    # Проверяем права доступа
    if collection.user != request.user and not is_admin(request.user):
        messages.error(request, 'У вас нет прав для редактирования этой подборки.')
        return redirect('collection_detail', pk=collection_id)
    
    # Удаляем фильм из подборки
    collection_item = collection.items.filter(movie_tvshow=movie).first()
    if collection_item:
        collection_item.delete()
        messages.success(request, f'"{movie.title}" удален из подборки "{collection.title}"!')
    else:
        messages.warning(request, f'"{movie.title}" не найден в подборке.')
    
    return redirect('collection_detail', pk=collection_id)


class GenreListView(ListView):
    """Список жанров"""
    model = Genre
    template_name = 'movies/genre_list.html'
    context_object_name = 'genres'
    paginate_by = 20
    
    def get_queryset(self):
        return Genre.objects.annotate(
        movies_count=Count('movies')
        ).order_by('name')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_admin'] = is_admin(self.request.user)
        context['is_authenticated'] = self.request.user.is_authenticated
        return context

class GenreDetailView(DetailView):
    """Детальный просмотр жанра"""
    model = Genre
    template_name = 'movies/genre_detail.html'
    context_object_name = 'genre'
    
    def get_queryset(self):
        return Genre.objects.prefetch_related('movies__genres')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        genre = self.object
        
        # Получаем фильмы этого жанра с оптимизацией
        movies = genre.movies.select_related().prefetch_related('genres').annotate(
            avg_rating=Avg('ratings__rating_value'),
            reviews_count=Count('reviews')
        ).order_by('-release_date')
        
        context['movies'] = movies
        context['is_admin'] = is_admin(self.request.user)
        context['is_authenticated'] = self.request.user.is_authenticated
        return context
