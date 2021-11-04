from django.urls import path, include

from apps.surveys.api.v1.views import (
    FormAnswerListView,
    FormAnswerRUDView,
    FormAnswerListCreateView,
    FormRespondent,
    FormSurveyQuestionsListView,
    FormSurveyRetrieveView,
    SubmitFormView,
    SurveyListCreateView,
    ActiveSurveyListView,
    SurveyQuestionsListCreateView,
    SurveyRUDView,
    FormListView,
    FormRetrieveView,
    SurveyStartView,
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

        path('<int:pk>/start/', SurveyStartView.as_view(), name='start_survey'),

    ])),

    # path('questions/', include([
    #     path('', name='all_questions'),
    #     path('<int:pk>/', name='question_detail'),
    #     path('<int:pk>/answers/', name='question_answers'),
    # ])),


    path('forms/', include([
        path('answers/', include([
            path('', FormAnswerListView.as_view(), name='all_form_answers'),
            path('<int:pk>/', FormAnswerRUDView.as_view(), name='form_answer_detail'),
        ])),
        
        path('', FormListView.as_view(), name='all_forms'),
        path('<slug:pk>/', FormRetrieveView.as_view(), name='form_detail'),
        path('<slug:pk>/respondent/', FormRespondent.as_view(), name='form_respondent'),

        path('<slug:pk>/survey/', FormSurveyRetrieveView.as_view(), name='form_survey'),
        path('<slug:pk>/survey/questions/', FormSurveyQuestionsListView.as_view(), name='form_survey_questions'),

        path('<slug:pk>/answers/', FormAnswerListCreateView.as_view(), name='form_answers'),

        path('<slug:pk>/submit/', SubmitFormView.as_view(), name='form_submit'),

    ])),

]