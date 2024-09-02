import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from PIL import Image, ImageTk


def disable_combo_scroll(event):
    return "break"


class WalkmanApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("OpenWalkman BY 天涯 - 流云清风赞助开发")
        self.geometry("600x400")

        self.resizable(False, False)

        # 创建音乐管理的GroupBox
        self.music_group = ttk.LabelFrame(self, text="音乐管理")
        self.music_group.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 创建一个包含Treeview和Scrollbar的Frame
        tree_frame = tk.Frame(self.music_group)
        tree_frame.pack(fill=tk.BOTH, expand=True)

        # 创建Treeview控件
        self.tree = ttk.Treeview(tree_frame, columns=("Filename", "Combo1", "Combo2", "Delete"), show='headings')
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 设置列标题和初始宽度
        self.tree.heading("Filename", text="文件路径")
        self.tree.heading("Combo1", text="输出质量选择")
        self.tree.heading("Combo2", text="音量放大")
        self.tree.heading("Delete", text="操作")

        self.tree.column("Filename", width=200)
        self.tree.column("Combo1", width=100)
        self.tree.column("Combo2", width=100)
        self.tree.column("Delete", width=100)

        # 绑定点击事件
        self.tree.bind("<Button-1>", self.on_click)
        # 绑定鼠标拖动事件
        self.tree.bind("<MouseWheel>", self.on_mouse_wheel)

        # 添加垂直滚动条
        scrollbar_top = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.on_scroll)
        scrollbar_top.pack(side=tk.RIGHT, fill=tk.Y)

        # 将Treeview和Scrollbar绑定
        self.tree.config(yscrollcommand=scrollbar_top.set)

        # 创建Cool图管理的GroupBox
        cool_image_group = ttk.LabelFrame(self, text="Cool图管理")
        cool_image_group.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, padx=10, pady=5)

        # 添加下方的Frame用于Listbox和图片预览
        bottom_frame = tk.Frame(cool_image_group)
        bottom_frame.pack(fill=tk.BOTH, expand=True)

        # 创建Listbox用于显示图像文件路径
        self.image_listbox = tk.Listbox(bottom_frame)
        self.image_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.image_listbox.bind("<<ListboxSelect>>", self.show_image_preview)

        # 添加滚动条到Listbox
        scrollbar_bottom = tk.Scrollbar(self.image_listbox)
        scrollbar_bottom.pack(side=tk.RIGHT, fill=tk.Y)
        self.image_listbox.config(yscrollcommand=scrollbar_bottom.set)
        scrollbar_bottom.config(command=self.image_listbox.yview)

        # 创建Label用于显示图片预览
        self.image_preview_label = tk.Label(bottom_frame)
        self.image_preview_label.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 当前显示的ComboBox或Button的数据
        self.current_widget = None
        self.current_widget_info = None  # 用于存储当前控件的位置信息

        # 轮询列宽
        self.previous_widths = {col: self.tree.column(col)['width'] for col in self.tree['columns']}
        self.after(100, self.check_column_widths)

        # 绑定窗口大小变化事件
        # self.bind("<Configure>", self.on_window_resize)

        # 示例数据
        self.add_row("file1.txt")
        self.add_row("file2.txt")
        self.add_row("file3.txt")
        self.add_row("file4.txt")
        self.add_row("file5.txt")
        self.add_row("file6.txt")
        self.add_row("file7.txt")
        self.add_row("file8.txt")
        self.add_row("file9.txt")
        self.add_row("file10.txt")
        self.add_row("file11.txt")
        self.add_row("file12.txt")
        self.add_row("file13.txt")
        self.add_row("file14.txt")

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
        row_id = self.tree.insert("", "end", values=(filename, "最高质量", "不放大", "删除"))
        return row_id

    def on_click(self, event):
        # 先把上一次选中的项目的数据保存
        if self.current_widget and self.current_widget_info:
            row_id, column = self.current_widget_info
            self.save_combo_value(row_id, column)

        # 获取点击的列和行信息
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            row_id = self.tree.identify_row(event.y)
            column = self.tree.identify_column(event.x)

            # 如果是Combo1或Combo2列
            if column == "#2" or column == "#3":
                self.create_combobox(self.music_group, row_id, column)
            # 如果是Delete按钮列
            elif column == "#4":
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
        options = ["最高质量", "高质量", "中等质量", "低质量", "立体声"] if column == "#2" else ["不放大", "两倍", "四倍", "八倍"]

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

    def on_window_resize(self, event):
        # 当窗口大小变化时销毁当前呼出的控件(如果有)
        if self.current_widget and self.current_widget_info:
            row_id, column = self.current_widget_info
            bbox = self.tree.bbox(row_id, column)
            if bbox:
                self.current_widget.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
                self.current_widget_info = (row_id, column)
            else:
                self.current_widget.destroy()
                self.current_widget = None
                self.current_widget_info = None


    def show_image_preview(self, event):
        # 获取选中的文件路径
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            filepath = self.image_listbox.get(index)
            try:
                # 打开并显示图片
                image = Image.open(filepath)
                image.thumbnail((200, 200))  # 调整图片大小以适应预览区域
                photo = ImageTk.PhotoImage(image)
                self.image_preview_label.config(image=photo)
                self.image_preview_label.image = photo
            except Exception as e:
                print(f"无法加载图片: {e}")


if __name__ == "__main__":
    app = WalkmanApp()
    app.mainloop()
