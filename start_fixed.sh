#!/bin/bash

# 启动修复版本的蓝牙HID控制器

echo "🚀 启动树莓派蓝牙HID控制器（修复版）"
echo "========================================"

# 检查是否存在修复版本文件
if [ ! -f "bt_mouse_controller_fixed.py" ]; then
    echo "❌ 错误: 找不到修复版本文件 bt_mouse_controller_fixed.py"
    exit 1
fi

# 预检查
echo "1. 检查系统状态..."

# 检查蓝牙服务
if ! systemctl is-active --quiet bluetooth; then
    echo "⚠️  蓝牙服务未运行，正在启动..."
    sudo systemctl start bluetooth
    sleep 2
    if ! systemctl is-active --quiet bluetooth; then
        echo "❌ 无法启动蓝牙服务"
        exit 1
    fi
fi
echo "✅ 蓝牙服务运行正常"

# 检查蓝牙适配器
if ! hciconfig hci0 2>/dev/null | grep -q "UP RUNNING"; then
    echo "⚠️  蓝牙适配器未启用，正在启用..."
    sudo hciconfig hci0 up
    sleep 2
    if ! hciconfig hci0 2>/dev/null | grep -q "UP RUNNING"; then
        echo "❌ 无法启用蓝牙适配器"
        exit 1
    fi
fi
echo "✅ 蓝牙适配器运行正常"

# 检查Python依赖
echo "2. 检查Python依赖..."
if ! python3 -c "import dbus, bluezero, gi" 2>/dev/null; then
    echo "❌ Python依赖不完整，请先运行: ./setup.sh"
    exit 1
fi
echo "✅ Python依赖完整"

# 停止可能存在的冲突程序
echo "3. 清理现有程序..."
sudo pkill -f "bt_mouse_controller.py" 2>/dev/null || true
sudo pkill -f "BleMouse.py" 2>/dev/null || true
sleep 1

# 显示启动信息
echo ""
echo "========================================"
echo "✅ 系统检查完成，准备启动程序"
echo ""
echo "📱 连接步骤:"
echo "   1. 等待程序启动完成"
echo "   2. 在iPhone上打开: 设置 > 蓝牙" 
echo "   3. 搜索并连接到 'RaspberryPi HID'"
echo "   4. 连接成功后可使用手势控制"
echo ""
echo "🎮 可用命令:"
echo "   1 - 左滑    2 - 右滑    3 - 上滑"
echo "   4 - 下滑    5 - 返回主界面    q - 退出"
echo ""
echo "按 Ctrl+C 可以安全退出程序"
echo "========================================"
echo ""

# 启动修复版本程序
echo "🔥 启动蓝牙HID控制器..."
python3 bt_mouse_controller_fixed.py