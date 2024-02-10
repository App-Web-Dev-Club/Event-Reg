from django.shortcuts import render

from django.http import JsonResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Form, Question, Choice
from .serializers import FormSerializer, QuestionSerializer , ChoiceSerializer
import json

class FormCreate(LoginRequiredMixin, View):
    def post(self, request):
        result = {"result": "", "error_reason": ""}
        unicode_body = request.body.decode('utf-8')
        dict_post_data = json.loads(unicode_body)

        if len(dict_post_data['questions']) > 0:
            form_data = {
                'title': dict_post_data['form_title'],
                'description': dict_post_data['form_description'],
                'owner': self.request.user.id
            }
            form_serializer = FormSerializer(data=form_data)

            if form_serializer.is_valid():
                form = form_serializer.save()

                for question_item in dict_post_data['questions']:
                    question_data = {
                        'question_text': question_item['text'],
                        'question_type': question_item['type'],
                        'form': form.id
                    }
                    question_serializer = QuestionSerializer(data=question_data)

                    if question_serializer.is_valid():
                        question = question_serializer.save()

                        if question_item['type'] == 'mcq_one' or question_item['type'] == 'mcq_many':
                            for choice_item in question_item['options']:
                                choice_data = {
                                    'choice_text': choice_item,
                                    'question': question.id
                                }
                                choice_serializer = ChoiceSerializer(data=choice_data)

                                if choice_serializer.is_valid():
                                    choice_serializer.save()
                                else:
                                    result['error_reason'] = ChoiceSerializer.errors
                                    break
                    else:
                        result['error_reason'] = question_serializer.errors
                        break

                result['result'] = 'Form saved successfully'

            else:
                result['error_reason'] = form_serializer.errors

        else:
            result['result'] = 'Add a question title'

        return JsonResponse(result)
