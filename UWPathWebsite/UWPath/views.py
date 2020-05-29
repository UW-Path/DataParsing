from django.core.mail import get_connection, send_mail, EmailMessage
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view

from django_projects import settings
from .models import UwpathApp, CourseInfo, Prereqs, Antireqs, Requirements, Communications, ContactForm, Breath
from .serializer import AppSerializer, CourseInfoSerializer, AntireqsSerializer, PrereqsSerializer, \
    RequirementsSerializer, CommunicationsSerializer, BreathSerializer
from UWPathAPI.ValidationCheckAPI import ValidationCheckAPI
from django.db.models import Q



# Create your views here.

def index(request):
    #Renders Home page with a drop down of major users can select form
    programs = Requirements_List().get_unique_major()
    return render(request, 'index.html', {'programs': programs})


def requirements(request, major, majorExtended="", option ="", optionExtended ="", minor=""):
    # Note option includes requirement

    #Renders the requiremnts + table for major/minor requested for

    #communications for math
    table1 = Communications_List().get_list()
    #Basic honors math req
    table2 = Requirements_List().get_major_requirement("Table II")
    # so we don't exclude courses from requirement
    table2_course_codes = [r["course_codes"] for r in table2 if("Table II" in r["additional_requirements"])]



    if majorExtended:
        # this is to solve bug where Degree Name includes '/'
        major = major + "/" + majorExtended
    option_list = Requirements_List().get_unique_major()
    #Prevent duplicate courses in table II and major
    requirements = Requirements_List().get_major_requirement(major).exclude(course_codes__in = table2_course_codes)

    #check for additional req in major
    if requirements:
        additional_req = requirements.first()["additional_requirements"]
        if "Honours" or "BCS" in additional_req:
            #find additional req
            additional_req_list = additional_req.split(",")
            for i in additional_req_list:
                if "Honours" in i or "BCS" in i:
                    if i == "BCS":
                        bcs_req = Requirements_List().get_major_requirement("Bachelor of Computer Science")
                        requirements = bcs_req | requirements
                        if "Table II" in bcs_req.first()["additional_requirements"]:
                            requirements = table2 | requirements
                        requirements = requirements.distinct()
                    else:
                        i = str(i).replace("Honours ", "")
                        new_req = Requirements_List().get_major_requirement(i)
                        requirements = new_req | requirements
                        if "Table II" in new_req.first()["additional_requirements"]:
                            requirements = table2 | requirements
                        requirements = requirements.distinct()
                    break

    if not requirements:
        return HttpResponseNotFound('<h1>404 Not Found: Major not valid</h1>')

    #filter options returned
    majorName = requirements.first()['major_name']
    option_list = option_list.filter(Q(major_name = majorName) | Q(plan_type = "Joint")).exclude(Q(plan_type = "Major") | Q(plan_type = "Minor"))
    option_list = option_list.order_by('plan_type', 'program_name')

    #filter minor returned
    minor_list = Requirements_List().get_unique_major().filter(plan_type="Minor")
    minor_list = minor_list.order_by('program_name')

    # specializations and options
    if option:
        if optionExtended:
            # this is to solve bug where Degree Name includes '/'
            option = option + "/" + optionExtended
        option_requirements = Requirements_List().get_minor_requirement(option)
        requirements_course_codes_list = [r["course_codes"] for r in requirements]
        option_requirements = option_requirements.filter(Q(major_name = majorName) | Q(plan_type = "Joint"))
        option_requirements = option_requirements.exclude(course_codes__in = requirements_course_codes_list)
        if not option_requirements:
            return HttpResponseNotFound('<h1>404 Not Found: Minor not valid</h1>')

    if minor:
        minor_requirements = Requirements_List().get_minor_requirement(minor)
        requirements_course_codes_list = [r["course_codes"] for r in requirements]
        if option:
            option_course_codes_list = [r["course_codes"] for r in option_requirements]

        minor_requirements = minor_requirements.exclude(course_codes__in=requirements_course_codes_list)

        if option:
            minor_requirements = minor_requirements.exclude(course_codes__in=option_course_codes_list)
        if not minor_requirements:
            return HttpResponseNotFound('<h1>404 Not Found: Option not valid</h1>')
        print("fetch minor req")

    if option and minor:
        return render(request, 'table.html',
                      {'option_list': option_list, 'minor_list': minor_list, 'major': major, 'requirements': requirements, 'option': option,
                       'option_requirements': option_requirements, 'minor': minor, 'minor_requirements': minor_requirements,
                           'table1': table1, 'table2': table2})

    elif option:
        return render(request, 'table.html', {'option_list': option_list, 'minor_list': minor_list,  'major': major, 'requirements': requirements, 'option': option, 'option_requirements': option_requirements, 'table1':table1, 'table2':table2})
    elif minor:
        return render(request, 'table.html',
                      {'option_list': option_list, 'minor_list': minor_list, 'major': major, 'requirements': requirements, 'minor': minor,
                       'minor_requirements': minor_requirements, 'table1': table1, 'table2': table2})

    else: return render(request, 'table.html', {'option_list': option_list, 'minor_list': minor_list, 'major': major, 'requirements': requirements, 'table1':table1, 'table2':table2})


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


class Breath_API(APIView):
    def get(self, request, pk, format=None):
        try:
            # if no primary key, then default go by id
            app = Breath.objects.get(pk=pk)
            serializer = BreathSerializer(app)
            return Response(serializer.data)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)


class Breath_List(APIView):
    def get(self, request, format=None):
        list = Breath.objects.all()
        serializer = BreathSerializer(list, many=True)
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


class BreathAPI(APIView):
    def breadth(self, list_of_courses_taken):
        breadth_objects = Breath.objects.all()
        codes = list(map(lambda x: x.split()[0], list_of_courses_taken))

        human = 2
        soc_sci = 2
        pure_sci = 1
        app_sci = 1
        app_pure = 0

        for code in codes:
            for obj in breadth_objects:
                if obj.subject == code:
                    if obj.humanities and human > 0:
                        human -= 1
                    elif obj.social_science and soc_sci > 0:
                        soc_sci -= 1
                    elif obj.applied_science and obj.pure_science:
                        app_pure += 1
                    elif obj.applied_science and app_sci > 0:
                        app_sci -= 1
                    elif obj.pure_science and pure_sci > 0:
                        pure_sci -= 1

        return not (human or soc_sci or app_pure < app_sci+pure_sci)


    def get(self, request, format=None):
        list_of_courses_taken = request.GET.getlist("list_of_courses_taken[]")

        response_data = {}
        response_data["breadth_met"] = self.breadth(list_of_courses_taken)

        return Response(response_data)
