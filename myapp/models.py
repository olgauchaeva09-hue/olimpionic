from django.db import models
from django.contrib.auth.models import AbstractUser

class Role(models.Model):
    role_name = models.CharField(max_length=24)
    class Meta:
        db_table = 'Role'

def get_default_role():
    role, created = Role.objects.get_or_create(role_name='user')
    return role.id

class User(AbstractUser):
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=320, unique=True)
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name = 'users', default=get_default_role)
    icon = models.ImageField(upload_to='images/', default='images/default_avatar.png')
    xp = models.IntegerField(default=0)
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',  # уникальное имя
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',  # уникальное имя
        related_query_name='custom_user',
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    class Meta:
        db_table = 'User'

class Subject(models.Model):
    subject_name = models.CharField(max_length = 30, unique=True)
    icon = models.CharField(max_length=5)
    class Meta:
        db_table = 'Subject'

class Topic(models.Model):
    topic_name = models.CharField(max_length=33)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name = 'topics')
    class Meta:
        db_table = 'Topic'

class Card(models.Model):
    title = models.TextField()
    type_number = models.IntegerField()
    type = models.CharField(max_length=15)
    topic = models.ManyToManyField(Topic)
    source = models.TextField(null = True)
    xp = models.IntegerField(default=10)
    link = models.URLField(null=True, blank=True, max_length=500)
    class Meta:
        db_table = 'Card'

class Xp_level(models.Model):
    name = models.CharField(max_length=50, unique=True)
    xp_required = models.PositiveIntegerField()
    icon = models.ImageField(upload_to='images/', null=True)
    class Meta:
        db_table = 'Xp_level'

class Read(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'read_by')
    card = models.ForeignKey(Card, on_delete = models.CASCADE, related_name = 'read')
    date_read = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'Read'
        unique_together = ['user', 'card']

class Solved(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'solved_by')
    card = models.ForeignKey(Card, on_delete = models.CASCADE, related_name = 'solved')
    date_solved = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'Solved'
        unique_together = ['user', 'card']

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'favorites_by')
    card = models.ForeignKey(Card, on_delete = models.CASCADE, related_name = 'favorites')
    date_added = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'Favorites'
        unique_together = ['user', 'card']

class Task(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'tasks_for')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name = 'tasks_topic', null=True, blank=True)
    card = models.ForeignKey(Card, on_delete = models.CASCADE, related_name = 'tasks', null=True, blank=True)
    date_to_do = models.DateTimeField(auto_now_add=True)
    class Meta:
        db_table = 'Task'
        unique_together = ['user', 'card']

class Planned(models.Model):
    user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = 'planned_by')
    card = models.ForeignKey(Card, on_delete=models.CASCADE, related_name = 'planned_card', null=True, blank=True)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name = 'planned_topic', null=True, blank=True)
    date_time = models.DateTimeField(null = True)
    end_datetime = models.DateTimeField(null=True, blank=True)
    source_type = models.CharField(max_length=20, default='topic')
    class Meta:
        db_table = 'Planned'
        unique_together = ['user', 'topic', 'date_time']

class Olympiad(models.Model):
    olympiad_name = models.CharField(max_length=124, unique=True)
    topic = models.ManyToManyField(Topic)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)
    class Meta:
        db_table = 'Olympiad'

class Direction(models.Model):
    direction_name = models.CharField(max_length=48, unique=True)
    olympiad = models.ManyToManyField(Olympiad)
    class Meta:
        db_table = 'Direction'

class University(models.Model):
    university_name = models.CharField(max_length=117, unique=True)
    file = models.FileField(upload_to='documents/', null=True, blank=True)
    link = models.URLField(max_length=500, null=True, blank=True)
    direction = models.ManyToManyField(Direction)
    class Meta:
        db_table = 'University'

class OlympiadNotification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='olympiad_notifications')
    olympiad = models.ForeignKey(Olympiad, on_delete=models.CASCADE, related_name='notifications')
    class Meta:
        db_table = 'OlympiadNotification'
        unique_together = ['user', 'olympiad']