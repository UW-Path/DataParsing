from rest_framework import serializers
from .models import UwpathApp, CourseInfo

class AppSerializer(serializers.ModelSerializer):
    class Meta:
        model = UwpathApp
        fields =  '__all__'

class CourseInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseInfo
        fields =  '__all__'