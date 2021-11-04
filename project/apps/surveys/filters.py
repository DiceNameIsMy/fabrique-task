from django.utils import timezone

from rest_framework import filters


class ActiveSurveysFilter(filters.BaseFilterBackend):
    """
    Return surveys which are active. 
    (current time is between start_date and end_date)
    """
    def filter_queryset(self, request, queryset, view):
        current_time = timezone.now()
        return queryset.filter(
            start_date__lt=current_time,
            end_date__gt=current_time
        )