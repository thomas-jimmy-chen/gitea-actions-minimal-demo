# EEBot - AI Assistant Handover Guide

> **Universal AI Programming Assistant Documentation**
>
> Compatible with: Claude Code CLI, Cursor, GitHub Copilot CLI, Cody, Tabnine, and all AI-powered code assistants

**Document Version**: 1.0
**Last Updated**: 2025-01-13
**Project Version**: 2.0.1+exam
**Maintainer**: wizard03

---

## 🎯 Quick Project Overview

### What is EEBot?

**EEBot** (Elearn Automation Bot) is a **Selenium-based automation tool** designed specifically for Taiwan Post's e-Learning platform (郵政e大學). It automates the process of completing online courses and exams.

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
- `delay`: Wait time in seconds before clicking
- `description`: Optional description for documentation

#### Exam Type (NEW ✨ 2025-01-13)
```json
{
  "program_name": "課程計畫名稱",
  "exam_name": "考試名稱",
  "course_type": "exam",
  "delay": 10.0,
  "description": "考試描述"
}
```

**Key Differences**:
- Uses `exam_name` instead of `lesson_name`
- Has `course_type: "exam"` marker
- No `course_id` (exam flow doesn't use it)
- Longer `delay` (10.0s) due to complex exam flow

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
      "delay": 10.0,
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
  "delay": 10.0,
  "description": "Exam description"
}
```

#### Step 3: (If flow is different) Modify exam_detail_page.py
```python
def my_custom_exam_step(self, delay: float = 10.0):
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

