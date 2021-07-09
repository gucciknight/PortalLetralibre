from django.urls import include, path

from classroom.views import classroom, tutors, coordinators

urlpatterns = [
    path('', include('classroom.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/signup/', classroom.SignUpView.as_view(), name='signup'),
    path('accounts/signup/tutor/', tutors.TutorSignUpView.as_view(), name='tutor_signup'),
    path('accounts/signup/coordinator/', coordinators.CoordinatorSignUpView.as_view(), name='coordinator_signup'),
]
