#!/bin/bash

# 一键解决UUID冲突问题的脚本

echo "🎯 一键解决UUID冲突问题"
echo "========================="
echo ""

# 检查参数
if [ "$1" = "--force" ]; then
    echo "使用强力清理模式..."
    FORCE_MODE=true
else
    echo "使用标准清理模式..."
    FORCE_MODE=false
fi

echo ""
echo "解决方案选择:"
echo "1. 强力清理 + 终极版本程序（推荐）"
echo "2. 仅使用终极版本程序"
echo "3. 强力清理 + 修复版本程序"
echo ""

read -p "请选择解决方案 (1-3): " choice

case $choice in
    1)
        echo ""
        echo "🔥 执行强力清理..."
        ./force_fix_bluetooth.sh
        
        echo ""
        echo "🚀 启动终极版本程序..."
        python3 bt_mouse_controller_ultimate.py
        ;;
    2)
        echo ""
        echo "🚀 直接启动终极版本程序..."
        python3 bt_mouse_controller_ultimate.py
        ;;
    3)
        echo ""
        echo "🔥 执行强力清理..."
        ./force_fix_bluetooth.sh
        
        echo ""
        echo "🚀 启动修复版本程序..."
        python3 bt_mouse_controller_fixed.py
        ;;
    *)
        echo "❌ 无效选择，退出"
        exit 1
        ;;
esac