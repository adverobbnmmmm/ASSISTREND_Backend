# notifications/views.py
from rest_framework import viewsets, mixins
from .models import Moderator, Perk, Guideline
from .serializers import ModeratorSerializer, PerkSerializer, GuidelineSerializer


class ModeratorViewSet(viewsets.ModelViewSet):
    queryset = Moderator.objects.all()
    serializer_class = ModeratorSerializer

class PerkViewSet(viewsets.ModelViewSet):
    queryset = Perk.objects.all()
    serializer_class = PerkSerializer

class GuidelineViewSet(viewsets.ModelViewSet):
    queryset = Guideline.objects.all()
    serializer_class = GuidelineSerializer
