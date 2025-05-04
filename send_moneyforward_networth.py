from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import traceback
import subprocess
import sys
import os
from subprocess import PIPE


USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36'
START_URL = 'https://moneyforward.com/users/sign_in'
BS_URL = 'https://moneyforward.com/bs/balance_sheet'
USER_DATA_DIR= '/home/ec2-user/cookies/moneyforward.com/'
# USER_DATA_DIR= 'cookies/moneyforward.com/'


ZABBIX_SERVER_HOST = "localhost"
ZABBIX_MONITOR_HOST = "MoneyForward"
ZABBIX_MONITOR_ITEM = "networth"

username = subprocess.run("get_login_username moneyforward.com", shell=True, stdout=PIPE, stderr=PIPE, text=True).stdout
password = subprocess.run("get_login_password moneyforward.com", shell=True, stdout=PIPE, stderr=PIPE, text=True).stdout


def get_networth():
    chrome_option = webdriver.ChromeOptions()
    chrome_option.add_argument('--headless=new')
    chrome_option.add_argument('--no-sandbox')
    chrome_option.add_argument('--disable-gpu')
    chrome_option.add_argument('--disable-dev-shm-usage')
    chrome_option.add_argument('--remote-debugging-port=9222')
    chrome_option.add_argument('user-agent=' + USER_AGENT)
    chrome_option.add_argument('--user-data-dir=' + USER_DATA_DIR)
    chrome_option.add_argument('--disable-software-rasterizer')
    chrome_option.add_argument('--disable-blink-features=AutomationControlled')
    chrome_option.add_argument('--disable-features=VizDisplayCompositor')
    chrome_option.add_argument("--enable-logging")
    chrome_option.add_argument("--v=1")

    service = Service("/usr/bin/chromedriver")  # ← `which chromedriver` で確認した実パス
    driver = webdriver.Chrome(service=service, options=chrome_option)

    wait = WebDriverWait(driver=driver, timeout=30)


    # ログイン画面を開く
    driver.get(START_URL)
    print("open START_URL")
    driver.save_screenshot('START_page_screenshot.png')
    wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))  # ←追加
    driver.save_screenshot("Before_Login_check.png")


    # （ログインボタンのクラス指定でコレクション取得した結果がfalse (＝ログインボタンが存在しない）なら、ログイン済みと判断。
    if(driver.find_elements(By.CLASS_NAME, 'rR4ct5ug')):
        if(sys.stdin.isatty()):

            # ユーザ名（メールアドレス）を入力し、submit
            driver.find_element(By.NAME, "mfid_user[email]").clear()
            driver.find_element(By.NAME, "mfid_user[email]").send_keys(username)
            driver.find_element(By.ID, 'submitto').click()

            print("send username.")
            driver.save_screenshot('After_send_username_page_screenshot.png')

            # 要素が全て検出できるまで待機する
            wait.until(EC.presence_of_all_elements_located)

            # パスワードを入力し、submit -> ここまででログイン完了
            driver.find_element(By.NAME, "mfid_user[password]").clear()
            driver.find_element(By.NAME, "mfid_user[password]").send_keys(password)
            driver.save_screenshot('After_input_password_screenshot.png')
            driver.find_element(By.ID, 'submitto').click()

            print("send password.")

            wait.until(EC.presence_of_all_elements_located)

            # メールで届いたワンタイムパスワードを入力
            email_otp = input("Enter OTP from email: ").strip()
            driver.find_element(By.NAME, "email_otp").clear()
            driver.find_element(By.NAME, "email_otp").send_keys(email_otp)
            driver.save_screenshot('After_input_email-otp_screenshot.png')
            driver.find_element(By.ID, 'submitto').click()
        else:
            print("OTP required, but no interactive input available. Skipping.")
            with open('/var/log/mf_networth_error.log', 'a') as log:
                log.write("[{}] OTP required, but script was run non-interactively. Login skipped.\n".format(
                    datetime.datetime.now().isoformat()
                ))
            driver.quit()
            return


    # バランスシートのページに遷移
    driver.get(BS_URL)
    # driver.save_screenshot('BS_page_screenshot.png')

    #「純資産」欄のテキストを取得
    networth_text = driver.find_element(By.XPATH, '//*[@id="bs-balance-sheet"]/section/section[2]/div/div[2]/section[2]/table/tbody/tr/td[1]').text

    #純資産を数値に変換
    networth = int(networth_text.rstrip("円").replace(",",""))

    driver.quit()

    return networth

def main():
    try:
        networth = get_networth()
        print("networth: ", networth)
        zabbix_sender_cmd = "zabbix_sender -z " + ZABBIX_SERVER_HOST + " -s " + ZABBIX_MONITOR_HOST + " -k " + ZABBIX_MONITOR_ITEM  + " -o " + str(networth)
        subprocess.run(zabbix_sender_cmd, shell=True, stdout=PIPE, stderr=PIPE, text=True).stdout

    except:
        print (traceback.format_exc())

if __name__ == '__main__':
    main()

