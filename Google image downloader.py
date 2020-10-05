import os
from os import listdir
from flask import Flask, flash, request, redirect, url_for, render_template, send_from_directory, send_file
from flask_mail import Mail, Message
import cv2 
from zipfile import ZipFile
import shutil
import string 
import random

app = Flask(__name__)
p=os.path.abspath(os.curdir)+'/output'
app.config.update(
    DEBUG=False,
    MAIL_USERNAME ='myprojects0709@gmail.com',
    MAIL_PASSWORD ='anmoljindal@1',
    MAIL_DEFAULT_SENDER=('Anmol Jindal','myprojects0709@gmail.com'),
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True
    )
mail = Mail(app)
###################################################################################################################################################
@app.route('/', methods = ['GET', 'POST'])
def upload_file():
    os.chdir(p)
    if request.method == 'POST':
        subject = request.form['subject']
        count = request.form['count']
        email = request.form['email']
        black_white = request.form['yes_no']
        resize = request.form['resize']
        return redirect(url_for('files', subject = subject, count = count, email = email, black_white = black_white, resize = resize))
    return render_template('login.html')
def filepaths(path):
    file_paths=[]
    for root,directories,files in os.walk(path):
        for filename in files:
            filepath=os.path.join(root,filename)
            file_paths.append(filepath)
    print('Following files will be zipped:') 
    for file_name in file_paths: 
        print(file_name) 
    with ZipFile('images.zip','w') as zip:
        for file in file_paths:
            zip.write(file)
    print('files are zipped succesfully')
###################################################################################################################################################
@app.route('/mail/<subject>/<count>/<black_white>/<resize>/<email>')
def files(subject, count, black_white, resize, email):
    l = 0
    ifr=''.join([random.choice(string.ascii_letters+string.digits) for n in range(15)])
    reset_path = os.path.abspath(os.curdir)
    cmd = "infinite_image_downloader "+subject+" "+str(count)
    os.system(cmd)
    #if os.path.exists(subject) != True:
    os.mkdir(subject+'-'+ifr)
    path = os.path.abspath(os.curdir)+'/'+subject+'-'+ifr
    subject_path = os.path.abspath(os.curdir)+'/dataset/'+subject
    os.chdir(subject_path)
    all_images = {i for i in listdir(os.path.abspath(os.curdir))}
    if black_white == 'Yes':
        for images in all_images:
            img = cv2.imread(images, cv2.IMREAD_GRAYSCALE)
            cv2.imwrite(os.path.join(path, str(l)+'.png'), img)
            l = l + 1
    all_images = {i for i in listdir(path)}
    os.chdir(path)
    if resize > str(0):
        for images in all_images:
            img = cv2.imread(images, cv2.IMREAD_UNCHANGED)
            width = int(img.shape[1] * int(resize) / 100)
            height = int(img.shape[0] * int(resize) / 100)
            dim = (width, height)
            img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
            cv2.imwrite(os.path.join(path, str(l)+'.png'), img)
    filepaths(path)
    msg=Message('Click on the link below to download your images',recipients=[email])
    msg.body='127.0.0.1:5000/download/'+subject+'-'+ifr
    mail.send(msg)
    shutil.rmtree(p+'/dataset')
    os.chdir(reset_path)

    return render_template('sent.html'),url_for('serve_static', subject = subject+'-'+ifr)
###################################################################################################################################################
@app.route('/download/<subject>') 
def serve_static(subject):
    root_dir = os.path.abspath(os.curdir)
    download = root_dir+'/'+subject+'/images.zip'
    return send_file(download, attachment_filename = 'images.zip')
if __name__ == '__main__':
    app.run(debug = True)