import pytz
from django.core.exceptions import ValidationError
from django.db.models import Q, Sum
from datetime import datetime, timedelta

from scheduler.models import Lesson
from loguru import logger


def cancel_regularity(instance):
    weekday = instance.start_time.weekday()+1
    start_time = instance.start_time.time()
    regular_lessons = Lesson.objects.filter(
        Q(start_time__iso_week_day=weekday) &
        Q(start_time__time=start_time) &
        Q(student=instance.student) &
        Q(subject=instance.subject) &
        Q(is_regular=True)
    )
    regular_lessons = regular_lessons.exclude(pk=instance.pk)
    regular_lessons.update(is_regular=False)


def appoint_regular_lessons(serializer_date, user_timezone):
    monday_date = serializer_date.get('monday_date')
    next_monday_date = monday_date + timedelta(weeks=1)
    regular_lessons = Lesson.objects.filter(is_regular=True, start_time__lt=next_monday_date)
    errors=[]

    target_monday = monday_date.astimezone(user_timezone)

    for lesson in regular_lessons:

        target_start_time = lesson.start_time.astimezone(user_timezone)

        start_time = target_monday.replace(hour=target_start_time.hour,
                                           minute=target_start_time.minute)
        start_time = start_time + timedelta(days=target_start_time.weekday())

        start_time = start_time.astimezone(pytz.utc)

        lesson_duration = lesson.finish_time - lesson.start_time
        finish_time = start_time + lesson_duration
        new_lesson = Lesson(
            student=lesson.student,
            subject=lesson.subject,
            start_time=start_time,
            finish_time=finish_time,
            price=lesson.price,
            is_regular=True
        )
        try:
            new_lesson.save()
        except ValidationError:
            errors.append(lesson)
    return errors


def get_income_statistics(tutor_id, from_date, to_date):
    lessons = Lesson.objects.filter(student__tutor_id=tutor_id,
                                    start_time__gte=from_date,
                                    start_time__lt=to_date,
                                    payment_date__isnull=False,
                                    performed=True)
    statistics = {
        "income": lessons.aggregate(Sum('price'))['price__sum']
    }
    return statistics

# TODO доделать
# def overlapped_regular_lessons(new_lesson_data):
#
#     start_weekday = new_lesson_data.get('start_time').weekday() + 1
#     start_time = new_lesson_data.get('start_time').time()
#
#     finish_weekday = new_lesson_data.get('finish_time').weekday() + 1
#     finish_time = new_lesson_data.get('finish_time').time()
#
#     start_time_condition = Q(start_time__iso_week_day=start_weekday,
#                              start_time__gte=new_lesson_data['start_time'],
#                              finish_time__lte=new_lesson_data['start_time'])
#     finish_time_condition = Q(start_time__gte=new_lesson_data['finish_time'],
#                               finish_time__lte=new_lesson_data['finish_time'])
#     logger.error(type(weekday))
#
#     regular_lessons = Lesson.objects.filter(
#         Q(start_time__iso_week_day=weekday) &
#         Q(start_time__time=start_time) &
#         Q(is_regular=True)
#     )