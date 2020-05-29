# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
from django import forms

class UwpathApp(models.Model):
    short_name = models.CharField(max_length=10)
    name = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = 'UWPath_app'


class Antireqs(models.Model):
    course_code = models.CharField(max_length=255, primary_key=True)
    antireq = models.CharField(max_length=500)
    extra_info = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'antireqs'


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)
    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.BooleanField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.BooleanField()
    is_active = models.BooleanField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class CourseInfo(models.Model):
    course_code = models.CharField(max_length=255, primary_key=True)
    course_abbr = models.CharField(max_length=10)
    course_number = models.IntegerField()
    course_id = models.CharField(max_length=255, blank=True, null=True)
    course_name = models.CharField(max_length=255, blank=True, null=True)
    credit = models.CharField(max_length=255, blank=True, null=True)
    info = models.CharField(max_length=2000, blank=True, null=True)
    offering = models.CharField(max_length=255, blank=True, null=True)
    online = models.BooleanField(blank=True, null=True)
    prereqs = models.CharField(max_length=500, blank=True, null=True)
    coreqs = models.CharField(max_length=500, blank=True, null=True)
    antireqs = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'course_info'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class Prereqs(models.Model):
    course_code = models.CharField(max_length=255, primary_key=True)
    logic = models.CharField(max_length=500, blank=True, null=True)
    courses = models.CharField(max_length=500, blank=True, null=True)
    grades = models.CharField(max_length=250, blank=True, null=True)
    not_open = models.CharField(max_length=250, blank=True, null=True)
    only_from = models.CharField(max_length=250, blank=True, null=True)
    min_level = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'prereqs'


class Requirements(models.Model):
    id = models.IntegerField(primary_key=True)
    major_name = models.CharField(max_length=255, blank=True, null=True)
    program_name = models.CharField(max_length=255, blank=True, null=True)
    plan_type = models.CharField(max_length=255, blank=True, null=True)
    course_codes = models.CharField(max_length=255, blank=True, null=True)
    number_of_courses = models.IntegerField(blank=True, null=True)
    additional_requirements = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'requirements'


class Communications(models.Model):
    # Table I
    id = models.IntegerField(primary_key=True)
    course_code = models.CharField(max_length=255, blank=True, null=True)
    list_number = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'communications'


class ContactForm(forms.Form):
     name = forms.CharField(max_length=100)
     email = forms.EmailField(required=True)
     subject = forms.CharField(max_length=100)
     message = forms.CharField(widget=forms.Textarea)


class Breath(models.Model):
    subject = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    humanities = models.BooleanField(blank=True, null=True)
    social_science = models.BooleanField(blank=True, null=True)
    pure_science = models.BooleanField(blank=True, null=True)
    applied_science = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'breadth_table'
