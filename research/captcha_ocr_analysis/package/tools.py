from winreg import SaveKey
import pyautogui
from time import sleep

def click(x, y):
    CLICK_TIMES = 2
    for _ in range(CLICK_TIMES):
        pyautogui.click(x, y)
    else:
        sleep(0.5)