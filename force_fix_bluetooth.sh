#!/bin/bash

# 强力蓝牙清理脚本 - 彻底解决UUID冲突问题

echo "🔥 强力清理蓝牙服务 - 解决顽固UUID冲突"
echo "============================================="

# 停止所有相关程序
echo "1. 停止所有蓝牙HID相关程序..."
sudo pkill -9 -f "bt_mouse_controller" 2>/dev/null || true
sudo pkill -9 -f "BleMouse" 2>/dev/null || true
sudo pkill -9 -f "python3.*hid" 2>/dev/null || true
sleep 2

# 检查已注册的profile
echo "2. 检查当前已注册的Profile..."
python3 << 'EOF'
import dbus
import dbus.mainloop.glib

try:
    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
    bus = dbus.SystemBus()
    
    # 获取所有已注册的objects
    bluez_obj = bus.get_object('org.bluez', '/')
    object_manager = dbus.Interface(bluez_obj, 'org.freedesktop.DBus.ObjectManager')
    objects = object_manager.GetManagedObjects()
    
    print("当前BlueZ管理的对象:")
    for path in objects:
        print(f"  - {path}")
        
    # 尝试清理可能的HID profile路径
    profile_manager = dbus.Interface(
        bus.get_object('org.bluez', '/org/bluez'),
        'org.bluez.ProfileManager1'
    )
    
    # 尝试多个可能的路径
    paths_to_try = [
        '/org/bluez/hid',
        '/org/bluez/profile/hid',
        '/profile/hid',
        '/hid'
    ]
    
    for path in paths_to_try:
        try:
            profile_manager.UnregisterProfile(path)
            print(f"✓ 清理了路径: {path}")
        except Exception as e:
            print(f"路径 {path}: {e}")
            
except Exception as e:
    print(f"D-Bus操作失败: {e}")
EOF

# 停止蓝牙服务
echo "3. 完全停止蓝牙服务..."
sudo systemctl stop bluetooth
sleep 3

# 清理蓝牙缓存和配置
echo "4. 清理蓝牙缓存和临时文件..."
sudo rm -rf /var/lib/bluetooth/*/cache/ 2>/dev/null || true
sudo rm -rf /tmp/.bluetoothd* 2>/dev/null || true
sudo rm -rf /run/bluetoothd* 2>/dev/null || true

# 重置蓝牙适配器
echo "5. 重置蓝牙硬件..."
sudo hciconfig hci0 down 2>/dev/null || true
sleep 2
sudo rmmod btusb 2>/dev/null || true
sudo rmmod bluetooth 2>/dev/null || true
sleep 2
sudo modprobe bluetooth
sudo modprobe btusb
sleep 3

# 启动蓝牙服务
echo "6. 重启蓝牙服务..."
sudo systemctl start bluetooth
sleep 5

# 启用蓝牙适配器
echo "7. 启用蓝牙适配器..."
sudo hciconfig hci0 up
sleep 2

# 验证蓝牙状态
echo "8. 验证蓝牙状态..."
if systemctl is-active --quiet bluetooth; then
    echo "✅ 蓝牙服务运行正常"
else
    echo "❌ 蓝牙服务异常"
    echo "尝试手动启动..."
    sudo systemctl start bluetooth
    sleep 3
fi

if hciconfig hci0 2>/dev/null | grep -q "UP RUNNING"; then
    echo "✅ 蓝牙适配器运行正常"
else
    echo "❌ 蓝牙适配器异常"
    echo "尝试手动启用..."
    sudo hciconfig hci0 up
    sleep 2
fi

# 显示当前蓝牙状态
echo "9. 当前蓝牙状态:"
echo "   服务状态: $(systemctl is-active bluetooth)"
echo "   适配器状态:"
hciconfig hci0 2>/dev/null | head -2 || echo "   适配器不可用"

echo ""
echo "🎉 强力清理完成！"
echo "============================================="
echo "建议措施:"
echo "1. 等待10秒让系统稳定"
echo "2. 使用修改过的程序版本（使用不同的UUID）"
echo "3. 如果仍有问题，请重启系统"
echo ""

# 等待系统稳定
echo "等待系统稳定..."
sleep 10

echo "现在可以尝试运行程序了！"