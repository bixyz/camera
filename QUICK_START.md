# 🚀 快速开始指南 - 解决UUID冲突

## 🎯 您的问题
遇到错误：`org.bluez.Error.NotPermitted: UUID already registered`

## ✅ 立即解决

### 最简单的方法（推荐）
```bash
./solve_uuid_problem.sh
```
选择选项 **1** - 强力清理 + 终极版本程序

### 或者直接使用终极版本
```bash
python3 bt_mouse_controller_ultimate.py
```

## 📱 连接iPhone

1. 程序启动后会显示：
   ```
   📱 在iPhone蓝牙设置中搜索: 'RaspberryPi HID Touch (1234)'
   ```

2. 在iPhone上：**设置 > 蓝牙** → 搜索并连接

3. 使用数字键控制手势：
   - **1** - 左滑
   - **2** - 右滑  
   - **3** - 上滑
   - **4** - 下滑
   - **5** - 返回主界面

## 🔧 如果还是有问题

### 强力清理
```bash
./force_fix_bluetooth.sh
```

### 系统重启（最后手段）
```bash
sudo reboot
```

## 📂 主要文件说明

- **bt_mouse_controller_ultimate.py** - 🌟 终极版本（避免UUID冲突）
- **solve_uuid_problem.sh** - 🎯 一键解决方案
- **force_fix_bluetooth.sh** - 🔥 强力清理工具

## 💡 为什么终极版本更好？

✅ 每次运行使用不同的路径  
✅ 自动清理冲突的注册信息  
✅ 随机会话ID避免重复  
✅ 更稳定的连接  

---

**就这么简单！现在您应该可以正常使用蓝牙HID控制iPhone了。** 🎉