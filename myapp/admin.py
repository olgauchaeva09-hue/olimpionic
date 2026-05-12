from django.contrib import admin
from .models import Role, User, Subject, Topic, Card, Read, Solved, Favorite, Planned, Olympiad, Direction, University, OlympiadNotification

admin.site.register(Role)
admin.site.register(Read)
admin.site.register(Solved)
admin.site.register(Favorite)
admin.site.register(Planned)
admin.site.register(OlympiadNotification)

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'username', 'role', 'xp') 
    search_fields = ('email', 'username')
    list_filter = ('role',)

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'type', 'source')
    list_filter = ('type', 'topic')
    search_fields = ('title', 'source')
    filter_horizontal = ('topic',)

@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ('id', 'university_name', 'file')
    filter_horizontal = ('direction',)  

@admin.register(Olympiad)
class OlympiadAdmin(admin.ModelAdmin):
    list_display = ('id', 'olympiad_name')
    filter_horizontal = ('topic',)

@admin.register(Direction)
class DirectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'direction_name')
    filter_horizontal = ('olympiad',)

@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('id', 'topic_name', 'subject')
    list_filter = ('subject',)
    search_fields = ('topic_name',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'subject_name', 'icon')