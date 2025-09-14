from django.shortcuts import render
from rest_framework import generics,status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated,AllowAny
from .models import UserAccount,Profile,GamificationQuestion,UserInterest,Interest
from .serializers import GamificationPointsUpdateSerializer
from django.db.models import Sum
# Create your views here.

       
class GamificationPointsUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = GamificationPointsUpdateSerializer
    permission_classes = [AllowAny]
    def get_object(self):
        return Profile.objects.get(userId=request.user.id)
    def get(self,request,*args,**kwargs):
        user_id = request.user.id
        points = Profile.objects.values_list('points',flat=True).get(userId=user_id)
        userInterestExist = UserInterest.objects.filter(userId=user_id)
        interestList = Interest.objects.all().values("id","interestName")
        profile = self.get_object()
        excluded = ["id","userName","userId","isPrivate","points"]

        empty_fields = [
            field.name for field in profile._meta.fields
            if field.name not in excluded and 
            (getattr(profile,field.name) is None or getattr(profile,field.name) == "")
        ]
        if(not userInterestExist):
            empty_fields.append("interests")
        return Response(
            {
                "success":True,
                'Message':"Point fetched successsfully",
                "points" : points,
                "empty_fields": empty_fields,
                'interest_list':list(interestList)
            },
        status=status.HTTP_200_OK)
    def update(self,request,*args,**kwargs):
        user_id = request.user.id
        profile = self.get_object()
        userInterest = UserInterest.objects.filter(userId=user_id)
        #updating user data
        data = request.data.copy()
        interest_ids = request.data.get('interestIds')
        if(interest_ids):
            data.pop('interestIds',None)
            #create interests
            if not user_id or not interest_ids or not isinstance(interest_ids, list) or len(interest_ids) == 0:
                return Response(
                    {'error': 'userId and interestIds (non-empty list) are required'}, 
                    status=400
                )
            try:
                user = UserAccount.objects.get(id=user_id)
            except UserAccount.DoesNotExist:
                return Response({'error': 'User not found'}, status=404)
            for interest_id in interest_ids:
                interest = Interest.objects.get(id=interest_id)
                UserInterest.objects.get_or_create(userId=user, InterestId=interest)

        serializer = self.get_serializer(profile,data=data,partial=True)
        if not serializer.is_valid():
            print(serializer.errors)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

       
        #calculating points
        excluded = ["id","userName","userId","isPrivate","points"]
        Filled_fields = [
            field.name for field in profile._meta.fields
            if field.name not in excluded and 
            (getattr(profile,field.name) is not None and getattr(profile,field.name) != "")
        ]
        gamificationFields = GamificationQuestion.objects.values_list('field_name',flat=True).filter(is_active=True)
        gamification_set = {field.lower() for field in gamificationFields}
        matched_fields = [
            field for field in Filled_fields if field.lower() in gamification_set
        ]
        points = GamificationQuestion.objects.filter(field_name__in=matched_fields).aggregate(
            total_points = Sum("points")
        )["total_points"] or 0


        #checking interests points
        if(not userInterest):
            interestPoint = GamificationQuestion.filter(field_name="interests",is_active=true).values("field_name","points")
            profile.points = interestPoint + points
        else:
            profile.points = points
        profile.save()
        return Response({
            'success':True,
            'message':"Gamification updated successfully",
            'earned_points':points,
            'profile_data':serializer.data
        },status=status.HTTP_200_OK)
        
        