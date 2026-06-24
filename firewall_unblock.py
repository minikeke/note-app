import subprocess
import ctypes
import sys
import os

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def main():
    if not is_admin():
        print("需要管理员权限，正在重新启动...")
        script = os.path.abspath(sys.argv[0])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}"', None, 1)
        return

    print("正在放行端口 8502...")
    result = subprocess.run(
        [
            "netsh", "advfirewall", "firewall", "add", "rule",
            "name=Streamlit-8502", "dir=in", "action=allow",
            "protocol=TCP", "localport=8502"
        ],
        capture_output=True,
        text=True
    )

    if result.returncode == 0:
        print("成功！端口 8502 已放行。")
        print("现在可以重新运行启动.bat，手机应该可以访问了。")
    else:
        print("失败，错误信息：")
        print(result.stderr)

    input("\n按回车键退出...")

if __name__ == "__main__":
    main()
