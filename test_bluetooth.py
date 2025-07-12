#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蓝牙功能测试脚本
用于验证树莓派蓝牙和HID功能是否正常
"""

import subprocess
import sys
import time
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_bluetooth_service():
    """检查蓝牙服务状态"""
    try:
        result = subprocess.run(['systemctl', 'is-active', 'bluetooth'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            logger.info("✓ 蓝牙服务运行正常")
            return True
        else:
            logger.error("✗ 蓝牙服务未运行")
            return False
    except Exception as e:
        logger.error(f"✗ 检查蓝牙服务失败: {e}")
        return False

def check_bluetooth_adapter():
    """检查蓝牙适配器"""
    try:
        result = subprocess.run(['hciconfig'], capture_output=True, text=True)
        if result.returncode == 0 and 'hci0' in result.stdout:
            logger.info("✓ 蓝牙适配器检测到")
            if 'UP RUNNING' in result.stdout:
                logger.info("✓ 蓝牙适配器已启用")
                return True
            else:
                logger.warning("⚠ 蓝牙适配器未启用，尝试启用...")
                subprocess.run(['sudo', 'hciconfig', 'hci0', 'up'], check=True)
                time.sleep(2)
                return check_bluetooth_adapter()
        else:
            logger.error("✗ 未检测到蓝牙适配器")
            return False
    except Exception as e:
        logger.error(f"✗ 检查蓝牙适配器失败: {e}")
        return False

def check_python_dependencies():
    """检查Python依赖"""
    dependencies = ['dbus', 'bluezero', 'gi']
    all_good = True
    
    for dep in dependencies:
        try:
            __import__(dep)
            logger.info(f"✓ {dep} 已安装")
        except ImportError:
            logger.error(f"✗ {dep} 未安装")
            all_good = False
    
    return all_good

def check_dbus_service():
    """检查D-Bus服务"""
    try:
        import dbus
        bus = dbus.SystemBus()
        bluez_obj = bus.get_object('org.bluez', '/org/bluez')
        logger.info("✓ D-Bus BlueZ服务可访问")
        return True
    except Exception as e:
        logger.error(f"✗ D-Bus BlueZ服务不可访问: {e}")
        return False

def check_bluetooth_permissions():
    """检查蓝牙权限"""
    try:
        import os
        import pwd
        
        # 获取当前用户
        current_user = pwd.getpwuid(os.getuid()).pw_name
        
        # 检查是否在bluetooth组中
        result = subprocess.run(['groups', current_user], capture_output=True, text=True)
        if 'bluetooth' in result.stdout:
            logger.info("✓ 用户有蓝牙权限")
            return True
        else:
            logger.warning("⚠ 用户没有蓝牙权限")
            logger.info("请运行: sudo usermod -a -G bluetooth $USER")
            return False
    except Exception as e:
        logger.error(f"✗ 检查蓝牙权限失败: {e}")
        return False

def test_bluetooth_scan():
    """测试蓝牙扫描功能"""
    try:
        logger.info("测试蓝牙扫描功能...")
        result = subprocess.run(['timeout', '10', 'bluetoothctl', 'scan', 'on'], 
                              capture_output=True, text=True)
        if result.returncode == 0 or result.returncode == 124:  # 124是timeout的返回码
            logger.info("✓ 蓝牙扫描功能正常")
            return True
        else:
            logger.error("✗ 蓝牙扫描功能异常")
            return False
    except Exception as e:
        logger.error(f"✗ 测试蓝牙扫描失败: {e}")
        return False

def test_hid_service():
    """测试HID服务配置"""
    try:
        # 检查HID UUID是否已注册
        result = subprocess.run(['sdptool', 'browse', 'local'], 
                              capture_output=True, text=True)
        if '0x1124' in result.stdout:
            logger.info("✓ HID服务已注册")
            return True
        else:
            logger.warning("⚠ HID服务未注册")
            return False
    except Exception as e:
        logger.warning(f"⚠ 无法检查HID服务: {e}")
        return True  # 不是致命错误

def run_all_tests():
    """运行所有测试"""
    logger.info("开始蓝牙功能测试...")
    logger.info("=" * 50)
    
    tests = [
        ("蓝牙服务状态", check_bluetooth_service),
        ("蓝牙适配器", check_bluetooth_adapter),
        ("Python依赖", check_python_dependencies),
        ("D-Bus服务", check_dbus_service),
        ("蓝牙权限", check_bluetooth_permissions),
        ("蓝牙扫描", test_bluetooth_scan),
        ("HID服务", test_hid_service),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n测试: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"测试 {test_name} 出错: {e}")
            results.append((test_name, False))
    
    logger.info("\n" + "=" * 50)
    logger.info("测试结果汇总:")
    logger.info("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        logger.info("🎉 所有测试通过！蓝牙HID功能应该可以正常工作。")
        return True
    else:
        logger.warning("⚠ 部分测试失败，请根据上面的提示进行修复。")
        return False

def main():
    """主函数"""
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print("蓝牙功能测试脚本")
        print("用法: python3 test_bluetooth.py")
        print("\n这个脚本会检查:")
        print("- 蓝牙服务状态")
        print("- 蓝牙适配器")
        print("- Python依赖")
        print("- D-Bus服务")
        print("- 蓝牙权限")
        print("- 蓝牙扫描功能")
        print("- HID服务配置")
        return 0
    
    success = run_all_tests()
    return 0 if success else 1

if __name__ == '__main__':
    sys.exit(main())