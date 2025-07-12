#!/bin/bash

# 蓝牙HID服务清理和修复脚本

echo "正在清理蓝牙HID服务..."
echo "================================"

# 停止可能正在运行的HID服务
echo "1. 停止现有HID服务..."
sudo pkill -f "bt_mouse_controller.py" || true
sudo pkill -f "BleMouse.py" || true

# 停止蓝牙服务
echo "2. 重启蓝牙服务..."
sudo systemctl stop bluetooth
sleep 2

# 清理蓝牙缓存和配置
echo "3. 清理蓝牙缓存..."
sudo rm -rf /var/lib/bluetooth/*/cache/ || true

# 重启蓝牙服务
sudo systemctl start bluetooth
sleep 3

# 重置蓝牙适配器
echo "4. 重置蓝牙适配器..."
sudo hciconfig hci0 down
sleep 1
sudo hciconfig hci0 up
sleep 2

# 清理已注册的HID Profile
echo "5. 清理已注册的HID Profile..."
python3 << 'EOF'
import dbus
import dbus.mainloop.glib
import sys

try:
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    
    # 尝试取消注册HID Profile
    profile_manager = dbus.Interface(
        bus.get_object('org.bluez', '/org/bluez'),
        'org.bluez.ProfileManager1'
    )
    
    try:
        profile_manager.UnregisterProfile('/org/bluez/hid')
        print("✓ HID Profile已取消注册")
    except Exception as e:
        print(f"HID Profile取消注册失败（可能本来就没有注册）: {e}")
        
except Exception as e:
    print(f"D-Bus操作失败: {e}")
EOF

# 检查蓝牙服务状态
echo "6. 检查蓝牙服务状态..."
if systemctl is-active --quiet bluetooth; then
    echo "✓ 蓝牙服务运行正常"
else
    echo "✗ 蓝牙服务未运行"
    sudo systemctl start bluetooth
fi

# 检查蓝牙适配器状态
echo "7. 检查蓝牙适配器状态..."
if hciconfig hci0 | grep -q "UP RUNNING"; then
    echo "✓ 蓝牙适配器运行正常"
else
    echo "✗ 蓝牙适配器未运行"
    sudo hciconfig hci0 up
fi

echo ""
echo "================================"
echo "蓝牙服务清理完成！"
echo "现在可以重新运行HID控制器程序了。"
echo "================================"