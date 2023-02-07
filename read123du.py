from urllib3.contrib.socks import SOCKSProxyManager
from bs4 import BeautifulSoup
import js2py
import re
import json
import time

def download_content(url, cookie):
    #使用代理
    proxy_addr = 'socks5://127.0.0.1:7890'
    proxy = SOCKSProxyManager(proxy_addr)
    #使用代理下载数据
    response = proxy.request('GET', url, headers = cookie)
    #判断是否为200
    while(response.status != 200):
        response = proxy.request('GET', url, headers = cookie)
    return response


# 第二个函数，将字符串内容保存到文件中
# 第一个参数为所要保存的文件名，第二个参数为要保存的字符串内容的变量
def save_to_file(filename, content):
    fo = open(filename, "w", encoding="utf-8")
    fo.write(content)
    fo.close()

def process_html_123du_title(content):
    #123du
    soup = BeautifulSoup(content, 'html.parser')
    div_main = soup.body.find_all('div', "DivMain")
    div_main = div_main[0].find_all('div', "DivMainLeft")
    div_main = div_main[0].find_all('div', id="DivContentBG")
    div_main = div_main[0]
    title = div_main.find('h1')
    return title

def process_html_123du_body(content):
    #123du
    soup = BeautifulSoup(content, 'html.parser')
    div_main = soup.body.find_all('div', "DivMain")
    div_main = div_main[0].find_all('div', "DivMainLeft")
    div_main = div_main[0].find_all('div', id="DivContentBG")
    div_main = div_main[0]
    title = div_main.find('h1')
    body_list = div_main.find_all('div')
    for body_item in body_list:
        id_key = body_item.attrs.get('id')
        if ((id_key != None) & (id_key != 'PageSet')):
            body = body_item
    return body

def process_html_123du_next_page(content):
    #123du
    soup = BeautifulSoup(content, 'html.parser')
    div_main = soup.body.find_all('div', "DivMain")
    div_main = div_main[0].find_all('div', "DivMainLeft")
    div_main = div_main[0].find_all('div', id="DivContentBG")
    div_main = div_main[0]
    next_page = div_main.find('script', language="javascript")
    next_page = next_page.text
    next_page = re.search(r'\r\n\t\t\t\tlocation=(.*).html', next_page)
    return next_page.group(0)[16:]

class Read123du:
    website_url = "https://www.123duw.com"
    book_url = "https://www.123duw.com/dudu-33/3250866/"
    section_id = "51981514.html"
    cookie = {'cookie':''}
    soup = None

    whole_text = ""

    def __init__(self, book_url, section_id):
        self.book_url = book_url
        self.section_id = section_id
        self.cookie = {'cookie':''}

    def setCookie(self):
        #get js & var
        response = download_content(self.book_url+self.section_id, self.cookie)
        response_header = response.headers
        response_header_cookie = response_header.get('Set-Cookie')
        self.cookie = {'cookie': response_header_cookie}
        content = response.data
        content = content.decode('gbk')
        soup = BeautifulSoup(content, 'html.parser')
        script_tags = soup.find_all('script')
        var_c2 = script_tags[0].text
        var_c2 = var_c2[8:-2]
        js_url = script_tags[1]['src']
        # get js content
        js_content = download_content(self.website_url+js_url, self.cookie)
        js_content = js_content.data[270:-237]
        js_content = js_content.decode('utf8')
        js_content = js_content + "ajax(\"" + var_c2 + "\");"
        # get decoder key url
        key_url = js2py.eval_js(js_content)
        key_response = download_content(self.website_url+key_url, self.cookie)
        self.cookie['cookie'] = key_response.headers.get('Set-Cookie')

    def getNextSectionId(self):
        response = download_content(self.book_url+self.section_id, self.cookie)
        content = response.data
        content = content.decode('gbk')
        self.soup = BeautifulSoup(content, 'html.parser')
        div_main = self.soup.body.find_all('div', "DivMain")
        div_main = div_main[0].find_all('div', "DivMainLeft")
        div_main = div_main[0].find_all('div', id="DivContentBG")
        div_main = div_main[0]
        next_page = div_main.find('script', language="javascript")
        next_page = next_page.text
        next_page = re.search(r'\r\n\t\t\t\tlocation=(.*).html', next_page)
        if (next_page != None):
            return next_page.group(0)[16:]
        else:
            return None

    def getSectionTitle(self):
        div_main = self.soup.body.find_all('div', "DivMain")
        div_main = div_main[0].find_all('div', "DivMainLeft")
        div_main = div_main[0].find_all('div', id="DivContentBG")
        div_main = div_main[0]
        title = div_main.find('h1')
        return title

    def getSectionData(self):
        div_main = self.soup.body.find_all('div', "DivMain")
        div_main = div_main[0].find_all('div', "DivMainLeft")
        div_main = div_main[0].find_all('div', id="DivContentBG")
        div_main = div_main[0]
        title = div_main.find('h1')
        body_list = div_main.find_all('div')
        for body_item in body_list:
            id_key = body_item.attrs.get('id')
            if ((id_key != None) & (id_key != 'PageSet')):
                body = body_item
        return body

    def getSectionIdLoop(self):
        next_id = self.getNextSectionId()
        self.whole_text = self.whole_text + str(self.getSectionTitle())
        self.whole_text = self.whole_text + str(self.getSectionData())
        print("正在处理：", self.getSectionTitle())
        while (next_id != None):
            self.section_id = next_id
            if ("-" in next_id):
                next_id = self.getNextSectionId()
                self.whole_text = self.whole_text + str(self.getSectionData())
            else:
                # set cookie
                self.setCookie()
                next_id = self.getNextSectionId()
                self.whole_text = self.whole_text + str(self.getSectionTitle())
                self.whole_text = self.whole_text + str(self.getSectionData())
                print("-------------------------------------------------------")
                print("正在处理：", self.getSectionTitle())



def main():
    # 下载网页
    section_url = "https://www.123duw.com/dudu-33/3250866/"
    section_id = "51981514.html"
    Read123du_inst = Read123du(section_url, section_id)
    Read123du_inst.setCookie()
    Read123du_inst.getSectionIdLoop()
    #param_start = 6
    #param_end = 516
    #whole_book_data = ""
    #for param in range(param_start,param_end):
    #    print("Start ------------------", param-5)
    #    url = const_url+str(param)+".html"
    #    result = download_content(url)
    #    processed_result = process_html(result)
    #    whole_book_data = whole_book_data + processed_result
    
    save_to_file("光阴之外1-501.html", Read123du_inst.whole_text)

if __name__ == '__main__':
    main()
