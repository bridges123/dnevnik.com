from django.urls import path
from main.views import *


app_name = 'main'

urlpatterns = [
    path('', index, name='main'),
    path('about', about, name='about'),
    path('support', support, name='support'),
    path('for-partners', for_partners, name='for_partners'),
    path('login', log_in, name='login'),
    path('logout/', log_out, name='logout'),
    path('sign-up', sign_up, name='sign_up'),
    path('profile', profile, name='profile'),
    path('join-oo', join_oo, name='join_oo'),
    path('my-marks/<str:period>', my_marks, name='my_marks'),
    path('change-marks/<str:edu_class>/<str:period>', change_marks, name='change-marks'),
    path('mark-back', mark_back, name='mark-back'),
    path('wt-back', wt_back, name='wt-back'),
    path('recovery', recovery, name='recovery'),
]
