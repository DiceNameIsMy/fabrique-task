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
    pass


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
    queryset = Question.objects.all()

    filter_backends = [URLRelatedFilter]
    url_related_field = 'survey_id'
    url_related_kwarg = 'pk'


class SurveyStartView(CreateAPIView):
    serializer_class = FormCreateSerizlier
    queryset = Form.objects.all()


class FormAnswerListView(ListAPIView):
    permission_classes = (IsAuthenticated, IsAdminUser)

    serializer_class = FormAnswerSerializer
    queryset = FormAnswer.objects.all()


class FormAnswerRUDView(RetrieveUpdateDestroyAPIView):
    serializer_class = FormAnswerSerializer
    queryset = FormAnswer.objects.all()


class FormListView(ListCreateAPIView):
    permission_classes = (IsAdminUser, )

    serializer_class = FormSerializer
    queryset = Form.objects.all()


class FormRetrieveView(RetrieveAPIView):
    serializer_class = FormSerializer
    queryset = Form.objects.all()


class FormRespondent(CreateRetrieveUpdateDestroyAPIView):
    serializer_class = RespondentSerializer
    
    def get_object(self):
        lookup_field = self.lookup_url_kwarg or self.lookup_field
        form_pk = self.kwargs[lookup_field]
        return get_object_or_404(Respondent, form__pk=form_pk)


class FormSurveyRetrieveView(RetrieveAPIView):
    serializer_class = SurveySerializer
    
    def get_object(self):
        lookup_field = self.lookup_url_kwarg or self.lookup_field
        form_pk = self.kwargs[lookup_field]
        return get_object_or_404(Survey, forms__pk=form_pk)


class FormSurveyQuestionsListView(ListAPIView):
    serializer_class = QuestionSerializer
    queryset = Question.objects.all()
    
    filter_backends = [URLRelatedFilter]
    url_related_field = 'survey__forms__pk'
    url_related_kwarg = 'pk'


class FormAnswerListCreateView(ListCreateAPIView):
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
    serializer_class = SubmitFormSerializer
    queryset = Form.objects.all()

