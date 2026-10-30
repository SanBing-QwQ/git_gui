# -*- coding: utf-8 -*-
# Copyright (c) 2026 散冰. All rights reserved.

# 本项目源码基于 GPL-3.0 许可证开源。
# 您可以自由地使用、修改和分发此代码，但需保留上述版权声明。

import os
import sys
import json
import random
import threading
import subprocess
import datetime
import shutil
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import tkinter.font as tkfont

基础目录 = os.path.dirname(os.path.abspath(sys.argv[0]))
文件目录 = os.path.join(基础目录, "file")
日志目录 = os.path.join(文件目录, "logs")
配置文件路径 = os.path.join(文件目录, "config.json")

Git官网地址 = "https://git-scm.com/download/win"
Winget地址 = "https://learn.microsoft.com/zh-cn/windows/package-manager/winget/"
Winget命令 = "winget install --id Git.Git -e --source winget & pause"

GITHUB_TOKEN页 = "https://github.com/settings/tokens"
GITHUB新建仓库页 = "https://github.com/new"

彩蛋文字 = "这是开发者留下的彩蛋（这只有5%的概率出现，你今天一定很好运）"

普通蓝色 = "#0066CC"
深蓝色 = "#0055AA"
红色 = "red"
深红色 = "#cc0000"
禁用底色 = "#cccccc"
禁用前景色 = "#888888"
绿色 = "#008000"
深绿色 = "#006400"

def 资源路径(名):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, 名)
    return os.path.join(基础目录, 名)

def 设置全局字体():
    for 名 in ["TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont",
              "TkCaptionFont", "TkSmallCaptionFont", "TkIconFont", "TkTooltipFont"]:
        try:
            tkfont.nametofont(名).configure(family="微软雅黑", size=10)
        except Exception:
            pass

def 设置样式(根):
    样式 = ttk.Style(根)
    try:
        样式.configure("Treeview", font=("微软雅黑", 10), rowheight=28)
        样式.configure("Treeview.Heading", font=("微软雅黑", 10, "bold"))
        样式.configure("TNotebook.Tab", font=("微软雅黑", 10))
        样式.configure("TCombobox", font=("微软雅黑", 10))
        样式.configure("TButton", font=("微软雅黑", 10))
        样式.configure("TCheckbutton", font=("微软雅黑", 10))
    except Exception:
        pass

def 确保目录():
    os.makedirs(日志目录, exist_ok=True)

def 今天字符串():
    return datetime.datetime.now().strftime("%Y-%m-%d")

def 居中窗口(窗口, 宽=None, 高=None):
    窗口.update_idletasks()
    if 宽 is None:
        宽 = max(窗口.winfo_width(), 窗口.winfo_reqwidth())
    if 高 is None:
        高 = max(窗口.winfo_height(), 窗口.winfo_reqheight())
    屏宽 = 窗口.winfo_screenwidth()
    屏高 = 窗口.winfo_screenheight()
    x = (屏宽 - 宽) // 2
    y = (屏高 - 高) // 2
    窗口.geometry(f"{宽}x{高}+{x}+{y}")

def 写日志(操作):
    确保目录()
    路径 = os.path.join(日志目录, f"log_{今天字符串()}.txt")
    首次 = not os.path.exists(路径)
    时间戳 = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(路径, "a", encoding="utf-8") as f:
            if 首次 and random.random() < 0.05:
                f.write(f"// {彩蛋文字}\n")
            f.write(f"[{时间戳}]{操作}\n")
    except Exception:
        pass

def 清理旧日志():
    确保目录()
    现在 = datetime.datetime.now()
    for 名 in os.listdir(日志目录):
        if not (名.startswith("log_") and 名.endswith(".txt")):
            continue
        日期串 = 名[4:-4]
        try:
            日期 = datetime.datetime.strptime(日期串, "%Y-%m-%d")
        except ValueError:
            continue
        if (现在 - 日期).days > 10:
            try:
                os.remove(os.path.join(日志目录, 名))
            except Exception:
                pass

def 加载配置():
    确保目录()
    if not os.path.exists(配置文件路径):
        配置 = {"repositories": [], "settings": {}, "github": {}}
        保存配置(配置)
        return 配置
    try:
        with open(配置文件路径, "r", encoding="utf-8") as f:
            文本 = f.read()
        行列表 = [行 for 行 in 文本.splitlines()
                if not 行.strip().startswith("#") and not 行.strip().startswith("//")]
        配置 = json.loads("\n".join(行列表))
        if not isinstance(配置, dict):
            配置 = {}
        if "repositories" not in 配置:
            配置["repositories"] = []
        if "settings" not in 配置:
            配置["settings"] = {}
        if "github" not in 配置:
            配置["github"] = {}
        return 配置
    except Exception:
        配置 = {"repositories": [], "settings": {}, "github": {}}
        保存配置(配置)
        return 配置

def 保存配置(配置):
    确保目录()
    内容 = json.dumps(配置, ensure_ascii=False, indent=2)
    with open(配置文件路径, "w", encoding="utf-8") as f:
        f.write(内容)

def 运行git(参数, 目录=None, 超时=120):
    try:
        创建标志 = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
        p = subprocess.run(
            ["git"] + 参数, cwd=目录,
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            creationflags=创建标志,
            timeout=超时
        )
        return p.returncode, p.stdout, p.stderr
    except subprocess.TimeoutExpired:
        return -1, "", f"git 命令超时（{超时} 秒），可能是网络或钩子导致挂起"
    except FileNotFoundError:
        return -1, "", "git not found"
    except Exception as e:
        return -1, "", str(e)

def 检查git():
    返回码, _, _ = 运行git(["--version"])
    return 返回码 == 0

def 获取全局用户名():
    码, 输出, _ = 运行git(["config", "--global", "user.name"])
    return 输出.strip() if 码 == 0 else ""

def 获取全局邮箱():
    码, 输出, _ = 运行git(["config", "--global", "user.email"])
    return 输出.strip() if 码 == 0 else ""

def 运行winget安装():
    try:
        subprocess.Popen(["cmd", "/c", "start", "cmd", "/k", Winget命令], shell=False)
        写日志("启动winget安装git")
    except Exception as e:
        messagebox.showerror("错误", f"启动失败：{e}")

def 显示无git窗口():
    根 = tk.Tk()
    根.title("Git_gui")
    设置全局字体()
    设置样式(根)
    居中窗口(根, 480, 380)

    try:
        根.iconbitmap(资源路径("Git_gui.ico"))
    except Exception:
        pass

    框架 = tk.Frame(根)
    框架.pack(expand=True, fill="both")

    tk.Label(
        框架,
        text="您还未安装git，您可以选择直接使用下面的方式（安装完成以后请重启应用程序）",
        font=("微软雅黑", 11), wraplength=400, justify="center"
    ).pack(pady=20, padx=20)

    按钮区 = tk.Frame(框架)
    按钮区.pack(fill="x", padx=30)
    
    tk.Button(按钮区, text="Git官方网站", height=2,
              command=lambda: os.startfile(Git官网地址)).pack(fill="x", pady=5)
    tk.Button(按钮区, text="自动运行winget", height=2,
              command=运行winget安装).pack(fill="x", pady=5)
              
    链接标签 = tk.Label(
        按钮区, 
        text="（需要保证你的电脑上拥有winget，点此处打开下载网址）", 
        font=("微软雅黑", 9), 
        fg=普通蓝色, 
        cursor="hand2"
    )
    链接标签.pack(pady=(0, 10))
    链接标签.bind("<Button-1>", lambda e: os.startfile(Winget地址))

    根.mainloop()

class Git管理器应用:
    def __init__(self):
        self.根窗口 = tk.Tk()
        self.根窗口.title("Git_gui")
        设置全局字体()
        self.根窗口.bind_all("<Map>", lambda e: self.统一设置图标(e))
        设置样式(self.根窗口)
        居中窗口(self.根窗口, 480, 720)
        self.根窗口.minsize(420, 600)

        self.配置 = 加载配置()
        self.当前仓库 = None
        self.当前仓库名 = None
        self.提交按钮 = None
        self._滚动更新计划 = None
        try:
            self.根窗口.iconbitmap(资源路径("Git_gui.ico"))
        except Exception:
            pass

        self.构建界面()

        仓库列表 = self.配置.get("repositories", [])
        if 仓库列表:
            目标 = self.选出起始仓库(仓库列表)
            self.设置当前仓库(目标["path"], 目标["name"], 记录日志=False)
            self.恢复上次分支()
        else:
            self.刷新全部()

        self.根窗口.after(100, self.启动检查用户信息)

    def 选出起始仓库(self, 仓库列表):
        最后路径 = self.配置.get("settings", {}).get("last_repo_path", "")
        if 最后路径:
            规范 = os.path.normcase(os.path.normpath(最后路径))
            for 仓 in 仓库列表:
                if os.path.normcase(os.path.normpath(仓["path"])) == 规范:
                    return 仓
        return 仓库列表[0]

    def 恢复上次分支(self):
        if not self.当前仓库:
            return
        最后分支 = self.配置.get("settings", {}).get("last_branch", "")
        if not 最后分支:
            return
        if 最后分支 == self.获取当前分支():
            return
        if 最后分支 not in self.获取分支列表():
            return
        码, _, 错 = 运行git(["checkout", 最后分支], self.当前仓库)
        if 码 == 0:
            写日志(f"恢复上次分支: {最后分支}")
            self.刷新全部()
        else:
            写日志(f"恢复上次分支失败: {最后分支} -> {(错 or '').strip()}")

    def 保存当前状态(self):
        if not self.当前仓库:
            return
        try:
            if "settings" not in self.配置:
                self.配置["settings"] = {}
            self.配置["settings"]["last_repo_path"] = self.当前仓库
            self.配置["settings"]["last_branch"] = self.获取当前分支()
            保存配置(self.配置)
        except Exception:
            pass

    def 获取设置(self, 键, 默认值=True):
        值 = self.配置.get("settings", {}).get(键, 默认值)
        if isinstance(值, str):
            return 值.lower() == "true"
        return bool(值)

    def 统一设置图标(self, 事件):
        控件 = 事件.widget
        if isinstance(控件, tk.Toplevel):
            try:
                控件.iconbitmap(资源路径("Git_gui.ico"))
            except Exception:
                pass

    def 启动检查用户信息(self):
        if not 获取全局用户名() or not 获取全局邮箱():
            self.设置用户信息(首次启动=True)

    def 构建界面(self):
        for w in self.根窗口.winfo_children():
            if w.winfo_class() in ["Frame", "TNotebook"]:
                w.destroy()
                
        self.构建自定义菜单栏()

        self.选项卡组 = ttk.Notebook(self.根窗口)
        self.选项卡组.pack(fill="both", expand=True)

        self.Git选项卡 = tk.Frame(self.选项卡组)
        self.提交信息选项卡 = tk.Frame(self.选项卡组)
        self.运行日志选项卡 = tk.Frame(self.选项卡组)
        
        self.选项卡组.add(self.Git选项卡, text="Git")
        self.选项卡组.add(self.提交信息选项卡, text="Git 提交信息")
        
        if self.获取设置("显示运行日志", True):
            self.选项卡组.add(self.运行日志选项卡, text="运行日志")

        self.构建Git选项卡()
        self.构建提交信息选项卡()
        self.构建运行日志选项卡()

    def 构建自定义菜单栏(self):
        菜单栏容器 = tk.Frame(self.根窗口, bg="#f0f0f0", height=28)
        菜单栏容器.pack(fill="x", side="top")
        菜单栏容器.pack_propagate(False)

        文件标签 = tk.Label(菜单栏容器, text="文件", font=("微软雅黑", 10),
                          padx=14, bg="#f0f0f0", cursor="hand2")
        文件标签.pack(side="left", fill="y")
        文件标签.bind("<Button-1>", self._弹出文件菜单)

        设置标签 = tk.Label(菜单栏容器, text="设置", font=("微软雅黑", 10),
                          padx=14, bg="#f0f0f0", cursor="hand2")
        设置标签.pack(side="left", fill="y")
        设置标签.bind("<Button-1>", lambda e: self.显示设置())

        if self.获取设置("显示关于", True):
            关于标签 = tk.Label(菜单栏容器, text="关于", font=("微软雅黑", 10),
                              padx=14, bg="#f0f0f0", cursor="hand2")
            关于标签.pack(side="left", fill="y")
            关于标签.bind("<Button-1>", lambda e: self.显示关于())

        def 进入(e):
            e.widget.config(bg="#e0e0e0")

        def 离开(e):
            e.widget.config(bg="#f0f0f0")

        for 标签 in 菜单栏容器.winfo_children():
            标签.bind("<Enter>", 进入)
            标签.bind("<Leave>", 离开)

    def _弹出文件菜单(self, 事件):
        菜单 = tk.Menu(self.根窗口, tearoff=0, font=("微软雅黑", 10))
        菜单.add_command(label="添加/新建仓库", command=self.添加仓库操作)
        菜单.add_command(label="设置用户信息", command=lambda: self.设置用户信息(首次启动=False))
        菜单.add_command(label="编辑仓库名称", command=self.编辑仓库名称)
        菜单.add_command(label="删除仓库", command=self.删除仓库操作)
        try:
            菜单.tk_popup(事件.x_root, 事件.y_root)
        finally:
            菜单.grab_release()

    def 构建Git选项卡(self):
        顶栏 = tk.Frame(self.Git选项卡)
        顶栏.pack(fill="x", padx=10, pady=6)
        self.仓库选择框架 = tk.Frame(顶栏)
        self.仓库选择框架.pack(side="left")
        self.分支选择框架 = tk.Frame(顶栏)
        self.分支选择框架.pack(side="right")

        self.主区域 = tk.Frame(self.Git选项卡)
        self.主区域.pack(fill="both", expand=True, padx=10, pady=6)

        self.底部路径栏 = tk.Frame(self.Git选项卡)
        tk.Label(self.底部路径栏, text="路径：").pack(side="left")
        self.路径变量 = tk.StringVar()
        路径框 = tk.Entry(self.底部路径栏, textvariable=self.路径变量)
        路径框.pack(side="left", fill="x", expand=True, padx=5)
        路径框.bind("<Return>", lambda e: self.尝试添加仓库(self.路径变量.get().strip()))
        tk.Button(self.底部路径栏, text="浏览", width=8,
                  command=self.浏览仓库).pack(side="left")

    def 构建提交信息选项卡(self):
        列 = ("序号", "说明", "哈希", "日期", "时间")
        self.提交表格 = ttk.Treeview(self.提交信息选项卡, columns=列, show="headings")
        self.提交表格.heading("序号", text="提交序号")
        self.提交表格.heading("说明", text="提交说明")
        self.提交表格.heading("哈希", text="提交哈希")
        self.提交表格.heading("日期", text="日期")
        self.提交表格.heading("时间", text="时间")
        self.提交表格.column("序号", width=60, anchor="center")
        self.提交表格.column("说明", width=120)
        self.提交表格.column("哈希", width=70, anchor="center")
        self.提交表格.column("日期", width=80, anchor="center")
        self.提交表格.column("时间", width=70, anchor="center")
        滚动条 = ttk.Scrollbar(self.提交信息选项卡, orient="vertical",
                               command=self.提交表格.yview)
        self.提交表格.configure(yscrollcommand=滚动条.set)
        self.提交表格.pack(side="left", fill="both", expand=True,
                         padx=(10, 0), pady=10)
        滚动条.pack(side="right", fill="y", padx=(0, 10), pady=10)
        self.提交表格.tag_configure("分隔", background="#e0e0e0",
                                  font=("微软雅黑", 10, "bold"))

    def 构建运行日志选项卡(self):
        顶栏 = tk.Frame(self.运行日志选项卡)
        顶栏.pack(fill="x", padx=10, pady=6)
        
        tk.Button(顶栏, text="清除日志", width=10,
                  command=self.清除日志).pack(side="right", padx=(5, 0))
        tk.Button(顶栏, text="复制", width=10,
                  command=self.复制日志).pack(side="right")

        self.日志容器 = tk.Frame(self.运行日志选项卡)
        self.日志容器.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self.日志容器.grid_rowconfigure(0, weight=1)
        self.日志容器.grid_columnconfigure(0, weight=1)

        self.日志文本框 = tk.Text(self.日志容器, wrap="none", font=("微软雅黑", 10))
        self.日志文本框.grid(row=0, column=0, sticky="nsew")
        self.日志文本框.config(state="disabled")

        self.日志竖滚动 = ttk.Scrollbar(self.日志容器, orient="vertical",
                                     command=self.日志文本框.yview)
        self.日志横滚动 = ttk.Scrollbar(self.日志容器, orient="horizontal",
                                     command=self.日志文本框.xview)
        self.日志文本框.configure(
            yscrollcommand=self.日志竖滚动.set,
            xscrollcommand=self.日志横滚动.set
        )

        self.日志文本框.bind("<Configure>", lambda e: self.安排更新日志滚动条())

    def 安排更新日志滚动条(self):
        if self._滚动更新计划 is not None:
            try:
                self.根窗口.after_cancel(self._滚动更新计划)
            except Exception:
                pass
        self._滚动更新计划 = self.根窗口.after(80, self.真正更新日志滚动条)

    def 真正更新日志滚动条(self):
        self._滚动更新计划 = None
        try:
            self.日志文本框.update_idletasks()
            y_start, y_end = self.日志文本框.yview()
            if y_end - y_start >= 0.999:
                self.日志竖滚动.grid_remove()
            else:
                if not self.日志竖滚动.winfo_ismapped():
                    self.日志竖滚动.grid(row=0, column=1, sticky="ns")
            x_start, x_end = self.日志文本框.xview()
            if x_end - x_start >= 0.999:
                self.日志横滚动.grid_remove()
            else:
                if not self.日志横滚动.winfo_ismapped():
                    self.日志横滚动.grid(row=1, column=0, sticky="ew")
        except Exception:
            pass

    def 获取提交列表(self):
        if not self.当前仓库:
            return []
        返回码, 输出, _ = 运行git(
            ["log", "--pretty=format:%H%x1f%s%x1f%ci", "-n", "1000"],
            self.当前仓库
        )
        if 返回码 != 0:
            return []
        结果 = []
        for 行 in 输出.splitlines():
            if not 行.strip():
                continue
            部分 = 行.split("\x1f")
            if len(部分) < 3:
                continue
            哈希, 说明, 日期串 = 部分[0], 部分[1], 部分[2]
            try:
                时间 = datetime.datetime.strptime(日期串[:19], "%Y-%m-%d %H:%M:%S")
            except Exception:
                时间 = None
            结果.append({
                "hash": 哈希,
                "short_hash": 哈希[:7],
                "msg": 说明,
                "dt": 时间,
                "year": 时间.year if 时间 else None
            })
        return 结果

    def 获取当前分支(self):
        if not self.当前仓库:
            return ""
        码, 输出, _ = 运行git(["symbolic-ref", "--short", "HEAD"], self.当前仓库)
        if 码 == 0 and 输出.strip():
            return 输出.strip()
        码, 输出, _ = 运行git(["rev-parse", "--abbrev-ref", "HEAD"], self.当前仓库)
        if 码 != 0:
            return ""
        return 输出.strip()

    def 获取分支列表(self):
        if not self.当前仓库:
            return []
        码, 输出, _ = 运行git(
            ["branch", "--format=%(refname:short)"], self.当前仓库
        )
        分支 = []
        if 码 == 0:
            分支 = [b.strip() for b in 输出.splitlines() if b.strip()]
        if not 分支:
            当前 = self.获取当前分支()
            if 当前:
                return [当前]
        return 分支

    def 获取标签列表(self):
        if not self.当前仓库:
            return []
        返回码, 输出, _ = 运行git(
            ["for-each-ref", "--format=%(refname:short)", "refs/tags"],
            self.当前仓库
        )
        if 返回码 != 0:
            return []
        结果 = []
        for 名 in 输出.splitlines():
            名 = 名.strip()
            if not 名:
                continue
            码, 内容, _ = 运行git(
                ["log", "-1", "--format=%H%x1f%s", 名], self.当前仓库
            )
            if 码 != 0:
                continue
            部分 = 内容.strip().split("\x1f", 1)
            if len(部分) < 2:
                continue
            结果.append({"name": 名, "commit_hash": 部分[0], "msg": 部分[1]})
        return 结果

    def 检查暂存区(self):
        if not self.当前仓库:
            return False
        码, 输出, _ = 运行git(["status", "--porcelain"], self.当前仓库)
        if 码 != 0:
            return False
        for 行 in 输出.splitlines():
            if len(行) >= 2:
                X = 行[0]
                if X not in (" ", "?", "!"):
                    return True
        return False

    def 检查工作区修改(self):
        if not self.当前仓库:
            return False
        码, 输出, _ = 运行git(["status", "--porcelain"], self.当前仓库)
        return bool(输出.strip())

    def 提交总数(self):
        if not self.当前仓库:
            return 0
        码, 输出, _ = 运行git(["rev-list", "--count", "HEAD"], self.当前仓库)
        try:
            return int(输出.strip())
        except Exception:
            return 0

    def 默认提交说明(self):
        return f"第{self.提交总数() + 1}次提交"

    def 刷新全部(self):
        self.刷新仓库选择器()
        self.刷新分支选择器()
        self.刷新主区域()
        self.刷新提交表格()
        if self.获取设置("显示运行日志", True):
            self.刷新日志视图()

    def 刷新仓库选择器(self):
        for 子 in self.仓库选择框架.winfo_children():
            子.destroy()
        仓库列表 = self.配置.get("repositories", [])
        if not 仓库列表:
            tk.Label(self.仓库选择框架, text="仓库：",
                     font=("微软雅黑", 11)).pack(side="left")
            return
        if len(仓库列表) == 1:
            仓 = 仓库列表[0]
            tk.Label(self.仓库选择框架, text=f"仓库：{仓['name']}",
                     font=("微软雅黑", 11)).pack(side="left")
        else:
            tk.Label(self.仓库选择框架, text="仓库：",
                     font=("微软雅黑", 11)).pack(side="left")
            名称列表 = [仓["name"] for 仓 in 仓库列表]
            当前名 = next(
                (仓["name"] for 仓 in 仓库列表
                 if self.当前仓库 and
                 os.path.normpath(仓["path"]) == os.path.normpath(self.当前仓库)),
                名称列表[0]
            )
            变量 = tk.StringVar(value=当前名)
            下拉 = ttk.Combobox(self.仓库选择框架, textvariable=变量,
                              values=名称列表, state="readonly", width=18)
            下拉.pack(side="left")

            def 变化(event):
                选中 = 变量.get()
                目标 = next((仓 for 仓 in 仓库列表 if 仓["name"] == 选中), None)
                if 目标 and (not self.当前仓库 or
                            os.path.normpath(目标["path"]) != os.path.normpath(self.当前仓库)):
                    self.设置当前仓库(目标["path"], 目标["name"])
            下拉.bind("<<ComboboxSelected>>", 变化)

    def 刷新分支选择器(self):
        for 子 in self.分支选择框架.winfo_children():
            子.destroy()
        if not self.当前仓库:
            return
        分支列表 = self.获取分支列表()
        当前 = self.获取当前分支()
        if len(分支列表) <= 1:
            tk.Label(self.分支选择框架, text=f"分支：{当前}",
                     font=("微软雅黑", 11)).pack(side="right")
        else:
            tk.Label(self.分支选择框架, text="分支：",
                     font=("微软雅黑", 11)).pack(side="left")
            变量 = tk.StringVar(value=当前)
            下拉 = ttk.Combobox(self.分支选择框架, textvariable=变量,
                              values=分支列表, state="readonly", width=18)
            下拉.pack(side="right")
            下拉.bind("<<ComboboxSelected>>", lambda e: self.切换分支(变量.get()))

    def 刷新主区域(self):
        for 子 in self.主区域.winfo_children():
            子.destroy()

        if not self.当前仓库:
            tk.Label(self.主区域,
                     text='您暂时还没有仓库，点击"浏览"或填写路径添加/新建仓库',
                     font=("微软雅黑", 12), wraplength=400,
                     justify="center").pack(pady=60, padx=20)
            self.提交按钮 = None
        else:
            tk.Button(self.主区域, text="将当前更改提交至暂存区", height=2,
                      bg=普通蓝色, fg="white",
                      activebackground=深蓝色, activeforeground="white",
                      command=self.添加到暂存区).pack(fill="x", padx=20, pady=5)

            self.提交按钮 = tk.Button(self.主区域, text="提交更改", height=2,
                                      bg=普通蓝色, fg="white",
                                      activebackground=深蓝色, activeforeground="white",
                                      command=self.执行提交流程)
            self.提交按钮.pack(fill="x", padx=20, pady=5)

            if self.获取设置("显示_更改提交", True):
                tk.Button(self.主区域, text="更改提交", height=2,
                          command=self.显示更改提交菜单).pack(fill="x", padx=20, pady=5)
            if self.获取设置("显示_标签", True):
                tk.Button(self.主区域, text="标签", height=2,
                          command=self.显示标签菜单).pack(fill="x", padx=20, pady=5)
            if self.获取设置("显示_分支操作", True):
                tk.Button(self.主区域, text="分支操作", height=2,
                          command=self.显示分支菜单).pack(fill="x", padx=20, pady=5)
            if self.获取设置("显示_追踪", True):
                tk.Button(self.主区域, text="添加/取消追踪文件", height=2,
                          command=self.添加取消追踪文件).pack(fill="x", padx=20, pady=5)
            if self.获取设置("显示_查看差异", True):
                tk.Button(self.主区域, text="查看差异", height=2,
                          command=self.查看差异).pack(fill="x", padx=20, pady=5)
            if self.获取设置("显示_GitHub", False):
                tk.Button(self.主区域, text="Github操作", height=2,
                          bg="#24292e", fg="white", activebackground="#000000",
                          activeforeground="white",
                          command=self.显示GitHub操作).pack(fill="x", padx=20, pady=5)

            self.更新提交按钮状态()

        if self.当前仓库:
            self.底部路径栏.pack_forget()
        else:
            if not self.底部路径栏.winfo_ismapped():
                self.底部路径栏.pack(fill="x", padx=10, pady=6)

    def 更新提交按钮状态(self):
        if not self.提交按钮:
            return
        if self.检查暂存区():
            self.提交按钮.config(state="normal", bg=普通蓝色, fg="white")
        else:
            self.提交按钮.config(state="disabled", bg=禁用底色,
                                fg=禁用前景色, disabledforeground=禁用前景色)

    def 刷新提交表格(self):
        for 行 in self.提交表格.get_children():
            self.提交表格.delete(行)
        提交列表 = self.获取提交列表()
        今年 = datetime.datetime.now().year
        上一年 = None
        for 序, 提 in enumerate(提交列表):
            if 提["year"] != 上一年 and 提["year"] is not None:
                上一年 = 提["year"]
                if 上一年 != 今年:
                    self.提交表格.insert(
                        "", "end",
                        values=(f"{上一年} 年", "", "", "", ""),
                        tags=("分隔",)
                    )
            日期串 = 提["dt"].strftime("%Y-%m-%d") if 提["dt"] else ""
            时间串 = 提["dt"].strftime("%H:%M:%S") if 提["dt"] else ""
            self.提交表格.insert(
                "", "end",
                values=(序 + 1, 提["msg"], 提["short_hash"], 日期串, 时间串)
            )

    def 刷新日志视图(self):
        self.日志文本框.config(state="normal")
        self.日志文本框.delete("1.0", "end")
        路径 = os.path.join(日志目录, f"log_{今天字符串()}.txt")
        if os.path.exists(路径):
            try:
                with open(路径, "r", encoding="utf-8") as f:
                    self.日志文本框.insert("end", f.read())
            except Exception:
                pass
        self.日志文本框.config(state="disabled")
        self.安排更新日志滚动条()

    def 复制日志(self):
        内容 = self.日志文本框.get("1.0", "end-1c")
        self.根窗口.clipboard_clear()
        self.根窗口.clipboard_append(内容)

    def 清除日志(self):
        if not messagebox.askyesno("确认", "确定要清除当天的日志吗？\n（这不会影响历史日志）"):
            return
        路径 = os.path.join(日志目录, f"log_{今天字符串()}.txt")
        if os.path.exists(路径):
            try:
                with open(路径, "w", encoding="utf-8") as f:
                    pass
                self.刷新日志视图()
            except Exception as e:
                messagebox.showerror("错误", f"清除日志失败：{e}")

    def 编辑仓库名称(self):
        if not self.当前仓库:
            messagebox.showinfo("提示", "当前没有选中的仓库")
            return
        对话框 = tk.Toplevel(self.根窗口)
        对话框.title("编辑仓库名称")
        对话框.transient(self.根窗口)
        对话框.grab_set()
        对话框.resizable(False, False)

        tk.Label(对话框, text="请输入新的仓库名称（不会影响文件夹名称）：", font=("微软雅黑", 11)).pack(padx=20, pady=(20, 6))
        变量 = tk.StringVar(value=self.当前仓库名)
        输入框 = tk.Entry(对话框, textvariable=变量, width=36, font=("微软雅黑", 10))
        输入框.pack(padx=20, pady=6)
        输入框.focus()

        def 确认():
            新名 = 变量.get().strip()
            if not 新名:
                messagebox.showwarning("提示", "名称不能为空", parent=对话框)
                return
            
            for 仓 in self.配置["repositories"]:
                if os.path.normpath(仓["path"]) == os.path.normpath(self.当前仓库):
                    仓["name"] = 新名
                    break
            保存配置(self.配置)
            写日志(f"编辑仓库名称: {self.当前仓库名} -> {新名}")
            self.当前仓库名 = 新名
            对话框.destroy()
            self.刷新全部()

        按钮区 = tk.Frame(对话框)
        按钮区.pack(pady=15)
        tk.Button(按钮区, text="取消", width=10, command=对话框.destroy).pack(side="left", padx=10)
        tk.Button(按钮区, text="确认", width=10, bg=普通蓝色, fg="white", command=确认).pack(side="left", padx=10)

        居中窗口(对话框)
        self.根窗口.wait_window(对话框)

    def 显示设置(self):
        对话框 = tk.Toplevel(self.根窗口)
        对话框.title("设置")
        对话框.transient(self.根窗口)
        对话框.grab_set()
        对话框.resizable(False, False)

        选项卡 = ttk.Notebook(对话框)
        选项卡.pack(padx=15, pady=15, fill="both", expand=True)

        常规页 = tk.Frame(选项卡)
        可见页 = tk.Frame(选项卡)
        选项卡.add(常规页, text="常规设置")
        选项卡.add(可见页, text="可见性")

        常规页.pack_propagate(False)
        常规页.config(width=380, height=220)
        
        v_double_confirm = tk.BooleanVar(value=self.获取设置("高危双重提示", True))
        ttk.Checkbutton(常规页, text="执行高危操作进行双重提示", variable=v_double_confirm).pack(anchor="w", padx=20, pady=5)

        v_skip_stage = tk.BooleanVar(value=self.获取设置("关闭暂存提示", False))
        ttk.Checkbutton(常规页, text="关闭暂存时的确认提示", variable=v_skip_stage).pack(anchor="w", padx=20, pady=5)

        def 导出配置():
            文件路径 = filedialog.asksaveasfilename(
                parent=对话框,
                title="导出配置文件",
                defaultextension=".json",
                initialfile="config.json",
                filetypes=[("JSON 文件", "*.json")]
            )
            if 文件路径:
                try:
                    shutil.copyfile(配置文件路径, 文件路径)
                    messagebox.showinfo("成功", "配置文件导出成功", parent=对话框)
                except Exception as e:
                    messagebox.showerror("错误", f"导出失败：{e}", parent=对话框)

        tk.Button(常规页, text="导出配置", width=15, command=导出配置).pack(pady=15)

        可见页.pack_propagate(False)
        可见页.config(width=380, height=450)

        frame_btn = tk.LabelFrame(可见页, text="页面按钮可见性", font=("微软雅黑", 10))
        frame_btn.pack(fill="x", padx=15, pady=10)
        
        v_btn_change = tk.BooleanVar(value=self.获取设置("显示_更改提交", True))
        v_btn_tag = tk.BooleanVar(value=self.获取设置("显示_标签", True))
        v_btn_branch = tk.BooleanVar(value=self.获取设置("显示_分支操作", True))
        v_btn_track = tk.BooleanVar(value=self.获取设置("显示_追踪", True))
        v_btn_diff = tk.BooleanVar(value=self.获取设置("显示_查看差异", True))
        v_btn_github = tk.BooleanVar(value=self.获取设置("显示_GitHub", False))

        ttk.Checkbutton(frame_btn, text="更改提交", variable=v_btn_change).pack(anchor="w", padx=10, pady=2)
        ttk.Checkbutton(frame_btn, text="标签", variable=v_btn_tag).pack(anchor="w", padx=10, pady=2)
        ttk.Checkbutton(frame_btn, text="分支操作", variable=v_btn_branch).pack(anchor="w", padx=10, pady=2)
        ttk.Checkbutton(frame_btn, text="添加取消追踪文件", variable=v_btn_track).pack(anchor="w", padx=10, pady=2)
        ttk.Checkbutton(frame_btn, text="查看差异", variable=v_btn_diff).pack(anchor="w", padx=10, pady=2)
        ttk.Checkbutton(frame_btn, text="Github操作", variable=v_btn_github).pack(anchor="w", padx=10, pady=2)

        frame_page = tk.LabelFrame(可见页, text="页面可见性", font=("微软雅黑", 10))
        frame_page.pack(fill="x", padx=15, pady=10)
        
        v_page_about = tk.BooleanVar(value=self.获取设置("显示关于", True))
        v_page_log = tk.BooleanVar(value=self.获取设置("显示运行日志", True))

        ttk.Checkbutton(frame_page, text='显示"关于"菜单选项', variable=v_page_about).pack(anchor="w", padx=10, pady=2)
        ttk.Checkbutton(frame_page, text='显示"运行日志"选项卡', variable=v_page_log).pack(anchor="w", padx=10, pady=2)

        def 保存设置():
            self.配置["settings"]["高危双重提示"] = bool(v_double_confirm.get())
            self.配置["settings"]["关闭暂存提示"] = bool(v_skip_stage.get())
            self.配置["settings"]["显示_更改提交"] = bool(v_btn_change.get())
            self.配置["settings"]["显示_标签"] = bool(v_btn_tag.get())
            self.配置["settings"]["显示_分支操作"] = bool(v_btn_branch.get())
            self.配置["settings"]["显示_追踪"] = bool(v_btn_track.get())
            self.配置["settings"]["显示_查看差异"] = bool(v_btn_diff.get())
            self.配置["settings"]["显示_GitHub"] = bool(v_btn_github.get())
            self.配置["settings"]["显示关于"] = bool(v_page_about.get())
            self.配置["settings"]["显示运行日志"] = bool(v_page_log.get())
            
            保存配置(self.配置)
            对话框.destroy()
            self.构建界面()  
            self.刷新全部()

        底部区 = tk.Frame(对话框)
        底部区.pack(pady=(0, 15))
        tk.Button(底部区, text="取消", width=10, command=对话框.destroy).pack(side="left", padx=10)
        tk.Button(底部区, text="保存", width=10, bg=普通蓝色, fg="white", command=保存设置).pack(side="left", padx=10)

        居中窗口(对话框)
        self.根窗口.wait_window(对话框)

    def 设置用户信息(self, 首次启动=False):
        对话框 = tk.Toplevel(self.根窗口)
        对话框.title("设置用户信息（以后可在文件菜单中修改）")
        对话框.transient(self.根窗口)
        对话框.grab_set()
        对话框.resizable(False, False)

        框 = tk.Frame(对话框)
        框.pack(padx=20, pady=20)

        当前用户 = 获取全局用户名()
        当前邮箱 = 获取全局邮箱()

        变量用户 = tk.StringVar(value=当前用户)
        变量邮箱 = tk.StringVar(value=当前邮箱)

        tk.Label(框, text="用户名：", font=("微软雅黑", 11)).grid(row=0, column=0, sticky="e", pady=5)
        输入用户 = tk.Entry(框, textvariable=变量用户, width=25, font=("微软雅黑", 10))
        输入用户.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(框, text="邮箱：", font=("微软雅黑", 11)).grid(row=1, column=0, sticky="e", pady=5)
        输入邮箱 = tk.Entry(框, textvariable=变量邮箱, width=25, font=("微软雅黑", 10))
        输入邮箱.grid(row=1, column=1, padx=10, pady=5)

        按钮区 = tk.Frame(框)
        按钮区.grid(row=0, column=2, rowspan=2, padx=10)

        def 保存():
            u = 变量用户.get().strip()
            e = 变量邮箱.get().strip()
            if not u or not e:
                messagebox.showwarning("警告", "用户名和邮箱不能为空", parent=对话框)
                return
            
            运行git(["config", "--global", "user.name", u])
            运行git(["config", "--global", "user.email", e])
            写日志(f"设置全局用户信息: {u} ({e})")
            对话框.destroy()

        tk.Button(按钮区, text="确认", width=8, font=("微软雅黑", 10), command=保存).pack(pady=(5, 2))
        tk.Button(按钮区, text="取消", width=8, font=("微软雅黑", 10), command=对话框.destroy).pack(pady=(2, 5))

        输入用户.focus()
        居中窗口(对话框)
        self.根窗口.wait_window(对话框)

    def 设置当前仓库(self, 路径, 名称, 记录日志=True):
        self.当前仓库 = 路径
        self.当前仓库名 = 名称
        self.路径变量.set(路径)
        if 记录日志:
            写日志(f"切换到仓库: {名称} ({路径})")
        self.刷新全部()
        self.保存当前状态()

    def 浏览仓库(self):
        路径 = filedialog.askdirectory()
        if 路径:
            self.路径变量.set(路径)
            self.尝试添加仓库(路径)

    def 添加仓库操作(self):
        self.浏览仓库()

    def 删除仓库操作(self):
        仓库列表 = self.配置.get("repositories", [])
        if not 仓库列表:
            messagebox.showinfo("提示", "当前没有可删除的仓库")
            return

        if len(仓库列表) == 1:
            目标 = 仓库列表[0]
            if not messagebox.askyesno(
                    "确认",
                    "这将会删除这个仓库，您确定要执行吗（不会影响仓库内文件）"):
                return
        else:
            对话框 = tk.Toplevel(self.根窗口)
            对话框.title("删除仓库")
            对话框.transient(self.根窗口)
            对话框.grab_set()
            对话框.resizable(False, False)
            tk.Label(对话框, text="请选择要删除的仓库：",
                     font=("微软雅黑", 11)).pack(padx=20, pady=(20, 6), anchor="w")
            名称列表 = [仓["name"] for 仓 in 仓库列表]
            变量 = tk.StringVar(value=名称列表[0])
            ttk.Combobox(对话框, textvariable=变量, values=名称列表,
                         state="readonly", width=36).pack(padx=20, pady=6)
            结果 = {"名称": None}

            def 确认():
                结果["名称"] = 变量.get()
                对话框.destroy()

            按钮区 = tk.Frame(对话框)
            按钮区.pack(pady=12)
            tk.Button(按钮区, text="取消", width=10,
                      command=对话框.destroy).pack(side="left", padx=8)
            tk.Button(按钮区, text="确认", width=10, bg=红色, fg="white",
                      activebackground=深红色, activeforeground="white",
                      command=确认).pack(side="left", padx=8)
            居中窗口(对话框)
            self.根窗口.wait_window(对话框)

            if not 结果["名称"]:
                return
            目标 = next((仓 for 仓 in 仓库列表 if 仓["name"] == 结果["名称"]), None)
            if not 目标:
                return
            if not messagebox.askyesno(
                    "确认",
                    "这将会删除这个仓库，您确定要执行吗（不会影响仓库内文件）"):
                return

        目标路径 = 目标["path"]
        目标名 = 目标["name"]
        新列表 = [仓 for 仓 in self.配置["repositories"]
                 if os.path.normpath(仓["path"]) != os.path.normpath(目标路径)]
        self.配置["repositories"] = 新列表
        保存配置(self.配置)
        写日志(f"删除仓库记录: {目标名} ({目标路径})")

        if self.当前仓库 and os.path.normpath(self.当前仓库) == os.path.normpath(目标路径):
            if 新列表:
                self.设置当前仓库(新列表[0]["path"], 新列表[0]["name"], 记录日志=False)
            else:
                self.当前仓库 = None
                self.当前仓库名 = None
                self.路径变量.set("")
                self.刷新全部()

    def 尝试添加仓库(self, 路径):
        if not 路径:
            return
        if not os.path.isdir(路径):
            messagebox.showerror("错误", "路径不存在或不是文件夹")
            return
        for 仓 in self.配置["repositories"]:
            if os.path.normpath(仓["path"]) == os.path.normpath(路径):
                self.设置当前仓库(仓["path"], 仓["name"])
                return
        if not os.path.exists(os.path.join(路径, ".git")):
            if not messagebox.askyesno(
                    "提示", "这个文件夹还不是一个仓库，确定要将其初始化为仓库吗"):
                return
            码, _, 错 = 运行git(["init"], 路径)
            if 码 != 0:
                messagebox.showerror("错误", f"初始化失败：\n{错}")
                return
            写日志(f"初始化仓库: {路径}")
        名称 = self.询问仓库名称(路径)
        if 名称 is None:
            return
        self.配置["repositories"].append({"path": 路径, "name": 名称})
        保存配置(self.配置)
        写日志(f"添加仓库: {路径} (名称: {名称})")
        self.设置当前仓库(路径, 名称, 记录日志=False)

    def 询问仓库名称(self, 路径):
        对话框 = tk.Toplevel(self.根窗口)
        对话框.title("命名仓库")
        对话框.transient(self.根窗口)
        对话框.grab_set()
        对话框.resizable(False, False)
        tk.Label(对话框, text="您要为此仓库命名吗（这不会影响文件夹名称）",
                 font=("微软雅黑", 11), wraplength=380,
                 justify="center").pack(padx=20, pady=20)
        按钮区 = tk.Frame(对话框)
        按钮区.pack(fill="x", padx=20, pady=(0, 15))
        结果 = {"名称": None}

        def 命名():
            名字 = self.询问文本("命名仓库", "请输入仓库名称：")
            if 名字:
                结果["名称"] = 名字
                对话框.destroy()

        def 跳过():
            结果["名称"] = os.path.basename(os.path.normpath(路径))
            对话框.destroy()

        tk.Button(按钮区, text="跳过", width=10, command=跳过).pack(side="right", padx=6)
        tk.Button(按钮区, text="命名", width=10, command=命名).pack(side="right", padx=6)
        居中窗口(对话框)
        self.根窗口.wait_window(对话框)
        return 结果["名称"]

    def 询问文本(self, 标题, 提示):
        对话框 = tk.Toplevel(self.根窗口)
        对话框.title(标题)
        对话框.transient(self.根窗口)
        对话框.grab_set()
        对话框.resizable(False, False)
        tk.Label(对话框, text=提示, font=("微软雅黑", 11)).pack(
            padx=20, pady=(20, 8), anchor="w")
        变量 = tk.StringVar()
        输入框 = tk.Entry(对话框, textvariable=变量, width=40)
        输入框.pack(padx=20, pady=8)
        输入框.focus()
        结果 = {"值": None}

        def 确认():
            值 = 变量.get().strip()
            if 值:
                结果["值"] = 值
            对话框.destroy()

        按钮区 = tk.Frame(对话框)
        按钮区.pack(pady=12)
        tk.Button(按钮区, text="取消", width=10,
                  command=对话框.destroy).pack(side="left", padx=8)
        tk.Button(按钮区, text="确认", width=10,
                  command=确认).pack(side="left", padx=8)
        居中窗口(对话框)
        self.根窗口.wait_window(对话框)
        return 结果["值"]

    def 显示关于(self):
        对话框 = tk.Toplevel(self.根窗口)
        对话框.title("关于")
        对话框.transient(self.根窗口)
        对话框.grab_set()
        对话框.resizable(False, False)
        tk.Label(对话框,
                 text="git图形化管理界面\n让git更易用\nv3.3\nBy：散冰",
                 font=("微软雅黑", 13), justify="center").pack(padx=50, pady=30)
        tk.Button(对话框, text="确定", width=10,
                  command=对话框.destroy).pack(pady=(0, 20))
        居中窗口(对话框)
        self.根窗口.wait_window(对话框)

    def 选择提交对话框(self, 标题):
        提交列表 = self.获取提交列表()
        if not 提交列表:
            messagebox.showinfo("提示", "当前仓库没有任何提交")
            return None
        对话框 = tk.Toplevel(self.根窗口)
        对话框.title(标题)
        对话框.transient(self.根窗口)
        对话框.grab_set()
        对话框.resizable(False, False)

        选项 = []
        for 序, 提 in enumerate(提交列表):
            if 序 == 0:
                选项.append(f"最近一次提交（{提['msg']}）")
            else:
                选项.append(f"{提['msg']}  ({提['short_hash']})")

        tk.Label(对话框, text="请选择提交：",
                 font=("微软雅黑", 11)).pack(padx=20, pady=(20, 6), anchor="w")
        变量 = tk.StringVar(value=选项[0])
        ttk.Combobox(对话框, textvariable=变量, values=选项,
                     state="readonly", width=48).pack(padx=20, pady=6)
        结果 = {"序号": None}

        def 确认():
            结果["序号"] = 选项.index(变量.get())
            对话框.destroy()

        按钮区 = tk.Frame(对话框)
        按钮区.pack(pady=12)
        tk.Button(按钮区, text="取消", width=10,
                  command=对话框.destroy).pack(side="left", padx=8)
        tk.Button(按钮区, text="确认", width=10,
                  command=确认).pack(side="left", padx=8)
        居中窗口(对话框)
        self.根窗口.wait_window(对话框)
        return 结果["序号"]

    def 添加到暂存区(self):
        if not self.当前仓库:
            return

        if not self.获取设置("关闭暂存提示", True):
            if not messagebox.askyesno("确认", "确认要将当前所有更改添加至暂存区吗？"):
                return
                
        码, _, 错 = 运行git(["add", "-A"], self.当前仓库)
        if 码 != 0:
            messagebox.showerror("错误", f"添加失败：\n{错}")
        else:
            写日志("将当前更改提交至暂存区")
        self.刷新全部()

    def 执行提交流程(self):
        if not self.当前仓库 or not self.检查暂存区():
            return
        对话框 = tk.Toplevel(self.根窗口)
        对话框.title("提交更改")
        对话框.transient(self.根窗口)
        对话框.grab_set()
        对话框.resizable(False, False)

        tk.Label(对话框, text="请输入提交说明：",
                 font=("微软雅黑", 11)).pack(padx=20, pady=(20, 6), anchor="w")
        变量 = tk.StringVar()
        输入框 = tk.Entry(对话框, textvariable=变量, width=44)
        输入框.pack(padx=20, pady=6)
        输入框.focus()
        结果 = {"说明": None}

        def 确认():
            说明 = 变量.get().strip() or self.默认提交说明()
            结果["说明"] = 说明
            对话框.destroy()

        def 跳过():
            结果["说明"] = self.默认提交说明()
            对话框.destroy()

        按钮区 = tk.Frame(对话框)
        按钮区.pack(fill="x", padx=20, pady=12)
        tk.Button(按钮区, text="跳过", width=10,
                  command=跳过).pack(side="right", padx=6)
        tk.Button(按钮区, text="确认", width=10,
                  command=确认).pack(side="right", padx=6)
        居中窗口(对话框)
        self.根窗口.wait_window(对话框)

        if 结果["说明"] is None:
            return
        if not self.获取设置("关闭暂存提示", True):
            if not messagebox.askyesno("确认", "确认要执行提交吗"):
                return

        if self.提交按钮:
            try:
                self.提交按钮.config(state="disabled")
            except Exception:
                pass

        def 后台():
            码, _, 错 = 运行git(["commit", "-m", 结果["说明"]], self.当前仓库, 超时=300)
            def 完成():
                if 码 != 0:
                    messagebox.showerror("错误", f"提交失败：\n{错}")
                else:
                    写日志(f"提交更改: {结果['说明']}")
                self.刷新全部()
            try:
                self.根窗口.after(0, 完成)
            except Exception:
                pass

        threading.Thread(target=后台, daemon=True).start()

    def 显示更改提交菜单(self):
        if not self.当前仓库:
            return
        对话框 = tk.Toplevel(self.根窗口)
        对话框.title("更改提交")
        对话框.transient(self.根窗口)
        对话框.grab_set()
        对话框.resizable(False, False)

        def 动作(类型):
            对话框.destroy()
            self.更改提交动作(类型)

        tk.Button(对话框, text="创建反向提交", height=2,
                  command=lambda: 动作("revert")).pack(fill="x", padx=20, pady=5)
        tk.Button(对话框, text="撤销提交，保留修改至暂存区", height=2,
                  command=lambda: 动作("soft")).pack(fill="x", padx=20, pady=5)
        tk.Button(对话框, text="撤销提交，保留修改至工作区", height=2,
                  command=lambda: 动作("mixed")).pack(fill="x", padx=20, pady=5)
        tk.Button(对话框, text="撤销提交，丢弃所有修改", height=2,
                  bg=红色, fg="white", activebackground=深红色,
                  activeforeground="white",
                  command=lambda: 动作("hard_discard")).pack(fill="x", padx=20, pady=5)
        居中窗口(对话框)

    def 更改提交动作(self, 类型):
        if not self.当前仓库:
            return
        if 类型 == "hard_discard":
            if not self.获取提交列表():
                messagebox.showinfo("提示", "当前仓库没有任何提交")
                return
            if self.提交总数() <= 1:
                messagebox.showinfo("提示", "当前仓库只有一次提交，无法向前撤销（找不到上一次提交）")
                return
            if not messagebox.askyesno(
                    "确认",
                    "这将会永久删除最近一次提交 并且没有任何保留，您确定要执行吗"):
                return
            if self.获取设置("高危双重提示", True):
                if not messagebox.askyesno("二次确认", "此操作不可逆，确认要丢弃所有修改吗？"):
                    return
            码, _, 错 = 运行git(["reset", "--hard", "HEAD~1"], self.当前仓库)
            if 码 != 0:
                messagebox.showerror("错误", f"操作失败：\n{错}")
            else:
                写日志("撤销提交(丢弃所有修改): 最近一次提交")
            self.刷新全部()
            return

        序号 = self.选择提交对话框("请选择提交")
        if 序号 is None:
            return
        提交列表 = self.获取提交列表()
        if 序号 >= len(提交列表):
            return
        目标 = 提交列表[序号]
        哈希 = 目标["hash"]

        if 类型 == "revert":
            提示 = f"此操作将会为提交 {目标['short_hash']} 创建一个反向提交，您确定要执行吗"
        elif 类型 == "soft":
            提示 = f"此操作将会撤销至提交 {目标['short_hash']}，修改保留在暂存区，您确定要执行吗"
        elif 类型 == "mixed":
            提示 = f"此操作将会撤销至提交 {目标['short_hash']}，修改保留在工作区，您确定要执行吗"
        else:
            return

        if not messagebox.askyesno("确认", 提示):
            return

        if 类型 == "revert":
            码, _, 错 = 运行git(["revert", "--no-edit", 哈希], self.当前仓库)
        elif 类型 == "soft":
            码, _, 错 = 运行git(["reset", "--soft", 哈希], self.当前仓库)
        else:
            码, _, 错 = 运行git(["reset", "--mixed", 哈希], self.当前仓库)

        if 码 != 0:
            messagebox.showerror("错误", f"操作失败：\n{错}")
        else:
            写日志(f"更改提交[{类型}]: -> {目标['short_hash']}")
        self.刷新全部()

    def 显示标签菜单(self):
        if not self.当前仓库:
            return
        对话框 = tk.Toplevel(self.根窗口)
        对话框.title("标签")
        对话框.transient(self.根窗口)
        对话框.grab_set()
        对话框.resizable(False, False)

        def 动作(函数):
            对话框.destroy()
            函数()

        tk.Button(对话框, text="查看标签", height=2,
                  command=lambda: 动作(self.查看标签)).pack(fill="x", padx=20, pady=5)
        tk.Button(对话框, text="创建标签", height=2,
                  command=lambda: 动作(self.创建标签)).pack(fill="x", padx=20, pady=5)
        tk.Button(对话框, text="添加附注标签", height=2,
                  command=lambda: 动作(self.创建附注标签)).pack(fill="x", padx=20, pady=5)
        tk.Button(对话框, text="删除标签", height=2,
                  bg=红色, fg="white", activebackground=深红色,
                  activeforeground="white",
                  command=lambda: 动作(self.删除标签)).pack(fill="x", padx=20, pady=5)
        居中窗口(对话框)

    def 查看标签(self):
        对话框 = tk.Toplevel(self.根窗口)
        对话框.title("查看标签")
        对话框.resizable(False, False)
        列 = ("标签", "说明", "哈希", "序号")
        表格 = ttk.Treeview(对话框, columns=列, show="headings")
        表格.heading("标签", text="标签")
        表格.heading("说明", text="提交说明")
        表格.heading("哈希", text="提交哈希")
        表格.heading("序号", text="提交序号")
        表格.column("标签", width=160)
        表格.column("说明", width=320)
        表格.column("哈希", width=100, anchor="center")
        表格.column("序号", width=80, anchor="center")
        滚动条 = ttk.Scrollbar(对话框, orient="vertical", command=表格.yview)
        表格.configure(yscrollcommand=滚动条.set)
        表格.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        滚动条.pack(side="right", fill="y", padx=(0, 10), pady=10)

        标签列表 = self.获取标签列表()
        提交列表 = self.获取提交列表()
        哈希到序号 = {提["hash"]: 序 + 1 for 序, 提 in enumerate(提交列表)}
        for 标 in 标签列表:
            表格.insert("", "end", values=(
                标["name"], 标["msg"], 标["commit_hash"][:7],
                哈希到序号.get(标["commit_hash"], "")
            ))
        居中窗口(对话框, 800, 500)

    def 创建标签(self):
        序号 = self.选择提交对话框("创建标签 - 选择提交")
        if 序号 is None:
            return
        提交列表 = self.获取提交列表()
        目标 = 提交列表[序号]
        名称 = self.询问文本("创建标签", "请输入标签名：")
        if not 名称:
            return
        码, _, 错 = 运行git(["tag", 名称, 目标["hash"]], self.当前仓库)
        if 码 != 0:
            messagebox.showerror("错误", f"创建失败：\n{错}")
        else:
            写日志(f"创建标签: {名称} -> {目标['short_hash']}")
        self.刷新全部()

    def 创建附注标签(self):
        序号 = self.选择提交对话框("添加附注标签 - 选择提交")
        if 序号 is None:
            return
        提交列表 = self.获取提交列表()
        目标 = 提交列表[序号]
        名称 = self.询问文本("添加附注标签", "请输入标签名：")
        if not 名称:
            return
        码, _, 错 = 运行git(
            ["tag", "-a", 名称, 目标["hash"], "-m", 名称], self.当前仓库)
        if 码 != 0:
            messagebox.showerror("错误", f"创建失败：\n{错}")
        else:
            写日志(f"添加附注标签: {名称} -> {目标['short_hash']}")
        self.刷新全部()

    def 删除标签(self):
        标签列表 = self.获取标签列表()
        if not 标签列表:
            messagebox.showinfo("提示", "当前没有任何标签")
            return
        对话框 = tk.Toplevel(self.根窗口)
        对话框.title("删除标签")
        对话框.transient(self.根窗口)
        对话框.grab_set()
        对话框.resizable(False, False)
        tk.Label(对话框, text="请选择要删除的标签：",
                 font=("微软雅黑", 11)).pack(padx=20, pady=(20, 6), anchor="w")
        名称列表 = [标["name"] for 标 in 标签列表]
        变量 = tk.StringVar(value=名称列表[0])
        ttk.Combobox(对话框, textvariable=变量, values=名称列表,
                     state="readonly", width=36).pack(padx=20, pady=6)
        结果 = {"名称": None}

        def 确认():
            结果["名称"] = 变量.get()
            对话框.destroy()

        按钮区 = tk.Frame(对话框)
        按钮区.pack(pady=12)
        tk.Button(按钮区, text="取消", width=10,
                  command=对话框.destroy).pack(side="left", padx=8)
        tk.Button(按钮区, text="确认", width=10, bg=红色, fg="white",
                  activebackground=深红色, activeforeground="white",
                  command=确认).pack(side="left", padx=8)
        居中窗口(对话框)
        self.根窗口.wait_window(对话框)

        if not 结果["名称"]:
            return
        if not messagebox.askyesno(
                "确认", f"确定要删除标签 {结果['名称']} 吗？此操作不可逆"):
            return
        if self.获取设置("高危双重提示", True):
            if not messagebox.askyesno("二次确认", "真的要删除该标签吗？不可恢复！"):
                return
        码, _, 错 = 运行git(["tag", "-d", 结果["名称"]], self.当前仓库)
        if 码 != 0:
            messagebox.showerror("错误", f"删除失败：\n{错}")
        else:
            写日志(f"删除标签: {结果['名称']}")
        self.刷新全部()

    def 显示分支菜单(self):
        if not self.当前仓库:
            return
        对话框 = tk.Toplevel(self.根窗口)
        对话框.title("分支操作")
        对话框.transient(self.根窗口)
        对话框.grab_set()
        对话框.resizable(False, False)
        tk.Label(对话框,
                 text="如果你需要查看或切换分支，可以在主界面的右上角进行更改",
                 font=("微软雅黑", 10), fg="gray", wraplength=380,
                 justify="center").pack(padx=20, pady=(15, 8))

        def 动作(函数):
            对话框.destroy()
            函数()

        tk.Button(对话框, text="创建新分支", height=2,
                  command=lambda: 动作(self.创建分支)).pack(fill="x", padx=20, pady=5)
        tk.Button(对话框, text="重命名分支", height=2,
                  command=lambda: 动作(self.重命名分支)).pack(fill="x", padx=20, pady=5)
        tk.Button(对话框, text="合并分支到其它分支", height=2,
                  command=lambda: 动作(self.合并分支)).pack(fill="x", padx=20, pady=5)
        tk.Button(对话框, text="删除分支", height=2,
                  bg=红色, fg="white", activebackground=深红色,
                  activeforeground="white",
                  command=lambda: 动作(self.删除分支)).pack(fill="x", padx=20, pady=5)
        居中窗口(对话框)

    def 创建分支(self):
        序号 = self.选择提交对话框("创建新分支 - 选择提交")
        if 序号 is None:
            return
        提交列表 = self.获取提交列表()
        目标 = 提交列表[序号]
        名称 = self.询问文本("创建新分支", "请输入分支名：")
        if not 名称:
            return
        码, _, 错 = 运行git(["branch", 名称, 目标["hash"]], self.当前仓库)
        if 码 != 0:
            messagebox.showerror("错误", f"创建失败：\n{错}")
        else:
            写日志(f"创建分支: {名称} -> {目标['short_hash']}")
        self.刷新全部()

    def 重命名分支(self):
        分支列表 = self.获取分支列表()
        if not 分支列表:
            return
        对话框 = tk.Toplevel(self.根窗口)
        对话框.title("重命名分支")
        对话框.transient(self.根窗口)
        对话框.grab_set()
        对话框.resizable(False, False)
        
        tk.Label(对话框, text="请选择要重命名的分支：", font=("微软雅黑", 11)).pack(padx=20, pady=(20, 6), anchor="w")
        变量 = tk.StringVar(value=分支列表[0])
        ttk.Combobox(对话框, textvariable=变量, values=分支列表, state="readonly", width=36).pack(padx=20, pady=6)
        
        tk.Label(对话框, text="请输入新分支名：", font=("微软雅黑", 11)).pack(padx=20, pady=(10, 6), anchor="w")
        新名变量 = tk.StringVar()
        tk.Entry(对话框, textvariable=新名变量, width=38, font=("微软雅黑", 10)).pack(padx=20, pady=6)

        结果 = {"旧名": None, "新名": None}
        def 确认():
            旧 = 变量.get()
            新 = 新名变量.get().strip()
            if not 新:
                messagebox.showwarning("提示", "新分支名不能为空", parent=对话框)
                return
            if 旧 == 新:
                messagebox.showwarning("提示", "新名与旧名相同", parent=对话框)
                return
            结果["旧名"] = 旧
            结果["新名"] = 新
            对话框.destroy()

        按钮区 = tk.Frame(对话框)
        按钮区.pack(pady=15)
        tk.Button(按钮区, text="取消", width=10, command=对话框.destroy).pack(side="left", padx=8)
        tk.Button(按钮区, text="确认", width=10, command=确认).pack(side="left", padx=8)
        居中窗口(对话框)
        self.根窗口.wait_window(对话框)

        if not 结果["旧名"]:
            return
        码, _, 错 = 运行git(["branch", "-m", 结果["旧名"], 结果["新名"]], self.当前仓库)
        if 码 != 0:
            messagebox.showerror("错误", f"重命名失败：\n{错}")
        else:
            写日志(f"重命名分支: {结果['旧名']} -> {结果['新名']}")
        self.刷新全部()

    def 合并分支(self):
        分支列表 = self.获取分支列表()
        if len(分支列表) < 2:
            messagebox.showinfo("提示", "至少需要两个分支才能合并")
            return
        对话框 = tk.Toplevel(self.根窗口)
        对话框.title("合并分支")
        对话框.transient(self.根窗口)
        对话框.grab_set()
        对话框.resizable(False, False)

        行 = tk.Frame(对话框)
        行.pack(padx=20, pady=20)
        左 = tk.Frame(行)
        左.pack(side="left", padx=10)
        tk.Label(左, text="将：").pack(anchor="w")
        源变量 = tk.StringVar(value=分支列表[0])
        ttk.Combobox(左, textvariable=源变量, values=分支列表,
                     state="readonly", width=18).pack()
        右 = tk.Frame(行)
        右.pack(side="left", padx=10)
        tk.Label(右, text="合并到：").pack(anchor="w")
        目标变量 = tk.StringVar(value=分支列表[0])
        ttk.Combobox(右, textvariable=目标变量, values=分支列表,
                     state="readonly", width=18).pack()

        结果 = {"确定": False}

        def 确认():
            结果["确定"] = True
            对话框.destroy()

        按钮区 = tk.Frame(对话框)
        按钮区.pack(pady=12)
        tk.Button(按钮区, text="取消", width=10,
                  command=对话框.destroy).pack(side="left", padx=8)
        tk.Button(按钮区, text="确认", width=10,
                  command=确认).pack(side="left", padx=8)
        居中窗口(对话框)
        self.根窗口.wait_window(对话框)

        if not 结果["确定"]:
            return
        源 = 源变量.get()
        目标 = 目标变量.get()
        if 源 == 目标:
            messagebox.showwarning("警告", "源分支和目标分支不能相同")
            return
        码, _, 错 = 运行git(["checkout", 目标], self.当前仓库)
        if 码 != 0:
            messagebox.showerror("错误", f"切换目标分支失败：\n{错}")
            return
        码, _, 错 = 运行git(["merge", 源], self.当前仓库)
        if 码 != 0:
            messagebox.showerror(
                "合并失败",
                f"合并过程中出现冲突或错误：\n{错}\n\n请处理冲突后重试，或重新选择分支。")
        else:
            写日志(f"合并分支: {源} -> {目标}")
        self.刷新全部()

    def 删除分支(self):
        分支列表 = self.获取分支列表()
        if len(分支列表) <= 1:
            messagebox.showinfo("提示", "你只有唯一一条分支，不可删除")
            return
        对话框 = tk.Toplevel(self.根窗口)
        对话框.title("删除分支")
        对话框.transient(self.根窗口)
        对话框.grab_set()
        对话框.resizable(False, False)
        tk.Label(对话框, text="请选择要删除的分支：",
                 font=("微软雅黑", 11)).pack(padx=20, pady=(20, 6), anchor="w")
        变量 = tk.StringVar(value=分支列表[0])
        ttk.Combobox(对话框, textvariable=变量, values=分支列表,
                     state="readonly", width=36).pack(padx=20, pady=6)
        结果 = {"名称": None}

        def 确认():
            结果["名称"] = 变量.get()
            对话框.destroy()

        按钮区 = tk.Frame(对话框)
        按钮区.pack(pady=12)
        tk.Button(按钮区, text="取消", width=10,
                  command=对话框.destroy).pack(side="left", padx=8)
        tk.Button(按钮区, text="确认", width=10, bg=红色, fg="white",
                  activebackground=深红色, activeforeground="white",
                  command=确认).pack(side="left", padx=8)
        居中窗口(对话框)
        self.根窗口.wait_window(对话框)

        if not 结果["名称"]:
            return
        if not messagebox.askyesno(
                "确认", f"确定要删除分支 {结果['名称']} 吗？此操作不可逆"):
            return
        if self.获取设置("高危双重提示", True):
            if not messagebox.askyesno("二次确认", "真的要删除该分支吗？不可恢复！"):
                return
        码, _, 错 = 运行git(["branch", "-D", 结果["名称"]], self.当前仓库)
        if 码 != 0:
            messagebox.showerror("错误", f"删除失败：\n{错}")
        else:
            写日志(f"删除分支: {结果['名称']}")
        self.刷新全部()

    def 切换分支(self, 分支):
        if not self.当前仓库 or not 分支:
            return
        if 分支 == self.获取当前分支():
            return
        有修改 = self.检查工作区修改()
        if 有修改:
            if not messagebox.askyesno(
                    "提示",
                    "您的工作区有未保存的修改，如果现在切换分支 将会丢失所有修改，确认继续吗"):
                self.刷新分支选择器()
                return
            码, _, 错 = 运行git(["checkout", "-f", 分支], self.当前仓库)
        else:
            码, _, 错 = 运行git(["checkout", 分支], self.当前仓库)
        if 码 != 0:
            messagebox.showerror("错误", f"切换分支失败：\n{错}")
        else:
            写日志(f"切换分支: {分支}")
            self.保存当前状态()
        self.刷新全部()

    def 添加取消追踪文件(self):
        if not self.当前仓库:
            return
        对话框 = tk.Toplevel(self.根窗口)
        对话框.title("添加/取消追踪文件")
        对话框.transient(self.根窗口)
        对话框.grab_set()
        对话框.resizable(False, False)

        def 执行(操作类型):
            对话框.destroy()
            self.选择文件并追踪(操作类型)

        tk.Button(对话框, text="添加", height=2,
                  bg=绿色, fg="white", activebackground=深绿色,
                  activeforeground="white",
                  command=lambda: 执行("添加")).pack(fill="x", padx=20, pady=(20, 8))
        tk.Button(对话框, text="取消", height=2,
                  bg=红色, fg="white", activebackground=深红色,
                  activeforeground="white",
                  command=lambda: 执行("取消")).pack(fill="x", padx=20, pady=(8, 20))
        居中窗口(对话框)

    def 选择文件并追踪(self, 操作类型):
        if not self.当前仓库:
            return

        选择 = messagebox.askyesnocancel(
            f"{操作类型}追踪", 
            f"您想要{操作类型}追踪一个 [文件] 还是 [文件夹]？\n\n"
            "点“是”：选择文件\n"
            "点“否”：选择文件夹"
        )
        if 选择 is None:
            return

        if 选择:
            目标路径 = filedialog.askopenfilename(
                title=f"请选择要{操作类型}追踪的文件",
                initialdir=self.当前仓库
            )
        else:
            目标路径 = filedialog.askdirectory(
                title=f"请选择要{操作类型}追踪的文件夹",
                initialdir=self.当前仓库
            )

        if not 目标路径:
            return

        仓库绝对 = os.path.normcase(os.path.normpath(os.path.abspath(self.当前仓库)))
        目标绝对 = os.path.normcase(os.path.normpath(os.path.abspath(目标路径)))
        
        try:
            公共 = os.path.commonpath([仓库绝对, 目标绝对])
        except ValueError:
            公共 = ""
            
        if 公共 != 仓库绝对:
            messagebox.showwarning("提示", "请选择当前仓库内的文件或文件夹来执行操作")
            return
            
        相对路径 = os.path.relpath(目标绝对, 仓库绝对)
        
        if not messagebox.askyesno(
                "确认", f"确认要{操作类型}追踪：\n{相对路径}"):
            return
            
        if 操作类型 == "添加":
            码, _, 错 = 运行git(["add", 相对路径], self.当前仓库)
            if 码 != 0:
                messagebox.showerror("错误", f"添加失败：\n{错}")
                return
            写日志(f"添加追踪: {相对路径}")
        else:
            码, _, 错 = 运行git(["rm", "--cached", 相对路径], self.当前仓库)
            if 码 != 0:
                messagebox.showerror("错误", f"取消追踪失败：\n{错}\n\n(提示：如果文件夹内有未提交的修改，Git默认会拒绝取消追踪)")
                return
            写日志(f"取消追踪: {相对路径}")
            
        self.刷新全部()

    def 查看差异(self):
        if not self.当前仓库:
            return
        差异列表 = self.获取工作区差异()
        对话框 = tk.Toplevel(self.根窗口)
        对话框.title("查看与缓存区或最近一次提交的差异")
        对话框.resizable(False, False)
        列 = ("文件", "时间", "操作")
        表格 = ttk.Treeview(对话框, columns=列, show="headings")
        表格.heading("文件", text="文件名称")
        表格.heading("时间", text="修改时间")
        表格.heading("操作", text="操作")
        表格.column("文件", width=340)
        表格.column("时间", width=170, anchor="center")
        表格.column("操作", width=160, anchor="center")
        滚动条 = ttk.Scrollbar(对话框, orient="vertical", command=表格.yview)
        表格.configure(yscrollcommand=滚动条.set)
        表格.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        滚动条.pack(side="right", fill="y", padx=(0, 10), pady=10)

        for 项 in 差异列表:
            表格.insert("", "end", values=(
                项["path"], 项["time"], 项["op"]
            ))
        居中窗口(对话框, 800, 500)

    def 获取工作区差异(self):
        if not self.当前仓库:
            return []
        码, 输出, _ = 运行git(
            ["-c", "core.quotepath=false", "status", "--porcelain", "--untracked-files=all"],
            self.当前仓库
        )
        if 码 != 0:
            return []
        结果 = []
        状态汉化 = {
            "A": "新建",
            "M": "修改",
            "D": "删除",
            "R": "重命名",
            "C": "复制",
            "U": "冲突",
        }
        for 行 in 输出.splitlines():
            if len(行) < 3:
                continue
            X = 行[0]
            Y = 行[1]
            路径 = 行[3:].strip()
            完整 = os.path.join(self.当前仓库, 路径)

            if X == "?" and Y == "?":
                try:
                    if os.path.getsize(完整) == 0:
                        continue
                except Exception:
                    continue
                操作 = "未跟踪"
            else:
                状态集 = set()
                for 字符 in (X, Y):
                    if 字符 in 状态汉化:
                        状态集.add(状态汉化[字符])
                if not 状态集:
                    continue
                操作 = ",".join(sorted(状态集))

            try:
                时间戳 = os.path.getmtime(完整)
                时间串 = datetime.datetime.fromtimestamp(时间戳).strftime(
                    "%Y-%m-%d %H:%M:%S")
            except Exception:
                时间串 = ""
            结果.append({"path": 路径, "time": 时间串, "op": 操作})
        return 结果

    def 显示GitHub操作(self):
        if not self.当前仓库:
            messagebox.showinfo("提示", "请先选择或添加一个仓库")
            return
        
        用户名 = self.配置["github"].get("username", "")
        令牌 = self.配置["github"].get("token", "")
        仓库地址 = self.配置["github"].get("repo_url", "")

        if not 用户名 or not 令牌 or not 仓库地址:
            if not messagebox.askyesno("未配置", "检测到您还未关联 GitHub 账号或未填写仓库地址，是否现在进行配置？\n（需要 Personal Access Token）"):
                return
            
            对话框 = tk.Toplevel(self.根窗口)
            对话框.title("配置 GitHub")
            对话框.transient(self.根窗口)
            对话框.grab_set()
            对话框.resizable(False, False)

            说明文字 = (
                "获取配置信息的方法：\n"
                "1) 用户名：你的 GitHub 账号名\n"
                "2) Token：点下方按钮打开 Token 页面，登录后点 Generate new token (classic)，\n"
                "   勾选 repo 权限，生成后立即复制（只显示一次）\n"
                "3) 仓库地址：点下方按钮打开新建仓库页面，创建空仓库后\n"
                "   复制其 HTTPS 地址（形如 https://github.com/用户名/仓库名.git）"
            )
            tk.Label(对话框, text=说明文字, font=("微软雅黑", 9),
                     justify="left", wraplength=520, fg="#444444"
            ).grid(row=0, column=0, columnspan=2, padx=12, pady=(12, 4), sticky="w")

            链接行 = tk.Frame(对话框)
            链接行.grid(row=1, column=0, columnspan=2, pady=(0, 8))
            tk.Button(链接行, text="打开 Token 页面", width=16,
                      command=lambda: os.startfile(GITHUB_TOKEN页)
            ).pack(side="left", padx=4)
            tk.Button(链接行, text="打开新建仓库页面", width=16,
                      command=lambda: os.startfile(GITHUB新建仓库页)
            ).pack(side="left", padx=4)

            tk.Label(对话框, text="GitHub 用户名：", font=("微软雅黑", 11)
            ).grid(row=2, column=0, sticky="e", padx=10, pady=5)
            v_user = tk.StringVar(value=用户名)
            tk.Entry(对话框, textvariable=v_user, width=30, font=("微软雅黑", 10)
            ).grid(row=2, column=1, padx=10, pady=5)

            tk.Label(对话框, text="Personal Access Token：", font=("微软雅黑", 11)
            ).grid(row=3, column=0, sticky="e", padx=10, pady=5)
            v_token = tk.StringVar(value=令牌)
            tk.Entry(对话框, textvariable=v_token, width=30, font=("微软雅黑", 10), show="*"
            ).grid(row=3, column=1, padx=10, pady=5)

            tk.Label(对话框, text="远程仓库地址 (HTTPS)：", font=("微软雅黑", 11)
            ).grid(row=4, column=0, sticky="e", padx=10, pady=5)
            v_url = tk.StringVar(value=仓库地址)
            tk.Entry(对话框, textvariable=v_url, width=30, font=("微软雅黑", 10)
            ).grid(row=4, column=1, padx=10, pady=5)

            def 保存():
                u = v_user.get().strip()
                t = v_token.get().strip()
                url = v_url.get().strip()
                if not u or not t or not url:
                    messagebox.showwarning("提示", "所有字段均不能为空", parent=对话框)
                    return
                if not url.endswith(".git"):
                    url += ".git"
                
                self.配置["github"]["username"] = u
                self.配置["github"]["token"] = t
                self.配置["github"]["repo_url"] = url
                保存配置(self.配置)
                写日志("配置 GitHub 信息")
                对话框.destroy()
                self.显示GitHub操作()

            按钮区 = tk.Frame(对话框)
            按钮区.grid(row=5, column=0, columnspan=2, pady=15)
            tk.Button(按钮区, text="取消", width=10, command=对话框.destroy).pack(side="left", padx=10)
            tk.Button(按钮区, text="确认", width=10, bg=普通蓝色, fg="white", command=保存).pack(side="left", padx=10)

            居中窗口(对话框)
            self.根窗口.wait_window(对话框)
            return

        对话框 = tk.Toplevel(self.根窗口)
        对话框.title("GitHub 操作")
        对话框.transient(self.根窗口)
        对话框.grab_set()
        对话框.resizable(False, False)

        tk.Label(对话框, text=f"已关联 GitHub: {用户名}\n目标仓库: {仓库地址}", font=("微软雅黑", 11), justify="center").pack(pady=15, padx=20)

        def 执行拉取():
            url_with_auth = 仓库地址.replace("https://", f"https://{用户名}:{令牌}@")
            码, _, 错 = 运行git(["pull", url_with_auth, self.获取当前分支()], self.当前仓库, 超时=300)
            if 码 == 0:
                messagebox.showinfo("成功", "拉取成功！", parent=对话框)
                写日志("GitHub拉取成功")
                对话框.destroy()
                self.刷新全部()
            else:
                messagebox.showerror("拉取失败", 错, parent=对话框)

        def 执行推送():
            url_with_auth = 仓库地址.replace("https://", f"https://{用户名}:{令牌}@")
            码, _, 错 = 运行git(["push", url_with_auth, self.获取当前分支()], self.当前仓库, 超时=300)
            if 码 == 0:
                messagebox.showinfo("成功", "推送成功！", parent=对话框)
                写日志("GitHub推送成功")
                对话框.destroy()
                self.刷新全部()
            else:
                messagebox.showerror("推送失败", 错, parent=对话框)

        tk.Button(对话框, text="拉取远程代码 (Pull)", height=2, width=25, bg=绿色, fg="white", command=执行拉取).pack(pady=10)
        tk.Button(对话框, text="推送本地代码 (Push)", height=2, width=25, bg=普通蓝色, fg="white", command=执行推送).pack(pady=10)
        
        底部 = tk.Frame(对话框)
        底部.pack(pady=(10, 15))
        tk.Button(底部, text="修改配置", command=self.修改GitHub配置).pack(side="left", padx=5)
        tk.Button(底部, text="关闭", command=对话框.destroy).pack(side="left", padx=5)

        居中窗口(对话框)
        self.根窗口.wait_window(对话框)

    def 修改GitHub配置(self):
        self.配置["github"]["username"] = ""
        self.配置["github"]["token"] = ""
        保存配置(self.配置)
        self.显示GitHub操作()

def 主函数():
    确保目录()
    清理旧日志()
    if not 检查git():
        显示无git窗口()
    else:
        应用 = Git管理器应用()
        应用.根窗口.mainloop()

if __name__ == "__main__":
    主函数()