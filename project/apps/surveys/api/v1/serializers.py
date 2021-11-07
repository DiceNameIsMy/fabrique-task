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
        fields = ('pk', 'title', 'start_date', 'end_date', 'is_active')

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
        if not self.instance:
            data = data.copy()
            data['survey'] = self.context['view'].kwargs['pk']
        return super().to_internal_value(data)

    def validate(self, attrs):
        if self.instance:
            if attrs.get('survey'):
                raise serializers.ValidationError(
                    'changing `survey` is not allowed'
                )
        return attrs

    @transaction.atomic
    def create(self, validated_data: dict):
        answers = validated_data.pop('answers', [])
        question = super().create(validated_data)
        if answers:
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
        extra_kwargs = {'question': {'required': True}}
        read_only_fields = ('form_choice', 'form_choices')


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

    def validate(self, attrs):
        if not attrs['survey'].is_active():
            raise serializers.ValidationError(
                'survey to take should be active'
            )
        return attrs


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
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('form', 'question'),
                message='form should have only one answer per question'
            )
        ]

    def validate(self, attrs):
        # TODO improve this ass long validation
        if self.instance:
            # if we are updating add instance fields
            obj_attrs = {
                'form': self.instance.form,
                'question': self.instance.question, 
                'choice': self.instance.choice,
                'choices': self.instance.choices.all()
            }
            obj_attrs.update(attrs)
            attrs = obj_attrs

        question = attrs.get('question')

        if attrs.get('form').survey != question.survey:
            raise serializers.ValidationError(
                'answer to question should be in survey'
            )

        if question.type == Question.TEXT:
           self.validate_text_type(attrs)
        elif question.type == Question.CHOICE:
            self.validate_choice_type(attrs)
        elif question.type == Question.CHECKBOX:
            self.validate_choices_type(attrs)
        
        return attrs

    def validate_form(self, form):
        if form.submitted:
            raise serializers.ValidationError(
                'form is already submitted'
            )

    def validate_text_type(self, attrs):
        self.validate_fields_are_empty(attrs, ['choice', 'choices'])
        if not attrs.get('text'):
            raise serializers.ValidationError(
                '`text` field is required' 
            )
            
    def validate_choice_type(self, attrs):
        self.validate_fields_are_empty(attrs, ['text', 'choices'])
        choice = attrs.get('choice')
        question = attrs.get('question') or getattr(self.instance, 'question')
        if not choice:
            raise serializers.ValidationError(
                '`choice` field is required' 
            )
        if choice not in question.answers.all():
            raise serializers.ValidationError(
                '`choice` should be in question choices' 
            )

    def validate_choices_type(self, attrs):
        self.validate_fields_are_empty(attrs, ['text', 'choice'])
        choices = attrs.get('choices')
        if not choices:
            raise serializers.ValidationError(
                '`choices` field is required' 
            )

        question = attrs.get('question') or getattr(self.instance, 'question')
        not_allowed_choices = set(choices) - set(question.answers.all())
        if not_allowed_choices:
            raise serializers.ValidationError(
                f'`choices` should be in question choices. Unwanted answers: {list(map(lambda obj: obj.pk, not_allowed_choices))}' 
            )

    def validate_fields_are_empty(self, attrs: dict, empty_fields: list):
        for field in empty_fields:
            if attrs.get(field):
                raise serializers.ValidationError(f'`{field}` is not allowed to be provided')


class FormAnswerCreateSerializer(FormAnswerSerializer):
    class Meta:
        model = FormAnswer
        fields = (
            'pk', 'form', 'question', 
            'text', 'choice', 'choices'
        )
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=('form', 'question'),
                message='form should have only one answer per question'
            )
        ]

    def to_internal_value(self, data):
        view = self.context['view']
        lookup_field = view.lookup_url_kwarg or view.lookup_field

        data = data.copy()
        data['form'] = view.kwargs[lookup_field]
        data = super().to_internal_value(data).copy()

        # For some reason passing UUID str to data before 
        # turning values to objects returns it as None so
        # I added form object after transformation
        data['form'] = Form.objects.get(pk=view.kwargs[lookup_field])
        
        return data


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

