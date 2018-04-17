import requests
import json
import os
from multiprocessing import Pool
from multiprocessing import cpu_count

def downloadProvinceData(url, file_path):
    content = requests.get(url).content.decode("utf-8")
    items = json.loads(content)
    items.sort(key=lambda x: x["areacode"])
    with open(file_path, "w+") as fp:
        i = 1;
        for item in items:
            fp.write("%d,%s,%s,%s\n" % (i, item["areacode"].encode("utf8"), item["areaname"].encode("utf8"), item["position"].encode("utf8")))
            i=i+1;
    return items

def downloadProvinceCityData(url, file_path):
    result = []
    content = requests.get(url).content.decode("utf-8")
    items = json.loads(content)
    items.sort(key=lambda x: x["areacode"])
    with open(file_path, "a+") as fp:
        for item in items:
            result.append(item)
            position = ''
            if item["position"]:
                position = item["position"]
            fp.write("%s,%s,%s,%s\n" % (item["areacode"].encode("utf8"), item["areaname"].encode("utf8"), item["parentcode"].encode("utf8"), position.encode("utf8")))
    return result

def downloadBankData(url, file_path):
    result = []
    content = requests.get(url).content.decode("utf-8")
    items = json.loads(content)
    items.sort(key=lambda x: x["clscode"])
    with open(file_path, "w+") as fp:
        for item in items:
            if cmp(item["clscode"],"313491099996") != 0 and cmp(item["clscode"],"102") != 0:
                result.append(item)
                fp.write("%s,%s,%s\n" % (item["clscode"].encode("utf8")[0:3], item["clscode"].encode("utf8"), item["bankname"].encode("utf8")))
    return result

def downloadBankBranch(url, file_path):
    pid = os.getpid()
    content = requests.get(url).content.decode("utf-8")
    items = json.loads(content)
    items.sort(key=lambda x: x["bank_code"])
    print('download -> pid:(%d) url:(%s) len:(%d) done...' % (pid, url, len(items)))
    with open(file_path, "w+") as fp:
        for item in items:
            effectDate = ''
            if item["EFFDATE"]:
                effectDate = item["EFFDATE"]
            fp.write("%s,%s,%s,%s,%s,%s,%s\n" % (
            item["cls_code"].encode("utf8"), item["drec_code"].encode("utf8"),
            item["city_code"].encode("utf8"), item["bank_code"].encode("utf8"), item["lname"].encode("utf8"),
            item["tel"].encode("utf8"), effectDate.encode("utf8")))
                
if __name__ == '__main__':
    root_path = "./assets"
    if not os.path.exists(root_path):
        os.makedirs(root_path)

    # province
    province_url = 'http://www.zybank.com.cn/eportal/ui?moduleId=0e014749013b439aab3f22c794bd61ea&struts.portlet.action=/portlet/cnaps-front!queryAreaInfo.action'
    province_file_path = root_path + "/province.txt"
    province_items = downloadProvinceData(province_url, province_file_path);
    
    # city
    city_items = []
    city_url = 'http://www.zybank.com.cn/eportal/ui?moduleId=0e014749013b439aab3f22c794bd61ea&struts.portlet.action=/portlet/cnaps-front!queryAreaInfo.action&parentcode=%s'
    city_file_path = root_path + "/city.txt"
    if os.path.exists(city_file_path):
        os.remove(city_file_path)
    for province_item in province_items:
        url = city_url % (province_item["areacode"])
        city_items = city_items + downloadProvinceCityData(url, city_file_path)
	
    bank_url = 'http://www.zybank.com.cn/eportal/ui?moduleId=0e014749013b439aab3f22c794bd61ea&struts.portlet.action=/portlet/cnaps-front!queryBankNames.action'
    bank_file_path = root_path + "/bank.txt"
    bank_items = downloadBankData(bank_url, bank_file_path)

    p = Pool(processes=cpu_count()*2)
    base_bank_branch_url = 'http://www.zybank.com.cn/eportal/ui?moduleId=0e014749013b439aab3f22c794bd61ea&struts.portlet.action=/portlet/cnaps-front!queryCnaps.action&areacode=%s&clscode=%s'
    for bank_item in bank_items:
        bank_branch_base_path = root_path + "/bank/" + bank_item["clscode"][0:3]
        if not os.path.exists(bank_branch_base_path):
            os.makedirs(bank_branch_base_path)
        for city_item in city_items:
            url = base_bank_branch_url%(city_item["areacode"].encode("utf8"), bank_item["clscode"][0:3])
            p.apply_async(downloadBankBranch, args=(url, bank_branch_base_path + "/" + city_item["areacode"] + ".txt"))
    print('Waiting for all subprocesses done...')
    p.close()
    p.join()
    print('All subprocesses done.')
