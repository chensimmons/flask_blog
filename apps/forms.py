from flask_wtf import FlaskForm, CsrfProtect
from wtforms import StringField, PasswordField, IntegerField, DateField, FileField, SubmitField, \
    TextAreaField, SelectField
from wtforms.validators import DataRequired, Length, Email, NumberRange
from flask_wtf.file import FileRequired, FileAllowed

from flask_uploads import IMAGES
from apps.models import AlbumTag, Album


album_tags = AlbumTag.query.all()
# albums = Album.query.all()


class RegistForm(FlaskForm):
    user_name = StringField(
        label="用户名",
        validators=[DataRequired(message="用户名不能为空！"),
                    Length(min=2, max=15, message="用户名长度在3到15个字符之间！")],
        render_kw={'id': 'user_name',
                   'class': 'form-control',
                   'placeholder': '输入用户名'}

    )

    user_pwd = PasswordField(
        label="用户密码",
        validators=[DataRequired(message='用户密码不能为空！'),
                    Length(min=3, max=5, message="用户密码长度在3到5个字符之间")],
        render_kw={'id': 'user_pwd',
                   'class': 'form-control',
                   'placeholder': '输入用户密码'}
    )

    user_email = StringField(
        label="用户邮箱",
        validators=[DataRequired(message="用户邮箱不能为空！"),
                    Email(message="用户邮箱格式不对！")],
        render_kw={'id': 'user_email',
                   'class': 'form-control',
                   'placeholder': '输入用户邮箱'})

    user_face = FileField(
        label="用户头像",
        validators=[FileRequired(message='用户头像不能为空！'),
                    FileAllowed(IMAGES, '只允许头像格式为{}'.format(IMAGES))],

        render_kw={'id': 'user_face',
                   'class': 'form-control',
                   'placeholder': '上传用户头像'}
    )

    user_intro = TextAreaField(
        label="用户简介",
        validators=[],
        render_kw={'id': 'user_intro',
                   'class': 'form-control',
                   'placeholder': '输入用户简介'})

    submit = SubmitField(
        label="提交表单",
        render_kw={"id": 'user_face',
                   'class': "btn btn-success",
                   'value': '注册'}
    )


class LoginForm(FlaskForm):
    user_name = StringField(
        label="用户名",
        validators=[DataRequired(message="用户名不能为空！")],
        render_kw={'id': 'user_name',
                   'class': 'form-control',
                   'placeholder': '输入用户名'}

    )

    user_pwd = PasswordField(
        label="用户密码",
        validators=[DataRequired(message='用户密码不能为空！')],
        render_kw={'id': 'user_pwd',
                   'class': 'form-control',
                   'placeholder': '输入用户密码'}
    )

    submit = SubmitField(
        label="提交表单",
        render_kw={"id": 'user_face',
                   'class': "btn btn-success",
                   'value': '登录'}
    )


class PwdForm(FlaskForm):
    old_pwd = PasswordField(
        label="用户旧密码",
        validators=[DataRequired(message='用户密码不能为空！'),
                    Length(min=3, max=5, message="用户密码长度在3到5个字符之间")],
        render_kw={'id': 'old_pwd',
                   'class': 'form-control',
                   'placeholder': '输入用户旧密码'}
    )

    new_pwd = PasswordField(
        label="用户新密码",
        validators=[DataRequired(message='用户密码不能为空！'),
                    Length(min=3, max=5, message="用户密码长度在3到5个字符之间")],
        render_kw={'id': 'new_pwd',
                   'class': 'form-control',
                   'placeholder': '输入用户新密码'}
    )

    submit = SubmitField(
        label="提交表单",
        render_kw={"id": 'user_face',
                   'class': "btn btn-success",
                   'value': '修改'}
    )


class InfoForm(FlaskForm):
    user_name = StringField(
        label="用户名",
        validators=[DataRequired(message="用户名不能为空！"),
                    Length(min=3, max=15, message="用户名长度在3到15个字符之间！")],
        render_kw={'id': 'user_name',
                   'class': 'form-control',
                   'placeholder': '输入用户名'}

    )

    user_email = StringField(
        label="用户邮箱",
        validators=[DataRequired(message="用户邮箱不能为空！"),
                    Email(message="用户邮箱格式不对！")],
        render_kw={'id': 'user_email',
                   'class': 'form-control',
                   'placeholder': '输入用户邮箱'})

    user_face = FileField(
        label="用户头像",
        validators=[FileAllowed(IMAGES, '只允许头像格式为{}'.format(IMAGES))],
        render_kw={'id': 'user_face',
                   'class': 'form-control',
                   'placeholder': '上传用户头像'}
    )

    user_intro = TextAreaField(
        label="用户简介",
        validators=[],
        render_kw={'id': 'user_intro',
                   'class': 'form-control',
                   'placeholder': '输入用户简介'})

    submit = SubmitField(
        label="提交表单",
        render_kw={"id": 'user_face',
                   'class': "btn btn-success",
                   'value': '修改'}
    )


class AlbumInfoForm(FlaskForm):
    album_title = StringField(
        label="相册标题",
        validators=[DataRequired(message="相册标题不能为空！"),
                    Length(min=2, max=15, message="相册标题长度在3到15个字符之间！")],
        render_kw={'id': 'album_title',
                   'class': 'form-control',
                   'placeholder': '请输入相册标题'}

    )

    album_desc = TextAreaField(
        label='相册描述',
        validators=[DataRequired(message='相册描述不能为空'),
                    Length(min=2, max=120, message='相册描述长度在10-200个字符之间！')],
        render_kw={'id': 'album_desc',
                   'class': 'form-control',
                   'row': 3,
                   'placeholder': '输入相册描述'

                   }

    )

    album_privacy = SelectField(
        label='相册浏览权限',
        #validators=[DataRequired(message='相册浏览权限不能为空')],
        coerce=str,
        choices=[('private', '绝密(只有你可以浏览)'), ('protect-1', '私密(只有你粉丝可以浏览)'),
                 ('protect-2', '私密(收藏相册后可以浏览)'), ('public', '公开(所有人可以浏览)')],

        render_kw={'id': 'album_privacy',
                   'class': 'form-control',

                   }

    )


    album_tag = SelectField(
        label='相册类别标签',
        validators=[DataRequired(message='相册标签不能为空')],
        coerce=int,
        choices=[(tag.id, tag.name) for tag in album_tags],

        render_kw={'id': 'album_privacy',
                   'class': 'form-control',}

    )

    submit = SubmitField(
        label="提交表单",
        render_kw={
                   'class': "form-control btn btn-primary",
                   'value': '创建相册'}
    )



class AlbumUploadForm(FlaskForm):
    album_title = SelectField(

        # validators=[DataRequired(message='相册名称不能为空')],
        coerce=int,
        #choices=[(item.id, item.title) for item in albums],

        render_kw={'id': 'album_title', 'class': 'form-control', }
    )

    album_upload = FileField(
        # validators=[FileRequired(message='请选择一张或多张图片'),
        #             FileAllowed(IMAGES, '只允许头像格式为{}'.format(IMAGES))],

        render_kw={'id': 'album_upload',
                   'class': 'form-control',
                   'multiple':'multiple'}
    )

    submit = SubmitField(
        render_kw={
            'class': "form-control btn btn-primary",
            'value': '上传相册图片'}
    )