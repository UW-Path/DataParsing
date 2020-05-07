from django.core.mail import get_connection, send_mail, EmailMessage
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from django_projects import settings
from .models import UwpathApp, CourseInfo, Prereqs, Antireqs, Requirements, Communications, ContactForm
from .serializer import AppSerializer, CourseInfoSerializer, AntireqsSerializer, PrereqsSerializer, \
    RequirementsSerializer, CommunicationsSerializer
from UWPathAPI.ValidationCheckAPI import ValidationCheckAPI
from django.db.models import Q



# Create your views here.

def index(request):
    #Renders Home page with a drop down of major users can select form
    programs = Requirements_List().get_unique_major()
    return render(request, 'index.html', {'programs': programs})


def requirements(request, major, majorExtended= "", minor = "", minorExtended = ""):
    #Renders the requiremnts + table for major/minor requested for

    #communications for math
    table1 = Communications_List().get_list()
    #Basic honors math req
    table2 = Requirements_List().get_major_requirement("Table II")


    if majorExtended:
        # this is to solve bug where Degree Name includes '/'
        major = major + "/" + majorExtended
    programs = Requirements_List().get_unique_major()
    requirements = Requirements_List().get_major_requirement(major)
    if not requirements:
        return HttpResponseNotFound('<h1>404 Not Found: Major not valid</h1>')

    #filter minor returned
    majorName = requirements.first()['major_name']
    programs = programs.filter(Q(major_name = majorName) | Q(plan_type = "Joint")).exclude(plan_type = "Major")

    # minor and options
    if minor:
        if minorExtended:
            # this is to solve bug where Degree Name includes '/'
            minor = minor + "/" + minorExtended
        minor_requirements = Requirements_List().get_minor_requirement(minor)
        minor_requirements = minor_requirements.filter(Q(major_name = majorName) | Q(plan_type = "Joint"))
        if not minor_requirements:
            return HttpResponseNotFound('<h1>404 Not Found: Minor not valid</h1>')
        return render(request, 'table.html', {'programs': programs, 'major': major, 'requirements': requirements, 'minor': minor, 'minor_requirements': minor_requirements, 'table1':table1, 'table2':table2})
    return render(request, 'table.html', {'programs': programs, 'major': major, 'requirements': requirements, 'table1':table1, 'table2':table2})


def contact(request):
    #Contact me form
    submitted = False
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            # for debugging
            # con = get_connection('django.core.mail.backends.console.EmailBackend')
            try:
                subject = cd['subject'] + ' from ' + cd['email']
                msg = EmailMessage(subject,
                          cd['message'],
                          settings.EMAIL_HOST_USER,
                          [settings.EMAIL_HOST_USER])
                msg.send()
            except:
                return render(request, 'contact.html', {'form': form, 'submitted': submitted, 'error': True})

            return HttpResponseRedirect('/contact?submitted=True')
    else:
        form = ContactForm()
        if 'submitted' in request.GET:
            submitted = True
    return render(request, 'contact.html', {'form': form, 'submitted': submitted})

# Anything that starts with class (APIView) can be accessed through url.py via Django Restframework
class AllApp(APIView):
    queryset = UwpathApp.objects.all()
    serializer_class = AppSerializer

    def post(self, request, format=None):
        serializer = AppSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AppView(APIView):
    def get(self, request, pk, format=None):
        try:
            app = UwpathApp.objects.get(pk=pk)
            serializer = AppSerializer(app)
            return Response(serializer.data)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk, format=None):
        app = UwpathApp.objects.get(pk=pk)
        app.delete()
        return Response(status=status.HTTP_200_OK)


class Course_Info_API(APIView):
    def get(self, request, pk, format=None):
        try:
            app = CourseInfo.objects.get(pk=pk)
            serializer = CourseInfoSerializer(app)
            return Response(serializer.data)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get_object(self, request, pk, format=None):
        try:
            app = CourseInfo.objects.get(pk=pk)
            return app
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @api_view(('GET',))
    def filter(request):
        try:
            start = int(request.GET['start'])
            end = int(request.GET['end'])
            code = request.GET['code']
            if code.startswith("~") and any(char.isdigit() for char in code):
                code = code[1:].split(",")
                app = CourseInfo.objects.exclude(course_code__in=code)
                app = app.filter(course_number__gte=start).filter(course_number__lte=end)
            elif code.startswith("~"):
                code = code[1:].split(",")
                app = CourseInfo.objects.exclude(course_abbr__in=code)
                app = app.filter(course_number__gte=start).filter(course_number__lte=end)
            elif any(char.isdigit() for char in code):
                code = code.split(",")
                app = CourseInfo.objects.filter(course_code__in=code)
                app = app.filter(course_number__gte=start).filter(course_number__lte=end)
            elif "," in code:
                code = code.split(",")
                app = CourseInfo.objects.filter(course_abbr__in=code)
                app = app.filter(course_number__gte=start).filter(course_number__lte=end)
            elif code != "none":
                app = CourseInfo.objects.filter(course_abbr__exact=code)
                app = app.filter(course_number__gte=start).filter(course_number__lte=end)
            else:
                app = CourseInfo.objects.filter(course_number__gte=start).filter(course_number__lte=end)
            serializer = CourseInfoSerializer(app, many=True)
            return Response(serializer.data)
        except Exception as e:
            print(e)
            return Response(status=status.HTTP_404_NOT_FOUND)


class Course_Info_List(APIView):
    def get(self, request, format=None):
        list = CourseInfo.objects.all()[:10]
        serializer = CourseInfoSerializer(list, many=True)
        return Response(serializer.data)


class Prereqs_API(APIView):
    def get(self, request, pk, format=None):
        try:
            # if no primary key, then default go by id
            app = Prereqs.objects.get(pk=pk)
            serializer = PrereqsSerializer(app)
            return Response(serializer.data)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get_object(self, request, pk, format=None):
        try:
            app = Prereqs.objects.get(pk=pk)
            return app
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)


class Prereqs_List(APIView):
    def get(self, request, format=None):
        list = Prereqs.objects.all()[:10]
        serializer = PrereqsSerializer(list, many=True)
        return Response(serializer.data)


class Antireqs_API(APIView):
    def get(self, request, pk, format=None):
        try:
            app = Antireqs.objects.get(pk=pk)
            serializer = AntireqsSerializer(app)
            return Response(serializer.data)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get_object(self, request, pk, format=None):
        try:
            app = Antireqs.objects.get(pk=pk)
            return app
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)


class Antireqs_List(APIView):
    def get(self, request, format=None):
        list = Antireqs.objects.all()[:10]
        serializer = AntireqsSerializer(list, many=True)
        return Response(serializer.data)


class Requirements_API(APIView):
    def get(self, request, pk, format=None):
        try:
            app = Requirements.objects.get(pk=pk)
            serializer = RequirementsSerializer(app)
            return Response(serializer.data)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get_object(self, request, pk, format=None):
        try:
            app = Requirements.objects.get(pk=pk)
            return app
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)


class Requirements_List(APIView):
    def get(self, request, format=None):
        list = Requirements.objects.all()[:10]
        serializer = RequirementsSerializer(list, many=True)
        return Response(serializer.data)

    def get_unique_major(self, format=None):
        querySet = Requirements.objects.values('program_name', 'plan_type', 'major_name').order_by('program_name').distinct()
        return querySet

    def get_major_requirement(self, major):
        querySet = Requirements.objects.values().filter(program_name=major).order_by('program_name')
        return querySet

    def get_minor_requirement(self, minor):
        querySet = Requirements.objects.values().filter(program_name=minor).order_by('program_name')
        return querySet


class Communications_API(APIView):
    def get(self, request, pk, format=None):
        try:
            app = Communications.objects.get(pk=pk)
            serializer = CommunicationsSerializer(app)
            return Response(serializer.data)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def get_object(self, request, pk, format=None):
        try:
            app = Communications.objects.get(pk=pk)
            return app
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)


class Communications_List(APIView):
    def get(self, request, format=None):
        list = Communications.objects.all()[:10]
        serializer = CommunicationsSerializer(list, many=True)
        return Response(serializer.data)

    def get_list(self):
        querySet = Communications.objects.values()
        return querySet


class UWPath_API(APIView):
    def get(self, request, pk, format=None):
        api = ValidationCheckAPI()

        #Check if valid course first
        courseInfo = Course_Info_API().get_object(None, pk)
        if (type(courseInfo) != CourseInfo):
            return HttpResponseNotFound('<h1>404 Not Found: Course not valid</h1>')

        prereqs = Prereqs_API().get_object(None, pk)
        antireqs = Antireqs_API().get_object(None, pk)

        api.set_prereqs(prereqs.logic, prereqs.courses)
        api.set_antireqs(antireqs.antireq)

        list_of_courses_taken = request.GET.getlist("list_of_courses_taken[]")
        current_term_courses = request.GET.getlist("current_term_courses[]")

        can_take = api.can_take_course(list_of_courses_taken, current_term_courses, pk)

        response_data = {}

        if can_take:
            response_data["can_take"] = True
        else:
            response_data["can_take"] = False

        return Response(response_data)


