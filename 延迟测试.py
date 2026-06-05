import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import re
import threading
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

class PingTesterUI:
    def __init__(self, root):
        self.root = root
        self.root.title("网络延迟测试工具")
        self.root.geometry("500x300")
        
        # 解决 matplotlib 中文乱码问题 (Windows 环境使用 SimHei)
        plt.rcParams['font.sans-serif'] = ['SimHei'] 
        plt.rcParams['axes.unicode_minus'] = False 

        # --- UI 布局 ---
        frame = ttk.Frame(root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text="目标地址:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.target_entry = ttk.Entry(frame, width=40)
        self.target_entry.insert(0, "www.baidu.com") # 默认测试百度
        self.target_entry.grid(row=0, column=1, pady=5, padx=5)

        ttk.Label(frame, text="测试次数:").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.count_entry = ttk.Entry(frame, width=40)
        self.count_entry.insert(0, "10")
        self.count_entry.grid(row=1, column=1, pady=5, padx=5)

        self.start_btn = ttk.Button(frame, text="开始测试", command=self.start_test)
        self.start_btn.grid(row=2, column=0, columnspan=2, pady=20)

        self.status_label = ttk.Label(frame, text="状态: 就绪", foreground="blue")
        self.status_label.grid(row=3, column=0, columnspan=2)

        # 数据存储
        self.latencies = []
        self.is_running = False

    def start_test(self):
        """启动测试，防止 UI 卡死"""
        if self.is_running:
            return
        self.is_running = True
        self.start_btn.config(state=tk.DISABLED)
        self.status_label.config(text="状态: 正在测试...", foreground="orange")
        
        # 在子线程中执行 ping，避免阻塞主 UI 线程
        thread = threading.Thread(target=self.run_ping_test)
        thread.daemon = True
        thread.start()

    def run_ping_test(self):
        """执行 ping 命令并提取延迟数据"""
        target = self.target_entry.get().strip()
        try:
            count = int(self.count_entry.get().strip())
        except ValueError:
            messagebox.showerror("错误", "请输入有效的测试次数！")
            self.reset_ui()
            return

        self.latencies = []
        # Windows 下使用 -n 指定次数
        command = f"ping -n {count} {target}"
        
        try:
            # 实时读取 ping 的输出
            process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            for line in process.stdout:
                # 匹配类似 "时间=14ms" 或 "time=14ms" 的格式
                match = re.search(r'[时间|time][=<](\d+)ms', line, re.IGNORECASE)
                if match:
                    latency = int(match.group(1))
                    self.latencies.append(latency)
                    # 更新 UI 状态
                    self.root.after(0, lambda l=latency: self.status_label.config(
                        text=f"状态: 已收到响应，延迟 {l}ms (共{len(self.latencies)}次)"
                    ))
        except Exception as e:
            messagebox.showerror("执行错误", f"无法执行 ping 命令: {str(e)}")
            self.reset_ui()
            return

        # 测试完成后生成图表
        if self.latencies:
            self.generate_chart()
        else:
            messagebox.showwarning("警告", "未获取到任何延迟数据，请检查网络或目标地址！")
        
        self.reset_ui()

    def generate_chart(self):
        """生成延迟随时间变化的折线图"""
        timestamps = list(range(1, len(self.latencies) + 1))
        
        plt.figure(figsize=(10, 5))
        plt.plot(timestamps, self.latencies, marker='o', linestyle='-', color='b')
        plt.title('网络延迟测试折线图')
        plt.xlabel('测试次数 (时间轴)')
        plt.ylabel('延迟 (ms)')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.show()

    def reset_ui(self):
        """重置 UI 状态"""
        self.is_running = False
        self.root.after(0, lambda: self.start_btn.config(state=tk.NORMAL))
        self.root.after(0, lambda: self.status_label.config(text="状态: 测试完成", foreground="green"))

if __name__ == "__main__":
    root = tk.Tk()
    app = PingTesterUI(root)
    root.mainloop()
