import sys
import traceback
import threading
import tldextract
import base64
import time
import requests
from requests.exceptions import ReadTimeout,HTTPError,RequestException
from datetime import datetime, timedelta
import openpyxl
from colorama import Fore
import urllib3
import lxml
from lxml import etree
import socket
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


xls_num = 0
xlsx_num = 2
domains = []
lock = threading.Lock()

def get_ip_address(domain):
    return socket.gethostbyname(domain)

def get_company_address(address):
    gaode_key = 'cef12df1867a06d82f2deaff921a3611'
    try:
        lonlat_resp = requests.get(
            f'https://restapi.amap.com/v3/geocode/geo?key={gaode_key}&address={address}&output=json',
            verify=False).json()
        if lonlat_resp["status"] == 0:
            return {"status": "fail"}
        from_which_province = lonlat_resp['geocodes'][0]['province']
        from_which_city = lonlat_resp['geocodes'][0]['city']
        from_which_district = lonlat_resp['geocodes'][0]['district']
        if from_which_province == from_which_city:
            if from_which_province == "上海市":
                from_which_city = from_which_district
                from_which_district = ""
            if from_which_province == "北京市":
                from_which_city = from_which_district
                from_which_district = ""
            if from_which_province == "天津市":
                from_which_city = from_which_district
                from_which_district = ""
            if from_which_province == "重庆市":
                from_which_city = from_which_district
                from_which_district = ""
        return {"status": "success", "from_which_province": from_which_province, "from_which_city": from_which_city,
                "from_which_district": from_which_district}
    except Exception as e:
        return {"status": "fail"}

burp0_cookies = {"speedworldhost": "uyislam.com", "Hm_lvt_aecc9715b0f5d5f7f34fba48a3c511d6": "1716186294", "auth-token": "undefined", "user-temp": "4affdfcb-496e-1601-76ad-b777bcbdc602", "toolbox_urls": "www.gamer520.com|api.sshttp.cn|221.206.194.54|jd.com|139.9.122.19|https%3a%2f%2fuyislam.com|www.at0086.com|www.temamotor.com|www.qdahgc.com|www.zhixuantj.com", "pinghost": "www.gamer520.com", "qHistory": "aHR0cDovL3Rvb2wuY2hpbmF6LmNvbV/nq5nplb/lt6Xlhbd8aHR0cDovL2lwLmNoaW5hei5jb20vaXBiYXRjaC9fSVDmibnph4/mn6Xor6J8Ly9pcC50b29sLmNoaW5hei5jb20vX0lQ5p+l6K+ifC8vaWNwLmNoaW5hei5jb20vX+e9keermeWkh+ahiOafpeivog==", "ucvalidate": "129d3a5c-7bb9-94dd-88d9-27e078ab97a9", "cz_statistics_visitor": "fd0a2ea3-23b0-eafd-3025-36adb379e47b", "Hm_lvt_ca96c3507ee04e182fb6d097cb2a1a4c": "1720418560,1720485596,1720659463,1720746407", "HMACCOUNT": "735F56C6DE938459", "Hm_lvt_32e161892d770dca4a9d436a5764a01a": "1720659463,1720746407", "Hm_lpvt_32e161892d770dca4a9d436a5764a01a": "1720746410", "JSESSIONID": "E8EB8F48814EF6C0B43DAD6FEEC2638E", "Hm_lpvt_ca96c3507ee04e182fb6d097cb2a1a4c": "1720746414"}
burp0_headers = {"Pragma": "no-cache", "Cache-Control": "no-cache", "Sec-Ch-Ua": "\"Not/A)Brand\";v=\"8\", \"Chromium\";v=\"126\", \"Google Chrome\";v=\"126\"", "Sec-Ch-Ua-Mobile": "?0", "Sec-Ch-Ua-Platform": "\"Windows\"", "Upgrade-Insecure-Requests": "1", "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36", "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7", "Sec-Fetch-Site": "same-origin", "Sec-Fetch-Mode": "navigate", "Sec-Fetch-User": "?1", "Sec-Fetch-Dest": "document", "Referer": "https://icp.chinaz.com/", "Accept-Encoding": "gzip, deflate", "Accept-Language": "zh-CN,zh;q=0.9", "Sec-Gpc": "1", "Priority": "u=0, i", "Connection": "close"}

def zhanzhang_test():
    global xlsx_num
    wb = openpyxl.load_workbook("wordpress.xlsx")
    sheet = wb['问题隐患填写模板']
    max_row = sheet.max_row - xlsx_num
    flag_num = 1
    for i in range(0,1000):
        xlsx_num += 1
        try:
            domain_name = sheet[f"J{xlsx_num}"].value
            print(domain_name)
            tld = tldextract.extract(domain_name)
            main_domain = tld.domain + '.' + tld.suffix
            print(f"爬取第{xlsx_num-2}条,:{main_domain}")
            rp = requests.get(f"https://icp.chinaz.com/{main_domain}", timeout=15,headers=burp0_headers, cookies=burp0_cookies,verify=False)
            #time.sleep(5)
            content = rp.text
            print(content)
            parse_html = etree.HTML(content)
            companyName = parse_html.xpath('//*[@id="companyName"]/text()')
            if len(companyName) == 0:
                continue
            companyHref = "https:"+parse_html.xpath('//*[@id="companyName"]/@href')[0]
            org = parse_html.xpath('/html/body/div[3]/div[2]/div/div[1]/div[2]/div/table/tbody/tr[1]/td[4]/text()')
            #address = parse_html.xpath('/html/body/div[3]/div[2]/div/div[2]/div[1]/div/div[2]/table/tbody/tr[5]/td[2]/div/text()')
            if org[0] =="企业":
                #time.sleep(10)
                time.sleep(2)
                rp = requests.get(companyHref, timeout=15,headers=burp0_headers, cookies=burp0_cookies,verify=False)
                
                content = rp.text
                #print(content)
                parse_html = etree.HTML(content)
                second_companyName = parse_html.xpath('/html/body/div[2]/div[2]/div/ul[2]/li[2]/a/span/text()')
                second_companyHref = "https://data.chinaz.com"+parse_html.xpath('/html/body/div[2]/div[2]/div/ul[2]/li[2]/a/@href')[0]
                if companyName == second_companyName:
                    print(second_companyHref)
                    #time.sleep(15)
                    time.sleep(2)
                    rp = requests.get(second_companyHref, timeout=15,headers=burp0_headers, cookies=burp0_cookies,verify=False)
                    #time.sleep(5)
                    content = rp.text
                    parse_html = etree.HTML(content)
                    unifiedCode = parse_html.xpath('/html/body/div[3]/div[4]/div[1]/table[1]/tbody/tr[4]/td[2]/text()')
                    address = parse_html.xpath('/html/body/div[3]/div[2]/div/div[2]/div/div[2]/text()')
                    print(address)
                    gca_rs = get_company_address(address[0])
                    if gca_rs.get("status") == "fail":
                        print("查公司的地址出错:{}".format(companyName))
                        continue
                    from_which_province = gca_rs["from_which_province"]
                    from_which_city = gca_rs["from_which_city"]
                    from_which_district = gca_rs["from_which_district"]
                    address = f"{from_which_province}/{from_which_city}/{from_which_district}"
                    print(unifiedCode)
                    print(companyName)
                    print(org)
                    print(address)
                    ip_address = get_ip_address(domain_name)
                    sheet[f"E{xlsx_num}"] = companyName[0]
                    sheet[f"F{xlsx_num}"] = unifiedCode[0]
                    sheet[f"G{xlsx_num}"] = address
                    sheet[f"I{xlsx_num}"] = ip_address
                    wb.save("wordpress.xlsx")
        except Exception as e:
            traceback.print_exc()
            print("异常：",e)


if __name__ == "__main__":
    zhanzhang_test()
