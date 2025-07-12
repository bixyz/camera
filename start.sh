#!/bin/bash

# 快速启动蓝牙HID控制器

echo "启动树莓派蓝牙HID控制器..."

# 检查是否已安装
if [ ! -f "bt_mouse_controller.py" ]; then
    echo "错误: 找不到主程序文件"
    exit 1
fi

# 检查蓝牙服务
if ! systemctl is-active --quiet bluetooth; then
    echo "启动蓝牙服务..."
    sudo systemctl start bluetooth
    sleep 2
fi

# 检查蓝牙适配器
if ! hciconfig hci0 | grep -q "UP RUNNING"; then
    echo "启用蓝牙适配器..."
    sudo hciconfig hci0 up
    sleep 2
fi

# 检查Python依赖
if ! python3 -c "import dbus, bluezero, gi" 2>/dev/null; then
    echo "错误: Python依赖不完整，请先运行 ./setup.sh"
    exit 1
fi

echo "启动HID控制器..."
python3 bt_mouse_controller.py