from rest_framework import serializers
from scheduler.models import Lesson, Student, Transaction
from django.db import transaction


class TimeZoneFieldSerializer(serializers.Field):
    def to_representation(self, value):
        return str(value)


class StudentNestedSerializer(serializers.ModelSerializer):
    time_zone = TimeZoneFieldSerializer()

    class Meta:
        model = Student
        fields = ('id', 'name', 'city', 'phone', 'time_zone', 'additional_information', 'subjects')


class LessonSerializer(serializers.ModelSerializer):
    student = StudentNestedSerializer()

    class Meta:
        model = Lesson
        fields = '__all__'


class AppointLessonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['student', 'subject', 'start_time', 'finish_time', 'price', 'is_regular']


class PaymentDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = ['payment_date']


class LessonSetPerformedSerializer(serializers.ModelSerializer):

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance = super().update(instance, validated_data)
            if instance.performed:
                Transaction(student=instance.student,
                            lesson_id=instance.pk,
                            date=instance.finish_time,
                            amount=-instance.price).save()
            else:
                Transaction.objects.get(lesson_id=instance.pk).delete()
            return instance

    class Meta:
        model = Lesson
        fields = ['performed']


class LessonSetRegularSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        fields = ['is_regular']


class AppointRegularLessonsSerializer(serializers.Serializer):
    monday_date = serializers.DateTimeField()
