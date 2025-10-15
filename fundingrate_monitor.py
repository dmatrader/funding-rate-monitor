#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import logging
from datetime import datetime
import ccxt

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 硬编码配置
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

def save_high_frequency_data(data):
    """保存高频资金费率数据到单独的文件"""
    try:
        high_freq_report = []
        high_freq_report.append(f"📈 高频资金费率统计（<4小时） - {data['last_update']}\n")
        
        for exchange_name, exchange_data in data['exchanges'].items():
            high_freq_pairs = {symbol: info for symbol, info in exchange_data['funding_intervals'].items() 
                             if info['interval'] < 4}
            if high_freq_pairs:
                high_freq_report.append(f"\n{exchange_name} 高频交易对：")
                for symbol, info in high_freq_pairs.items():
                    high_freq_report.append(f"{symbol}: {info['interval']:.2f}小时")
            else:
                high_freq_report.append(f"\n{exchange_name} 暂无高频交易对")
        
        # 将报告保存到单独的文件
        report_text = "\n".join(high_freq_report)
        with open('funding_high_frequency.txt', 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        logger.info(f"高频资金费率报告已保存到 funding_high_frequency.txt")
        return True
    except Exception as e:
        logger.error(f"保存高频资金费率数据失败: {e}")
        return False

def save_data(data):
    """保存数据到文件"""
    try:
        # 生成报告
        report = []
        report.append(f"📊 资金费率监控报告 - {data['last_update']}\n")
        
        # Binance 数据
        report.append("🔥 Binance 前10名资金费率：")
        for symbol, rate in data['exchanges']['Binance']['top_10']:
            report.append(f"{symbol}: {rate:.4f}%")
        
        # OKX 数据
        report.append("\n🔥 OKX 前10名资金费率：")
        for symbol, rate in data['exchanges']['OKX']['top_10']:
            report.append(f"{symbol}: {rate:.4f}%")
        
        # 将报告保存到文件
        report_text = "\n".join(report)
        with open('funding_report.txt', 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        logger.info(f"报告已保存到 funding_report.txt")
        
        # 检查是否有超过阈值的币对，如果有则生成预警
        alert_messages = []
        for exchange_name, exchange_data in data['exchanges'].items():
            if exchange_data['high_rates']:
                alert_messages.append(f"⚠️ {exchange_name} 资金费率预警：")
                for symbol, rate in exchange_data['high_rates']:
                    alert_messages.append(f"{symbol}: {rate:.4f}%")
        
        if alert_messages:
            alert_text = "\n".join(alert_messages)
            with open('funding_alert.txt', 'w', encoding='utf-8') as f:
                f.write(alert_text)
            logger.info("已生成资金费率预警")
        
        # 保存高频资金费率数据
        save_high_frequency_data(data)
        
        return True
    except Exception as e:
        logger.error(f"保存数据失败: {e}")
        return False

def fetch_funding_rates(exchange_name, exchange):
    """获取指定交易所的资金费率"""
    rates = {}
    funding_intervals = {}
    try:
        logger.info(f"开始获取 {exchange_name} 的资金费率")
        markets = exchange.load_markets()
        
        # 添加请求延迟
        request_delay = 0.1  # 100ms延迟
        
        for symbol, market in markets.items():
            if market.get('quote') == 'USDT' and market.get('type') == 'swap':
                try:
                    # 添加延迟
                    time.sleep(request_delay)
                    
                    funding = exchange.fetch_funding_rate(symbol)
                    rate = float(funding['fundingRate']) * 100  # 转换为百分比
                    rates[symbol] = rate
                    
                    # 获取资金费率周期信息
                    try:
                        # 再次添加延迟
                        time.sleep(request_delay)
                        funding_info = exchange.fetch_funding_rate_history(symbol, limit=2)
                        if len(funding_info) >= 2:
                            # 确保时间戳按正确顺序排列
                            timestamps = sorted([info['timestamp'] for info in funding_info])
                            interval = (timestamps[1] - timestamps[0]) / (1000 * 3600)  # 转换为小时
                            frequency = "高" if interval < 4 else "标准"  # 修改为4小时
                            funding_intervals[symbol] = {
                                'interval': round(interval, 2),
                                'frequency': frequency
                            }
                    except Exception as e:
                        if "403" in str(e):
                            logger.warning(f"获取 {symbol} 历史资金费率被限制，等待后重试...")
                            time.sleep(1)  # 等待1秒后重试
                            try:
                                funding_info = exchange.fetch_funding_rate_history(symbol, limit=2)
                                if len(funding_info) >= 2:
                                    # 确保时间戳按正确顺序排列
                                    timestamps = sorted([info['timestamp'] for info in funding_info])
                                    interval = (timestamps[1] - timestamps[0]) / (1000 * 3600)
                                    funding_intervals[symbol] = {
                                        'interval': round(interval, 2),
                                        'frequency': "高" if interval < 4 else "标准"  # 修改为4小时
                                    }
                            except Exception as retry_e:
                                logger.warning(f"重试获取 {symbol} 历史资金费率失败: {retry_e}")
                        else:
                            logger.warning(f"获取 {symbol} 历史资金费率失败: {e}")
                            
                except Exception as e:
                    if "403" in str(e):
                        logger.warning(f"获取 {symbol} 资金费率被限制，等待后重试...")
                        time.sleep(1)  # 等待1秒后重试
                        try:
                            funding = exchange.fetch_funding_rate(symbol)
                            rate = float(funding['fundingRate']) * 100
                            rates[symbol] = rate
                        except Exception as retry_e:
                            logger.warning(f"重试获取 {symbol} 资金费率失败: {retry_e}")
                    else:
                        logger.warning(f"获取 {symbol} 资金费率失败: {e}")
                    continue
                    
        logger.info(f"成功获取 {exchange_name} 的 {len(rates)} 个币对资金费率")
    except Exception as e:
        logger.error(f"获取 {exchange_name} 资金费率失败: {e}")
    return rates, funding_intervals

def main():
    try:
        logger.info("开始运行资金费率监控程序")
        
        # 初始化数据
        data = {
            "last_update": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "exchanges": {
                "Binance": {
                    "top_10": [],
                    "high_rates": [],
                    "funding_intervals": {}
                },
                "OKX": {
                    "top_10": [],
                    "high_rates": [],
                    "funding_intervals": {}
                }
            }
        }
        
        # 获取各个交易所的数据
        for exchange_id, exchange_info in CONFIG['exchanges'].items():
            if not exchange_info['enabled']:
                logger.info(f"跳过未启用的交易所: {exchange_info['name']}")
                continue
                
            exchange = getattr(ccxt, exchange_id)()
            rates, funding_intervals = fetch_funding_rates(exchange_info['name'], exchange)
            
            # 获取该交易所的前10名（按绝对值排序）
            top_10 = sorted(rates.items(), key=lambda x: abs(x[1]), reverse=True)[:10]
            logger.info(f"{exchange_info['name']} 前10名资金费率已计算")
            
            # 获取该交易所超过阈值的币对
            high_rates = [(symbol, rate) for symbol, rate in rates.items() 
                         if abs(rate) >= CONFIG['threshold']]
            logger.info(f"{exchange_info['name']} 超过阈值的币对数量: {len(high_rates)}")
            
            # 更新该交易所的数据
            data["exchanges"][exchange_info['name']] = {
                "top_10": top_10,
                "high_rates": high_rates,
                "funding_intervals": funding_intervals
            }
        
        if save_data(data):
            logger.info("数据更新成功")
        else:
            logger.error("数据更新失败")
            
    except Exception as e:
        logger.error(f"程序运行出错: {e}")

if __name__ == "__main__":
    main()
