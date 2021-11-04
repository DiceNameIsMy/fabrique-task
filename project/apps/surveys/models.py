import uuid

from django.utils import timezone
from django.db import models


class Survey(models.Model):
    title = models.CharField(max_length=128)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    # FK questions 
    # FK forms

    def is_active(self):
        current_time = timezone.now()
        return (
            self.start_date <= current_time and
            self.end_date >= current_time
        )

    def __str__(self) -> str:
        return f'{self.title[:15]}, {self.start_date.date()}'


""" I was also considering an alternative implementation
where every question type would be a spearate model.
Also the one where similar question types would be merged 
and have their own types
"""
class Question(models.Model):
    TEXT = 1
    CHOICE = 2
    CHECKBOX = 3
    TYPE_CHOICES = [
        (TEXT, 'Text'),
        (CHOICE, 'Choice'),
        (CHECKBOX, 'Checkbox'),
    ]
        
    survey = models.ForeignKey(
        to=Survey,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    type = models.PositiveSmallIntegerField(
        choices=TYPE_CHOICES,
        default=TEXT
    )
    text = models.CharField(max_length=512)
    # FK answers
    # FK form_answers

    def __str__(self) -> str:
        return f'{self.get_type_display()}: {self.text[:15]}'


class Answer(models.Model):
    question = models.ForeignKey(
        to=Question,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='answers'
    )
    text = models.CharField(max_length=128)
    # FK form_choice 
    # M2M form_choices

    def __str__(self) -> str:
        return self.text[:15]


class Respondent(models.Model):
    first_name = models.CharField(max_length=128)
    last_name = models.CharField(max_length=128)
    age = models.PositiveSmallIntegerField()
    # O2O form

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}, {self.age}'


class Form(models.Model):
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False
    )
    respondent = models.OneToOneField(
        to=Respondent,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='form'
    )
    survey = models.ForeignKey(
        to=Survey,
        on_delete=models.CASCADE,
        related_name='forms'
    )
    submitted = models.BooleanField(
        default=False
    )
    submitted_date = models.DateTimeField(
        null=True, 
        blank=True
    )
    # FK answers

    def __str__(self) -> str:
        respondent_name = getattr(self.respondent, "first_name", "----")
        return f'{respondent_name} : {self.survey}'


class FormAnswer(models.Model):
    form = models.ForeignKey(
        to=Form,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    question = models.ForeignKey(
        to=Question,
        on_delete=models.CASCADE,
        related_name='form_answers'
    )
    text = models.CharField(
        max_length=512,
        blank=True
    )
    # TODO rename related names for 
    # `choice` and `choices` fields

    # Used if question type is CHOICE
    choice = models.ForeignKey(
        to=Answer,
        on_delete=models.CASCADE,
        null=True, 
        blank=True,
        related_name='form_choice'
    )
    # Used if question type is CHECKBOX
    choices = models.ManyToManyField(
        to=Answer,
        blank=True,
        related_name='form_choices'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['form', 'question'], 
                name='unique_answer_to_question_in_form'
            )
        ]

    def __str__(self) -> str:
        return str(self.question)