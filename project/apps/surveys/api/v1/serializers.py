from django.db import transaction

from rest_framework import serializers

from apps.surveys.models import (
    Survey, 
    Question,
    Answer,
    Respondent, 
    Form,
    FormAnswer
)


class SurveySerializer(serializers.ModelSerializer):
    class Meta:
        model = Survey
        fields = ('pk', 'title', 'start_date', 'end_date')

    def validate(self, attrs):
        if (self.instance is not None) and attrs.get('start_date'):
            raise serializers.ValidationError('changing `start_date` is not allowed')
        return attrs


class _AnswerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ('pk', 'question', 'text')
        extra_kwargs = {
            'question': {'write_only': True}
        }

    def create(self, validated_data):
        validated_data['question'] = self.context['question']
        return super().create(validated_data)


class QuestionSerializer(serializers.ModelSerializer):
    answers = _AnswerCreateSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = ('pk', 'survey', 'type', 'text', 'answers')

    def to_internal_value(self, data):
        data = data.copy()
        data['survey'] = self.context['view'].kwargs['pk']
        return super().to_internal_value(data)

    @transaction.atomic
    def create(self, validated_data: dict):
        answers = validated_data.pop('answers')
        question = super().create(validated_data)
        answers_serializer = _AnswerCreateSerializer(
            data=answers, 
            many=True, 
            context={'question': question}
        )
        answers_serializer.is_valid(raise_exception=True)
        answers_serializer.save()
        return question


class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = (
            'pk', 'question', 
            'text', 'form_choice', 'form_choices'
        )


class RespondentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Respondent
        fields = ('pk', 'first_name', 'last_name', 'age')


class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        fields = (
            'pk', 'respondent', 'survey', 
            'submitted', 'submitted_date'
        )


class FormAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormAnswer
        fields = (
            'pk', 'form', 'question', 
            'text', 'choice', 'choices'
        )


