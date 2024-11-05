#!/bin/bash

# 激活Python虚拟环境（如果使用）
source venv/bin/activate

# 检查配置文件
if [ ! -f config/.env ]; then
    echo "Error: Missing .env file"
    exit 1
fi

# 初始化数据库
python3 scripts/init_db.py

# 启动主程序
python3 src/main.py
