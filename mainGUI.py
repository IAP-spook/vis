#-*- coding:utf-8 -*-
#*   Copyright (C) 2020 WYN. All rights reserved.
#*   文件名称：mainGUI.py
#*   创 建 者：WangYinan
#*   创建日期：2020年09月17日

from dearpygui.dearpygui import *
from contextlib import contextmanager
from functools import wraps
import serial
import serial.tools.list_ports
from SerialClass import *
import time

# Context Managers : normally in dearpygui.wrappers
#########################################################
def wrap_container(container):
    @contextmanager
    @wraps(container)
    def container_context(*args,**kwargs):
        try: yield container(*args,**kwargs)
        finally: end()
    return container_context

window = wrap_container(add_window)
menu_bar = wrap_container(add_menu_bar)
menu = wrap_container(add_menu)
child = wrap_container(add_child)
collapsing_header = wrap_container(add_collapsing_header)
group = wrap_container(add_group)
tab_bar = wrap_container(add_tab_bar)
tab = wrap_container(add_tab)
tree_node = wrap_container(add_tree_node)
tooltip = wrap_container(add_tooltip)
popup = wrap_container(add_popup)

##########################################################
def saveFile(sender,data):
    print(sender,data)

def getAllPortName():
    port_list = list(serial.tools.list_ports.comports())
    device_list = [pl.device for pl in port_list]
    return device_list
#GUI settings
set_main_window_title(u"探空能见度接收软件-v1.0")
set_main_window_size(1000,900)
add_additional_font("NotoSerifCJKjp-Medium.otf", 20, "chinese_simplified_common")
# MenuBar Part
with menu_bar("MenuBar"):
    def saveFile(sender,data):
        print(sender,data)
    with menu(u"设置"):
        add_menu_item(u"保存文件",callback=saveFile)
        add_menu_item(u'另存文件',callback=saveFile)
    with menu(u"帮助"):
        add_menu_item(u"帮助",callback=saveFile)

#串口相关
portWidth = 100

class SerialGUI(BaseSerial):
    def decodeData(self,data):
        pass

serGUI=None
portControl = True
receiveData = []

def PortOpenCallback(sender,data):
    global serGUI,portControl
    portControl = True
    port = get_value('Port##widget')
    baudrate = get_value('Baudrate##widget')
    serGUI = SerialGUI(port,baudrate)
    run_async_function(longReadSerial,serGUI,return_handler=asyncText)        

def longReadSerial(sender,data):
    global receiveData
    while portControl and data.com.isOpen():
        data.readSerial()
        receiveData.append(str(data.data))
    return receiveData

def asyncText(sender,data):
    for i in range(len(data)):
        add_label_text(str(i)+" ##"+str(i),data[i],parent="PortTextGroup")
        show_item(str(i)+' ##'+str(i))

def PortCloseCallbak(sender,data):
    global portControl
    portControl = False
    # 协程Async一直在读数据，如果不暂停会因为关闭com导致错误
    time.sleep(1)
    serGUI.onoffSignal=False
    serGUI.com.close()

with child("PortGroup",width=200,height=250):
    add_text(u"串口通讯设置")
    allPorts = getAllPortName()
    add_combo("Port##widget",allPorts,width=portWidth)
    add_combo("Baudrate##widget",[19200,9600],default_value="19200",width=portWidth)
    add_combo("DataBytes##widget",[8,7,6,5],width=portWidth,default_value="8")
    add_combo("Parity##widget",["None","Ord","Even","Mark","Space"],
              default_value="None",width=portWidth)
    add_combo("Stopbits##widget",[1,0,2],width=portWidth,default_value="1")
    add_button("OPEN##widget",width=50,callback=PortOpenCallback)
    add_same_line()
    add_button("CLOSE##widget",width=50,callback=PortCloseCallbak,callback_data=serGUI)

add_same_line()
with child("PortTextGroup",width=750,height=250):
    pass
add_separator()

setup_dearpygui()
while is_dearpygui_running():
    render_dearpygui_frame()
cleanup_dearpygui()
