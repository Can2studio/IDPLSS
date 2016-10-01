# coding: utf-8
from flask import current_app, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired
from datetime import datetime
from app.utils.model_tools import set_model_attr, user_info_transform, id_change_user, time_transform
from app import db


class Permission:
    """
    系统权限划分
    说明:
    暂无
    """
    COMMENT_FOLLOW_COLLECT = 0x01
    UPLOAD_RESOURCE = 0x02
    UPLOAD_VIDEO = 0x04
    WRITE_ARTICLE = 0x08
    DELETE_VIDEO = 0x10
    DELETE_RESOURCE = 0x20
    DELETE_ARTICLE = 0x40
    ADMINISTER = 0x80

    def __init__(self):
        pass


class Follow(db.Model):
    """
    用户关注表:
    follower_id:粉丝id
    followed_id:被关注者id
    """
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return '< follower_id %r>' % self.followed_id

    def followers_to_json(self):
        json_follow = {
            "name": user_info_transform(self.follower_id, 'name'),
            "user_url": url_for('main.show_user', uid=self.follower_id, _external=True),
            "user_id": self.follower_id,
            "user_avatar": user_info_transform(self.follower_id, 'avatar'),
            "about_me": user_info_transform(self.follower_id, 'about_me')
        }
        return json_follow

    def following_to_json(self):
        json_following = {
            "name": user_info_transform(self.followed_id, 'name'),
            "user_url": url_for('main.show_user', uid=self.followed_id, _external=True),
            "user_id": self.followed_id,
            "user_avatar": user_info_transform(self.followed_id, 'avatar'),
            "about_me": user_info_transform(self.followed_id, 'about_me')
        }
        return json_following


class Role(db.Model):
    """
    角色表,定义系统中用户角色
    分为:学生,教师,学校管理员,系统管理员
    说明:暂无
    """
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True, index=True)
    role_name = db.Column(db.String(32), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def create_roles():
        roles = {
            'Student': (Permission.COMMENT_FOLLOW_COLLECT |
                        Permission.UPLOAD_RESOURCE |
                        Permission.WRITE_ARTICLE, True),
            'Teacher': (Permission.COMMENT_FOLLOW_COLLECT |
                        Permission.UPLOAD_RESOURCE |
                        Permission.UPLOAD_VIDEO |
                        Permission.WRITE_ARTICLE, False),
            'SchoolAdmin': (Permission.COMMENT_FOLLOW_COLLECT |
                            Permission.UPLOAD_VIDEO |
                            Permission.UPLOAD_RESOURCE |
                            Permission.WRITE_ARTICLE |
                            Permission.DELETE_ARTICLE |
                            Permission.DELETE_RESOURCE |
                            Permission.DELETE_VIDEO, False),
            'Admin': (0xff, False)

        }
        for r in roles:
            role = Role.query.filter_by(role_name=r).first()
            if role is None:
                role = Role(role_name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.role_name


collectionPosts = db.Table('collectionPosts',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id')),
    db.Column('timestamp', db.DateTime, default=datetime.utcnow)
    )


collectionCourses = db.Table('collectionCourses',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id')),
    db.Column('timestamp', db.DateTime, default=datetime.utcnow)
    )


collectionTextResource = db.Table('collectionTextResource',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('text_resource_id', db.Integer, db.ForeignKey('text_resources.id')),
    db.Column('timestamp', db.DateTime, default=datetime.utcnow)
    )


class User(db.Model):
    """
    用户信息表
    说明:
    user_type: 0代表学生,用户注册时默认为学生,1代表教师,school_admin可以对该值进行修改


    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    user_name = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(32), unique=True, index=True)
    user_type = db.Column(db.Integer, default=0)
    avatar = db.Column(db.String(64))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(32))
    about_me = db.Column(db.String(128))
    followings = db.relationship('Follow', foreign_keys=[Follow.follower_id], backref=db.backref('follower',
                                lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')
    followers = db.relationship('Follow', foreign_keys=[Follow.followed_id], backref=db.backref('followed',
                                lazy='joined'), lazy='dynamic', cascade='all, delete-orphan')
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    post_comments = db.relationship('PostComment', backref='author', lazy='dynamic')
    courses = db.relationship('Course', backref='author', lazy='dynamic')
    courses_video = db.relationship('VideoList', backref='uploader', lazy='dynamic')
    course_comments = db.relationship('CourseComment', backref='author', lazy='dynamic')
    text_resource = db.relationship('TextResource', backref='uploader', lazy='dynamic')
    text_resource_comments = db.relationship('TextResourceComment', backref='author', lazy='dynamic')
    collection_posts = db.relationship('Post', secondary=collectionPosts,
                                       backref=db.backref('users', lazy='dynamic'), lazy='dynamic')
    collection_courses = db.relationship('Course', secondary=collectionCourses,
                                        backref=db.backref('users', lazy='dynamic'), lazy='dynamic')
    collection_text_resource = db.relationship('TextResource', secondary=collectionTextResource,
                                               backref=db.backref('users', lazy='dynamic'), lazy='dynamic')

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['IDPLSS_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    def __repr__(self):
        return '<User %r>' % self.user_name

    def to_json(self):
        json_user = {
            'user_id': self.id,
            'user_name': self.user_name,
            'name': self.name,
            'user_email': self.email,
            'user_type': self.user_type,
            'user_avatar': self.avatar,
            'user_about_me': self.about_me,
            'user_member_since': time_transform(self.member_since),
            'user_last_seen': time_transform(self.last_seen),
            'user_followers': self.followers.count(),
            'user_followings': self.followings.count(),
            'user_confirmed': self.confirmed
        }
        return json_user

    @staticmethod
    def from_json(user, json_user):
        user.name = set_model_attr(json_user, 'name')
        user.about_me = set_model_attr(json_user, 'about_me')
        user.avatar = set_model_attr(json_user, 'avatar')
        return user

    @property
    def pass_word(self):
        raise AttributeError('the attribute can not to read')

    @pass_word.setter
    def pass_word(self, password):
        """
        设置密码,verify_password验证密码散列值是否正确
        :param password:
        :return:
        """
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expiration=3600):
        """
        生成具有时效的token,供用户登录的调用,无需每次都上传用户名和密码
        :param expiration:
        :return:
        """
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        user = User.query.get(data['id'])
        if user is None:
            return None
        else:
            return user

    def generate_confirm_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'confirm': self.id})

    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get['confirm'] != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True

    def can(self, permissions):
        return self.role is not None and (self.role.permissions & permissions) == permissions

    def is_administer(self):
        return self.can(Permission.ADMINISTER)

    def update_login_time(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)
            db.session.commit()

    def unfollow(self, user):
        print self.user_name
        print user.user_name
        f = self.followings.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
            db.session.commit()

    def is_following(self, user):
        """
        判断当前用户是否关注了user, 如果用户已经关注,返回True,没有关注返回false
        :param user:
        :return:boolean
        """
        return self.followings.filter_by(followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        """
        判断当前用户是否被user关注  如果是用户的粉丝,返回True,如果不是,返回False
        :param user:
        :return: boolean
        """
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def collect_post(self, post):
        if not self.is_collecting_post(post):
            self.collection_posts.append(post)
            db.session.commit()

    def uncollect_post(self, post):
        if self.is_collecting_post(post):
            self.collection_posts.remove(post)
            db.session.commit()

    def is_collecting_post(self, post):
        if post in self.collection_posts.all():
            return True
        else:
            return False

    def is_collecting_course(self, course):
        if course in self.collection_courses.all():
            return True
        else:
            return False

    def collect_course(self, course):
        if not self.is_collecting_course(course):
            self.collection_courses.append(course)
            db.session.commit()

    def uncollect_course(self, course):
        if self.is_collecting_course(course):
            self.collection_courses.remove(course)
            db.session.commit()

    def is_collecting_text_resouurce(self, text_resource):
        if text_resource in self.collection_text_resource.all():
            return True
        else:
            return False

    def collect_text_resouce(self, text_resource):
        if not self.is_collecting_text_resouurce(text_resource):
            self.collection_text_resource.append(text_resource)
            db.session.commit()

    def uncollect_text_resource(self, text_resource):
        if self.is_collecting_text_resouurce((text_resource)):
            self.collection_text_resource.remove(text_resource)
            db.session.commit()


class AnonymousUser(object):
    def __init__(self):
        pass

    @staticmethod
    def can(permissions):
        return False

    @staticmethod
    def is_admin():
        return False


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    post_category = db.Column(db.Integer, default=1)  # 计算机/互联网0 基础科学1 工程技术2 历史哲学3 经管法律4 语言文学5 艺术音乐6
    body = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    images = db.Column(db.String(512))
    show = db.Column(db.Boolean, default=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('PostComment', backref='post', lazy='dynamic')

    def __repr__(self):
        return '< Post_title %r>' % self.title

    def to_json(self):
        json_post = {
            'id': self.id,
            'title': self.title,
            'post_category': self.post_category,
            'body': self.body,
            'timestamp': time_transform(self.timestamp),
            'images': self.images,
            'show': self.show,
            'author_id': self.author_id,
            'author_user_name': id_change_user(self.author_id).user_name,
            'author_name': id_change_user(self.author_id).name,
            'author_avatar': id_change_user(self.author_id).avatar,
            'comments_count': self.comments.count()
        }
        return json_post

    @staticmethod
    def from_json(json_post):
        body = json_post.get('body')
        post_category = json_post.get('post_category')
        author_id = json_post.get('author_id')
        title = json_post.get('title')
        images = json_post.get('images')
        return Post(title=title, body=body, author_id=author_id, images=images, post_category=post_category)


class PostComment(db.Model):
    __tablename__ = 'post_comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(128))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    show = db.Column(db.Boolean, default=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))

    def __repr__(self):
        return '<Comment_id %r>' % self.id

    def to_json(self):
        json_comment = {
            'comment_id': self.id,
            'body': self.body,
            'author_id': self.author_id,
            'author_user_name': id_change_user(self.author_id).user_name,
            'author_name': id_change_user(self.author_id).name,
            'author_avatar': id_change_user(self.author_id).avatar,
            'timestamp': time_transform(self.timestamp),
            'show': self.show,
            'post_id': self.post_id
        }
        return json_comment

    @staticmethod
    def from_json(json_post_comment):
        body = json_post_comment.get('body')
        author_id = json_post_comment.get('author_id')
        post_id = json_post_comment.get('post_id')
        return PostComment(body=body, author_id=author_id, post_id=post_id)


class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(128))
    description = db.Column(db.Text)
    course_category = db.Column(db.Integer, default=1)  # 计算机/互联网0 基础科学1 工程技术2 历史哲学3 经管法律4 语言文学5 艺术音乐6
    images = db.Column(db.String(256))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    show = db.Column(db.Boolean, default=True)
    course_all_video = db.relationship('VideoList', backref='course', lazy='dynamic')
    course_comments = db.relationship('CourseComment', backref='course', lazy='dynamic')

    def __repr__(self):
        return '<course_name is %r>' % self.course_name

    def to_json(self):
        json_course = {
            'id': self.id,
            'course_name': self.course_name,
            'description': self.description,
            'course_category': self.course_category,
            'images': self.images,
            'show': self.show,
            'timestamp': time_transform(self.timestamp),
            'author_id': self.author_id,
            'author_user_name': id_change_user(self.author_id).user_name,
            'author_name': id_change_user(self.author_id).name,
            'author_avatar': id_change_user(self.author_id).avatar,
            'video_count': self.course_all_video.count(),
            'comments_count': self.course_comments.count()
        }
        return json_course

    @staticmethod
    def from_json(json_course):
        course_name = json_course.get('course_name')
        description = json_course.get('description')
        category = json_course.get('category')
        images = json_course.get('images')
        author_id = json_course.get('author_id')
        return Course(course_name=course_name, description=description, course_category=category,
                       images=images, author_id=author_id)


class VideoList(db.Model):
    __tablename__ = 'video_list'
    id = db.Column(db.Integer, primary_key=True)
    video_name = db.Column(db.String(128))
    video_description = db.Column(db.Text)
    source_url = db.Column(db.String(256))
    show = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    time_line = db.Column(db.String(128))
    # TODO:保留一个timeline 如前端能返回视频的时间则用
    video_order = db.Column(db.Integer)  # 视频的顺序
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

    def __repr__(self):
        return '<course_video_name is %r>' % self.video_name

    def to_json(self):
        json_video = {
            'id': self.id,
            'video_name': self.video_name,
            'video_description': self.video_description,
            'source_url': self.source_url,
            'show': self.show,
            'timestamp': time_transform(self.timestamp),
            'time_line': self.time_line,
            'author_id': self.author_id,
            'video_order': self.video_order,
            'author_user_name': id_change_user(self.author_id).user_name,
            'author_name': id_change_user(self.author_id).name,
            'author_avatar': id_change_user(self.author_id).avatar,
            'course_id': self.course_id
        }
        return json_video

    @staticmethod
    def from_json(json_video):
        video_name = json_video.get('video_name')
        video_description = json_video.get('video_description')
        source_url = json_video.get('source_url')
        author_id = json_video.get('author_id')
        video_order = json_video.get('video_order')
        course_id = json_video.get('course_id')
        return VideoList(video_name=video_name, video_description=video_description, source_url=source_url,
                         author_id=author_id, course_id=course_id, video_order=video_order)


class CourseComment(db.Model):
    __tablename__ = 'course_comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(128))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    show = db.Column(db.Boolean, default=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))

    def __repr__(self):
        return 'CourseComment_id %r>' % self.id

    def to_json(self):
        json_comment = {
            'id': self.id,
            'body': self.body,
            'author_id': self.author_id,
            'author_user_name': id_change_user(self.author_id).user_name,
            'author_avatar': id_change_user(self.author_id).avatar,
            'author_name': id_change_user(self.author_id).name,
            'timestamp': time_transform(self.timestamp),
            'show': self.show,
            'course_id': self.course_id
        }
        return json_comment

    @staticmethod
    def from_json(json_course_comment):
        body = json_course_comment.get('body')
        author_id = json_course_comment.get('author_id')
        course_id = json_course_comment.get('course_id')
        return CourseComment(body=body, author_id=author_id, course_id=course_id)


class TextResource(db.Model):
    __tablename__ = 'text_resources'
    id = db.Column(db.Integer, primary_key=True)
    resource_name = db.Column(db.String(128))
    description = db.Column(db.Text)
    resource_category = db.Column(db.Integer, default=1)  # 计算机/互联网0 基础科学1 工程技术2 历史哲学3 经管法律4 语言文学5 艺术音乐6
    resource_type = db.Column(db.Integer, default=0)  # word类型1  excel类型2  pdf类型3  ppt类型4 其它0
    source_url = db.Column(db.String(256))
    show = db.Column(db.Boolean, default=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('TextResourceComment', backref='text_resources', lazy='dynamic')

    def __reper__(self):
        return '<TextResource file_name %r>' % self.file_name

    def to_json(self):
        json_text_resource = {
            "id": self.id,
            "resource_name": self.resource_name,
            "description": self.description,
            "source_url": self.source_url,
            "show": self.show,
            "resource_type":self.resource_type,
            "timestamp": time_transform(self.timestamp),
            "author_id": self.author_id,
            "author_user_name": id_change_user(self.author_id).user_name,
            "author_name": id_change_user(self.author_id).name,
            "author_avatar": id_change_user(self.author_id).avatar,
            "resource_category": self.resource_category
        }
        return json_text_resource

    @staticmethod
    def from_json(json_text_resource):
        resource_name = json_text_resource.get('resource_name')
        description = json_text_resource.get('description')
        source_url = json_text_resource.get('source_url')
        author_id = json_text_resource.get('author_id')
        resource_type = json_text_resource.get('resource_type')
        resource_category = json_text_resource.get('resource_category')
        return TextResource(resource_name=resource_name, description=description, source_url=source_url,
                            author_id=author_id, resource_type=resource_type, resource_category=resource_category)


class TextResourceComment(db.Model):
    __tablename__ = 'resource_comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(128))
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    show = db.Column(db.Boolean, default=True)
    text_resource_id = db.Column(db.Integer, db.ForeignKey('text_resources.id'))

    def __repr__(self):
        return '<TextResourceComment id %r>' % self.id

    def to_json(self):
        json_text_resource_comment = {
            "id": self.id,
            "body": self.body,
            "author_id": self.author_id,
            "author_user_name": id_change_user(self.author_id).user_name,
            "author_name": id_change_user(self.author_id).name,
            "author_avatar": id_change_user(self.author_id).avatar,
            "timestamp": time_transform(self.timestamp),
            "show": self.show,
            "text_resource_id": self.text_resource_id
        }
        return json_text_resource_comment

    @staticmethod
    def from_json(json_resource_comment):
        body = json_resource_comment.get('body')
        author_id = json_resource_comment.get('author_id')
        text_resource_id = json_resource_comment.get('text_resource_id')
        return TextResourceComment(body=body, author_id=author_id, text_resource_id=text_resource_id)



