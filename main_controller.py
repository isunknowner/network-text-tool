import tkinter as tk
from tkinter import ttk
import subprocess
import os

class AppControllerUI:
    def __init__(self, root):
        self.root = root
        self.root.title("程序总控制台")
        self.root.geometry("400x200")
        
        # ⚠️ 在这里修改为你实际的绝对路径
        self.programs = {
            "网关严格度测试": r"Absolute file path",#such as "C:\Users\Desktop\abc\网关严格度测试.py"
            "延迟测试": r"Absolute file path"
        }
        
        self.processes = {}  # 用于存储运行中的进程对象
        
        # UI 布局
        frame = ttk.Frame(root, padding="20")
        frame.pack(fill=tk.BOTH, expand=True)
        
        row = 0
        for name in self.programs:
            ttk.Label(frame, text=f"{name}:").grid(row=row, column=0, sticky=tk.W, pady=10)
            
            btn_frame = ttk.Frame(frame)
            btn_frame.grid(row=row, column=1, padx=10)
            
            start_btn = ttk.Button(btn_frame, text="启动", command=lambda n=name: self.start_program(n))
            start_btn.pack(side=tk.LEFT, padx=5)
            
            stop_btn = ttk.Button(btn_frame, text="关闭", command=lambda n=name: self.stop_program(n))
            stop_btn.pack(side=tk.LEFT, padx=5)
            
            row += 1

    def start_program(self, name):
        """启动指定的子程序，并隐藏黑窗口"""
        if name in self.processes and self.processes[name].poll() is None:
            # messagebox.showwarning("警告", f"{name} 已经在运行中！") # 已删除
            return
            
        script_path = self.programs[name]
        if not os.path.exists(script_path):
            # messagebox.showerror("错误", f"找不到文件:\n{script_path}") # 已删除
            return

        try:
            # 核心：使用 CREATE_NO_WINDOW 标志隐藏控制台窗口
            creation_flags = 0x08000000  # subprocess.CREATE_NO_WINDOW
            
            process = subprocess.Popen(
                ['pythonw', script_path],  # 使用 pythonw 也可以避免窗口
                creationflags=creation_flags
            )
            self.processes[name] = process
            # messagebox.showinfo("成功", f"{name} 已成功启动！") # 已删除
        except Exception as e:
            # messagebox.showerror("启动失败", str(e)) # 已删除
            pass

    def stop_program(self, name):
        """关闭指定的子程序"""
        if name in self.processes:
            process = self.processes[name]
            if process.poll() is None:  # 检查进程是否还在运行
                process.terminate()     # 发送终止信号
                process.wait()          # 等待进程结束
                del self.processes[name]
                # messagebox.showinfo("成功", f"{name} 已成功关闭！") # 已删除
            else:
                # messagebox.showinfo("提示", f"{name} 已经停止运行。") # 已删除
                del self.processes[name]
        else:
            # messagebox.showinfo("提示", f"{name} 当前未在运行。") # 已删除
            pass

if __name__ == "__main__":
    root = tk.Tk()
    app = AppControllerUI(root)
    root.mainloop()
