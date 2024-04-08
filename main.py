
from tkinter import *
from tkinter.ttk import *
from Data_capture import Weather
from PIL import Image, ImageTk


# 框架画布，基类，继承类：Frame_mainFrame(Frame)，Frame_picFrame(Frame)
class WinGUI(Tk):
    def __init__(self):
        super().__init__()
        self.__win()
        self.tk_frame_picFrame = Frame_picFrame(self)
        self.tk_frame_mainFrame = Frame_mainFrame(self)

    def __win(self):
        self.title("未来14天温度走势图")
        # 设置窗口大小、居中
        width = 640
        height = 540
        screenwidth = self.winfo_screenwidth()
        screenheight = self.winfo_screenheight()
        geometry = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        self.geometry(geometry)
        self.resizable(width=False, height=False)


# 查询界面主框架样式
class Frame_mainFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.frame()
        self.tk_label_group = self.__tk_label_group()
        self.tk_input_tar_city = \
            self.__tk_input_tar_city()
        self.tk_button_search = self.__tk_button_search()
        self.tk_label_tip = self.__tk_label_tip()
        self.tk_list_box_city_list = self.__tk_list_box_city_list()
        self.tk_label_tip1 = self.__tk_label_tip1()

    # 初始化函数，将画布映射到主框架，调用place出现画布
    def frame(self):
        self.place(x=-2, y=0, width=640, height=540)

    # log
    def __tk_label_group(self):
        global log
        img = Image.open('./log.png')
        log = ImageTk.PhotoImage(img)
        label = Label(self, image=log, anchor="center")
        label.place(x=20, y=20, width=97, height=98)
        return label

    # 输入框
    def __tk_input_tar_city(self):
        ipt = Entry(self)
        ipt.place(x=200, y=80, width=232, height=38)
        return ipt

    # 搜索按钮
    def __tk_button_search(self):
        btn = Button(self, text="搜索")
        btn.place(x=480, y=80, width=80, height=41)
        return btn

    # 提示：您可以输入省份或城市查询
    def __tk_label_tip(self):
        label = Label(self, text="您可以输入省份或城市查询", anchor="center")
        label.place(x=200, y=40, width=232, height=27)
        return label

    # 提示：选择您要查询的城市即可
    def __tk_label_tip1(self):
        label = Label(self, text="选择您要查询的城市即可", anchor="center")
        label.place(x=40, y=150, width=149, height=24)
        return label

    # 地区列表，列表框
    def __tk_list_box_city_list(self):
        lb = Listbox(self)
        lb.place(x=41, y=180, width=557, height=320)
        return lb


# 走势图界面设计
class Frame_picFrame(Frame):
    def __init__(self, parent):
        super().__init__(parent)  # 初始化继承基类
        self.tk_button_return = self.__tk_button_return()
        self.tk_label_picture = ''  # 图片初始为空

    # 走势图框架初始化
    def frame(self):
        self.tk_label_picture = self.__tk_label_picture()
        self.place(x=0, y=0, width=640, height=540)

    # 返回按扭
    def __tk_button_return(self):
        btn = Button(self, text="返回")
        btn.place(x=290, y=500, width=50, height=24)
        return btn

    # 温度走势图
    def __tk_label_picture(self):
        global phl
        img = Image.open('./tem.png')
        phl = ImageTk.PhotoImage(img)
        label = Label(self, text='123', image=phl)
        label.place(x=10, y=10, width=619, height=460)
        return label


# 继承WinGUI
class Win(WinGUI):
    def __init__(self):
        super().__init__()  # 初始化基类，先进入win初始化函数，然后调用到WinGUI，然后初始化其他的，
        self.__event_bind()
        self.rep = Weather()
        # Weather在Data_capture文件中没有初始化，而是在win类初始化时，导入
        # 初始化Data_capture文件中的weather类，在listBoxInsert，show_pic，back需要用到weather

    # 城市地区列表框插入
    def listBoxInsert(self, lis):
        self.tk_frame_mainFrame.tk_list_box_city_list.delete(0, END)
        for i in lis:
            self.tk_frame_mainFrame.tk_list_box_city_list.insert(0, i)
            # lis是cityList

    # 城市地区列表搜索显示
    def search_city(self, evt):
        cityName = self.tk_frame_mainFrame.tk_input_tar_city.get()
        cityList = self.rep.get_cityList(cityName)
        if cityList:
            self.listBoxInsert(cityList[::-1])
        else:
            self.listBoxInsert(['请输入正确城市或省份名'])  # 如果搜不到城市，citlist为空，插入提示
        print("get")
        # 不为空就显示列表数据

    # 显示温度走势图
    def show_pic(self, evt):
        self.tk_frame_mainFrame.place_forget()  # 隐藏主画布
        w = evt.widget
        # 防止报错，报错正常退出报错，没有就显示第一个画布
        try:
            index = int(w.curselection()[0])  # 取得索引值
        except IndexError:
            self.tk_frame_mainFrame.frame()
            return
        value = w.get(index)  # 返回指定索引的值，城市或省份名
        if value != '请输入正确城市或省份名':
            self.rep.getTem(value)  # getTem获取温度，绘图，渲染第二个画布
            self.tk_frame_picFrame.frame()
        else:
            self.tk_frame_mainFrame.frame()
        print('ok')

    # 返回按钮，将主画布渲染，走势图画布关闭
    def back(self, evt):
        self.tk_frame_mainFrame.frame()
        self.tk_frame_picFrame.place_forget()
        print('return')

    # 三个绑定事件
    def __event_bind(self):
        self.tk_frame_mainFrame.tk_button_search.bind('<Button-1>', self.search_city)
        # 点击搜索按钮触发search_city处理函数
        self.tk_frame_mainFrame.tk_list_box_city_list.bind('<<ListboxSelect>>', self.show_pic)
        # 点击列表框选项触发show_pic处理函数
        self.tk_frame_picFrame.tk_button_return.bind('<Button-1>', self.back)
        # 点击返回按钮触发back处理函数


if __name__ == "__main__":
    win = Win()  # 初始化Win类时，初始化weather类及其他类
    win.mainloop()
