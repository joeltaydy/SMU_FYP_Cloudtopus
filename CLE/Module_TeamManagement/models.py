from django.db import models

class Section(models.Model):
    section_number = models.CharField(
        db_column='Section_Number',
        max_length=2,
        primary_key=True,
    )

    class Meta:
        managed = True
        db_table = 'Section'

class Student(models.Model):
    email = models.EmailField(
        db_column='Student_Email',
        primary_key=True,
    )
    username = models.CharField(
        db_column='Username',
        max_length=255,
    )
    firstname = models.CharField(
        db_column='Firstname',
        max_length=255,
    )
    lastname = models.CharField(
        db_column='Lastname',
        max_length=255,
    )
    password = models.CharField(
        db_column='Password',
        max_length=255,
    )

    class Meta:
        managed = True
        db_table = 'Student'

class Instructor(models.Model):
    email = models.EmailField(
        db_column='Instructor_Email',
        primary_key=True,
    )
    username = models.CharField(
        db_column='Username',
        max_length=255,
    )
    firstname = models.CharField(
        db_column='Firstname',
        max_length=255,
    )
    lastname = models.CharField(
        db_column='Lastname',
        max_length=255,
    )
    password = models.CharField(
        db_column='Password',
        max_length=255,
    )
    section = models.ManyToManyField(
        Section,
        db_column='Section',
        null=True,
    )

    class Meta:
        managed = True
        db_table = 'Instructor'

class Assigned_Team(models.Model):
    student = models.OneToOneField(
        Student,
        on_delete=models.CASCADE,
        db_column='Student',
        primary_key=True,
        default='NULL'
    )
    team_number = models.CharField(
        db_column='Team_Number',
        max_length=6,
    )
    section = models.ForeignKey(
        Section,
        on_delete=models.CASCADE,
        db_column='Section',
        default='G0'
    )

    class Meta:
        managed = True
        db_table = 'Assigned_Team'