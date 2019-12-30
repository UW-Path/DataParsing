from rest_framework import serializers
from .models import UwpathApp, CourseInfo, Antireqs, Coreqs, Prereqs, Requirements


class AppSerializer(serializers.ModelSerializer):
    class Meta:
        model = UwpathApp
        fields =  '__all__'

class CourseInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CourseInfo
        fields =  '__all__'


class AntireqsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Antireqs
        fields =  '__all__'


class CoreqsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coreqs
        fields =  '__all__'

class PrereqsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prereqs
        fields =  '__all__'

class RequirementsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Requirements
        fields =  '__all__'
