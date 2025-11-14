# 考試頁面元素定位策略

> **文檔目的**: 記錄考試答題頁面的 DOM 結構和元素定位方法
> **分析日期**: 2025-01-14
> **分析來源**: `高齡客戶投保權益保障(114年度) - 郵政ｅ大學-exam/4郵政ｅ大學.html`

---

## 📊 考試頁面結構概覽

```
<div class="paper-content card">
  <div class="exam-subjects">
    <ol class="subjects-jit-display">
      <li class="subject"> ← 題目容器（重複）
        <div class="subject-head">
          <span class="subject-description"> ← 題目文字
        <div class="subject-body">
          <ol class="subject-options">
            <li class="option"> ← 選項容器（重複）
              <label>
                <input type="radio"> ← 單選按鈕
                <div class="option-content"> ← 選項文字
```

---

## 🎯 1. 定位所有題目

### HTML 結構

```html
<li class="subject ng-scope single_selection"
    ng-repeat="subject in subjects | orderBy: 'sort'"
    ng-class="subject.type"
    ng-controller="ExamContentController">
```

### 定位策略

| 方法 | 定位器 | 優先度 | 說明 |
|------|--------|--------|------|
| **CSS Selector** | `li.subject` | ⭐⭐⭐⭐⭐ | 最簡單可靠 |
| **XPath** | `//li[@class='subject']` | ⭐⭐⭐⭐ | 部分匹配（含其他 class） |
| **XPath (精確)** | `//li[contains(@class, 'subject')]` | ⭐⭐⭐⭐⭐ | 推薦使用 |

### Selenium 程式碼

```python
# 方法 1: 使用 CSS Selector（推薦）
questions = driver.find_elements(By.CSS_SELECTOR, "li.subject")

# 方法 2: 使用 XPath
questions = driver.find_elements(By.XPATH, "//li[contains(@class, 'subject')]")

# 獲取總題數
total_questions = len(questions)
print(f"總共有 {total_questions} 題")
```

---

## 📝 2. 定位題目文字（description）

### HTML 結構

```html
<span ng-compile-html="subject.displayedDescription || subject.description | sanitizeHtml"
      class="pre-wrap subject-description simditor-viewer mathjax-process"
      mathjax="">
    <p class="ng-scope">高齡客戶投保權益保障的主要對象是指幾歲以上的長者?</p>
</span>
```

### 定位策略

| 方法 | 定位器 | 優先度 | 說明 |
|------|--------|--------|------|
| **CSS Selector** | `.subject-description` | ⭐⭐⭐⭐⭐ | 簡單直接 |
| **XPath** | `.//span[@class='subject-description']` | ⭐⭐⭐⭐ | 相對於題目元素 |
| **XPath (包含)** | `.//span[contains(@class, 'subject-description')]` | ⭐⭐⭐⭐⭐ | 最穩定 |

### Selenium 程式碼

```python
# 針對每個題目元素
for question_elem in questions:
    # 方法 1: CSS Selector（推薦）
    desc_elem = question_elem.find_element(By.CSS_SELECTOR, ".subject-description")

    # 方法 2: XPath（更穩定）
    desc_elem = question_elem.find_element(By.XPATH, ".//span[contains(@class, 'subject-description')]")

    # 獲取題目文字（包含 HTML）
    question_html = desc_elem.get_attribute('innerHTML')

    # 獲取純文字
    question_text = desc_elem.text

    print(f"題目: {question_text}")
```

**注意事項**:
- 題目文字包含在 `<p>` 標籤內
- 使用 `.text` 屬性會自動去除 HTML 標籤
- 使用 `.get_attribute('innerHTML')` 可保留 HTML 結構

---

## ✅ 3. 定位所有選項（options）

### HTML 結構

```html
<ol class="subject-options">
    <li class="option ng-scope horizontal"
        ng-class="subject.settings.options_layout"
        ng-repeat="option in subject.options | orderBy: 'sort'"
        style="width: 25%;">
        <label ng-class="{'answered-option': option.id == subject.answeredOption}">
            <!-- 選項內容 -->
        </label>
    </li>
</ol>
```

### 定位策略

| 方法 | 定位器 | 優先度 | 說明 |
|------|--------|--------|------|
| **CSS Selector** | `.subject-options .option` | ⭐⭐⭐⭐⭐ | 推薦使用 |
| **XPath** | `.//ol[@class='subject-options']/li` | ⭐⭐⭐⭐ | 更精確 |
| **XPath (包含)** | `.//li[contains(@class, 'option')]` | ⭐⭐⭐⭐⭐ | 最穩定 |

### Selenium 程式碼

```python
# 針對每個題目元素
for question_elem in questions:
    # 方法 1: CSS Selector（推薦）
    options = question_elem.find_elements(By.CSS_SELECTOR, ".subject-options .option")

    # 方法 2: XPath（更穩定）
    options = question_elem.find_elements(By.XPATH, ".//li[contains(@class, 'option')]")

    print(f"選項數量: {len(options)}")
```

---

## 🔘 4. 定位單選按鈕（radio button）

### HTML 結構

```html
<input ng-if="subject.type=='single_selection' || subject.type=='true_or_false'"
       type="radio"
       ng-value="9823"
       ng-model="subject.answeredOption"
       ng-change="onChangeSubmission(subject)"
       class="ng-pristine ng-untouched ng-valid ng-scope ng-empty"
       name="240"
       value="9823">
```

### 定位策略

| 方法 | 定位器 | 優先度 | 說明 |
|------|--------|--------|------|
| **Type 屬性** | `input[type="radio"]` | ⭐⭐⭐⭐⭐ | 最簡單 |
| **XPath** | `.//input[@type='radio']` | ⭐⭐⭐⭐⭐ | 相對定位 |

### Selenium 程式碼

```python
# 針對每個選項元素
for option_elem in options:
    # 方法 1: CSS Selector
    radio_button = option_elem.find_element(By.CSS_SELECTOR, "input[type='radio']")

    # 方法 2: XPath
    radio_button = option_elem.find_element(By.XPATH, ".//input[@type='radio']")

    # 點擊選項（推薦使用 JavaScript）
    driver.execute_script("arguments[0].click();", radio_button)
```

**重要提示**:
- AngularJS 頁面建議使用 JavaScript 點擊
- 使用 `execute_script` 可避免元素被遮擋的問題

---

## 📄 5. 定位選項文字（option content）

### HTML 結構

```html
<div class="option-content">
    <span ng-compile-html="option.content | sanitizeHtml"
          class="pre-wrap simditor-viewer mathjax-process"
          mathjax="">
        <p class="ng-scope">60歲</p>
    </span>
</div>
```

### 定位策略

| 方法 | 定位器 | 優先度 | 說明 |
|------|--------|--------|------|
| **CSS Selector** | `.option-content` | ⭐⭐⭐⭐⭐ | 簡單直接 |
| **XPath** | `.//div[@class='option-content']` | ⭐⭐⭐⭐ | 精確匹配 |

### Selenium 程式碼

```python
# 針對每個選項元素
for idx, option_elem in enumerate(options):
    # 獲取選項文字
    option_content = option_elem.find_element(By.CSS_SELECTOR, ".option-content")
    option_text = option_content.text

    print(f"選項 {chr(65+idx)}: {option_text}")
```

---

## 🔢 6. 獲取總題數

### 方法總結

| 方法 | 程式碼 | 準確度 |
|------|--------|--------|
| **計算題目元素** | `len(driver.find_elements(By.CSS_SELECTOR, "li.subject"))` | ⭐⭐⭐⭐⭐ |
| **從頁面資訊** | 解析頁面上的 "第 X 題 / 共 N 題" | ⭐⭐⭐⭐ |

### Selenium 程式碼（推薦）

```python
def get_total_questions(driver):
    """獲取考試總題數"""
    questions = driver.find_elements(By.CSS_SELECTOR, "li.subject")
    total = len(questions)
    print(f"✅ 共 {total} 題")
    return total
```

---

## 🧪 完整測試腳本範例

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def test_exam_page_locators(driver):
    """測試考試頁面元素定位"""

    # 等待頁面載入
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, "li.subject"))
    )

    print("=" * 60)
    print("考試頁面元素定位測試")
    print("=" * 60)

    # 1. 獲取所有題目
    questions = driver.find_elements(By.CSS_SELECTOR, "li.subject")
    total_questions = len(questions)
    print(f"\n✅ 1. 總題數: {total_questions} 題\n")

    # 2. 遍歷每一題
    for idx, question_elem in enumerate(questions, 1):
        print(f"--- 第 {idx} 題 ---")

        # 2.1 獲取題目文字
        desc_elem = question_elem.find_element(
            By.XPATH, ".//span[contains(@class, 'subject-description')]"
        )
        question_text = desc_elem.text
        print(f"題目: {question_text[:50]}...")  # 只顯示前50字

        # 2.2 獲取所有選項
        options = question_elem.find_elements(
            By.XPATH, ".//li[contains(@class, 'option')]"
        )
        print(f"選項數: {len(options)}")

        # 2.3 遍歷每個選項
        for opt_idx, option_elem in enumerate(options):
            # 獲取選項文字
            option_content = option_elem.find_element(By.CSS_SELECTOR, ".option-content")
            option_text = option_content.text

            # 獲取單選按鈕
            try:
                radio_button = option_elem.find_element(By.CSS_SELECTOR, "input[type='radio']")
                print(f"  {chr(65+opt_idx)}. {option_text} [單選按鈕已定位 ✓]")
            except:
                print(f"  {chr(65+opt_idx)}. {option_text} [無單選按鈕]")

        print()  # 空行分隔

    print("=" * 60)
    print("✅ 測試完成！")
    print("=" * 60)
```

---

## 📌 關鍵發現總結

### ✅ 成功定位的元素

| 元素 | CSS Selector | XPath | 狀態 |
|------|--------------|-------|------|
| 題目容器 | `li.subject` | `//li[contains(@class, 'subject')]` | ✅ 可靠 |
| 題目文字 | `.subject-description` | `.//span[contains(@class, 'subject-description')]` | ✅ 可靠 |
| 選項容器 | `.subject-options .option` | `.//li[contains(@class, 'option')]` | ✅ 可靠 |
| 單選按鈕 | `input[type="radio"]` | `.//input[@type='radio']` | ✅ 可靠 |
| 選項文字 | `.option-content` | `.//div[@class='option-content']` | ✅ 可靠 |

### ⚠️ 注意事項

1. **AngularJS 頁面特性**
   - 使用 `ng-repeat` 動態生成元素
   - 建議等待元素載入完成再操作
   - 使用 JavaScript 點擊避免遮擋問題

2. **HTML 內容處理**
   - 題目和選項都包含 HTML 標籤（`<p>`）
   - 使用 `.text` 獲取純文字
   - 使用 `.get_attribute('innerHTML')` 獲取 HTML

3. **題型識別**
   - 單選題：`class="subject ... single_selection"`
   - 複選題：`class="subject ... multiple_selection"`
   - 可通過 `input` 類型判斷：`radio` vs `checkbox`

---

## 🚀 下一步行動

### Phase 1: 驗證定位策略
- [ ] 創建獨立測試腳本
- [ ] 在實際考試頁面運行測試
- [ ] 驗證所有元素都能正確定位

### Phase 2: 實作答題頁面類別
- [ ] 創建 `ExamAnswerPage` 類別
- [ ] 實作 `get_all_questions()` 方法
- [ ] 實作 `get_question_text()` 方法
- [ ] 實作 `get_options()` 方法
- [ ] 實作 `click_option()` 方法

### Phase 3: 整合自動答題流程
- [ ] 整合題庫查詢服務
- [ ] 實作答案匹配邏輯
- [ ] 測試完整流程

---

**文檔版本**: 1.0
**維護者**: wizard03
**最後更新**: 2025-01-14
