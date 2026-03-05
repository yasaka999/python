# AnkiAudio Platform API 文档

## 概述

AnkiAudio Platform 是一个个人云端音频 Anki 服务，自动从 YouTube 视频提取音频和字幕，生成可导入 Anki 的听力卡片牌组。

**基础 URL:** `http://cloudcone.080828.xyz:8000`

**API 版本:** v0.1.0

**最后更新:** 2026-03-06

---

## 目录

- [健康检查](#健康检查)
- [处理流程](#处理流程)
- [卡片渲染](#卡片渲染)
- [导出与偏好](#导出与偏好)
- [数据模型](#数据模型)
- [错误处理](#错误处理)

---

## 健康检查

### 服务状态

检查服务是否正常运行。

**Endpoint:**
```
GET /health
```

**示例请求:**
```bash
curl -X GET "http://cloudcone.080828.xyz:8000/health"
```

**成功响应 (200):**
```json
{
  "status": "ok",
  "version": "0.1.0"
}
```

---

## 处理流程

### 提交视频处理

提交 YouTube URL 开始处理流程。系统会在后台下载视频、提取音频和字幕、切分音频片段。

**Endpoint:**
```
POST /process
```

**Content-Type:** `application/json`

**请求体:**

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `youtube_url` | string | 是 | YouTube 视频链接 |
| `lang` | string | 否 | 字幕语言代码，默认 `en` |

**支持的语言代码:**
- `en` - 英语
- `zh-CN` - 简体中文
- `zh-TW` - 繁体中文
- `ja` - 日语
- `ko` - 韩语
- `fr` - 法语
- `de` - 德语
- `es` - 西班牙语
- `ru` - 俄语
- `auto` - 自动检测

**示例请求:**
```bash
curl -X POST "http://cloudcone.080828.xyz:8000/process" \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "lang": "en"
  }'
```

**成功响应 (200):**
```json
{
  "task_id": "a1b2c3d4e5f6...",
  "deck_id": "f6e5d4c3b2a1...",
  "status_url": "/status/a1b2c3d4e5f6..."
}
```

**错误响应:**
- `400` - 请求参数错误（URL 格式不正确）
- `500` - 服务器内部错误

---

### 查询任务状态

轮询查询任务处理进度。

**Endpoint:**
```
GET /status/{task_id}
```

**路径参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| `task_id` | string | 任务 ID（由 `/process` 返回） |

**示例请求:**
```bash
curl -X GET "http://cloudcone.080828.xyz:8000/status/a1b2c3d4e5f6..."
```

**成功响应 (200):**
```json
{
  "task_id": "a1b2c3d4e5f6...",
  "deck_id": "f6e5d4c3b2a1...",
  "status": "processing",
  "title": "Video Title",
  "progress": 15,
  "total": 42,
  "error_msg": null,
  "done": false
}
```

**状态说明:**

| 状态 | 说明 |
|------|------|
| `pending` | 等待处理 |
| `downloading` | 正在下载视频 |
| `extracting` | 正在提取音频/字幕 |
| `splitting` | 正在切分音频 |
| `generating` | 正在生成 Anki 牌组 |
| `done` | 处理完成 |
| `error` | 处理失败 |

**错误响应:**
- `404` - 任务不存在

---

### 获取牌组列表

获取所有已创建的牌组列表。

**Endpoint:**
```
GET /decks
```

**示例请求:**
```bash
curl -X GET "http://cloudcone.080828.xyz:8000/decks"
```

**成功响应 (200):**
```json
[
  {
    "id": "f6e5d4c3b2a1...",
    "youtube_url": "https://www.youtube.com/watch?v=...",
    "title": "Video Title",
    "lang_cd": "en",
    "status": "done",
    "progress": 42,
    "total": 42,
    "created_at": "2026-03-05T12:34:56"
  }
]
```

---

## 卡片渲染

### 渲染卡片页面

服务端渲染 HTML 卡片页面，供 Anki iframe 加载使用。

**Endpoint:**
```
GET /card/{card_id}?side={side}
```

**路径参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| `card_id` | string | 卡片 ID（segment ID） |

**查询参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `side` | integer | 否 | 卡片面，`0`=正面，`1`=背面，默认 `0` |

**示例请求:**
```bash
# 获取卡片正面（仅音频播放器）
curl -X GET "http://cloudcone.080828.xyz:8000/card/seg_001?side=0"

# 获取卡片背面（音频+字幕+单词标注）
curl -X GET "http://cloudcone.080828.xyz:8000/card/seg_001?side=1"
```

**成功响应 (200):**
返回 HTML 页面，包含：
- 圆形旋转缩略图
- 音频播放器（支持循环播放、变速）
- 时间显示和进度条
- 播放控制按钮
- 字幕文本（背面显示）
- 生词标注（点击显示释义）

**播放器功能:**
- ▶️ 播放/暂停
- ⏮️ 后退 5 秒
- ⏭️ 前进 5 秒
- 🔄 循环播放（正面自动开启）
- ⚡ 变速播放（0.5x, 0.75x, 1x, 1.25x, 2x）
- 📊 进度条拖拽

**错误响应:**
- `404` - 卡片不存在

---

### 查询单词释义

查询单词的中英双语释义。

**Endpoint:**
```
GET /word/{word}?lang={lang}
```

**路径参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| `word` | string | 要查询的单词 |

**查询参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `lang` | string | 否 | 语言代码，默认 `en` |

**示例请求:**
```bash
curl -X GET "http://cloudcone.080828.xyz:8000/word/hello"
```

**成功响应 (200):**
```json
{
  "word": "hello",
  "phonetic": "/həˈloʊ/",
  "pos": "int.",
  "definition_cn": "你好；喂（用于打招呼或引起注意）",
  "definition_en": "used as a greeting or to begin a telephone conversation",
  "example": "Hello, how are you?"
}
```

**词典来源:**
- 有道词典 API（主要）
- Free Dictionary API（英文备用）

**错误响应:**
- `404` - 未找到该单词

---

### 获取卡片缩略图

获取卡片对应的牌组缩略图。

**Endpoint:**
```
GET /card/thumbnail/{card_id}
```

**路径参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| `card_id` | string | 卡片 ID |

**示例请求:**
```bash
curl -X GET "http://cloudcone.080828.xyz:8000/card/thumbnail/seg_001"
```

**成功响应 (200):**
返回 JPEG 图片文件。

**错误响应:**
- `404` - 缩略图不存在

---

## 导出与偏好

### 下载 Anki 牌组

下载已生成的 `.apkg` 文件，可直接导入 Anki。

**Endpoint:**
```
GET /export/{deck_id}/anki
```

**路径参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| `deck_id` | string | 牌组 ID |

**示例请求:**
```bash
curl -X GET "http://cloudcone.080828.xyz:8000/export/f6e5d4c3b2a1.../anki" \
  -o "MyDeck.apkg"
```

**成功响应 (200):**
返回 `.apkg` 二进制文件，文件名格式：`{title}.apkg`

**错误响应:**
- `400` - 牌组尚未处理完成
- `404` - 牌组不存在或 apkg 文件不存在

---

### 获取用户偏好

获取用户的界面偏好设置（如夜间模式）。

**Endpoint:**
```
GET /deck/prefer/{username}/
```

**路径参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| `username` | string | 用户名（MVP 阶段使用 `default`） |

**示例请求:**
```bash
curl -X GET "http://cloudcone.080828.xyz:8000/deck/prefer/default/"
```

**成功响应 (200):**
```json
{
  "dark_mode": false
}
```

---

### 设置用户偏好

设置用户的界面偏好。

**Endpoint:**
```
POST /deck/prefer/{username}/
```

**路径参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| `username` | string | 用户名 |

**查询参数:**

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `dark_mode` | boolean | 否 | 是否启用夜间模式 |

**示例请求:**
```bash
curl -X POST "http://cloudcone.080828.xyz:8000/deck/prefer/default/?dark_mode=true"
```

**成功响应 (200):**
```json
{
  "ok": true
}
```

---

## 静态文件服务

### 音频文件

音频片段文件通过静态文件服务提供。

**URL 格式:**
```
/storage/{deck_id}/{segment_id}.mp3
```

**示例:**
```
http://cloudcone.080828.xyz:8000/storage/f6e5d4c3b2a1.../seg_001.mp3
```

---

## 数据模型

### Deck（牌组）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | TEXT | 主键，UUID |
| `youtube_url` | TEXT | YouTube 视频链接 |
| `title` | TEXT | 视频标题 |
| `thumbnail` | TEXT | 缩略图文件路径 |
| `lang_cd` | TEXT | 字幕语言代码 |
| `status` | TEXT | 处理状态 |
| `progress` | INTEGER | 当前处理进度 |
| `total` | INTEGER | 总片段数 |
| `error_msg` | TEXT | 错误信息 |
| `created_at` | DATETIME | 创建时间 |

### Segment（片段/卡片）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | TEXT | 主键，UUID |
| `deck_id` | TEXT | 所属牌组 ID |
| `seg_index` | INTEGER | 片段序号 |
| `audio_path` | TEXT | 音频文件路径 |
| `sentence` | TEXT | 字幕文本 |
| `words` | TEXT | 单词标注数据（JSON） |
| `start_ms` | INTEGER | 开始时间（毫秒） |
| `end_ms` | INTEGER | 结束时间（毫秒） |
| `created_at` | DATETIME | 创建时间 |

### Task（任务）

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | TEXT | 主键，UUID |
| `deck_id` | TEXT | 关联牌组 ID |
| `status` | TEXT | 任务状态 |
| `created_at` | DATETIME | 创建时间 |

---

## 错误处理

### 错误响应格式

所有错误遵循以下格式：

```json
{
  "detail": "错误信息"
}
```

### HTTP 状态码

| 状态码 | 含义 | 常见场景 |
|--------|------|----------|
| 200 | 成功 | 正常响应 |
| 400 | 请求错误 | 参数验证失败、牌组未完成 |
| 404 | 未找到 | 资源不存在 |
| 422 | 验证错误 | 请求体格式错误 |
| 500 | 服务器错误 | 内部处理异常 |

---

## 完整使用流程示例

### 1. 提交视频处理

```bash
# 提交 YouTube 视频
curl -X POST "http://cloudcone.080828.xyz:8000/process" \
  -H "Content-Type: application/json" \
  -d '{
    "youtube_url": "https://www.youtube.com/watch?v=VIDEO_ID",
    "lang": "en"
  }'

# 响应：
# {"task_id": "abc123", "deck_id": "def456", "status_url": "/status/abc123"}
```

### 2. 轮询任务状态

```bash
# 每 2 秒查询一次状态，直到 done=true
curl -X GET "http://cloudcone.080828.xyz:8000/status/abc123"

# 当 status=done 时继续下一步
```

### 3. 下载 Anki 牌组

```bash
# 下载 .apkg 文件
curl -X GET "http://cloudcone.080828.xyz:8000/export/def456/anki" \
  -o "MyDeck.apkg"
```

### 4. 导入 Anki

1. 打开 Anki
2. 文件 → 导入
3. 选择下载的 `.apkg` 文件
4. 开始学习！

---

## Web 管理界面

访问根路径即可打开 Web 管理界面：

```
http://cloudcone.080828.xyz:8000
```

功能包括：
- 提交 YouTube 链接
- 查看处理进度
- 下载 Anki 牌组
- 管理历史记录
