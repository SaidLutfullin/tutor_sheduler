from django.db import models
from django.db.models import Q


from users.models import User
from timezone_field import TimeZoneField
from django.core.exceptions import ValidationError
from loguru import logger
import json

from django.db import transaction


class Student(models.Model):
    tutor = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    city = models.CharField(max_length=50,)
    phone = models.CharField(max_length=50, blank=True, null=True)
    time_zone = TimeZoneField(default='UTC')
    additional_information = models.TextField(blank=True, null=True)
    subjects = models.JSONField(blank=True, null=True, default=[""])
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)

    def validate_json_array(value):
        try:
            decoded_value = json.loads(value)
            if not isinstance(decoded_value, list):
                raise ValidationError('Введенное значение не является массивом.')
        except (json.JSONDecodeError, TypeError):
            raise ValidationError('Введите корректный JSON-массив.')


class Lesson(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    subject = models.CharField(max_length=50, blank=True, null=True)
    start_time = models.DateTimeField()
    finish_time = models.DateTimeField()
    price = models.DecimalField(decimal_places=2, max_digits=10)
    performed = models.BooleanField(default=False)
    is_regular = models.BooleanField(default=False)

    def __str__(self):
        return (f"pk: {self.pk},"
                f"student: {self.student},"
                f"subject: {self.subject},"
                f"start_time: {self.start_time},"
                f"finish_time: {self.finish_time},"
                f"price: {self.price},"
                f"performed: {self.performed},"
                f"is_regular: {self.is_regular}, ")

    def clean(self):
        start_time_condition = Q(start_time__gte=self.start_time, start_time__lt=self.finish_time)
        finish_time_condition = Q(finish_time__gt=self.start_time, finish_time__lte=self.finish_time)
        full_overlap_condition = Q(start_time__lte=self.start_time, finish_time__gte=self.finish_time)

        if Lesson.objects.filter(
                start_time_condition | finish_time_condition | full_overlap_condition
        ).exclude(pk=self.pk).exists():
            raise ValidationError('Time slots overlap with other recordings.')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        with transaction.atomic():
            if hasattr(self, 'transaction'):
                self.transaction.delete()
            super().delete(*args, **kwargs)

    class Meta:
        ordering = ['start_time']


class Transaction(models.Model):
    student = models.ForeignKey(Student, on_delete=models.PROTECT)
    lesson = models.OneToOneField(Lesson, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField()
    bill = models.TextField(blank=True, null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=10)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.change_student_balance(self.amount)
    
    def delete(self, *args, **kwargs):
        self.change_student_balance(-self.amount)
        super().delete(*args, **kwargs)
    
    def change_student_balance(self, amount):
        student = Student.objects.get(pk=self.student.pk)
        student.balance += amount
        student.save()

    class Meta:
        ordering = ['-date']