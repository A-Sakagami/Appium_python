from appium.webdriver.appium_service import AppiumService
from appium.options.ios import XCUITestOptions
# remote_server_addr の設定方法が変更され、新しい ClientConfig を使用するよう推奨された 2025/2/18
from selenium.webdriver.remote.remote_connection import RemoteConnection
from appium import webdriver
import pytest

@pytest.fixture(scope="module")
def ios_driver():
    options = XCUITestOptions()
    options.set_capability("platformName", "iOS")
    # options.set_capability("platformVersion", "16.0")
    options.set_capability("platformVersion", "18.3")
    # options.set_capability("deviceName", "iPhone 14 Pro Max")
    options.set_capability("deviceName", "iPhone 16 Pro Max")
    options.set_capability("automationName", "XCUITest")
    options.set_capability("bundleId", "com.apple.Preferences")
    options.set_capability("noReset", True)

    driver = webdriver.Remote("http://localhost:4723", options=options)

    yield driver
    driver.quit()

def test_ios_launch(ios_driver):
    assert ios_driver.is_app_installed("com.apple.Preferences")
    ios_driver.terminate_app("com.apple.Preferences")
    assert ios_driver.query_app_state("com.apple.Preferences") == 1

if __name__ == "__main__":
    pytest.main(["-v", "-s", __file__])
