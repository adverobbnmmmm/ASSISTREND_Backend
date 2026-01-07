# moderation/serializers.py
from rest_framework import serializers
from .models import Moderator, Perk, Guideline


class ModeratorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Moderator
        fields = '__all__'

class PerkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perk
        fields = '__all__'

class GuidelineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guideline
        fields = '__all__'
