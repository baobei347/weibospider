import weibo_spider
import test

# # 爬虫起始网站（微博社区管理中心-不实信息-结果公示）
spider=weibo_spider.WeiboSpider(login_url='http://service.account.weibo.com/?type=5&status=4')
# # # 抓取页面
spider.spider_start(start_page=1851,end_page=1868)

# #测试 爬虫起始网站
# spider = test.WeiboSpider(login_url='http://service.account.weibo.com/?type=5&status=0')
# #测试 抓取页面
# spider.spider_start(start_page=1,end_page=1)
