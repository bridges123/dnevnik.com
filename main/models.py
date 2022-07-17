import datetime
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from . import utils

FIRST_LETTER_ID = 1040


# модель Учебного Предмета
class Subject(models.Model):
    name = models.CharField(max_length=32, verbose_name='Название предмета', unique=True, default='')

    def __str__(self):
        return f'{self.name}'


# модель Школы
class School(models.Model):
    school_type = models.CharField(max_length=10, verbose_name='Тип школы', default='',
                                   choices=(('МБОУ', 'МБОУ'), ('Гимназия', 'Гимназия'),
                                            ('Лицей', 'Лицей'), ('Интернат', 'Интернат')))
    school_name = models.CharField(max_length=32, verbose_name='Название школы', default='')
    city = models.CharField(max_length=32, verbose_name='Город')
    address = models.CharField(max_length=128, verbose_name='Адрес')
    website = models.URLField(verbose_name='Сайт школы', unique=True)
    phone = models.CharField(max_length=11, verbose_name='Номер телефона', unique=True)
    logo = models.ImageField(verbose_name='Логотип', upload_to='logos/', blank=True)

    def __str__(self):
        return f'{self.school_type} {self.school_name} | г.{self.city}'


# модель Учебного Класса
class Class(models.Model):
    number = models.SmallIntegerField(verbose_name='Класс', choices=((i, i) for i in range(1, 11 + 1)))
    letter = models.CharField(verbose_name='Параллель', max_length=1,
                              choices=((chr(i), chr(i)) for i in range(FIRST_LETTER_ID, FIRST_LETTER_ID + 6 + 1)))
    subjects = models.ManyToManyField(Subject, verbose_name='Предметы', related_name='class_subjects')

    def __str__(self):
        return f'{self.number}{self.letter}'

    class Meta:
        verbose_name_plural = 'Classes'

    def full_class(self):
        return str(self.number) + self.letter

    full_class = property(full_class)


# модель Профиля Учителя
class TeacherProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, verbose_name='Пользователь')
    surname = models.CharField(max_length=32, verbose_name='Фамилия', default='')
    name = models.CharField(max_length=30, verbose_name='Имя', default='')
    patronymic = models.CharField(max_length=32, verbose_name='Отчество', default='')
    phone = models.CharField(max_length=11, verbose_name='Номер телефона', default='', unique=True)
    email = models.EmailField(verbose_name='Эл. почта', default='', unique=True)
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, verbose_name='Школа')
    classes = models.ManyToManyField(Class, verbose_name='Классы', related_name='teacher_classes')
    photo = models.ImageField(verbose_name='Фото', upload_to='photos/', blank=True, default=f'photos/default_photo.jpg')

    def __str__(self):
        return f'{self.surname} {self.name[0].upper()}.{self.patronymic[0].upper()}.'


# модель Профиля Ученика
class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True, verbose_name='Пользователь')
    surname = models.CharField(max_length=32, verbose_name='Фамилия', default='')
    name = models.CharField(max_length=32, verbose_name='Имя', default='')
    patronymic = models.CharField(max_length=32, verbose_name='Отчество', default='')
    phone = models.CharField(max_length=11, verbose_name='Номер телефона', default='', unique=True,
                             validators=[utils.phone_validator])
    email = models.EmailField(verbose_name='Эл. почта', default='', unique=True)
    school = models.ForeignKey(School, on_delete=models.SET_NULL, null=True, verbose_name='Школа')
    edu_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, verbose_name='Класс')
    photo = models.ImageField(verbose_name='Фото', upload_to='photos/', blank=True, default='photos/default_photo.jpg')

    def __str__(self):
        return f'{self.surname} {self.name[0].upper()}.{self.patronymic[0].upper()}.'

    # функция фильтрации оценок для ученика
    def get_marks_info(self, period):
        now = datetime.datetime.now()
        if period in ('1', '2') and 1 <= now.month <= 8:
            y = now.year - 1
        else:
            y = now.year
        months = utils.QUARTERS[str(period)]
        borders = (datetime.date(year=y, month=months[0], day=1), datetime.date(year=y, month=months[-1], day=1))
        marks_info = []

        # пробегаемся про предметам Класса этого ученика
        subjects = self.edu_class.subjects.all()
        for subject in subjects:
            # берем сам предмет, оценки по этому предмету
            info = [subject, Mark.objects.filter(student=self, subject=subject, date__range=borders)]
            if info[1]:
                # если они имеются, считаем avg
                info.append(round(info[1].aggregate(models.Sum('mark')).get('mark__sum') / len(info[1]), 2))
                # если он 5.01 и т.д., то округляем
                if '.0' in str(info[2]):
                    info[2] = int(str(info[2]).split('.')[0])
                # если нет оценок, то убираем 0
                if info[2] == 0:
                    info[2] = ''
            else:
                info.append('')

            try:
                itog = FinalMark.objects.get(student=self, subject=subject, quarter=period)
            except:
                itog = ''
            info.append(itog)
            marks_info.append(info)
        return marks_info


# модель планирования заданий
class WorkingPlan(models.Model):
    edu_class = models.ForeignKey(Class, on_delete=models.CASCADE, verbose_name='Класс')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Предмет')
    work_type = models.CharField(max_length=32, verbose_name='Тип работы', choices=utils.work_types)
    plan_text = models.CharField(max_length=128, verbose_name='Текст', blank=True)
    date = models.DateField(verbose_name='Дата')

    def __str__(self):
        return f'{self.subject} | {self.work_type} | {self.date.strftime("%d.%m.%Y")}'


# модель оценивания знаний
class Mark(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, verbose_name='Ученик')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Предмет')
    mark = models.CharField(max_length=1, verbose_name='Оценка',
                            choices=(('2', '2'), ('3', '3'), ('4', '4'), ('5', '5'), ('П', 'П'), ('Б', 'Б')))
    comment = models.CharField(max_length=100, verbose_name='Комментарий', default='Отсутствует', blank=True)
    date = models.DateField(verbose_name='Дата выставления')
    work_type = models.CharField(max_length=32, verbose_name='Тип работы', choices=utils.work_types, default='ОТВ')

    def __str__(self):
        return f'{self.student.name} {self.student.surname} | {self.subject} | {self.mark}'

    def get_quarter(self):
        month = self.date.month
        quarter = '1'
        for q, ms in utils.QUARTERS.items():
            if month in ms:
                quarter = q
        return quarter

    quarter = property(get_quarter)


class FinalMark(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, verbose_name='Ученик')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, verbose_name='Предмет')
    mark = models.CharField(max_length=1, verbose_name='Оценка', choices=(('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')))
    quarter = models.CharField(max_length=1, verbose_name='Четверть', choices=utils.CHOICE_QUARTERS)

    def __str__(self):
        return f'Итоговая оценка {self.mark} | {self.subject} | {self.student}'