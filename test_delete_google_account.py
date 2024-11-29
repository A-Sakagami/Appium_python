import pytest
import time
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.actions.interaction import POINTER_TOUCH
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
    options.app_package = 'com.android.settings'
    options.app_activity = 'Settings'
    options.no_reset = True

    # Appiumサーバーに接続
    driver = webdriver.Remote("http://localhost:4723", options=options)
    yield driver

    # テスト終了後にドライバーを閉じる
    driver.quit()

def test_delete_account(driver):
    driver.press_keycode(3)  # 3はホームボタンに対応

    screen_size = driver.get_window_size()
    # 中央スワイプでは別オプションが起動することがあるため、x始点をやや左側に調整
    start_x = screen_size["width"] // 3
    start_y = screen_size["height"] * 0.8
    end_y = screen_size["height"] * 0.2

    # PointerInputを使用したスワイプ操作
    touch_input = PointerInput(POINTER_TOUCH, "finger")
    action_builder = ActionBuilder(driver, touch_input)
    action_builder.pointer_action.move_to_location(start_x, start_y)
    action_builder.pointer_action.pointer_down()
    action_builder.pointer_action.move_to_location(start_x, end_y)
    action_builder.pointer_action.pointer_up()
    action_builder.perform()

    setting = driver.find_element(AppiumBy.XPATH, value='//android.widget.TextView[@content-desc="設定"]')
    setting.click()
    account = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((AppiumBy.XPATH, '//androidx.recyclerview.widget.RecyclerView[@resource-id="com.android.settings:id/recycler_view"]/android.widget.LinearLayout[7]/android.widget.RelativeLayout'))
    )
    account.click()

    # アカウントがあれば削除する。ない場合はpass
    # アカウントが存在するか確認
     # アカウントが存在するか確認
    try:
        account_list = driver.find_elements(AppiumBy.XPATH, value='//androidx.recyclerview.widget.RecyclerView[@resource-id="com.android.settings:id/recycler_view"]/android.widget.LinearLayout/android.widget.LinearLayout')
        
        if len(account_list) == 0:
            print("アカウントが見つかりませんでした。処理を終了します。")
            return
        else:
            for account in account_list:
                account.click()
                time.sleep(1)

                # 削除の確認
                try:
                    delete_button = driver.find_element(AppiumBy.ID, value='com.android.settings:id/button')
                    delete_button.click()
                    time.sleep(2)

                    # 確認ダイアログで「OK」をクリック
                    confirm_button = driver.find_element(AppiumBy.ID, value='android:id/button1')
                    confirm_button.click()
                    time.sleep(2)
                    print("アカウントを削除しました。")
                except NoSuchElementException:
                    print("アカウント削除ボタンが見つかりません。")
    except NoSuchElementException:
        print("アカウントが見つかりませんでした。")
        return