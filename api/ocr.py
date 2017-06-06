# -*- coding: utf-8 -*-
from django.conf import settings
import sys, os, os.path, subprocess, shutil


# get the directory of ocropy script
curfilePath = os.path.abspath(__file__)
curDir = os.path.abspath(os.path.join(curfilePath, os.pardir))
parentDir = os.path.abspath(os.path.join(curDir, os.pardir))
ocropyDir = parentDir + "/ocropy"

# get the directory of the source image and output file
srcImageDir = settings.BASE_DIR + "/data/srcImages/"
dstDir = settings.BASE_DIR + "/data/output/"

# Execute ocr scripts: extract texts in a image
# Parameter: the original image
# Return: the .txt file of the image
def ocr_exec(imagename):

    # Prepare path for OCR service
    srcImagePath = srcImageDir + imagename
    image_name, image_extension = os.path.splitext(imagename)
    outputDir = dstDir + image_name
    
    # Call binarization script
    binarize_cmd = ocropyDir + "/ocropus-nlbin -n " + srcImagePath + " -o " + outputDir
    r_binarize = subprocess.call([binarize_cmd], shell=True)
    if r_binarize != 0:
        sys.exit("Error: Binarization process failed")
    
    # Call page layout analysis script
    la_inputPath = outputDir + "/????.bin" + image_extension
    layoutAnalysis_cmd = ocropyDir + "/ocropus-gpageseg -n --minscale 1.0 " + la_inputPath
    r_layoutAnalysis = subprocess.call([layoutAnalysis_cmd], shell=True)
    if r_layoutAnalysis != 0:
        sys.exit("Error: Layout analysis process failed")

    # Call text recognition script
    recog_model = ocropyDir + "/models/en-default.pyrnn.gz"
    recog_inputPath = outputDir + "/????/??????.bin" + image_extension
    textRecog_cmd = ocropyDir + "/ocropus-rpred -n -Q 2 -m " + recog_model + " " + recog_inputPath
    r_textRecognition = subprocess.call([textRecog_cmd], shell=True)
    if r_textRecognition != 0:
        sys.exit("Error: Text recognition process failed")
    

    # Generate output file
    output_file = outputDir + "/" + image_name + ".txt"
    cat_cmd = "cat " + outputDir + "/0001/??????.txt >" + output_file
    r_genOutput = subprocess.call([cat_cmd], shell=True)
    if r_genOutput != 0:
        sys.exit("Error: Generate output process failed")

    '''
    # Generate HTML output 
    output_file = outputDir + "/" + image_name + ".html"
    genOutput_cmd = ocropyDir + "/ocropus-hocr " + la_inputPath + " -o " + outputFile
    r_genOutput = subprocess.call([genOutput_cmd], shell=True)
    if r_genOutput != 0:
        sys.exit("Error: Generate output process failed")
    '''
    
    return output_file

# Delete all files related to this service time
def del_ocr_files():
    # Delete all original images
    for the_file in os.listdir(srcImageDir):
	file_path = os.path.join(srcImageDir, the_file)
	try:
	    if os.path.isfile(file_path):
		os.unlink(file_path)
	    elif os.path.isdir(file_path):
		shutil.rmtree(file_path)
	except Exception as e:
	    print(e)

    # Delete all outputs
    for the_file in os.listdir(dstDir):
	file_path = os.path.join(dstDir, the_file)
	try:
	    if os.path.isfile(file_path):
		os.unlink(file_path)
	    elif os.path.isdir(file_path):
		shutil.rmtree(file_path)
	except Exception as e:
	    print(e)

