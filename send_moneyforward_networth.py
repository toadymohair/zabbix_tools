from selene.browsers import BrowserName
from selene.api import *
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import traceback
import subprocess
from subprocess import PIPE


USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'
START_URL = 'https://moneyforward.com/users/sign_in'
USER_DATA_DIR= '/home/ec2-user/cookies/moneyforward.com/'


ZABBIX_SERVER_HOST = "localhost"
ZABBIX_MONITOR_HOST = "MoneyForward"
ZABBIX_MONITOR_ITEM = "networth"

username = subprocess.run("get_login_username moneyforward.com", shell=True, stdout=PIPE, stderr=PIPE, text=True).stdout
password = subprocess.run("get_login_password moneyforward.com", shell=True, stdout=PIPE, stderr=PIPE, text=True).stdout

def get_networth():
    config.browser_name = BrowserName.CHROME
    chrome_option = webdriver.ChromeOptions()
    chrome_option.add_argument('--headless')
    chrome_option.add_argument('--no-sandbox')
    chrome_option.add_argument('--disable-gpu')
    chrome_option.add_argument('user-agent=' + USER_AGENT)
    chrome_option.add_argument('--user-data-dir=' + USER_DATA_DIR)
    driver = webdriver.Chrome(executable_path="/usr/bin/chromedriver", options=chrome_option)
    browser.set_driver(driver)

    # ログイン画面を開く
    browser.open_url(START_URL)

    # （ss でログインボタンのクラス指定でコレクション取得した結果がfalse (＝ログインボタンが存在しない）なら、ログイン済みと判断。
    if(ss('a[class="_2YH0UDm8 ssoLink"]')):

        # 「メールアドレスでログイン」ボタンをクリック（"_2YH0UDm8 ssoLink" クラスの一番上のボタン）
        s('a[class="_2YH0UDm8 ssoLink"]').click()

        # ユーザ名（メールアドレス）を入力し、submit
        s('input[name="mfid_user[email]"]').set_value(username)
        s('input[type="submit"]').click()

        # パスワードを入力し、submit -> ここまででログイン完了
        s('input[name="mfid_user[password]"]').set_value(password)
        s('input[type="submit"]').click()

    # 「...」 をクリック
    s('a[href="/analysis/monthly_reports/latest"]').click()

    # 「バランスシート」をクリック
    s('a[href="/bs/balance_sheet"]').click()

    #「純資産」欄のテキストを取得
    networth_text = s(by.xpath('//*[@id="bs-balance-sheet"]/section/section[2]/div/div[2]/section[2]/table/tbody/tr/td[1]')).text

    #純資産を数値に変換
    networth = int(networth_text.rstrip("円").replace(",",""))

    browser.quit()

    return networth

def main():
    try:
        networth = get_networth()
        zabbix_sender_cmd = "zabbix_sender -z " + ZABBIX_SERVER_HOST + " -s " + ZABBIX_MONITOR_HOST + " -k " + ZABBIX_MONITOR_ITEM  + " -o " + str(networth)
        subprocess.run(zabbix_sender_cmd, shell=True, stdout=PIPE, stderr=PIPE, text=True).stdout

    except:
        print (traceback.format_exc())
        browser.quit()

if __name__ == '__main__':
    main()

