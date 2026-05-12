from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.http import JsonResponse
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect 
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from .models import User, Xp_level, Subject, Topic, Card, Favorite, Task, Read, Solved, Planned, Olympiad, Direction, University, OlympiadNotification
from django.utils import timezone
from datetime import datetime, timedelta
from django.contrib.auth import login
from collections import OrderedDict
from django.utils.timezone import localdate, localtime, now

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            return render(request, 'registration/register.html', {'error': 'Пароли не совпадают'})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'registration/register.html', {'error': 'Пользователь с такой почтой уже существует'})
        
        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        return redirect('/')
    
    return render(request, 'registration/register.html')

class CustomLoginView(LoginView):
    template_name = 'registration/login.html'
    
    def get_success_url(self):
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url:
            return next_url
        return '/'

def tasks(request):
    user = request.user
    if not request.user.is_authenticated:
        return redirect('login')
    xp = user.xp

    current_level_obj = Xp_level.objects.filter(xp_required__lte=xp).order_by('-xp_required').first()
    next_level = Xp_level.objects.filter(xp_required__gt=xp).order_by('xp_required').first()
    
    if next_level:
        xp_for_next = next_level.xp_required - xp
        xp_in_current = xp - (current_level_obj.xp_required if current_level_obj else 0)
        xp_needed = next_level.xp_required - (current_level_obj.xp_required if current_level_obj else 0)
        progress_percent = int((xp_in_current / xp_needed) * 100) if xp_needed > 0 else 100
    else:
        xp_for_next = 0
        progress_percent = 100
    
    current_level_icon = current_level_obj.icon.url if current_level_obj and current_level_obj.icon else None
    
    context = {
        'xp': xp,
        'current_level': current_level_obj.name if current_level_obj else 'Новичок',
        'next_level': next_level.name if next_level else 'MAX',
        'xp_for_next': xp_for_next,
        'progress_percent': progress_percent,
        'current_level_icon': current_level_icon,
    }
    return render(request, 'tasks.html', context)

@login_required
def planner_final(request):
    user = request.user
    
    # Автосохранение тем из сессии
    selected_topic_ids = request.session.get('selected_topics', [])
    if selected_topic_ids:
        for topic_id in selected_topic_ids:
            topic = get_object_or_404(Topic, id=topic_id)
            Planned.objects.get_or_create(
                user=user,
                topic=topic,
                date_time__isnull=True,
                defaults={
                    'card': None,
                    'date_time': None,
                    'end_datetime': None,
                    'source_type': 'topic'
                }
            )
        request.session.pop('selected_topics', None)
    
    if not Planned.objects.filter(user=user, source_type='topic').exists():
        return redirect('planned_step1')
    
    # Параметр недели
    week_offset = int(request.GET.get('week', 0))
    today = localdate()
    monday = today - timedelta(days=today.weekday())
    week_start = monday + timedelta(weeks=week_offset)
    week_end = week_start + timedelta(days=6)
    dates = [week_start + timedelta(days=i) for i in range(7)]
    
    all_planned = Planned.objects.filter(user=user).select_related('topic', 'card')
    
    # Конвертируем distributed в локальное время для отображения
    distributed = []
    undistributed = []
    for p in all_planned:
        if p.date_time is not None:
            p.date_time = localtime(p.date_time)  # UTC → местное
            distributed.append(p)
        else:
            undistributed.append(p)
    
    # sidebar_items
    sidebar_items = OrderedDict()
    for item in undistributed:
        if item.source_type == 'topic' and item.topic:
            subject_name = item.topic.subject.subject_name
            sidebar_items.setdefault(subject_name, []).append({
                'source_id': item.topic.id,
                'item_type': 'topic',
                'title': item.topic.topic_name,
                'planned_id': item.id,
                'type_label': 'Тема',
                'is_card': False,
            })
        elif item.source_type == 'card' and item.card:
            first_topic = item.card.topic.first()
            subject_name = first_topic.subject.subject_name if first_topic else 'Без предмета'
            sidebar_items.setdefault(subject_name, []).append({
                'source_id': item.card.id,
                'item_type': 'card',
                'title': item.card.title[:60],
                'planned_id': item.id,
                'type_label': 'Карточка',
                'is_card': True,
            })
    
    sidebar_items = OrderedDict(sorted(sidebar_items.items()))
    
    # Олимпиады
    olympiad_notifications = OlympiadNotification.objects.filter(user=user).select_related('olympiad')
    olympiad_periods = []
    for notification in olympiad_notifications:
        olympiad = notification.olympiad
        if olympiad.start_date and olympiad.end_date:
            current_date = olympiad.start_date.date()
            end_date = olympiad.end_date.date()
            while current_date <= end_date:
                olympiad_periods.append({
                    'date': current_date,
                    'name': olympiad.olympiad_name,
                    'olympiad_id': olympiad.id,
                    'notification_id': notification.id,
                })
                current_date += timedelta(days=1)
    
    olympiad_by_date = {}
    for period in olympiad_periods:
        date_str = period['date'].isoformat()
        olympiad_by_date.setdefault(date_str, []).append(period)
    
    hours = list(range(0, 23))
    
    schedule_map = {}
    for item in distributed:
        if item.date_time:
            item_date = item.date_time.date()
            if week_start <= item_date <= week_end:
                date_key = item_date.isoformat()
                hour_key = item.date_time.hour
                schedule_map.setdefault(date_key, {})[hour_key] = item
    
    context = {
        'sidebar_items': sidebar_items,
        'olympiad_by_date': olympiad_by_date,
        'dates': dates,
        'hours': hours,
        'schedule_map': schedule_map,
        'today': today,
        'week_start': week_start,
        'week_end': week_end,
        'week_offset': week_offset,
    }
    
    return render(request, 'planned.html', context)

@login_required
def get_notifications(request):
    user = request.user
    today = timezone.now().date()
    notifications = []
    subscriptions = OlympiadNotification.objects.filter(user=user).select_related('olympiad')
    
    for sub in subscriptions:
        olympiad = sub.olympiad
        start_date = olympiad.start_date
        
        if start_date:
            start_date = start_date.date() if hasattr(start_date, 'date') else start_date
            days_left = (start_date - today).days
            
            if days_left in [15, 7, 1, 0]:
                messages = {
                    15: f'Олимпиада "{olympiad.olympiad_name}" начнётся через 15 дней',
                    7: f'Олимпиада "{olympiad.olympiad_name}" начнётся через неделю',
                    1: f'Олимпиада "{olympiad.olympiad_name}" начнётся завтра!',
                    0: f'Олимпиада "{olympiad.olympiad_name}" начинается сегодня!',
                }
                notifications.append({
                    'message': messages[days_left],
                    'days_left': days_left,
                    'olympiad_name': olympiad.olympiad_name,
                })
    return JsonResponse({'notifications': notifications})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_olympiad_notification(request):
    user = request.user
    olympiad_id = request.data.get('olympiad_id')
    set_active = request.data.get('set_active')  
    if set_active:
        OlympiadNotification.objects.get_or_create(user=user, olympiad_id=olympiad_id)
    else:
        OlympiadNotification.objects.filter(user=user, olympiad_id=olympiad_id).delete()
    return Response({'success': True})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request):
    user = request.user
    card_id = request.data.get('card_id')
    set_active = request.data.get('set_active')
    
    if set_active:
        Favorite.objects.get_or_create(user=user, card_id=card_id)
    else:
        Favorite.objects.filter(user=user, card_id=card_id).delete()
    
    return Response({'success': True})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_task(request):
    user = request.user
    card_id = request.data.get('card_id')
    set_active = request.data.get('set_active')
    
    if set_active:
        card = Card.objects.get(id=card_id)
        topic = card.topic.first()
        Task.objects.get_or_create(user=user, card_id=card_id, defaults={'topic': topic})
    else:
        Task.objects.filter(user=user, card_id=card_id).delete()
    
    return Response({'success': True})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_planned(request):
    user = request.user
    card_id = request.data.get('card_id')
    set_active = request.data.get('set_active')
    
    if set_active:
        card = Card.objects.get(id=card_id)
        Planned.objects.get_or_create(
            user=user,
            card_id=card_id,
            date_time__isnull=True,
            defaults={
                'topic': None,
                'date_time': None,
                'end_datetime': None,
                'source_type': 'card'
            }
        )
    else:
        Planned.objects.filter(user=user, card_id=card_id).delete()
    
    return Response({'success': True})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_complete(request):
    user = request.user
    card_id = request.data.get('card_id')
    set_active = request.data.get('set_active')
    
    card = Card.objects.get(id=card_id)
    if card.type_number == 0:
        model = Read
    else:
        model = Solved
    
    if set_active:
        obj, created = model.objects.get_or_create(user=user, card=card)
        if created:
            user.xp += card.xp
            user.save()
    else:
        deleted_count, _ = model.objects.filter(user=user, card=card).delete()
        if deleted_count > 0:
            user.xp = max(0, user.xp - card.xp)
            user.save()
    
    return Response({'success': True, 'xp': user.xp})

def get_card_flags(user, card):
    is_read = Read.objects.filter(user=user, card=card).exists()
    is_solved = Solved.objects.filter(user=user, card=card).exists()
    is_planned = Planned.objects.filter(user=user, card=card).exists()
    is_task = Task.objects.filter(user=user, card=card).exists()
    is_favorite = Favorite.objects.filter(user=user, card=card).exists()
    return {
        'is_read': is_read,
        'is_solved': is_solved,
        'is_planned': is_planned,
        'is_task': is_task,
        'is_favorite': is_favorite,
    }

@login_required
def profile(request):
    user = request.user
    context = {
        'user': user,
    }
    return render(request, 'profile.html', context)

def materials(request):
    subjects = Subject.objects.prefetch_related('topics').all()
    context = {
        'subjects': subjects,
    }
    return render(request, 'materials1.html', context)

def filter(request):
    olympiads = Olympiad.objects.all()
    types = Card.objects.values_list('type', flat=True).distinct()
    context = {
        'olympiads': olympiads,
        'types': types,
    }
    return render(request, 'materials2.html', context)

def cards_materials(request):
    user = request.user if request.user.is_authenticated else None
    query = request.GET.get('q', '')
    
    cards = Card.objects.all()
    
    if query:
        cards = cards.filter(title__icontains=query)
    
    cards_with_flags = []
    for card in cards:
        if user:
            flags = get_card_flags(user, card)
            card.is_favorite = flags['is_favorite']
            card.is_solved = flags['is_solved']
            card.is_read = flags['is_read']
            card.is_planned = flags['is_planned']
            card.is_task = flags['is_task']
        else:
            card.is_favorite = False
            card.is_solved = False
            card.is_read = False
            card.is_planned = False
            card.is_task = False
        cards_with_flags.append(card)

    olympiads = Olympiad.objects.all()
    types = Card.objects.values_list('type', flat=True).distinct()

    return render(request, 'materials2.html', {
        'cards': cards_with_flags,
        'olympiads': olympiads,
        'types': types,
        'query': query,
    })

@login_required
def cards_favorite(request):
    user = request.user
    favorites = Favorite.objects.filter(user=user).select_related('card')
    
    cards_list = []
    for fav in favorites:
        card = fav.card
        flags = get_card_flags(user, card)
        card.is_favorite = True  
        card.is_solved = flags['is_solved']
        card.is_read = flags['is_read']
        card.is_planned = flags['is_planned']
        card.is_task = flags['is_task']
        cards_list.append(card)
    
    return render(request, 'favorites.html', {'cards': cards_list})

@login_required
def cards_task(request):
    user = request.user
    today = localdate()
    xp = user.xp
    
    current_level_obj = Xp_level.objects.filter(xp_required__lte=xp).order_by('-xp_required').first()
    next_level = Xp_level.objects.filter(xp_required__gt=xp).order_by('xp_required').first()
    
    xp_for_next = next_level.xp_required - xp if next_level else 0
    current_level_icon = current_level_obj.icon.url if current_level_obj and current_level_obj.icon else None
    
    # Задачи
    all_tasks = Task.objects.filter(user=user).select_related('card')
    
    # Запланированные на сегодня
    planned_today = Planned.objects.filter(
        user=user,
        date_time__date=today
    ).select_related('card', 'topic')
    
    # Разделяем на карточки и темы
    cards_list = []
    topic_list = []
    existing_card_ids = set()
    
    for t in all_tasks:
        card = t.card
        flags = get_card_flags(user, card)
        card.is_favorite = flags['is_favorite']
        card.is_solved = flags['is_solved']
        card.is_read = flags['is_read']
        card.is_planned = flags['is_planned']
        card.is_task = True
        cards_list.append(card)
        existing_card_ids.add(card.id)
    
    for p in planned_today:
        if p.source_type == 'card' and p.card and p.card.id not in existing_card_ids:
            card = p.card
            flags = get_card_flags(user, card)
            card.is_favorite = flags['is_favorite']
            card.is_solved = flags['is_solved']
            card.is_read = flags['is_read']
            card.is_planned = True
            card.is_task = False
            cards_list.append(card)
            existing_card_ids.add(card.id)
        elif p.source_type == 'topic' and p.topic:
            topic_list.append({
                'id': p.topic.id,
                'title': p.topic.topic_name,
            })
    
    context = {
        'cards': cards_list,
        'topics': topic_list,
        'xp': xp,
        'current_level': current_level_obj.name if current_level_obj else 'Новичок',
        'current_level_icon': current_level_icon,
        'current_level_number': current_level_obj.id if current_level_obj else 0,
        'xp_for_next': xp_for_next,
        'user': user,
    }
    return render(request, 'tasks.html', context)

@login_required
def cards_read(request):
    user = request.user
    read = Read.objects.filter(user=user).select_related('card')
    
    cards_list = []
    for r in read:
        card = r.card
        flags = get_card_flags(user, card)
        card.is_favorite = flags['is_favorite']  
        card.is_solved = flags['is_solved']
        card.is_read = True
        card.is_planned = flags['is_planned']
        card.is_task = flags['is_task']
        cards_list.append(card)
    
    return render(request, 'read.html', {'cards': cards_list})

@login_required
def cards_solved(request):
    user = request.user
    solved = Solved.objects.filter(user=user).select_related('card')
    
    cards_list = []
    for s in solved:
        card = s.card
        flags = get_card_flags(user, card)
        card.is_favorite = flags['is_favorite']  
        card.is_solved = True
        card.is_read = flags['is_read']
        card.is_planned = flags['is_planned']
        card.is_task = flags['is_task']
        cards_list.append(card)
    
    return render(request, 'solved.html', {'cards': cards_list})

@login_required
def cards_planned(request):
    user = request.user
    plan = Planned.objects.filter(user=user).select_related('card')
    
    cards_list = []
    for p in plan:
        card = p.card
        flags = get_card_flags(user, card)
        card.is_favorite = flags['is_favorite']  
        card.is_solved = flags['is_solved']
        card.is_read = flags['is_read']
        card.is_planned = True
        card.is_task = flags['is_task']
        cards_list.append(card)
    
    return render(request, 'planned.html', {'cards': cards_list})

@login_required
def planner_step1(request):
    if Planned.objects.filter(user=request.user, source_type='topic').exists():
        return redirect('planned')
    if request.method == 'POST':
        selected_directions = request.POST.getlist('directions')
        request.session['selected_directions'] = selected_directions
        return redirect('planned_step2')
    universities = University.objects.prefetch_related('direction').all()
    context = {
        'universities': universities,
    }
    return render(request, 'planned-step1.html', context)

@login_required
def planner_step2(request):
    selected_directions = request.session.get('selected_directions', [])
    if selected_directions:
        directions = Direction.objects.filter(id__in=selected_directions)
        olympiads = Olympiad.objects.filter(direction__in=directions).distinct()
    else:
        olympiads = Olympiad.objects.all()

    subscribed = OlympiadNotification.objects.filter(user=request.user).values_list('olympiad_id', flat=True)
    
    if request.method == 'POST':
        selected_olympiads = request.POST.getlist('olympiads')
        request.session['selected_olympiads'] = selected_olympiads
        return redirect('planned_step3')
    return render(request, 'planned-step2.html', {'olympiads': olympiads, 'subscribed_ids': list(subscribed)})

@login_required
def planner_step3(request):
    if Planned.objects.filter(user=request.user, source_type='topic').exists():
        return redirect('planned')
    
    selected_olympiads = request.session.get('selected_olympiads', [])
    if selected_olympiads:
        olympiads = Olympiad.objects.filter(id__in=selected_olympiads)
        subjects = Subject.objects.filter(topics__olympiad__in=olympiads).distinct().prefetch_related('topics')
        for subject in subjects:
            subject.filtered_topics = subject.topics.filter(olympiad__in=olympiads).distinct()
    else:
        subjects = Subject.objects.prefetch_related('topics').all()
        for subject in subjects:
            subject.filtered_topics = subject.topics.all()

    if request.method == 'POST':
        selected_topics = request.POST.getlist('topics')
        user = request.user
        for topic_id in selected_topics:
            topic = get_object_or_404(Topic, id=topic_id)
            Planned.objects.get_or_create(
                user=user,
                topic=topic,
                date_time__isnull=True,
                defaults={
                    'card': None,
                    'date_time': None,
                    'end_datetime': None,
                    'source_type': 'topic'
                }
            )
        request.session.pop('selected_directions', None)
        request.session.pop('selected_olympiads', None)
        return redirect('planned')
    
    return render(request, 'planned-step3.html', {'subjects': subjects})


def olympiads_info(request):
    universities = University.objects.all()
    return render(request, 'benefits.html', {'universities': universities})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_schedule(request):
    """Возвращает все записи Planned для текущего пользователя"""
    user = request.user
    schedule = Planned.objects.filter(user=user).select_related('topic', 'card')
    
    result = []
    for item in schedule:
        result.append({
            'id': item.id,
            'topic_id': item.topic.id if item.topic else None,
            'topic_name': item.topic.topic_name if item.topic else None,
            'card_id': item.card.id if item.card else None,
            'card_title': item.card.title if item.card else None,
            'source_type': item.source_type,
            'date_time': item.date_time.isoformat() if item.date_time else None,
            'end_datetime': item.end_datetime.isoformat() if item.end_datetime else None,
        })
    
    return Response({'success': True, 'data': result})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_sidebar(request):
    user = request.user
    topic_id = request.data.get('topic_id')
    card_id = request.data.get('card_id')
    
    if topic_id:
        topic = get_object_or_404(Topic, id=topic_id)
        planned, created = Planned.objects.get_or_create(
            user=user,
            topic=topic,
            date_time__isnull=True,
            defaults={
                'card': None,
                'date_time': None,
                'end_datetime': None,
                'source_type': 'topic'
            }
        )
        if not created:
            return Response({'success': False, 'error': 'Тема уже добавлена в планировщик'}, status=400)
        
        return Response({
            'success': True,
            'id': planned.id,
            'topic_id': topic.id,
            'topic_name': topic.topic_name,
            'source_type': 'topic'
        })
    
    elif card_id:
        card = get_object_or_404(Card, id=card_id)
        planned, created = Planned.objects.get_or_create(
            user=user,
            card=card,
            date_time__isnull=True,
            defaults={
                'topic': None,
                'date_time': None,
                'end_datetime': None,
                'source_type': 'card'
            }
        )
        if not created:
            return Response({'success': False, 'error': 'Карточка уже добавлена в планировщик'}, status=400)
        
        return Response({
            'success': True,
            'id': planned.id,
            'card_id': card.id,
            'card_title': card.title,
            'source_type': 'card'
        })
    
    else:
        return Response({'success': False, 'error': 'Необходимо указать topic_id или card_id'}, status=400)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def move_to_grid(request):
    """
    Перемещает элемент из боковой панели в сетку (задаёт дату и время)
    Тело запроса: {
        "item_id": 5,
        "start_datetime": "2025-04-10 10:00:00",
        "end_datetime": "2025-04-10 11:00:00"
    }
    """
    user = request.user
    item_id = request.data.get('item_id')
    start_datetime_str = request.data.get('start_datetime')
    end_datetime_str = request.data.get('end_datetime')
    
    if not item_id:
        return Response({'success': False, 'error': 'item_id обязателен'}, status=400)
    
    try:
        planned = Planned.objects.get(id=item_id, user=user)
    except Planned.DoesNotExist:
        return Response({'success': False, 'error': 'Элемент не найден'}, status=404)
    
    # Преобразуем строки в datetime
    try:
        start_datetime = datetime.fromisoformat(start_datetime_str)
        end_datetime = datetime.fromisoformat(end_datetime_str) if end_datetime_str else None
    except ValueError:
        return Response({'success': False, 'error': 'Неверный формат даты'}, status=400)
    
    planned.date_time = start_datetime
    planned.end_datetime = end_datetime
    planned.save()
    
    return Response({
        'success': True,
        'id': planned.id,
        'start_datetime': start_datetime.isoformat(),
        'end_datetime': end_datetime.isoformat() if end_datetime else None
    })

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_schedule_item(request, item_id):
    """
    Обновляет дату, время и длительность элемента в сетке
    Тело запроса: {
        "start_datetime": "2025-04-11 14:00:00",
        "end_datetime": "2025-04-11 16:00:00"
    }
    """
    user = request.user
    
    try:
        planned = Planned.objects.get(id=item_id, user=user)
    except Planned.DoesNotExist:
        return Response({'success': False, 'error': 'Элемент не найден'}, status=404)
    
    start_datetime_str = request.data.get('start_datetime')
    end_datetime_str = request.data.get('end_datetime')
    
    if start_datetime_str:
        try:
            planned.date_time = datetime.fromisoformat(start_datetime_str)
        except ValueError:
            return Response({'success': False, 'error': 'Неверный формат start_datetime'}, status=400)
    
    if end_datetime_str:
        try:
            planned.end_datetime = datetime.fromisoformat(end_datetime_str)
        except ValueError:
            return Response({'success': False, 'error': 'Неверный формат end_datetime'}, status=400)
    
    planned.save()
    
    return Response({
        'success': True,
        'id': planned.id,
        'start_datetime': planned.date_time.isoformat() if planned.date_time else None,
        'end_datetime': planned.end_datetime.isoformat() if planned.end_datetime else None
    })

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_schedule_item(request, item_id):
    """
    Удаляет элемент из планировщика (из сетки или из боковой панели)
    """
    user = request.user
    
    try:
        planned = Planned.objects.get(id=item_id, user=user)
        planned.delete()
        return Response({'success': True, 'message': 'Элемент удалён'})
    except Planned.DoesNotExist:
        return Response({'success': False, 'error': 'Элемент не найден'}, status=404)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_full_schedule(request):
    """
    Сохраняет всё расписание целиком (синхронизация)
    Тело запроса: {
        "schedule": [
            {
                "item_id": 5,
                "start_datetime": "2025-04-10 10:00:00",
                "end_datetime": "2025-04-10 11:00:00"
            },
            ...
        ]
    }
    """
    user = request.user
    schedule_data = request.data.get('schedule', [])
    
    updated_ids = []
    errors = []
    
    for item_data in schedule_data:
        item_id = item_data.get('item_id')
        start_datetime_str = item_data.get('start_datetime')
        end_datetime_str = item_data.get('end_datetime')
        
        if not item_id:
            errors.append({'error': 'item_id отсутствует', 'data': item_data})
            continue
        
        try:
            planned = Planned.objects.get(id=item_id, user=user)
        except Planned.DoesNotExist:
            errors.append({'error': f'Элемент {item_id} не найден', 'data': item_data})
            continue
        
        if start_datetime_str:
            try:
                planned.date_time = datetime.fromisoformat(start_datetime_str)
            except ValueError:
                errors.append({'error': f'Неверный формат даты для {item_id}', 'data': item_data})
                continue
        
        if end_datetime_str:
            try:
                planned.end_datetime = datetime.fromisoformat(end_datetime_str)
            except ValueError:
                errors.append({'error': f'Неверный формат end_datetime для {item_id}', 'data': item_data})
                continue
        
        planned.save()
        updated_ids.append(planned.id)
    
    return Response({
        'success': len(errors) == 0,
        'updated_ids': updated_ids,
        'errors': errors if errors else None
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_topics_from_session(request):
    """
    Добавляет все темы из сессии в планировщик (нераспределённые)
    Тело запроса: {"topic_ids": [5, 12, 23]}
    """
    user = request.user
    topic_ids = request.data.get('topic_ids', [])
    
    if not topic_ids:
        return Response({'success': False, 'error': 'Нет ID тем'}, status=400)
    
    topics = Topic.objects.filter(id__in=topic_ids)
    created_items = []
    errors = []
    
    for topic in topics:
        try:
            planned, created = Planned.objects.get_or_create(
                user=user,
                topic=topic,
                defaults={
                    'date_time': None,
                    'end_datetime': None,
                    'source_type': 'topic'
                }
            )
            if created:
                created_items.append({
                    'id': planned.id,
                    'topic_id': topic.id,
                    'topic_name': topic.topic_name
                })
        except Exception as e:
            errors.append({'topic_id': topic.id, 'error': str(e)})
    
    return Response({
        'success': True,
        'added_count': len(created_items),
        'added_items': created_items,
        'errors': errors if errors else None
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_in_planner(request):
    """
    Проверяет, добавлен ли элемент в планировщик
    Параметры: ?topic_id=5 или ?card_id=10
    """
    user = request.user
    topic_id = request.GET.get('topic_id')
    card_id = request.GET.get('card_id')
    
    if topic_id:
        exists = Planned.objects.filter(user=user, topic_id=topic_id).exists()
        return Response({'exists': exists, 'topic_id': topic_id})
    
    elif card_id:
        exists = Planned.objects.filter(user=user, card_id=card_id).exists()
        return Response({'exists': exists, 'card_id': card_id})
    
    else:
        return Response({'error': 'Укажите topic_id или card_id'}, status=400)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_undistributed(request):
    user = request.user
    Planned.objects.filter(user=user, date_time__isnull=True).delete()
    return Response({'success': True})

def welcome(request):
    if request.user.is_authenticated:
        return redirect('tasks')
    return render(request, 'welcome.html')