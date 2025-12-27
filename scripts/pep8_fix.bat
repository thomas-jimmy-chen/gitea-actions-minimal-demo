@echo off
REM PEP 8 自動修復腳本
REM 用途：自動格式化代碼

echo ========================================
echo PEP 8 代碼自動格式化
echo ========================================
echo.
echo 警告：此操作會修改文件！
echo 請確保已提交或備份當前代碼。
echo.

set /p confirm="繼續? (y/n): "
if /i not "%confirm%"=="y" (
    echo 已取消
    pause
    exit /b
)

echo.
echo [1/3] 排序導入語句 (isort)...
isort src/ menu.py --profile black
if %ERRORLEVEL% EQU 0 (
    echo ✓ isort 完成
) else (
    echo ✗ isort 失敗
    pause
    exit /b 1
)
echo.

echo [2/3] 格式化代碼 (Black)...
black src/ menu.py --line-length 79
if %ERRORLEVEL% EQU 0 (
    echo ✓ Black 完成
) else (
    echo ✗ Black 失敗
    pause
    exit /b 1
)
echo.

echo [3/3] 檢查剩餘問題 (Flake8)...
flake8 src/ menu.py --max-line-length 79 --statistics > flake8_report.txt
if %ERRORLEVEL% EQU 0 (
    echo ✓ 沒有 Flake8 錯誤
) else (
    echo ⚠ Flake8 發現一些問題，請查看 flake8_report.txt
)
echo.

echo ========================================
echo 格式化完成！
echo.
echo 下一步：
echo   1. 檢查修改: git diff
echo   2. 測試功能: python menu.py
echo   3. 提交代碼: git commit -m "style: 應用 PEP 8 格式化"
echo ========================================
pause
