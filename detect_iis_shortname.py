import sys
import ssl
import http.client as httplib
import urllib.parse as urlparse
import threading
import queue
from colorama import Fore

class Scanner:
    def __init__(self, target, proxy=None):
        self.target = target.lower()
        if not self.target.startswith("http"):
            self.target = f"http://{self.target}"
        self.scheme, self.netloc, self.path, _, _, _ = urlparse.urlparse(self.target)
        if not self.path.endswith("/"):
            self.path += "/"
        self.request_method = ""
        self.proxy = proxy

    def _conn(self):
        try:
            if self.proxy:
                conn = httplib.HTTPConnection(self.proxy)
                conn.set_tunnel(self.netloc)
            elif self.scheme == "https":
                conn = httplib.HTTPSConnection(self.netloc, context=ssl._create_unverified_context())
            else:
                conn = httplib.HTTPConnection(self.netloc)
            return conn
        except Exception as e:
            raise Exception(f"[Error] Failed to establish connection: {e}")

    def _get_status(self, path):
        conn = self._conn()
        if conn is None:
            raise Exception(f"[Error] Connection object is None for path {path}")
        try:
            conn.request(self.request_method, path)
            response = conn.getresponse()
            status = response.status
            conn.close()
            return status
        except Exception as e:
            raise Exception(f"[Error] Failed to get status for {path}: {e}")

    def is_vulnerable(self):
        try:
            for _method in ["GET", "OPTIONS"]:
                self.request_method = _method
                status_1 = self._get_status(self.path + "/*~1*/a.aspx")
                status_2 = self._get_status(self.path + "/l1j1e*~1*/a.aspx")
                if status_1 == 404 and status_2 not in [404, 403]:
                    return True
            return False
        except Exception as e:
            raise Exception(f"[Error] Vulnerability check failed: {e}")


def scan_target(target, proxy, results, lock):
    """扫描单个目标"""
    scanner = Scanner(target, proxy=proxy)
    try:
        print(f"[*] Checking {target}...")
        if scanner.is_vulnerable():
            print(Fore.GREEN+f"[+] {target} is vulnerable!")
            with lock:
                results.append(target)
        else:
            print(Fore.YELLOW+f"[-] {target} is not vulnerable")
    except Exception as e:
        print(f"[Error] {target}: {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python detect_iis_shortname.py targets.txt")
        sys.exit(1)

    proxy = "127.0.0.1:10809"  # 示例: "127.0.0.1:8080" 使用 HTTP 代理
    targets_file = sys.argv[1]

    # 读取目标
    with open(targets_file, "r") as f:
        targets = [line.strip() for line in f if line.strip()]

    # 多线程设置
    results = []  # 存储检测到漏洞的目标
    lock = threading.Lock()  # 确保线程安全
    threads = []
    max_threads = 10  # 设置最大线程数

    # 创建线程池
    target_queue = queue.Queue()
    for target in targets:
        target_queue.put(target)

    def worker():
        while not target_queue.empty():
            target = target_queue.get()
            scan_target(target, proxy, results, lock)
            target_queue.task_done()

    # 启动线程
    for _ in range(max_threads):
        thread = threading.Thread(target=worker)
        threads.append(thread)
        thread.start()

    # 等待所有线程完成
    target_queue.join()

    # 保存结果
    with open("vulnerable_targets.txt", "w") as f:
        f.write("\n".join(results))

    print("[+] Vulnerability detection complete!")
    print("[+] Vulnerable targets saved to 'vulnerable_targets.txt'.")
