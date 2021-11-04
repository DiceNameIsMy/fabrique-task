from django.db import transaction
from django.utils import timezone

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
        fields = ('pk', 'first_name', 'last_name', 'age', 'form')

    def to_internal_value(self, data):
        view = self.context['view']
        lookup_field = view.lookup_url_kwarg or view.lookup_field

        data = data.copy()
        data['form'] = view.kwargs[lookup_field]
        return super().to_internal_value(data)

    def save(self, **kwargs):
        # OneToOne form field doesn's save correctly 
        # for some reason so i made it this way
        form = self.validated_data.pop('form')
        respondent = super().save(**kwargs)
        form.respondent = respondent
        form.save()
        return respondent


class FormCreateSerizlier(serializers.ModelSerializer):
    class Meta:
        model = Form
        fields = (
            'pk', 'survey'
        )   

    def to_internal_value(self, data):
        view = self.context['view']
        lookup_field = view.lookup_url_kwarg or view.lookup_field

        data = data.copy()
        data['survey'] = view.kwargs[lookup_field]
        return super().to_internal_value(data)


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

    def to_internal_value(self, data):
        view = self.context['view']
        lookup_field = view.lookup_url_kwarg or view.lookup_field

        data = data.copy()
        data['form'] = view.kwargs[lookup_field]
        return super().to_internal_value(data)


class SubmitFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        fields = ('pk',)

    def validate(self, attrs):
        form = self.instance
        if form.submitted:
            raise serializers.ValidationError(
                'form is already submitted'
            )

        form_answers = form.answers.all()
        form_survey_questions = form.survey.questions.all()
        unanswered_questions_amount = len(form_survey_questions) - len(form_answers)
        if unanswered_questions_amount:
            raise serializers.ValidationError(
                f'survey form should answer to all questions. {unanswered_questions_amount} left.'
            )

        return attrs

    def update(self, instance, validated_data):
        instance.submitted = True
        instance.submitted_date = timezone.now()
        instance.save()
        return instance

