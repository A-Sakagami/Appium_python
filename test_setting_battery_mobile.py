import unittest
from appium import webdriver
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

# CapabilitiesをUiAutomator2Optionsで設定
options = UiAutomator2Options()
options.platform_name = 'Android'
options.automation_name = 'UiAutomator2'
# 接続端末の名前
options.device_name = 'Xperia1_and10'
# udid: adb devicesで検索
options.udid= 'QV7147331V'
options.app_package = 'com.android.settings'
options.app_activity = '.Settings'

appium_server_url = 'http://localhost:4723'


class TestAppium(unittest.TestCase):
    def setUp(self) -> None:
        self.driver = webdriver.Remote(appium_server_url, options=options)

    def tearDown(self) -> None:
        if self.driver:
            self.driver.quit()

    def test_find_battery(self) -> None:
        try:
            # バッテリー要素が表示されるのを最大10秒待機して検索
            el = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((AppiumBy.XPATH, '//androidx.recyclerview.widget.RecyclerView[@resource-id="com.android.settings:id/recycler_view"]/android.widget.LinearLayout[6]/android.widget.RelativeLayout'))
            )
            # 要素が見つかったらクリック
            el.click()
            print("Battery element clicked successfully")
        
        except TimeoutException:
            print("Battery element not found within the time limit.")
        
        except NoSuchElementException:
            print("Battery element not found on the page.")

if __name__ == '__main__':
    unittest.main()