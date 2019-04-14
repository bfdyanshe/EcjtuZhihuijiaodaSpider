import http.cookiejar
import urllib.request
import requests
from bs4 import BeautifulSoup
import re
import time
import os
Headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:66.0) Gecko/20100101 Firefox/66.0','Connection':'keep-alive'}

def loginInfo():
    try:
        f=open("logindata.data",'r')
        info=[]
        for a in f.readlines():
            info.append(a.rstrip('\n'))
        f.close()
        if info.__len__()<1:
            info.append(str(input("输入学号：")))
            info.append(str(input("输入密码：")))
            f=open("logindata.data",'w')
            f.write("\n".join(info))
            f.close()
    except:
        info=[]
        info.append(str(input("输入学号：")))
        info.append(str(input("输入密码：")))
        f=open("logindata.data",'w')
        f.write("\n".join(info))
        f.close()
    url="http://cas.ecjtu.edu.cn/cas/loginPasswdEnc"
    values={'pwd':info[1]}
    data=urllib.parse.urlencode(values).encode()
    try:
        response=urllib.request.urlopen(url,data)
        encodePasswd=str(response.read())
        encodePasswd=re.findall(r":\"(.+?)\"\}",encodePasswd)
        newpasswd=encodePasswd[0]
    except urllib.error.URLError as e:
        print(e.reason)
    if(newpasswd.__len__()>20):
        info[1]=newpasswd
    return info

class user:
    def __init__(self,info):
        self.id=info[0]
        self.passwd=info[1]
        self.cookie=http.cookiejar.CookieJar()
        self.handler=urllib.request.HTTPCookieProcessor(self.cookie)
        self.opener=urllib.request.build_opener(self.handler)

    def LoginData(self):
        lturl='http://cas.ecjtu.edu.cn/cas/login?service=http%3A%2F%2Fportal.ecjtu.edu.cn%2Fdcp%2Findex.jsp'
        requestLt=urllib.request.Request(lturl,headers=Headers)
        try:
            responseLt=self.opener.open(requestLt)
            html=responseLt.read()
            html=BeautifulSoup(html,"html5lib")
            inputlt=html.find("input",attrs={"name":"lt"})
            self.lt=inputlt.get(key="value")
        except urllib.error.URLError as e:
            print(e.reason)
        self.data={
            "encodeService":"http%253a%252f%252fportal.ecjtu.edu.cn%252fdcp%252findex.jsp",
            "service":"http%3A%2F%2Fportal.ecjtu.edu.cn%2Fdcp%2Findex.jsp",
            "serviceName":"null",
            "loginErrCnt":"0",
            "username":self.id,
            "password":self.passwd,
            "lt":self.lt,
            "autoUser":"on",
            "autoLogin":"on"
        }

    def Login(self):
        self.LoginData()
        loginUrl='http://cas.ecjtu.edu.cn/cas/login'
        logindata=urllib.parse.urlencode(self.data).encode()
        postLogin=urllib.request.Request(loginUrl,logindata,Headers)
        try:
            responseLogin=self.opener.open(postLogin)
            html=str(responseLogin.read())
            html=BeautifulSoup(html,"html5lib")
            yesorno=html.find("noscript")
            if yesorno==None:
                print("登录失败，请检查账号，密码..")
                os.remove('logindata.data')
            else :
                print("登录成功..")
        except urllib.error.URLError as e:
            print(e.reason)

#返回一个二维数组，其中每一个二级数组是每一天的课程
    def Schedule(self):
        posturl="http://portal.ecjtu.edu.cn:8080/form/allSv/allSv.action"
        loginActionUrl="http://jwxt.ecjtu.jx.cn/stuMag/Login_dcpLogin.action"
        jwcPost1=urllib.request.Request(posturl,headers=Headers)
        jwcLogin=urllib.request.Request(loginActionUrl,headers=Headers)
        try:
            post1=self.opener.open(jwcPost1)
            getread=post1.read()
            post1html=BeautifulSoup(getread,"html5lib")
            href=post1html.find("a").get(key="href")
            jwcPost1=urllib.request.Request(href,headers=Headers)
            jwcPost1=self.opener.open(jwcPost1)
            try:
                jwcLoginRes=self.opener.open(jwcLogin)
                getread=jwcLoginRes.read()
                getread=BeautifulSoup(getread,"html5lib")
                jumphref=getread.find("a").get(key="href")
                jump=urllib.request.Request(jumphref,headers=Headers)
                jumpRes=self.opener.open(jump)
                getread=jumpRes.read()
                cdata=urllib.request.Request("http://jwxt.ecjtu.jx.cn/Schedule/Schedule_getUserSchedume.action",headers=Headers)
                cdataRes=self.opener.open(cdata)
                getread=cdataRes.read()
                schHtml=BeautifulSoup(getread,"html5lib")
                table=schHtml.find("table",attrs={"id":"courseSche"})
                table=BeautifulSoup(str(table),"html5lib")
                trList=table.find_all("tr")
                tdList=[]
                allClass=[]
                for a in trList:
                    tdList.append(a.find_all("td"))
                count=0
                for a in range(8):
                    allClass.append([])
                for a in tdList:
                    for b in a:
                        allClass[count].append(b.get_text())
                        count=(count+1)%8
                return allClass
            except urllib.error.URLError as e:
                print(e.reason)
        except urllib.error.URLError as e:
            print(e.reason)

        
    def PrintCookies(self):
        for a in self.cookie:
            print(a)


auser=user(loginInfo())
auser.Login()
print(auser.Schedule())