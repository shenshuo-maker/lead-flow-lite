# LeadFlow Lite

面向 **餐饮、美业、健身、教培等本地服务业** 门店的轻量 **AI 获客演示系统**：从「求推荐/问价」类意向中筛客资、递进式私域私信、极简后台与套餐说明页，适合现场演示与交付。

## 技术栈

- 前端：React 19、Vite 8、Tailwind CSS 4、React Router
- 后端：Python 3.10+、Flask、Flask-CORS
- 数据：JSON 文件（`backend/data/`，可扩展为话术库等轻量存盘）
- AI：OpenAI API（`gpt-3.5-turbo`），**未配置 Key 时自动降级为演示话术**，不阻断演示

## 目录结构

```
leadflow-lite/
├── frontend/          # React 前端
├── backend/           # Flask 后端
├── .env.example       # 环境变量示例（API Key 等）
└── README.md
```

## 环境准备

1. 安装 [Node.js](https://nodejs.org/)（建议 LTS）与 [Python 3.10+](https://www.python.org/)。
2. 复制环境变量（任选其一，推荐在 `backend` 下配置）：

   ```bash
   copy .env.example backend\.env
   ```

3. 编辑 `backend\.env`，填入 `OPENAI_API_KEY`（可选，不填走演示模式）。

**收款（无营业执照时）**：默认 `PAYMENT_MODE=manual_transfer`，客户按页面提示用支付宝转账并在「备注」填写系统生成的商户单号；你方核对到账后，用 `POST /api/orders/<order_id>/confirm-paid` + `X-Order-Confirm-Secret` 确认开通。支付宝/微信的「个人收款码」没有开放自动验款 API，无法像官方商户支付一样全自动回调。

> 安全提示：请勿把 `.env` / `backend.env` 等密钥文件提交到仓库；若曾泄露 Key，请到控制台立刻“旋转/作废”并重新生成。

## 安装依赖

**后端：**

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**前端：**

```bash
cd frontend
npm install
```

## 启动（开发）

**终端 1 — 启动 API（默认 5000 端口）：**

```bash
cd backend
python app.py
```

**终端 2 — 启动前端（Vite 开发服务器，已代理 `/api` 到 5000）：**

```bash
cd frontend
npm run dev
```

浏览器访问 Vite 提示的本地地址（一般为 `http://127.0.0.1:5173`）。

- 落地页可进入「管理后台」；核心流程在 **意向客发现**（省市区下拉 + 需求词预设 + 按最近时间排序的模拟客资，**不爬取**各平台；合规接入后再换真实源）→ **按场景**生成私信（3 场景×3 套）→ **客户跟进**页记客情（本机 localStorage 演示）。
- 若未配置 `OPENAI_API_KEY`，仍可使用完整 UI，话术为内置演示版。

**生产/直连后端时**：可在 `frontend` 中复制 `.env.example` 为 `.env`，设置 `VITE_API_BASE=http://你的后端地址:5000`，并重新 `npm run build`。

## 生产构建

```bash
cd frontend
npm run build
```

将 `frontend/dist` 由任意静态服务托管；需保证静态站点能访问到后端 API 地址，并在后端为前端来源配置 CORS（开发模式已放通，生产应收紧为具体域名）。

## 后续替换真实数据 / AI

- 模拟意向客资：修改 `backend/services/mock_leads.py`（与路由解耦；默认模拟发帖求推荐的 C 端用户）
- 文案生成：修改 `backend/services/ai_messages.py`（可换模型、改 Prompt）
- 本地 JSON 存盘：见 `backend/storage.py` 与 `backend/data/`

## 许可与声明

本仓库为**演示/售卖用交付物骨架**，其中套餐价格为示例文案，正式商务以合同为准。
