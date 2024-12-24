import subprocess
import schedule
import time
import os
import signal

current_process = None

def run_script():
    global current_process

    # 判斷程式是否在執行
    if current_process and current_process.poll() is None:  
        os.kill(current_process.pid, signal.SIGTERM)  
        try:
            current_process.wait(timeout=5) 
        except subprocess.TimeoutExpired:
            os.kill(current_process.pid, signal.SIGKILL) 

    current_process = subprocess.Popen(["python", "drop_notice.py"])

# 立即執行一次 run_script
run_script()

# 排程時間設定
schedule.every().day.at("09:00").do(run_script)

while True:
    schedule.run_pending()
    time.sleep(1)