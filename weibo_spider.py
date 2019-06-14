from selenium import webdriver
import time
import env
import db_tool
import data_model
import re


class WeiboSpider(object):
    def __init__(self, login_url):
        self.__browser = webdriver.Chrome()
        self.__db_session = db_tool.Session()
        self.__login(login_url=login_url)

    def __login(self, login_url, wait_login_time_out=20):
        self.__browser.get(login_url)
        time.sleep(wait_login_time_out)

    def get_weibo_detail_page_content(self):  # 根据微博URL获取详情页内容
        weibo_function_elements = self.__browser.find_elements_by_class_name('WB_handle')
        if not weibo_function_elements:
            return None
        weibo_function_element=weibo_function_elements[0]
        weibo_functions = weibo_function_element.text.split('\n')
        if len(weibo_functions) !=4:
            return None
        model = data_model.Weibo()
        # 获取转发数
        forward = re.findall(r'\d+', weibo_functions[1])
        if not forward:
            model.forward = 0
        else:
            model.forward = forward[0]
        # 获取评论数
        comment = re.findall(r'\d+', weibo_functions[2])
        if not comment:
            model.comment = 0
        else:
            model.comment = comment[0]
        # 获取点赞数
        like = re.findall(r'\d+', weibo_functions[3])
        if not like:
            model.like = 0
        else:
            model.like = like[0]
        # 获取微博文本
        model.content = self.__browser.find_elements_by_class_name('WB_text')[0].text
        # 获取微博图片使用情况
        images = self.__browser.find_elements_by_class_name('artwork_box')
        if images:
            model.image = 1
            image_box = self.__browser.find_elements_by_class_name('choose_box')
            if image_box:
                image_list = image_box[0].find_elements_by_tag_name("li")
                model.image = len(image_list)
        else:
            model.image = 0
         # 获取微博表情使用情况
        faces = self.__browser.find_elements_by_class_name('WB_text')[0].find_elements_by_class_name('W_img_face')
        if faces:
            face_list=[]
            for face in faces:
                face_list.append(face.get_attribute('title'))
                # print(face.get_attribute('title'))
            model.face_title=','.join(face_list)
            model.face = len(face_list)
        else:
            model.face = 0
        return model

    def get_detail_page_url_list(self): #获取不实信息列表中的URL列表
        report_list_elements = self.__browser.find_elements_by_class_name('m_table_tit')[1:]
        report_detail_page_url_list = []
        for element in report_list_elements:
            report_element = element.find_element_by_tag_name('a')
            # 获取列表页网址
            url = report_element.get_property('href')
            report_detail_page_url_list.append(url)
        return report_detail_page_url_list
        # 网址去重后返回URL列表，似乎没有重复的
        # return list(set(report_detail_page_url_list))


    def get_origin_weibo_url(self): # 获取原始微博URL、发布时间、用户id、用户名
        origin_url = None
        win = self.__browser.find_elements_by_class_name('resault')
        if not win:
            return origin_url
        publishers = self.__browser.find_elements_by_class_name('publisher')
        global timestamp
        global user_url
        global user_name
        for publisher in publishers:
            origin = publisher.find_elements_by_tag_name('a')
            if not origin:
                continue
            origin = origin[0]
            # 获取微博原文网址
            origin_url = origin.get_property('href')
            # 获取微博发布时间
            timestamp = publisher.text # 被举报微博 发布时间：2019-03-28 19:20:22 | 原文
            timestamp = re.findall('20.*\s\d\d:\d\d:\d\d', timestamp)  #注意用findall
            timestamp = timestamp[0]  # 只保留 2019-03-28 19:20:22
        # 获取用户id,用户名
        user = self.__browser.find_element_by_class_name('W_main_half_r')

        user = user.find_element_by_css_selector('a')
        user_url = user.get_attribute('href')
        user_name = user.text
        return origin_url

    def spider_start(self, start_page=1, end_page=5):
        for i in range(start_page, end_page + 1):
            base_url = 'http://service.account.weibo.com/?type=5&status=4&page={0}'.format(str(i))
            self.__browser.get(base_url)
            # 获取列表页中详情页网址，每页20条
            # print(i)
            detail_page_url_list = self.get_detail_page_url_list()
            # print(len(detail_page_url_list))
            j = 0
            for detail_page_url in detail_page_url_list:
                # print(detail_page_url)
                j = j+1
                # if j < 16: continue
                self.__browser.get(detail_page_url)
                triple = self.get_origin_weibo_url()
                if not triple:
                    continue
                origin_weibo_url = self.get_origin_weibo_url()
                self.__browser.get(origin_weibo_url)
                # 等待页面加载时间
                time.sleep(15)
                model:data_model.Weibo = self.get_weibo_detail_page_content()
                if not model:
                    continue
                model.weibo_url = origin_weibo_url
                model.timestamp = timestamp
                model.user_url = user_url
                model.user_name = user_name
                print(j)  #只打印采集到的
                self.__db_session.db_writer(model)
            print('完成第{0}页'.format(str(i)))