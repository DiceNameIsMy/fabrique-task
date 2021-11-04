from django.urls import path, include

from apps.surveys.api.v1.views import (
    SurveyListCreateView,
    ActiveSurveyListView,
    SurveyQuestionsListCreateView,
    SurveyRUDView
)

"""

admin:
CRUD surveys, survey start_date is not mutable
CRUD survey questions and answers

users:
get all active surveys
take a survey(only active)
    anonymously or add respondent relation
    return survey form id after completion

get survey form details by id


"""
urlpatterns = [
    path('surveys/', include([
        path('', SurveyListCreateView.as_view(), name='all_surveys'),
        path('active/', ActiveSurveyListView.as_view(),  name='all_active_surveys'),
        
        path('<int:pk>/', SurveyRUDView.as_view(), name='survey_detail'),
        path('<int:pk>/questions/', SurveyQuestionsListCreateView.as_view(), name='survey_questions'),
        # # TODO endpoint to get stats about a survey

        # path('<int:pk>/start/', name='start_survey'),

    ])),

    # path('questions/', include([
    #     path('', name='all_questions'),
    #     path('<int:pk>/', name='question_detail'),
    #     path('<int:pk>/answers/', name='question_answers'),
    # ])),

    # path('answers/', include([
    #     path('', name='all_answers'),
    #     path('<int:pk>/', name='answer_detail'),
    # ])),

    # path('forms/', include([
    #     path('', name='all_forms'),
    #     path('<int:pk>/', name='form_detail'),
    #     path('<int:pk>/respondent/', name='form_respondent'),

    #     path('<int:pk>/survey/', name='form_survey'),
    #     path('<int:pk>/survey/questions/', name='form_survey_questions'),

    #     path('<int:pk>/answers/', name='form_answers'),

    #     path('<int:pk>/submit/', name='form_submit'),
    # ])),

]