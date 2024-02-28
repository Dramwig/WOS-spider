# -*- coding: utf-8 -*-

"""
File: WOS_spider.py
Author: Dramwig
Email: dramwig@outlook.com
Date: 2024-02-27
Version: 1.3

Description: This script uses Selenium and BeautifulSoup to scrape detailed paper information from Web of Science (WOS) website.
It navigates through each paper's detail page, extracts key information such as title, citation count, country, journal, etc., 
and saves the collected data into a CSV file.

Please note that this script is intended for educational purposes only, and you should abide by the terms of service and usage policies 
of the Web of Science when using it or any derivative work.

"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from bs4 import BeautifulSoup
import pandas as pd
import time

# 解析html
def parse_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    
    # 创建一个空的字典
    data_dict = {}
    
    try:
        containers = soup.find_all('div', class_='cdx-two-column-grid-container')
        for container in containers:
            # 在这个容器内找到所有的标签和数据
            labels = container.find_all(class_='cdx-grid-label')
            datas = container.find_all(class_='cdx-grid-data')
            label = labels[0].text.strip()
            data_texts = [data.text.strip() for data in datas] # 提取数据列表中的文本
            text = '\n'.join(data_texts) # 将文本连接成一个字符串，使用换行符分隔
            
            # 存储到字典中
            data_dict[label] = text
    except:
        print(f"解析容器失败")
    
    try:
        class_title = soup.find(class_="title text--large cdx-title")
        data_dict['title'] = class_title.text.strip()
    except:
        print("获取标题失败")

    try:
        class_citation = soup.find(class_="mat-tooltip-trigger medium-link-number link ng-star-inserted")
        data_dict['citation'] = class_citation.text.strip()
    except:
        data_dict['citation'] = '0'

    try:
        class_addresses = soup.find('span', class_='ng-star-inserted', id='FRAOrgTa-RepAddressFull-0')
        print(class_addresses.text.strip())
        data_dict['country'] = class_addresses.text.split(',')[-1].strip()
    except:
        print("获取国家失败")
    
    try:
        class_journal = soup.find(class_="mat-focus-indicator mat-tooltip-trigger font-size-14 summary-source-title-link remove-space no-left-padding mat-button mat-button-base mat-primary font-size-16 ng-star-inserted")
        data_dict['journal'] = class_journal.text.strip()
    except:
        print("获取期刊失败")
    
    try:
        input_box = soup.find(class_='wos-input-underline page-box')  # 获取包含输入框的标签
        index = int(input_box['aria-label'].split()[-1].replace(",", ""))
    except:
        print("获取页码失败")
        
    return index, data_dict    
        

if __name__ == "__main__": 
    # 0000391627
    # adolescent depression 1: https://webofscience-clarivate-cn-s.era.lib.swjtu.edu.cn/wos/alldb/full-record/WOS:000653016400005 
    url_root = 'https://webofscience-clarivate-cn-s.era.lib.swjtu.edu.cn/wos/alldb/basic-search'
    papers_need = 100000
    file_path = 'result.csv'    
    wait_time = 30
    pause_time = 4
    
    # 变量
    xpath_nextpaper = '/html/body/app-wos/main/div/div/div[2]/div/div/div[2]/app-input-route/app-full-record-home/div[1]/app-page-controls/div/form/div/button[2]'
    df = pd.DataFrame()
    index = 0
    
    # 读取df
    ifread = input("是否读取已有的CSV文件？(y/n)")
    if ifread == 'y':
        df = pd.read_csv(file_path, index_col=0)
        index = int(df.index[-1].split('_')[-1])
        print(f"读取已有的CSV文件，当前行索引为{index},即第{index+1}篇论文")
    
    # 打开的页面
    driver = webdriver.Chrome()
    driver.get(url_root)
    
    # 手动操作，比如切换标签页等
    input("请手动操作至论文详情页面,完成后按Enter键继续...")
    
    # 获取获取当前所有窗口的句柄
    window_handles = driver.window_handles
    
    # 假设新窗口是最后被打开的
    new_window_handle = window_handles[-1]

    # 切换到新窗口
    driver.switch_to.window(new_window_handle)

    # 在新窗口上进行操作，例如获取新窗口的标题
    print("新窗口的标题(请确保页面正确):", driver.title)

    while index <= papers_need:
        print("正在处理第", index+1, "篇论文")
        
        # 等待页面加载
        time.sleep(pause_time/2)
        
        try:
            # 或者等待直到某个元素可见
            element = WebDriverWait(driver, wait_time).until(
                EC.visibility_of_element_located((By.XPATH, '//*[@id="FRAOrgTa-RepAddressFull-0"]'))
            )
        except Exception as e:
            print("An error occurred:", e)
            print("等待超时，可能是页面加载失败")

        time.sleep(pause_time/2)
                
        # 使用Selenium获取页面的HTML源码
        html = driver.page_source
        
        # 解析HTML
        try:
            index,data = parse_html(html)
            row_index = f'Row_{index}'
            if row_index in df.index:
                df.loc[row_index] = pd.Series(data, name=row_index) # 如果行索引存在，则覆盖对应行的数据
            else:
                df = df._append(pd.Series(data, name=row_index)) # 如果行索引不存在，则追加新的行
            df.to_csv(file_path, index=True)  # 将DataFrame保存为CSV文件,保留行索引作为第一列

            # debug
            # input("完成后按Enter键继续...")
        
            # 切换到下一页
            WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath_nextpaper))).click()
        except Exception as e:
            print("An error occurred:", e)
            input("网页出现问题等待手动解决...")
        

    # 关闭浏览器
    driver.quit()
    
