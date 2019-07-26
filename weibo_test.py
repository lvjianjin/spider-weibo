# -*- coding: utf-8 -*-
"""
Created on Fri Jul 12 09:41:11 2019

@author: Administrator
"""

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import pymysql
import random
import time
import bs4
import re

num = 0
conn = pymysql.connect(
                       host="192.168.1.172",
                       user="wxx",
                       password="123456",
                       database="test",
                       charset="utf8"
                       )
# 得到一个可以执行SQL语句的光标对象
cur = conn.cursor()

def sql_insert(table,column_name,value):
    #数据入库语句
    if len(column_name) != len(value):
        sql = ''
    else:
        kkk = "'%s'," * len(column_name)
        sql = 'INSERT INTO ' + table + ' (' + ','.join(column_name) + ') VALUES (' + kkk[:-1] + ')'
        sql = sql %(tuple(value))
    return sql

while 1:
    print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())))
    err = 0
    error = '无'
    while 1:
        try:
            driver = webdriver.PhantomJS()   # 无头浏览器
            #driver = webdriver.Firefox()   # Firefox浏览器
            driver.set_window_size(1920,1080)
            driver.set_page_load_timeout(10)
            driver.set_script_timeout(10)
            driver.get('https://www.sina.com.cn/') # 打开网页
            time.sleep(random.uniform(8,10))
            #for handle in driver.window_handles:
            #    driver.switch_to_window(handle)
            mouse = driver.find_element_by_link_text("登录")
            print(1)
            ActionChains(driver).move_to_element(mouse).perform()
            driver.find_element_by_xpath('''//*[@name="loginname"]''').send_keys('你的微博用户名')
            time.sleep(random.uniform(8,10))
            driver.find_element_by_xpath('''//*[@name="password"]''').send_keys('你的微博密码')
            print(2)
            time.sleep(random.uniform(8,10))
            driver.find_element_by_xpath('''//*[@class="login_btn"]''').click()
            time.sleep(random.uniform(8,10))
            print(3)
            driver.find_element_by_xpath('''//*[@suda-uatrack="key=index_new_menu&value=weibo_click"]''').click()
            print(4)
            time.sleep(random.uniform(8,10))
            #for handle in driver.window_handles:
            #    driver.switch_to_window(handle)
            #listCookies = driver.get_cookies()
            driver.switch_to_window(driver.window_handles[1])
            print(5)
            time.sleep(random.uniform(8,10))
            break
        except:
            print('打开网页出错，请检查！')
            try:
                driver.quit()
            except:
                pass
            time.sleep(10)

    try:
        while 1:
            driver.find_element_by_xpath('''//*[@suda-data="key=tblog_home_tab&value=all"]''').click()
            time.sleep(random.uniform(5,8))
            html = str(driver.page_source)
            #driver.quit()
            soup = bs4.BeautifulSoup(html)
            block = soup.select('div[action-type="feed_list_item"]')
            
            for cat in block:
                #微博id
                name = cat.select('div[class="WB_info"]>a')[0].text.replace(' ','').replace('\n','')
                #微博id
                u_id = re.compile(r'id=(.*?)&refer').findall(cat.select('div[class="WB_info"]>a')[0]['usercard'])[0]
                #微博头像
                img = cat.select('div[class="face"]>a>img')[0]['src']
                #时间
                p_time = cat.select('div[class="WB_from S_txt2"]>a')[0].text
                if '刚刚' in p_time:
                    f_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                elif '秒前' in p_time:
                    f_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - int(re.sub("\D", "", p_time)))) 
                elif '分钟前' in p_time:
                    f_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - 60*int(re.sub("\D", "", p_time)))) 
                elif '小时前' in p_time:
                    f_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - 60*60*int(re.sub("\D", "", p_time))))
                elif '推荐' in p_time:
                    f_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                elif '今天' in p_time:
                    f_time = time.strftime("%Y-%m-%d", time.localtime(time.time())) + p_time.replace('今天','') + ':00'
                else:
                    f_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
                #来源
                try:
                    if ':' not in cat.select('div[class="WB_from S_txt2"]>a')[1].text.replace(' ','').replace('来自',''):
                        f_from = cat.select('div[class="WB_from S_txt2"]>a')[1].text.replace(' ','').replace('来自','')
                    else:
                        f_from = ''
                except:
                    f_from = ''
                #内容
                content = cat.select('div[class="WB_text W_f14"]')[0].text
                #图片
                try:
                    pic = '||'.join([key['src'] for key in cat.select('ul[class="WB_media_a WB_media_a_mn WB_media_a_m9 clearfix"]>li>img')])
                except:
                    pic = ''
                #转发、评论、点赞
                try:
                    dog = cat.select('a[class="S_txt2"]>span>span>span>em')
                    report = dog[3].text.replace(' ','').replace('\n','').replace('转发','') #转发
                    comments = dog[5].text.replace(' ','').replace('\n','').replace('评论','')#评论
                    excellent = dog[7].text.replace(' ','').replace('\n','').replace('赞','')#点赞
                except:
                    report = '0'
                    comments = '0'
                    excellent = '0'
                
                sql = sql_insert(
                    'weibo',
                    ['name','img','f_time','f_from','content','pic','report','comments','excellent','u_id'],
                    [name,img,f_time,f_from,content,pic,report,comments,excellent,u_id]
                    )
                try:
                    cur.execute(sql)
                    conn.commit()
                    num = num + 1
                except:
                    conn.rollback()
                    err = err + 1
                #    except:
                #        error = '爬取出错。'
                #爬取情况
            b_sql = sql_insert(
                'b_weibo',
                ['time','num','error'],
                [time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time())),str(num),error]
                )
            try:
                cur.execute(b_sql)
                conn.commit()
            except:
                conn.rollback()
            print('共计导入数据：' + str(num) + '条；错误信息：' + error)
            time.sleep(5*60)
    except:
        print('页面刷新失败。')
        try:
            driver.quit()
        except:
            pass
conn.close()
