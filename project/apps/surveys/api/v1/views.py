from django.http import Http404

from rest_framework.generics import (
    get_object_or_404,
    GenericAPIView,
    CreateAPIView,
    ListAPIView,
    ListCreateAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
    UpdateAPIView
)
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAuthenticated, 
    IsAdminUser, 
)
from apps.surveys.models import (
    Survey, 
    Question,
    Answer,
    Respondent, 
    Form,
    FormAnswer
)
from apps.surveys.permissions import IsAdminOrCreateOnly, IsAdminOrReadOnly
from apps.surveys.filters import ActiveSurveysFilter
from apps.utils.filters import URLRelatedFilter
from .serializers import (
    AnswerSerializer,
    FormAnswerCreateSerializer,
    FormCreateSerizlier,
    RespondentSerializer,
    SubmitFormSerializer,
    SurveySerializer,
    QuestionSerializer,
    FormSerializer,
    FormAnswerSerializer,
)

class CreateRetrieveUpdateDestroyAPIView(
    RetrieveUpdateDestroyAPIView,
    CreateAPIView
):
    def create(self, request, *args, **kwargs):
        try:
            self.get_object()
            return Response(
                {'detail': 'object already exists'},
                status=400
            )
        except Http404:
            return super().create(request, *args, **kwargs)


# Survey
class SurveyListCreateView(ListCreateAPIView):
    """ Show all or Create Survey
    """
    permission_classes = (IsAuthenticated, IsAdminUser)

    serializer_class = SurveySerializer
    queryset = Survey.objects.all()


class ActiveSurveyListView(ListAPIView):
    """ Show all active surveys
    """
    serializer_class = SurveySerializer
    queryset = Survey.objects.all()

    filter_backends = (ActiveSurveysFilter,)


class SurveyRUDView(RetrieveUpdateDestroyAPIView):
    """ Change survey
    """
    permission_classes = (IsAuthenticated, IsAdminUser)

    serializer_class = SurveySerializer
    queryset = Survey.objects.all()


# Survey related
class SurveyQuestionsListCreateView(ListCreateAPIView):
    """ Show all or Create Question for survey
    """
    permission_classes = (IsAdminOrReadOnly, )

    serializer_class = QuestionSerializer
    queryset = Question.objects.all()

    filter_backends = [URLRelatedFilter]
    url_related_field = 'survey_id'
    url_related_kwarg = 'pk'


class SurveyStartView(CreateAPIView):
    """ Start a survey
    """
    serializer_class = FormCreateSerizlier
    queryset = Form.objects.all()


# Question
class QuestionListView(ListAPIView):
    """ All questions
    """
    permission_classes = (IsAdminUser, )

    serializer_class = QuestionSerializer
    queryset = Question.objects.all()


class QuestionRUDView(RetrieveUpdateDestroyAPIView):
    """ Change question
    """
    permission_classes = (IsAdminUser, )

    serializer_class = QuestionSerializer
    queryset = Question.objects.all()


# Question related
class QuestionAnswersListCreateView(ListCreateAPIView):
    """ Question answers
    """
    permission_classes = (IsAdminUser, )

    serializer_class = AnswerSerializer
    queryset = Answer.objects.all()


# Answer
class AnswerListView(ListAPIView):
    """ All questions
    """
    permission_classes = (IsAdminUser, )

    serializer_class = AnswerSerializer
    queryset = Answer.objects.all()


class AnswerRUDView(RetrieveUpdateDestroyAPIView):
    """ Change question
    """
    permission_classes = (IsAdminUser, )

    serializer_class = AnswerSerializer
    queryset = Answer.objects.all()


# Form
class FormListView(ListCreateAPIView):
    """ Show all forms
    """
    permission_classes = (IsAdminUser, )

    serializer_class = FormSerializer
    queryset = Form.objects.all()


class FormRetrieveView(RetrieveAPIView):
    """ Get form detail
    """
    serializer_class = FormSerializer
    queryset = Form.objects.all()


# Form related
class FormRespondent(CreateRetrieveUpdateDestroyAPIView):
    """ Create or change respondent
    """
    serializer_class = RespondentSerializer
    
    def get_object(self):
        lookup_field = self.lookup_url_kwarg or self.lookup_field
        form_pk = self.kwargs[lookup_field]
        return get_object_or_404(Respondent, form__pk=form_pk)


class FormSurveyRetrieveView(RetrieveAPIView):
    """ View survey of current form
    """
    serializer_class = SurveySerializer
    
    def get_object(self):
        lookup_field = self.lookup_url_kwarg or self.lookup_field
        form_pk = self.kwargs[lookup_field]
        return get_object_or_404(Survey, forms__pk=form_pk)


class FormSurveyQuestionsListView(ListAPIView):
    """ View questions of survey of current form
    """
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
    
    filter_backends = [URLRelatedFilter]
    url_related_field = 'survey__forms__pk'
    url_related_kwarg = 'pk'


class FormAnswerListCreateView(ListCreateAPIView):
    """ Show all form answers or create (one or many are avaliable)
    """
    serializer_class = FormAnswerCreateSerializer
    queryset = FormAnswer.objects.all()

    filter_backends = [URLRelatedFilter]
    url_related_field = 'form__pk'
    url_related_kwarg = 'pk'

    def get_serializer(self, *args, **kwargs):
        if isinstance(self.request.data, list):
            kwargs['many'] = True
        return super().get_serializer(*args, **kwargs)


class SubmitFormView(UpdateAPIView):
    """ Submit form
    """
    serializer_class = SubmitFormSerializer
    queryset = Form.objects.all()


# FormAnswer
class FormAnswerListView(ListAPIView):
    """ Show all answers to form
    """
    permission_classes = (IsAuthenticated, IsAdminUser)

    serializer_class = FormAnswerSerializer
    queryset = FormAnswer.objects.all()


class FormAnswerRUDView(RetrieveUpdateDestroyAPIView):
    """ Change form answer
    """
    serializer_class = FormAnswerSerializer
    queryset = FormAnswer.objects.all()

