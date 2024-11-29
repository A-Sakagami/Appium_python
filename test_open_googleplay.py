import pytest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from selenium.webdriver.common.actions.interaction import POINTER_TOUCH
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Desired Capabilitiesの設定
# CapabilitiesをUiAutomator2Optionsで設定
@pytest.fixture(scope="module")
def driver():
    options = UiAutomator2Options()
    options.platform_name = 'Android'
    options.automation_name = 'UiAutomator2'
    options.device_name = 'emulator-5554'

    # Appiumサーバーに接続
    driver = webdriver.Remote("http://localhost:4723", options=options)
    yield driver

    # テスト終了後にドライバーを閉じる
    driver.quit()

def test_google_play_open(driver):
    # 1. ホーム画面からスワイプしてアプリ一覧を開く
    
    # Androidのホームボタンを押して、ホーム画面に戻る
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

    # 2. アプリ一覧からGoogle Playを検索して起動
    try:
        # Google Playアプリを探す (IDやXPathを適切に指定)
        google_play_icon = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((AppiumBy.XPATH, "//android.widget.TextView[@content-desc=\"Play Store\"]"))
        )
        google_play_icon.click()
        assert google_play_icon is not None, "Google Play app not found"

    except Exception as e:
        pytest.fail(f"Test failed due to: {e}")

