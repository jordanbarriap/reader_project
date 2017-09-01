from django.shortcuts import render
from django.http import HttpResponse
import json
from django.core import serializers

from django.core.serializers.json import DjangoJSONEncoder

from reader.models import *

from django.db import connection

# Create your views here.
import datetime

def load_course(request,group_id):
    course_id = Group.objects.values("course__id").filter(id=group_id)
    print(course_id)
    if request.user.is_authenticated():
        user_id = request.user.id
        try:
            last_page_read = ReadingLog.objects.values().filter(user__id=user_id, course__id=course_id, action="page-load").latest("datetime")
            print(connection.queries[-1]['sql'])
            print(last_page_read["page"])
            last_page_read["datetime"] = str(last_page_read["datetime"])
            last_page_read["zoom"] = float(last_page_read["zoom"])
        except ReadingLog.DoesNotExist:
            last_page_read = {}
            print("No reading")
        course_json = Course.objects.get(id=course_id)
        hierarchical_structure = course_json.course_structure
        linear_structure = []
        enrich_course_structure(linear_structure,hierarchical_structure,user_id,course_id)
        return render(request, "reader.html", {"group":group_id, "course":{"id":course_json.id, "name":course_json.name}, "course_hierarchical":hierarchical_structure,"course_linear":linear_structure,"last_page_read":last_page_read})

def enrich_course_structure(array,data,user_id,course_id):
    if "children" in data:
        for subsection in data["children"]:
            #Add the id of each section
            id = ""
            if "id" in subsection:
                id = subsection["id"]
            #Add the name of each section
            name = ""
            if "name" in subsection:
                name = subsection["name"]
            #Add start and end pages information for each section
            spage = ""
            epage = ""
            resourceid = ""
            if ("spage" in subsection) and ("epage" in subsection) and ("resourceid" in subsection):
                spage = int(subsection["spage"])
                epage = int(subsection["epage"])
                resourceid = subsection["resourceid"]
                visited_pages = set(ReadingLog.objects.values_list('page', flat=True).filter(user__id=user_id, course__id=course_id, section=id, action="page-load"))
                num_visited_pages = len(visited_pages)
                array.append({"section": id, "name": name, "spage": spage, "epage": epage, "resource": resourceid, "visited_pages":num_visited_pages})
                subsection["num_visited_pages"] = num_visited_pages
            enrich_course_structure(array,subsection,user_id,course_id)