import subprocess
import json
import asyncio
import shlex
import os
import re
import dotenv

# 環境変数をロード
dotenv.load_dotenv()

def load_env_variables():
    """ 必要な環境変数を取得し、不足していたらエラーを出す """
    required_vars = ["IOS_VERSION", "DEVICE_ID", "DEVICE_NAME", "WDA_PROJECT_PATH"]
    env_vars = {var: os.getenv(var) for var in required_vars}

    missing_vars = [var for var, value in env_vars.items() if value is None]
    if missing_vars:
        raise ValueError(f"以下の環境変数が不足しています: {', '.join(missing_vars)}")

    return env_vars

async def run_command(command, cwd=None, capture_output=False):
    """ 非同期でコマンドを実行し、出力をリアルタイムで取得 """
    process = await asyncio.create_subprocess_exec(
        *shlex.split(command), cwd=cwd,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    stdout_lines = []
    stderr_lines = []

    async for line in process.stdout:
        decoded_line = line.decode().strip()
        stdout_lines.append(decoded_line)
        print(decoded_line)  # 標準出力をリアルタイム表示

    async for line in process.stderr:
        decoded_line = line.decode().strip()
        stderr_lines.append(decoded_line)
        print(f"ERROR: {decoded_line}")  # エラー出力をリアルタイム表示

    await process.wait()

    return stdout_lines, stderr_lines, process.returncode

async def start_webdriver_agent(env_vars):
    """ WebDriverAgent を非同期で起動し、ServerURL を検出 """
    print("Starting WebDriverAgent...")

    build_command = (
        f"xcodebuild -project WebDriverAgent.xcodeproj "
        f"-scheme WebDriverAgentRunner "
        f"-destination \"id={env_vars['DEVICE_ID']}\" "
        f"test -verbose"
    )
    print(f"Executing command: {build_command}")

    process = await asyncio.create_subprocess_exec(
        *shlex.split(build_command),
        cwd=env_vars["WDA_PROJECT_PATH"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    wda_url = None
    async for line in process.stdout:
        decoded_line = line.decode().strip()
        print(decoded_line)  # 標準出力をリアルタイムで表示
        
        # ServerURL の検出
        match = re.search(r"ServerURLHere->\s*(http://[0-9\.]+:\d+)", decoded_line)
        if match:
            wda_url = match.group(1)
            print(f"✅ WebDriverAgent started at {wda_url}")
            break  # URL を検出したらループを抜ける

    if not wda_url:
        print("❌ Error: WebDriverAgent failed to start properly.")
        await process.wait()
        return None

    return wda_url

async def check_webdriver_agent(wda_url):
    """ WebDriverAgent のステータスを非同期で定期的に確認 """
    print(f"Checking WebDriverAgent status at {wda_url}...")

    while True:
        status_command = f"curl -s -X GET {wda_url}/status"
        stdout, stderr, _ = await run_command(status_command)

        if stdout:
            try:
                status = json.loads("".join(stdout))
                print("✅ WebDriverAgent Status:", json.dumps(status, indent=2))
                break  # 正常なレスポンスが返ってきたらループを抜ける
            except json.JSONDecodeError:
                print("⚠️ Invalid response from WebDriverAgent:", stdout)

        if stderr:
            print("❌ Error checking WebDriverAgent:", stderr)

        await asyncio.sleep(10)  # 10秒ごとにチェック


async def start_ios_simulator(env_vars):
    """ iOS シミュレーターを起動するが、すでに Booted ならスキップ """
    print("Checking if iOS Simulator is already booted...")

    # すでに Booted なら何もしない
    stdout, _, _ = await run_command("xcrun simctl list devices booted")
    if env_vars['DEVICE_ID'] in " ".join(stdout):
        print("✅ iOS Simulator is already booted. Skipping boot command.")
    else:
        print("🔄 Booting iOS Simulator...")
        await run_command(f"xcrun simctl boot {env_vars['DEVICE_ID']}")

    # シミュレーターアプリを開く
    print("📱 Opening iOS Simulator...")
    await run_command("open -a Simulator")

async def main():
    """ メイン処理 """
    env_vars = load_env_variables()

    await start_ios_simulator(env_vars)

    wda_url = await start_webdriver_agent(env_vars)  # WebDriverAgent の ServerURL を監視
    if wda_url:
        await check_webdriver_agent(wda_url)  # ServerURL が検出されたら接続確認

    print("WebDriverAgent is still running. You can access it at:", wda_url)
    print("All tasks completed. Exiting...")

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())  # メイン処理を実行
    except KeyboardInterrupt:
        print("Received exit signal. Stopping gracefully...")
    finally:
        print("Event loop closed.")
        loop.close()

