# CAPTCHA OCR 技術指南

> 最後更新: 2025-12-29
> 研究目錄: `research/captcha_ocr_analysis/`
> 測試樣本: 420 張 TronClass CAPTCHA

---

## 快速開始

```python
# 推薦: 優化版 - 97.6% 準確率
from research.captcha_ocr_analysis.optimized_ocr import recognize_with_fallback
success, result, confidence = recognize_with_fallback('captcha.png')

# 備選: 單一策略 - 75.7% 準確率 (較快)
from research.captcha_ocr_analysis.captcha_profiles import recognize_with_profile
success, result, confidence = recognize_with_profile('captcha.png', 'tronclass')
```

---

## 1. 研究成果總覽

### 1.1 方法比較 (420 樣本測試)

| 方法 | 成功率 | 高精度(4位) | 執行時間 | 說明 |
|------|--------|------------|---------|------|
| **Optimized** | **97.6%** | 68.1% | 608ms | **推薦** 多策略 |
| v3_islands | 75.7% | 52.1% | 129ms | 單一策略基準 |
| v8_twostage | 75.5% | 50.5% | ~130ms | 連接噪點 |
| v7_multidim | 71.2% | 44.3% | ~130ms | 線條噪點 |
| v1_original | 34.8% | 19.3% | ~120ms | Auto-WFH 原始 |

### 1.2 優化提升

```
原始方法 (Auto-WFH):  34.8%
單一策略 (v3_islands): 75.7%  (+40.9%)
多策略優化:           97.6%  (+21.9%)
────────────────────────────────────
總提升:               +62.8%
```

### 1.3 執行時間基準 (50 樣本平均)

| 方法 | 每張耗時 | 相對速度 |
|------|---------|---------|
| v3_islands | 129ms | 1.0x (基準) |
| Optimized | 608ms | 4.7x 較慢 |

---

## 2. 技術架構

### 2.1 Optimized 多策略方法

```python
strategies = [
    (preprocess_v3, min_size=40, psm=7),    # 標準
    (preprocess_v3, min_size=35, psm=7),    # 較小閾值
    (preprocess_v3, min_size=30, psm=7),    # 更小閾值
    (preprocess_v3, min_size=40, psm=8),    # 單字模式
    (preprocess_v3, min_size=40, psm=13),   # 原始行模式
    (preprocess_clahe, min_size=40, psm=7), # CLAHE 增強
    (preprocess_clahe, min_size=35, psm=7),
    (preprocess_adaptive, min_size=30, psm=7), # 自適應閾值
    (preprocess_sharpen, min_size=40, psm=7),  # 銳化
]

# 評分機制
def score_result(result):
    if len(result) == 4 and result.isdigit(): return 100  # 完美
    if len(result) == 3 and result.isdigit(): return 50   # 可接受
    return len(result) * 10  # 部分識別
```

### 2.2 v3_islands 單一策略

```python
def preprocess_v3_islands(image, min_size=40):
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    blurred = cv.medianBlur(gray, 3)
    _, binary = cv.threshold(blurred, 0, 255,
                             cv.THRESH_BINARY_INV | cv.THRESH_OTSU)
    cleaned = remove_noise_by_area(binary, min_size)
    cleaned = cv.medianBlur(cleaned, 3)
    cv.bitwise_not(cleaned, cleaned)
    return cleaned

def remove_noise_by_area(binary_img, min_size=40):
    num_labels, labels, stats, _ = cv.connectedComponentsWithStats(
        binary_img, connectivity=8)
    output = np.zeros_like(binary_img)
    for i in range(1, num_labels):
        if stats[i, cv.CC_STAT_AREA] >= min_size:
            output[labels == i] = 255
    return output
```

### 2.3 處理流程

```
原圖 → 灰階 → 模糊 → 二值化(Otsu) → Connected Components → OCR
                 ↓
           [多策略版本]
                 ↓
    ┌─ CLAHE 增強 ──┐
    ├─ 自適應閾值 ──┼→ 多種 min_size → 多種 PSM → 取最佳
    └─ 銳化處理 ───┘
```

---

## 3. 失敗案例分析

### 3.1 失敗類型分布 (v3_islands)

| 類型 | 數量 | 比例 | 說明 |
|------|------|------|------|
| 識別 2 位 | 47 | 46% | 丟失 2 個數字 |
| 完全空白 | 30 | 29% | 無法識別 |
| 識別 1 位 | 25 | 25% | 丟失 3 個數字 |

### 3.2 失敗特徵對比

| 指標 | 成功樣本 | 失敗樣本 | 差異 |
|------|---------|---------|------|
| 平均亮度 | 154.7 | 160.2 | +3.5% |
| 元件數量 | 3.94 | 4.27 | +8.4% |
| 總面積 | 1574 | 1450 | -7.9% |
| 對比度 | 255 | 255 | 0% |

**結論**: 失敗案例多為數字被過度過濾，而非對比度問題。

---

## 4. Profile 系統

### 4.1 可用 Profile

| Profile | 方法 | 用途 |
|---------|------|------|
| tronclass | islands | TronClass (郵政 elearn) 預設 |
| tronclass_strict | islands | 嚴格過濾 |
| line_noise | multidim | 線條/刮痕噪點 |
| connected_noise | twostage | 連接型噪點 |
| hybrid_standard | hybrid | 混合模式 |
| digits_only | islands | 純數字 |
| alphanumeric | multidim | 英數混合 |

### 4.2 選擇指南

```
CAPTCHA 類型        → 推薦 Profile
─────────────────────────────────
隨機小點            → tronclass
斜線/橫線           → line_noise
噪點連到字          → connected_noise
複雜混合            → hybrid_standard
需最高準確率        → optimized_ocr
```

---

## 5. 參數調優

### 5.1 Grid Search 結果

| 參數 | 測試值 | 最佳值 | 說明 |
|------|--------|--------|------|
| min_size | 25-55 | 40 | 面積閾值 |
| blur_before | 0,3,5 | 3 | 前置模糊 |
| blur_after | 0,3 | 3 | 後置模糊 |

### 5.2 調優腳本

```bash
# 快速調優 (100 樣本 + 驗證)
conda run -n eebot python fast_tune.py

# 效能基準測試
conda run -n eebot python benchmark.py
```

---

## 6. 整合到 EEBot

### 6.1 建議整合方式

```python
# src/utils/captcha_ocr.py

from research.captcha_ocr_analysis.optimized_ocr import recognize_with_fallback

def solve_captcha(image_path: str) -> str:
    """
    自動識別 CAPTCHA

    Returns:
        識別結果 (4位數字) 或 None
    """
    success, result, confidence = recognize_with_fallback(image_path)

    if success and confidence in ('high', 'medium'):
        return result
    return None
```

### 6.2 登入流程整合

```python
# src/pages/login_page.py

from src.utils.captcha_ocr import solve_captcha

def fill_captcha(self):
    # 儲存驗證碼圖片
    captcha_path = 'captcha.png'
    self.save_captcha_image(captcha_path)

    # 自動識別
    result = solve_captcha(captcha_path)

    if result:
        self.captcha_input.send_keys(result)
    else:
        # 回退到手動輸入
        result = input("請輸入驗證碼: ")
        self.captcha_input.send_keys(result)
```

### 6.3 依賴套件

```bash
# 已在 eebot 環境安裝
conda activate eebot
pip install opencv-python pillow pytesseract
conda install -c conda-forge tesseract
```

---

## 7. 檔案結構

```
research/captcha_ocr_analysis/
├── optimized_ocr.py        # 多策略優化版 (97.6%)
├── captcha_profiles.py     # Profile 系統 (75.7%)
├── improved_ocr.py         # 9種預處理方法
├── analyze_failures.py     # 失敗案例分析
├── technique_analysis.py   # 技術對比分析
├── benchmark.py            # 效能基準測試
├── fast_tune.py            # 快速參數調優
├── auto_collect_captcha.py # 樣本收集腳本
├── samples/                # 420張 CAPTCHA 樣本
└── failed_samples/         # 失敗案例 (含處理後圖片)
```

---

## 8. 下階段計畫

### 8.1 P0 優先: 整合到 EEBot

> 詳見 `docs/CLAUDE_CODE_HANDOVER-8.md` 及 `docs/TODO.md`

| # | 任務 | 預期產出 |
|---|------|---------|
| 1 | 建立 `src/utils/captcha_ocr.py` | 封裝 OCR 函數 |
| 2 | 修改 `src/pages/login_page.py` | 自動識別 + 手動回退 |
| 3 | 測試完整登入流程 | 確認端到端運作 |

### 8.2 可選優化

- [ ] 收集更多樣本驗證穩定性
- [ ] 針對失敗案例特調參數
- [ ] 考慮輕量 CNN 模型 (需 GPU)

---

## 9. 參考資源

- [PyImageSearch - Connected Components](https://pyimagesearch.com/2021/02/22/opencv-connected-component-labeling-and-analysis/)
- [Simple-Captcha-Breaker Tutorial](https://cagriuysal.github.io/Simple-Captcha-Breaker/)
- [kingsman142/captcha-solver](https://github.com/kingsman142/captcha-solver)
- [Auto-WFH (原始參考)](https://github.com/dec880126/Auto-WFH)
