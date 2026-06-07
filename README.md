# Novel2Script · AI 小说转剧本工具
AI小说转剧本工具 - 将小说章节转换为结构化YAML剧本，辅助编剧快速生成初稿。
以下是一个完整、规范的 `README.md`，请直接复制到项目根目录替换原有内容。

> 将任意小说（建议≥3章）快速转换为结构化 YAML 剧本，支持在线编辑、追问打磨、历史记录与批量处理。

本项目为 **XEngineer 新工科计划** 第三批议题「AI 小说转剧本工具」的参赛作品，基于智谱 GLM-4.5-Air 大模型，提供 Web 端一站式剧本改编体验。

---

## ✨ 功能特性

- **小说 → YAML 剧本**  
  智能提取角色、场景、对话，输出严格遵循自定义 Schema 的 YAML 文件。
- **多格式导入**  
  支持 `.txt` / `.md` / `.docx` 文件，可追加或替换内容。
- **在线编辑**  
  右侧 YAML 输出区可直接修改，修改后的内容将用于后续追问或导出。
- **可追问打磨**  
  基于当前 YAML 向 AI 提问或请求修改（如“把第二场地点改为咖啡馆”），AI 可直接返回修改后的完整 YAML，一键应用。
- **历史记录（含问答）**  
  本地保存最近 10 次转换记录及每次的追问对话，支持一键加载任一历史版本。
- **批量转换**  
  一次性上传多个小说文件，后台串行处理并分别提供结果下载。
- **自定义导出文件名**  
  导出时自动从 YAML 的 `title` 字段提取文件名，也支持手动输入。
- **智能约束**  
  自动检测章节数（至少3章）、文本长度（≤80000 字符），不足时友好弹窗。

---

## 🧩 技术栈

| 领域         | 技术                                 |
| ------------ | ------------------------------------ |
| 后端框架     | Flask 2.3+                           |
| AI 模型      | 智谱 GLM-4.5-Air（zhipuai SDK）      |
| 前端         | 原生 HTML / CSS / JavaScript          |
| 文件解析     | python-docx, chardet                 |
| YAML 处理    | PyYAML                               |
| 环境管理     | python-dotenv                        |

---

## 📦 安装与运行

### 1. 克隆仓库
```bash
git clone https://github.com/Tacita-Ln/Novel2Script.git
cd Novel2Script
```

### 2. 创建虚拟环境（推荐）
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux / Mac:
source venv/bin/activate
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 配置 API Key
复制 `.env.example` 为 `.env`，并填入你的智谱 API Key：
```ini
ZHIPU_API_KEY=你的真实key
MODEL_NAME=glm-4.5-air
```
> 获取 API Key：[智谱AI开放平台](https://open.bigmodel.cn/)

### 5. 启动服务
```bash
python -m app.app
```
打开浏览器访问 `http://127.0.0.1:5000`

---

## 🖥️ 使用指南

1. **左侧（导入小说）**  
   - 直接粘贴小说文本，或上传 `.txt` / `.md` / `.docx` 文件。  
   - 勾选「追加到当前内容」可将文件内容追加到已有文本后。  
   - 点击「清空」可快速清空输入框。

2. **点击「✨ 转换为剧本 YAML」**  
   - 系统会自动检测章节数（≥3 章），若不足会弹窗询问是否继续。  
   - 转换过程约 10~20 秒，右侧将显示生成的可编辑 YAML。  
   - 转换成功后，该记录会自动保存到右侧历史列表。

3. **中栏（编辑与追问）**  
   - **YAML 编辑**：可直接修改右侧文本框中的内容，所有后续操作（追问、导出）均基于当前编辑后的内容。  
   - **可追问打磨**：输入问题（如“请检查主角台词是否自然”），AI 会给出回答；若要求修改并返回了新 YAML，可点击「应用修改后的 YAML」一键替换。  
   - **导出**：可自定义文件名（默认自动从 `title` 提取），点击「导出 YAML」下载文件。

4. **右栏（历史记录）**  
   - 每次成功转换后自动保存（含当时的小说摘要、YAML 和所有追问对话）。  
   - 点击「加载」可将历史 YAML 恢复到中栏，并允许继续追问。  
   - 点击「展开问答」可查看该次转换后的每一次追问与回答。  
   - 「清空历史」会删除所有本地存储的记录。

---

## 📐 YAML Schema 说明

完整 Schema 定义及设计理由请参见 [`docs/SCHEMA_DESIGN.md`](./docs/SCHEMA_DESIGN.md)。

核心结构预览：
```yaml
title: string
author: string
logline: string
characters:
  - name: string
    age: int (可选)
    personality: string
    role_type: 主角/配角/反派
scenes:
  - scene_id: int
    location: string
    time: string
    action: string (可选)
    dialogues:
      - character: string
        line: string
```

---

## 🎥 演示视频

[点击观看完整演示视频] https://www.bilibili.com/video/BV1ZqEt6xEVs/  
> 视频包含：小说输入 → 转换 → YAML 编辑 → 追问修改 → 自定义导出 → 历史加载全流程。

---

## 📝 依赖清单（原创性说明）

- **后端**：Flask、zhipuai、PyYAML、python-dotenv、chardet、python-docx
- **前端**：原生 HTML/CSS/JS + js-yaml（CDN）
- **AI 模型**：智谱 GLM-4.5-Air（仅作为 API 调用，未修改模型本身）

所有核心转换逻辑、前端交互、历史存储、追问打磨、批量处理等均为本人原创。

---

## 🚧 已知限制与后续规划

- 单次转换的小说文本最大长度为 **80000 字符**（约 4 万汉字），超出会返回错误提示。
- 实际模型上下文窗口更大，但出于性能和成本考虑设置了应用层限制。
- 批量转换时为串行处理，文件较多时等待时间较长。
- 后续可增加剧本质量评分、Fountain/PDF 导出、角色关系图等。

---

## 📄 许可证

MIT License © 2026 Tacita-Ln

---

## 🙏 致谢

- 智谱 AI 提供 GLM-4.5-Air API
- XEngineer 新工科计划提供赛题与平台
