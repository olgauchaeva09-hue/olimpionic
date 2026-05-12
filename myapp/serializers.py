from rest_framework import serializers  
from .models import Role, User, Subject, Topic, Card, Read, Solved, Favorite, Planned, Olympiad, Direction, University, OlympiadNotification, Xp_level, Task

class UserProfileSerializer(serializers.ModelSerializer):
    role = serializers.SlugRelatedField(slug_field='role_name', read_only=True)   
    class Meta:  
        model = User  
        fields = ('id', 'email', 'username', 'role', 'icon', 'xp')

class UserRegistrationSerializer(serializers.ModelSerializer):  
    class Meta:  
        model = User  
        fields = ('username', 'email', 'password')

class CardSerializer(serializers.ModelSerializer):  
    class Meta:  
        model = Card  
        fields = '__all__'

class Xp_levelSerializer(serializers.ModelSerializer):  
    class Meta:  
        model = Xp_level  
        fields = '__all__'

class TopicSerializer(serializers.ModelSerializer): 
    class Meta:
        model = Topic
        fields = '__all__'
    
class SubjectSerializer(serializers.ModelSerializer):
    topics = TopicSerializer(read_only=True, many=True) 
    class Meta:
        model = Subject
        fields = ('id', 'subject_name', 'icon', 'topics')

class ReadSerializer(serializers.ModelSerializer):
    card_inf = CardSerializer(read_only=True)
    class Meta:
        model = Read
        fields = ('id', 'user', 'card', 'date_read', 'card_inf')

class SolvedSerializer(serializers.ModelSerializer):
    card_inf = CardSerializer(read_only=True)
    class Meta:
        model = Solved
        fields = ('id', 'user', 'card', 'date_solved', 'card_inf')

class FavoriteSerializer(serializers.ModelSerializer):
    card_inf = CardSerializer(read_only=True)
    class Meta:
        model = Favorite
        fields = ('id', 'user', 'card', 'date_added', 'card_inf')

class TaskSerializer(serializers.ModelSerializer):
    card_inf = CardSerializer(read_only=True)
    topic_inf = TopicSerializer(read_only=True)
    class Meta:
        model = Task
        fields = ('id', 'user', 'card', 'topic', 'date_to_do', 'card_inf', 'topic_inf')

class PlannedSerializer(serializers.ModelSerializer):
    card_inf = CardSerializer(read_only=True)
    topic_inf = TopicSerializer(read_only=True)
    class Meta:
        model = Planned
        fields = ('id', 'user', 'card', 'topic', 'date_time', 'card_inf', 'topic_inf')

class OlympiadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Olympiad
        fields = '__all__'

class DirectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Direction
        fields = '__all__'

class UniversitySerializer(serializers.ModelSerializer):
    direction_inf = DirectionSerializer(read_only=True)
    class Meta:
        model = University
        fields = ('id', 'university_name', 'direction_inf')

class FileUniversitySerializer(serializers.ModelSerializer):
    class Meta:
        model = University
        fields = ('id', 'university_name', 'file')

class OlympiadNotificationSerializer(serializers.ModelSerializer):
    olympiad_name = serializers.CharField(source='olympiad.olympiad_name', read_only=True)
    class Meta:
        model = OlympiadNotification
        fields = ('id', 'user', 'olympiad', 'start_date', 'end_date', 'olympiad_name')