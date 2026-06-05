import tkinter as tk
from tkinter import ttk, messagebox
import requests
import threading
import time
import statistics

class GatewayTesterUI:
    def __init__(self, root):
        self.root = root
        self.root.title("国内外服务器网关严格水平测试工具")
        self.root.geometry("750x450")
        
        # 测试目标列表：(名称, URL, 权重)
        # 权重说明：1.0为普通国内/常用站点，1.5为重要国外/游戏平台站点
        self.targets = [
            # 原有目标
            ("百度 (国内)", "https://www.baidu.com", 1.0),
            ("阿里云 (国内)", "https://www.aliyun.com", 1.0),
            ("GitHub (国外)", "https://github.com", 1.5),
            ("Google (国外)", "https://www.google.com", 1.5),
            ("Cloudflare (国外)", "https://1.1.1.1", 1.2),
            
            # 新增游戏平台目标 (权重设为 1.5)
            ("R星 (Rockstar)", "https://www.rockstargames.com", 1.5),
            ("战雷 (War Thunder)", "https://warthunder.com", 1.5),
            ("EA 官网", "httpsUp://www.ea.com", 1.5),
            ("Steam", "https://store.steampowered.com", 1.5),
            ("育碧 (Ubisoft)", "https://www.ubisoft.com", 1.5),
            ("EPIC 游戏商城", "https://www.epicgames.com", 1.5),
        ]

        # UI 布局
        frame = ttk.Frame(root, padding="10")
        frame.pack(fill=tk.BOTH, expand=True)

        # 创建表格 (Treeview)
        columns = ("name", "latency", "weight", "score", "ref_score")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings")
        self.tree.heading("name", text="网站名称")
        self.tree.heading("latency", text="平均延迟 (ms)")
        self.tree.heading("weight", text="算法权重")
        self.tree.heading("score", text="网关严格水平评分")
        self.tree.heading("ref_score", text="参考评分")

        # 设置列宽
        self.tree.column("name", width=150, anchor="w")
        self.tree.column("latency", width=100, anchor="center")
        self.tree.column("weight", width=80, anchor="center")
        self.tree.column("score", width=120, anchor="center")
        self.tree.column("ref_score", width=120, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)

        # 状态标签和按钮
        self.status_label = ttk.Label(frame, text="状态: 就绪", foreground="blue")
        self.status_label.pack(pady=10)
        self.start_btn = ttk.Button(frame, text="开始测试", command=self.start_test)
        self.start_btn.pack(pady=5)

        # 初始化表格
        self.init_table()

    def init_table(self):
        """初始化表格数据"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        for name, _, weight in self.targets:
            self.tree.insert("", tk.END, values=(name, "测试中...", weight, "计算中...", "参考中..."))

    def start_test(self):
        """启动测试，防止 UI 卡死"""
        self.start_btn.config(state=tk.DISABLED)
        self.status_label.config(text="状态: 正在并发测试...", foreground="orange")
        self.init_table()
        thread = threading.Thread(target=self.run_tests)
        thread.daemon = True
        thread.start()

    def run_tests(self):
        """执行所有目标的测试"""
        results = []
        for i, (name, url, weight) in enumerate(self.targets):
            latency, loss_rate, stdev = self.test_single_target(url)
            # 计算网关严格水平评分 (0-100，分数越低网关越严格)
            score = max(0, 100 - (loss_rate * 100) - (stdev / 10))
            # 根据权重调整参考评分
            ref_score = 85 * weight
            results.append((name, latency, weight, round(score, 1), round(ref_score, 1)))
            
            # 更新 UI
            self.root.after(0, self.update_row, i, latency, score, ref_score)
        
        self.root.after(0, self.test_finished)

    def test_single_target(self, url):
        """测试单个目标，返回延迟、丢包率、标准差"""
        latencies = []
        timeout_count = 0
        total_tests = 5
        for _ in range(total_tests):
            try:
                start = time.time()
                # 使用 HEAD 请求更轻量，超时设为 3 秒
                requests.head(url, timeout=3)
                latency = (time.time() - start) * 1000
                latencies.append(latency)
            except requests.exceptions.RequestException:
                timeout_count += 1
            time.sleep(0.2) # 避免请求过快
        
        loss_rate = timeout_count / total_tests
        stdev = statistics.stdev(latencies) if len(latencies) > 1 else 0
        avg_latency = round(statistics.mean(latencies), 1) if latencies else "超时"
        return avg_latency, loss_rate, stdev

    def update_row(self, index, latency, score, ref_score):
        """更新表格中某一行的数据"""
        item = self.tree.get_children()[index]
        values = self.tree.item(item, "values")
        self.tree.item(item, values=(values[0], latency, values[2], score, ref_score))

    def test_finished(self):
        """测试完成后的 UI 状态更新"""
        self.start_btn.config(state=tk.NORMAL)
        self.status_label.config(text="状态: 测试完成 (分数越低代表网关越严格)", foreground="green")

if __name__ == "__main__":
    root = tk.Tk()
    app = GatewayTesterUI(root)
    root.mainloop()
