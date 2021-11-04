from django.contrib import admin

from .models import (
    Survey, 
    Question,
    Answer,
    Respondent, 
    Form,
    FormAnswer
)

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0

class FormAnswerInline(admin.TabularInline):
    model = FormAnswer
    extra = 0


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    pass

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]


@admin.register(Respondent)
class RespondentAdmin(admin.ModelAdmin):
    pass

@admin.register(Form)
class SurveyAdmin(admin.ModelAdmin):
    inlines = [FormAnswerInline]
