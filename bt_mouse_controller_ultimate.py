#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
树莓派Zero 2W蓝牙HID触摸控制器 - 终极版本
使用不同的UUID和路径来避免冲突
支持连接iPhone并模拟各种手势操作
"""

import os
import sys
import time
import threading
import logging
import uuid
import random
from bluezero import adapter
from bluezero import device
from bluezero import dbus_tools
import dbus
import dbus.service
import dbus.mainloop.glib
from gi.repository import GLib
import signal

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BluetoothHIDService(dbus.service.Object):
    """蓝牙HID服务类"""
    
    # HID报告描述符 - 定义为触摸板设备
    HID_REPORT_DESCRIPTOR = bytes([
        0x05, 0x0d,                    # USAGE_PAGE (Digitizers)
        0x09, 0x05,                    # USAGE (Touch Pad)
        0xa1, 0x01,                    # COLLECTION (Application)
        0x85, 0x01,                    #   REPORT_ID (Touch)
        0x09, 0x22,                    #   USAGE (Finger)
        0xa1, 0x02,                    #   COLLECTION (Logical)
        0x09, 0x42,                    #     USAGE (Tip Switch)
        0x15, 0x00,                    #     LOGICAL_MINIMUM (0)
        0x25, 0x01,                    #     LOGICAL_MAXIMUM (1)
        0x75, 0x01,                    #     REPORT_SIZE (1)
        0x95, 0x01,                    #     REPORT_COUNT (1)
        0x81, 0x02,                    #     INPUT (Data,Var,Abs)
        0x95, 0x07,                    #     REPORT_COUNT (7)
        0x81, 0x03,                    #     INPUT (Cnst,Var,Abs)
        0x75, 0x08,                    #     REPORT_SIZE (8)
        0x09, 0x51,                    #     USAGE (Contact Identifier)
        0x95, 0x01,                    #     REPORT_COUNT (1)
        0x81, 0x02,                    #     INPUT (Data,Var,Abs)
        0x05, 0x01,                    #     USAGE_PAGE (Generic Desk..
        0x26, 0xff, 0x0f,              #     LOGICAL_MAXIMUM (4095)
        0x75, 0x10,                    #     REPORT_SIZE (16)
        0x55, 0x0e,                    #     UNIT_EXPONENT (-2)
        0x65, 0x13,                    #     UNIT (Inch,EngLinear)
        0x09, 0x30,                    #     USAGE (X)
        0x35, 0x00,                    #     PHYSICAL_MINIMUM (0)
        0x46, 0xb5, 0x04,              #     PHYSICAL_MAXIMUM (1205)
        0x81, 0x02,                    #     INPUT (Data,Var,Abs)
        0x46, 0x8a, 0x03,              #     PHYSICAL_MAXIMUM (906)
        0x09, 0x31,                    #     USAGE (Y)
        0x81, 0x02,                    #     INPUT (Data,Var,Abs)
        0xc0,                          #   END_COLLECTION
        0x05, 0x0d,                    #   USAGE_PAGE (Digitizers)
        0x09, 0x54,                    #   USAGE (Contact Count)
        0x95, 0x01,                    #   REPORT_COUNT (1)
        0x75, 0x08,                    #   REPORT_SIZE (8)
        0x81, 0x02,                    #   INPUT (Data,Var,Abs)
        0x09, 0x55,                    #   USAGE (Contact Count Maximum)
        0xb1, 0x02,                    #   FEATURE (Data,Var,Abs)
        0xc0                           # END_COLLECTION
    ])

    def __init__(self, bus, path):
        super().__init__(bus, path)
        self.bus = bus
        self.path = path
        self.interrupt_socket = None
        self.control_socket = None
        
    @dbus.service.method('org.bluez.Profile1', in_signature='oha{sv}', out_signature='')
    def NewConnection(self, path, fd, properties):
        """处理新的蓝牙连接"""
        logger.info(f"新连接: {path}")
        if 'interrupt' in str(properties):
            self.interrupt_socket = fd
            logger.info("中断通道已连接")
        else:
            self.control_socket = fd
            logger.info("控制通道已连接")

    @dbus.service.method('org.bluez.Profile1', in_signature='o', out_signature='')
    def RequestDisconnection(self, path):
        """处理断开连接请求"""
        logger.info(f"断开连接: {path}")
        if self.interrupt_socket:
            os.close(self.interrupt_socket)
            self.interrupt_socket = None
        if self.control_socket:
            os.close(self.control_socket)
            self.control_socket = None

    def send_report(self, report_data):
        """发送HID报告"""
        if self.interrupt_socket:
            try:
                os.write(self.interrupt_socket, report_data)
                return True
            except Exception as e:
                logger.error(f"发送报告失败: {e}")
                return False
        return False

class GestureController:
    """手势控制器"""
    
    def __init__(self, hid_service):
        self.hid_service = hid_service
        self.screen_width = 4095  # 逻辑坐标最大值
        self.screen_height = 4095
        
    def _create_touch_report(self, touch_active, x, y, contact_id=1):
        """创建触摸报告数据"""
        report = bytearray(8)
        report[0] = 0x01  # Report ID
        report[1] = 0x01 if touch_active else 0x00  # Tip switch
        report[2] = contact_id  # Contact identifier
        report[3] = x & 0xFF  # X coordinate low byte
        report[4] = (x >> 8) & 0xFF  # X coordinate high byte
        report[5] = y & 0xFF  # Y coordinate low byte
        report[6] = (y >> 8) & 0xFF  # Y coordinate high byte
        report[7] = 0x01 if touch_active else 0x00  # Contact count
        return bytes(report)

    def touch_down(self, x, y):
        """按下触摸"""
        report = self._create_touch_report(True, x, y)
        return self.hid_service.send_report(report)

    def touch_move(self, x, y):
        """移动触摸"""
        report = self._create_touch_report(True, x, y)
        return self.hid_service.send_report(report)

    def touch_up(self):
        """抬起触摸"""
        report = self._create_touch_report(False, 0, 0)
        return self.hid_service.send_report(report)

    def swipe_left(self, duration=0.5):
        """左滑手势"""
        logger.info("执行左滑手势")
        start_x = int(self.screen_width * 0.8)  # 右侧开始
        end_x = int(self.screen_width * 0.2)    # 左侧结束
        y = int(self.screen_height * 0.5)       # 屏幕中央
        
        return self._perform_swipe(start_x, y, end_x, y, duration)

    def swipe_right(self, duration=0.5):
        """右滑手势"""
        logger.info("执行右滑手势")
        start_x = int(self.screen_width * 0.2)  # 左侧开始
        end_x = int(self.screen_width * 0.8)    # 右侧结束
        y = int(self.screen_height * 0.5)       # 屏幕中央
        
        return self._perform_swipe(start_x, y, end_x, y, duration)

    def swipe_up(self, duration=0.5):
        """上滑手势"""
        logger.info("执行上滑手势")
        x = int(self.screen_width * 0.5)        # 屏幕中央
        start_y = int(self.screen_height * 0.8) # 底部开始
        end_y = int(self.screen_height * 0.2)   # 顶部结束
        
        return self._perform_swipe(x, start_y, x, end_y, duration)

    def swipe_down(self, duration=0.5):
        """下滑手势"""
        logger.info("执行下滑手势")
        x = int(self.screen_width * 0.5)        # 屏幕中央
        start_y = int(self.screen_height * 0.2) # 顶部开始
        end_y = int(self.screen_height * 0.8)   # 底部结束
        
        return self._perform_swipe(x, start_y, x, end_y, duration)

    def home_gesture(self):
        """返回主界面手势 (从底部上滑)"""
        logger.info("执行返回主界面手势")
        x = int(self.screen_width * 0.5)        # 屏幕中央
        start_y = int(self.screen_height * 0.95) # 底部边缘
        end_y = int(self.screen_height * 0.5)   # 屏幕中央
        
        return self._perform_swipe(x, start_y, x, end_y, 0.3)

    def _perform_swipe(self, start_x, start_y, end_x, end_y, duration):
        """执行滑动操作"""
        steps = 20  # 滑动步数
        step_delay = duration / steps
        
        # 按下
        if not self.touch_down(start_x, start_y):
            return False
            
        time.sleep(0.01)
        
        # 移动
        for i in range(1, steps):
            progress = i / (steps - 1)
            current_x = int(start_x + (end_x - start_x) * progress)
            current_y = int(start_y + (end_y - start_y) * progress)
            
            if not self.touch_move(current_x, current_y):
                self.touch_up()
                return False
                
            time.sleep(step_delay)
        
        # 抬起
        return self.touch_up()

class BluetoothHIDController:
    """主控制器"""
    
    def __init__(self):
        self.bus = None
        self.hid_service = None
        self.gesture_controller = None
        self.main_loop = None
        self.profile_registered = False
        
        # 生成唯一的路径和ID
        self.session_id = random.randint(1000, 9999)
        self.profile_path = f'/org/bluez/rpi_hid_{self.session_id}'
        
        # 使用不同的UUID（仍然是HID但避免冲突）
        self.hid_uuid = '00001124-0000-1000-8000-00805f9b34fb'
        
        logger.info(f"使用Profile路径: {self.profile_path}")
        logger.info(f"会话ID: {self.session_id}")

    def cleanup_all_possible_profiles(self):
        """清理所有可能的HID Profile"""
        try:
            profile_manager = dbus.Interface(
                self.bus.get_object('org.bluez', '/org/bluez'),
                'org.bluez.ProfileManager1'
            )
            
            # 尝试清理可能存在的路径
            paths_to_clean = [
                '/org/bluez/hid',
                '/org/bluez/profile/hid',
                '/profile/hid',
                '/hid',
                self.profile_path
            ]
            
            for path in paths_to_clean:
                try:
                    profile_manager.UnregisterProfile(path)
                    logger.info(f"清理了Profile路径: {path}")
                except Exception as e:
                    if 'Does Not Exist' not in str(e):
                        logger.debug(f"清理路径 {path}: {e}")
                        
            time.sleep(1)  # 等待清理完成
            
        except Exception as e:
            logger.warning(f"清理Profile时出错: {e}")

    def setup_bluetooth(self):
        """设置蓝牙"""
        try:
            # 初始化DBus
            dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
            self.bus = dbus.SystemBus()
            
            # 清理所有可能的冲突Profile
            self.cleanup_all_possible_profiles()
            
            # 创建HID服务
            self.hid_service = BluetoothHIDService(self.bus, self.profile_path)
            self.gesture_controller = GestureController(self.hid_service)
            
            # 获取ProfileManager
            profile_manager = dbus.Interface(
                self.bus.get_object('org.bluez', '/org/bluez'),
                'org.bluez.ProfileManager1'
            )
            
            profile_options = {
                'ServiceRecord': self._get_hid_service_record(),
                'Role': 'server',
                'RequireAuthentication': False,
                'RequireAuthorization': False
            }
            
            # 注册Profile
            profile_manager.RegisterProfile(
                self.profile_path,
                self.hid_uuid,
                profile_options
            )
            self.profile_registered = True
            logger.info(f"蓝牙HID服务已注册到路径: {self.profile_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"蓝牙设置失败: {e}")
            return False

    def _get_hid_service_record(self):
        """获取HID服务记录"""
        return """<?xml version="1.0" encoding="UTF-8" ?>
<record>
    <attribute id="0x0001">
        <sequence>
            <uuid value="0x1124" />
        </sequence>
    </attribute>
    <attribute id="0x0004">
        <sequence>
            <sequence>
                <uuid value="0x0100" />
                <uint16 value="0x0011" />
            </sequence>
            <sequence>
                <uuid value="0x0011" />
            </sequence>
        </sequence>
    </attribute>
    <attribute id="0x0005">
        <sequence>
            <uuid value="0x1002" />
        </sequence>
    </attribute>
    <attribute id="0x0006">
        <sequence>
            <uint16 value="0x656e" />
            <uint16 value="0x006a" />
            <uint16 value="0x0100" />
        </sequence>
    </attribute>
    <attribute id="0x0009">
        <sequence>
            <sequence>
                <uuid value="0x1124" />
                <uint16 value="0x0100" />
            </sequence>
        </sequence>
    </attribute>
    <attribute id="0x000d">
        <sequence>
            <sequence>
                <sequence>
                    <uuid value="0x0100" />
                    <uint16 value="0x0013" />
                </sequence>
                <sequence>
                    <uuid value="0x0011" />
                </sequence>
            </sequence>
        </sequence>
    </attribute>
    <attribute id="0x0100">
        <text value="RaspberryPi HID Touch" />
    </attribute>
    <attribute id="0x0101">
        <text value="Virtual Touch Pad Controller" />
    </attribute>
    <attribute id="0x0102">
        <text value="RaspberryPi Foundation" />
    </attribute>
    <attribute id="0x0200">
        <uint16 value="0x0100" />
    </attribute>
    <attribute id="0x0201">
        <uint16 value="0x0111" />
    </attribute>
    <attribute id="0x0202">
        <uint8 value="0x40" />
    </attribute>
    <attribute id="0x0203">
        <uint8 value="0x21" />
    </attribute>
    <attribute id="0x0204">
        <boolean value="false" />
    </attribute>
    <attribute id="0x0205">
        <boolean value="true" />
    </attribute>
    <attribute id="0x0206">
        <sequence>
            <sequence>
                <uint8 value="0x22" />
                <text encoding="hex" value="%s" />
            </sequence>
        </sequence>
    </attribute>
    <attribute id="0x0207">
        <sequence>
            <sequence>
                <uint16 value="0x0409" />
                <uint16 value="0x0100" />
            </sequence>
        </sequence>
    </attribute>
    <attribute id="0x020b">
        <uint16 value="0x0100" />
    </attribute>
    <attribute id="0x020c">
        <uint16 value="0x0c80" />
    </attribute>
    <attribute id="0x020d">
        <boolean value="false" />
    </attribute>
    <attribute id="0x020e">
        <boolean value="true" />
    </attribute>
    <attribute id="0x020f">
        <uint16 value="0x0640" />
    </attribute>
    <attribute id="0x0210">
        <uint16 value="0x0320" />
    </attribute>
</record>""" % self.hid_service.HID_REPORT_DESCRIPTOR.hex()

    def make_discoverable(self):
        """使设备可被发现"""
        try:
            adapter_obj = self.bus.get_object('org.bluez', '/org/bluez/hci0')
            adapter_props = dbus.Interface(adapter_obj, 'org.freedesktop.DBus.Properties')
            
            # 设置设备名称包含会话ID
            adapter_props.Set('org.bluez.Adapter1', 'Alias', f'RaspberryPi HID Touch ({self.session_id})')
            adapter_props.Set('org.bluez.Adapter1', 'Discoverable', True)
            adapter_props.Set('org.bluez.Adapter1', 'Pairable', True)
            adapter_props.Set('org.bluez.Adapter1', 'DiscoverableTimeout', 0)
            
            logger.info(f"设备现在可被发现，名称: RaspberryPi HID Touch ({self.session_id})")
            return True
            
        except Exception as e:
            logger.error(f"设置可发现模式失败: {e}")
            return False

    def run_command_interface(self):
        """运行命令行界面"""
        print(f"\n🎮 树莓派蓝牙触摸控制器 [会话:{self.session_id}]")
        print("=" * 50)
        print("可用命令:")
        print("1 - 左滑")
        print("2 - 右滑") 
        print("3 - 上滑")
        print("4 - 下滑")
        print("5 - 返回主界面")
        print("q - 退出")
        print("=" * 50)
        
        while True:
            try:
                cmd = input("\n请输入命令: ").strip().lower()
                
                if cmd == 'q':
                    break
                elif cmd == '1':
                    self.gesture_controller.swipe_left()
                elif cmd == '2':
                    self.gesture_controller.swipe_right()
                elif cmd == '3':
                    self.gesture_controller.swipe_up()
                elif cmd == '4':
                    self.gesture_controller.swipe_down()
                elif cmd == '5':
                    self.gesture_controller.home_gesture()
                else:
                    print("无效命令，请重试")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"命令执行错误: {e}")

    def cleanup(self):
        """清理资源"""
        try:
            if self.profile_registered:
                profile_manager = dbus.Interface(
                    self.bus.get_object('org.bluez', '/org/bluez'),
                    'org.bluez.ProfileManager1'
                )
                profile_manager.UnregisterProfile(self.profile_path)
                logger.info(f"已取消注册HID Profile: {self.profile_path}")
                
            if self.hid_service:
                if self.hid_service.interrupt_socket:
                    os.close(self.hid_service.interrupt_socket)
                if self.hid_service.control_socket:
                    os.close(self.hid_service.control_socket)
                    
        except Exception as e:
            logger.error(f"清理资源时出错: {e}")

    def signal_handler(self, signum, frame):
        """信号处理器"""
        logger.info("接收到退出信号，正在清理...")
        self.cleanup()
        if self.main_loop:
            self.main_loop.quit()
        sys.exit(0)

    def run(self):
        """运行主程序"""
        # 设置信号处理器
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        if not self.setup_bluetooth():
            return False
            
        if not self.make_discoverable():
            return False
            
        print(f"🚀 蓝牙HID服务已启动 [会话:{self.session_id}]")
        print(f"📱 在iPhone蓝牙设置中搜索: 'RaspberryPi HID Touch ({self.session_id})'")
        print("⚡ 等待iPhone连接...")
        
        # 在新线程中运行命令界面
        cmd_thread = threading.Thread(target=self.run_command_interface)
        cmd_thread.daemon = True
        cmd_thread.start()
        
        # 运行主循环
        try:
            self.main_loop = GLib.MainLoop()
            self.main_loop.run()
        except KeyboardInterrupt:
            logger.info("程序被用户中断")
        finally:
            self.cleanup()
        
        return True

def main():
    """主函数"""
    controller = BluetoothHIDController()
    try:
        controller.run()
    except Exception as e:
        logger.error(f"程序运行错误: {e}")
        controller.cleanup()
        return 1
    return 0

if __name__ == '__main__':
    sys.exit(main())