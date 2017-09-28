from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import (HttpResponse,
                         HttpResponseForbidden,
                         HttpResponseBadRequest)
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser

import annotator
from annotator import models as annotator_models
import quiz
from quiz import models as quiz_models
import reader
from reader import models as reader_models

import json

from api import serializers


############################### Annotator API views ###############################

class JSONResponse(HttpResponse):
    """
    An ``HttpResponse`` that renders its content into JSON.
    """

    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs["content_type"] = "application/json"
        super(JSONResponse, self).__init__(content, **kwargs)


def root(request):
    if request.method == "GET":
        return JSONResponse({"name": getattr(settings,
                                             "ANNOTATOR_NAME",
                                             "django-annotator-store"),
                             "version": annotator.__version__})
    else:
        return HttpResponseForbidden()


@csrf_exempt
def index_create(request):
    if request.method == "GET":
        annotations = annotator_models.Annotation.objects.all()
        serializer = serializers.AnnotationSerializer(annotations, many=True)
        return JSONResponse(serializer.data)
    elif request.method == "POST":
        data = JSONParser().parse(request)
        serializer = serializers.AnnotationSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            response = HttpResponse(status=303)
            response["Location"] = reverse("read_update_delete",
                                           kwargs={"pk": serializer.data["id"]})
            return response
        else:
            return HttpResponseBadRequest(content=str(serializer.errors))
    else:
        return HttpResponseForbidden()


@csrf_exempt
def read_update_delete(request, pk):
    if request.method == "GET":
        annotation = get_object_or_404(annotator_models.Annotation, pk=pk)
        serializer = serializers.AnnotationSerializer(annotation)
        return JSONResponse(serializer.data, status=200)
    elif request.method == "PUT":
        annotation = get_object_or_404(annotator_models.Annotation, pk=pk)
        data = JSONParser().parse(request)
        serializer = serializers.AnnotationSerializer(annotation, data=data)
        if serializer.is_valid():
            serializer.save()
            response = HttpResponse(status=303)
            response["Location"] = reverse("read_update_delete",
                                           kwargs={"pk": serializer.data["id"]})
            return response
        else:
            return HttpResponseBadRequest(content=str(serializer.errors))
    elif request.method == "DELETE":
        annotation = get_object_or_404(annotator_models.Annotation, pk=pk)
        annotation.delete()
        return HttpResponse(status=204)
    else:
        return HttpResponseForbidden()


def search(request):
    if request.method == "GET":
        query = {k: v for k, v in request.GET.items()}
        annotations = annotator_models.Annotation.objects.filter(**query)
        serializer = serializers.AnnotationSerializer(annotations, many=True)
        return JSONResponse({"total": len(serializer.data), "rows": serializer.data})
    else:
        return HttpResponseForbidden()


############################### Reading Log API views ###############################
@csrf_exempt
def reading_log(request):
    """
    Add a reading log
    """
    if request.method == 'POST':
        data = JSONParser().parse(request)
        serializer = serializers.ReadingLogSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JSONResponse(serializer.data, status=201)
        else:
            return HttpResponseBadRequest(content=str(serializer.errors))
    else:
        return HttpResponseForbidden()


############################### Quiz API views ###############################
@csrf_exempt
def quiz(request):
    """
    Returning a requested quiz for an specific course section
    """
    if request.method == 'GET':
        section_id = request.GET["section"]

        #Query the multiple choice questions associated with the section
        mcquestions = quiz_models.Quiz.objects.filter(course_section=section_id).values("mcquestions__id","mcquestions__statement","mcquestions__answers__id","mcquestions__answers__statement", "mcquestions__answers__order")
        mcquestions_json = {}
        if len(mcquestions)>0:
            for question in mcquestions:
                question_id = question["mcquestions__id"]
                if question_id not in mcquestions_json:
                    mcquestions_json[question_id]={"statement":question["mcquestions__statement"], "answers":[{"id":question["mcquestions__answers__id"], "statement":question["mcquestions__answers__statement"],  "order":question["mcquestions__answers__order"]}]}
                else:
                    mcquestions_json[question_id]["answers"].append({"id":question["mcquestions__answers__id"], "statement":question["mcquestions__answers__statement"],  "order":question["mcquestions__answers__order"]})

        #Query the textual questions associated with the section
        textualquestions = quiz_models.Quiz.objects.filter(course_section=section_id).values("textualquestions__id","textualquestions__statement")
        textualquestions_json = {}
        if len(textualquestions) > 0:
            for question in textualquestions:
                question_id = question["textualquestions__id"]
                if question_id not in textualquestions_json:
                    textualquestions_json[question_id] = question["textualquestions__statement"]

        return JSONResponse({"mcquestions":mcquestions_json, "textualquestions":textualquestions_json}, status=201)

    else:
        return HttpResponseForbidden()

def check_quiz(request):
    """
    Returning a requested quiz for an specific course section
    """
    if request.method == 'GET':
        answers = request.GET["answers"]
        mc_answers = answers["mc_answers"]
        text_answers = answers["text_answers"]
        for answer in text_answers:
            answer_log = quiz_models.AnswerLog(name='Beatles Blog', tagline='All the latest Beatles news.')
        return JSONResponse({"answers":answers}, status=201)

    else:
        return HttpResponseForbidden()