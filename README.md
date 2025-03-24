# JMComic Downloader for NoneBot

✨ 一个NoneBot 2.0插件，用于从JMComic下载本子并转换为PDF格式，支持文件缓存和自动上传到QQ群，本人使用DeepSeek辅助完成编写，没有仔细测试，代码质量很差。

[![NoneBot2](https://img.shields.io/badge/NoneBot-2.0.0rc1+-green.svg)](https://v2.nonebot.dev/)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)

## 📦 功能特性

- ✅ 通过JM本子ID直接下载
- ✅ 自动转换图片为PDF文件
- ✅ 智能本地缓存检查机制
  - 优先使用已生成的PDF文件
  - 存在图片时跳过下载直接转换
- ✅ 安全可靠的文件保留策略
  - 上传失败保留所有文件
  - 转换失败自动清理无效PDF
- ✅ 支持QQ群文件直接上传
- ✅ 完善的错误提示系统

## 感谢以下项目
参考此项目编写 https://github.com/salikx/image2pdf

## 🛠️ 安装指南

### 前置要求
- 已安装NoneBot 2.0框架
- Python 3.8+ 环境

### 安装步骤
1. 通过pip安装依赖库：
```bash
pip install jmcomic -i https://pypi.org/project -U
```
2. 将插件文件放入NoneBot项目的插件目录（如src/plugins）
3. 在项目根目录创建配置文件 config.yml
```
download:
  # 推荐设置为绝对路径
  base_dir: "/path/to/downloads"  
  # 可选配置项...
```
⚙️ 配置说明
必要配置
在config.yml中添加：
```
jmcomic:
  download:
    base_dir: "/path/to/your/download/folder"
    # 其他下载相关配置...
```
🚀 使用手册
基本命令
```
/jm [JM本子ID]
```