import pytest
import time
import os
from dotenv import load_dotenv
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Desired Capabilitiesの設定
# CapabilitiesをUiAutomator2Optionsで設定
@pytest.fixture(scope="module")
def driver():
    options = UiAutomator2Options()
    options.platform_name = 'Android'
    options.automation_name = 'UiAutomator2'
    options.device_name = 'emulator-5554' # エミュレーター
    #options.device_name = 'Aquos sense4 Lite'  # 実機
    #options.udid= '354961111303777'  # adb devicesで検索
    options.unicodeKeyboard = True
    options.resetKeyboard = True

    # Appiumサーバーに接続
    driver = webdriver.Remote("http://localhost:4723", options=options)
    yield driver

    # テスト終了後にドライバーを閉じる
    driver.quit()

def test_google_serach(driver):
    # Androidのホームボタンを押して、ホーム画面に戻る
    driver.press_keycode(3)  # 3はホームボタンに対応
    time.sleep(2)  # ページロード待機
    # Google検索
    # Chromeがあるか確認する
    try:
        chrome = driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value="Chrome")
        assert chrome.is_displayed()
        chrome.click()
        time.sleep(2)
    except NoSuchElementException:
        pytest.fail("Chrome not found")

    # 検索ボックスが存在するか確認する
    if (driver.find_elements(by=AppiumBy.ID, value="com.android.chrome:id/search_provider_logo")):
        search_box = driver.find_element(by=AppiumBy.ID, value="com.android.chrome:id/search_box_text")
    else:
        search_box = driver.find_element(by=AppiumBy.ID, value="com.android.chrome:id/url_bar")
    search_box.send_keys("Appium")
    driver.press_keycode(66)  # 66はEnterキーに対応

    # 検索結果が表示されるまで待機
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((AppiumBy.ID, "com.android.chrome:id/url_bar"))
    )

    # 検索結果が"Appium"を含むことを確認
    assert "Appium" in driver.find_element(by=AppiumBy.ID, value="com.android.chrome:id/url_bar").text
    time.sleep(5)
    search_keyword = driver.find_element(by=AppiumBy.ANDROID_UIAUTOMATOR, value="new UiSelector().text(\"Welcome - Appium Documentation\")")
    search_keyword.click()
    time.sleep(5)

    # URLにappium.ioが含まれているか確認
    page_source = driver.page_source
    assert "appium.io" in page_source, f"Expected page source to contain 'appium.io', but got {page_source}"

    # Chromeのタブを閉じる
    chrome_tab = driver.find_element(by=AppiumBy.ID, value="com.android.chrome:id/tab_switcher_button")
    chrome_tab.click()
    time.sleep(2)
    try:
        while(driver.find_element(by=AppiumBy.ANDROID_UIAUTOMATOR, value="new UiSelector().resourceId(\"com.android.chrome:id/tab_title\").instance(0)").is_displayed()):
            driver.find_element(by=AppiumBy.ANDROID_UIAUTOMATOR, value="new UiSelector().resourceId(\"com.android.chrome:id/action_button\").instance(0)").click()
            time.sleep(2)
    except NoSuchElementException:
        driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value="New tab").click()
        pass
    
    driver.press_keycode(3)  # 3はホームボタンに対応

# googleアカウントにログインする
def test_google_login(driver):
    # .env ファイルをロード
    load_dotenv()
    email=os.getenv("GMAIL_EMAIL")
    password=os.getenv("GMAIL_PASSWORD")
    print(email)
    print(password)


    driver.press_keycode(3)  # 3はホームボタンに対応
    time.sleep(2)  # ページロード待機
    
    # ホーム画面のアカウントボタンを押す
    chrome = driver.find_element(by=AppiumBy.ACCESSIBILITY_ID, value="Chrome")
    chrome.click()

    # ログイン画面に遷移する
    login_button = WebDriverWait(driver,30).until(
        EC.presence_of_element_located((AppiumBy.ACCESSIBILITY_ID, "Signed out. Opens options to sign in."))
    )
    login_button.click()
    select_account = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().className(\"android.widget.ImageView\").instance(3)"))
    )
    select_account.click()
    add_new_account = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((AppiumBy.ANDROID_UIAUTOMATOR, "new UiSelector().text(\"Add account to device\")"))
    )
    add_new_account.click()

    # メールアドレス入力画面まで待機
    email_field = WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((AppiumBy.CLASS_NAME, "android.widget.EditText"))
    )

    # メールアドレスを入力する
    email_field.click()
    email_field.send_keys(email)
    time.sleep(2)

    # NEXTボタンをタップする
    driver.find_element(by=AppiumBy.ANDROID_UIAUTOMATOR, value="new UiSelector().text(\"NEXT\")").click()
    time.sleep(5)

    # パスワード入力画面まで待機
    password_field =  WebDriverWait(driver, 30).until(
        EC.presence_of_element_located((AppiumBy.CLASS_NAME, "android.widget.EditText"))
    )
    # パスワードを入力する
    password_field.click()
    password_field.send_keys(password)
    driver.press_keycode(66)  # 66はEnterキーに対応
    time.sleep(2)

    # NEXTボタンをタップする
    driver.find_element(by=AppiumBy.ANDROID_UIAUTOMATOR, value="new UiSelector().text(\"NEXT\")").click()
    time.sleep(5)
    driver.save_screenshot("screenshots/screenshot.png")

    # ログイン後のアカウント画面が表示されることを確認する
    assert "Account" in driver.page_source, "Expected page source to contain 'Account', but got {}".format(driver.page_source)

    # ホーム画面に戻る
    driver.press_keycode(3)  # 3はホームボタンに対応
    time.sleep(2)  # ページロード待機

if __name__ == "__main__":
    pytest.main()