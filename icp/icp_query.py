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


def zhanzhang_test():
    global xlsx_num
    wb = openpyxl.load_workbook("wordpress.xlsx")
    sheet = wb['问题隐患填写模板']
    max_row = sheet.max_row - xlsx_num
    flag_num = 1
    proxies = {}
    for i in range(0,100000):
        xlsx_num += 1
        try:
            domain_name = sheet[f"J{xlsx_num}"].value
            print(domain_name)
            tld = tldextract.extract(domain_name)
            main_domain = tld.domain + '.' + tld.suffix
            print(f"爬取第{xlsx_num-2}条,:{main_domain}")
            rp = requests.get(f"https://icp.chinaz.com/{main_domain}", timeout=15, verify=False,proxies=proxies)
            #time.sleep(5)
            content = rp.text
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
                rp = requests.get(companyHref, timeout=15,
                                  verify=False,proxies=proxies)
                
                content = rp.text
                #print(content)
                parse_html = etree.HTML(content)
                second_companyName = parse_html.xpath('/html/body/div[2]/div[2]/div/ul[2]/li[2]/a/span/text()')
                second_companyHref = "https://data.chinaz.com"+parse_html.xpath('/html/body/div[2]/div[2]/div/ul[2]/li[2]/a/@href')[0]
                if companyName == second_companyName:
                    print(second_companyHref)
                    #time.sleep(15)
                    time.sleep(2)
                    rp = requests.get(second_companyHref, timeout=15,
                                      verify=False,proxies=proxies)
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
            #traceback.print_exc()
            #print("异常：",e)


if __name__ == "__main__":
    zhanzhang_test()
