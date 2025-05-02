# Python 虚拟环境使用指南

## 1. 虚拟环境简介

虚拟环境（Virtual Environment）是 Python 的一个工具，用于创建独立的 Python 运行环境。它可以帮助我们：
- 隔离不同项目的依赖
- 避免包版本冲突
- 方便项目迁移和部署
- 保持全局 Python 环境的整洁

## 2. 创建虚拟环境

### 2.1 使用 venv 创建虚拟环境

```bash
# 在项目根目录下创建虚拟环境
python3 -m venv venv
```

这将在当前目录下创建一个名为 `venv` 的虚拟环境目录。

### 2.2 激活虚拟环境

```bash
# 在 macOS/Linux 上激活虚拟环境
source venv/bin/activate

# 在 Windows 上激活虚拟环境
venv\Scripts\activate
```

激活后，命令行提示符前会显示 `(venv)`，表示当前处于虚拟环境中。

## 3. 管理依赖

### 3.1 安装依赖

在虚拟环境中，可以使用 pip 安装项目所需的依赖：

```bash
# 从 requirements.txt 安装所有依赖
pip install -r requirements.txt

# 安装单个包
pip install package_name

# 安装指定版本的包
pip install package_name==version
```

### 3.2 使用国内镜像源加速

为了加快下载速度，可以使用国内镜像源：

```bash
# 使用清华镜像源
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple package_name

# 使用百度镜像源
pip install -i https://mirror.baidu.com/pypi/simple package_name
```

### 3.3 导出依赖

```bash
# 导出当前环境的依赖到 requirements.txt
pip freeze > requirements.txt
```

## 4. 运行项目

在虚拟环境中运行 Python 项目：

```bash
# 运行 Python 脚本
python your_script.py

# 运行 FastAPI 应用
uvicorn app:app --reload
```

## 5. 退出虚拟环境

完成工作后，可以退出虚拟环境：

```bash
deactivate
```

## 6. 常见问题解决

### 6.1 依赖安装失败

如果遇到依赖安装失败，可以尝试：
1. 使用不同的镜像源
2. 检查 Python 版本兼容性
3. 更新 pip：`pip install --upgrade pip`

### 6.2 虚拟环境无法激活

如果激活命令报错，检查：
1. 虚拟环境是否正确创建
2. 激活脚本的路径是否正确
3. 文件权限是否正确

## 7. 最佳实践

1. 为每个项目创建独立的虚拟环境
2. 在项目根目录下创建虚拟环境
3. 将 `venv` 目录添加到 `.gitignore` 中
4. 定期更新依赖版本
5. 使用 `requirements.txt` 管理依赖

## 8. 注意事项

1. 虚拟环境是项目特定的，不要在不同项目间共享
2. 确保在正确的虚拟环境中安装依赖
3. 在部署时，确保使用相同的虚拟环境配置
4. 定期备份 `requirements.txt` 文件

## 9. 常用命令速查

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 导出依赖
pip freeze > requirements.txt

# 退出虚拟环境
deactivate
``` 

# 执行
source venv/bin/activate && uvicorn app:app --reload --host 0.0.0.0 --port 8011