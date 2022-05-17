import datetime

from django.db import models
from django.shortcuts import render, redirect, reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse

from .models import *
from .forms import LoginForm, RegisterForm
from . import utils
from .models import Subject, School, Class, Mark, TeacherProfile, StudentProfile, WorkingPlan


def page_404(request):
    return render(request, '404.html', status=404)


def index(request):
    context = {}
    return render(request, 'main/index.html', context=context)


def about(request):
    context = {}
    return render(request, 'main/about.html', context=context)


def support(request):
    context = {}
    return render(request, 'main/support.html', context=context)


def for_partners(request):
    context = {}
    return render(request, 'main/for_partners.html', context=context)


@login_required(login_url='/login')
def profile(request):
    context = {}
    if request.method == 'GET':
        try:
            student_profile = StudentProfile.objects.get(user=request.user)
            context = {
                'student': student_profile
            }
        except StudentProfile.DoesNotExist:
            try:
                teacher_profile = TeacherProfile.objects.get(user=request.user)
                context = {
                    'teacher': teacher_profile,
                    'classes': teacher_profile.classes.all()
                }
            except TeacherProfile.DoesNotExist:
                return render(request, '404.html')
    return render(request, 'main/profile.html', context=context)


def log_in(request):
    if request.user.is_authenticated:
        return redirect('profile')
    if request.method == 'POST':
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    return redirect('main:profile')
                else:
                    login_form.add_error('__all__', 'Ошибка! Пользователь неактивен!')
            else:
                login_form.add_error('__all__', 'Ошибка! Проверьте введённые данные!')
    else:
        login_form = LoginForm()
    context = {
        'form': login_form,
    }
    return render(request, 'main/login.html', context=context)


def log_out(request):
    logout(request)
    return redirect('/login')


def sign_up(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            name = form.cleaned_data['name']
            surname = form.cleaned_data['surname']
            role = form.cleaned_data['role']
            city = form.cleaned_data['city']
            organization = form.cleaned_data['organization']
            StudentProfile.objects.create(
                user=user,
                name=name,
                surname=surname,
                city=city,
                role=role,
                organization=organization
            )
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/')
    else:
        form = RegisterForm()
    context = {
        'form': form,
    }
    return render(request, 'main/sign_up.html', context=context)


@login_required(login_url='/login')
def schedule(request):
    context = {}
    return render(request, 'main/schedule.html', context=context)


@login_required(login_url='/login')
def my_marks(request, period=''):
    try:
        user_profile = StudentProfile.objects.get(user=request.user)
    except:
        return redirect('/')
    if user_profile:
        if period not in (f'{i}' for i in range(5)):
            period = utils.get_quarter()
            return redirect(reverse('main:my_marks', args=(period,)))
        subjects = Subject.objects.all()
        context = {
            'period': period,
            'subjects': subjects,
            'student': user_profile,
            'marks_info': user_profile.get_marks_info(period)
        }
        return render(request, 'main/my_marks.html', context=context)


@login_required(login_url='/login')
def change_marks(request, edu_class='', period=''):
    teacher_profile = TeacherProfile.objects.get(user=request.user)
    if teacher_profile:
        classes = teacher_profile.classes.all()
        if len(classes) > 0:
            quarter = utils.get_quarter()
            if not edu_class:
                return redirect(
                    reverse('main:change-marks', args=(teacher_profile.classes.all()[0].full_class, quarter)))
            if period not in (f'{i}' for i in range(5)):
                period = quarter
                return redirect(reverse('main:change-marks', args=(edu_class, period)))
        else:
            return redirect('main:profile')

        context = {
            'teacher': teacher_profile,
            'edu_class': edu_class,
            'period': period,
            'now_year': datetime.datetime.now().year,
            'months': [],
            'students': []
        }
        context = utils.get_previous_context(context, Class)

        # обработка POST запросов
        if request.method == 'POST':
            subject = request.POST.get('select-subject')
            if subject:
                context['subject'] = Subject.objects.get(name=subject)

        context['marks'] = Mark.objects.filter(subject=context['subject'], student__edu_class=context['class_obj'])
        context['work_plans'] = WorkingPlan.objects.filter(subject=context['subject'],
                                                           edu_class=context['class_obj'])

        context = utils.get_months_info(context, WorkingPlan)

        # достаем все оценки всех студентов
        context = utils.get_students_info(context, Mark, StudentProfile)

        return render(request, 'main/change_marks.html', context=context)


def mark_back(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action in ('add', 'change', 'delete'):
            new_value = request.POST.get('new_value', None)
            new_comment = request.POST.get('new_comment', None)
            if action == 'add':
                subject = request.POST.get('subject', None)
                edu_class = request.POST.get('edu_class', None)
                mark_date = request.POST.get('mark_date', None)
                student_id = request.POST.get('student_id', None)
                if new_value and new_comment and subject and edu_class and mark_date and student_id:
                    work_type = request.POST.get('work_type', None)
                    mark_date = datetime.date.fromordinal(int(mark_date))
                    if not work_type:
                        work_type = 'ОТВ'
                        class_letter = edu_class[-1]
                        class_number = edu_class[:len(edu_class) - 1]
                        WorkingPlan.objects.get_or_create(
                            edu_class=Class.objects.get(number=class_number, letter=class_letter),
                            subject=Subject.objects.get(name=subject),
                            work_type=work_type,
                            date=mark_date
                        )
                    Mark.objects.get_or_create(
                        student=StudentProfile.objects.get(id=student_id),
                        subject=Subject.objects.get(name=subject),
                        mark=new_value,
                        comment=new_comment,
                        date=mark_date,
                        work_type=work_type
                    )
                    return JsonResponse({'success': True})
            mark_id = request.POST.get('mark_id', None)
            if mark_id:
                mark = Mark.objects.get(id=int(mark_id))
                if action == 'change':
                    if new_value and new_comment:
                        mark.mark = new_value
                        mark.comment = new_comment
                        mark.save()
                else:
                    mark.delete()
                return JsonResponse({'success': True})
        return JsonResponse({'success': False, 'msg': 'Ошибка, проверьте введенные данные.'})


def wt_back(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action in ('add', 'change', 'delete'):
            plan_id = request.POST.get('plan_id')
            new_wt = request.POST.get('new_wt')
            new_plan_text = request.POST.get('new_plan_text')
            if plan_id and new_wt and new_plan_text:
                wp = WorkingPlan.objects.get(id=plan_id)
                maybe_wp = WorkingPlan.objects.filter(work_type=new_wt, date=wp.date)
                if not maybe_wp:
                    attached_mark = Mark.objects.filter(work_type=wp.work_type, date=wp.date)[0]
                    wp.work_type = new_wt
                    wp.plan_text = new_plan_text
                    wp.save()
                    attached_mark.work_type = new_wt
                    attached_mark.save()
                    return JsonResponse({'success': True})
                return JsonResponse({'success': False, 'msg': 'Такой тип работы уже существует.'})


def recovery(request):
    context = {}
    return render(request, 'main/recovery.html', context=context)


def join_oo(request):
    context = {}
    return render(request, 'main/join_oo.html', context=context)
