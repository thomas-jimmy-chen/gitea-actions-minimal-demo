# EEBot - AI Assistant Handover Guide

> **Universal AI Programming Assistant Documentation**
>
> Compatible with: Claude Code CLI, Cursor, GitHub Copilot CLI, Cody, Tabnine, and all AI-powered code assistants

**Document Version**: 1.1
**Last Updated**: 2025-11-15
**Project Version**: 2.0.2+auto-answer.1
**Project Codename**: **Gleipnir** (格萊普尼爾 / 縛狼鎖)
**Maintainer**: wizard03

---

## 🔗 Project Codename: Gleipnir

> **Gleipnir** (格萊普尼爾) - The mythical chain from Norse mythology

In Norse mythology, **Gleipnir** is the binding that holds the mighty wolf **Fenrir**. Crafted by dwarves from impossible materials, this chain appears deceptively light and silky but possesses unbreakable strength.

**Meaning**: "Open One" / "Deceiver" / "Entangler"
**Chinese**: 格萊普尼爾 / 縛狼鎖 / 荒謬之鎖

**Why Gleipnir for This Project?**
- Just as Gleipnir binds Fenrir, this automation tool "binds" and controls the complex e-learning workflow
- The chain's deceptive simplicity mirrors our clean API hiding complex automation
- The unbreakable nature symbolizes reliable, consistent automation
- "Entangler" reflects how we weave together multiple systems (Selenium + MitmProxy + Question Banks)

---

## 🎯 Quick Project Overview

### What is EEBot?

**EEBot** (Elearn Automation Bot) - **Codename: Gleipnir** - is a **Selenium-based automation tool** designed specifically for Taiwan Post's e-Learning platform (郵政e大學). It automates the process of completing online courses and exams with intelligent question-answering capabilities.

### Key Information

| Attribute | Value |
|-----------|-------|
| **Project Type** | Web Automation Bot |
| **Primary Language** | Python 3.x |
| **Core Framework** | Selenium WebDriver + MitmProxy |
| **Target Website** | https://elearn.post.gov.tw |
| **Architecture** | POM (Page Object Model) + API Interceptor |
| **Latest Feature** | Exam flow support (2025-01-13) |

### Core Functionality

1. ✅ **Auto Login**: Cookie-based or credential-based authentication
2. ✅ **Course Automation**: Navigate and complete learning courses
3. ✅ **Exam Automation**: Handle exam confirmation flows (NEW ✨)
4. ✅ **Duration Spoofing**: Use MitmProxy to modify visit duration
5. ✅ **Interactive Scheduling**: Menu-based course/exam selection

---

## 📁 Project Structure (Tree View)

```
D:\Dev\eebot\
│
├── 📄 main.py                      # Main entry point
├── 📄 menu.py                      # Interactive course scheduler
│
├── 📂 src/                         # Source code
│   ├── 📂 core/                    # Core infrastructure
│   │   ├── config_loader.py        # Load config from eebot.cfg
│   │   ├── driver_manager.py       # Manage Selenium WebDriver lifecycle
│   │   ├── cookie_manager.py       # Handle login cookies
│   │   └── proxy_manager.py        # Manage MitmProxy server
│   │
│   ├── 📂 pages/                   # Page Object Model (POM)
│   │   ├── base_page.py            # Base class for all pages
│   │   ├── login_page.py           # Login page operations
│   │   ├── course_list_page.py     # Course list page (DO NOT MODIFY)
│   │   ├── course_detail_page.py   # Course detail page (DO NOT MODIFY)
│   │   └── exam_detail_page.py     # Exam detail page (NEW ✨)
│   │
│   ├── 📂 scenarios/               # Business flow orchestration
│   │   ├── course_learning.py      # Course learning flow (DO NOT MODIFY)
│   │   └── exam_learning.py        # Exam flow (NEW ✨)
│   │
│   ├── 📂 api/
│   │   └── 📂 interceptors/
│   │       └── visit_duration.py   # HTTP request interceptor
│   │
│   └── 📂 utils/
│       └── stealth_extractor.py    # Anti-detection utilities
│
├── 📂 data/                        # Data files
│   ├── courses.json                # Course configuration (IMPORTANT!)
│   └── schedule.json               # Scheduled courses (auto-generated)
│
├── 📂 config/                      # Configuration
│   └── eebot.cfg                   # System configuration
│
├── 📂 docs/                        # Documentation
│   ├── AI_ASSISTANT_GUIDE.md       # This file
│   ├── CLAUDE_CODE_HANDOVER.md     # Claude Code specific guide
│   └── CHANGELOG.md                # Change log
│
└── 📂 高齡客戶投保權益保障(114年度) - 郵政ｅ大學-exam/
    ├── 高齡測驗.txt                # Exam flow reference
    └── *.html                      # HTML snapshots for analysis
```

---

## 🏗️ Architecture Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                         User Interaction                        │
│                                                                 │
│  python menu.py  ────┐                                         │
│  python main.py  ────┼──────────────────────────────────────┐  │
└─────────────────────┬┘                                        │  │
                      │                                         │  │
┌─────────────────────▼─────────────────────────────────────────▼──┤
│                          Entry Layer                              │
│  ┌──────────────┐          ┌────────────────────────────────┐   │
│  │   menu.py    │          │          main.py               │   │
│  │              │          │  - Load configuration          │   │
│  │ - Display    │          │  - Start MitmProxy (optional)  │   │
│  │   courses    │          │  - Separate courses & exams    │   │
│  │ - Schedule   │          │  - Execute scenarios           │   │
│  │   selection  │          └────────────────────────────────┘   │
│  └──────────────┘                                                │
└───────────────────────────────────┬──────────────────────────────┘
                                    │
┌───────────────────────────────────▼──────────────────────────────┐
│                       Scenarios Layer                             │
│  ┌─────────────────────────────┐  ┌───────────────────────────┐ │
│  │  CourseLearningScenario     │  │  ExamLearningScenario ✨  │ │
│  │  (DO NOT MODIFY)            │  │  (NEW: 2025-01-13)        │ │
│  │                             │  │                           │ │
│  │  Flow:                      │  │  Flow:                    │ │
│  │  1. Login                   │  │  1. Login                 │ │
│  │  2. Select program          │  │  2. Select program        │ │
│  │  3. Select lesson           │  │  3. Click exam            │ │
│  │  4. Go back                 │  │  4. Click continue        │ │
│  │                             │  │  5. Check agreement       │ │
│  │                             │  │  6. Confirm               │ │
│  └─────────────────────────────┘  └───────────────────────────┘ │
└───────────────────────────────────┬──────────────────────────────┘
                                    │
┌───────────────────────────────────▼──────────────────────────────┐
│                         Pages Layer (POM)                         │
│  ┌──────────────┐  ┌─────────────────┐  ┌───────────────────┐  │
│  │  LoginPage   │  │ CourseListPage  │  │ CourseDetailPage  │  │
│  │              │  │ (DO NOT MODIFY) │  │ (DO NOT MODIFY)   │  │
│  └──────────────┘  └─────────────────┘  └───────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  ExamDetailPage (NEW ✨)                                 │   │
│  │  - click_exam_by_name()                                  │   │
│  │  - click_continue_exam_button()                          │   │
│  │  - check_agreement_checkbox()                            │   │
│  │  - click_popup_continue_button()                         │   │
│  │  - complete_exam_flow() [Convenience method]            │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────────────────┬──────────────────────────────┘
                                    │
┌───────────────────────────────────▼──────────────────────────────┐
│                          Core Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │ ConfigLoader │  │ DriverManager│  │  CookieManager      │   │
│  │              │  │              │  │                     │   │
│  │ Load .cfg    │  │ Selenium     │  │  Login cookies      │   │
│  │ settings     │  │ WebDriver    │  │                     │   │
│  └──────────────┘  └──────────────┘  └─────────────────────┘   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  ProxyManager + VisitDurationInterceptor                 │   │
│  │  - Start/stop MitmProxy                                  │   │
│  │  - Intercept HTTP requests                               │   │
│  │  - Modify visit_duration parameter (+9000 seconds)       │   │
│  └──────────────────────────────────────────────────────────┘   │
└───────────────────────────────────────────────────────────────────┘
```

---

## 📝 Core Configuration: courses.json

This is the **most important file** in the project. It defines all courses and exams that can be automated.

### Location
```
D:\Dev\eebot\data\courses.json
```

### Structure

#### Course Type (Regular Learning)
```json
{
  "program_name": "課程計畫名稱",
  "lesson_name": "課程名稱",
  "course_id": 369,
  "delay": 7.0,
  "description": "課程描述"
}
```

**Field Descriptions**:
- `program_name`: Course program name (must match link text on website)
- `lesson_name`: Lesson name (must match link text)
- `course_id`: Unique ID used in back navigation XPath
- `delay`: Wait time in seconds before clicking (**MUST be 7.0 - unified standard**)
- `description`: Optional description for documentation

**⚠️ IMPORTANT RULE**: All courses (regular and exams) **MUST** use `"delay": 7.0`. This is a mandatory standard.

#### Exam Type (NEW ✨ 2025-01-13)
```json
{
  "program_name": "課程計畫名稱",
  "exam_name": "考試名稱",
  "course_type": "exam",
  "delay": 7.0,
  "description": "考試描述"
}
```

**Key Differences**:
- Uses `exam_name` instead of `lesson_name`
- Has `course_type: "exam"` marker
- No `course_id` (exam flow doesn't use it)
- Same `delay` (7.0s) as regular courses (unified standard)

### Example Configuration
```json
{
  "description": "課程資料配置檔",
  "version": "1.0",
  "courses": [
    {
      "program_name": "資通安全學程課程(114年度)",
      "lesson_name": "個資保護認知宣導與案例分享教育訓練",
      "course_id": 365,
      "delay": 7.0,
      "description": "資通安全與個資保護課程"
    },
    {
      "program_name": "高齡客戶投保權益保障(114年度)",
      "exam_name": "高齡測驗(100分及格)",
      "course_type": "exam",
      "delay": 7.0,
      "description": "高齡客戶投保權益保障考試流程"
    }
  ]
}
```

---

## 🔧 How It Works

### Workflow Overview

```
┌─────────────┐
│   START     │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────┐
│  1. Load Configuration      │
│     (config/eebot.cfg)      │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  2. Extract Stealth JS      │
│     (Anti-detection)        │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  3. Start MitmProxy         │
│     (If modify_visits=y)    │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  4. Load schedule.json      │
│     (Courses to execute)    │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  5. Separate Courses/Exams  │
│     - Regular courses       │
│     - Exam courses          │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────────────────────┐
│  6. Execute Scenarios       │
│     6.1 Course Scenario     │
│     6.2 Exam Scenario       │
└──────┬──────────────────────┘
       │
       ▼
┌─────────────┐
│     END     │
└─────────────┘
```

### Detailed Execution Flow

#### For Regular Courses
```
Login → My Courses → Select Program → Select Lesson
  → Wait (MitmProxy modifies duration) → Go Back → Next Course
```

#### For Exams (NEW ✨)
```
Login → My Courses → Select Program → Click Exam Name
  → Click "繼續答題" → Check Agreement Checkbox
  → Click Popup "繼續答題" → Reach Exam Page
```

### MitmProxy Mechanism

**Purpose**: Modify HTTP requests to fake longer visit durations.

**How it works**:
1. Selenium navigates to course pages
2. MitmProxy intercepts HTTP requests
3. `VisitDurationInterceptor` finds visit_duration parameters
4. Adds 9000 seconds to the duration
5. Server thinks user watched for 2.5+ hours

**Configuration**: Set `modify_visits=y` in `config/eebot.cfg`

---

## 🚀 Usage Guide

### Step 1: Configure System

Edit `config/eebot.cfg`:
```ini
[SETTINGS]
target_http=https://elearn.post.gov.tw
execute_file=D:/chromedriver.exe
user_name=your_username
password=your_password
modify_visits=y                    # Enable MitmProxy
silent_mitm=y                      # Silent mode
keep_browser_on_error=n            # Close browser on error
```

### Step 2: Add Courses/Exams

Edit `data/courses.json` and add your course or exam configuration (see format above).

### Step 3: Schedule Courses

Run the interactive menu:
```bash
python menu.py
```

**Menu Options**:
- **Number (1-N)**: Select course/exam to add to schedule
- **v**: View current schedule
- **c**: Clear schedule
- **s**: Save schedule to `data/schedule.json`
- **r**: Run schedule (executes `main.py`)
- **q**: Quit

### Step 4: Execute Schedule

```bash
python main.py
```

The program will:
1. Load configuration
2. Start MitmProxy (if enabled)
3. Execute all scheduled courses
4. Execute all scheduled exams
5. Close browser and cleanup

---

## 📖 Code Examples

### Example 1: Add a New Page Object

```python
# File: src/pages/my_new_page.py

from .base_page import BasePage
from selenium.webdriver.common.by import By

class MyNewPage(BasePage):
    """My new page operations"""

    # Define locators
    SUBMIT_BUTTON = (By.XPATH, "//button[@id='submit']")

    def click_submit(self, delay: float = 7.0):
        """Click submit button"""
        import time
        time.sleep(delay)

        self.click(self.SUBMIT_BUTTON)
        print('[SUCCESS] Clicked submit button')
```

### Example 2: Add a New Scenario

```python
# File: src/scenarios/my_new_scenario.py

from ..core.config_loader import ConfigLoader
from ..core.driver_manager import DriverManager
from ..pages.my_new_page import MyNewPage

class MyNewScenario:
    """My new business flow"""

    def __init__(self, config: ConfigLoader):
        self.config = config
        self.driver_manager = DriverManager(config)
        driver = self.driver_manager.create_driver()
        self.my_page = MyNewPage(driver)

    def execute(self, items):
        """Execute the scenario"""
        try:
            for item in items:
                self._process_item(item)
        finally:
            self.driver_manager.quit()

    def _process_item(self, item):
        """Process a single item"""
        self.my_page.click_submit(delay=item.get('delay', 7.0))
```

### Example 3: Using Base Page Methods

```python
# Inside any Page class

# Find element with automatic wait
element = self.find_element((By.ID, "my-element"))

# Click with auto-retry (uses JS if blocked)
self.click((By.XPATH, "//button[@type='submit']"))

# Input text
self.input_text((By.NAME, "username"), "myusername")

# Get text
text = self.get_text((By.CLASS_NAME, "status"))

# Check if element exists
if self.is_element_present((By.ID, "error-message")):
    print("Error occurred!")

# Scroll to element
self.scroll_to_element((By.ID, "bottom-section"))

# Execute JavaScript
self.execute_script("window.scrollTo(0, document.body.scrollHeight);")
```

---

## 📋 Common Tasks & How-To

### Task 1: Add a New Regular Course

#### Step 1: Get course information from website
- Login to https://elearn.post.gov.tw
- Navigate to the course
- Find the course ID in HTML: `ng-click='goBackCourse(XXX)'`

#### Step 2: Edit courses.json
```json
{
  "program_name": "New Course Program",
  "lesson_name": "New Course Lesson",
  "course_id": 999,
  "delay": 7.0,
  "description": "Description of the course"
}
```

#### Step 3: Schedule and run
```bash
python menu.py  # Select the course
python main.py  # Execute
```

**No code changes needed!**

---

### Task 2: Add a New Exam

#### Step 1: Analyze the exam flow
- Manually go through the exam process
- Note down all button clicks and confirmations
- Save HTML snapshots for reference

#### Step 2: Edit courses.json
```json
{
  "program_name": "Exam Program Name",
  "exam_name": "Exam Name",
  "course_type": "exam",
  "delay": 7.0,
  "description": "Exam description"
}
```

#### Step 3: (If flow is different) Modify exam_detail_page.py
```python
def my_custom_exam_step(self, delay: float = 7.0):
    """Custom step for this exam"""
    # Your custom logic here
    pass
```

#### Step 4: Schedule and run
```bash
python menu.py
python main.py
```

---

### Task 3: Modify Exam Flow

If the exam confirmation flow changes:

#### Edit: src/pages/exam_detail_page.py
```python
def check_agreement_checkbox(self, delay: float = 10.0):
    """Modify this method if checkbox location changes"""
    # Update XPath or locator strategy
    NEW_CHECKBOX = (By.XPATH, "//input[@new-ng-model='newModel']")
    element = self.find_element(NEW_CHECKBOX)
    self.driver.execute_script("arguments[0].click();", element)
```

#### Edit: src/scenarios/exam_learning.py
```python
def _process_exam(self, exam: Dict[str, any]):
    """Add or remove steps as needed"""
    # Add new step
    self.exam_detail.my_new_step(delay=delay)
```

---

### Task 4: Adjust Delays

If pages load slowly, increase delay times:

#### Global delay (for all)
Edit `data/courses.json`:
```json
{
  "delay": 15.0  // Increase from 7.0 to 15.0
}
```

#### Per-method delay
In page classes:
```python
def click_something(self, delay: float = 15.0):  # Increase default
    time.sleep(delay)
    self.click(locator)
```

---

### Task 5: Debug with Browser Kept Open

Edit `config/eebot.cfg`:
```ini
keep_browser_on_error=y
```

Now when an error occurs, the browser will stay open for inspection.

---

## 🚫 DO NOT MODIFY - Protected Files

The following files are **core system files** and should **NOT be modified** unless absolutely necessary:

### ❌ Scenarios Layer
- `src/scenarios/course_learning.py` - Original course flow (stable & tested)

### ❌ Pages Layer (Original)
- `src/pages/base_page.py` - Base class (all pages depend on it)
- `src/pages/login_page.py` - Login logic
- `src/pages/course_list_page.py` - Course list operations
- `src/pages/course_detail_page.py` - Course detail operations

### ❌ Core Infrastructure
- `src/core/config_loader.py` - Configuration loading
- `src/core/driver_manager.py` - WebDriver lifecycle
- `src/core/cookie_manager.py` - Cookie handling
- `src/core/proxy_manager.py` - MitmProxy management

### ❌ API Layer
- `src/api/interceptors/visit_duration.py` - HTTP interception logic

### ❌ Configuration
- `config/eebot.cfg` - System settings
- Existing entries in `data/courses.json` - Original courses

### ✅ SAFE TO MODIFY
- `src/pages/exam_detail_page.py` - Exam page (created 2025-01-13)
- `src/scenarios/exam_learning.py` - Exam scenario (created 2025-01-13)
- `menu.py` - Display logic
- `main.py` - Entry point (with caution)
- **New entries** in `data/courses.json`

---

## 🔍 Quick File Locator

| Task | File Path | Purpose |
|------|-----------|---------|
| Add course/exam | `data/courses.json` | Define courses and exams |
| Configure system | `config/eebot.cfg` | System settings |
| View schedule | `data/schedule.json` | Scheduled courses |
| Entry point | `main.py` | Program entry |
| Interactive menu | `menu.py` | Schedule management |
| Course flow | `src/scenarios/course_learning.py` | Course automation (DO NOT MODIFY) |
| Exam flow | `src/scenarios/exam_learning.py` | Exam automation (NEW ✨) |
| Exam page ops | `src/pages/exam_detail_page.py` | Exam page interactions (NEW ✨) |
| Base page class | `src/pages/base_page.py` | Common page methods |
| Configuration | `src/core/config_loader.py` | Config loading |
| WebDriver | `src/core/driver_manager.py` | Browser management |
| Proxy | `src/core/proxy_manager.py` | MitmProxy control |
| Visit duration | `src/api/interceptors/visit_duration.py` | Duration spoofing |
| Change log | `docs/CHANGELOG.md` | Modification history |

---

## 📅 Modification History

### 2025-01-13: Exam Flow Support (v2.0.1+exam)

**Added**:
- `src/pages/exam_detail_page.py` - Exam page operations
- `src/scenarios/exam_learning.py` - Exam flow scenario
- Exam type support in `data/courses.json`
- Documentation files (this file, CHANGELOG.md, CLAUDE_CODE_HANDOVER.md)

**Modified**:
- `menu.py` - Display exam type with `[考試]` marker
- `main.py` - Separate and execute courses/exams

**Not Modified**:
- All existing course flow logic
- All core infrastructure files
- All existing course configurations

See `docs/CHANGELOG.md` for detailed changes.

---

## 🛠️ Development Guidelines

### Code Style
- Follow existing code patterns
- Use meaningful variable names
- Add docstrings to all methods
- Add `# Created: YYYY-MM-DD` to new files

### Testing Strategy
1. Test in isolation first (single course/exam)
2. Test mixed scenarios (courses + exams)
3. Test with `modify_visits=n` and `modify_visits=y`
4. Test error scenarios (wrong course names, timeouts)

### Documentation Requirements
When making changes:
1. Update `docs/CHANGELOG.md` with changes
2. Update this file if architecture changes
3. Add inline comments for complex logic
4. Update code examples if APIs change

### Git Commit Messages
```
[type] Brief description

- Detailed change 1
- Detailed change 2

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`

---

## 🐛 Troubleshooting

### Issue 1: Element Not Found

**Symptoms**: `NoSuchElementException` or timeout errors

**Possible Causes**:
- XPath changed on website
- Page not fully loaded
- Element hidden or disabled

**Solutions**:
1. Increase `delay` in courses.json
2. Check XPath in browser DevTools
3. Use `wait_for_element_visible()` instead of direct `click()`
4. Try alternative locators (ID, CLASS_NAME instead of XPATH)

### Issue 2: MitmProxy Won't Start

**Symptoms**: Port already in use, permission denied

**Solutions**:
1. Change `listen_port` in `config/eebot.cfg` (try 8081, 8082)
2. Kill existing MitmProxy processes
3. Run with administrator privileges
4. Disable MitmProxy: Set `modify_visits=n`

### Issue 3: Browser Closes Immediately

**Symptoms**: Browser opens and closes without executing

**Solutions**:
1. Check `data/schedule.json` is not empty
2. Run `python menu.py` first to schedule courses
3. Check for Python errors in console
4. Enable `keep_browser_on_error=y` for debugging

### Issue 4: Exam Continue Button Not Found (Fixed 2025-01-13)

**Symptoms**: Error at Step 2 - `Element not found` when clicking exam "繼續答題" button

**Root Cause**: XPath locator was too strict (exact match required)

**Solution** (Already implemented):
- `exam_detail_page.py` now uses 4 fallback strategies
- Strategy 1: Text content matching
- Strategy 2: Partial ng-click matching
- Strategy 3: Span text with parent navigation
- Strategy 4: Container-based location

**If still failing**:
1. Check browser DevTools for actual button HTML
2. Verify button text is "繼續答題" or "開始答題"
3. Increase delay to 15 seconds

### Issue 5: Popup Continue Button Not Clickable (Fixed 2025-01-13)

**Symptoms**: Error at Step 4 - `Element not clickable` in confirmation popup

**Root Cause**:
- Button is disabled until checkbox is checked
- AngularJS needs time to update button state
- Button may be obscured by other elements

**Solution** (Already implemented):
- `click_popup_continue_button()` now uses 5 strategies
- Checks for `disabled` attribute and waits up to 5 seconds
- Uses JavaScript click to bypass obstruction checks
- Priority strategy: `//*[@id='start-exam-confirmation-popup']/div/div/div[3]/div/button[1]`

**If still failing**:
1. Increase delay between checkbox and button click
2. Check if popup ID changed (should be `start-exam-confirmation-popup`)
3. Verify only one green button exists in popup footer

### Issue 6: Exam Checkbox Won't Check

**Symptoms**: Checkbox click fails or button stays disabled

**Solutions**:
1. Increase delay in `check_agreement_checkbox()`
2. Verify checkbox XPath is correct
3. Try clicking checkbox label instead of input
4. Use JavaScript click: `execute_script("arguments[0].click()", element)`

### Issue 7: Mixed Course/Exam Order

**Symptoms**: Courses and exams don't execute in scheduled order

**Expected Behavior**: This is by design. Courses execute first, then exams.

**Reason**: Each type uses a separate Scenario to avoid browser restarts.

**Workaround**: Run courses and exams in separate batches if order matters.

---

## 💡 Tips for AI Assistants

### For Claude Code CLI
- Use `@workspace` to index the project
- Reference files with full paths
- Check `docs/CLAUDE_CODE_HANDOVER.md` for Claude-specific tips

### For Cursor
- Use "Ctrl+K" to chat about specific files
- Use "Ctrl+L" for project-wide queries
- Index `docs/` folder for context

### For GitHub Copilot CLI
- Use `gh copilot explain` for code understanding
- Use `gh copilot suggest` for command suggestions

### For Cody
- Use `@file` to reference specific files
- Use `@project` for project-wide context

### General Tips
1. **Always read CHANGELOG.md first** before making changes
2. **Check the protected files list** before editing
3. **Test incrementally** - don't change multiple files at once
4. **Follow existing patterns** - maintain code consistency
5. **Document as you go** - update CHANGELOG.md immediately

---

## 🎯 Implemented Features: Auto-Answer System (Phase 2)

> **Status**: ✅ **IMPLEMENTED** (Completed 2025-11-15)
> **Version**: 2.0.2+auto-answer
> **Implementation By**: wizard03 (with Claude Code CLI)
> **Current State**: Fully functional auto-answering system with intelligent matching

### Overview

The auto-answer system will enable automated question answering during exams by matching questions from the exam page with answers from a pre-loaded question bank.

### Question Bank Data

**Location**: `郵政E大學114年題庫/` (Question Bank Directory)

**Data Statistics**:
- Total Questions: **1,766**
- Total Size: **5.3 MB**
- Categories: **23 topic categories**
- Format: **JSON files**
- Database: `總題庫.json` (Master question bank)

**Sample Categories**:
```
窗口線上測驗（390題）.json
郵務窗口(114年度)（188題）.json
儲匯壽窗口(114年度)（202題）.json
資通安全（30題）.json
法令遵循／防制洗錢（262題）.json
高齡投保（10題）.json
... (and 17 more categories)
```

**Question Data Structure**:
```json
{
  "description": "<p>問題內容</p>",
  "type": "single_selection",  // or "multiple_selection"
  "difficulty_level": "medium",
  "options": [
    {
      "content": "<p>選項內容</p>",
      "is_answer": true,  // Correct answer flag
      "sort": 0
    }
  ]
}
```

---

### Exam Page Analysis

**HTML Structure** (Analyzed from exam snapshot):

#### 1. Question Elements
```html
<li class="subject" ng-repeat="subject in subjects">
    <span class="subject-description"
          ng-compile-html="subject.description">
        題目內容
    </span>
</li>
```

**Locators**:
- CSS Class: `.subject-description`
- XPath: `//li[@class='subject']//span[@class='subject-description']`

#### 2. Option Elements

**Single Choice (Radio)**:
```html
<li class="option">
    <label>
        <input type="radio"
               ng-model="subject.answeredOption"
               ng-change="onChangeSubmission(subject)" />
        <div class="option-content">
            <span>選項內容</span>
        </div>
    </label>
</li>
```

**Multiple Choice (Checkbox)**:
```html
<li class="option">
    <label>
        <input type="checkbox"
               ng-model="option.checked"
               ng-change="onChangeSubmission(subject)" />
        <div class="option-content">
            <span>選項內容</span>
        </div>
    </label>
</li>
```

**Locators**:
- CSS Class: `.option-content`
- Radio: `input[type="radio"]`
- Checkbox: `input[type="checkbox"]`

#### 3. Submit Button
```html
<a class="button button-green"
   ng-click="calUnsavedSubjects()">
   交卷
</a>

<!-- Confirmation popup -->
<button ng-click="submitAnswer(...)">確定</button>
```

**Important**: Exam uses **whole-page display** (all questions on one page), not paginated.

---

### Database Strategy Evaluation

#### Recommended Approach: **Hybrid Mode (SQLite + JSON)**

| Database | Single-User | Speed | Deployment | Matching | Recommendation |
|----------|------------|-------|------------|----------|----------------|
| **SQLite** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ (Zero config) | ⭐⭐⭐⭐⭐ (SQL LIKE) | **✅ Recommended** |
| JSON | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ (Already exists) | ⭐⭐⭐ (String match) | ✅ For MVP |
| MySQL | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ (Need server) | ⭐⭐⭐⭐⭐ | ❌ Overkill |
| DuckDB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ (Need install) | ⭐⭐⭐⭐⭐ | ⚠️ Alternative |

**Why SQLite?**
- ✅ Zero configuration (built-in Python `sqlite3`)
- ✅ File-based (single `.db` file, easy backup)
- ✅ Fast queries (millisecond-level for 1,766 questions)
- ✅ Full-text search support (FTS5 extension)
- ✅ Perfect for 5.3MB dataset
- ✅ Cross-platform compatibility

**Hybrid Strategy**:
```
Phase 1 (MVP): Use existing JSON files directly
Phase 2 (Optimization): Auto-build SQLite on first run
Phase 3 (Production): Use SQLite, keep JSON as backup
```

---

### Proposed Architecture

#### New File Structure (POM Compliant)
```
eebot/
├── src/
│   ├── pages/
│   │   ├── exam_detail_page.py        # Existing (DO NOT MODIFY)
│   │   └── exam_answer_page.py        # NEW - Answer page operations
│   │
│   ├── scenarios/
│   │   ├── exam_learning.py           # Existing (DO NOT MODIFY)
│   │   └── exam_auto_answer.py        # NEW - Auto-answer scenario
│   │
│   ├── services/                      # NEW - Business logic layer
│   │   ├── __init__.py
│   │   ├── question_bank.py           # NEW - Question bank service
│   │   └── answer_matcher.py          # NEW - Answer matching engine
│   │
│   └── models/                        # NEW - Data models
│       ├── __init__.py
│       └── question.py                # NEW - Question/Option classes
│
├── data/
│   ├── courses.json                   # Existing
│   ├── schedule.json                  # Existing
│   └── questions.db                   # NEW - SQLite database (auto-generated)
│
└── 郵政E大學114年題庫/
    └── *.json                         # Existing (kept as backup)
```

#### Layer Responsibilities

**ExamAnswerPage** (Page Object):
```python
class ExamAnswerPage(BasePage):
    def get_all_questions() -> List[WebElement]
    def get_question_text(question_elem) -> str
    def get_options(question_elem) -> List[WebElement]
    def get_option_text(option_elem) -> str
    def click_option(option_elem, is_checkbox=False)
    def submit_exam(delay=2.0)
    def get_progress() -> (answered, total)
```

**QuestionBankService** (Data Layer):
```python
class QuestionBankService:
    def __init__(mode='sqlite', **kwargs)
    def find_answer(question_text) -> Optional[Dict]
    # Returns: {question_id, type, correct_options[]}
```

**AnswerMatcher** (Matching Engine):
```python
class AnswerMatcher:
    @staticmethod
    def normalize_text(text) -> str
    def find_best_match(web_q, db_qs) -> Optional[Dict]
    # Multi-level fallback:
    # 1. Exact match (fastest)
    # 2. Contains match
    # 3. Similarity match (SequenceMatcher)
```

**ExamAutoAnswerScenario** (Orchestration):
```python
class ExamAutoAnswerScenario:
    def auto_answer_all_questions()
    # Workflow:
    # 1. Get all questions from page
    # 2. For each question:
    #    - Extract question text
    #    - Query question bank
    #    - Match options
    #    - Click correct option(s)
    # 3. Submit exam
```

---

### Answer Matching Strategy

#### Challenge: Web Question vs Database Question Differences

| Difference Type | Example | Solution |
|----------------|---------|----------|
| HTML Tags | `<p>問題</p>` vs `問題` | Strip HTML with BeautifulSoup |
| Whitespace | Multiple spaces vs single | Normalize with regex |
| Punctuation | Full-width vs half-width | Standardize `？` → `?` |
| Line breaks | `\n` vs `<br>` | Replace all to space |

#### Multi-Level Matching Algorithm

```python
class AnswerMatcher:
    def find_best_match(self, web_question, db_questions):
        web_norm = self.normalize_text(web_question)

        for db_q in db_questions:
            db_norm = self.normalize_text(db_q['description'])

            # Strategy 1: Exact match (fastest)
            if web_norm == db_norm:
                return db_q

            # Strategy 2: Contains match
            if web_norm in db_norm or db_norm in web_norm:
                return db_q

            # Strategy 3: Similarity match (SequenceMatcher)
            similarity = SequenceMatcher(None, web_norm, db_norm).ratio()
            if similarity >= 0.85:  # Confidence threshold
                return db_q

        return None  # No match found
```

**Confidence Threshold**: 0.85 (85% similarity required to avoid false positives)

---

### SQLite Database Schema

#### Tables

**questions** (Main question table):
```sql
CREATE TABLE questions (
    id INTEGER PRIMARY KEY,
    category TEXT NOT NULL,              -- 分類（窗口線上測驗、法遵等）
    description TEXT NOT NULL,            -- 題目內容（HTML）
    description_text TEXT,                -- 純文字版本（用於匹配）
    difficulty_level TEXT,                -- 難度（easy/medium/hard）
    type TEXT NOT NULL,                   -- 題型（single_selection/multiple_selection）
    answer_explanation TEXT,
    last_updated_at TEXT
);
```

**options** (Options table):
```sql
CREATE TABLE options (
    id INTEGER PRIMARY KEY,
    question_id INTEGER NOT NULL,
    content TEXT NOT NULL,                -- 選項內容（HTML）
    content_text TEXT,                    -- 純文字版本
    is_answer BOOLEAN NOT NULL,           -- 是否為正確答案
    sort INTEGER,
    FOREIGN KEY (question_id) REFERENCES questions(id)
);
```

**Indexes** (Performance optimization):
```sql
-- Full-text search (Critical for fuzzy matching)
CREATE VIRTUAL TABLE questions_fts USING fts5(
    description_text,
    content='questions',
    content_rowid='id'
);

-- Regular indexes
CREATE INDEX idx_category ON questions(category);
CREATE INDEX idx_type ON questions(type);
CREATE INDEX idx_description_text ON questions(description_text);
```

#### Migration Script Concept
```python
def migrate_json_to_sqlite(json_dir, db_path):
    # 1. Read all JSON files
    # 2. Extract questions and options
    # 3. Clean HTML → plain text
    # 4. Insert into SQLite
    # 5. Build FTS5 index
```

---

### Implementation Phases

#### Phase 1: MVP (Minimum Viable Product)
**Goal**: Prove auto-answering works

- ✅ Use existing JSON files (no conversion needed)
- ✅ Implement `QuestionBankService` (JSON mode)
- ✅ Implement basic `AnswerMatcher`
- ✅ Implement `ExamAnswerPage` (read questions, click options)
- ✅ Integrate into `ExamLearningScenario`
- ✅ Test with single exam

**Estimated Time**: 2-3 hours

#### Phase 2: Optimize Matching
**Goal**: Improve accuracy

- ✅ Enhance `AnswerMatcher` (similarity algorithms)
- ✅ Handle HTML cleaning edge cases
- ✅ Add matching logs (track success/failure)
- ✅ Test with full question bank

**Estimated Time**: 2-3 hours

#### Phase 3: Migrate to SQLite
**Goal**: Performance optimization

- ✅ Write JSON → SQLite migration script
- ✅ Build FTS5 full-text index
- ✅ Implement `QuestionBankService` (SQLite mode)
- ✅ Performance comparison testing

**Estimated Time**: 1-2 hours

#### Phase 4: Production Ready
**Goal**: Robust and maintainable

- ✅ Hybrid mode (auto-build SQLite on first run)
- ✅ Auto-detect question bank updates
- ✅ Screenshot failed matches for debugging
- ✅ Generate answer accuracy reports
- ✅ Configuration options in `eebot.cfg`

**Estimated Time**: 2-3 hours

---

### Configuration Options (Planned)

#### eebot.cfg additions
```ini
# Existing config...
user_name=your_username
password=your_password

# NEW: Auto-answer configuration
enable_auto_answer=y                     # Enable auto-answering
question_bank_mode=sqlite                # 'sqlite' or 'json'
question_bank_path=data/questions.db
answer_confidence_threshold=0.85         # Minimum similarity score
auto_submit_exam=y                       # Auto-submit after answering
screenshot_on_mismatch=y                 # Screenshot when no match found
```

---

### Risk Assessment

| Risk | Description | Mitigation |
|------|-------------|------------|
| **Matching Failure** | Web question ≠ DB question | Multi-level fallback + confidence threshold |
| **Dynamic Loading** | AngularJS render delay | Increase WebDriverWait timeout |
| **Detection Risk** | Website may detect automation | Already using Stealth JS |
| **Outdated Bank** | Question bank out of sync | Log mismatches, manual review |
| **Multiple Choice** | Need to click multiple options | Check `type` field in database |

---

### Success Criteria

**MVP Success**:
- [ ] Successfully match ≥80% of questions
- [ ] Auto-click correct options (single choice)
- [ ] Auto-click correct options (multiple choice)
- [ ] Submit exam automatically

**Production Success**:
- [ ] Match rate ≥95%
- [ ] SQLite query time <10ms per question
- [ ] Zero false positives (wrong answers)
- [ ] Graceful handling of unmatched questions

---

### Testing Strategy

#### Unit Testing
```python
# Test answer matcher
def test_exact_match():
    assert matcher.find_best_match("問題A", ["問題A", "問題B"]) == "問題A"

def test_html_cleaning():
    assert matcher.normalize_text("<p>問題</p>") == "問題"
```

#### Integration Testing
```bash
# Test single exam with known answers
python main.py --test-mode --exam="高齡測驗"
```

#### Manual Testing Checklist
- [ ] Single choice questions answered correctly
- [ ] Multiple choice questions answered correctly
- [ ] Exam submission successful
- [ ] Unmatched questions skipped gracefully
- [ ] Screenshot saved for failed matches

---

### Documentation Requirements

When implementing auto-answer:

1. **Update this file** (`AI_ASSISTANT_GUIDE.md`):
   - Move from "Planned Features" to "Implemented Features"
   - Add usage examples

2. **Update `CLAUDE_CODE_HANDOVER.md`**:
   - Add auto-answer workflow
   - Update file structure

3. **Update `CHANGELOG.md`**:
   - Record implementation date
   - List all new files
   - Document breaking changes

4. **Update `README.md`**:
   - Add auto-answer quick start guide

---

### ✅ Implementation Status (Updated 2025-11-15)

**Implementation Completed**: ✅ All planned features have been implemented

**Implemented Components**:
1. ✅ Data Models (`src/models/question.py`)
2. ✅ Question Bank Service (`src/services/question_bank.py`)
3. ✅ Answer Matcher Engine (`src/services/answer_matcher.py`)
4. ✅ Exam Answer Page (`src/pages/exam_answer_page.py`)
5. ✅ Auto Answer Scenario (`src/scenarios/exam_auto_answer.py`)
6. ✅ Configuration System (`config/eebot.cfg`)
7. ✅ Main Integration (`main.py`)

**Key Features Delivered**:
- ✅ Automatic question detection (count, type)
- ✅ Multi-level matching algorithm (exact → contains → similarity)
- ✅ Single/multiple choice handling
- ✅ Screenshot capture for unmatched questions
- ✅ Answer statistics and reporting
- ✅ User confirmation before submission
- ✅ Total bank mode (1,766 questions)

**Configuration File**: `config/eebot.cfg`
```ini
enable_auto_answer = y
question_bank_mode = total_bank
answer_confidence_threshold = 0.85
auto_submit_exam = n
screenshot_on_mismatch = y
skip_unmatched_questions = y
```

**Dependencies Added**:
- `beautifulsoup4>=4.9.0` (HTML parsing)

**Testing Status**: Ready for user testing

---

**Implementation Version**: 2.0.2+auto-answer
**Implemented By**: wizard03 (with Claude Code CLI - Sonnet 4.5)
**Implementation Date**: 2025-11-15
**Status**: ✅ **PRODUCTION READY**

---

## 🎯 Smart Mode: Per-Course Auto-Answer (Updated 2025-11-15)

> **Breaking Change**: Auto-answer logic changed from global activation to per-course activation

### Overview

**Previous Behavior (v2.0.2+auto-answer)**:
- Global `enable_auto_answer` setting in `config/eebot.cfg`
- All exams either enabled or disabled for auto-answer
- Required changing config file to enable/disable

**New Behavior (v2.0.2+auto-answer Smart Mode)**:
- Per-course `enable_auto_answer` field in `data/courses.json`
- Each exam can independently enable/disable auto-answer
- No need to modify config file for different exams
- Automatic detection of exam answer page before activation

### Configuration Changes

#### 1. Per-Exam Configuration (courses.json)

**Add `enable_auto_answer` field to specific exams**:

```json
{
  "program_name": "高齡客戶投保權益保障(114年度)",
  "exam_name": "高齡測驗(100分及格)",
  "course_type": "exam",
  "enable_auto_answer": true,    // Enable auto-answer for this exam only
  "delay": 7.0,
  "description": "高齡客戶投保權益保障考試流程 - 啟用自動答題"
}
```

**Exams without this field default to manual mode**:

```json
{
  "program_name": "其他考試(114年度)",
  "exam_name": "其他測驗",
  "course_type": "exam",
  // enable_auto_answer not set → manual mode (user completes exam)
  "delay": 7.0,
  "description": "需手動完成的考試"
}
```

#### 2. Question Bank Mode (config/eebot.cfg)

**Recommended Setting**: Use `file_mapping` mode for better accuracy

```ini
[AUTO_ANSWER]
enable_auto_answer = y                          # Keep enabled (legacy setting)
question_bank_mode = file_mapping               # Changed from 'total_bank'
question_bank_path = 郵政E大學114年題庫/總題庫.json
answer_confidence_threshold = 0.85
auto_submit_exam = n
screenshot_on_mismatch = y
skip_unmatched_questions = y
screenshot_dir = screenshots/unmatched
```

**Question Bank Mapping** (in `QuestionBankService`):

| Program Name | Question Bank File |
|-------------|-------------------|
| 高齡客戶投保權益保障(114年度) | 高齡投保（10題）.json |
| 資通安全學程課程(114年度) | 資通安全（30題）.json |
| 壽險業務員在職訓練學程課程及測驗(114年度) | 壽險業務員在職訓練（30題）.json |
| 金融服務業公平待客原則＆洗錢防制及打擊資恐教育訓練(114年度) | 法令遵循／防制洗錢（262題）.json |

### Workflow Changes

#### Previous Workflow (Global Mode)
```
1. Edit config/eebot.cfg → set enable_auto_answer=y
2. Run python menu.py → select exam
3. Run python main.py → all exams auto-answer
4. Edit config back to enable_auto_answer=n (if needed)
```

#### New Workflow (Smart Mode)
```
1. Edit data/courses.json → add "enable_auto_answer": true to specific exam
2. Run python menu.py → select exam
3. Run python main.py → only marked exams auto-answer
4. System auto-detects exam answer page before activation
```

### Technical Implementation

#### 1. Exam Answer Page Detection

**New Method**: `_is_in_exam_answer_page()` in `ExamLearningScenario`

```python
def _is_in_exam_answer_page(self) -> bool:
    """Detect if currently on exam answer page"""
    try:
        driver = self.driver_manager.get_driver()
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "li.subject"))
        )
        questions = driver.find_elements(By.CSS_SELECTOR, "li.subject")
        if len(questions) > 0:
            print(f'  ✅ 偵測到考卷區頁面（共 {len(questions)} 題）')
            return True
        return False
    except Exception as e:
        print(f'  ⚠️  考卷區檢測失敗: {e}')
        return False
```

**Purpose**: Prevents auto-answer from activating on wrong pages

#### 2. Lazy Initialization

**Previous**: Question bank and matcher loaded for all exams

**New**: Only load when `enable_auto_answer=true` and on exam answer page

```python
class ExamLearningScenario:
    def __init__(self, config, keep_browser_on_error=False):
        # ... existing code ...
        self.exam_answer_page = ExamAnswerPage(driver)
        self.question_bank = None      # Lazy init
        self.answer_matcher = None     # Lazy init

    def _auto_answer_current_exam(self, exam):
        """Initialize question bank only when needed"""
        if self.question_bank is None:
            print('[初始化] 載入題庫...')
            self.question_bank = QuestionBankService(self.config)
            question_count = self.question_bank.load_question_bank(
                exam.get('program_name')
            )

        if self.answer_matcher is None:
            print('[初始化] 載入答案匹配器...')
            self.answer_matcher = AnswerMatcher(self.config)
```

**Benefits**:
- Save memory for manual exams
- Faster startup time
- Only load relevant question bank (file_mapping mode)

#### 3. Conditional Activation Logic

**New Process in `_process_exam()`**:

```python
def _process_exam(self, exam: Dict[str, any]):
    # ... existing exam flow (login, navigate, click exam) ...

    # NEW: Check if auto-answer is enabled for this exam
    enable_auto_answer = exam.get('enable_auto_answer', False)

    if enable_auto_answer and self._is_in_exam_answer_page():
        print('【自動答題模式啟動】')
        self._auto_answer_current_exam(exam)
    else:
        print('請手動完成考試')
        input('完成後按 Enter 繼續...')
```

**Decision Tree**:
```
Is enable_auto_answer=true?
  ├─ No → Manual mode (wait for user)
  └─ Yes → Check if on exam answer page
      ├─ No → Manual mode (wrong page)
      └─ Yes → Auto-answer mode (activate)
```

### Main Program Simplification

**Previous**: Two separate scenarios

```python
# Old code (removed)
if enable_auto_answer:
    exam_scenario = ExamAutoAnswerScenario(...)
else:
    exam_scenario = ExamLearningScenario(...)
```

**New**: Unified scenario

```python
# New code (simplified)
exam_scenario = ExamLearningScenario(config, keep_browser_on_error)
exam_scenario.execute(exams)
# Each exam decides its own mode internally
```

**Benefits**:
- Single browser session for all exams
- No browser restarts between exams
- Cleaner main.py code

### Important Bug Fixes (2025-11-15)

#### 1. UTF-8 BOM Encoding
**Problem**: JSON files have UTF-8 BOM markers
**Solution**: Changed all JSON reads to `encoding='utf-8-sig'`

**Affected Files**:
- `src/services/question_bank.py`
- `main.py`
- `menu.py`

#### 2. Pagination Structure Handling
**Problem**: Question bank files use `[{"subjects": [...]}]` structure
**Solution**: Added pagination detection in `_load_specific_bank()`

```python
if isinstance(data[0], dict) and 'subjects' in data[0]:
    # Pagination structure
    for page in data:
        if 'subjects' in page:
            for subject in page['subjects']:
                # Process question
```

#### 3. Element Interaction Issues
**Problem**: Submit buttons not clickable (element not interactable)
**Solution**: Use JavaScript clicks with precise XPaths

```python
# Updated locators in exam_answer_page.py
SUBMIT_BUTTON = (By.XPATH, "/html/body/div[3]/div[4]/div[3]/div[9]/div/div/div[3]/div/div[3]/a")
CONFIRM_BUTTON = (By.XPATH, "//*[@id='submit-exam-confirmation-popup']/div/div[3]/div/button[1]")

# JavaScript click
self.driver.execute_script("arguments[0].click();", submit_btn)
time.sleep(3)
```

### Usage Examples

#### Example 1: Enable Auto-Answer for Specific Exam

**Step 1**: Edit `data/courses.json`

```json
{
  "description": "課程資料配置檔",
  "version": "1.0",
  "courses": [
    {
      "program_name": "高齡客戶投保權益保障(114年度)",
      "exam_name": "高齡測驗(100分及格)",
      "course_type": "exam",
      "enable_auto_answer": true,    // Enable for this exam
      "delay": 7.0,
      "description": "高齡測驗 - 自動答題"
    },
    {
      "program_name": "其他考試(114年度)",
      "exam_name": "其他測驗",
      "course_type": "exam",
      // No enable_auto_answer → manual mode
      "delay": 7.0,
      "description": "其他測驗 - 手動完成"
    }
  ]
}
```

**Step 2**: Schedule and run

```bash
python menu.py
# Select both exams

python main.py
# Exam 1: Auto-answer activated ✅
# Exam 2: Manual mode (user completes) ⏸️
```

#### Example 2: Mixed Course and Exam Schedule

```bash
python menu.py
# Select:
# [1] Course A (regular course)
# [2] Course B (regular course)
# [3] Exam A (enable_auto_answer: true)
# [4] Exam B (enable_auto_answer: false)

python main.py
# Execution order:
# 1. Course A → Auto-complete ✅
# 2. Course B → Auto-complete ✅
# 3. Exam A → Auto-answer ✅
# 4. Exam B → Manual mode (wait for user) ⏸️
```

### Testing Results

**Test Case**: 高齡客戶投保權益保障考試

| Metric | Result |
|--------|--------|
| Questions Loaded | 10 |
| Questions Matched | 10 (100%) |
| Match Confidence | 95-100% |
| Auto-Answer Success | ✅ All correct |
| Exam Submission | ✅ Success |

### Migration Guide (from v2.0.2+auto-answer)

**If you were using global `enable_auto_answer`**:

1. Keep `enable_auto_answer=y` in `config/eebot.cfg` (backward compatible)
2. Add `"enable_auto_answer": true` to exams you want automated
3. Change `question_bank_mode` to `file_mapping` for better accuracy
4. Remove old `ExamAutoAnswerScenario` imports (if any)

**Breaking Changes**:
- Global config `enable_auto_answer` no longer controls all exams
- Must explicitly set per-exam configuration
- `ExamAutoAnswerScenario` class removed (functionality merged into `ExamLearningScenario`)

**Backward Compatibility**:
- Exams without `enable_auto_answer` field default to manual mode
- All existing manual exam workflows unchanged
- Course learning flows unaffected

### Best Practices

#### 1. Start with Manual Testing
```json
{
  "enable_auto_answer": false,  // or omit field
  "description": "Test manually first"
}
```

#### 2. Verify Question Bank Mapping
Check `src/services/question_bank.py` for program name mapping:

```python
QUESTION_BANK_MAPPING = {
    "高齡客戶投保權益保障(114年度)": "高齡投保（10題）.json",
    # Add more mappings as needed
}
```

#### 3. Monitor Match Success
Watch console output:
```
[匹配] 第 1 題: 正確答案為哪一個選項？
  ✅ 匹配成功（信心: 100.00%）
  ✅ 正確答案: ['選項1', '選項2']
```

#### 4. Review Screenshots for Failures
Unmatched questions saved to `screenshots/unmatched/`:
```
question_5_20251115_143022.png
question_5_20251115_143022.txt  // Contains question text
```

### Troubleshooting Smart Mode

#### Issue 1: Auto-Answer Not Activating

**Check**:
1. Is `"enable_auto_answer": true` in courses.json?
2. Is exam on the correct page (exam answer page)?
3. Check console for page detection messages

**Debug Output**:
```
✅ 偵測到考卷區頁面（共 10 題）
【自動答題模式啟動】
[初始化] 載入題庫...
```

#### Issue 2: Questions Not Matching

**Check**:
1. Is `question_bank_mode` set correctly?
2. Is program name exactly matching the mapping?
3. Check confidence threshold (default 0.85)

**Debug Output**:
```
[載入] 題庫檔案: 郵政E大學114年題庫/高齡投保（10題）.json
[成功] 載入題庫: 10 題
```

#### Issue 3: Submit Button Not Working

**Check**:
1. XPath locators in `exam_answer_page.py`
2. Wait times between clicks (default 3 seconds)
3. JavaScript execution enabled

**Solution**: Locators were updated with user-provided XPaths

#### Issue 4: 0% Match Rate on Second Exam (CRITICAL BUG - FIXED)

**Symptom**:
- First exam: 100% match rate ✅
- Second exam: 0% match rate ❌
- All questions showing as "無法匹配"

**Root Cause**:
Lazy loading bug in `src/scenarios/exam_learning.py:261` caused multiple exams to share the same question bank instance.

**Problem Mechanism**:
```python
# ❌ BUGGY CODE (Before Fix)
if self.question_bank is None:
    self.question_bank = QuestionBankService(self.config)
    question_count = self.question_bank.load_question_bank(exam.get('program_name'))
```

1. Exam 1 loads question bank A (e.g., 高齡投保 10 題)
2. `self.question_bank` is no longer `None`
3. Exam 2 skips initialization
4. Exam 2 tries to match against wrong question bank A
5. Result: 0% match rate

**Solution** (Applied in v2.0.2+auto-answer.1):
```python
# ✅ FIXED CODE
# Always reload question bank for each exam
self.question_bank = QuestionBankService(self.config)
program_name = exam.get('program_name')
question_count = self.question_bank.load_question_bank(program_name)
```

**Key Changes**:
- ✅ Removed `if self.question_bank is None` check
- ✅ Always create new `QuestionBankService` instance per exam
- ✅ Added program_name logging for debugging

**Verification**:
Run multiple exams and verify each loads correct question bank:
```
--- Processing Exam 1/2 ---
  📚 正在載入題庫...
  ✅ 題庫已載入（共 10 題）
  📋 課程名稱: 高齡客戶投保權益保障(114年度)

--- Processing Exam 2/2 ---
  📚 正在載入題庫...
  ✅ 題庫已載入（共 21 題）
  📋 課程名稱: 金融服務業公平待客原則＆洗錢防制及打擊資恐教育訓練(114年度)
```

**⚠️ Important Lesson**:
> **Lazy Loading + Shared State = Potential Bug**
>
> When an object instance is reused for processing multiple different datasets:
> - ❌ DO NOT use lazy loading without checking if data context changed
> - ✅ DO reload resources when processing new data
> - ✅ DO add logging to track which resource is loaded
> - ✅ DO test with multiple sequential operations

**Code Review Checklist for Similar Patterns**:
- [ ] Is there lazy loading (`if self.resource is None`)?
- [ ] Is the instance reused for different data?
- [ ] Does the resource depend on input parameters?
- [ ] Is there a test for multiple sequential operations?

---

**Smart Mode Version**: 2.0.2+auto-answer.1 (Lazy Loading Bug Fixed)
**Updated**: 2025-11-15 晚間
**Updated By**: wizard03 (with Claude Code CLI - Gleipnir Project)

---

## 📞 Support & Resources

### Documentation
- **AI Assistant Guide**: `docs/AI_ASSISTANT_GUIDE.md` (this file)
- **Claude Code Guide**: `docs/CLAUDE_CODE_HANDOVER.md`
- **Change Log**: `docs/CHANGELOG.md`

### External Resources
- **Selenium Docs**: https://www.selenium.dev/documentation/
- **MitmProxy Docs**: https://docs.mitmproxy.org/
- **Python POM Pattern**: https://selenium-python.readthedocs.io/page-objects.html

### Quick Commands Reference
```bash
# Schedule courses
python menu.py

# Run scheduled courses
python main.py

# View configuration
cat config/eebot.cfg

# View courses
cat data/courses.json

# View schedule
cat data/schedule.json

# View recent changes
cat docs/CHANGELOG.md

# Find course_id in HTML
grep -r "goBackCourse" .

# Check Python version
python --version

# Install dependencies (if needed)
pip install -r requirements.txt
```

---

## ✅ Pre-Modification Checklist

Before making any changes, verify:

- [ ] I have read `docs/CHANGELOG.md`
- [ ] I have checked the "DO NOT MODIFY" list
- [ ] I understand the existing code pattern
- [ ] I have a backup or version control
- [ ] I have planned my changes
- [ ] I know how to test my changes
- [ ] I will update CHANGELOG.md after changes

---

**Document Maintained By**: wizard03
**For**: All AI Programming Assistants
**Last Updated**: 2025-01-13
**Version**: 1.0

---

**Happy Coding! 🚀**

*This project was enhanced with AI assistance (Claude Code CLI)*

