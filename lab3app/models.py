from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Student(models.Model):
    student_user=models.OneToOneField(User,unique=True,on_delete=models.CASCADE)
    student_id = models.CharField(max_length=20)
    student_name = models.CharField(max_length=20)
    # student_email = models.EmailField()
    # student_password = models.CharField(max_length=20)
    student_regiter_time = models.DateTimeField()
    student_is_leader = models.BooleanField()

class Submission(models.Model):
    submission_serial = models.IntegerField()
    submission_student = models.ForeignKey(Student,on_delete=models.CASCADE)
    submission_file_h = models.FileField()
    submission_file_cc = models.FileField()
    submission_time = models.DateTimeField()
    submission_revised = models.BooleanField()

class Group(models.Model):
    group_serial = models.IntegerField()
    group_name = models.CharField(max_length=40)
    group_leader = models.ForeignKey(Student,on_delete=models.CASCADE)
    group_register_time = models.DateTimeField()

class StudentGroup(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    group = models.ForeignKey(Group,on_delete=models.CASCADE)
    join_time = models.DateTimeField()
 
class Score(models.Model):
    submission = models.ForeignKey(Submission,on_delete=models.CASCADE)
    score_1 = models.IntegerField()
    score_2 = models.IntegerField()
    score_3 = models.IntegerField()
    score_time = models.DateTimeField()

class Message(models.Model):
    message_from = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='message_from')
    message_to   = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='message_to')
    message_request_or_answer = models.BooleanField()
    message_join_or_quit = models.BooleanField()
    message_revised = models.BooleanField()
    message_time = models.DateTimeField()

class Suggestion(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    suggestion_subject = models.CharField(max_length=40)
    suggestion_content = models.TextField()
    suggestion_time = models.DateTimeField() 

class SerailNo(models.Model):
    serial_group = models.IntegerField()
    serial_submission = models.IntegerField()
