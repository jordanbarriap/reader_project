from django.db import models
from django.contrib.auth.models import User

from django.utils import timezone
# Create your models here.


class Answer(models.Model):
    id = models.AutoField(primary_key=True)
    statement =  models.CharField(max_length=500, default="test")
    correct = models.BooleanField()
    order = models.IntegerField()


class MCQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    statement = models.CharField(max_length=500, default="test")
    answers = models.ManyToManyField(Answer)


class TextualQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    statement = models.CharField(max_length=500, default="test")


class Quiz(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, default="book")
    course_section = models.CharField(max_length=100, default="0")
    mcquestions = models.ManyToManyField(MCQuestion)
    textualquestions = models.ManyToManyField(TextualQuestion)


class AnswerLog(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    question = models.ForeignKey(MCQuestion, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)


class KC(models.Model):
    id = models.AutoField(primary_key=True)
    kc = models.CharField(max_length=100, default="kc")
    section = models.CharField(max_length=100, default="section")


class KCLevel(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    kc = models.ForeignKey(KC, on_delete=models.CASCADE)
    datetime = models.DateTimeField(default=timezone.now())
    level = models.IntegerField()

