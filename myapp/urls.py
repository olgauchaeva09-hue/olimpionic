from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from . import frontend_views 
from django.contrib.auth import views as auth_views
from .frontend_views import CustomLoginView

router = DefaultRouter()

router.register(r'users', views.UserViewSet)
router.register(r'subjects', views.SubjectViewSet)
router.register(r'topics', views.TopicViewSet)
router.register(r'cards', views.CardViewSet)
router.register(r'reads', views.ReadViewSet, basename='read')
router.register(r'solved', views.SolvedViewSet, basename='solved')
router.register(r'favorites', views.FavoriteViewSet, basename='favorite')
router.register(r'planned-api', views.PlannedViewSet, basename='planned')
router.register(r'task', views.TaskViewSet, basename='task')
router.register(r'olympiads', views.OlympiadViewSet)
router.register(r'universities', views.UniversityViewSet)
router.register(r'universities-file', views.FileUniversityViewSet, basename='universityfile')

urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', frontend_views.register, name='register'),

    # API (ViewSet'ы)
    path('api/', include(router.urls)),
    
    # API (toggle-действия для карточек)
    path('api/toggle/favorite/', frontend_views.toggle_favorite, name='toggle_favorite'),
    path('api/toggle/task/', frontend_views.toggle_task, name='toggle_task'),
    path('api/toggle/planned/', frontend_views.toggle_planned, name='toggle_planned'),
    path('api/toggle/complete/', frontend_views.toggle_complete, name='toggle_complete'),
    path('api/toggle/olympiad/', frontend_views.toggle_olympiad_notification, name='toggle_olympiad'),
    
    # API (уведомления)
    path('api/notifications/', frontend_views.get_notifications, name='api_notifications'),

    # API (кастомные эндпоинты для планировщика)
    path('api/planned/schedule/', frontend_views.get_user_schedule, name='api_planner_schedule'),
    path('api/planned/add_to_sidebar/', frontend_views.add_to_sidebar, name='api_planner_add_to_sidebar'),
    path('api/planned/move_to_grid/', frontend_views.move_to_grid, name='api_planner_move_to_grid'),
    path('api/planned/save_full/', frontend_views.save_full_schedule, name='api_planner_save_full'),
    path('api/planned/clear_undistributed/', frontend_views.clear_undistributed, name='api_planner_clear'),
    path('api/planned/add_from_session/', frontend_views.add_topics_from_session, name='api_planner_add_session'),
    path('api/planned/check/', frontend_views.check_in_planner, name='api_planner_check'),
    path('api/planned/update/<int:item_id>/', frontend_views.update_schedule_item, name='api_planner_update'),
    path('api/planned/delete/<int:item_id>/', frontend_views.delete_schedule_item, name='api_planner_delete'),
    
    # HTML страницы
    path('', frontend_views.welcome, name='index'),
    path('tasks/', frontend_views.cards_task, name='tasks'),
    path('materials/', frontend_views.materials, name='materials'),
    path('materials/cards/', frontend_views.cards_materials, name='cards_materials'),
    path('favorites/', frontend_views.cards_favorite, name='favorites'),
    path('read/', frontend_views.cards_read, name='read'),
    path('solved/', frontend_views.cards_solved, name='solved'),
    path('olympiads/', frontend_views.olympiads_info, name='olympiads'),
    path('planned/step1/', frontend_views.planner_step1, name='planned_step1'),
    path('planned/step2/', frontend_views.planner_step2, name='planned_step2'),
    path('planned/step3/', frontend_views.planner_step3, name='planned_step3'),
    path('planned/', frontend_views.planner_final, name='planned'),
    path('planned/cards/', frontend_views.cards_planned, name='planned_cards'),
    path('profile/', frontend_views.profile, name='profile'),
]