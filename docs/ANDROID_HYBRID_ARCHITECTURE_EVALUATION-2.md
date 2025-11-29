# EEBot Android 移植評估報告 - 混合架構方案 (第 2 段)

> **分段資訊**: 本文檔共 2 段
> - 📄 **當前**: 第 2 段 - 成本效益、風險評估與部署方案
> - ⬅️ **上一段**: [ANDROID_HYBRID_ARCHITECTURE_EVALUATION-1.md](./ANDROID_HYBRID_ARCHITECTURE_EVALUATION-1.md)
> - 📑 **完整索引**: [返回索引](./ANDROID_HYBRID_ARCHITECTURE_EVALUATION.md)

---

## 📖 本段內容

- [成本效益分析](#-成本效益分析)
- [風險評估與緩解](#-風險評估與緩解)
- [概念驗證 (PoC)](#-概念驗證-poc)
- [部署選項分析](#-部署選項分析)
- [安全性設計](#-安全性設計)
- [使用者體驗設計](#-使用者體驗設計)
- [可擴展性規劃](#-可擴展性規劃)
- [結論與建議](#-結論與建議)

---

## 💰 成本效益分析

### 開發成本估算

| 項目 | 時間 (小時) | 人力成本估算 |
|------|------------|-------------|
| Phase 0: 環境準備 | 2-3 | 低 |
| Phase 1: API Server | 8-12 | 中 |
| Phase 2: Android Client | 6-10 | 中 |
| Phase 3: 整合測試 | 2-4 | 低 |
| Phase 4: Docker 部署 | 4-6 | 中 |
| Phase 5: 文檔編寫 | 2-3 | 低 |
| **總計** | **24-38** | **中等** |

**保守估計**: **28 小時**

---

### 基礎設施成本

#### 選項 A: 本地 PC 部署 (推薦個人使用)

| 項目 | 成本 |
|------|------|
| **硬體** | $0 (使用現有 PC) |
| **軟體** | $0 (Docker 免費) |
| **網路** | $0 (家用網路 + DDNS) |
| **總計** | **$0** |

---

#### 選項 B: 雲端部署 (推薦商業使用)

**雲端平台選項**:

| 平台 | 方案 | 規格 | 月費 | 適用性 |
|------|------|------|------|--------|
| **AWS EC2** | t3.small | 2 vCPU, 2GB RAM | ~$15 | ⭐⭐⭐⭐ 推薦 |
| **Google Cloud** | e2-small | 2 vCPU, 2GB RAM | ~$13 | ⭐⭐⭐⭐ 推薦 |
| **DigitalOcean** | Droplet | 1 vCPU, 2GB RAM | ~$12 | ⭐⭐⭐⭐⭐ 最推薦 |
| **Linode** | Nanode | 1 vCPU, 1GB RAM | ~$5 | ⭐⭐⭐ 經濟型 |
| **Heroku** | Hobby | 512MB RAM | ~$7 | ⭐⭐ 簡單但受限 |

**推薦配置**: DigitalOcean Droplet (2GB RAM, $12/月)

---

### 投資回報分析 (ROI)

#### 一次性投入
- 開發時間: 28 小時
- 開發成本: $0 (自行開發)
- 測試時間: 4 小時

**總投入**: **32 小時**

#### 運營成本 (月)
- 雲端伺服器: $12/月 (或 $0 本地部署)
- 維護時間: 1-2 小時/月

**月成本**: **$12** (雲端) 或 **$0** (本地)

#### 收益
- **時間節省**: 隨時隨地控制執行 (vs 綁定桌面 PC)
- **靈活性提升**: 外出也能管理課程
- **可擴展性**: 未來可支援多使用者

**無形收益**: 極高

---

## ⚠️ 風險評估與緩解

### 技術風險

| 風險 | 機率 | 影響 | 緩解策略 |
|------|------|------|---------|
| **API 效能瓶頸** | 低 | 中 | 實施快取機制、非同步執行 |
| **網路不穩定** | 中 | 高 | 實施重試機制、離線緩存 |
| **認證安全性** | 中 | 高 | 使用 HTTPS、JWT Token、定期輪替 |
| **Docker 部署問題** | 低 | 中 | 詳細文檔、測試環境驗證 |
| **瀏覽器相容性** | 低 | 低 | 使用穩定版 Chrome、定期更新 |

---

### 安全風險

| 風險 | 機率 | 影響 | 緩解策略 |
|------|------|------|---------|
| **未授權存取** | 中 | 高 | JWT 認證、API Rate Limiting |
| **中間人攻擊** | 低 | 高 | 強制 HTTPS、證書 Pinning |
| **密碼洩露** | 低 | 高 | bcrypt 雜湊、多因素認證 (未來) |
| **DDoS 攻擊** | 低 | 中 | Cloudflare、Rate Limiting |

---

### 營運風險

| 風險 | 機率 | 影響 | 緩解策略 |
|------|------|------|---------|
| **伺服器當機** | 低 | 高 | 自動重啟、健康檢查 |
| **資料遺失** | 低 | 高 | 定期備份、版本控制 |
| **依賴套件過時** | 中 | 中 | Dependabot、定期更新 |
| **成本超支** | 低 | 低 | 監控使用量、設定預算警報 |

---

## 🔬 概念驗證 (PoC)

### PoC 目標

驗證混合架構的核心可行性：
1. ✅ API Server 可成功封裝原有功能
2. ✅ Android Client 可順利呼叫 API
3. ✅ 非同步執行機制正常運作

### PoC 範圍

**最小可行產品 (MVP)**:
- ✅ 基礎 API Server (Flask)
- ✅ 認證系統 (簡化版)
- ✅ 單一 API 端點 (/api/execute)
- ✅ Android Client (基礎版)

**預估時間**: **8-10 小時**

### PoC 實施計畫

#### Step 1: 最簡 API Server (3-4h)

```python
# poc_server.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import time

app = Flask(__name__)
CORS(app)

# 簡化的認證 (PoC 用)
VALID_TOKEN = 'test_token_12345'

def execute_in_background():
    """模擬背景執行"""
    time.sleep(5)  # 模擬執行 5 秒
    print('Execution completed!')

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    if data.get('username') == 'test' and data.get('password') == 'test':
        return jsonify({'status': 'success', 'token': VALID_TOKEN})
    return jsonify({'status': 'error'}), 401

@app.route('/api/execute', methods=['POST'])
def execute():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if token != VALID_TOKEN:
        return jsonify({'status': 'error', 'message': 'Unauthorized'}), 401

    # 非同步執行
    thread = threading.Thread(target=execute_in_background)
    thread.daemon = True
    thread.start()

    return jsonify({'status': 'accepted', 'task_id': 'poc_task_001'}), 202

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
```

#### Step 2: 最簡 Android Client (2-3h)

```python
# poc_client.py
import requests

class PoCClient:
    def __init__(self, server_url):
        self.server_url = server_url
        self.token = None

    def login(self):
        response = requests.post(f'{self.server_url}/api/login',
                                  json={'username': 'test', 'password': 'test'})
        if response.status_code == 200:
            self.token = response.json()['token']
            return True
        return False

    def execute(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        response = requests.post(f'{self.server_url}/api/execute', headers=headers)
        return response.json()

# 測試
if __name__ == '__main__':
    client = PoCClient('http://localhost:5000')

    if client.login():
        print('✅ Login successful')
        result = client.execute()
        print(f'✅ Execution result: {result}')
    else:
        print('❌ Login failed')
```

#### Step 3: 整合測試 (1h)

1. 啟動 PoC Server
2. 運行 PoC Client
3. 驗證非同步執行
4. 檢查錯誤處理

#### Step 4: 決策點 (1h)

**PoC 成功標準**:
- [x] Client 成功登入並取得 Token
- [x] Client 成功觸發非同步執行
- [x] Server 正確處理請求
- [x] 錯誤處理正常運作

**決策**:
- ✅ 成功 → 繼續完整實施
- ❌ 失敗 → 重新評估架構

---

## 🚀 部署選項分析

### 選項 1: 本地 PC 部署 (推薦個人使用)

#### 架構圖

```
家用網路
├── PC (Windows/Linux/macOS)
│   └── Docker Container
│       └── EEBot API Server
│           ├── Flask API
│           ├── Selenium
│           └── MitmProxy
│
└── Router
    ├── Port Forwarding: 5000 → PC:5000
    └── DDNS (動態 DNS)
        ↓
        ↓ Internet
        ↓
Android 設備 (外網)
```

#### 優點
- ✅ **零成本**: 不需額外雲端費用
- ✅ **完全控制**: 資料存放在本地
- ✅ **低延遲**: 在同一網路時回應快速

#### 缺點
- ❌ **可用性**: PC 需持續開機
- ❌ **外網存取**: 需要 DDNS 和 Port Forwarding
- ❌ **安全性**: 家用網路暴露風險

#### 實施步驟

**Step 1: 安裝 Docker**
```bash
# Windows
# 下載並安裝 Docker Desktop: https://www.docker.com/products/docker-desktop

# Linux (Ubuntu/Debian)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# macOS
# 下載並安裝 Docker Desktop: https://www.docker.com/products/docker-desktop
```

**Step 2: 啟動 API Server**
```bash
cd /path/to/eebot
docker-compose -f docker/docker-compose.yml up -d
```

**Step 3: 設定 Port Forwarding**
1. 登入路由器管理介面 (通常是 192.168.1.1)
2. 找到「虛擬伺服器」或「Port Forwarding」設定
3. 新增規則:
   - 外部端口: 5000
   - 內部 IP: PC 的區網 IP (例如 192.168.1.100)
   - 內部端口: 5000
   - 協議: TCP

**Step 4: 設定 DDNS (可選)**

使用 No-IP 或 DuckDNS 服務:
```bash
# 使用 DuckDNS (免費)
# 1. 註冊 https://www.duckdns.org
# 2. 取得 Token
# 3. 設定自動更新腳本

echo url="https://www.duckdns.org/update?domains=your-domain&token=your-token&ip=" | curl -k -o ~/duckdns/duck.log -K -
```

**Step 5: Android 端配置**
```python
# 在 Android 的 config_android.py 中設定
server_url = 'http://your-ddns-domain.duckdns.org:5000'
# 或使用固定 IP
server_url = 'http://123.45.67.89:5000'
```

---

### 選項 2: 雲端部署 (推薦商業使用)

#### 架構圖

```
Internet
  ↓
Cloudflare CDN/DDoS Protection
  ↓
Load Balancer (可選)
  ↓
雲端伺服器 (DigitalOcean Droplet)
  ├── Nginx (Reverse Proxy)
  │   └── SSL/TLS (Let's Encrypt)
  │       ↓
  └── Docker Container
      └── EEBot API Server
          ├── Flask API
          ├── Selenium
          └── MitmProxy
          ↓
          ↓
Android 設備 (全球任何地點)
```

#### 優點
- ✅ **高可用性**: 24/7 運行
- ✅ **穩定網路**: 商業級頻寬
- ✅ **安全性**: 專業級防護
- ✅ **擴展性**: 隨時升級規格

#### 缺點
- ❌ **月費成本**: $5-15/月
- ❌ **資料隱私**: 資料存放於雲端

#### 實施步驟 (以 DigitalOcean 為例)

**Step 1: 建立 Droplet**
1. 註冊 DigitalOcean 帳號
2. 建立 Droplet:
   - 映像: Ubuntu 22.04 LTS
   - 方案: Basic ($12/月, 2GB RAM)
   - 資料中心: Singapore (亞洲最近)
   - SSH Keys: 上傳公鑰

**Step 2: 初始化伺服器**
```bash
# SSH 連線
ssh root@your-droplet-ip

# 更新系統
apt update && apt upgrade -y

# 安裝 Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# 安裝 Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose
```

**Step 3: 部署應用**
```bash
# 上傳專案檔案 (從本地)
scp -r /path/to/eebot root@your-droplet-ip:/opt/eebot

# 在伺服器上啟動
cd /opt/eebot
docker-compose -f docker/docker-compose.yml up -d
```

**Step 4: 設定 Nginx + SSL**
```bash
# 安裝 Nginx
apt install nginx -y

# 安裝 Certbot (Let's Encrypt)
apt install certbot python3-certbot-nginx -y

# 取得 SSL 憑證
certbot --nginx -d your-domain.com

# Nginx 配置範例
cat > /etc/nginx/sites-available/eebot << 'EOF'
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

# 啟用站點
ln -s /etc/nginx/sites-available/eebot /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

**Step 5: 設定防火牆**
```bash
# 使用 ufw
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw enable
```

**Step 6: 監控與維護**
```bash
# 查看日誌
docker-compose logs -f

# 重啟服務
docker-compose restart

# 備份資料
tar -czf backup_$(date +%Y%m%d).tar.gz /opt/eebot/data
```

---

### 選項 3: 混合部署 (進階)

#### 架構圖

```
家用 PC (主要執行)
  ↓
  ↓ 同步
  ↓
雲端伺服器 (備援 + API)
  ↓
  ↓ Load Balance
  ↓
Android 設備
```

#### 優點
- ✅ **高可用性**: 雙重保障
- ✅ **成本控制**: 大部分在本地執行
- ✅ **負載分散**: 雲端處理 API，本地執行任務

#### 缺點
- ❌ **複雜度高**: 需要同步機制
- ❌ **維護成本**: 兩套環境

---

## 🔐 安全性設計

### 1. 認證與授權

#### JWT Token 機制

```python
# 生成 Token
from flask_jwt_extended import create_access_token

access_token = create_access_token(
    identity=user.id,
    expires_delta=timedelta(hours=24)
)
```

#### Token 刷新策略
- Access Token: 24 小時有效
- Refresh Token: 30 天有效
- 自動刷新機制

---

### 2. 通訊加密

#### HTTPS 強制
```python
# 強制 HTTPS 重定向
@app.before_request
def before_request():
    if not request.is_secure and app.env == 'production':
        url = request.url.replace('http://', 'https://', 1)
        return redirect(url, code=301)
```

#### TLS 1.3
- 使用最新的 TLS 1.3 協議
- Let's Encrypt 免費 SSL 憑證
- 定期更新憑證 (自動化)

---

### 3. 資料保護

#### 密碼雜湊
```python
from werkzeug.security import generate_password_hash, check_password_hash

# 儲存密碼
hashed = generate_password_hash(password, method='pbkdf2:sha256')

# 驗證密碼
check_password_hash(hashed, password)
```

#### 敏感資料加密
- 資料庫: SQLite 檔案加密
- 配置: 環境變數管理
- 日誌: 遮蔽敏感資訊

---

### 4. API 安全

#### Rate Limiting
```python
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=lambda: request.headers.get('Authorization', 'anonymous'),
    default_limits=["100 per hour"]
)

@app.route('/api/execute')
@limiter.limit("5 per hour")  # 每小時最多 5 次
def execute():
    pass
```

#### CORS 配置
```python
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://your-android-app.com"],
        "methods": ["GET", "POST", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

---

### 5. 日誌與審計

#### 存取日誌
```python
import logging

logging.basicConfig(
    filename='logs/api_access.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

@app.before_request
def log_request():
    logging.info(f'{request.method} {request.path} - {request.remote_addr}')
```

#### 敏感操作審計
- 記錄所有認證嘗試
- 記錄執行操作
- 記錄配置變更

---

## 👥 使用者體驗設計

### Android 端操作流程

#### 首次使用流程

```
[啟動應用]
    ↓
[伺服器設定]
    ├─ 輸入伺服器位址 (http://your-server.com:5000)
    ├─ 測試連線
    └─ 儲存設定
    ↓
[登入]
    ├─ 輸入帳號密碼
    ├─ (可選) 記住我
    └─ 登入成功
    ↓
[主選單]
```

#### 日常使用流程

```
[啟動應用]
    ↓
[自動登入] (若啟用記住我)
    ↓
[主選單]
    ├─ [1] 檢視課程列表
    │   └─ 捲動瀏覽所有課程
    │
    ├─ [2] 檢視目前排程
    │   └─ 查看已排程的課程
    │
    ├─ [3] 新增課程到排程
    │   ├─ 選擇課程編號
    │   └─ 確認新增
    │
    ├─ [4] 清空排程
    │   ├─ 確認警告
    │   └─ 清空完成
    │
    ├─ [5] 執行排程 ⭐
    │   ├─ 確認執行
    │   ├─ 取得 Task ID
    │   └─ 選擇監控或返回
    │       ├─ [監控] 即時顯示進度
    │       └─ [返回] 稍後查詢
    │
    └─ [6] 查詢執行狀態
        ├─ 輸入 Task ID
        └─ 顯示狀態與進度
```

---

### UI 改進建議 (未來)

#### Phase 2.1: 圖形化介面 (GUI)

使用 **Kivy** 或 **BeeWare** 建立真正的 Android App:

```python
# 使用 Kivy 範例
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

class EEBotApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')

        label = Label(text='EEBot Android Controller')
        button = Button(text='Execute Schedule')
        button.bind(on_press=self.execute)

        layout.add_widget(label)
        layout.add_widget(button)

        return layout

    def execute(self, instance):
        # 呼叫 API
        pass

EEBotApp().run()
```

**優點**:
- ✅ 原生 App 體驗
- ✅ 觸控友善
- ✅ 更美觀的介面

**預估開發時間**: 20-30 小時

---

#### Phase 2.2: 推送通知

使用 **Firebase Cloud Messaging (FCM)**:

```python
# 伺服器端推送通知
from firebase_admin import messaging

def send_completion_notification(device_token, task_id):
    message = messaging.Message(
        notification=messaging.Notification(
            title='執行完成',
            body=f'任務 {task_id} 已完成!'
        ),
        token=device_token
    )
    messaging.send(message)
```

**優點**:
- ✅ 即時通知執行結果
- ✅ 無需輪詢狀態

---

## 🔄 可擴展性規劃

### 短期擴展 (3-6 個月)

#### 1. 多使用者支援
- 使用者註冊系統
- 角色權限管理 (Admin/User)
- 個人化排程

#### 2. 排程自動化
```python
# 定時排程功能
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(
    func=execute_scheduled_tasks,
    trigger='cron',
    hour=2,  # 每天凌晨 2 點執行
    minute=0
)
scheduler.start()
```

#### 3. 報告優化
- PDF 格式報告
- Email 自動寄送
- 圖表視覺化

---

### 中期擴展 (6-12 個月)

#### 1. WebUI 管理介面
```
React/Vue.js 前端
    ↓
RESTful API (已有)
    ↓
EEBot 核心
```

**優點**:
- ✅ 跨平台存取 (瀏覽器)
- ✅ 更豐富的視覺化
- ✅ 團隊協作

#### 2. 分散式執行
```
多台執行節點
    ├─ Node 1 (PC)
    ├─ Node 2 (雲端)
    └─ Node 3 (備援)
        ↓
    任務調度器
        ↓
    Android 控制端
```

**優點**:
- ✅ 負載均衡
- ✅ 高可用性
- ✅ 效能提升

---

### 長期擴展 (1+ 年)

#### 1. AI 智能排程
- 學習使用習慣
- 自動建議課程
- 預測完成時間

#### 2. 跨平台擴展
- iOS App
- Web App
- 桌面 App (Electron)

#### 3. 企業版功能
- 團隊管理
- 稽核日誌
- SLA 保證

---

## 📋 結論與建議

### 總結

**混合架構方案評估結果**: ✅ **強烈推薦**

| 評估維度 | 評分 | 說明 |
|---------|------|------|
| **技術可行性** | ⭐⭐⭐⭐⭐ | 完全可行，無技術障礙 |
| **開發成本** | ⭐⭐⭐⭐⭐ | 28 小時，成本低 |
| **運營成本** | ⭐⭐⭐⭐⭐ | $0-12/月，極低 |
| **使用者體驗** | ⭐⭐⭐⭐ | 隨時隨地控制，體驗佳 |
| **可維護性** | ⭐⭐⭐⭐⭐ | 分離架構，易於維護 |
| **可擴展性** | ⭐⭐⭐⭐⭐ | 架構靈活，擴展性強 |
| **安全性** | ⭐⭐⭐⭐ | HTTPS + JWT，安全可靠 |

**總評**: ⭐⭐⭐⭐⭐ (5/5)

---

### 立即行動建議

#### 建議 1: 執行概念驗證 (PoC)
**時間**: 8-10 小時
**目標**: 驗證核心可行性
**輸出**: PoC 報告 + 最簡實作

#### 建議 2: 完整實施混合架構
**時間**: 24-38 小時
**目標**: 生產就緒版本
**輸出**: 可部署的系統 + 完整文檔

#### 建議 3: 雲端部署試運行
**成本**: $12/月 (DigitalOcean)
**時間**: 1-2 小時部署
**目標**: 實際環境測試

---

### 不建議的方案

❌ **完全移植到 Android**
- 開發時間: 150+ 小時
- 成功率: 低 (Selenium/MitmProxy 限制)
- 投資回報: 差

❌ **原生 Android 重寫**
- 開發時間: 150+ 小時
- 技術複雜度: 極高
- 維護成本: 極高

---

### 下一步行動

**Phase 0: 決策 (1-2 天)**
1. 評估本報告
2. 決定是否採用混合架構
3. 選擇部署方式 (本地 vs 雲端)

**Phase 1: PoC 驗證 (1-2 天)**
1. 建立最簡 API Server
2. 建立最簡 Android Client
3. 整合測試
4. Go/No-Go 決策

**Phase 2: 完整實施 (1-2 週)**
1. 按照實施計畫執行
2. 階段性驗收
3. 文檔編寫

**Phase 3: 上線運營 (持續)**
1. 部署到生產環境
2. 監控與維護
3. 收集使用者反饋
4. 迭代優化

---

## 📞 聯絡與支援

**報告編寫**: wizard03 (with Claude Code CLI)
**專案代號**: Gleipnir (格萊普尼爾)
**專案版本**: 2.0.5

**文檔更新日期**: 2025-11-24
**報告有效期**: 6 個月 (2025-05-24 前)

---

**本段結束**

> ⬅️ [返回上一段](./ANDROID_HYBRID_ARCHITECTURE_EVALUATION-1.md) | 📑 [返回索引](./ANDROID_HYBRID_ARCHITECTURE_EVALUATION.md)

✅ 文檔已全部閱讀完畢

**建議執行優先級**: 🔥 **高優先級** - 建議立即執行 PoC 驗證

---

*本報告為技術評估報告，實際實施可能因環境差異而需調整。*
*報告內容基於當前技術狀態，未來可能有所變化。*
*建議定期審查並更新本報告。*

---

**Happy Coding! 🚀**

*This evaluation report was generated with AI assistance (Claude Code CLI - Sonnet 4.5)*
