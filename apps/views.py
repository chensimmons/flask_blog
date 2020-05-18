import os
import shutil
import uuid
from random import randint
from flask import render_template, request, redirect, g, flash, session, make_response, url_for
from functools import wraps
from flask_uploads import UploadSet, IMAGES, UploadNotAllowed, configure_uploads
from werkzeug.security import generate_password_hash
from apps import app
from apps.forms import *
from apps.utils import *
from apps.models import *
from apps import db

photoSet = UploadSet(name='photos', extensions=IMAGES)
configure_uploads(app, photoSet)


# 登录装饰器检查登录状态
def user_login_req(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_name" not in session:
            return redirect(url_for("user_login", next=request.url))
        return f(*args, **kwargs)

    return decorated_function


@app.route('/')
def index():
    # all = User.query.all()
    # print(all)
    return render_template('index.html')


@app.route('/user/login/', methods=['GET', 'POST'])
def user_login():
    form = LoginForm()
    if form.validate_on_submit():
        username = request.form['user_name']
        userpwd = request.form['user_pwd']
        # 查看用户名是否存在
        user_x = User.query.filter_by(name=username).first()
        if not user_x:
            flash("用户名不存在", category="err")
            return render_template('user_login.html', form=form)
        else:
            if not user_x.check_pwd(str(userpwd)):
                flash('用户输入密码错误', category='err')
                return render_template('user_login.html', form=form)
            else:
                # flash("登陆成功", category='ok')
                session["user_name"] = user_x.name
                session["user_id"] = user_x.id
                return redirect(url_for('index'))
    return render_template('user_login.html', form=form)


@app.route('/user/logout')
@user_login_req
def logout():
    # remove the username from the session if it's there
    session.pop('user_name', None)
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/user/regist/', methods=['GET', 'POST'])
def user_regist():
    form = RegistForm()
    if form.validate_on_submit():

        # 查看用户名是否存在
        user_name = form.user_name.data
        user_x = User.query.filter_by(name=user_name).first()
        if user_x:
            flash("用户名已经存在！", category='err')
            return render_template('user_regist.html', form=form)

        user_email = form.user_email.data
        user_x = User.query.filter_by(email=user_email).first()
        if user_x:
            flash("邮箱已经被注册！", category='err')
            return render_template('user_regist.html', form=form)

        # 如果用户不存在，执行注册
        user = User()
        user.name = form.user_name.data
        user.pwd = generate_password_hash(form.user_pwd.data)
        user.email = form.user_email.data
        user.intro = form.data['user_intro']
        user.uuid = str(uuid.uuid4().hex)[0:10]
        filestorage = request.files['user_face']
        print(filestorage)
        user.face = secure_filename_with_uuid(filestorage.filename)

        # 保存用户头像
        try:
            db.session.add(user)
            db.session.commit()
            photoSet.save(storage=filestorage, folder=user.name, name=user.face)

            flash("用户注册成功！", category='ok')
            return redirect(url_for("user_login", username=user.name))
        except UploadNotAllowed:
            flash("头像文件格式不对", category='err')
            return render_template('user_regist.html', form=form)

    return render_template('user_regist.html', form=form)


# 定义的user_login函数要放在user_regist函数前面，才能实现重定向


@app.route('/user/center/')
@user_login_req
def user_center():
    return render_template("user_center.html")


@app.route('/user/detail/')
@user_login_req
def user_detail():
    user = User.query.get_or_404(int(session.get('user_id')))

    face_url = photoSet.url(user.name + "/" + user.face)
    return render_template('user_detail.html', face_url=face_url, user=user)


@app.route("/user/pwd/", methods=["GET", "POST"])
@user_login_req
def user_pwd():
    form = PwdForm()
    if form.validate_on_submit():
        old_pwd = form.old_pwd.data
        new_pwd = form.new_pwd.data
        user = User.query.get_or_404(int(session.get('user_id')))
        if user.check_pwd(old_pwd):

            user.pwd = generate_password_hash(new_pwd)
            db.session.add(user)
            db.session.commit()
            session.pop('user_name', None)
            session.pop('user_id', None)
            flash(message="修改密码成功，请重新登录！", category='ok')
            return redirect(url_for("user_login", username=user.name))
        else:
            flash(message="旧密码输入错误！", category='err')
            return render_template("user_pwd.html", form=form)
    return render_template("user_pwd.html", form=form)


@app.route("/user/info/", methods=['GET', 'POST'])
@user_login_req
def user_info():
    form = InfoForm()
    user = User.query.get_or_404(int(session.get('user_id')))
    if request.method == 'GET':
        form.user_intro.data = user.intro

    if form.validate_on_submit():
        old_name = user.name
        user.name = form.data["user_name"]
        user.email = form.data["user_email"]

        user.intro = form.user_intro.data

        if "user_face" in request.files:

            # 如果上传了新的头像文件，则首先删除旧的，再保存新的
            filestorage = request.files["user_face"]

            userface_path = photoSet.path(filename=user.face, folder=old_name)
            os.remove(path=userface_path)
            user.face = secure_filename_with_uuid(filestorage.filename)
            photoSet.save(storage=filestorage, folder=old_name, name=user.face)

        else:
            pass

        if old_name != user.name:
            os.rename(os.path.join(app.config["UPLOADS_FOLDER"], old_name),
                      os.path.join(app.config["UPLOADS_FOLDER"], user.name))

        # 更新数据项
        db.session.add(user)
        db.session.commit()
        session["user_name"] = user.name
        session['user_id'] = user.id
        return redirect(url_for("user_detail"))
    return render_template("user_info.html", user=user, form=form)


@app.route('/user/del/', methods=['GET', 'POST'])
@user_login_req
def user_del():
    if request.method == 'POST':
        # 删除用户上传的文件资源
        del_path = os.path.join(app.config["UPLOADS_FOLDER"], session.get('user_name'))
        shutil.rmtree(del_path, ignore_errors=True)
        user = User.query.get_or_404(int(session.get('user_id')))
        db.session.delete(user)
        db.session.commit()
        return redirect(url_for('logout'))
    return render_template('user_del.html')


@app.route('/album/')
def album_index():
    return render_template('album_index.html')


@app.route('/album/create', methods=['GET', 'POST'])
@user_login_req
def album_create():
    form = AlbumInfoForm()

    if form.validate_on_submit():
        album_title = form.album_title.data
        existedCount = Album.query.filter(Album.user_id == session['user_id'],
                                          Album.title == album_title).count()

        if existedCount >= 1:
            flash(message='相册已存在', category='err')
            return render_template('album_create.html', form=form)

        album_desc = form.album_desc.data
        album_privacy = form.album_privacy.data
        album_tag = form.album_tag.data
        existed = True
        album_uuid = str(uuid.uuid4().hex)[0:10]
        # 确保UUID唯一
        while existed:
            if Album.query.filter_by(uuid=album_uuid).count() > 0:
                existed = True
                album_uuid = str(uuid.uuid4().hex)[0:10]
            else:
                existed = False

        album = Album(title=album_title, description=album_desc, privacy=album_privacy, tag_id=album_tag,
                      uuid=album_uuid, user_id=int(session.get('user_id')))
        db.session.add(album)
        db.session.commit()

        return redirect(url_for('album_upload'))
    return render_template('album_create.html', form=form)


@app.route('/album/upload', methods=['GET', 'POST'])
def album_upload():
    form = AlbumUploadForm()
    albums = Album.query.filter_by(user_id=session.get('user_id')).all()
    form.album_title.choices = [(item.id, item.title) for item in albums]
    if len(form.album_title.choices) < 1:
        flash(message='请先创建一个相册', category='err')
        return redirect(url_for('album_create'))
    # if form.validate_on_submit():
    if request.method == 'POST':
        fses = request.files.getlist('album_upload')

        valid_fses = check_filestorages_extension(fses, ALLOWED_IMAGE_EXTENSIONS)
        if len(valid_fses) < 1:
            flash(message='只允许上传文件类型：' + str(ALLOWED_IMAGE_EXTENSIONS), category='err')
            return redirect((url_for('album_upload')))
        else:
            files_url = []
            album_cover = ''
            for fs in valid_fses:
                album_title = ''
                for id, title in form.album_title.choices:
                    if id == form.album_title.data:
                        album_title = title
                folder = session.get('user_name') + '/' + album_title
                name_origin = secure_filename_with_uuid(fs.filename)
                ts_path = photoSet.config.destination + '/' + folder
                fname = photoSet.save(fs, folder=folder, name=name_origin)
                # 创建并保存缩略图
                name_thumb = create_thumbnail(path=ts_path, filename=name_origin, base_width=300)
                # 创建并保存展示图
                name_show = create_show(path=ts_path, filename=name_origin, base_width=800)
                # 把产生的Photo 对象保存到数据库
                photo = Photo(originame=name_origin, showname=name_show, thumbname=name_thumb,
                              album_id=form.album_title.data)
                db.session.add(photo)
                db.session.commit()
                # 设置封面图像
                album_cover = photo.thumbname

                # 获取刚才保存的缩略图文件的URL
                furl = photoSet.url(folder + '/' + name_thumb)
                files_url.append(furl)
            album = Album.query.filter_by(id=form.album_title.data).first()

            album.photonum += len(valid_fses)
            album.cover = album_cover
            db.session.add(album)  # update 数据
            db.session.commit()
            message = '成功保存：' + str(len(valid_fses)) + '张图像;'
            message += '当前相册共有：' + str(album.photonum) + '张图像'
            flash(message=message, category='ok')
            return render_template('album_upload.html', form=form, files_url=files_url)

    return render_template('album_upload.html', form=form)


@app.route('/album/list/<int:page>', methods=['GET'])
def album_list(page):
    albumtags = AlbumTag.query.all()
    tag_id = request.args.get('tag', 'all')
    # print("************")
    if tag_id == 'all':
        albums = Album.query.filter(Album.privacy != 'private' ) \
            .order_by(Album.addtime.desc()).paginate(page=page, per_page=4)
        # print('###########123')
    else:
        albums = Album.query.filter(Album.privacy != 'private', Album.tag_id == int(tag_id)) \
            .order_by(Album.addtime.desc()).paginate(page=page, per_page=4)
        # print('1234567')
    # album_covers_url = []
    for album in albums.items:
        # cover_image = album.photos[randint(0, len(album.photos) - 1)].thumbname
        folder = album.user.name + '/' + album.title
        cover_image_url = photoSet.url(filename=folder + '/' + album.cover)
        album.cover_image_url = cover_image_url
        # album_covers_url.append(cover_image_url)
        # print(album, 1234556)
    # for album in albums.items:
    #
    #     print("**********", albums.items,  123456)
    # print(albums.iter_pages())
    # for rt in albums.iter_pages():
    #     print(rt)
    return render_template('album_list.html', albumtags=albumtags, albums=albums)


@app.route('/album/browse/<int:id>', methods=["GET"])
def album_browse(id):
    album = Album.query.get_or_404(int(id))
    album.clicknum += 1
    db.session.add(album)
    db.session.commit()
    recommend_albums = Album.query.filter(Album.tag_id == album.tag_id,
                                          Album.id != album.id).all()

    for rec_album in recommend_albums:
        rec_album.cover = rec_album.photos[randint(0, len(rec_album.photos) - 1)].thumbname
        folder = rec_album.user.name + '/' + rec_album.title
        cover_image_url = photoSet.url(filename=folder + '/' + rec_album.cover)
        rec_album.cover_image_url = cover_image_url
    # 我的收藏
    favor_albums = []
    if 'user_id' in session:
        login_user = User.query.get_or_404(int(session.get('user_id')))
        for favor in login_user.favors:
            favor_albums.append(favor.album)
        for f_album in favor_albums:
            f_album.cover = f_album.photos[randint(0, len(f_album.photos) - 1)].thumbname
            folder = f_album.user.name + '/' + f_album.title
            cover_image_url = photoSet.url(filename=folder + '/' + f_album.cover)
            f_album.cover_image_url = cover_image_url
    # 取出作者头像
    user_face_url = photoSet.url(filename=album.user.name+'/'+album.user.face)
    for photo in album.photos:
        photo_folder = album.user.name + '/' + album.title + '/'
        photo.url = photoSet.url(filename=photo_folder + photo.showname)
    return render_template('album_browse.html', album=album,
                           user_face_url=user_face_url,
                           recommend_albums=recommend_albums,
                           favor_albums=favor_albums)


@app.route('/album/favor', methods=['GET'])
def album_favor():
    #获取参数
    aid = request.args.get('aid')
    uid = request.args.get('uid')
    act = request.args.get('act')
    if act == 'add':
        # 不能收藏自己的相册
        album = Album.query.get_or_404(int(aid))
        if album.user_id == session.get('user_id'):
            res = {'ok': -1}
        else:

            # 查询数据库是否已存在相同记录
            existed_count = AlbumFavor.query.filter_by(user_id=uid, album_id=aid).count()
            if existed_count >= 1:
                res = {'ok': 0}
            else:
                favor = AlbumFavor(user_id=uid, album_id=aid)
                db.session.add(favor)
                db.session.commit()
                res = {'ok': 1}
                # 累计该相册的收藏量
                album.favornum += 1
                db.session.add(album)
                db.session.commit()
    if act == 'del':
        favor = AlbumFavor.query.filter_by(user_id=uid, album_id=aid).first_or_404()

        db.session.delete(favor)
        db.session.commit()
        res = {'ok': 2}
        album = Album.query.get_or_404(int(aid))
        album.favornum -= 1
        db.session.add(album)
        db.session.commit()
    import json
    return json.dumps(res)

@app.route('/user/album/favor/', methods=['GET'])
def user_album_favor():

    albumtags = AlbumTag.query.all()
    tag_id = request.args.get('tag', 'all')

    if tag_id == 'all':
        albums = Album.query.join(AlbumFavor). \
            filter(Album.privacy != 'private',
                   AlbumFavor.user_id == int(session.get('user_id'))) \
            .order_by(Album.addtime.desc()).all()
    else:
        albums = Album.query.join(AlbumFavor).filter(
            Album.privacy != 'private', Album.tag_id == int(tag_id),
            AlbumFavor.user_id == int(session.get('user_id'))) \
            .order_by(Album.addtime.desc()).all()

    for album in albums:
        # cover_image = album.photos[randint(0, len(album.photos) - 1)].thumbname
        folder = album.user.name + '/' + album.title
        cover_image_url = photoSet.url(filename=folder + '/' + album.cover)
        album.cover_image_url = cover_image_url
    return render_template('user_album_favor.html', albumtags=albumtags, albums=albums)



@app.route('/user/album/mine/', methods=['GET'])
def user_album_mine():
    return render_template('user_album_mine.html')


@app.errorhandler(404)
def page_not_found(error):
    resp = make_response(render_template('page_not_found.html'), 404)
    return resp
