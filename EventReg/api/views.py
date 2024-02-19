from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated , AllowAny
from .models import *
import json
from django.shortcuts import render
from django.contrib.auth.models import User
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404, render
from .serializers import *
from rest_framework.views import APIView
from api.views import *
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from django.http import HttpResponseNotFound
from .models import Form, Question, Choice
from .serializers import FormSerializer, QuestionSerializer, ChoiceSerializer

class FormListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        forms = Form.objects.all()
        # customize the response data according to your needs
        data = [{'title': form.title, 'description': form.description} for form in forms]
        return Response(data)

class FormCreate(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        result = {"result": "", "error_reason": ""}
        data = request.data

        if len(data['questions']) > 0:
            form = Form.objects.create(
                title=data['form_title'],
                description=data['form_description'],
                owner=request.user
            )
            result['result'] = 'Form saved successfully'

            for question_item in data['questions']:
                question = Question.objects.create(
                    question_text=question_item['text'],
                    question_type=question_item['type'],
                    form=form
                )

                if question_item['type'] == 'mcq_one' or question_item['type'] == 'mcq_many':
                    for choice_item in question_item['options']:
                        Choice.objects.create(
                            choice_text=choice_item,
                            question=question
                        )
        else:
            result['result'] = 'Add a question title'

        return Response(result, status=status.HTTP_200_OK)
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from .models import Form
from .serializers import FormSerializer

class Formcreate(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        result = {"result": "", "error_reason": ""}
        data = request.data

        # Check if the user is authenticated
        if request.user.is_authenticated:
            if len(data['questions']) > 0:
                form = Form.objects.create(
                    title=data['form_title'],
                    description=data['form_description'],
                    owner=request.user  # Assign authenticated user as owner
                )
                result['result'] = 'Form saved successfully'
                for question_item in data['questions']:
                    question = Question.objects.create(
                    question_text=question_item['text'],
                    question_type=question_item['type'],
                    form=form
                )

                if question_item['type'] == 'mcq_one' or question_item['type'] == 'mcq_many':
                    for choice_item in question_item['options']:
                        Choice.objects.create(
                            choice_text=choice_item,
                            question=question
                        )
            else:
                result['error_reason'] = 'Add a question title'
        else:
            result['error_reason'] = 'User is not authenticated'

        return Response(result, status=status.HTTP_200_OK)

    
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponseNotFound


class FormApiView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # Use the authenticated user instead of extracting from URL
            user = request.user

            # Assuming the primary key is now provided in the request data
            pk = request.data.get('pk', None)
            if pk is None:
                return Response({"detail": "Primary key not provided."}, status=status.HTTP_400_BAD_REQUEST)

            form = get_object_or_404(Form, id=pk, owner=user)

            # Use select_related or prefetch_related to optimize queries
            questions = Question.objects.filter(form=form).select_related('form')
            choices = Choice.objects.filter(question__in=questions).select_related('question')

            form_serializer = FormSerializer(form)
            question_serializer = QuestionSerializer(questions, many=True)
            choice_serializer = ChoiceSerializer(choices, many=True)

            serialized_data = {
                'form': form_serializer.data,
                'questions': question_serializer.data,
                'choices': choice_serializer.data
            }

            return Response(serialized_data, status=status.HTTP_200_OK)

        except Exception as e:
            # Log the exception for debugging purposes
            print(f"An error occurred: {str(e)}")
            return Response({"detail": "Form not found."}, status=status.HTTP_404_NOT_FOUND)
        
class AnswerForm(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        result = {"result": "", "error_reason": ""}
        data = request.data

        # Check if the user is authenticated
        if request.user.is_authenticated:
            if 'form_id' in data and 'answers' in data:
                form_id = data['form_id']
                form = Form.objects.get(pk=form_id)

                for answer_data in data['answers']:
                    question_id = answer_data['question_id']
                    question = Question.objects.get(pk=question_id)

                    if question.question_type == 'text':
                        TextAnswer.objects.create(
                            question=question,
                            user=request.user,
                            answer_text=answer_data['answer']
                        )
                    elif question.question_type == 'mcq_one':
                        choice_id = answer_data['answer']
                        choice = Choice.objects.get(pk=choice_id)
                        McqOneAnswer.objects.create(
                            question=question,
                            user=request.user,
                            choice=choice
                        )
                    elif question.question_type == 'mcq_many':
                        choices_ids = answer_data['answer']
                        choices = Choice.objects.filter(pk__in=choices_ids)

                        # Correct way to set many-to-many relationship
                        mcq_many_answer = McqManyAnswer.objects.create(
                            question=question,
                            user=request.user
                        )
                        mcq_many_answer.choices.set(choices)  # Use set() to set the many-to-many relationship

                    elif question.question_type == 'binary':
                        answer_option = answer_data['answer']
                        BinaryAnswer.objects.create(
                            question=question,
                            user=request.user,
                            answer_option=answer_option
                        )

                result['result'] = 'Answers saved successfully'
            else:
                result['error_reason'] = 'Invalid data format'
        else:
            result['error_reason'] = 'User is not authenticated'

        return Response(result, status=status.HTTP_200_OK)
