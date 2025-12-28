import pyautogui
from time import sleep
import pyscreenshot as ImageGrab
from PIL import Image
import pytesseract
import cv2 as cv
import re
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'

def getPic(save_to: str):
    im = ImageGrab.grab(
            bbox=(
                1413, 798,
                1555, 842
            )
        )

    im.save(save_to)

def recognize_text(image):
    # 邊緣保留濾波、去噪
    blur =cv.pyrMeanShiftFiltering(image, sp=8, sr=60)

    # 灰化
    gray = cv.cvtColor(blur, cv.COLOR_BGR2GRAY)

    # 二元化
    ret, binary = cv.threshold(gray, 0, 255, cv.THRESH_BINARY_INV | cv.THRESH_OTSU)

    # 型態操作 獲取結構元素
    kernel = cv.getStructuringElement(cv.MORPH_RECT, (3, 2))
    bin1 = cv.morphologyEx(binary, cv.MORPH_OPEN, kernel)
    kernel = cv.getStructuringElement(cv.MORPH_OPEN, (2, 3))
    bin2 = cv.morphologyEx(bin1, cv.MORPH_OPEN, kernel)

    # 變成白底黑字，比較好辨識
    cv.bitwise_not(bin2, bin2)

    # 辨識
    test_message = Image.fromarray(bin2)
    text = pytesseract.image_to_string(test_message)
    try:
        text = re.match(r'\d+', text).group()
    except AttributeError:
        pass
    
    if len(text) > 1 and len(text) < 6:
        return True, text
    else:
        return False, text


# def is_verifyCode_correct(fileName = "is_verifyCode_correct.png"):
#     im = ImageGrab.grab(
#             bbox=(
#                 1597, 157, 
#                 1877, 202
#             )
#         )
#     im.save(fileName)
#     img = Image.open(fileName)
#     text = pytesseract.image_to_string(img, lang='chi_tra').replace(' ', '').replace('\n', '')

#     if '驗證碼輸入有誤' in text:
#         print(f"[!]錯誤訊息: {text}")
#         # 點掉彈出視窗
#         pyautogui.click(2187, 238)
#         return False
#     else:
#         print(f"[!] 登入成功 !")
#         print(text)
#         return True

def enter_string(input: str):
    for word in input:
        pyautogui.press(word)


def login_TaiwanJobs(account: str, password: str, verifyCode: str, screen_no: int):
    """
    Automatically login TaiwanJobs in the resolution == 3840*2160
    """
    sleep_time = 0.1
    from main import WORKING_TASK

    # click2_and_sleep((1500, 650), 0.1)
    click2_and_sleep(WORKING_TASK.LOGIN_ACCOUNT_BOX[screen_no], sleep_time)

    for _ in range(len(account)):
        pyautogui.press('backspace')
    enter_string(account)

    # click2_and_sleep((2100, 750), sleep_time)
    
    click2_and_sleep(WORKING_TASK.LOGIN_PWD_BOX[screen_no], sleep_time)
    enter_string(password)

    click2_and_sleep(WORKING_TASK.LOGIN_VERIFY_BOX[screen_no], sleep_time)
    enter_string(verifyCode)

    sleep(sleep_time)
    pyautogui.click(1157, 954)

def click2_and_sleep(position: tuple, sleep_time: float):
    pyautogui.click(*position)
    sleep(sleep_time)
    pyautogui.click(*position)


def login_process():
    n = 1
    try_login_times = 1
    while True:
        print(f"[*]第 {n} 次分析驗證碼")
        n += 1
        getPic()
        src = cv.imread(r'./t.png')
        is_recognize, text = recognize_text(src)

        if not is_recognize:
            pyautogui.click(1596, 842)
            sleep(1)
            continue
        print(f'[*]第 {try_login_times} 次嘗試登入中 -> 驗證碼: {text}')
        try_login_times += 1

        login_TaiwanJobs(
            account='juexuan1010@gmail.com',
            password='beelove0108',
            verifyCode=text,
            screen_no=0
        )

        sleep(1.5)

        if is_verifyCode_correct():
            break

