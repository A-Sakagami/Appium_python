import pytest
import time
import unittest
import os
from dotenv import load_dotenv
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException


# CapabilitiesをUiAutomator2Optionsで設定
@pytest.fixture(scope="module")
def driver():
    options = UiAutomator2Options()
    options.platform_name = 'Android'
    options.automation_name = 'UiAutomator2'
    # 接続端末の名前
    options.device_name = 'Xperia1_and10'
    # udid: adb devicesで検索
    options.udid= 'QV7147331V'  
    options.app_package = 'com.google.android.gm'
    options.app_activity = 'com.google.android.gm.ConversationListActivityGmail'
    options.no_reset = True

    # Appiumサーバーに接続
    driver = webdriver.Remote("http://localhost:4723", options=options)
    yield driver

    # テスト終了後にドライバーを閉じる
    driver.quit()

def test_google_login(driver):
    # .envファイルを読み込む
    load_dotenv()

    # Androidのホームボタンを押して、ホーム画面に戻る
    driver.press_keycode(3)  # 3はホームボタンに対応
    time.sleep(2)  # ページロード待機
    
    # GMAILアイコンをタップ
    gmail_icon = driver.find_element(AppiumBy.ACCESSIBILITY_ID, 'Gmail')
    gmail_icon.click()

    # skipボタンをタップ
    skip_button = driver.find_element(AppiumBy.ID, 'com.google.android.gm:id/welcome_tour_skip')
    skip_button.click()

    # メールアドレス追加ボタンをタップ
    add_mail_address = driver.find_element(AppiumBy.ID, 'com.google.android.gm:id/setup_addresses_add_another')
    add_mail_address.click()

    # googleを選択
    select_google = driver.find_element(AppiumBy.XPATH, '(//android.widget.LinearLayout[@resource-id="com.google.android.gm:id/account_setup_item"])[1]')
    select_google.click()

    time.sleep(10)  # ページロード待機

    # ログインするGMAILアカウントを入力
    # 要素取得が不安定だったため、要素探索を反復試行する関数を導入
    assert find_element_until_found(driver, AppiumBy.CLASS_NAME, 'android.widget.EditText', 30, 2).send_keys(os.getenv('GMAIL_EMAIL'))
    driver.find_element(by=AppiumBy.XPATH, value='//android.widget.Button[@text="次へ"]').click()

    time.sleep(3)  # ページロード待機
    # パスワード入力
    driver.find_element(AppiumBy.CLASS_NAME, value='android.widget.EditText').send_keys(os.getenv('GMAIL_PASSWORD'))
    driver.find_element(AppiumBy.XPATH, value='//android.widget.Button[@text="次へ"]').click()

    # ボタンタップ
    time.sleep(3) # ページロード待機
    driver.find_element(AppiumBy.XPATH, value='//android.widget.Button[@text="同意する"]').click()

    # ボタンタップ
    time.sleep(5) # ページロード待機
    toggle = driver.find_element(AppiumBy.XPATH, value='//android.widget.Switch[@resource-id="com.google.android.gms:id/sud_items_switch"]')
    if toggle.get_attribute('checked') == True:
        toggle.click()
    driver.find_element(AppiumBy.XPATH, value='//android.widget.Button[@text="同意する"]').click()

# 要素が見つかるまで繰り返す処理
def find_element_until_found(driver, by, value, timeout, interval):
    """
    要素が見つかるまで指定の時間繰り返す
        driver: WebDriverインスタンス
        by: 検索のタイプ (例: AppiumBy.ID, AppiumBy.XPATH)
        value: 検索する値（特定のID, CLASS名、XPATHなど）
        timeout: 見つかるまでの最大時間 (秒)
        interval: 要素が見つからなかった場合の再試行間隔 (秒)
    """
    end_time = time.time() + timeout
    while True:
        try:
            # 要素が見つかった場合
            element = driver.find_element(by, value)
            return element  # 見つかった要素を返す
        except NoSuchElementException:
            # タイムアウトに達した場合
            if time.time() > end_time:
                raise Exception(f"Element not found within {timeout} seconds")
            # 指定した間隔だけ待機して再試行
            time.sleep(interval)

if __name__ == '__main__':
    unittest.main()

