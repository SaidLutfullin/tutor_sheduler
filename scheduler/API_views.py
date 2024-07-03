from datetime import datetime, timedelta

from django.db.models import Q

from rest_framework import generics
from rest_framework.response import Response
from loguru import logger
from rest_framework.views import APIView

from scheduler.mixins import TeacherRequiredMixin
from scheduler.models import Student, Lesson
from scheduler.serializers import LessonSerializer, StudentNestedSerializer, AppointLessonSerializer, \
    PaymentDateSerializer, LessonSetPerformedSerializer, LessonSetRegularSerializer, AppointRegularLessonsSerializer

from scheduler.services import cancel_regularity, appoint_regular_lessons, get_income_statistics
import pytz


class StudentsAPIView(TeacherRequiredMixin,generics.ListAPIView):
    serializer_class = StudentNestedSerializer

    def get_queryset(self):
        return Student.objects.filter(tutor=self.request.user,
                                      is_active=True)


class LessonsAPIView(TeacherRequiredMixin, generics.ListCreateAPIView):
    queryset = Lesson.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return LessonSerializer
        elif self.request.method == 'POST':
            return AppointLessonSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        monday_date = datetime.strptime(self.request.GET.get('monday_date'), '%Y-%m-%dT%H:%M')
        next_monday_date = monday_date + timedelta(weeks=1) + timedelta(days=1)

        start_time_condition = Q(start_time__gte=monday_date, start_time__lt=next_monday_date)
        finish_time_condition = Q(finish_time__lte=next_monday_date, finish_time__gt=monday_date)
        tutor_condition = Q(student__tutor__pk=self.request.user.pk)
        queryset = queryset.filter((start_time_condition | finish_time_condition) & tutor_condition)

        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save()


class LessonsDeleteAPIView(TeacherRequiredMixin, generics.DestroyAPIView):
    def get_queryset(self):
        return Lesson.objects.filter(student__tutor__pk=self.request.user.pk)


class LessonSetPerformedAPIView(TeacherRequiredMixin, generics.UpdateAPIView):
    serializer_class = LessonSetPerformedSerializer

    def get_queryset(self):
        return Lesson.objects.filter(student__tutor__pk=self.request.user.pk)


class LessonSetRegularAPIView(TeacherRequiredMixin, generics.UpdateAPIView):
    serializer_class = LessonSetRegularSerializer

    def get_queryset(self):
        return Lesson.objects.filter(student__tutor__pk=self.request.user.pk)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data['is_regular'] == False:
            cancel_regularity(instance)
        self.perform_update(serializer)

        custom_data = {'message': 'Дополнительная логика была выполнена успешно'}
        return Response({**serializer.data, **custom_data})


class AppointRegularLessonsAPIView(TeacherRequiredMixin, generics.CreateAPIView):
    serializer_class = AppointRegularLessonsSerializer

    def get_queryset(self):
        return Lesson.objects.filter(student__tutor__pk=self.request.user.pk)

    def perform_create(self, serializer):
        errors = appoint_regular_lessons(serializer.validated_data, self.request.user.time_zone)


class GetIncomeStatisticsAPIView(TeacherRequiredMixin, APIView):
    def get(self, request, *args, **kwargs):
        tutor_id = self.request.user.pk
        tutor_time_zone = str(self.request.user.time_zone)

        from_date = datetime.strptime(self.request.GET.get('from_date'), '%Y-%m-%d')
        from_date = from_date.replace(hour=0, minute=0, second=0, microsecond=0,
                                      tzinfo=pytz.timezone(tutor_time_zone)).astimezone(pytz.utc)

        to_date = datetime.strptime(self.request.GET.get('to_date'), '%Y-%m-%d') + timedelta(days=1)
        to_date = to_date.replace(hour=0, minute=0, second=0, microsecond=0,
                                  tzinfo=pytz.timezone(tutor_time_zone)).astimezone(pytz.utc)

        return Response(get_income_statistics(tutor_id, from_date, to_date))
