import subprocess
import time
import json

def run_command(command, cwd=None):
    """指定されたコマンドを実行し、出力を取得する"""
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return None, str(e)

def start_webdriver_agent():
    """WebDriverAgent の起動"""
    print("Starting WebDriverAgent...")
    build_command = "xcodebuild -project WebDriverAgent.xcodeproj -scheme WebDriverAgentRunner -destination 'platform=iOS Simulator,name=iPhone 16 Pro Max' test"
    stdout, stderr = run_command(build_command, cwd="/Users/apple/Appium_python/node_modules/appium-xcuitest-driver/node_modules/appium-webdriveragent")
    if stderr:
        print("Error starting WebDriverAgent:", stderr)
    else:
        print("WebDriverAgent started successfully.")

def check_webdriver_agent():
    """cURL を用いて WebDriverAgent の起動確認"""
    print("Checking WebDriverAgent status...")
    time.sleep(5)  # WebDriverAgent の起動待機
    status_command = "curl -X GET http://localhost:8100/status"
    stdout, stderr = run_command(status_command)
    if stdout:
        try:
            status = json.loads(stdout)
            print("WebDriverAgent Status:", json.dumps(status, indent=2))
        except json.JSONDecodeError:
            print("Invalid response from WebDriverAgent:", stdout)
    if stderr:
        print("Error checking WebDriverAgent:", stderr)

def start_ios_simulator():
    """iOS シミュレーターを起動"""
    print("Starting iOS Simulator...")
    simulator_command = "open -a Simulator"
    stdout, stderr = run_command(simulator_command)
    if stderr:
        print("Error starting iOS Simulator:", stderr)
    else:
        print("iOS Simulator started.")

def main():
    start_ios_simulator()
    start_webdriver_agent()
    check_webdriver_agent()

if __name__ == "__main__":
    main()
