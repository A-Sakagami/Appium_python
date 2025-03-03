import subprocess
import time
import json

def run_command_realtime(command, cwd=None):
    """ コマンドをリアルタイムで実行し、出力を表示する """
    try:
        process = subprocess.Popen(command, shell=True, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        # リアルタイムでログを表示
        for line in iter(process.stdout.readline, ''):
            print(line, end='')

        process.stdout.close()
        process.wait()

        return process.returncode
    except Exception as e:
        print("Error executing command:", str(e))
        return -1

def start_webdriver_agent():
    """WebDriverAgent の起動"""
    print("Starting WebDriverAgent...")
    build_command = (
        "xcodebuild -project WebDriverAgent.xcodeproj "
        "-scheme WebDriverAgentRunner "
        "-destination 'platform=iOS Simulator,name=iPhone 16 Pro Max' "
        "test -verbose | tee wda_log.txt"
    )
    exit_code = run_command_realtime(build_command, cwd="/Users/apple/Appium_python/node_modules/appium-xcuitest-driver/node_modules/appium-webdriveragent")

    if exit_code == 0:
        print("WebDriverAgent started successfully.")
    else:
        print("Error starting WebDriverAgent:", exit_code)

def check_webdriver_agent():
    """ cURL を用いて WebDriverAgent の起動確認 """
    print("Checking WebDriverAgent status...")
    time.sleep(5)  # WebDriverAgent の起動待機
    WDA_IP = "192.168.10.103"
    status_command = f"curl -X GET http://{WDA_IP}:8100/status"

    stdout, stderr = subprocess.run(status_command, shell=True, capture_output=True, text=True).stdout, stderr

    if stdout:
        try:
            status = json.loads(stdout)
            print("WebDriverAgent Status:", json.dumps(status, indent=2))
        except json.JSONDecodeError:
            print("Invalid response from WebDriverAgent:", stdout)
    if stderr:
        print("Error checking WebDriverAgent:", stderr)

def start_ios_simulator():
    """ iOS シミュレーターを起動 """
    print("Starting iOS Simulator...")
    simulator_command = "open -a Simulator"
    subprocess.run(simulator_command, shell=True)

def main():
    start_ios_simulator()
    start_webdriver_agent()
    check_webdriver_agent()

if __name__ == "__main__":
    main()
