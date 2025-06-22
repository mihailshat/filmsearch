from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Collection, CollectionItem, MovieTVShow, Review, Rating, Recommendation, Genre, UserProfile
from .forms import CustomUserCreationForm
from typing import Any, Dict, Optional
import json


@csrf_exempt
@require_http_methods(["POST"])
def register_api(request: HttpRequest) -> JsonResponse:
    """
    API для регистрации пользователя.
    Принимает JSON с данными пользователя, создает пользователя и профиль.
    Args:
        request: HttpRequest
    Returns:
        JsonResponse: Результат регистрации
    """
    try:
        data = json.loads(request.body)
        form = CustomUserCreationForm(data)
        
        if form.is_valid():
            user = form.save()
            # Создаем профиль пользователя
            UserProfile.objects.create(user=user)
            
            return JsonResponse({
                'success': True,
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def login_api(request: HttpRequest) -> JsonResponse:
    """
    API входа пользователя.
    Принимает JSON с username и password, выполняет аутентификацию и вход.
    Args:
        request: HttpRequest
    Returns:
        JsonResponse: Результат входа
    """
    try:
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return JsonResponse({
                'success': False,
                'error': 'Имя пользователя и пароль обязательны'
            }, status=400)
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return JsonResponse({
                'success': True,
                'message': 'Успешный вход в систему',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Неверное имя пользователя или пароль'
            }, status=401)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Некорректный JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def logout_api(request: HttpRequest) -> JsonResponse:
    """
    API выхода пользователя.
    Завершает сессию пользователя, если он авторизован.
    Args:
        request: HttpRequest
    Returns:
        JsonResponse: Результат выхода
    """
    try:
        if request.user.is_authenticated:
            username = request.user.username
            logout(request)
            return JsonResponse({
                'success': True,
                'message': f'Пользователь {username} успешно вышел из системы'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Пользователь не авторизован'
            }, status=401)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def profile_api(request: HttpRequest) -> JsonResponse:
    """
    API профиля пользователя.
    Возвращает информацию о текущем пользователе, если он авторизован.
    Args:
        request: HttpRequest
    Returns:
        JsonResponse: Данные профиля пользователя
    """
    try:
        if request.user.is_authenticated:
            return JsonResponse({
                'success': True,
                'user': {
                    'id': request.user.id,
                    'username': request.user.username,
                    'email': request.user.email,
                    'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'is_staff': request.user.is_staff,
                    'is_superuser': request.user.is_superuser,
                    'date_joined': request.user.date_joined.isoformat(),
                    'last_login': request.user.last_login.isoformat() if request.user.last_login else None
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Пользователь не авторизован'
            }, status=401)
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def collections_api(request: HttpRequest) -> JsonResponse:
    """
    API для работы с подборками.
    GET: возвращает список подборок.
    POST: создает новую подборку для авторизованного пользователя.
    Args:
        request: HttpRequest
    Returns:
        JsonResponse: Результат операции
    """
    try:
        if request.method == 'GET':
            # Получение списка подборок
            collections = Collection.objects.all().order_by('-created_at')
            
            collections_data = []
            for collection in collections:
                collections_data.append({
                    'id': collection.id,
                    'title': collection.title,
                    'description': collection.description,
                    'user': collection.user.username if collection.user else 'Система',
                    'is_public': collection.is_public,
                    'created_at': collection.created_at.isoformat(),
                    'movies_count': collection.items.count()
                })
            
            return JsonResponse({
                'success': True,
                'collections': collections_data
            })
            
        elif request.method == 'POST':
            # Создание новой подборки
            if not request.user.is_authenticated:
                return JsonResponse({
                    'success': False,
                    'error': 'Необходима авторизация'
                }, status=401)
            
            data = json.loads(request.body)
            title = data.get('title') or data.get('name')  # Поддерживаем оба варианта
            description = data.get('description', '')
            is_public = data.get('is_public', True)
            
            if not title:
                return JsonResponse({
                    'success': False,
                    'error': 'Название подборки обязательно'
                }, status=400)
            
            collection = Collection.objects.create(
                title=title,
                description=description,
                user=request.user,
                is_public=is_public
            )
            
            return JsonResponse({
                'success': True,
                'message': 'Подборка создана успешно',
                'collection': {
                    'id': collection.id,
                    'title': collection.title,
                    'description': collection.description,
                    'is_public': collection.is_public,
                    'created_at': collection.created_at.isoformat()
                }
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Некорректный JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def admin_dashboard_api(request: HttpRequest) -> JsonResponse:
    """
    API для админ-панели.
    Возвращает статистику, последние фильмы, отзывы и топ пользователей.
    Args:
        request: HttpRequest
    Returns:
        JsonResponse: Данные для админ-панели
    """
    try:
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Необходима авторизация'
            }, status=401)
        
        if not (request.user.is_staff or request.user.is_superuser):
            return JsonResponse({
                'success': False,
                'error': 'Доступ запрещен. Требуются права администратора.'
            }, status=403)
        
        from django.db.models import Count, Avg
        
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
        recent_movies = []
        for movie in MovieTVShow.objects.order_by('-created_at')[:5]:
            recent_movies.append({
                'id': movie.id,
                'title': movie.title,
                'type': movie.get_type_display(),
                'release_date': movie.release_date.isoformat(),
                'created_at': movie.created_at.isoformat()
            })
        
        # Последние отзывы
        recent_reviews = []
        for review in Review.objects.select_related('user', 'movie_tvshow').order_by('-created_at')[:5]:
            recent_reviews.append({
                'id': review.id,
                'user': review.user.username,
                'movie': review.movie_tvshow.title,
                'text_preview': review.review_text[:100] + '...' if len(review.review_text) > 100 else review.review_text,
                'created_at': review.created_at.isoformat()
            })
        
        # Топ пользователей по активности
        active_users = []
        for user in User.objects.annotate(
            reviews_count=Count('reviews'),
            ratings_count=Count('ratings')
        ).order_by('-reviews_count', '-ratings_count')[:5]:
            active_users.append({
                'id': user.id,
                'username': user.username,
                'reviews_count': user.reviews_count,
                'ratings_count': user.ratings_count,
                'is_staff': user.is_staff,
                'is_superuser': user.is_superuser
            })
        
        return JsonResponse({
            'success': True,
            'stats': stats,
            'recent_movies': recent_movies,
            'recent_reviews': recent_reviews,
            'active_users': active_users
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def generate_recommendations_api(request: HttpRequest) -> JsonResponse:
    """
    API для генерации рекомендаций (только для администратора).
    Создает рекомендации для всех пользователей по топ-рейтинговым фильмам.
    Args:
        request: HttpRequest
    Returns:
        JsonResponse: Результат генерации
    """
    try:
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Необходима авторизация'
            }, status=401)
        
        if not (request.user.is_staff or request.user.is_superuser):
            return JsonResponse({
                'success': False,
                'error': 'Доступ запрещен. Требуются права администратора.'
            }, status=403)
        
        from django.db.models import Count, Avg
        
        # Получаем всех активных пользователей
        users = User.objects.filter(is_active=True)
        recommendations_created = 0
        
        for user in users:
            # Получаем топ-рейтинговые фильмы, которые пользователь еще не оценивал
            top_movies = MovieTVShow.objects.annotate(
                avg_rating=Avg('ratings__rating_value'),
                ratings_count=Count('ratings')
            ).filter(
                ratings_count__gte=3  # Минимум 3 оценки
            ).exclude(
                ratings__user=user  # Исключаем уже оцененные пользователем
            ).order_by('-avg_rating')[:3]  # Топ-3 фильма
            
            for movie in top_movies:
                recommendation, created = Recommendation.objects.get_or_create(
                    user=user,
                    movie_tvshow=movie,
                    defaults={
                        'reason_code': 'admin_generated'
                    }
                )
                if created:
                    recommendations_created += 1
        
        return JsonResponse({
            'success': True,
            'message': f'Создано {recommendations_created} новых рекомендаций',
            'recommendations_created': recommendations_created,
            'users_processed': users.count()
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def moderate_review_api(request: HttpRequest, review_id: int) -> JsonResponse:
    """
    API для модерации отзывов администратором.
    Позволяет одобрять или отклонять отзывы.
    Args:
        request: HttpRequest
        review_id: int — ID отзыва
    Returns:
        JsonResponse: Результат модерации
    """
    try:
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Необходима авторизация'
            }, status=401)
        
        if not (request.user.is_staff or request.user.is_superuser):
            return JsonResponse({
                'success': False,
                'error': 'Доступ запрещен. Требуются права администратора.'
            }, status=403)
        
        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Отзыв не найден'
            }, status=404)
        
        data = json.loads(request.body)
        action = data.get('action')  # 'approve', 'reject'
        
        if action == 'approve':
            review.approve(request.user)
            message = 'Отзыв одобрен'
            
        elif action == 'reject':
            reason = data.get('reason', 'Нарушение правил сообщества')
            review.reject(request.user, reason)
            message = 'Отзыв отклонен'
            
        else:
            return JsonResponse({
                'success': False,
                'error': 'Неверное действие. Используйте "approve" или "reject"'
            }, status=400)
        
        return JsonResponse({
            'success': True,
            'message': message,
            'review': {
                'id': review.id,
                'status': review.moderation_status,
                'moderated_by': request.user.username,
                'moderated_at': review.moderated_at.isoformat() if review.moderated_at else None,
                'rejection_reason': review.rejection_reason
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Некорректный JSON'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["GET"])
def pending_reviews_api(request: HttpRequest) -> JsonResponse:
    """
    API для получения отзывов на модерации.
    Возвращает список отзывов со статусом 'pending'.
    Args:
        request: HttpRequest
    Returns:
        JsonResponse: Список отзывов на модерации
    """
    try:
        if not request.user.is_authenticated:
            return JsonResponse({
                'success': False,
                'error': 'Необходима авторизация'
            }, status=401)
        
        if not (request.user.is_staff or request.user.is_superuser):
            return JsonResponse({
                'success': False,
                'error': 'Доступ запрещен. Требуются права администратора.'
            }, status=403)
        
        # Получаем отзывы на модерации
        pending_reviews = Review.objects.filter(
            moderation_status='pending'
        ).select_related('user', 'movie_tvshow').order_by('-created_at')
        
        reviews_data = []
        for review in pending_reviews:
            reviews_data.append({
                'id': review.id,
                'user': review.user.username,
                'movie': review.movie_tvshow.title,
                'text': review.review_text,
                'created_at': review.created_at.isoformat(),
                'status': review.moderation_status
            })
        
        return JsonResponse({
            'success': True,
            'pending_reviews': reviews_data,
            'count': len(reviews_data)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500) 