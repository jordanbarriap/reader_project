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

user_id = 0
group_id = 0
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

def load_course(request,url_group_id):
    global user_id, group_id
    group_id = url_group_id
    course_id = Group.objects.only("course").get(id=group_id).course.id
    if request.user.is_authenticated():
        user_id = request.user.id
        try:
            last_page_read = ReadingLog.objects.values().filter(user__id=user_id, group__id=group_id, action="page-load").latest("datetime")
            print(connection.queries[-1]["sql"])
            print(last_page_read)
            last_page_read["datetime"] = str(last_page_read["datetime"])
            last_page_read["zoom"] = float(last_page_read["zoom"])
        except ReadingLog.DoesNotExist:
            last_page_read = {}
            print("No reading")
        course_json = Course.objects.get(id=course_id)
        num_students = int(Group.objects.annotate(num_students=Count('students'))[0].num_students)
        hierarchical_structure = course_json.course_structure
        calculate_reading_progress(hierarchical_structure)
        return render(request, "reader.html", {"group":group_id, "course":{"id":course_json.id, "name":course_json.name}, "course_hierarchical":hierarchical_structure,"last_page_read":last_page_read})


def calculate_reading_progress(node):
    if "children" not in node:
        num_pages = get_number_of_pages(node)
        read_pages = get_number_of_read_pages(node)
        set_number_of_pages(node,num_pages)
        set_number_of_read_pages(node, read_pages)
        return num_pages, read_pages
    else:
        if has_pages(node):
            subsections_num_pages, subsections_read_pages = calculate_subsections_reading_progress(node["children"])
            num_pages = get_number_of_pages(node) + subsections_num_pages
            read_pages = get_number_of_read_pages(node) + subsections_read_pages
            set_number_of_pages(node,num_pages)
            set_number_of_read_pages(node,read_pages)
            return num_pages, read_pages
        else:
            num_pages, read_pages = calculate_subsections_reading_progress(node["children"])
            set_number_of_pages(node,num_pages)
            set_number_of_read_pages(node, read_pages)
            return num_pages, read_pages


def calculate_subsections_reading_progress(subsections):
    total_pages = 0
    read_pages = 0
    for subsection in subsections:
        subsection_total_pages, subsection_read_pages = calculate_reading_progress(subsection)
        total_pages = total_pages + subsection_total_pages
        read_pages = read_pages + subsection_read_pages
    return total_pages, read_pages


def get_number_of_pages(node):
    spage = int(node["spage"])
    epage = int(node["epage"])
    return epage - spage + 1


def get_number_of_read_pages(node):
    global user_id, group_id
    section_id = node["id"]
    read_pages = set(
        ReadingLog.objects.values_list('page', flat=True).filter(user__id=user_id, group__id=group_id, section=section_id,
                                                                 action="page-load"))
    return len(read_pages)


def has_pages(node):
    if "spage" in node and "epage" in node and "resourceid" in node:
        return True
    else:
        return False


def set_number_of_pages(node, num_pages):
    node["num_pages"] = num_pages


def set_number_of_read_pages(node, num_read_pages):
    node["read_pages"] = num_read_pages


'''def enrich_course_structure(array,data,user_id,group_id,num_students):
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
            if "spage" in subsection and "epage" in subsection and "resourceid" in subsection:
                print("not a leaf with pages")
                spage = int(subsection["spage"])
                epage = int(subsection["epage"])
                resourceid = subsection["resourceid"]
                visited_pages = set(ReadingLog.objects.values_list('page', flat=True).filter(user__id=user_id, group__id=group_id, section=id, action="page-load"))
                num_visited_pages = len(visited_pages)
                readers_proportion = 0.0
                num_pages = epage-spage+1
                for i in range(spage,epage+1):
                    #print(ReadingLog.objects.values_list('user__id', flat=True).filter(group__id=group_id, section=id, action="page-load", page = i).query)
                    students_who_read_page = set(ReadingLog.objects.values_list('user__id', flat=True).exclude(user__id=user_id).filter(group__id=group_id, section=id, action="page-load", page = i))
                    num_students_who_read_page = len(students_who_read_page)
                    readers_proportion = readers_proportion + float(num_students_who_read_page/num_students)
                    #print(students_who_read_page)
                if(num_pages!=0):
                    readers_proportion = readers_proportion/num_pages
                else:
                    readers_proportion = 0

                num_visited_pages = num_visited_pages + enrich_course_structure(array, subsection, user_id, group_id, num_students)
                #num_visited_pages = num_visited_pages + section_visited_pages
                #readers_proportion = readers_proportion + section_readers_proportion
                #num_visited_pages = num_visited_pages + enrich_course_structure(array, subsection, user_id, group_id, num_students)
                #array.append({"section": id, "name": name, "spage": spage, "epage": epage, "resource": resourceid, "visited_pages":num_visited_pages})
                print(id)
                subsection["num_visited_pages"] = num_visited_pages
                enrich_course_structure(array, subsection, user_id, group_id, num_students)
                #print(array)
            else:
                print("not a leaf without pages")
                readers_proportion = 0.0

                num_visited_pages = enrich_course_structure(array, subsection, user_id, group_id,
                                                                                num_students)
                #array.append({"section": id, "name": name, "spage": spage, "epage": epage, "visited_pages": num_visited_pages})
                print(id)
                subsection["num_visited_pages"] = num_visited_pages
        return num_visited_pages
    else:
        print("last section")
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
        num_visited_pages = 0
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
                    ReadingLog.objects.values_list('user__id', flat=True).exclude(user__id=user_id).filter(group__id=group_id, section=id,
                                                                                 action="page-load", page=i))
                num_students_who_read_page = len(students_who_read_page)
                readers_proportion = readers_proportion + float(num_students_who_read_page / num_students)

            readers_proportion = readers_proportion / num_pages
            #print(id)
            #array.append({"section": id, "name": name, "spage": spage, "epage": epage, "resource": resourceid, "visited_pages": num_visited_pages, "group_read_proportion":readers_proportion})
            subsection["num_visited_pages"] = num_visited_pages
            subsection["group_read_proportion"] = readers_proportion
        print(num_visited_pages)
        return num_visited_pages'''


'''def enrich_course_structure(array,data,user_id,group_id):
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
            enrich_course_structure(array,subsection,user_id,group_id)'''

'''def calculate_sections_num_pages(data):
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
            if "spage" in subsection and "epage" in subsection and "resourceid" in subsection:
                #print("not a leaf with pages")
                spage = int(subsection["spage"])
                epage = int(subsection["epage"])
                num_pages = epage - spage + 1;
                num_pages = num_pages + calculate_sections_num_pages(subsection)
                subsection["num_pages"] = num_pages
                #enrich_course_structure(array, subsection, user_id, group_id, num_students)
                #print(array)
            else:
                num_pages = calculate_sections_num_pages(subsection)
                subsection["num_pages"] = num_pages
        return num_pages
    else:
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
        num_pages = 0
        if "spage" in subsection and "epage" in subsection and "resourceid" in subsection:
            # print("not a leaf with pages")
            spage = int(subsection["spage"])
            epage = int(subsection["epage"])
            num_pages = epage - spage + 1;
            subsection["num_pages"] = num_pages
            # enrich_course_structure(array, subsection, user_id, group_id, num_students)
            # print(array)
            return num_pages'''