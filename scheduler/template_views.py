
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect

from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, TemplateView, DeleteView

from scheduler.forms import SubjectForm, TransactionForm
from scheduler.mixins import TeacherRequiredMixin
from scheduler.models import Student, Transaction

from django.middleware.csrf import get_token
from loguru import logger

class StudentsListView(TeacherRequiredMixin, ListView):
    model = Student
    context_object_name = "students"
    template_name = 'scheduler/students.html'

    def get_queryset(self):
        return Student.objects.filter(tutor=self.request.user)


class StudentDetailView(TeacherRequiredMixin, DetailView):
    model = Student
    context_object_name = "student"
    pk_url_kwarg = 'student_id'
    template_name = 'scheduler/student.html'

    def get_queryset(self):
        return Student.objects.filter(tutor=self.request.user)


class StudentDeleteView(TeacherRequiredMixin, LoginRequiredMixin, DeleteView):
    model = Student
    template_name = 'scheduler/student_confirm_delete.html'
    context_object_name = 'student'
    pk_url_kwarg = 'student_id'
    success_url = reverse_lazy('students')

    def get_queryset(self):
        return Student.objects.filter(tutor=self.request.user)


class CreatingStudent(TeacherRequiredMixin, CreateView):
    form_class = SubjectForm
    template_name = 'scheduler/student_form.html'
    success_url = reverse_lazy('students')

    def form_valid(self, form):
        form.instance.tutor = self.request.user
        return super().form_valid(form)


class UpdatingStudent(TeacherRequiredMixin, UpdateView):
    model = Student
    form_class = SubjectForm
    pk_url_kwarg = 'student_id'
    template_name = 'scheduler/student_form.html'
    
    def get_success_url(self):
        return self.request.path

    def get_queryset(self):
        return Student.objects.filter(tutor=self.request.user)


class TimeTableView(TeacherRequiredMixin, TemplateView):
    template_name = "scheduler/timetable.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["constants"] = {
            "API_URL": self.request.build_absolute_uri('/') + "api/v1/",
            "userTimeZone": str(self.request.user.time_zone),
            "csrfToken": get_token(self.request),
        }
        return context


class IncomeStatisticsView(TeacherRequiredMixin, TemplateView):
    template_name = "scheduler/income_statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["constants"] = {
            "API_URL": self.request.build_absolute_uri('/') + "api/v1/",
        }
        return context


class TransactionsListView(TeacherRequiredMixin, ListView):
    model = Transaction
    context_object_name = "transactions"
    template_name = 'scheduler/transactions.html'

    def get_queryset(self):
        return self.model.objects.filter(student=self.kwargs.get('student_id'),
                                         student__tutor=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["student"] = Student.objects.get(id=self.kwargs.get('student_id'))
        return context


class TransactionCreateView(TeacherRequiredMixin, CreateView):
    form_class = TransactionForm
    template_name = 'scheduler/transaction_form.html'
    # success_url = reverse_lazy('students')

    def form_valid(self, form):
        form.instance.student = Student.objects.get(id=self.kwargs.get('student_id'))
        self.object = form.update_account()
        return HttpResponseRedirect(self.get_success_url())


class TransactionUpdateView(TeacherRequiredMixin, UpdateView):
    form_class = TransactionForm
    template_name = 'scheduler/transaction_form.html'
    pk_url_kwarg = 'transaction_id'

    def get_queryset(self):
        return Transaction.objects.filter(student__tutor=self.request.user)

    def get_object(self, queryset=None):
        object = super().get_object()
        self.previous_amount = object.amount
        return object

    def form_valid(self, form):

        logger.error(self.previous_amount)
        self.object = form.update_transaction(previous_amount=self.previous_amount)
        return HttpResponseRedirect(self.get_success_url())