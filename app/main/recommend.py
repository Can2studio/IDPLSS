# -*- coding: utf-8 -*-
"""
    main.recommend
    ~~~~~~~~~~~~

    处理兴趣推荐板块API请求

"""

from flask import jsonify, g

from . import main
from .. import redis_store
from .decorators import user_login_info
from .tasks import get_course, get_tests, get_text_resources
from ..recommend import popular_course, popular_text_resource, popular_test, code_start_course, code_start_test, \
    code_start_text_resource
from ..models import Course, TextResource, TestList, CourseBehavior, TextResourceBehavior, TestBehavior


# local val
RECOMMEND_COUNT = 3  # 推荐的数量


@main.route('/api/recommend/popular-courses', methods=['GET'])
def popular_courses_recommend():
    courses = popular_course()
    print "recommend courses is %s" % courses
    return jsonify({
                "count": len(courses),
                "recommend_courses": [course.to_json() for course in courses],
                "status": "successfully"
            })


@main.route('/api/recommend/popular-text-resources', methods=['GET'])
def popular_resources_recommend():
    resources = popular_text_resource()
    return jsonify({
                "count": len(resources),
                "recommend_text_resources": [t_resource.to_json() for t_resource in resources],
                "status": "successfully"
            })


@main.route('/api/recommend/popular-tests', methods=['GET'])
def popular_tests_recommend():
    tests = popular_test()
    print 'popular test is %s' % tests
    return jsonify({
                "count": len(tests),
                "recommend_tests": [test.to_json() for test in tests],
                "status": "successfully"
                })


@main.route('/api/recommend/courses/<int:type_id>')
@user_login_info
def recommend_courses(type_id):
    """
    推荐方式:未登录采用热度推荐,登录但是行为很少采用冷启动推荐,登录数据多采用算法(用户相似或者课程相似)推荐
    :param: type_id(采用的推荐算法的类型ItemCf或者UserCf)
    :return: course(json)
    """
    # 命名 UserCf(id_num_user_course),ItemCf(id_num_item_course)
    user = g.current_user
    if user is None:   # 如果用户未登录、则根据热度推荐
        courses = popular_course()
        return jsonify({
                "count": len(courses),
                "recommend_courses": [course.to_json() for course in courses],
                "status": "successfully"
            })

    else:
        user_behaviors = CourseBehavior.query.filter_by(user_id=user.id).all()
        if len(user_behaviors) < 5:   # 当用户行为的数量少于X时, 由于数据量少计算没有意义 因为根据用户兴趣标签来进行推荐
            print 'code start calc start'
            courses = code_start_course(user)

            return jsonify({
                "count": len(courses),
                "recommend_courses": [course.to_json() for course in courses],
                "status": "successfully"
            })
        else:                         # 如果行为数量已经足够,则进行UserCf或者ItemCf算法推荐
            print "personal recommend start"
            if type_id == 0:
                if redis_store.get(str(user.id)+"_1_user_course") is None:   # 如果缓存中没有课程数据,则计算
                    get_course.delay(user, type_id=0)
                    return jsonify({
                         "count": 0,
                         "recommend_courses": 0,
                         "status": 'calc...ing, wait for an hour'
                    })

                else:                                           # 如果缓存中有数据,则直接获取返回
                    courses = []
                    for x in range(1, RECOMMEND_COUNT+1):
                        course_name = str(user.id)+"_"+str(x)+"_user_course"
                        cid = redis_store.get(course_name)
                        if cid is not None:
                            courses.append(Course.query.filter_by(id=cid).first())
                    return jsonify({
                        "count": len(courses),
                        "recommend_courses": [course.to_json() for course in courses],
                        "status": "successfully"

                    })
            else:
                if redis_store.get(str(user.id)+"_1_item_course") is None:   # 如果缓存中没有课程数据,则计算
                    get_course.delay(user, type_id=1)
                    return jsonify({
                         "count": 0,
                         "recommend_courses": 0,
                         "status": 'calc...ing, wait for an hour'
                    })

                else:                                           # 如果缓存中有数据,则直接获取返回
                    courses = []
                    for x in range(1, RECOMMEND_COUNT+1):
                        course_name = str(user.id)+"_"+str(x)+"_item_course"
                        cid = redis_store.get(course_name)
                        if cid is not None:
                            courses.append(Course.query.filter_by(id=cid).first())
                    return jsonify({
                        "count": len(courses),
                        "recommend_courses": [course.to_json() for course in courses],
                        "status": "successfully"

                    })


@main.route('/api/recommend/text-resources/<int:type_id>')
@user_login_info
def recommend_text_resources(type_id):
    """
    推荐方式:未登录采用热度推荐,登录但是行为很少采用冷启动推荐,登录数据多采用算法(用户相似或者文本资源相似)推荐
    :param: type_id(采用的推荐算法的类型)
    :return: course(json)
    """
    # 命名 UserCf(id_num_user_resource),ItemCf(id_num_item_resource)
    user = g.current_user
    if user is None:
        resources = popular_text_resource()
        return jsonify({
                    "count": len(resources),
                    "recommend_text_resources": [t_resource.to_json() for t_resource in resources],
                    "status": "successfully"
                })
    else:
        user_behaviors = TextResourceBehavior.query.filter_by(user_id=user.id).all()
        if len(user_behaviors) < 5:   # 当用户行为的数量少于X时, 由于数据量少计算没有意义 因为根据用户兴趣标签来进行推荐
            print 'code start calc start'
            resources = code_start_text_resource(user)
            return jsonify({
                "count": len(resources),
                "recommend_text_resources": [t_resource.to_json() for t_resource in resources]
            })
        else:                         # 如果行为数量已经足够,则进行UserCf或者ItemCf算法推荐
            if type_id == 0:

                if redis_store.get(str(user.id)+"_1_user_resource") is None:   # 如果缓存中没有文本数据,则计算
                    get_text_resources.delay(user, type_id=0)
                    return jsonify({
                         "count": 0,
                         "recommend_text_resources": 0,
                         "status": 'calc...ing, wait for an hour'
                    })

                else:                                           # 如果缓存中有文本数据,则直接获取返回
                    resources_list = []
                    for x in range(1, RECOMMEND_COUNT+1):
                        resource_name = str(user.id)+"_"+str(x)+"_user_resource"
                        cid = redis_store.get(resource_name)
                        if cid is not None:
                            resources_list.append(TextResource.query.filter_by(id=cid).first())
                    return jsonify({
                        "count": len(resources_list),
                        "recommend_text_resources": [t_resource.to_json() for t_resource in resources_list],
                        "status": "successfully"

                    })
            else:
                if redis_store.get(str(user.id)+"_1_item_resource") is None:   # 如果缓存中没有数据,则计算
                    get_text_resources.delay(user, type_id=1)
                    return jsonify({
                         "count": 0,
                         "recommend_text_resources": 0,
                         "status": 'calc...ing, wait for an hour'
                    })

                else:                                           # 如果缓存中有数据,则直接获取返回
                    resources_list = []
                    for x in range(1, RECOMMEND_COUNT+1):
                        resource_name = str(user.id)+"_"+str(x)+"_item_resource"
                        cid = redis_store.get(resource_name)
                        if cid is not None:
                            resources_list.append(Course.query.filter_by(id=cid).first())
                    return jsonify({
                        "count": len(resources_list),
                        "recommend_text_resources": [t_resource.to_json() for t_resource in resources_list],
                        "status": "successfully"

                    })


@main.route('/api/recommend/tests/<int:type_id>')
@user_login_info
def recommend_test(type_id):
    """
    推荐方式:未登录采用热度推荐,登录但是行为很少采用冷启动推荐,登录数据多采用算法(用户相似或者课程相似)推荐
    :param: type_id(采用的推荐算法的类型)
    :return: course(json)
    """
    # 命名 UserCf(id_num_user_test),ItemCf(id_num_item_test)
    user = g.current_user
    if user is None:
        all_test = popular_test()
        return jsonify({
                "count": len(all_test),
                "recommend_tests": [test.to_json() for test in all_test],
                "status": "successfully"
                })
    else:
        user_behaviors = TestBehavior.query.filter_by(user_id=user.id).all()
        if len(user_behaviors) < 5:   # 当用户行为的数量少于X时, 由于数据量少计算没有意义 因为根据用户兴趣标签来进行推荐
            print 'code start calc start'
            all_test = code_start_test(user)
            return jsonify({
                "count": len(all_test),
                "recommend_tests": [test.to_json() for test in all_test],
                "status": "successfully"
            })
        else:
            if type_id == 0:
                if redis_store.get(str(user.id)+"_1_user_test") is None:   # 如果缓存中没有课程数据,则计算
                    get_tests.delay(user, type_id=0)
                    return jsonify({
                         "count": 0,
                         "recommend_tests": 0,
                         "status": 'calc...ing, wait for an hour'
                    })

                else:                                           # 如果缓存中有数据,则直接获取返回
                    tests = []
                    for x in range(1, RECOMMEND_COUNT+1):
                        test_name = str(user.id)+"_"+str(x)+"_user_test"
                        cid = redis_store.get(test_name)
                        if cid is not None:
                            tests.append(TestList.query.filter_by(id=cid).first())
                    return jsonify({
                        "count": len(tests),
                        "recommend_tests": [test.to_json() for test in tests],
                        "status": "successfully"

                    })
            else:
                if redis_store.get(str(user.id)+"_1_item_test") is None:   # 如果缓存中没有课程数据,则计算
                    get_tests.delay(user, type_id=1)
                    return jsonify({
                         "count": 0,
                         "recommend_tests": 0,
                         "status": 'calc...ing, wait for an hour'
                    })

                else:                                           # 如果缓存中有数据,则直接获取返回
                    tests = []
                    for x in range(1, RECOMMEND_COUNT+1):
                        test_name = str(user.id)+"_"+str(x)+"_item_test"
                        cid = redis_store.get(test_name)
                        if cid is not None:
                            tests.append(TestList.query.filter_by(id=cid).first())
                    return jsonify({
                        "count": len(tests),
                        "recommend_tests": [test.to_json() for test in tests],
                        "status": "successfully"

                    })


