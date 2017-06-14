# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.http import HttpResponse, FileResponse
from django.shortcuts import render
from django.conf import settings
from wsgiref.util import FileWrapper
from .models import UploadedImage
from .serializers import UploadedImageSerializer
from .ocr import resize_image, ocr_exec, del_service_files
import sys, os, os.path, zipfile, StringIO


# Get the directory which stores all input and output files
dataDir = settings.MEDIA_ROOT


def index(request):
    return render(request, 'index.html')


@csrf_exempt
@api_view(['GET', 'POST'])
def ocrView(request, format=None):

    # Receive uploaded image(s)
    keys = request.data.keys()
    if len(keys)<1:
	return HttpResponse("Please selecting at least one image.")
    imagenames = []
    # One or multiple files/values in one field
    for key in keys:
	uploadedimages = request.data.getlist(key)
	print("######## %d" % len(uploadedimages))
	if len(uploadedimages) == 1:
	    image_str = str(uploadedimages[0])
	    imagenames.append(image_str)
    	    default_storage.save(dataDir+"/"+image_str, uploadedimages[0])
	elif len(uploadedimages) > 1:
	    for image in uploadedimages:
		image_str = str(image)
		imagenames.append(image_str)
		default_storage.save(dataDir+"/"+image_str, image)
	
    # Resize the image if its size smaller than 600*600
    for imagename in imagenames:
	imagepath = dataDir+"/"+imagename
	resize_image(imagepath)

    # Call OCR function
    output_files = []
    for imagename in imagenames:
	output_file = ocr_exec(imagename)
	output_files.append(output_file)

    # One file: return directly
    if len(output_files) == 1: 
	fdir, fname = os.path.split(output_files[0])
	short_report = open(output_files[0], 'rb')
        response = HttpResponse(FileWrapper(short_report), content_type='application/force-download')
        response['Content-Disposition'] = 'attachment; filename=%s' % fname
    # Multiple files: return in zip type
    else: 
        # Folder name in ZIP archive which contains the above files
    	zip_subdir = "texts_of_images"
    	zip_filename = "%s.zip" % zip_subdir
    	# Open StringIO to grab in-memory ZIP contents
    	strio = StringIO.StringIO()
   	# The zip compressor
    	zf = zipfile.ZipFile(strio, "w")

    	for fpath in output_files:
            # Caculate path for file in zip
            fdir, fname = os.path.split(fpath)
            zip_path = os.path.join(zip_subdir, fname)
            # Add file, at correct path
            zf.write(fpath, zip_path)

    	zf.close()
    	# Grab ZIP file from in-memory, make response with correct MIME-type
    	response = HttpResponse(strio.getvalue(), content_type="application/x-zip-compressed")
    	# And correct content-disposition
    	response["Content-Disposition"] = 'attachment; filename=%s' % zip_filename
    
    # Delete all files related to this service time
    del_service_files(dataDir)

    return response

    # Another way to response one file
    #return FileResponse(open(srcImageDir + "testpage.html", 'rb'))

'''
@csrf_exempt
@api_view(['GET', 'POST'])
@parser_classes((MultiPartParser,))
def ocrView(request, format=None):
    data = MultiPartParser().parse(request.data)
    serializer = UploadedImageSerializer(data=data)
    if serializer.is_valid():
	serializer.save()
	default_storage.save(srcImageDir + str(serializer.data.get('imagemodel')), serializer.data.get('imagemodel'))
	return Response(serializer.data, status=200)
    return Response(serializer.errors, status=400)
'''

