from django.urls import path, include

from apps.surveys.api.v1.views import (
    AnswerListView,
    AnswerRUDView,
    FormAnswerListView,
    FormAnswerRUDView,
    FormAnswerListCreateView,
    FormRespondent,
    FormSurveyQuestionsListView,
    FormSurveyRetrieveView,
    QuestionAnswersListCreateView,
    QuestionListView,
    QuestionRUDView,
    SubmitFormView,
    SurveyListCreateView,
    ActiveSurveyListView,
    SurveyQuestionsListCreateView,
    SurveyRUDView,
    FormListView,
    FormRetrieveView,
    SurveyStartView,
)

urlpatterns = [
    path('surveys/', include([
        path('', SurveyListCreateView.as_view(), name='all_surveys'),
        path('active/', ActiveSurveyListView.as_view(),  name='all_active_surveys'),
        
        path('<int:pk>/', SurveyRUDView.as_view(), name='survey_detail'),
        path('<int:pk>/questions/', SurveyQuestionsListCreateView.as_view(), name='survey_questions'),
        # # TODO endpoint to get stats about a survey

        path('<int:pk>/start/', SurveyStartView.as_view(), name='start_survey'),

    ])),

    path('questions/', include([
        path('', QuestionListView.as_view(), name='all_questions'),
        path('<int:pk>/', QuestionRUDView.as_view(), name='question_detail'),
        path('<int:pk>/answers/', QuestionAnswersListCreateView.as_view(), name='question_answers'),
    ])),

    path('answers/', include([
        path('', AnswerListView.as_view(), name='all_answers'),
        path('<int:pk>/', AnswerRUDView.as_view(), name='answer_detail'),
    ])),

    path('forms/', include([
        path('', FormListView.as_view(), name='all_forms'),
        path('<slug:pk>/', FormRetrieveView.as_view(), name='form_detail'),
        path('<slug:pk>/respondent/', FormRespondent.as_view(), name='form_respondent'),

        path('<slug:pk>/survey/', FormSurveyRetrieveView.as_view(), name='form_survey'),
        path('<slug:pk>/survey/questions/', FormSurveyQuestionsListView.as_view(), name='form_survey_questions'),

        path('<slug:pk>/answers/', FormAnswerListCreateView.as_view(), name='form_answers'),

        path('<slug:pk>/submit/', SubmitFormView.as_view(), name='form_submit'),

        path('answers/', include([
            path('', FormAnswerListView.as_view(), name='all_answers'),
            path('<int:pk>/', FormAnswerRUDView.as_view(), name='answer_detail'),
        ])),
    ])),

]