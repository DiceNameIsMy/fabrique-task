from rest_framework.generics import (
    ListAPIView,
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
)
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
from apps.surveys.permissions import IsAdminOrReadOnly
from apps.surveys.filters import ActiveSurveysFilter
from .serializers import (
    SurveySerializer,
    QuestionSerializer,
)

class SurveyListCreateView(ListCreateAPIView):
    permission_classes = (IsAuthenticated, IsAdminUser)

    serializer_class = SurveySerializer
    queryset = Survey.objects.all()


class ActiveSurveyListView(ListAPIView):
    serializer_class = SurveySerializer
    queryset = Survey.objects.all()

    filter_backends = (ActiveSurveysFilter,)


class SurveyRUDView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticated, IsAdminUser)

    serializer_class = SurveySerializer
    queryset = Survey.objects.all()


class SurveyQuestionsListCreateView(ListCreateAPIView):
    permission_classes = (IsAdminOrReadOnly, )

    serializer_class = QuestionSerializer

    def get_queryset(self):
        lookup_field = self.lookup_url_kwarg or self.lookup_field
        survey_pk = self.kwargs[lookup_field]
        return Question.objects.filter(survey_id=survey_pk)
