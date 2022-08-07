from django.urls import path

from . import views

urlpatterns = [
    path('',views.signin,name='signin'),
    path('signinform/', views.signinform, name='signinform'),

    path('register/', views.register, name='register'),
    path('register/registerform/', views.registerform, name='registerform'),

    # path('index/', views.index, name='index'),
    # path('base/', views.base, name='base'),
    path('welcome/', views.welcome, name='welcome'),

    path('personal/', views.personal, name='personal'),
    path('score/', views.score, name='score'),

    path('creategroup/', views.creategroup, name='creategroup'),
    path('creategroupform/', views.creategroupform, name='creategroupform'),
 
    path('joingroup/', views.joingroup, name='joingroup'),
    path('joingroupform/<str:group_serial>/', views.joingroupform, name='joingroupform'),

    path('quitgroup/', views.quitgroup, name='quitgroup'),
    path('quitgroupform/<str:group_serial>/', views.quitgroupform, name='quitgroupform'),

    path('dismissgroup/', views.dismissgroup, name='dismissgroup'),
    path('dismissgroupform/<str:group_serial>/', views.dismissgroupform, name='dismissgroupform'),

    path('submit/', views.submit, name='submit'),
    path('submitform/', views.submitform, name='submitform'),
 
    path('suggestion/', views.suggestion, name='suggestion'),
    path('suggestionform/', views.suggestionform, name='suggestionform'),

    path('signout/', views.signout, name='signout'),

    path('agreemessage/<str:messageid>/', views.agreemessage, name='agreemessage'),
    path('refusemessage/<str:messageid>/', views.refusemessage, name='refusemessage'),
]
