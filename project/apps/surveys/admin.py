from django.contrib import admin

from .models import (
    Survey, 
    Question,
    Answer,
    Respondent, 
    Form,
    FormAnswer
)

class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0

class FormAnswerInline(admin.TabularInline):
    model = FormAnswer
    extra = 0

class FormInline(admin.StackedInline):
    model = Form
    extra = 0


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_date', 'end_date']
    inlines = [QuestionInline]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['survey', 'type']
    inlines = [AnswerInline]


@admin.register(Respondent)
class RespondentAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'age']
    inlines = [FormInline]


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ['survey', 'respondent', 'submitted', 'submitted_date']
    list_filter = ['survey', 'submitted', 'submitted_date']
    inlines = [FormAnswerInline]
