import os
import uuid
from datetime import datetime

from werkzeug.utils import secure_filename
import PIL
from PIL import Image


def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        os.chmod(folder_path, os.O_RDWR)


def change_filename_with_timestamp_uuid(filename):
    fileinfo = os.path.splitext(filename)
    filename = datetime.now().strftime('%Y%m%d%H%M%S') + \
               str(uuid.uuid4().hex) + fileinfo[-1].lower()
    return filename

def secure_filename_with_timestamp(filename):
    fileinfo = os.path.splitext(filename)
    filename_prefix = secure_filename(fileinfo[0])
    filename = filename_prefix + '_'+ datetime.now().strftime("%Y%m%d%H%M%S") \
               + fileinfo[-1].lower()
    return filename

def secure_filename_with_uuid(filename):
    fileinfo = os.path.splitext(filename)
    filename_prefix = secure_filename(fileinfo[0])
    filename = filename_prefix + '_' + str(uuid.uuid4().hex)[0:6] + fileinfo[-1].lower()
    return filename



ALLOWED_IMAGE_EXTENSIONS = set(['png', 'jpeg', 'jpg'])
ALLOWED_VIDEO_EXTENSIONS = set(['mp4', 'avi'])
ALLOWED_AUDIO_EXTENSIONS = set(['mp3', 'm4a'])

def check_files_extension(filenameslist, allowed_extensions):
    for fname in filenameslist:
        check_state = '.' in fname and fname.rsplit('.', 1)[1].lower() in allowed_extensions
        if not check_state:
            return False
    return True


def check_filestorages_extension(filestoragelist, allowed_extension):
    extension_valid_fs = []
    for fs in filestoragelist:
        check_state = '.' in fs.filename and \
                      fs.filename.rsplit('.', 1)[1].lower() in allowed_extension

        if check_state:
            extension_valid_fs.append(fs)
    return extension_valid_fs

def create_thumbnail(path, filename, base_width=300):
    imgname, ext = os.path.splitext(filename)
    newfilename = imgname + '_thumb_' + ext   # 缩略图的文件名
    img = Image.open(os.path.join(path, filename)) #根据指定的途径打开图像
    if img.size[0] > base_width:
        #如果图片宽度大于base_width，将其缩放到base_with,并保持图像原来的宽高比
        w_percent = (base_width / float(img.size[0]))
        h_size = int(float(img.size[1]*float(w_percent)))
        img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)

    img.save(os.path.join(path, newfilename))
    return newfilename


def create_show(path, filename, base_width=800):
    imgname, ext = os.path.splitext(filename)
    newfilename = imgname + '_show_' + ext   # 缩略图的文件名
    img = Image.open(os.path.join(path, filename)) #根据指定的途径打开图像
    if img.size[0] < base_width:
        # 如果图片宽度大于base_width，将其缩放到base_width,并保持图像原来的宽高比
        w_percent = (base_width / float(img.size[0]))
        h_size = int(float(img.size[1]*float(w_percent)))
        img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)

    img.save(os.path.join(path, newfilename))
    return newfilename







