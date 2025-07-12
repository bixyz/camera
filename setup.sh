#!/bin/bash

# 树莓派Zero 2W蓝牙HID控制器安装脚本

set -e

echo "正在安装树莓派蓝牙HID控制器..."
echo "=================================="

# 更新系统
echo "更新系统包..."
sudo apt update
sudo apt upgrade -y

# 安装必要的系统包
echo "安装系统依赖包..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-dev \
    python3-gi \
    python3-gi-cairo \
    gir1.2-gtk-3.0 \
    bluez \
    bluez-tools \
    libbluetooth-dev \
    libdbus-1-dev \
    libglib2.0-dev \
    libcairo2-dev \
    libgirepository1.0-dev \
    pkg-config

# 安装Python依赖
echo "安装Python依赖包..."
pip3 install --user -r requirements.txt

# 启用蓝牙服务
echo "配置蓝牙服务..."
sudo systemctl enable bluetooth
sudo systemctl start bluetooth

# 配置蓝牙HID
echo "配置蓝牙HID支持..."
sudo cp /etc/bluetooth/main.conf /etc/bluetooth/main.conf.backup

# 修改蓝牙配置
sudo tee /etc/bluetooth/main.conf > /dev/null <<EOF
[General]
Name = RaspberryPi HID
Class = 0x002540
DiscoverableTimeout = 0
PairableTimeout = 0
AutoConnectTimeout = 60
EnableGatt = true

[Policy]
AutoEnable = true
EOF

# 重启蓝牙服务
sudo systemctl restart bluetooth

# 创建服务文件
echo "创建系统服务..."
sudo tee /etc/systemd/system/bt-hid-controller.service > /dev/null <<EOF
[Unit]
Description=Bluetooth HID Controller
After=bluetooth.service
Requires=bluetooth.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi
ExecStart=/usr/bin/python3 /home/pi/bt_mouse_controller.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# 设置权限
echo "设置权限..."
chmod +x bt_mouse_controller.py
sudo usermod -a -G bluetooth pi

echo ""
echo "=================================="
echo "安装完成！"
echo ""
echo "使用方法："
echo "1. 手动运行: python3 bt_mouse_controller.py"
echo "2. 启用自动启动: sudo systemctl enable bt-hid-controller"
echo "3. 启动服务: sudo systemctl start bt-hid-controller"
echo ""
echo "在iPhone上：设置 > 蓝牙 > 搜索并连接 'RaspberryPi HID'"
echo ""
echo "注意：如果遇到权限问题，请重启系统。"