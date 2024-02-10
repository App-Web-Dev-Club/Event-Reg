from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Form, Question


class UserSerializer(serializers.ModelSerializer):
    forms = serializers.PrimaryKeyRelatedField(many=True, queryset=Form.objects.all())
    class Meta:
        model = User
        fields = '__all__'

class FormSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.id')
    class Meta:
        model = Form
        fields = '__all__'


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'