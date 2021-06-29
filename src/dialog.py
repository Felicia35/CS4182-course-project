 #*-coding: utf-8-*-
#file: Dialog.py
#
import win32ui
#导入win32ui模块
import win32con
#导入win32con模块
from pywin. mfc import dialog
#从 pywin.mfc导入 dialog
class MyDialog(dialog. Dialog): # 通过继承dialog Dialog生成对话框类
	def OnInitDialog(self):		#重载对话框初始化方法
		dialog.Dialog.OnInitDialog(self)	#调用父类的对话框初始化方法
		self.edit = self.GetDlgItem(13)
	
	def OnOK(self):		#重载OnOK方法
		win32ui.MessageBox('Press', 'Python', win32con.MB_OK)
		print(self.edit.GetWindowText())
		self.EndDialog(1)
	
	def OnCancel(self):#重载OnCancel方法
		win32ui. MessageBox('Press Cancel', 'Python'. win32con.MB_OK)
		self.EndDialog()

style = (win32con.DS_MODALFRAME	| #定义对话框样式
		 win32con.WS_POPUP |
		 win32con.WS_VISIBLE |
		 win32con.WS_CAPTION |
		 win32con.WS_SYSMENU |
		 win32con.DS_SETFONT)

childstyle =(win32con. WS_CHILD |	#定义控件样式
win32con.WS_VISIBLE)

buttonstyle = win32con.WS_TABSTOP | childstyle

di = ['Python', (0, 0, 200, 90), style, None,(8, "MS Sans Serif")]
 
ButoK =(['Button', #设置OK按钮属性
"OK",
win32con.IDOK,
(50, 50, 50, 14),
buttonstyle | win32con.BS_PUSHBUTTON])

ButCancel =(['Button', #设置Cancel按钮属性
"Cancel",
win32con.IDCANCEL,
(110, 50, 50, 14),
buttonstyle | win32con.BS_PUSHBUTTON])

Stadic =(['Static', #设置标签属性
'Resolution:',
12,
(10, 30, 60, 14), childstyle])

Width =(['Edit', #设置文本框属性
'1280',
13,
(50, 30, 50, 14),
childstyle | win32con.ES_LEFT |
win32con.WS_BORDER | win32con.WS_TABSTOP])

Height =(['Edit', #设置文本框属性
'720',
14,
(110, 30, 50, 14),
childstyle | win32con.ES_LEFT |
win32con.WS_BORDER | win32con.WS_TABSTOP])

init = []	#初始化信息列表
init.append(di)
init.append(ButoK)
init.append(ButCancel)
init.append(Stadic)
init.append(Width)
init.append(Height)
mydialog = MyDialog(init) #生成对话框实例对象
mydialog. DoModal()	#创建对话框