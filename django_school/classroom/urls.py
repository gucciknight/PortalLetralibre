from django.urls import include, path

from .views import classroom, tutors, teachers

urlpatterns = [
    path('', classroom.home, name='home'),

    path('tutors/', include(([
        path('', tutors.QuizListView.as_view(), name='quiz_list'),
        path('interests/', tutors.TutorInterestsView.as_view(), name='tutor_interests'),
        path('taken/', tutors.TakenQuizListView.as_view(), name='taken_quiz_list'),
        path('quiz/<int:pk>/', tutors.take_quiz, name='take_quiz'),
        path('miperfil/', tutors.UserListView.as_view(), name='lista_de_datos'),
    ], 'classroom'), namespace='tutors')),

    path('teachers/', include(([
        path('', teachers.QuizListView.as_view(), name='quiz_change_list'),
        path('quiz/add/', teachers.QuizCreateView.as_view(), name='quiz_add'),
        path('quiz/<int:pk>/', teachers.QuizUpdateView.as_view(), name='quiz_change'),
        path('quiz/<int:pk>/delete/', teachers.QuizDeleteView.as_view(), name='quiz_delete'),
        path('quiz/<int:pk>/results/', teachers.QuizResultsView.as_view(), name='quiz_results'),
        path('quiz/<int:pk>/question/add/', teachers.question_add, name='question_add'),
        path('quiz/<int:quiz_pk>/question/<int:question_pk>/', teachers.question_change, name='question_change'),
        path('quiz/<int:quiz_pk>/question/<int:question_pk>/delete/', teachers.QuestionDeleteView.as_view(), name='question_delete'),
    ], 'classroom'), namespace='teachers')),
]
