from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, ListView, UpdateView

from ..decorators import tutor_required
from ..forms import TutorInterestsForm, TutorSignUpForm, TakeQuizForm
from ..models import Quiz, Tutor, TutorAnswer, TakenQuiz, User


class TutorSignUpView(CreateView):
    model = User
    form_class = TutorSignUpForm
    template_name = 'registration/signup_form.html'

    def get_context_data(self, **kwargs):
        kwargs['user_type'] = 'tutor'
        return super().get_context_data(**kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('tutors:quiz_list')


@method_decorator([login_required, tutor_required], name='dispatch')
class TutorInterestsView(UpdateView):
    model = Tutor
    form_class = TutorInterestsForm
    template_name = 'classroom/tutors/interests_form.html'
    success_url = reverse_lazy('tutors:quiz_list')

    def get_object(self):
        return self.request.user.tutor

    def form_valid(self, form):
        messages.success(self.request, 'Interests updated with success!')
        return super().form_valid(form)

@method_decorator([login_required, tutor_required], name='dispatch')
class UserListView(ListView):
    model = Tutor
    context_object_name = 'info'
    template_name = 'classroom/tutors/lista_de_datos.html'

    def get_name(self):
        tutor = self.request.user.st

@method_decorator([login_required, tutor_required], name='dispatch')
class QuizListView(ListView):
    model = Quiz
    ordering = ('name', )
    context_object_name = 'quizzes'
    template_name = 'classroom/tutors/quiz_list.html'

    def get_queryset(self):
        tutor = self.request.user.tutor
        tutor_interests = tutor.interests.values_list('pk', flat=True)
        taken_quizzes = tutor.quizzes.values_list('pk', flat=True)
        queryset = Quiz.objects.filter(subject__in=tutor_interests) \
            .exclude(pk__in=taken_quizzes) \
            .annotate(questions_count=Count('questions')) \
            .filter(questions_count__gt=0)
        return queryset


@method_decorator([login_required, tutor_required], name='dispatch')
class TakenQuizListView(ListView):
    model = TakenQuiz
    context_object_name = 'taken_quizzes'
    template_name = 'classroom/tutors/taken_quiz_list.html'

    def get_queryset(self):
        queryset = self.request.user.tutor.taken_quizzes \
            .select_related('quiz', 'quiz__subject') \
            .order_by('quiz__name')
        return queryset


@login_required
@tutor_required
def take_quiz(request, pk):
    quiz = get_object_or_404(Quiz, pk=pk)
    tutor = request.user.tutor

    if tutor.quizzes.filter(pk=pk).exists():
        return render(request, 'tutors/taken_quiz.html')

    total_questions = quiz.questions.count()
    unanswered_questions = tutor.get_unanswered_questions(quiz)
    total_unanswered_questions = unanswered_questions.count()
    progress = 100 - round(((total_unanswered_questions - 1) / total_questions) * 100)
    question = unanswered_questions.first()

    if request.method == 'POST':
        form = TakeQuizForm(question=question, data=request.POST)
        if form.is_valid():
            with transaction.atomic():
                tutor_answer = form.save(commit=False)
                tutor_answer.tutor = tutor
                tutor_answer.save()
                if tutor.get_unanswered_questions(quiz).exists():
                    return redirect('tutors:take_quiz', pk)
                else:
                    correct_answers = tutor.quiz_answers.filter(answer__question__quiz=quiz, answer__is_correct=True).count()
                    score = round((correct_answers / total_questions) * 100.0, 2)
                    TakenQuiz.objects.create(tutor=tutor, quiz=quiz, score=score)
                    if score < 50.0:
                        messages.warning(request, 'Better luck next time! Your score for the quiz %s was %s.' % (quiz.name, score))
                    else:
                        messages.success(request, 'Congratulations! You completed the quiz %s with success! You scored %s points.' % (quiz.name, score))
                    return redirect('tutors:quiz_list')
    else:
        form = TakeQuizForm(question=question)

    return render(request, 'classroom/tutors/take_quiz_form.html', {
        'quiz': quiz,
        'question': question,
        'form': form,
        'progress': progress
    })
