# AnkiAudio Platform 部署指南

## 环境要求

### 服务器配置

| 组件 | 最低配置 | 推荐配置 |
|------|---------|---------|
| CPU | 1 核 | 2 核+ |
| 内存 | 1 GB | 2 GB+ |
| 磁盘 | 10 GB SSD | 20 GB+ SSD |
| 带宽 | 5 Mbps | 10 Mbps+ |
| 操作系统 | Ubuntu 20.04+ / CentOS 8+ | Ubuntu 22.04 LTS |

### 软件依赖

| 软件 | 版本 | 用途 |
|------|------|------|
| Python | 3.10+ | 后端运行环境 |
| FFmpeg | 4.4+ | 音频处理 |
| yt-dlp | 2026.3.3+ | 视频下载 |
| Nginx | 1.18+ | 反向代理（可选） |
| Git | 2.x+ | 代码管理 |

---

## 快速部署

### 方式一：自动安装脚本（推荐）

```bash
# 下载并运行安装脚本
curl -fsSL https://raw.githubusercontent.com/yasaka999/python/master/anki-audio-platform/install.sh | bash
```

### 方式二：手动部署

#### 1. 系统准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装基础依赖
sudo apt install -y python3 python3-pip python3-venv git wget

# 安装 FFmpeg
sudo apt install -y ffmpeg

# 验证 FFmpeg
ffmpeg -version

# 安装 yt-dlp
sudo curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp
sudo chmod a+rx /usr/local/bin/yt-dlp

# 验证 yt-dlp
yt-dlp --version
```

#### 2. 部署应用

```bash
# 创建应用目录
sudo mkdir -p /opt/anki-audio-platform
sudo chown $USER:$USER /opt/anki-audio-platform
cd /opt/anki-audio-platform

# 克隆代码
git clone https://github.com/yasaka999/python.git temp
cp -r temp/anki-audio-platform-app/* .
rm -rf temp

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 创建数据目录
mkdir -p data storage

# 配置环境变量
cp .env.example .env
nano .env
```

编辑 `.env` 文件：

```env
BASE_URL=http://your-domain.com:8000
STORAGE_DIR=./storage
DB_PATH=./data/ankitube.db
FFMPEG_PATH=/usr/bin/ffmpeg
```

#### 3. 启动服务

```bash
# 开发模式（前台运行，用于测试）
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# 生产模式（后台运行）
nohup python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4 > server.log 2>&1 &

# 查看日志
tail -f server.log
```

#### 4. 配置 Systemd 服务（推荐）

创建服务文件：

```bash
sudo nano /etc/systemd/system/ankiaudio.service
```

内容：

```ini
[Unit]
Description=AnkiAudio Platform
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/anki-audio-platform
Environment="PATH=/opt/anki-audio-platform/venv/bin:/usr/local/bin:/usr/bin"
ExecStart=/opt/anki-audio-platform/venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

启用并启动服务：

```bash
# 创建用户
sudo useradd -r -s /bin/false www-data 2>/dev/null || true

# 设置权限
sudo chown -R www-data:www-data /opt/anki-audio-platform

# 重载 systemd
sudo systemctl daemon-reload

# 启用开机自启
sudo systemctl enable ankiaudio

# 启动服务
sudo systemctl start ankiaudio

# 查看状态
sudo systemctl status ankiaudio

# 查看日志
sudo journalctl -u ankiaudio -f
```

---

## Nginx 反向代理（可选）

### 安装 Nginx

```bash
sudo apt install -y nginx
```

### 配置站点

```bash
sudo nano /etc/nginx/sites-available/ankiaudio
```

内容：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 100M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # 静态文件缓存
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|mp3)$ {
        proxy_pass http://127.0.0.1:8000;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

启用配置：

```bash
sudo ln -s /etc/nginx/sites-available/ankiaudio /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### HTTPS 配置（Let's Encrypt）

```bash
# 安装 Certbot
sudo apt install -y certbot python3-certbot-nginx

# 申请证书
sudo certbot --nginx -d your-domain.com

# 自动续期测试
sudo certbot renew --dry-run
```

---

## Docker 部署

### Dockerfile

```dockerfile
FROM python:3.11-slim

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 安装 yt-dlp
RUN wget -O /usr/local/bin/yt-dlp https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp \
    && chmod +x /usr/local/bin/yt-dlp

# 设置工作目录
WORKDIR /app

# 复制依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 创建数据目录
RUN mkdir -p data storage

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "-m", "uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  ankiaudio:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - ./storage:/app/storage
      - ./.env:/app/.env:ro
    environment:
      - BASE_URL=http://localhost:8000
    restart: unless-stopped
```

### 启动

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

---

## 日常运维

### 查看服务状态

```bash
# Systemd 方式
sudo systemctl status ankiaudio
sudo journalctl -u ankiaudio -f

# 手动启动方式
ps aux | grep uvicorn
tail -f /opt/anki-audio-platform/server.log
```

### 重启服务

```bash
# Systemd 方式
sudo systemctl restart ankiaudio

# 手动方式
pkill -f uvicorn
nohup python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4 > server.log 2>&1 &
```

### 数据库备份

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/ankiaudio"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
cp /opt/anki-audio-platform/data/ankitube.db $BACKUP_DIR/ankitube_$DATE.db

# 保留最近 7 天备份
find $BACKUP_DIR -name "ankitube_*.db" -mtime +7 -delete

echo "Backup completed: $BACKUP_DIR/ankitube_$DATE.db"
```

添加到定时任务：

```bash
chmod +x backup.sh
sudo crontab -e

# 每天凌晨 2 点备份
0 2 * * * /opt/anki-audio-platform/backup.sh >> /var/log/ankiaudio-backup.log 2>&1
```

### 清理旧数据

```bash
#!/bin/bash
# cleanup.sh

# 删除 30 天前的已完成牌组（可选）
# 注意：这会删除相关音频文件！

cd /opt/anki-audio-platform
source venv/bin/activate

python3 << 'EOF'
import aiosqlite
import asyncio
import os
from datetime import datetime, timedelta

DB_PATH = "./data/ankitube.db"
STORAGE_DIR = "./storage"

async def cleanup():
    cutoff = datetime.now() - timedelta(days=30)
    
    async with aiosqlite.connect(DB_PATH) as db:
        # 查找旧牌组
        async with db.execute(
            "SELECT id FROM deck WHERE status='done' AND created_at < ?",
            (cutoff.isoformat(),)
        ) as cursor:
            old_decks = [row[0] for row in await cursor.fetchall()]
        
        for deck_id in old_decks:
            # 删除音频目录
            audio_dir = os.path.join(STORAGE_DIR, deck_id)
            if os.path.exists(audio_dir):
                import shutil
                shutil.rmtree(audio_dir)
                print(f"Deleted: {audio_dir}")
            
            # 删除数据库记录
            await db.execute("DELETE FROM segment WHERE deck_id=?", (deck_id,))
            await db.execute("DELETE FROM task WHERE deck_id=?", (deck_id,))
            await db.execute("DELETE FROM deck WHERE id=?", (deck_id,))
        
        await db.commit()
        print(f"Cleaned up {len(old_decks)} old decks")

asyncio.run(cleanup())
EOF
```

---

## 故障排查

### 问题 1：服务无法启动

**现象:** `systemctl start ankiaudio` 失败

**排查:**

```bash
# 查看详细错误
sudo journalctl -u ankiaudio -n 50

# 检查权限
ls -la /opt/anki-audio-platform/
sudo chown -R www-data:www-data /opt/anki-audio-platform

# 检查环境变量
cat /opt/anki-audio-platform/.env

# 手动测试启动
cd /opt/anki-audio-platform
source venv/bin/activate
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
```

### 问题 2：视频下载失败

**现象:** 任务状态卡在 `downloading`

**排查:**

```bash
# 检查 yt-dlp
yt-dlp --version
which yt-dlp

# 测试下载
yt-dlp -F "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

# 检查网络
curl -I https://www.youtube.com

# 查看日志
tail -f /opt/anki-audio-platform/server.log | grep -i error
```

### 问题 3：音频切分失败

**现象:** 任务状态变为 `error`，错误信息包含 FFmpeg

**排查:**

```bash
# 检查 FFmpeg
ffmpeg -version
which ffmpeg

# 测试音频处理
ffmpeg -i test.mp3 -ss 00:00:10 -t 5 output.mp3

# 检查临时目录空间
df -h /tmp
df -h /opt/anki-audio-platform
```

### 问题 4：卡片无法播放音频

**现象:** Anki 中卡片显示但无法播放

**排查:**

```bash
# 检查音频文件是否存在
ls -la /opt/anki-audio-platform/storage/{deck_id}/

# 检查文件权限
sudo chown -R www-data:www-data /opt/anki-audio-platform/storage

# 测试直接访问
curl -I http://your-domain:8000/storage/{deck_id}/seg_001.mp3

# 检查 CORS 配置
curl -H "Origin: https://ankiweb.net" -I http://your-domain:8000/card/{card_id}
```

### 问题 5：词典查询失败

**现象:** 点击生词无反应或显示"未找到"

**排查:**

```bash
# 测试有道词典 API
curl "http://cloudcone.080828.xyz:8000/word/hello"

# 检查网络连接
curl -I https://dict.youdao.com

# 查看词典服务日志
grep -i dictionary /opt/anki-audio-platform/server.log
```

---

## 性能优化

### 1. Uvicorn Worker 数量

根据 CPU 核心数调整：

```bash
# 公式：2 * CPU核心数 + 1
# 2核服务器：--workers 5
# 4核服务器：--workers 9

python -m uvicorn backend.main:app --workers 5
```

### 2. Nginx 优化

```nginx
# /etc/nginx/nginx.conf
worker_processes auto;
worker_connections 4096;

# 启用 gzip
gzip on;
gzip_types text/plain text/css application/json application/javascript;

# 文件上传大小
client_max_body_size 100M;
```

### 3. 数据库优化

SQLite 在并发写入时性能有限，如需高并发考虑迁移到 PostgreSQL。

---

## 安全加固

### 1. 防火墙配置

```bash
# 仅开放必要端口
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable
```

### 2. 文件权限

```bash
# 限制敏感文件权限
chmod 600 /opt/anki-audio-platform/.env
chmod 700 /opt/anki-audio-platform/data
chmod 755 /opt/anki-audio-platform/storage
```

### 3. 定期更新

```bash
# 更新 yt-dlp
sudo yt-dlp -U

# 更新 Python 依赖
cd /opt/anki-audio-platform
source venv/bin/activate
pip install --upgrade -r requirements.txt

# 重启服务
sudo systemctl restart ankiaudio
```

---

## 升级指南

### 小版本升级

```bash
cd /opt/anki-audio-platform

# 拉取最新代码
git pull origin master

# 更新依赖
source venv/bin/activate
pip install -r requirements.txt

# 重启服务
sudo systemctl restart ankiaudio
```

### 大版本升级

1. **备份数据**
   ```bash
   cp -r data data.backup.$(date +%Y%m%d)
   cp -r storage storage.backup.$(date +%Y%m%d)
   ```

2. **查看升级说明**
   ```bash
   cat CHANGELOG.md
   ```

3. **执行升级**
   ```bash
   git pull origin master
   # 按 CHANGELOG 执行额外步骤
   ```

4. **验证升级**
   ```bash
   curl http://localhost:8000/health
   ```

---

## 联系支持

如有部署问题：

1. 查看日志：`sudo journalctl -u ankiaudio -f`
2. 检查配置：`cat /opt/anki-audio-platform/.env`
3. 测试服务：`curl http://localhost:8000/health`
4. 提交 Issue：https://github.com/yasaka999/python/issues
