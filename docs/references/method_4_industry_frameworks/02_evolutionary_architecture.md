# Evolutionary Architecture 文獻彙整

**備份日期**: 2025-01-03
**來源**: ThoughtWorks, O'Reilly 等

---

## 1. ThoughtWorks Decoder

**標題**: Evolutionary Architecture
**原始 URL**: https://www.thoughtworks.com/insights/decoder/e/evolutionary-architecture

### 核心定義

> "Evolutionary architecture is an approach to building software that's designed to evolve over time as business priorities change, customer demands shift, and new technologies emerge."

該方法將敏捷實踐應用於軟體開發，創造更靈活且適應變化的系統。

### 主要特性

| 特性 | 說明 |
|------|------|
| **增量化變化** | 支持增量化變化，隨著需求和技術能力的演進而調整 |
| **避免僵化** | 避免傳統架構的僵化 |
| **探索創新** | 讓開發者能夠探索最新創新 |

### 商業價值

1. **快速適應業務優先級變化**
2. **降低開發和部署成本**
   > "significantly reducing development and deployment costs"
3. **使組織能夠採納新技術，保持競爭優勢**

### GitHub 案例

> "GitHub refactor a critical part of its IT infrastructure using evolutionary architecture principles, seamlessly deploying two simultaneous instances of the same system to compare and optimize results."

**做法**：
- 同時部署兩個實例版本
- 在生產環境比較行為與結果
- 逐步替換舊系統，而不是一次性大改

---

## 2. Microservices as EA

**標題**: Microservices as an Evolutionary Architecture
**原始 URL**: https://www.thoughtworks.com/insights/blog/microservices-evolutionary-architecture

### 微服務與演化架構的關係

微服務是「第一個後 DevOps 革命的架構風格」，完全擁抱持續交付的工程實踐。

> "Microservices meet this definition because of its strong bounded context principle"

**關鍵特點**：
- 通過將邏輯邊界物理分離
- 使得單個微服務可像「交換樂高積木」一樣被替換

### 實驗能力

演化架構為業務帶來的「超能力」之一是**實驗能力**。

> "Operationally inexpensive trivial change to applications allows common Continuous Delivery practices like A/B testing, Canary Releases"

這種能力使組織能進行**假設驅動開發 (Hypothesis-Driven Development)**，而非依賴猜測。

### 持續交付的關鍵角色

持續交付是演化架構的重要推動力。

> "continuous delivery is an important enabler for any evolutionary architecture"

它通過部署管道、自動化配置等實踐實現「bring the pain forward」原則，降低架構演進成本。

### 演化架構支援的實踐

| 實踐 | 說明 |
|------|------|
| **A/B Testing** | 同時運行兩個版本，比較效果 |
| **Canary Releases** | 金絲雀發布，逐步推廣 |
| **Feature Flags** | 功能開關，控制上線 |
| **Blue-Green Deployment** | 藍綠部署，無縫切換 |

---

## 3. Building Evolutionary Architectures

**標題**: Building Evolutionary Architectures: Support Constant Change
**作者**: Neal Ford, Rebecca Parsons, Patrick Kua
**出版**: O'Reilly Media
**原始 URL**: https://www.thoughtworks.com/insights/books/building-evolutionary-architectures

### 書籍概述

這是演化架構領域的經典參考書，系統整理了：
- Fitness Functions
- 實務案例
- 治理模式

### Fitness Functions

**定義**：自動化的品質與約束檢查機制

**目的**：
- 確保架構演進符合預期
- 自動驗證架構約束
- 持續監控品質指標

**類型**：

| 類型 | 範例 |
|------|------|
| **原子 Fitness Function** | 單一指標檢查（如：回應時間 < 200ms） |
| **整體 Fitness Function** | 系統級檢查（如：Netflix Chaos Monkey） |
| **觸發式** | CI/CD 管道中執行 |
| **持續式** | 生產環境監控 |

### Fitness Function 實例

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Fitness Functions 實例                           │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  效能類                                                             │
│  ├── 回應時間 < 200ms (P95)                                        │
│  ├── 吞吐量 > 1000 req/s                                           │
│  └── 記憶體使用 < 80%                                              │
│                                                                     │
│  可靠性類                                                           │
│  ├── 可用性 > 99.9%                                                │
│  ├── 錯誤率 < 0.1%                                                 │
│  └── 故障恢復時間 < 5 分鐘                                         │
│                                                                     │
│  架構類                                                             │
│  ├── 模組循環依賴 = 0                                              │
│  ├── API 向後相容                                                  │
│  └── 資料庫遷移可回滾                                              │
│                                                                     │
│  安全類                                                             │
│  ├── 無已知漏洞                                                    │
│  ├── 敏感資料加密                                                  │
│  └── 身份驗證通過率 100%                                           │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 4. GOTO Conference 演講

**標題**: Building Evolutionary Architectures
**原始 URL**: https://gotopia.tech/episodes/232/building-evolutionary-architectures

### 演講重點

討論怎麼把「演化計算 + Fitness Functions」概念應用到軟體治理，分享在多個客戶專案中的實驗經驗。

### 關鍵概念

1. **借鑑生物演化**
   - 自然選擇 → Fitness Functions
   - 突變 → 架構變更
   - 適應 → 持續演進

2. **架構治理**
   - 不是一次性決策
   - 是持續的演進過程
   - 需要自動化支援

---

## 5. Hypothesis-Driven Development

**標題**: How evolutionary architecture simplified hypothesis driven development
**原始 URL**: https://www.theserverside.com/feature/How-evolutionary-architecture-simplified-hypothesis-driven-development

### 案例研究

#### 德國汽車品牌案例

針對成熟的行動搜尋 App：
- 對不同功能組合做實驗
- 了解哪些功能組合真的對使用者有價值
- 透過可演化架構，快速開多個版本做 A/B 測試
- 根據結果前進或 rollback，不會牽連整個系統

#### Netflix Chaos Monkey

被拿來當作「整體性 Fitness Function」案例：
- 透過隨機關閉服務測試系統韌性
- 倒逼架構必須可恢復、可演化

### 假設驅動開發流程

```
1. 提出假設
   "如果我們加入功能 X，轉換率會提升 10%"

2. 設計實驗
   - 定義成功指標
   - 設計 A/B 測試

3. 快速實作
   - 使用 Feature Flag
   - 最小化變更範圍

4. 收集數據
   - 監控關鍵指標
   - 比較實驗組與對照組

5. 驗證或否定假設
   - 成功 → 全面推廣
   - 失敗 → 回滾，學習，下一個假設
```

---

## 6. 可演化架構的特徵

### 模組化

| 特徵 | 說明 |
|------|------|
| **清晰邊界** | 每個模組有明確的職責 |
| **鬆散耦合** | 模組間依賴最小化 |
| **獨立部署** | 單個模組可獨立發布 |
| **可替換** | 可用新實作替換舊實作 |

### 增量變更

| 原則 | 說明 |
|------|------|
| **小步快跑** | 每次變更範圍最小化 |
| **可回滾** | 每次變更都可以回滾 |
| **向後相容** | 新版本相容舊客戶端 |
| **功能開關** | 使用 Feature Flag 控制 |

### 自動化驗證

| 驗證類型 | 工具/方法 |
|----------|-----------|
| **單元測試** | pytest, JUnit |
| **整合測試** | API 測試, 端到端測試 |
| **架構測試** | ArchUnit, 依賴分析 |
| **效能測試** | 負載測試, 壓力測試 |
| **安全測試** | 漏洞掃描, 滲透測試 |

---

## 7. 名詞對照表

| 英文 | 繁體中文 | 說明 |
|------|----------|------|
| Evolutionary Architecture | 演化架構 | 可隨時間演進的架構 |
| Fitness Function | 適應度函數 | 自動化品質檢查機制 |
| Bounded Context | 限界上下文 | DDD 中的模組邊界概念 |
| Microservices | 微服務 | 細粒度的服務架構 |
| Continuous Delivery | 持續交付 | CD，自動化部署流程 |
| A/B Testing | A/B 測試 | 對比實驗 |
| Canary Release | 金絲雀發布 | 漸進式發布策略 |
| Feature Flag | 功能開關 | 動態控制功能啟用 |
| Blue-Green Deployment | 藍綠部署 | 雙環境切換策略 |
| Hypothesis-Driven | 假設驅動 | 基於假設的開發方式 |
| Rollback | 回滾 | 恢復到之前版本 |

---

## 8. 延伸閱讀

### 書籍

- 《Building Evolutionary Architectures》 - Neal Ford, Rebecca Parsons, Patrick Kua
- 《Domain-Driven Design》 - Eric Evans
- 《Continuous Delivery》 - Jez Humble, David Farley
- 《Release It!》 - Michael Nygard

### 線上資源

- ThoughtWorks Technology Radar
- Martin Fowler's Blog (martinfowler.com)
- InfoQ Architecture & Design

---

**備份日期**: 2025-01-03
**維護者**: Claude Code (Opus 4.5)
