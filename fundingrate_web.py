#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Flask, render_template_string, jsonify
import json
import os
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.ERROR,  # 只显示错误日志
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# HTML 模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>资金费率监控</title>
    <meta http-equiv="refresh" content="300">  <!-- 每5分钟自动刷新 -->
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        .container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 5px;
        }
        .update-time {
            text-align: center;
            color: #666;
            font-size: 0.9em;
            margin-bottom: 20px;
        }
        h2 {
            color: #444;
            margin-top: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #f8f9fa;
            font-weight: bold;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
        .positive {
            color: #28a745;
        }
        .negative {
            color: #dc3545;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>资金费率监控</h1>
        <div class="update-time">
            最后更新时间: {{ last_update }}
        </div>

        <h2>资金费率预警</h2>
        {% if alerts %}
            <table>
                <tr>
                    <th>交易所</th>
                    <th>交易对</th>
                    <th>资金费率</th>
                </tr>
                {% for alert in alerts %}
                <tr>
                    <td>{{ alert.exchange }}</td>
                    <td>{{ alert.symbol }}</td>
                    <td class="{{ 'positive' if alert.rate > 0 else 'negative' }}">
                        {{ alert.rate }}%
                    </td>
                </tr>
                {% endfor %}
            </table>
        {% else %}
            <p>当前没有预警信息</p>
        {% endif %}

        <h2>高频资金费率统计</h2>
        {% if high_freq %}
            <table>
                <tr>
                    <th>交易所</th>
                    <th>交易对</th>
                    <th>间隔时间(小时)</th>
                </tr>
                {% for item in high_freq %}
                <tr>
                    <td>{{ item.exchange }}</td>
                    <td>{{ item.symbol }}</td>
                    <td>{{ item.interval }}</td>
                </tr>
                {% endfor %}
            </table>
        {% else %}
            <p>当前没有高频资金费率数据</p>
        {% endif %}

        <h2>Top10 资金费率</h2>
        {% for exchange, rates in top10.items() %}
            <h3>{{ exchange }}</h3>
            <table>
                <tr>
                    <th>交易对</th>
                    <th>资金费率</th>
                </tr>
                {% for rate in rates %}
                <tr>
                    <td>{{ rate.symbol }}</td>
                    <td class="{{ 'positive' if rate.rate > 0 else 'negative' }}">
                        {{ rate.rate }}%
                    </td>
                </tr>
                {% endfor %}
            </table>
        {% endfor %}
    </div>
</body>
</html>
"""

def read_alert_file():
    """读取预警文件"""
    alerts = []
    try:
        with open('funding_alert.txt', 'r', encoding='utf-8') as f:
            current_exchange = None
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line.startswith('⚠️'):
                    current_exchange = line.split('资金费率预警')[0].replace('⚠️', '').strip()
                elif current_exchange and ':' in line:
                    symbol, rate = line.split(':', 1)
                    # 处理可能包含的 USDT: 前缀
                    rate = rate.replace('USDT:', '').strip()
                    rate = float(rate.replace('%', '').strip())
                    alerts.append({
                        'exchange': current_exchange,
                        'symbol': symbol.strip(),
                        'rate': rate
                    })
    except FileNotFoundError:
        pass
    return alerts

def read_high_freq_file():
    """读取高频资金费率文件"""
    high_freq = []
    try:
        with open('funding_high_frequency.txt', 'r', encoding='utf-8') as f:
            current_exchange = None
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if '高频交易对' in line:
                    current_exchange = line.split('高频交易对')[0].strip()
                elif current_exchange and ':' in line:
                    symbol, interval = line.split(':', 1)
                    # 处理可能包含的 USDT: 前缀
                    interval = interval.replace('USDT:', '').strip()
                    interval = float(interval.replace('小时', '').strip())
                    high_freq.append({
                        'exchange': current_exchange,
                        'symbol': symbol.strip(),
                        'interval': interval
                    })
    except FileNotFoundError:
        pass
    return high_freq

def read_top10_file():
    """读取Top10文件"""
    top10 = {}
    try:
        with open('funding_report.txt', 'r', encoding='utf-8') as f:
            current_exchange = None
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if '前10名资金费率' in line:
                    current_exchange = line.split('前10名资金费率')[0].replace('🔥', '').strip()
                    top10[current_exchange] = []
                elif current_exchange and ':' in line:
                    symbol, rate = line.split(':', 1)
                    # 处理可能包含的 USDT: 前缀
                    rate = rate.replace('USDT:', '').strip()
                    rate = float(rate.replace('%', '').strip())
                    top10[current_exchange].append({
                        'symbol': symbol.strip(),
                        'rate': rate
                    })
    except FileNotFoundError:
        pass
    return top10

@app.route('/')
def index():
    """主页"""
    alerts = read_alert_file()
    high_freq = read_high_freq_file()
    top10 = read_top10_file()
    
    # 获取最后更新时间
    last_update = "未知"
    try:
        with open('funding_report.txt', 'r', encoding='utf-8') as f:
            content = f.read()
            if '资金费率监控报告' in content:
                # 提取完整的时间戳
                timestamp_part = content.split('-', 1)[1].split('\n')[0].strip()
                try:
                    dt = datetime.strptime(timestamp_part, '%Y-%m-%d %H:%M:%S')
                    last_update = dt.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    pass
    except FileNotFoundError:
        pass
    
    return render_template_string(
        HTML_TEMPLATE,
        alerts=alerts,
        high_freq=high_freq,
        top10=top10,
        last_update=last_update
    )

@app.route('/api/data')
def api_data():
    """API 接口"""
    return jsonify({
        'alerts': read_alert_file(),
        'high_freq': read_high_freq_file(),
        'top10': read_top10_file(),
        'last_update': datetime.now().strftime('%Y-%m-%d %H:%M')
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9099, debug=False)  # 关闭调试模式 