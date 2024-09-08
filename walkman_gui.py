import tkinter as tk
import ctypes
import os
import struct
import re
from threading import Thread
from tkinter import ttk, colorchooser, filedialog, messagebox
from PIL import Image, ImageTk, ImageDraw, ImageFont
from subprocess import Popen
from time import sleep

font_mapping = {
    "宋体": "simsun.ttc",
    "黑体": "simhei.ttf",
    "楷体": "simkai.ttf",
    "仿宋": "simfang.ttf",
}

def disable_combo_scroll(event):
    return "break"

def validate_input_x(p):
    if p == "":  # 允许清空输入框
        return True
    """验证输入是否是 0 到 240 之间的数字"""
    if p.isdigit():
        try:
            value = int(p)
            return 0 <= value < 240
        except ValueError:
            return False
    return False

def validate_input_y(p):
    if p == "":  # 允许清空输入框
        return True
    """验证输入是否是 0 到 160 之间的数字"""
    if p.isdigit():
        try:
            value = int(p)
            return 0 <= value < 160
        except ValueError:
            return False
    return False

def validate_input_z(p):
    if p == "":  # 允许清空输入框
        return True
    """验证输入是否是 12 到 24 之间的数字"""
    if p.isdigit():
        try:
            value = int(p)
            return 0 < value <= 24
        except ValueError:
            return False
    return False

class WalkmanApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.TThread = None
        self.font_path = None
        self.file_size_list2 = None
        self.file_size_list1 = None
        self.music_arg_list = None
        self.proc = None
        self.title("OpenGBA Walkman V1.0 BY 天涯 - 流云清风赞助开发")
        self.geometry("800x600")

        # 禁止调整窗口大小
        self.resizable(False, False)

        # 创建音乐管理的GroupBox
        self.music_group = ttk.LabelFrame(self, text="音乐管理")

        # 创建Treeview控件
        self.tree = ttk.Treeview(self.music_group, columns=("Filename", "Combo1", "Delete"), show='headings')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 添加垂直滚动条
        scrollbar_top = ttk.Scrollbar(self.music_group, orient=tk.VERTICAL, command=self.on_scroll)
        scrollbar_top.pack(side=tk.RIGHT, fill=tk.Y)

        # 设置列标题和初始宽度
        self.tree.heading("Filename", text="文件路径")
        self.tree.heading("Combo1", text="输出质量选择")
        self.tree.heading("Delete", text="操作")
        self.tree.column("Filename", width=300)
        self.tree.column("Combo1", width=100)
        self.tree.column("Delete", width=100)

        # 绑定点击事件
        self.tree.bind("<Button-1>", self.on_click)
        # 绑定鼠标拖动事件
        self.tree.bind("<MouseWheel>", self.on_mouse_wheel)
        # 将Treeview和Scrollbar绑定
        self.tree.config(yscrollcommand=scrollbar_top.set)

        # 完成创建音乐管理的GroupBox
        self.music_group.pack(side=tk.TOP, fill=tk.BOTH, padx=5, pady=5)

        # 创建Cool图管理的GroupBox
        cool_image_group = tk.Frame(self)

        image_list_frame = ttk.LabelFrame(cool_image_group, text="Cool图管理")
        # 创建Listbox用于显示图像文件路径
        self.image_listbox = tk.Listbox(image_list_frame)
        self.image_listbox.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 添加滚动条到Listbox
        scrollbar_bottom = tk.Scrollbar(self.image_listbox)
        scrollbar_bottom.pack(side=tk.RIGHT, fill=tk.Y)
        scrollbar_bottom.config(command=self.image_listbox.yview)

        # 绑定滚动条和列表选择事件
        self.image_listbox.bind("<<ListboxSelect>>", self.show_image_preview)
        self.image_listbox.config(yscrollcommand=scrollbar_bottom.set)

        button_frame = tk.Frame(image_list_frame)
        add_button = tk.Button(button_frame, text="添加", command=self.add_image)
        add_button.pack(side=tk.LEFT, padx=5, pady=5)

        delete_button = tk.Button(button_frame, text="删除", command=self.delete_image)
        delete_button.pack(side=tk.LEFT, padx=5, pady=5)

        up_button = tk.Button(button_frame, text="上移", command=self.move_up)
        up_button.pack(side=tk.LEFT, padx=5, pady=5)

        down_button = tk.Button(button_frame, text="下移", command=self.move_down)
        down_button.pack(side=tk.LEFT, padx=5, pady=5)
        button_frame.pack(side=tk.BOTTOM)

        image_list_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 创建Label用于显示图片预览
        control_frame = ttk.LabelFrame(cool_image_group, text="总控制台")

        control_btn_row1 = tk.Frame(control_frame)
        btn_row1_label = tk.Label(control_btn_row1, text="音乐控制:")
        btn_row1_label.pack(side=tk.LEFT, padx=5, pady=5)

        add_btn = tk.Button(control_btn_row1, text="添加", command=self.tree_add_file)
        add_btn.pack(side=tk.LEFT, padx=5, pady=5)

        up_btn = tk.Button(control_btn_row1, text="上移", command=self.tree_move_up)
        up_btn.pack(side=tk.LEFT, padx=5, pady=5)

        down_btn = tk.Button(control_btn_row1, text="下移", command=self.tree_move_down)
        down_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # 添加一个复选框
        self.compress_var = tk.BooleanVar()  # 用于存储复选框状态的变量
        self.checkbox = tk.Checkbutton(control_btn_row1, text="使用6:1压缩算法", variable=self.compress_var)
        self.checkbox.pack(side=tk.LEFT, padx=5, pady=5)

        gen_btn = tk.Button(control_btn_row1, text="生成ROM", command=self.generate_wrap)
        gen_btn.pack(side=tk.LEFT, padx=5, pady=5)
        control_btn_row1.pack()

        control_btn_row2 = tk.Frame(control_frame)
        self.songTitle_var = tk.BooleanVar()  # 用于存储复选框状态的变量
        song_title = tk.Checkbutton(control_btn_row2, text="Cool图附加歌曲标题", variable=self.songTitle_var)
        song_title.pack(side=tk.LEFT, padx=5, pady=5)

        color_button_label = tk.Label(control_btn_row2, text="文字颜色:")
        color_button_label.pack(side=tk.LEFT, padx=5, pady=5)
        # 添加颜色选择按钮
        self.color_button = tk.Button(control_btn_row2, bg="white", text="", command=self.choose_color, width=5, bd=0)
        self.color_button.pack(side=tk.LEFT, padx=5, pady=5)

        font_label = tk.Label(control_btn_row2, text="字体选择:")
        font_label.pack(side=tk.LEFT, padx=5, pady=5)
        # 获取系统字体列表
        fonts = ["宋体", "黑体", "楷体", "仿宋"]
        # 创建字体选择的Combobox
        self.font_combo = ttk.Combobox(control_btn_row2, values=fonts, width=10)
        self.font_combo.set("宋体")  # 设置初始字体
        self.font_combo.pack(side=tk.LEFT, padx=5, pady=5)

        control_btn_row2.pack()

        control_btn_row3 = tk.Frame(control_frame)
        x_label = tk.Label(control_btn_row3, text="标题X坐标:")
        x_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.x_entry = tk.Entry(control_btn_row3, validate='key', width=5,
                           validatecommand=(control_btn_row3.register(validate_input_x), '%P'))
        self.x_entry.pack(side=tk.LEFT, padx=5, pady=5)

        y_label = tk.Label(control_btn_row3, text="标题Y坐标:")
        y_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.y_entry = tk.Entry(control_btn_row3, validate='key', width=5,
                           validatecommand=(control_btn_row3.register(validate_input_y), '%P'))
        self.y_entry.pack(side=tk.LEFT, padx=5, pady=5)

        z_label = tk.Label(control_btn_row3, text="字号设置:")
        z_label.pack(side=tk.LEFT, padx=5, pady=5)
        self.z_entry = tk.Entry(control_btn_row3, validate='key', width=5,
                                validatecommand=(control_btn_row3.register(validate_input_z), '%P'))
        self.z_entry.pack(side=tk.LEFT, padx=5, pady=5)

        self.sel_font_button = tk.Button(control_btn_row3, text="加载字体", width=7, command=self.select_font_file)
        self.sel_font_button.pack(side=tk.LEFT, padx=5, pady=5)
        control_btn_row3.pack()

        self.image_preview_label = tk.Label(control_frame)
        self.set_default_black_image()
        self.image_preview_label.pack(fill=tk.BOTH, expand=True)

        # 创建进度条控件
        self.progressbar = ttk.Progressbar(control_frame, orient="horizontal", length=300, mode="determinate")
        self.progressbar.pack(side=tk.BOTTOM, padx=5, pady=5)

        control_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5)

        cool_image_group.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # 当前显示的ComboBox或Button的数据
        self.current_widget = None
        self.current_widget_info = None  # 用于存储当前控件的位置信息

        # 轮询列宽
        self.previous_widths = {col: self.tree.column(col)['width'] for col in self.tree['columns']}
        self.after(100, self.check_column_widths)

    def set_all_widgets_state(self, state):
        # 遍历所有子控件并设置状态
        self._set_widgets_state(self, state)

    def _set_widgets_state(self, widget, state):
        # 如果控件支持 state 选项，则设置其状态
        if state in [tk.NORMAL, tk.DISABLED]:
            if isinstance(widget,
                          (tk.Entry, tk.Button, tk.Checkbutton, tk.Radiobutton, tk.Text, tk.Spinbox, ttk.Combobox)):
                widget.config(state=state)

        # 遍历所有子控件并设置状态
        for child in widget.winfo_children():
            self._set_widgets_state(child, state)

    def select_font_file(self):
        # 弹出文件选择对话框，限制扩展名为 .ttf 和 .ttc
        file_path = filedialog.askopenfilename(
            title="选择字体文件",
            filetypes=[("受支持的字体文件", "*.ttf *.ttc")],
            defaultextension=".ttf"
        )

        # 如果未选择文件，直接返回
        if not file_path:
            self.font_path = None
            self.font_combo.config(state=tk.NORMAL)
            return

        # 否则，赋值给 self.font_path
        self.font_path = file_path

        # 禁用 font_combo
        self.font_combo.config(state=tk.DISABLED)

    def choose_color(self):
        # 弹出颜色选择器对话框
        color_code = colorchooser.askcolor(title="选择颜色")

        if color_code:
            # 选择的颜色值返回为 (RGB, HEX)
            selected_color = str(color_code[1])  # 获取 HEX 值
            # 将颜色应用到 btn 的背景色
            self.color_button.config(bg=selected_color)

    def on_mouse_wheel(self, event):
        if self.current_widget and self.current_widget_info:
            # 获取控件左上角的坐标和尺寸
            widget_x = self.current_widget.winfo_rootx()
            widget_y = self.current_widget.winfo_rooty()
            widget_width = self.current_widget.winfo_width()
            widget_height = self.current_widget.winfo_height()
            # 获取鼠标当前位置
            mouse_x = event.x_root
            mouse_y = event.y_root

            # 判断鼠标是否在控件范围内
            if not (widget_x <= mouse_x <= widget_x + widget_width and widget_y <= mouse_y <= widget_y + widget_height):
                row_id, column = self.current_widget_info
                self.save_combo_value(row_id, column)

    def on_scroll(self, *args):
        # 当滚动时(隐藏控件并应用控件值)
        self.tree.yview(*args)
        if self.current_widget and self.current_widget_info:
            row_id, column = self.current_widget_info
            self.save_combo_value(row_id, column)

    def check_column_widths(self):
        current_widths = {col: self.tree.column(col)['width'] for col in self.tree['columns']}
        for col in self.tree['columns']:
            if current_widths[col] != self.previous_widths[col]:
                if self.current_widget and self.current_widget_info:
                    row_id, column = self.current_widget_info
                    self.save_combo_value(row_id, column)
                self.previous_widths[col] = current_widths[col]

        self.after(100, self.check_column_widths)  # 继续轮询

    def add_row(self, filename):
        # 添加一行数据
        row_id = self.tree.insert("", "end", values=(filename, "最高质量", "删除"))
        return row_id

    def on_click(self, event):
        if self.TThread is not None:
            return
        # 先把上一次选中的项目的数据保存
        if self.current_widget and self.current_widget_info:
            row_id, column = self.current_widget_info
            self.save_combo_value(row_id, column)

        # 获取点击的列和行信息
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            row_id = self.tree.identify_row(event.y)
            column = self.tree.identify_column(event.x)

            # 如果是Combo1
            if column == "#2":
                self.create_combobox(self.music_group, row_id, column)
            # 如果是Delete按钮列
            elif column == "#3":
                self.create_delete_button(self.music_group, row_id, column)

    def draw_current_widget(self, row_id, column):
        # 获取单元格位置并绘制控件
        bbox = self.tree.bbox(row_id, column)
        if bbox:
            self.current_widget.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
            self.current_widget_info = (row_id, column)

    def save_combo_value(self, row_id, column):
        # 保存ComboBox的值到Treeview
        try:
            value = self.current_widget.get()
            self.tree.set(row_id, column=column, value=value)
        except AttributeError:
            pass
        self.current_widget.destroy()
        self.current_widget = None
        self.current_widget_info = None

    def create_combobox(self, parent, row_id, column):
        if self.current_widget:
            self.current_widget.destroy()  # 移除之前的控件

        # 获取当前单元格的内容
        value = self.tree.set(row_id, column=column)
        options = ["最高质量", "高质量", "中等质量", "低质量"]

        # 创建ComboBox并放置到单元格位置
        self.current_widget = ttk.Combobox(parent, values=options, state="readonly")
        self.current_widget.set(value)
        self.current_widget.bind("<<ComboboxSelected>>", lambda e: self.save_combo_value(row_id, column))

        # 禁用滚轮切换选项
        self.current_widget.bind("<MouseWheel>", disable_combo_scroll)  # Windows, macOS
        self.current_widget.bind("<Button-4>", disable_combo_scroll)  # Linux
        self.current_widget.bind("<Button-5>", disable_combo_scroll)  # Linux

        self.draw_current_widget(row_id, column)

    def create_delete_button(self, parent, row_id, column):
        if self.current_widget:
            self.current_widget.destroy()  # 移除之前的控件

        # 创建Button并放置到单元格位置
        self.current_widget = tk.Button(parent, text="删除", relief=tk.RAISED, borderwidth=2,
                                        command=lambda: self.delete_row(row_id))

        self.draw_current_widget(row_id, column)

    def delete_row(self, row_id):
        # 删除当前行
        self.tree.delete(row_id)
        if self.current_widget:
            self.current_widget.destroy()
            self.current_widget = None
            self.current_widget_info = None

    def set_default_black_image(self):
        # 创建240x160的纯黑图像
        black_image = Image.new("RGB", (240, 160), color="black")

        # 将图像转换为PhotoImage
        black_photo = ImageTk.PhotoImage(black_image)

        # 设置Label为纯黑图像
        self.image_preview_label.config(image=black_photo)
        self.image_preview_label.image = black_photo

    def show_image_preview(self, event):
        # 获取选中的文件路径
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            filepath = self.image_listbox.get(index)
            filepath = re.sub(r'^\[.*?]', '', filepath)
            try:
                # 打开并显示图片
                image = Image.open(filepath)
                image = image.resize((240, 160), Image.LANCZOS) # 调整图片大小以适应预览区域

                # 检查是否需要绘制文字
                if self.songTitle_var.get() and index - 1 < len(self.tree.get_children()) and index != 0:
                    x = self.x_entry.get()
                    y = self.y_entry.get()
                    z = self.z_entry.get()

                    # 检查x和y值是否有效
                    if x.isdigit() and y.isdigit() and z.isdigit():
                        x = int(x)
                        y = int(y)
                        z = int(z)

                        # 获取选择的字体和颜色
                        selected_font = font_mapping[self.font_combo.get()]
                        selected_color = self.color_button.cget("bg")

                        # 创建一个绘图对象
                        draw = ImageDraw.Draw(image)

                        item_id = self.tree.get_children()[index - 1]
                        item_text = self.tree.item(item_id, 'values')[0]
                        filename = os.path.basename(item_text)
                        filename_without_extension = os.path.splitext(filename)[0]

                        # 在指定位置绘制文本
                        draw.text((x, y), filename_without_extension,
                                  font=ImageFont.truetype(selected_font if self.font_path is None else self.font_path, z),
                                  fill=selected_color)

                photo = ImageTk.PhotoImage(image)
                self.image_preview_label.config(image=photo)
                self.image_preview_label.image = photo
            except Exception as e:
                print(f"无法加载图片: {e}")

    def add_image(self):
        current_items = self.image_listbox.size()
        if current_items >= 21:
            messagebox.showerror("错误", "Cool图列表已达到最大容量 (21 项)")
            return

        # 打开文件选择对话框，选择图像文件
        filetypes = [("常见图像文件", "*.jpg;*.png;*.gif;*.bmp"), ("All files", "*.*")]
        filepaths = filedialog.askopenfilenames(title="选择图像文件", filetypes=filetypes)
        for filepath in filepaths:
            if self.image_listbox.size() >= 21:
                messagebox.showerror("错误", "Cool图列表已达到最大容量 (21 项)")
                return
            if self.image_listbox.size() == 0:
                self.image_listbox.insert(tk.END, "[专辑封面]" + filepath)
            else:
                self.image_listbox.insert(tk.END, "[歌曲封面" + str(self.image_listbox.size())  + "]" + filepath)

    def delete_image(self):
        # 删除选中的图像文件路径
        selection = self.image_listbox.curselection()
        if selection:
            self.image_listbox.delete(selection)

    def update_all_items(self, listbox):
        # 遍历现有项并更新其文本
        for i in range(listbox.size()):
            if i == 0:
                text = self.image_listbox.get(i)
                text = re.sub(r'^\[.*?]', '', text)
                listbox.delete(i)
                listbox.insert(i, "[专辑封面]" + text)
            else:
                text = self.image_listbox.get(i)
                text = re.sub(r'^\[.*?]', '', text)
                listbox.delete(i)
                listbox.insert(i, "[歌曲封面" + str(i) + "]" + text)

    def move_up(self):
        # 将选中的项目上移
        selection = self.image_listbox.curselection()
        if selection:
            index = selection[0]
            if index > 0:
                text = self.image_listbox.get(index)
                self.image_listbox.delete(index)
                self.image_listbox.insert(index - 1, text)
                self.update_all_items(self.image_listbox)
                self.image_listbox.selection_set(index - 1)

    def move_down(self):
        # 将选中的项目下移
        selection = self.image_listbox.curselection()
        if selection:
            index = selection[0]
            if index < self.image_listbox.size() - 1:
                text = self.image_listbox.get(index)
                self.image_listbox.delete(index)
                self.image_listbox.insert(index + 1, text)
                self.update_all_items(self.image_listbox)
                self.image_listbox.selection_set(index + 1)

    def tree_add_file(self):
        current_items = len(self.tree.get_children())
        if current_items >= 20:
            messagebox.showerror("错误", "音乐列表已达到最大容量 (20 项)")
            return

        # 打开文件选择对话框，支持的音乐文件类型为常见格式
        filetypes = [("常见音乐格式", "*.mp3 *.wav *.flac *.aac *.ogg"),
                     ("所有文件", "*.*")]
        files = filedialog.askopenfilenames(title="选择音乐文件", filetypes=filetypes)

        # 将选中的文件添加到 Treeview 中
        for file in files:
            if len(self.tree.get_children()) >= 20:
                messagebox.showerror("错误", "音乐列表已达到最大容量 (20 项)")
                return
            self.add_row(file)

    def tree_move_up(self):
        selected_items = self.tree.selection()
        for item in selected_items:
            prev_item = self.tree.prev(item)
            if prev_item:
                if self.current_widget and self.current_widget_info:
                    row_id, column = self.current_widget_info
                    self.save_combo_value(row_id, column)
                self.tree.move(item, '', self.tree.index(prev_item))

    def tree_move_down(self):
        selected_items = self.tree.selection()
        for item in reversed(selected_items):  # 逆序处理以避免索引问题
            next_item = self.tree.next(item)
            if next_item:
                if self.current_widget and self.current_widget_info:
                    row_id, column = self.current_widget_info
                    self.save_combo_value(row_id, column)
                self.tree.move(item, '', self.tree.index(next_item))

    @staticmethod
    def write_image(out_path):
        result = dll.WriteHeader(b"temp.gba", 1)
        if not result == 0:
            return False
        result = dll.WriteImage(b"temp.bmp", 1)
        if not result == 0:
            os.remove("temp.bmp")
            os.remove("temp.gba")
            dll.WriteTail(1, 1)
            return False

        dll.WriteTail(1, 1)

        # 读取 temp.gba 从 0x4000 开始的数据
        with open("temp.gba", "rb") as gba_file:
            gba_file.seek(0x4000)  # 移动到 0x4000 位置
            data = gba_file.read()  # 读取到文件结尾的数据

        # 追加数据到 out_path 文件
        with open(out_path, "ab") as out_file:
            out_file.write(data)

        os.remove("temp.bmp")
        os.remove("temp.gba")

        return True

    def write_music(self, out_path, music_arg):
        result = dll.WriteHeader(b"temp.gba", 1)
        if not result == 0:
            return False
        if self.compress_var.get():
            result = dll.WriteMusic3(b"temp.wav", 1, music_arg, 0, 0)
        else:
            result = dll.WriteMusic(b"temp.wav", 1, music_arg, 0, 0)
        if not result == 0:
            os.remove("temp.wav")
            os.remove("temp.gba")
            dll.WriteTail(1, 1)
            return False

        dll.WriteTail(1, 1)

        # 读取 temp.gba 从 0x4000 开始的数据
        with open("temp.gba", "rb") as gba_file:
            gba_file.seek(0x4000)  # 移动到 0x4000 位置
            data = gba_file.read()  # 读取到文件结尾的数据

        # 追加数据到 out_path 文件
        with open(out_path, "ab") as out_file:
            out_file.write(data)

        os.remove("temp.wav")
        os.remove("temp.gba")

        return True

    def write_info_data(self, out_path):
        # 打开文件，以读写模式，并且不改变文件大小
        with open(out_path, 'r+b') as f:
            # 定位到 0x3E6C 位置
            f.seek(0x3E6C)

            # 获取 Treeview 元素的数量
            num_entries = len(self.tree.get_children())

            # 以8位整数写入元素的数量
            f.write(struct.pack('<B', num_entries))  # 写入8位整数
            # 根据compress_value，写入对应的值
            f.write(struct.pack('<B', 1 if self.compress_var.get() else 0))  # 另一个8位整数
            # 写入16位的0
            f.write(struct.pack('<H', 0))  # 16位的0

            # 遍历每个元素，按照要求写入数据
            for i in range(num_entries):
                # 固定写入 0x1
                f.write(struct.pack('<I', 0x1))

                # 写入 music_arg_list[i]
                f.write(struct.pack('<I', self.music_arg_list[i]))

                # 写入 file_size_list1[i]
                f.write(struct.pack('<I', self.file_size_list1[i]))

                # 写入 file_size_list2[i] 两次
                f.write(struct.pack('<I', self.file_size_list2[i]))
                f.write(struct.pack('<I', self.file_size_list2[i]))

    def generate_wrap(self):
        if self.current_widget and self.current_widget_info:
            row_id, column = self.current_widget_info
            self.save_combo_value(row_id, column)

        if not self.tree.get_children():
            # 如果没有元素，弹出提示对话框
            messagebox.showwarning("警告", "尚未添加任何文件")
            return

        # 呼出保存文件对话框，只允许保存为 .gba 格式
        out_path = filedialog.asksaveasfilename(
            defaultextension=".gba",
            filetypes=[("GBA ROM", "*.gba")],
            title="保存 GBA 文件"
        )

        if not out_path or out_path == "":
            # 如果用户选择了文件路径，继续执行文件转换和保存操作
            return

        self.set_all_widgets_state(tk.DISABLED)
        self.TThread = Thread(target=self.generate, args=(out_path,))
        self.TThread.start()

    def generate(self, out_path):
        # 初始化三个长度为20的列表，用来存储32位整数
        self.music_arg_list = [0] * 20
        self.file_size_list1 = [0] * 20
        self.file_size_list2 = [0] * 20

        result = dll.WriteHeader(b"temp.gba", 1)
        dll.WriteTail(1, 1)  # Close file then I can rename it
        if os.path.exists(out_path):
            os.remove(out_path)
        os.rename("temp.gba", out_path)

        # 检查结果
        if not result == 0:
            messagebox.showerror("错误", "文件头写入失败")
            self.set_all_widgets_state(tk.NORMAL)
            self.progressbar['value'] = 0
            self.TThread = None
            return

        output_image = "temp.bmp"

        if self.image_listbox.size() > 0:
            image_file = self.image_listbox.get(0)
            image_file = re.sub(r'^\[.*?]', '', image_file)
            # 转换图像文件为24位色、240x160分辨率的BMP
            with Image.open(image_file) as img:
                img = img.convert("RGB")  # 转换为24位色
                img = img.resize((240, 160), Image.LANCZOS)  # 缩放到指定分辨率
                img.save(output_image, "BMP")  # 保存为BMP格式

        if os.path.exists(output_image):
            if not self.write_image(out_path):
                messagebox.showerror("错误", "Cool图写入失败")
                self.set_all_widgets_state(tk.NORMAL)
                self.progressbar['value'] = 0
                self.TThread = None
                return
        else:
            with open(out_path, "ab") as gba_file:
                with open("default.bin", "rb") as bin_file:
                    gba_file.write(bin_file.read())

        for i, item in enumerate(self.tree.get_children()):
            self.progressbar['value'] = i * 100 / len(self.tree.get_children())
            file_path = self.tree.item(item, 'values')[0]

            # 使用ffmpeg转换音乐文件为WAV格式
            self.proc = Popen(["ffmpeg", "-i", file_path, "-ar", "44100", "-ac", "1", "-map", "0:0",
                               "-map_metadata", "-1", "-y", "temp.wav"])
            ret_val = self.proc.wait()

            if ret_val == 0:
                # 获取文件大小
                file_size = os.path.getsize(out_path)
                self.file_size_list1[i] = file_size

                music_arg = QUALITY_ARG_MAP[self.tree.item(item, 'values')[1]]
                self.music_arg_list[i] = music_arg
                if not self.write_music(out_path, music_arg):
                    messagebox.showerror("错误", "音乐写入失败")
                    self.set_all_widgets_state(tk.NORMAL)
                    self.progressbar['value'] = 0
                    self.TThread = None
                    return

                # 获取文件大小
                file_size = os.path.getsize(out_path)
                self.file_size_list2[i] = file_size

                # 检查image_listbox中是否有相同索引值的项目
                if i + 1 < self.image_listbox.size():  # 假设image_listbox也是从0开始索引
                    image_file = self.image_listbox.get(i + 1)
                    image_file = re.sub(r'^\[.*?]', '', image_file)
                    # 转换图像文件为24位色、240x160分辨率的BMP
                    with Image.open(image_file) as img:
                        img = img.convert("RGB")  # 转换为24位色
                        img = img.resize((240, 160), Image.LANCZOS)  # 缩放到指定分辨率
                        # 检查是否需要绘制文字
                        if self.songTitle_var.get():
                            x = self.x_entry.get()
                            y = self.y_entry.get()
                            z = self.z_entry.get()

                            # 检查x和y值是否有效
                            if x.isdigit() and y.isdigit() and z.isdigit():
                                x = int(x)
                                y = int(y)
                                z = int(z)

                                # 获取选择的字体和颜色
                                selected_font = font_mapping[self.font_combo.get()]
                                selected_color = self.color_button.cget("bg")

                                # 创建一个绘图对象
                                draw = ImageDraw.Draw(img)

                                filename = os.path.basename(file_path)
                                filename_without_extension = os.path.splitext(filename)[0]

                                # 在指定位置绘制文本
                                draw.text((x, y), filename_without_extension, font=ImageFont.truetype(selected_font, z),
                                          fill=selected_color)
                        img.save(output_image, "BMP")  # 保存为BMP格式

                if os.path.exists(output_image):
                    if not self.write_image(out_path):
                        messagebox.showerror("错误", "Cool图写入失败")
                        self.set_all_widgets_state(tk.NORMAL)
                        self.progressbar['value'] = 0
                        self.TThread = None
                        return
                else:
                    with open(out_path, "ab") as gba_file:
                        with open("default.bin", "rb") as bin_file:
                            gba_file.write(bin_file.read())

        # 最后写入信息头数据
        self.write_info_data(out_path)
        self.progressbar['value'] = 100
        sleep(1)
        self.set_all_widgets_state(tk.NORMAL)
        self.progressbar['value'] = 0
        self.TThread = None

if __name__ == "__main__":
    # 加载DLL
    dll = ctypes.windll.LoadLibrary('walkfree.dll')

    # 定义函数的参数和返回类型
    dll.WriteHeader.argtypes = [ctypes.c_char_p, ctypes.c_int]
    dll.WriteHeader.restype = ctypes.c_int

    dll.WriteImage.argtypes = [ctypes.c_char_p, ctypes.c_int]
    dll.WriteImage.restype = ctypes.c_int

    dll.WriteTail.argtypes = [ctypes.c_int, ctypes.c_int]
    dll.WriteTail.restype = ctypes.c_int

    # 第3个参数是音质(1-6 不能为4 1代表高音质 2代表立体声 3代表高音质一般音频 5为中等 6为低音质)
    dll.WriteMusic.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    dll.WriteMusic.restype = ctypes.c_int

    dll.WriteMusic3.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
    dll.WriteMusic3.restype = ctypes.c_int

    QUALITY_ARG_MAP = {
        '最高质量': 1,
        '高质量': 3,
        '中等质量': 5,
        '低质量': 6,
        '立体声': 2,
    }

    app = WalkmanApp()
    app.mainloop()
