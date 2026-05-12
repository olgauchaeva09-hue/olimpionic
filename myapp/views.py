#from django.shortcuts import render
from rest_framework import viewsets, permissions, filters 
from django_filters.rest_framework import DjangoFilterBackend  
from rest_framework.decorators import action  
from rest_framework.response import Response  
from .models import Role, User, Subject, Topic, Card, Read, Solved, Favorite, Planned, Olympiad, Direction, University, OlympiadNotification, Task, Xp_level
from .serializers import UserProfileSerializer, UserRegistrationSerializer, CardSerializer, SubjectSerializer, TopicSerializer, ReadSerializer, SolvedSerializer, FavoriteSerializer, PlannedSerializer, OlympiadSerializer, DirectionSerializer, UniversitySerializer, FileUniversitySerializer, OlympiadNotificationSerializer, Xp_levelSerializer, TaskSerializer
from .permissions import IsOwnerOrAdmin, IsAdminOrReadOnly, IsAuthor

class UserViewSet(viewsets.ModelViewSet):  
    queryset = User.objects.all()  

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegistrationSerializer
        return UserProfileSerializer
    
    def get_permissions(self):
        if self.action == 'create': 
            return [permissions.AllowAny()] 
        return [IsOwnerOrAdmin()]
    
class SubjectViewSet(viewsets.ModelViewSet):  
    queryset = Subject.objects.all()  
    serializer_class = SubjectSerializer  
    permission_classes = [IsAdminOrReadOnly]  

class CardViewSet(viewsets.ModelViewSet):  
    queryset = Card.objects.all()  
    serializer_class = CardSerializer  
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['type','source']  
    search_fields = ['title']  
    ordering = ['title']
    pagination_class = None
    
    def get_queryset(self):
        queryset = super().get_queryset()
        source = self.request.query_params.get('source', None)
        if source and source != 'olympiads_all':
            queryset = queryset.filter(source__icontains=source)
        return queryset

class Xp_levelViewSet(viewsets.ModelViewSet):  
    queryset = Xp_level.objects.all()  
    serializer_class = Xp_levelSerializer  
    permission_classes = [IsAdminOrReadOnly]

class TopicViewSet(viewsets.ModelViewSet):  
    queryset = Topic.objects.all()  
    serializer_class = TopicSerializer  
    permission_classes = [IsAdminOrReadOnly]  

class ReadViewSet(viewsets.ModelViewSet):  
    serializer_class = ReadSerializer  
    permission_classes = [IsAuthor]  
    def get_queryset(self):
        return Read.objects.filter(user=self.request.user)

class SolvedViewSet(viewsets.ModelViewSet):  
    serializer_class = SolvedSerializer  
    permission_classes = [IsAuthor]  
    def get_queryset(self):
        return Solved.objects.filter(user=self.request.user)

class FavoriteViewSet(viewsets.ModelViewSet):  
    serializer_class = FavoriteSerializer  
    permission_classes = [IsAuthor]  
    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)

class TaskViewSet(viewsets.ModelViewSet):  
    serializer_class = TaskSerializer  
    permission_classes = [IsAuthor]  
    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

class PlannedViewSet(viewsets.ModelViewSet):  
    serializer_class = PlannedSerializer  
    permission_classes = [IsAuthor]  
    def get_queryset(self):
        return Planned.objects.filter(user=self.request.user)

class OlympiadViewSet(viewsets.ModelViewSet):  
    queryset = Olympiad.objects.all()  
    serializer_class = OlympiadSerializer  
    permission_classes = [IsAdminOrReadOnly]

class UniversityViewSet(viewsets.ModelViewSet):  
    queryset = University.objects.all()  
    serializer_class = UniversitySerializer  
    permission_classes = [IsAdminOrReadOnly]

class FileUniversityViewSet(viewsets.ModelViewSet):  
    queryset = University.objects.all()  
    serializer_class = FileUniversitySerializer  
    permission_classes = [IsAdminOrReadOnly]

class OlympiadNotificationViewSet(viewsets.ModelViewSet):  
    serializer_class = OlympiadNotificationSerializer  
    permission_classes = [IsAuthor]  
    def get_queryset(self):
        return OlympiadNotification.objects.filter(user=self.request.user)
