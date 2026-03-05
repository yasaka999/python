# AnkiAudio Platform 架构文档

## 系统概述

AnkiAudio Platform 是一个个人云端音频 Anki 服务，自动从 YouTube 视频提取音频和字幕，生成可导入 Anki 的听力卡片牌组。系统采用异步处理流水线，支持智能音频切分、双语词典查询和精美的卡片渲染。

---

## 系统架构图

```
┌─────────────────────────────────────────────────────────────┐
│                        客户端层                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Web 浏览器  │  │    Anki     │  │    命令行工具        │ │
│  │  (管理界面)   │  │  (iframe)   │  │                     │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘ │
└─────────┼────────────────┼────────────────────┼────────────┘
          │                │                    │
          └────────────────┴────────────────────┘
                           │
                    HTTP/HTTPS
                           │
┌──────────────────────────┼──────────────────────────────────┐
│                      FastAPI 后端                            │
│  ┌───────────────────────┼────────────────────────────────┐ │
│  │                       ▼                                │ │
│  │  ┌─────────┐  ┌─────────────┐  ┌──────────────────┐   │ │
│  │  │  API    │  │  Services   │  │  External APIs   │   │ │
│  │  │  Layer  │◄─┤  Pipeline   │◄─┤  YouTube/Dict    │   │ │
│  │  └────┬────┘  └─────────────┘  └──────────────────┘   │ │
│  │       │                                                │ │
│  │       ▼                                                │ │
│  │  ┌─────────┐  ┌─────────────┐  ┌──────────────────┐   │ │
│  │  │ SQLite  │  │  Storage    │  │  Static Files    │   │ │
│  │  │  DB     │  │  (Audio)    │  │  (HTML/JS/CSS)   │   │ │
│  │  └─────────┘  └─────────────┘  └──────────────────┘   │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## 技术栈详解

### 后端技术栈

| 组件 | 技术 | 版本 | 用途 |
|------|------|------|------|
| 框架 | FastAPI | 0.100+ | 高性能异步 Web 框架 |
| 数据库 | SQLite + aiosqlite | 3.x | 轻量级异步数据库 |
| 视频下载 | yt-dlp | 2026.3.3+ | YouTube 视频下载 |
| 音频处理 | pydub + FFmpeg | - | 音频切分和格式转换 |
| Anki 生成 | genanki | 0.13+ | .apkg 文件生成 |
| 字幕解析 | webvtt-py, srt | - | VTT/SRT 字幕解析 |
| HTTP 客户端 | aiohttp | 3.9+ | 异步 HTTP 请求 |
| 配置管理 | python-dotenv | - | 环境变量管理 |
| 服务器 | Uvicorn | 0.24+ | ASGI 服务器 |

### 前端技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| 框架 | Vanilla JS | 纯 JavaScript，无框架依赖 |
| UI 样式 | CSS3 | 现代化样式，支持暗色模式 |
| 图标 | SVG | 内联 SVG 图标 |
| 播放器 | HTML5 Audio API | 原生音频播放控制 |

---

## 目录结构

```
anki-audio-platform-app/
├── backend/                          # 后端代码
│   ├── api/                          # API 路由层
│   │   ├── __init__.py
│   │   ├── process.py               # 处理流程 API (/process, /status, /decks)
│   │   ├── card.py                  # 卡片渲染 API (/card, /word, /thumbnail)
│   │   └── export.py                # 导出 API (/export, /prefer)
│   │
│   ├── services/                     # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── pipeline.py              # 处理流水线（核心）
│   │   ├── downloader.py            # yt-dlp 视频下载器
│   │   ├── subtitle.py              # 字幕解析器
│   │   ├── splitter.py              # 音频切分器
│   │   ├── storage.py               # 文件存储服务
│   │   ├── anki_export.py           # Anki 牌组生成器
│   │   └── dictionary.py            # 词典查询服务
│   │
│   ├── static/                       # 静态文件
│   │   └── index.html               # Web 管理界面
│   │
│   ├── main.py                       # FastAPI 应用入口
│   └── db.py                         # 数据库操作
│
├── storage/                          # 音频文件存储
│   └── {deck_id}/                    # 按牌组分目录
│       ├── audio.mp3                 # 完整音频
│       ├── thumbnail.jpg             # 视频缩略图
│       ├── seg_001.mp3               # 片段音频
│       ├── seg_002.mp3
│       └── ...
│
├── data/                             # 数据库文件
│   └── ankitube.db                   # SQLite 数据库
│
├── tmp*                              # 临时文件（处理中）
│
├── requirements.txt                  # Python 依赖
├── .env.example                      # 环境变量模板
├── .env                              # 实际环境变量
├── README.md                         # 项目说明
├── API.md                            # API 文档
├── ARCHITECTURE.md                   # 架构文档
└── ROADMAP.md                        # 开发路线图
```

---

## 数据模型

### E-R 图

```
┌─────────────────┐         ┌─────────────────┐         ┌─────────────────┐
│      Deck       │         │     Segment     │         │      Task       │
├─────────────────┤         ├─────────────────┤         ├─────────────────┤
│ id (PK)         │◄───────►│ id (PK)         │         │ id (PK)         │
│ youtube_url     │    1:N  │ deck_id (FK)    │         │ deck_id (FK)    │
│ title           │         │ seg_index       │         │ status          │
│ thumbnail       │         │ audio_path      │         │ created_at      │
│ lang_cd         │         │ sentence        │         └─────────────────┘
│ status          │         │ words (JSON)    │
│ progress        │         │ start_ms        │
│ total           │         │ end_ms          │
│ error_msg       │         │ created_at      │
│ created_at      │         └─────────────────┘
└─────────────────┘
```

### 表结构详情

#### deck 表

```sql
CREATE TABLE deck (
    id          TEXT PRIMARY KEY,      -- UUID v4
    youtube_url TEXT NOT NULL,         -- YouTube 链接
    title       TEXT,                  -- 视频标题
    thumbnail   TEXT,                  -- 缩略图路径
    lang_cd     TEXT DEFAULT 'en',     -- 语言代码
    status      TEXT DEFAULT 'pending',-- 状态
    progress    INTEGER DEFAULT 0,     -- 当前进度
    total       INTEGER DEFAULT 0,     -- 总数量
    error_msg   TEXT,                  -- 错误信息
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### segment 表

```sql
CREATE TABLE segment (
    id          TEXT PRIMARY KEY,      -- UUID v4
    deck_id     TEXT NOT NULL REFERENCES deck(id),
    seg_index   INTEGER NOT NULL,      -- 片段序号
    audio_path  TEXT NOT NULL,         -- 音频文件路径
    sentence    TEXT,                  -- 字幕文本
    words       TEXT,                  -- 单词标注 JSON
    start_ms    INTEGER,               -- 开始时间(ms)
    end_ms      INTEGER,               -- 结束时间(ms)
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### task 表

```sql
CREATE TABLE task (
    id          TEXT PRIMARY KEY,      -- UUID v4
    deck_id     TEXT NOT NULL REFERENCES deck(id),
    status      TEXT DEFAULT 'pending',-- 任务状态
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## 核心流程

### 1. 视频处理流水线

```
用户提交 URL
    │
    ▼
┌─────────────┐
│  创建任务    │ ──► 写入 deck 表 (status=pending)
│  (API层)    │ ──► 写入 task 表
└──────┬──────┘
       │
       ▼ BackgroundTask
┌─────────────┐
│  下载视频    │ ──► yt-dlp 下载音频和字幕
│  Downloader │ ──► 更新 status=downloading
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  解析字幕    │ ──► webvtt-py/srt 解析
│  Subtitle   │ ──► 按句子边界合并短句
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  切分音频    │ ──► pydub + FFmpeg
│  Splitter   │ ──► 按时间戳切分片段
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  生成牌组    │ ──► genanki 生成 .apkg
│  AnkiExport │ ──► 嵌入 iframe 卡片模板
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  完成       │ ──► 更新 status=done
│  Done       │ ──► 清理临时文件
└─────────────┘
```

### 2. 卡片渲染流程

```
Anki 加载卡片
    │
    ▼
┌─────────────┐
│  iframe     │ ──► GET /card/{card_id}?side=0|1
│  请求卡片   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  查询数据    │ ──► 从 segment 表获取音频路径、字幕
│  (DB层)     │ ──► 从 deck 表获取缩略图、标题
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  单词标注    │ ──► 调用 dictionary.annotate_sentence()
│  (可选)     │ ──► 有道词典 API 查询生词
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  渲染 HTML   │ ──► _render_card_page() 生成页面
│  (Template) │ ──► 包含播放器、字幕、单词弹窗
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  返回响应    │ ──► HTMLResponse
│  Response   │
└─────────────┘
```

### 3. 词典查询流程

```
用户点击生词
    │
    ▼
┌─────────────┐
│  显示弹窗    │ ──► JavaScript 拦截点击事件
│  Popup      │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  预存数据?   │ ──► 检查 segment.words 字段
│  Check Cache │
└──────┬──────┘
       │
   Yes /   \ No
       │     \
       ▼      ▼
┌─────────┐  ┌─────────────┐
│直接使用  │  │ 实时查询    │ ──► GET /word/{word}
│缓存数据  │  │             │
└────┬────┘  └──────┬──────┘
     │              │
     │              ▼
     │         ┌─────────────┐
     │         │ 有道词典 API │ ──► aiohttp 异步请求
     │         │ 或 Free Dict │
     │         └──────┬──────┘
     │                │
     └────────────────┘
                      ▼
               ┌─────────────┐
               │ 显示释义    │ ──► 中文释义 + 英文释义
               │ Display     │ ──► 音标 + 词性 + 例句
               └─────────────┘
```

---

## 关键模块设计

### 1. 处理流水线 (pipeline.py)

```python
async def run_pipeline(task_id, deck_id, youtube_url, lang):
    """主处理流水线"""
    try:
        # 1. 下载
        await update_status(deck_id, "downloading")
        info = await download_video(youtube_url, lang)
        
        # 2. 解析字幕
        await update_status(deck_id, "extracting")
        segments = parse_subtitles(info['subtitle_path'])
        
        # 3. 切分音频
        await update_status(deck_id, "splitting")
        for seg in segments:
            await split_audio(info['audio_path'], seg)
        
        # 4. 生成牌组
        await update_status(deck_id, "generating")
        await generate_apkg(deck_id, segments)
        
        # 5. 完成
        await update_status(deck_id, "done")
        
    except Exception as e:
        await update_status(deck_id, "error", str(e))
        raise
```

### 2. 字幕切分策略 (splitter.py)

**核心算法：** 按句子边界合并短句

```python
def merge_segments_by_sentences(segments, min_duration=3000):
    """
    将短片段按句子边界合并
    
    规则：
    1. 如果当前片段 < 3秒，尝试与下一个片段合并
    2. 只在句号、问号、感叹号处分割
    3. 合并后总时长不超过 15秒
    """
    merged = []
    current = None
    
    for seg in segments:
        if current is None:
            current = seg
        elif should_merge(current, seg):
            current = merge_two(current, seg)
        else:
            merged.append(current)
            current = seg
    
    if current:
        merged.append(current)
    
    return merged
```

### 3. 词典服务 (dictionary.py)

**多源查询策略：**

```python
async def lookup_word(word: str, lang: str = "en"):
    """
    查询单词释义，支持多源回退
    
    优先级：
    1. 有道词典 API（中英双语）
    2. Free Dictionary API（仅英文，备用）
    """
    # 尝试有道词典
    result = await youdao_lookup(word)
    if result:
        return result
    
    # 回退到 Free Dictionary
    if lang == "en":
        result = await free_dict_lookup(word)
        if result:
            return result
    
    return None
```

### 4. 卡片模板设计

**正面（side=0）：**
- 圆形旋转缩略图
- 音频播放器（自动循环）
- 播放控制按钮
- 变速选择器

**背面（side=1）：**
- 所有正面元素
- 字幕文本显示
- 生词下划线标注
- 点击弹出释义

**技术特点：**
- 纯 HTML/CSS/JS，无外部依赖
- 支持暗色模式切换
- 响应式设计
- 内联所有资源（适合离线使用）

---

## 性能优化

### 1. 异步处理

- 视频下载使用 `BackgroundTasks`，不阻塞 API 响应
- 数据库操作使用 `aiosqlite` 异步驱动
- HTTP 请求使用 `aiohttp` 异步客户端

### 2. 流式进度更新

```python
# 实时更新处理进度
await db.execute(
    "UPDATE deck SET progress = ?, total = ? WHERE id = ?",
    (current, total, deck_id)
)
```

### 3. 缓存策略

- **单词标注缓存：** 存储在 `segment.words` 字段，避免重复查询
- **缩略图缓存：** 下载一次，重复使用
- **音频片段缓存：** 生成后持久化存储

### 4. 临时文件管理

```python
# 使用 tempfile 创建临时目录
with tempfile.TemporaryDirectory() as tmpdir:
    # 下载和处理...
    # 自动清理
```

---

## 安全设计

### 1. 输入验证

- URL 格式验证（Pydantic HttpUrl）
- 文件名安全检查（防止路径遍历）
- SQL 注入防护（参数化查询）

### 2. CORS 配置

```python
# 允许 Anki iframe 跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 3. 文件访问控制

- 音频文件通过 `/storage` 路径提供
- 不暴露绝对路径
- 文件名使用 UUID，不可预测

---

## 扩展性设计

### 1. 模块化服务层

每个服务独立封装，便于替换：

```python
# 当前实现
from backend.services.downloader import YouTubeDownloader

# 未来可替换为其他平台
from backend.services.downloader import BilibiliDownloader
```

### 2. 插件化词典

```python
class DictionaryProvider(ABC):
    @abstractmethod
    async def lookup(self, word: str) -> dict:
        pass

# 可注册多个 provider
providers = [YoudaoProvider(), FreeDictProvider()]
```

### 3. 多用户支持（规划中）

```sql
-- 未来添加用户表
CREATE TABLE user (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE,
    password_hash TEXT,
    created_at DATETIME
);

-- deck 表添加 user_id 外键
ALTER TABLE deck ADD COLUMN user_id TEXT REFERENCES user(id);
```

---

## 部署架构

### 单机部署

```
┌─────────────────────────────────────┐
│           云服务器                   │
│  ┌─────────────────────────────┐   │
│  │  Nginx (反向代理)            │   │
│  │  - 端口 80/443              │   │
│  └─────────────┬───────────────┘   │
│                │                    │
│  ┌─────────────▼───────────────┐   │
│  │  FastAPI (Uvicorn)          │   │
│  │  - 端口 8000                │   │
│  │  - 4 workers                │   │
│  └─────────────┬───────────────┘   │
│                │                    │
│  ┌─────────────▼───────────────┐   │
│  │  SQLite                     │   │
│  │  storage/ (音频文件)         │   │
│  └─────────────────────────────┘   │
└─────────────────────────────────────┘
```

### Systemd 服务配置

```ini
[Unit]
Description=AnkiAudio Platform
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/anki-audio-platform
Environment="PATH=/opt/anki-audio-platform/venv/bin"
ExecStart=/opt/anki-audio-platform/venv/bin/python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

---

## 监控与日志

### 日志配置

```python
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
```

### 关键日志点

- 任务提交：`logger.info(f"已提交任务 task_id={task_id}")`
- 状态变更：`logger.info(f"状态更新: {deck_id} -> {status}")`
- 错误记录：`logger.error(f"处理失败: {e}", exc_info=True)`

---

## 待改进项

详见 [ROADMAP.md](ROADMAP.md)，主要包括：

1. **本地文件上传** - 支持上传自有音频+字幕
2. **牌组管理** - 删除、重命名、预览功能
3. **用户系统** - 多用户隔离、JWT 认证
4. **邮件通知** - 处理完成提醒
5. **卡片编辑** - 导出前修改字幕
6. **单元测试** - pytest 测试覆盖
