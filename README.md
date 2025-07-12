# 树莓派Zero 2W蓝牙HID触摸控制器

这是一个运行在树莓派Zero 2W上的蓝牙HID程序，可以通过蓝牙连接iPhone并模拟触摸手势操作。

## 功能特性

- 🔗 蓝牙HID连接iPhone
- 👆 模拟触摸手势操作
- ⬅️ 左滑手势
- ➡️ 右滑手势  
- ⬆️ 上滑手势
- ⬇️ 下滑手势
- 🏠 返回主界面手势
- 🎮 交互式命令界面

## 系统要求

- 树莓派Zero 2W
- Raspberry Pi OS (推荐最新版本)
- Python 3.7+
- 蓝牙功能正常

## 安装步骤

### 1. 下载代码

```bash
# 克隆或下载代码到树莓派
git clone <repository-url>
cd bluetooth-hid-controller
```

### 2. 运行安装脚本

```bash
# 给安装脚本执行权限
chmod +x setup.sh

# 运行安装脚本
./setup.sh
```

安装脚本会自动：
- 更新系统包
- 安装必要的系统依赖
- 安装Python依赖
- 配置蓝牙服务
- 创建系统服务
- 设置权限

### 3. 重启系统

```bash
sudo reboot
```

## 使用方法

### 手动运行

```bash
python3 bt_mouse_controller.py
```

### 作为系统服务运行

```bash
# 启用自动启动
sudo systemctl enable bt-hid-controller

# 启动服务
sudo systemctl start bt-hid-controller

# 查看服务状态
sudo systemctl status bt-hid-controller

# 查看日志
sudo journalctl -u bt-hid-controller -f
```

## 连接iPhone

1. 在树莓派上运行程序后，设备会变为可发现状态
2. 在iPhone上打开：**设置 > 蓝牙**
3. 搜索并连接到 **"RaspberryPi HID"**
4. 连接成功后，程序会显示连接状态

## 手势操作

程序运行后会显示交互式命令界面：

```
树莓派蓝牙触摸控制器
==============================
可用命令:
1 - 左滑
2 - 右滑
3 - 上滑
4 - 下滑
5 - 返回主界面
q - 退出
==============================
```

输入对应数字即可执行相应手势。

## 手势说明

- **左滑 (1)**: 从屏幕右侧向左滑动，用于返回上一页或切换界面
- **右滑 (2)**: 从屏幕左侧向右滑动，用于前进或切换界面
- **上滑 (3)**: 从屏幕底部向上滑动，用于显示更多内容
- **下滑 (4)**: 从屏幕顶部向下滑动，用于刷新或显示通知
- **返回主界面 (5)**: 从屏幕底部边缘向上滑动，模拟iPhone的Home手势

## 故障排除

### 蓝牙连接问题

如果无法连接蓝牙：

```bash
# 检查蓝牙状态
sudo systemctl status bluetooth

# 重启蓝牙服务
sudo systemctl restart bluetooth

# 检查蓝牙设备
hciconfig -a
```

### 权限问题

如果出现权限错误：

```bash
# 将用户添加到bluetooth组
sudo usermod -a -G bluetooth $USER

# 重启系统
sudo reboot
```

### 依赖问题

如果缺少依赖包：

```bash
# 重新安装依赖
pip3 install --user -r requirements.txt

# 或手动安装
pip3 install --user bluezero dbus-python PyGObject
```

## 自定义配置

### 修改设备名称

编辑 `/etc/bluetooth/main.conf` 文件中的 `Name` 字段：

```ini
[General]
Name = 你的设备名称
```

### 调整手势参数

在 `bt_mouse_controller.py` 中的 `GestureController` 类中，可以调整：

- `duration`: 手势持续时间
- `steps`: 手势步数（影响平滑度）
- 坐标范围和起始位置

## 注意事项

1. **安全性**: 此程序会让树莓派作为HID设备连接到iPhone，请确保在安全的环境中使用
2. **电源**: 树莓派Zero 2W功耗较低，但建议使用稳定的电源
3. **兼容性**: 主要针对iPhone设计，其他设备可能需要调整
4. **距离**: 蓝牙连接距离一般在10米左右
5. **权限**: 某些操作需要root权限，请根据提示执行

## 技术原理

程序使用蓝牙HID协议模拟触摸板设备：

1. **HID报告描述符**: 定义设备为触摸板
2. **D-Bus接口**: 与BlueZ蓝牙栈通信
3. **触摸报告**: 发送触摸坐标和状态
4. **手势模拟**: 通过连续的触摸点移动模拟手势

## 许可证

本项目仅供学习和研究使用，请遵守相关法律法规。

## 支持

如果遇到问题，请检查：
- 系统日志: `sudo journalctl -u bt-hid-controller`
- 蓝牙状态: `sudo systemctl status bluetooth`
- 设备连接: `hciconfig` 和 `bluetoothctl`