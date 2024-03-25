# IMPORTING IMPORTANT MODULES
from flask import Flask, render_template, request,send_file,redirect,flash,url_for
from PIL import Image,ImageFilter,ImageDraw,ImageEnhance
from werkzeug.utils import secure_filename
from flask import send_from_directory
import numpy as np
import os
import re

# ATTRIBUTES
UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'gif',"webp"}
app=Flask(__name__)
app.config['UPLOAD_FOLDER'] = "static"

#0011 these folder is useless if you are not displaying edited image into the page else showing the image


# METHOD FOR ROTATION AND FLIP TO IMAGE
def rotate_and_flip_image(img, degrees_to_rotate=0, flip_direction=None):
    img = img.rotate(degrees_to_rotate)
    if flip_direction == 'horizontal':
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    elif flip_direction == 'vertical':
        img = img.transpose(Image.FLIP_TOP_BOTTOM)
    else:
        pass 
    return img

def apply_circle_blur(image_path, diameter_strength=100, value_of_blur=0):
    img = image_path.convert("RGBA")
    diameter = (min(img.size) * (diameter_strength)) / 100
    img_array = np.array(img)
    width, height = img.size
    center_x = width // 2
    center_y = height // 2
    x, y = np.meshgrid(np.arange(width), np.arange(height))
    distance_from_center = np.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
    outside_circle_mask = distance_from_center > (diameter // 2)
    blurred_img = img.filter(ImageFilter.GaussianBlur(value_of_blur))
    blurred_img_array = np.array(blurred_img)

    
    img_array[outside_circle_mask] = blurred_img_array[outside_circle_mask]
    result_img = Image.fromarray(img_array)
    return result_img

# METHOD FOR CROPPING THE IMAGE
def apply_crop(image_path, left=100, top=100, right=100, bottom=100):
    image_path = image_path.crop((left, top, right, bottom))
    return image_path



#METHOD FOR APPLYING GREYSCALE TO IMAGE
def apply_grayscale(image,value):
    if int(value)==1:
       image=image.convert("L")
       return image
    return image

# METHOD FOR CONTRAST EFFECT
def adjust_contrast(image, contrast_factor):
    enhancer = ImageEnhance.Contrast(image)
    adjusted_image = enhancer.enhance(contrast_factor)
    return adjusted_image

# METHOD FOR ADJUSTMENT OF BRIGHTNESS OF IMAGE
def increase_brightness(image, brightness_factor):
    enhancer = ImageEnhance.Brightness(image)
    enhanced_image = enhancer.enhance(brightness_factor)
    return enhanced_image

#METHOD FOR RESIZING THE IMAGE
def resize_image(image, width=None, height=None):
    original_width, original_height = image.size
    if width and height:
        new_size = (int(width), int(height))
    elif width:
        new_size = (int(width), int(int(width)* original_height / original_width))
    elif height:
        new_size = (int(int(height) * original_width / original_height), int(height))
    else:
        return image 
    resized_image = image.resize(new_size)
    return resized_image

# METHOD TO VALIDATE FILE FORMATE
def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# HOMEPAGE
@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template("home.html")



# PAGE TO UPLOAD IMAGE
@app.route('/index', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('invalid file')
            return redirect(request.url)
        file = request.files['file']

        # VALIDATING FILE
        if file.filename == '':
            flash('invalid form of file')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            formate=filename.rsplit('.', 1)[1].lower()
            filename = "input_image_for_edit_123.png"
            output_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(output_path)
            print(filename)
            return  redirect(url_for('uploaded_file',filename=filename))
    return render_template("index.html")

# PAGE FOR IMAGE EDITING
@app.route('/uploads/<filename>',methods=["GET","POST"])
def uploaded_file(filename):

    # OPENING IMAGE FROM TEMP_ORIGINAL FOLDER
    image_path = os.path.join(app.root_path, 'static', f'{filename}')
    img=Image.open(image_path)
    show=False

    # FOR DEFAULT VALUE IN INPUT METHOD AT EDIT.HTML
    width,height=img.size
    if request.method=="POST":

        # resizing the image
        if request.form["dimension-feature"]=="yes":
            width=request.form["width"]
            height=request.form["height"]
            img=resize_image(img,width,height)

        # ENHANCING THE IMAGE
        brightness=request.form["brightness"]
        contrast=request.form["contrast"]
        img=increase_brightness(img,int(brightness))
        img=adjust_contrast(img,int(contrast))

        # FLIPPING AND ROTATION OF IMAGE
        angle=request.form["rotation"]
        axis=request.form["select"]
        img=rotate_and_flip_image(img,int(angle),axis)

        # APPLYING CICULAR BLUR
        diameter=request.form["blur_diameter"]
        blur_value=request.form["blur_value"]
        img=apply_circle_blur(img,int(diameter),int(blur_value))

        # APPLYING GRAYSCALE
        value=request.form["options"]
        img=apply_grayscale(img,value)
        img.show()
        output_path = os.path.join(app.config['UPLOAD_FOLDER'], "output_edited_image_123.png")
        img.save(output_path)
        show=True

        return render_template("edit.html",width=width,height=height,show=show,filename=filename)
    return render_template("edit.html",width=width,height=height,show=show,filename=filename)
if __name__ == '__main__':
    app.run(debug=True)

