# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse, JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from rest_framework.decorators import api_view
from wsgiref.util import FileWrapper
from django.shortcuts import render
from django.conf import settings
from .models import UploadedImage
from .ocr import ocr_exec, del_ocr_files
import sys, os, os.path, subprocess, zipfile, StringIO


# get the directory of the source image and output file
srcImageDir = settings.BASE_DIR + "/data/srcImages/"
dstDir = settings.BASE_DIR + "/data/output/"


def index(request):
    return render(request, 'index.html')

@csrf_exempt
@api_view(['GET', 'POST'])
def ocrView(request, format=None):

    # Receive uploaded image(s)
    keys = request.data.keys()
    imagenames = []
    for index, key in enumerate(keys):
	uploadedimage = request.data.get(key)
	imagenames.append(str(uploadedimage))
    	default_storage.save(srcImageDir + imagenames[index], uploadedimage)
	
    # Call OCR function
    # Files (local path) to put in the .zip
    output_files = []
    for index, imagename in enumerate(imagenames):
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
    del_ocr_files()

    return response

    # Another way to response one file
    #return FileResponse(open(srcImageDir + "testpage.html", 'rb'))


