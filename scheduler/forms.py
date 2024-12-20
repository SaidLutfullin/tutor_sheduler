import zoneinfo

import pytz
from django.forms import ModelForm
from django import forms
from scheduler.models import Student, Transaction
from tinymce.widgets import TinyMCE

from django.db import transaction
from loguru import logger

class AlphabeticalTimezoneSelect(forms.Select):
    def __init__(self, attrs=None, choices=(), *args, **kwargs):
        sorted_choices = sorted(choices, key=lambda x: x[1])
        super().__init__(attrs, sorted_choices, *args, **kwargs)


class SubjectForm(ModelForm):

    class Meta:
        model = Student
        fields = ('name',
                  'is_active',
                  'city',
                  'phone',
                  'time_zone',
                  'additional_information',
                  'subjects',
        )
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input'}),
            'city': forms.TextInput(attrs={'class': 'input'}),
            'phone': forms.TextInput(attrs={'class': 'input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'checkbox'}),
            'additional_information': TinyMCE(attrs={"cols": 80, "rows": 70}),
            'subjects': forms.Textarea(
                attrs={'class': 'input', 'placeholder': 'Enter subjects, separated by commas'}),
        }
        labels = {
            'name': 'Студент',
            'is_active': 'Активный',
            'city': 'Город',
            'phone': 'Телефон',
            'additional_information': 'Дополнительная информация',
            'subjects': 'Предметы',
        }

    time_zone_choices = [(tz, tz) for tz in sorted(pytz.all_timezones)]
    time_zone = forms.ChoiceField(choices=time_zone_choices, widget=forms.Select(attrs={'class': 'select'}))

class TransactionForm(ModelForm):
    def update_account(self):
        with transaction.atomic():
            object = super().save()
            return object

    def update_transaction(self, previous_amount):
        with transaction.atomic():
            object = super().save()
            object.change_student_balance(-previous_amount)
            return object

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if self.instance and self.instance.date:
            user_timezone = self.instance.student.tutor.time_zone
            local_date = self.instance.date.astimezone(user_timezone)
            self.initial['date'] = local_date.strftime('%Y-%m-%dT%H:%M')

    def clean_date(self):
        date = self.cleaned_data['date']
        user_timezone = self.instance.student.tutor.time_zone

        aware_date = date.replace(tzinfo=user_timezone)

        utc_time = aware_date.astimezone(zoneinfo.ZoneInfo("UTC"))
        return utc_time.replace(tzinfo=None)

    class Meta:
        model = Transaction
        fields = ('date', 'amount', 'bill')
        widgets = {
            'date': forms.DateTimeInput(attrs={'class': 'input',
                                               'type': 'datetime-local'},
                                        format='%Y-%m-%d %H:%M:%S'),
            'amount': forms.NumberInput(attrs={'class': 'input'}),
            'bill': TinyMCE(attrs={"cols": 80, "rows": 70}),
        }
        labels = {
            'date': 'Дата',
            'amount': 'Сумма',
            'bill': 'Чек (комментарии)',
        }
