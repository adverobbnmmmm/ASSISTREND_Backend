from rest_framework import serializers
from .models import UserAccount,Profile,GamificationQuestion

    

class GamificationPointsUpdateSerializer(serializers.ModelSerializer):
    profileImageurl = serializers.ImageField(required=False)
    audioUrl = serializers.FileField(required=False)
    class Meta:
        model = Profile
        fields = '__all__'