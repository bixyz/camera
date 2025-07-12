#!/bin/bash

# 快速解决UUID已注册问题的脚本

echo "🔧 快速修复蓝牙UUID已注册问题"
echo "=================================="

# 检查是否有正在运行的相关程序
echo "1. 停止正在运行的蓝牙HID程序..."
sudo pkill -f "bt_mouse_controller.py" 2>/dev/null || true
sudo pkill -f "BleMouse.py" 2>/dev/null || true
sudo pkill -f "bt_mouse_controller_fixed.py" 2>/dev/null || true

# 等待程序完全停止
sleep 2

echo "2. 清理蓝牙HID Profile..."
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
        print("✓ HID Profile已清理")
    except Exception as e:
        print(f"注意: HID Profile清理失败（可能本来就没有注册）: {e}")
        
except Exception as e:
    print(f"警告: D-Bus操作失败: {e}")
    print("建议重启蓝牙服务")
EOF

echo "3. 重启蓝牙服务..."
sudo systemctl restart bluetooth
sleep 3

echo "4. 重置蓝牙适配器..."
sudo hciconfig hci0 down
sleep 1
sudo hciconfig hci0 up
sleep 2

echo "5. 检查修复状态..."
if systemctl is-active --quiet bluetooth; then
    echo "✓ 蓝牙服务运行正常"
else
    echo "✗ 蓝牙服务异常，请检查"
    exit 1
fi

if hciconfig hci0 | grep -q "UP RUNNING"; then
    echo "✓ 蓝牙适配器运行正常"
else
    echo "✗ 蓝牙适配器异常，请检查"
    exit 1
fi

echo ""
echo "🎉 修复完成！"
echo "=================================="
echo "现在可以运行以下命令启动程序:"
echo "  python3 bt_mouse_controller_fixed.py"
echo ""
echo "或者使用快速启动脚本:"
echo "  ./start_fixed.sh"
echo ""

# 询问是否立即启动
read -p "是否立即启动修复版本的程序？(y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "启动修复版本程序..."
    python3 bt_mouse_controller_fixed.py
fi