from django.shortcuts import render
from django.http import HttpResponse
import json
from django.core import serializers

from django.core.serializers.json import DjangoJSONEncoder

from reader.models import *

from django.db import connection
from django.db.models import Count

# Create your views here.
import datetime

'''def load_course(request,course_id):
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
        return render(request, "reader.html", {"course":{"id":course_json.id,"name":course_json.name}, "course_hierarchical":hierarchical_structure,"course_linear":linear_structure,"last_page_read":last_page_read})'''

def load_course(request,group_id):
    course_id = Group.objects.only("course").get(id=group_id).course.id
    print(course_id)
    if request.user.is_authenticated():
        user_id = request.user.id
        try:
            last_page_read = ReadingLog.objects.values().filter(user__id=user_id, group__id=group_id, action="page-load").latest("datetime")
            print(connection.queries[-1]["sql"])
            print(last_page_read["page"])
            last_page_read["datetime"] = str(last_page_read["datetime"])
            last_page_read["zoom"] = float(last_page_read["zoom"])
        except ReadingLog.DoesNotExist:
            last_page_read = {}
            print("No reading")
        course_json = Course.objects.get(id=course_id)
        #num_students = int(Group.objects.annotate(num_students=Count('students'))[0].num_students)
        #print(num_students)
        hierarchical_structure = course_json.course_structure
        linear_structure = []
        enrich_course_structure(linear_structure, hierarchical_structure, user_id, group_id)
        #enrich_course_structure(linear_structure,hierarchical_structure,user_id,group_id)#,num_students-1)
        return render(request, "reader.html", {"group":group_id, "course":{"id":course_json.id, "name":course_json.name}, "course_hierarchical":hierarchical_structure,"course_linear":linear_structure,"last_page_read":last_page_read})

def enrich_course_structure(array,data,user_id,group_id):
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
                visited_pages = set(ReadingLog.objects.values_list('page', flat=True).filter(user__id=user_id, group__id=group_id, section=id, action="page-load"))
                num_visited_pages = len(visited_pages)
                array.append({"section": id, "name": name, "spage": spage, "epage": epage, "resource": resourceid, "visited_pages":num_visited_pages})
                subsection["num_visited_pages"] = num_visited_pages
            enrich_course_structure(array,subsection,user_id,group_id)

'''def enrich_course_structure(array,data,user_id,group_id,num_students):
    if "children" in data:
        #print("not a leaf")
        for subsection in data["children"]:
            #Add the id of each section
            id = ""
            if "id" in subsection:
                id = subsection["id"]
            print(id)
            #Add the name of each section
            name = ""
            if "name" in subsection:
                name = subsection["name"]
            #Add start and end pages information for each section
            spage = ""
            epage = ""
            if ("spage" in subsection) and ("epage" in subsection) and ("resourceid" in subsection):
                #print("not a leaf with pages")
                spage = int(subsection["spage"])
                epage = int(subsection["epage"])
                resourceid = subsection["resourceid"]
                visited_pages = set(ReadingLog.objects.values_list('page', flat=True).filter(user__id=user_id, group__id=group_id, section=id, action="page-load"))
                num_visited_pages = len(visited_pages)
                readers_proportion = 0.0
                num_pages = epage-spage+1
                for i in range(spage,epage+1):
                    #print(ReadingLog.objects.values_list('user__id', flat=True).filter(group__id=group_id, section=id, action="page-load", page = i).query)
                    students_who_read_page = set(ReadingLog.objects.values_list('user__id', flat=True).filter(group__id=group_id, section=id, action="page-load", page = i))
                    num_students_who_read_page = len(students_who_read_page)
                    readers_proportion = readers_proportion + float(num_students_who_read_page/num_students)
                    #print(students_who_read_page)
                readers_proportion = readers_proportion/num_pages
                #print(str(num_visited_pages)+"en este comienzo de seccion")
                num_visited_pages = enrich_course_structure(array, subsection, user_id, group_id, num_students)
                array.append({"section": id, "name": name, "spage": spage, "epage": epage, "resource": resourceid, "visited_pages":num_visited_pages})
                subsection["num_visited_pages"] = num_visited_pages
                #enrich_course_structure(array, subsection, user_id, group_id, num_students)
                #print(array)
            else:
                print("not a leaf without pages")
                readers_proportion = 0.0
                num_pages = 0
                #readers_proportion = readers_proportion / num_pages
                num_visited_pages = enrich_course_structure(array, subsection, user_id, group_id,
                                                                                num_students)
                array.append({"section": id, "name": name, "spage": spage, "epage": epage, "resource": resourceid,
                              "visited_pages": num_visited_pages})
                subsection["num_visited_pages"] = num_visited_pages

        return num_visited_pages
    else:
        print("a leaf")
        subsection = data
        # Add the id of each section
        id = ""
        if "id" in subsection:
            id = subsection["id"]
        # Add the name of each section
        name = ""
        if "name" in subsection:
            name = subsection["name"]
        # Add start and end pages information for each section
        spage = ""
        epage = ""
        resourceid = ""
        if ("spage" in subsection) and ("epage" in subsection) and ("resourceid" in subsection):
            spage = int(subsection["spage"])
            epage = int(subsection["epage"])
            resourceid = subsection["resourceid"]
            visited_pages = set(
                ReadingLog.objects.values_list('page', flat=True).filter(user__id=user_id, group__id=group_id,
                                                                         section=id, action="page-load"))
            num_visited_pages = len(visited_pages)

            readers_proportion = 0.0
            num_pages = epage - spage + 1
            for i in range(spage, epage + 1):
                # print(ReadingLog.objects.values_list('user__id', flat=True).filter(group__id=group_id, section=id, action="page-load", page = i).query)
                students_who_read_page = set(
                    ReadingLog.objects.values_list('user__id', flat=True).filter(group__id=group_id, section=id,
                                                                                 action="page-load", page=i))
                num_students_who_read_page = len(students_who_read_page)
                readers_proportion = readers_proportion + float(num_students_who_read_page / num_students)
                #print(students_who_read_page)
            readers_proportion = readers_proportion / num_pages

            array.append({"section": id, "name": name, "spage": spage, "epage": epage, "resource": resourceid,
                          "visited_pages": num_visited_pages})
            subsection["num_visited_pages"] = num_visited_pages
            print("last section level")
            print(int(num_visited_pages))
            return num_visited_pages'''
