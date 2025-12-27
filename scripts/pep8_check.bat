@echo off
REM PEP 8 檢查腳本
REM 用途：快速檢查代碼風格，不修改文件

echo ========================================
echo PEP 8 代碼風格檢查
echo ========================================
echo.

echo [1/3] 檢查代碼格式 (Black)...
black src/ menu.py --check --diff
if %ERRORLEVEL% EQU 0 (
    echo ✓ Black 檢查通過
) else (
    echo ✗ Black 發現格式問題
)
echo.

echo [2/3] 檢查導入排序 (isort)...
isort src/ menu.py --check-only --diff
if %ERRORLEVEL% EQU 0 (
    echo ✓ isort 檢查通過
) else (
    echo ✗ isort 發現排序問題
)
echo.

echo [3/3] 檢查代碼質量 (Flake8)...
flake8 src/ menu.py --max-line-length 79 --statistics
if %ERRORLEVEL% EQU 0 (
    echo ✓ Flake8 檢查通過
) else (
    echo ✗ Flake8 發現問題
)
echo.

echo ========================================
echo 檢查完成！
echo.
echo 如需自動修復格式問題，請運行:
echo   scripts\pep8_fix.bat
echo ========================================
pause
