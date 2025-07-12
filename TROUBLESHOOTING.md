# 故障排除指南

## 常见问题及解决方案

### 1. UUID已注册错误

**错误信息**: 
```
ERROR:__main__:蓝牙设置失败: org.bluez.Error.NotPermitted: UUID already registered
```

**解决方案**:

#### 方法1: 使用修复脚本（推荐）
```bash
# 运行蓝牙清理脚本
./fix_bluetooth.sh

# 等待脚本完成后，使用修复版本的程序
python3 bt_mouse_controller_fixed.py
```

#### 方法2: 手动清理
```bash
# 停止正在运行的程序
sudo pkill -f "bt_mouse_controller.py"
sudo pkill -f "BleMouse.py"

# 重启蓝牙服务
sudo systemctl restart bluetooth

# 重置蓝牙适配器
sudo hciconfig hci0 down
sudo hciconfig hci0 up

# 运行修复版本
python3 bt_mouse_controller_fixed.py
```

#### 方法3: 系统重启
```bash
# 如果上述方法都不行，重启系统
sudo reboot
```

### 2. 蓝牙适配器未启用

**错误信息**: 
```
✗ 蓝牙适配器未启用
```

**解决方案**:
```bash
# 启用蓝牙适配器
sudo hciconfig hci0 up

# 检查状态
hciconfig hci0
```

### 3. 蓝牙服务未运行

**错误信息**: 
```
✗ 蓝牙服务未运行
```

**解决方案**:
```bash
# 启动蓝牙服务
sudo systemctl start bluetooth

# 启用自动启动
sudo systemctl enable bluetooth

# 检查状态
sudo systemctl status bluetooth
```

### 4. 权限问题

**错误信息**: 
```
Permission denied
```

**解决方案**:
```bash
# 将用户添加到bluetooth组
sudo usermod -a -G bluetooth $USER

# 重新登录或重启系统
sudo reboot
```

### 5. Python依赖问题

**错误信息**: 
```
ModuleNotFoundError: No module named 'dbus'
```

**解决方案**:
```bash
# 重新安装依赖
pip3 install --user -r requirements.txt

# 或者运行安装脚本
./setup.sh
```

### 6. D-Bus服务不可访问

**错误信息**: 
```
✗ D-Bus BlueZ服务不可访问
```

**解决方案**:
```bash
# 检查D-Bus服务
sudo systemctl status dbus

# 重启D-Bus服务
sudo systemctl restart dbus

# 重启蓝牙服务
sudo systemctl restart bluetooth
```

### 7. iPhone连接问题

**问题**: iPhone无法发现或连接到树莓派

**解决方案**:
1. 确保树莓派程序正在运行
2. 在iPhone上删除之前的配对记录
3. 重新搜索蓝牙设备
4. 确保距离足够近（1-2米内）

### 8. 手势操作无效

**问题**: 连接成功但手势操作不生效

**解决方案**:
1. 检查是否有连接日志显示
2. 确保iPhone屏幕已解锁
3. 尝试在不同的应用中测试
4. 检查触摸坐标是否正确

## 调试命令

### 查看蓝牙状态
```bash
# 查看蓝牙适配器状态
hciconfig -a

# 查看蓝牙服务状态
sudo systemctl status bluetooth

# 查看已配对设备
bluetoothctl devices
```

### 查看程序日志
```bash
# 如果作为服务运行
sudo journalctl -u bt-hid-controller -f

# 如果手动运行，查看终端输出
```

### 测试蓝牙功能
```bash
# 运行蓝牙测试脚本
python3 test_bluetooth.py
```

## 程序版本说明

- **bt_mouse_controller.py**: 原始版本
- **bt_mouse_controller_fixed.py**: 修复版本，包含UUID冲突处理
- **fix_bluetooth.sh**: 蓝牙清理脚本

**建议**: 如果遇到UUID已注册错误，请使用修复版本的程序。

## 联系支持

如果以上方法都无法解决问题，请：

1. 运行测试脚本: `python3 test_bluetooth.py`
2. 记录错误信息和系统信息
3. 检查系统日志: `sudo journalctl -xe`

## 预防措施

1. 程序退出时请使用Ctrl+C正常退出，避免强制终止
2. 定期重启蓝牙服务以保持稳定性
3. 不要同时运行多个蓝牙HID程序
4. 建议定期更新系统和依赖包