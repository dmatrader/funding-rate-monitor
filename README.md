# 加密货币资金费率监控系统 / Cryptocurrency Funding Rate Monitor

> 实时监控币安和OKX交易所的资金费率，提供Web仪表盘展示 | Real-time monitoring of funding rates from Binance and OKX exchanges with web dashboard

## 📖 项目介绍 / Project Description

**中文**: 这是一个基于 Python 和 Flask 的加密货币资金费率监控系统，支持币安和OKX两大交易所的资金费率数据收集、分析和可视化展示。系统提供实时资金费率监控、高频交易对识别、预警功能等，帮助交易者了解市场资金成本和套利机会。

**English**: This is a cryptocurrency funding rate monitoring system based on Python and Flask, supporting funding rate data collection, analysis and visualization from Binance and OKX exchanges. The system provides real-time funding rate monitoring, high-frequency trading pair identification, and alert functions to help traders understand market funding costs and arbitrage opportunities.

## 🚀 在线演示 / Live Demo

**[点击体验 / Click to Experience](https://dmatrader.github.io/funding-rate-monitor/)**

## ✨ 功能特性 / Features

- 📊 **实时资金费率监控** - 监控币安和OKX的资金费率变化
- 🔥 **Top10排行榜** - 显示资金费率最高和最低的交易对
- ⚡ **高频交易对识别** - 识别资金费率更新频率<4小时的交易对
- ⚠️ **预警功能** - 当资金费率超过阈值时自动预警
- 📱 **Web界面展示** - 直观的Web仪表盘，支持自动刷新
- 🎯 **双交易所支持** - 同时监控币安和OKX交易所

## 📖 使用说明 / Usage

### 快速开始
```bash
# 1. 安装依赖
pip install ccxt flask

# 2. 运行数据收集程序
python fundingrate_monitor.py

# 3. 启动Web展示服务
python fundingrate_web.py

# 4. 访问 http://localhost:9099 查看界面
```

### 详细步骤
1. **数据收集**: 运行 `fundingrate_monitor.py` 获取最新资金费率数据
2. **Web展示**: 运行 `fundingrate_web.py` 启动Web服务器
3. **查看数据**: 浏览器访问 `http://localhost:9099` 查看监控界面
4. **自动刷新**: 页面每5分钟自动刷新，或手动运行数据收集程序

## 🎨 界面说明 / Interface Guide

- **资金费率报告**: 显示各交易所Top10资金费率
- **预警信息**: 显示超过阈值的资金费率预警
- **高频统计**: 显示资金费率更新频率<4小时的交易对
- **更新时间**: 显示最后数据更新时间

## 🛠️ 技术栈 / Tech Stack

- **Python 3** - 主要编程语言
- **CCXT** - 加密货币交易所API库
- **Flask** - Web框架
- **HTML/CSS** - 前端界面

## 📊 数据来源 / Data Source

- **币安合约**: 通过CCXT库获取资金费率数据
- **OKX合约**: 通过CCXT库获取资金费率数据
- **更新频率**: 手动运行或定时任务
- **数据格式**: 资金费率百分比、更新间隔、预警阈值

## ⚙️ 配置说明 / Configuration

### 主要参数
```python
CONFIG = {
    "threshold": 0.9,  # 资金费率阈值（百分比）
    "exchanges": {
        "binance": {
            "name": "Binance",
            "enabled": True
        },
        "okx": {
            "name": "OKX", 
            "enabled": True
        }
    }
}
```

### 自定义配置
- **阈值调整**: 修改 `threshold` 值来调整预警阈值
- **交易所开关**: 设置 `enabled` 来启用/禁用特定交易所
- **Web端口**: 修改 `fundingrate_web.py` 中的端口号

## 📁 项目结构 / Project Structure

```
git-funding-rate-monitor/
├── fundingrate_monitor.py    # 数据收集程序
├── fundingrate_web.py        # Web展示程序
├── requirements.txt          # 依赖包列表
└── README.md                # 项目说明文档
```

## 🚀 快速开始 / Quick Start

1. **克隆项目**
```bash
git clone https://github.com/dmatrader/funding-rate-monitor.git
cd funding-rate-monitor
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **运行程序**
```bash
# 终端1：数据收集
python fundingrate_monitor.py

# 终端2：Web服务
python fundingrate_web.py
```

4. **访问界面**
打开浏览器访问 `http://localhost:9099`

## 📝 生成文件说明 / Generated Files

- **`funding_report.txt`** - Top10资金费率报告
- **`funding_alert.txt`** - 资金费率预警信息
- **`funding_high_frequency.txt`** - 高频交易对统计

## 📄 许可证 / License

MIT License - 可自由使用和修改 | Free to use and modify

---

⭐ **如果觉得这个项目有帮助，请给个星标！**  
⭐ **If you find this project helpful, please give it a star!**
