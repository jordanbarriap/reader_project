from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class Answer(models.Model):
    id = models.AutoField(primary_key=True)
    statement =  models.CharField(max_length=200, default="test")
    correct = models.BooleanField()
    order = models.IntegerField()

class MCQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    statement = models.CharField(max_length=200, default="test")
    answers = models.ManyToManyField(Answer)

class Quiz(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, default="book")
    course_section = models.CharField(max_length=100, default="0")
    questions = models.ManyToManyField(MCQuestion)

class AnswerLog(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    question = models.ForeignKey(MCQuestion, on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE)