# Checkitout Weather

一款基于 [和风天气](https://www.qweather.com) API 的桌面天气应用，使用 PySide6 构建。

手动刷新（无自动刷新），即查即知。

Downloads Count: ![GitHub release downloads](https://img.shields.io/github/downloads/hellodk34/checkitout_weather/total)

## 功能

- 实时天气：温度、体感温度、湿度、降水、气压、风向风力、能见度
- 昨日天气 + 未来 7 天预报
- 空气质量 (AQI) 与首要污染物
- 紫外线指数与等级描述
- 日出 / 日落时间
- 城市搜索、收藏管理
- 亮色 / 暗色主题切换

## 截图

![screenshot1](./assets/screenshot1.jpg)
![screenshot2](./assets/screenshot2.jpg)

## 下载

从 [Releases](https://github.com/hellodk34/checkitout_weather/releases) 页面下载对应平台的预构建分发包

目前已构建的版本：

- Linux
- Windows

## 版本历史

1. v1.0.0 初版发布
2. v1.0.1 修复风量级别显示的错误，增加风速具体数值显示；修复紫外线等级和强度描述；增加星期显示（周x）

## 配置

### 1. 注册和风天气

前往 [和风天气控制台](https://console.qweather.com) 注册账号并创建一个项目。

### 2. 生成 Ed25519 密钥对

和风天气控制台推荐使用 JSON Web Token 方式认证：

> API KEY的认证方式无法提供足够的安全性，因此我们计划从2027年1月1日起，使用API KEY认证方式都将受请求量的限制。  
> 我们推荐使用JSON Web Token (JWT)的认证方式获得更高等级的安全性以及不受限的API请求。

传统的 API KEY 认证将很快受到限制。生成 Ed25519 密钥对：

```bash
# 生成私钥
openssl genpkey -algorithm ED25519 -out ed25519-private.pem

# 从私钥导出公钥
openssl pkey -pubout -in ed25519-private.pem > ed25519-public.pem
```

### 3. 配置和风天气

在和风天气控制台完成以下操作：

1. 进入 **项目管理** → 你的项目，复制出项目 ID
2. 在 **JWT 凭证** 中添加一个凭证
3. 将上一步生成的 `ed25519-public.pem` 的内容粘贴到公钥输入框中
4. 保存后你会获得一个 **Credential ID**

### 4. 填写配置

**推荐首次直接运行**，配置文件会自动生成，但是会警告没有提供必要配置，此时关闭程序，按需填入配置，更新配置文件再启动程序即可。

或者，显式的创建配置文件夹和配置文件 `~/.config/checkitout_weather/config.toml`：

```toml
[api]
host = "你的专属 Host"
project_id = "你的 Project ID"
credential_id = "你的 Credential ID"
private_key_path = "/path/to/ed25519-private.pem"
# 或用 inline 私钥内容（替代文件路径）
# private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"

```

所有字段也可通过环境变量设置（优先级最高）：

| 环境变量 | 说明 |
|---|---|
| `QWEATHER_API_HOST` | API 专属 Host |
| `QWEATHER_PROJECT_ID` | 项目 ID |
| `QWEATHER_CREDENTIAL_ID` | JWT 凭证 ID |
| `QWEATHER_PRIVATE_KEY_PATH` | 私钥文件路径 |
| `QWEATHER_PRIVATE_KEY` | 私钥内容（直接填入 PEM 字符串） |

## 给 linux 创建 desktop 文件

```
# 这里用的是 debian13+gnome48 with wayland，测试良好
# 1. 创建 desktop 文件 ~/.local/share/applications/checkitout-weather.desktop ，内容如下
[Desktop Entry]
Name=Checkitout Weather
Comment=手动刷新查看天气
Exec=/your/path/to/CheckitoutWeather
Icon=checkitout-weather
Terminal=false
Type=Application
Categories=Utility;
StartupNotify=true

# 2. 创建桌面图标文件 ~/.local/share/icons/hicolor/scalable/apps/checkitout-weather.svg，内容即本仓库的 assets/checkitout-weather.svg 内容，复制粘贴过去即可

# 3. 更新桌面图标
update-desktop-database ~/.local/share/applications
```

## 从源码运行

### 环境要求

- Python >= 3.13
- PySide6 >= 6.6 (Qt6)

### 安装依赖

```bash
git clone https://github.com/hellodk34/checkitout_weather.git
cd checkitout_weather

# 创建python独立隔离的虚拟环境
python -m venv .venv
# 激活环境
source .venv/bin/activate # Windows: source .venv/Scripts/activate
# 安装依赖
pip install -r requirements.txt
```

### 独立启动

```bash
python main.py
```

## 构建分发包

使用 PyInstaller 构建独立可执行文件。三个平台的构建命令相同（`.spec` 文件跨平台），仅产物文件名不同。

### Linux

```bash
bash build_for_linux.sh
```

手动构建：

```bash
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --noconfirm CheckitoutWeather.spec
```

构建产物：`dist/CheckitoutWeather`

### Windows

```bash
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --noconfirm CheckitoutWeather.spec
```

构建产物：`dist\CheckitoutWeather.exe`

### macOS

```bash
pip install -r requirements.txt
pip install pyinstaller
pyinstaller --noconfirm CheckitoutWeather.spec
```

构建产物：`dist/CheckitoutWeather`

### 其他说明

当前应用大小是 PySide6 应用的正常水平，体积大头是 Qt6 的 C++ 共享库（约 40-60MB），难以再压缩。

PyInstaller `--onefile` 内部已使用 zlib 压缩归档载荷，UPX 对这类文件基本无效（压缩率 ≈0%），因此 `spec` 中默认禁用 UPX。

**关于中文输入法**：应用启动时会自动检测运行环境。
> - Windows 与 macOS 的中文输入法走系统原生 TSF / Input Method Kit
> - **Linux Wayland**：清除 `QT_IM_MODULE`，Qt6 使用原生 text-input 协议通过 compositor 与 fcitx5/ibus 通信
> - **Linux X11**：自动检测正在运行的输入法框架（fcitx5/ibus）并设置 `QT_IM_MODULE` 等环境变量
>
> 详见 `main.py` 中的 `_setup_input_method()`。

## 许可

MIT License.
