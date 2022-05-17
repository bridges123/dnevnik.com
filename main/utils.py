import datetime
import calendar
from django.db import models

work_types = (('ДЗ', 'Домашняя работа'), ('КР', 'Контрольная работа'),
              ('СР', 'Самостоятельная работа'), ('ОТВ', 'Работа на уроке'))

QUARTERS = {
    '1': (9, 10),
    '2': (11, 12),
    '3': (1, 2, 3),
    '4': (4, 5)
}

MONTHS = [
    'Январь',
    'Февраль',
    'Март',
    'Апрель',
    'Май',
    'Июнь',
    'Июль',
    'Август',
    'Сентябрь',
    'Октябрь',
    'Ноябрь',
    'Декабрь'
]


# получение текущей четверти
def get_quarter():
    month = datetime.datetime.now().month
    quarter = '1'
    for q, ms in QUARTERS.items():
        if month in ms:
            quarter = q
    return quarter


# проверка на правильность телефона
def phone_validator(phone):
    if len(phone) != 11 or phone[0] not in ('7', '8'):
        raise ValidationError('Введите корректный номер телефона. Номер телефона должен начинаться на 7 или 8')


def get_previous_context(context, Class):
    edu_class = context['edu_class']
    number = str(edu_class)[:len(edu_class) - 1]
    letter = str(edu_class)[-1]

    class_obj = Class.objects.get(number=number, letter=letter)
    subjects = class_obj.subjects.all()
    subject = subjects[0]

    context['class_obj'] = class_obj
    context['subjects'] = subjects
    context['subject'] = subject
    context['mark_types'] = ('2', '3', '4', '5', 'П', 'Б')
    context['work_types'] = work_types
    return context


def get_months_info(context, WorkingPlan):
    now = datetime.datetime.now()
    months_nums = QUARTERS[context['period']]
    for m in months_nums:
        y = now.year if m >= now.month else now.year + 1
        y = 2022
        days = []
        cells_count = 0
        for d in range(1, calendar.monthrange(y, m)[1] + 1):
            days.append((d, WorkingPlan.objects.filter(date__year=y, date__month=m, date__day=d,
                                                       subject=context['subject'],
                                                       edu_class=context['class_obj'])))
            if len(days[-1][1]) > 0:
                cells_count += len(days[-1][1])
            else:
                cells_count += 1
        context['months'].append((m, MONTHS[m - 1], days, cells_count))
    return context


def get_students_info(context, Mark, StudentProfile):
    now = datetime.datetime.now()
    students = StudentProfile.objects.filter(edu_class=context['class_obj'])
    for student in students:
        all_student_marks = Mark.objects.filter(student=student, subject=context['subject'])
        student_marks = []
        for month in context['months']:
            month_num = month[0]
            y = now.year if month_num >= now.month else now.year + 1
            y = 2022
            month_marks = []
            for day, plans in month[2]:
                pp = []
                for plan in plans:
                    marks = all_student_marks.filter(date__year=y, date__month=month_num, date__day=day,
                                                     work_type=plan.work_type)
                    # проблема с датой, не выдает новые оценки
                    if marks:
                        marks = marks[0]
                    pp.append((marks, plan.work_type))
                month_marks.append((pp, datetime.date(year=y, month=month_num, day=day).toordinal()))
            student_marks.append(month_marks)
        context['students'].append((student, student_marks))
    return context
