import os
import re
import json
import requests
header = {'User-agent': 'Googlebot'} #构造请求头

def fetch_text(doc_id, title, doc_type): #获取文档的文字内容
    abstract_url = 'https://wenku.baidu.com/api/doc/getdocinfo?callback=cb&doc_id=' + doc_id #构造摘要地址
    abstract = requests.get(abstract_url, headers =header, timeout =30) #获取文档摘要信息，包括md5码，总页数，rsign等
    md5 = re.findall(r'"md5sum":"(.*?)"', abstract.text)[0] #md5
    pn = re.findall(r'"totalPageNum":"(.*?)"', abstract.text)[0] #页码
    rsign = re.findall(r'"rsign":"(.*?)"', abstract.text)[0] #rsign
    content_url = 'https://wkretype.bdimg.com/retype/text/' + doc_id + '?rn=' + pn + '&type=txt' + md5 + '&rsign=' + rsign #构造文档内容的地址
    content = requests.get(content_url, headers = header, timeout =30) #对文档内容请求
    page_contents = json.loads(content.text) #所有页的内容形成一个list
    doc_path = r"D:\项目\百度文库下载与文本解析\doc"+ os.sep + title + ".doc" #选择要保存的本地doc文件名
    with open(doc_path, mode = 'w+', encoding ='utf-8') as file:  #打开文件
        for page_content in page_contents: #每一页循环
            lines = page_content['parags'][0]["c"].replace('\r','').replace('\\n','') #每一页的文字内容是一个整体
            file.write(lines) #写入doc文档
    file.close() #关闭doc
    print("文本素材保存完毕")

def fetch_image(url, doc_id, title, doc_type):#获同篇文档里面的图片素材
    image_path = r"D:\项目\百度文库下载与文本解析\image"+os.sep+title #保存图片的路径
    if not os.path.exists(image_path): #创建同名文件夹保存图片
        os.mkdir(image_path)
    resource = requests.get(url).content.decode('utf-8', 'ignore')
    image_urls = re.findall(r'(https:\\\\/\\\\/wkbjcloudbos.bdimg.com.+?0.png.+?\\")', resource) #正则图片素材地址
    #print(len(image_urls))
    for idx, image_url in enumerate(image_urls):
        image_url = image_url.replace("\\", "").replace('\"', "")
        if len(image_url)< 650:
            img = requests.get(image_url, headers = header, timeout =30).content
            with open(image_path+os.sep+str(idx)+".png", "wb") as f:
                f.write(img)
            f.close()
    print("图片素材保存完毕")

def downloadWenku(url): #进入文档地址获取文档基础信息，包括文档id，文档标题，文档类型
    html = requests.get(url, headers = header, timeout = 30)
    html.raise_for_status()
    html.encoding = 'gbk'
    doc_id = re.findall(r"docId.*?:.*?\'(.*?)\'\,", html.text)[0] #docid
    title = re.findall(r"title.*?\:.*?\'(.*?)\'\,", html.text)[0] #文档标题
    doc_type = re.findall(r"docType.*?\:.*?\'(.*?)\'\,", html.text)[0] #文档类型
    #print(doc_id, title, doc_type, doc_type)
    fetch_text(doc_id, title, doc_type) #调用下载文字函数
    fetch_image(url, doc_id, title, doc_type) #调用下载图片函数

if __name__ =="__main__":
    url = input("\n请输入文档的地址, 回车键确认:")
    downloadWenku(url)