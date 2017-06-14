# -*- coding: utf-8 -*-
from django.conf import settings
from PIL import Image
from resizeimage import resizeimage # Used for image resize
import sys, os, os.path, subprocess, shutil


# get the directory of ocropy script
ocropyDir = settings.BASE_DIR + "/ocropy"


# Get the directory which stores all input and output files
dataDir = settings.MEDIA_ROOT

# Resize the image size to meet the smallest size requirment of binarization: 600*600 pixels
# Resize by adding a white backgroud border, but not to strech the original image
def resize_image(imagepath):
    fd_img = open(imagepath, 'r')
    img = Image.open(fd_img)
    w, h = img.size
    if w<600 or h<600:
	if w<600: w = 600
	if h<600: h = 600
	new_size = [w, h]
	new_image = resizeimage.resize_contain(img, new_size)
	new_image.save(imagepath, new_image.format) # override the original image
	fd_img.close()
    else:
	pass


# Execute ocr scripts: extract texts in a image
# Parameter: the original image
# Return: the .txt file of the image
def ocr_exec(imagename):

    # Prepare path for OCR service
    srcImagePath = dataDir +"/"+ imagename
    image_base, image_extension = os.path.splitext(imagename)
    outputDir = dataDir +"/"+ image_base
    
    # Call binarization script
    binarize_cmd = ocropyDir + "/ocropus-nlbin -n " + srcImagePath + " -o " + outputDir
    r_binarize = subprocess.call([binarize_cmd], shell=True)
    if r_binarize != 0:
        sys.exit("Error: Binarization process failed")
    
    # Call page layout analysis script
    la_inputPath = outputDir + "/????.bin.png"
    layoutAnalysis_cmd = ocropyDir + "/ocropus-gpageseg -n --minscale 1.0 " + la_inputPath
    r_layoutAnalysis = subprocess.call([layoutAnalysis_cmd], shell=True)
    if r_layoutAnalysis != 0:
        sys.exit("Error: Layout analysis process failed")

    # Call text recognition script
    recog_model = ocropyDir + "/models/en-default.pyrnn.gz"
    recog_inputPath = outputDir + "/????/??????.bin.png"
    textRecog_cmd = ocropyDir + "/ocropus-rpred -n -Q 2 -m " + recog_model + " " + recog_inputPath
    r_textRecognition = subprocess.call([textRecog_cmd], shell=True)
    if r_textRecognition != 0:
        sys.exit("Error: Text recognition process failed")
    
    # Generate output file
    output_file = outputDir + "/" + image_base + ".txt"
    cat_cmd = "cat " + outputDir + "/0001/??????.txt >" + output_file
    r_genOutput = subprocess.call([cat_cmd], shell=True)
    if r_genOutput != 0:
        sys.exit("Error: Generate output process failed")

    '''
    # Generate HTML output 
    output_file = outputDir + "/" + image_base + ".html"
    genOutput_cmd = ocropyDir + "/ocropus-hocr " + la_inputPath + " -o " + outputFile
    r_genOutput = subprocess.call([genOutput_cmd], shell=True)
    if r_genOutput != 0:
        sys.exit("Error: Generate output process failed")
    '''
    
    return output_file

# Delete all files related to this service time
def del_service_files(dataDir):
    # Delete all original images
    for the_file in os.listdir(dataDir):
	file_path = os.path.join(dataDir, the_file)
	try:
	    if os.path.isfile(file_path):
		os.unlink(file_path)
	    elif os.path.isdir(file_path):
		shutil.rmtree(file_path)
	except Exception as e:
	    print(e)

