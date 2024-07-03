from django.urls import path

from scheduler.template_views import StudentsListView, StudentDetailView, CreatingStudent, UpdatingStudent, \
    TimeTableView, StudentDeleteView, IncomeStatisticsView, TransactionsListView, TransactionCreateView, \
    TransactionUpdateView
from scheduler.API_views import LessonsAPIView, \
    StudentsAPIView, LessonSetPerformedAPIView, LessonsDeleteAPIView, \
    LessonSetRegularAPIView, AppointRegularLessonsAPIView, GetIncomeStatisticsAPIView

urlpatterns = [
    path('students', StudentsListView.as_view(), name='students'),
    path('students/new', CreatingStudent.as_view(), name='new_student'),
    path('students/<int:student_id>', StudentDetailView.as_view(), name='student'),
    path('students/<int:student_id>/update', UpdatingStudent.as_view(), name='update_student'),
    path('students/<int:student_id>/delete/', StudentDeleteView.as_view(), name='student_delete'),
    path('', TimeTableView.as_view(), name='timetable'),
    path('income_statistics', IncomeStatisticsView.as_view(), name='income_statistics'),
    # Transactions
    path('transactions/<int:student_id>', TransactionsListView.as_view(), name='transactions'),
    path('transactions/<int:student_id>/add', TransactionCreateView.as_view(), name='add_transaction'),
    path('transactions/<int:transaction_id>/update', TransactionUpdateView.as_view(), name='update_transaction'),
    # API endpoints
    path('api/v1/lessons/', LessonsAPIView.as_view()),
    path('api/v1/lessons/<int:pk>/delete/', LessonsDeleteAPIView.as_view()),
    path('api/v1/lessons/set_performed/<int:pk>/', LessonSetPerformedAPIView.as_view()),
    path('api/v1/lessons/set_is_regular/<int:pk>/', LessonSetRegularAPIView.as_view()),
    path('api/v1/lessons/appoint_regular_lessons/', AppointRegularLessonsAPIView.as_view()),
    path('api/v1/students/', StudentsAPIView.as_view()),
    path('api/v1/get_income_statistics/', GetIncomeStatisticsAPIView.as_view()),
]