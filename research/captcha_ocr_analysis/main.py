

# How to use: 
#     python main.py <num_of_screen_split>

import os
import sys
import time
import random
import datetime
import pyautogui
import webbrowser
import pytesseract
import configparser
import pyscreenshot as ImageGrab
from PIL import Image
from package.tools import *
from package.verify import login_process, click2_and_sleep, enter_string
from package.img_process import getPic, is_type_correct, recognize_text, is_verifyCode_correct, get_verification
from package.initialization import *


print(' INITIALIZATION '.center(100, '=')) 

pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'
version = '220220'
_MAIN_RESOLUTION = tuple(pyautogui.size())
_SCREEN_SPLIT = (1, 4)
_USERS_PATH = './USERS.ini'
_IMAGE_PATH = './images/'
_WINDOWS_TASKBAR_h = 45 # 工作列高度約45~60

try:
    check_argv(sys.argv, _SCREEN_SPLIT)

    check_images_folder(_IMAGE_PATH)

    check_users_file(_USERS_PATH)

    check_pytesseract(pytesseract.pytesseract.tesseract_cmd)
except Exception as err_msg:
    print(err_msg)
    print(' INTERRUPT '.center(100, '=')) 
    for _ in range(5):
        print('↓'.center(100))
    sys.exit()

print('======='.center(100, '='))
print('↓'.center(100))
print('↓'.center(100))
# ****************************位置像素設定****************************
# 注意: 以下參數請以1920*1080的解析度，畫面縮放為100%來測量。
#
# > 首頁
# 先把我的最愛第一個設定為上課首頁後，我的最愛第一個書籤位置:
_HP_BOOKMARK = (35, 90)
# 首頁登入按鈕: 
_HP_LOGIN_BUTTON = (1056, 140)

# > 登入畫面
# 登入帳號框: 
_LOGIN_ACCOUNT_BOX = (570, 451)
# 登入密碼框: 
_LOGIN_PWD_BOX = (570, 493)
# 驗證碼框:   
_LOGIN_VERIFY_BOX = (570, 566)
_LOGIN_VERIFY_BOX_POINT_A = (_LOGIN_VERIFY_BOX[0] - 100, _LOGIN_VERIFY_BOX[1] - 20)
_LOGIN_VERIFY_BOX_POINT_B = (_LOGIN_VERIFY_BOX[0], _LOGIN_VERIFY_BOX[1] + 10)
# 驗證碼圖左上角: 
_LOGIN_VERIFY_IMG_POINT_A = (710, 539)
# 驗證碼圖右下角: 
_LOGIN_VERIFY_IMG_POINT_B = (805, 571)
# 送出按鈕: 
_LOGIN_COMMIT_BUTTON = (570, 640)
# 登入錯誤訊息左上角: 
_LOGIN_ERROR_MSG_POINT_A = (740, 110)
# 登入錯誤訊息右下角: 
_LOGIN_ERROR_MSG_POINT_B = (930, 140)
# 關閉登入錯誤訊息
_LOGIN_ERROR_CONFIRM = (1130, 160)

# > 上課畫面
# 進入課程前的 上課去 按鈕:
_LEARNING_START_BUTTON = (None)
# 關閉課程分頁按鈕:
_LEARNING_CLOSE_TAB = (None)
# 課程時數狀態左上角: 
_LEARNING_TIMING_POINT_A = (None)
# 課程時數狀態右下角: 
_LEARNING_TIMING_POINT_B = (None)
# 課程時數狀態左上角: 
_LEARNING_STATUS_POINT_A = (None)
# 課程時數狀態右下角: 
_LEARNING_STATUS_POINT_B = (None)
# ******************************************************************

# 帳號與密碼
config = configparser.ConfigParser()    
config.read(_USERS_PATH, encoding="utf-8")
_USERS = list()
for idx in range(4):
    _USERS.append(
        {
            'account': config[f'USER_{idx}']['account'],
            'password': config[f'USER_{idx}']['password']
        }
    )

class Screen():
    def __init__(self, SCREEN_SPLIT, RESOLUTION_X, RESOLUTION_Y) -> None:
        """
        HP: Home Page
        """
        self.SCREEN_SPLIT = SCREEN_SPLIT
        self.RESOLUTION = (RESOLUTION_X, RESOLUTION_Y-_WINDOWS_TASKBAR_h)
        self.HP_BOOKMARK = list()
        self.HP_LOGIN_BUTTON = list()
        self.LOGIN_ACCOUNT_BOX = list()
        self.LOGIN_PWD_BOX = list()
        self.LOGIN_VERIFY_BOX = list()
        self.LOGIN_VERIFY_IMG_POINT_A = list()
        self.LOGIN_VERIFY_IMG_POINT_B = list()
        self.LOGIN_COMMIT_BUTTON = list()
        self.LOGIN_ERROR_MSG_POINT_A = list()
        self.LOGIN_ERROR_MSG_POINT_B = list()
        self.LOGIN_ERROR_CONFIRM = list()
        self.LOGIN_VERIFY_BOX_POINT_A = list()
        self.LOGIN_VERIFY_BOX_POINT_B = list()

        print(' INFO SETUP '.center(100, '='))        
        self.set_windows()
        self.set_HP_info(self.SCREEN_SPLIT)
        self.set_LOGIN_info(self.SCREEN_SPLIT)
        print('=========='.center(100, '='))
        print('↓'.center(100))
        print('↓'.center(100))

    def set_windows(self):
        if self.SCREEN_SPLIT == 1:
            self._WINDOWS = [
                ((0, 0), self.RESOLUTION)
            ]
        elif self.SCREEN_SPLIT == 4:
            res = self.RESOLUTION
            self._WINDOWS = [
                ((0.0, 0.0), (res[0]/2, res[1]/2)),
                ((res[0]/2, 0), (res[0], res[1]/2)),
                ((0, res[1]/2), (res[0]/2, res[1])),
                ((res[0]/2, res[1]/2), (res[0], res[1]))
            ]
        print('Windows Info Set up -> Success!')

    def set_HP_info(self, SCREEN_NO = 1):
        for SCREENS in range(SCREEN_NO):
            point_A = self._WINDOWS[SCREENS][0]
            point_B = self._WINDOWS[SCREENS][1]
            self.HP_BOOKMARK.append((point_A[0] + _HP_BOOKMARK[0], point_A[1] + _HP_BOOKMARK[1]))
            self.HP_LOGIN_BUTTON.append((point_A[0] + (point_B[0] - point_A[0])*_HP_LOGIN_BUTTON[0]/1920, point_A[1] + _HP_LOGIN_BUTTON[1]))
        else:
            print('Home Page Set up -> Success!')

    def set_LOGIN_info(self, SCREEN_NO = 1):
        for SCREENS in range(SCREEN_NO):
            point_A = self._WINDOWS[SCREENS][0]
            point_B = self._WINDOWS[SCREENS][1]
            self.LOGIN_ACCOUNT_BOX.append((point_A[0] + _LOGIN_ACCOUNT_BOX[0], point_A[1] + _LOGIN_ACCOUNT_BOX[1]))
            self.LOGIN_PWD_BOX.append((point_A[0] + _LOGIN_PWD_BOX[0], point_A[1] + _LOGIN_PWD_BOX[1]))
            self.LOGIN_VERIFY_BOX.append((point_A[0] + _LOGIN_VERIFY_BOX[0], point_A[1] + _LOGIN_VERIFY_BOX[1]))
            self.LOGIN_VERIFY_IMG_POINT_A.append((point_A[0] + _LOGIN_VERIFY_IMG_POINT_A[0], point_A[1] + _LOGIN_VERIFY_IMG_POINT_A[1]))
            self.LOGIN_VERIFY_IMG_POINT_B.append((point_A[0] + _LOGIN_VERIFY_IMG_POINT_B[0], point_A[1] + _LOGIN_VERIFY_IMG_POINT_B[1]))
            self.LOGIN_COMMIT_BUTTON.append((point_A[0] + _LOGIN_COMMIT_BUTTON[0], point_A[1] + _LOGIN_COMMIT_BUTTON[1]))
            self.LOGIN_ERROR_MSG_POINT_A.append((point_A[0] + _LOGIN_ERROR_MSG_POINT_A[0], point_A[1] + _LOGIN_ERROR_MSG_POINT_A[1]))
            self.LOGIN_ERROR_MSG_POINT_B.append((point_A[0] + _LOGIN_ERROR_MSG_POINT_B[0], point_A[1] + _LOGIN_ERROR_MSG_POINT_B[1]))
            self.LOGIN_ERROR_CONFIRM.append((point_A[0] + _LOGIN_ERROR_CONFIRM[0], point_A[1] + _LOGIN_ERROR_CONFIRM[1]))
            self.LOGIN_VERIFY_BOX_POINT_A.append((point_A[0] + _LOGIN_VERIFY_BOX_POINT_A[0], point_A[1] + _LOGIN_VERIFY_BOX_POINT_A[1]))
            self.LOGIN_VERIFY_BOX_POINT_B.append((point_A[0] + _LOGIN_VERIFY_BOX_POINT_B[0], point_A[1] + _LOGIN_VERIFY_BOX_POINT_B[1]))
        else:
            print('Login Page Set up -> Success!')

    def show(self):
        ATTRS = vars(self)
        print(' INFOS '.center(100, '='))        
        for attr in ATTRS:
            print(f'{attr} = {ATTRS[attr]}')
        print('======='.center(100, '='))
        print('↓'.center(100))
        print('↓'.center(100))

    def test(self):
        for i in range(self.SCREEN_SPLIT):
            # if i > len(_USERS)-1: continue
            click(self.HP_BOOKMARK[i])
            print(f'點擊書籤按鈕 {i}')
            click(self.HP_LOGIN_BUTTON[i])
            print(f'點擊首頁的登入按鈕 {i}')
            # self.test_click(self.LOGIN_ACCOUNT_BOX[i])
            # pyautogui.press('t')
            # self.test_click(self.LOGIN_PWD_BOX[i])
            # pyautogui.press('t')
            # self.test_click(self.LOGIN_VERIFY_BOX[i])
            # pyautogui.press('t')
            # self.test_click(self.LOGIN_COMMIT_BUTTON[i])

    def test_click(self, location, wait: int = 2):
        pyautogui.click(0, _MAIN_RESOLUTION[1]/2) # Reset
        print(f'Click -> {location[0]} {location[1]}')
        pyautogui.click(*location)
        time.sleep(wait)

    def login(self):
        print(' NAVIGATION '.center(100, '='))        
        for _window in range(self.SCREEN_SPLIT):
            # click(*self.HP_BOOKMARK[_window])
            print(f'PRESS BOOKMARK BUTTON -> {_window}')

        for _window in range(self.SCREEN_SPLIT):
            # click(*self.HP_LOGIN_BUTTON[_window])
            print(f'PRESS LOGIN BUTTON -> {_window}')

        for _window in range(self.SCREEN_SPLIT):
            pass

        print('================'.center(100, '='))
        print('↓'.center(100))
        print('↓'.center(100))
        sys.exit()

SCREENS = Screen(int(sys.argv[1]), _MAIN_RESOLUTION[0], _MAIN_RESOLUTION[1])
SCREENS.show()
SCREENS.login()
# print(f"[*]滑鼠位置: {pyautogui.position()}")

class Task():
    USERS = _USERS
    PNG_NAME = 'verify'
    LOGIN_DONE = list()

    def __init__(self) -> None:
        pass

    def LOGIN(self):
        def type_account_password(idx: str):
            click(SCREENS.LOGIN_ACCOUNT_BOX[idx][0] + 250, SCREENS.LOGIN_ACCOUNT_BOX[idx][1])
            for _ in range(len(_USERS[idx]['account'])):
                pyautogui.press('backspace')
            enter_string(_USERS[idx]['account'])
            click(SCREENS.LOGIN_ACCOUNT_BOX[idx][0], SCREENS.LOGIN_ACCOUNT_BOX[idx][1] - 50)
            time.sleep(0.3)
            click(*SCREENS.LOGIN_PWD_BOX[idx])
            enter_string(_USERS[idx]['password'])
        
        for idx, USER in enumerate(self.USERS):
            is_login  = False
            while not is_login:
            # self.login_process(USER, idx)
                type_account_password(idx)
                self.verify_code_processing(idx)
                is_login = is_verifyCode_correct(
                    './images/' + self.PNG_NAME + f'_{idx}.png',
                    SCREENS.LOGIN_ERROR_MSG_POINT_A[idx],
                    SCREENS.LOGIN_ERROR_MSG_POINT_B[idx]
                )
                if not is_login:
                    click(*SCREENS.LOGIN_ERROR_CONFIRM[idx])
            else:
                is_login = True

    def START_LEARNING(self):
        pass
    
    def verify_code_processing(self, idx):
        is_recognize, text = get_verification(
            save_to = './images/' + self.PNG_NAME + f'_{idx}.png',
            point_A = SCREENS.LOGIN_VERIFY_IMG_POINT_A[idx],
            point_B = SCREENS.LOGIN_VERIFY_IMG_POINT_B[idx]
        )

        print('\n' + '='*100 + '\n')
        print(f'{is_recognize=}\t{text=}')
        print('\n' + '='*100 + '\n')

        # 輸入驗證碼
        _is_type_correct = False
        tries = 0
        MAX_TRIES = 5
        while not _is_type_correct:
            if tries == MAX_TRIES - 1:
                break
            else:
                tries += 1

            click(*SCREENS.LOGIN_VERIFY_BOX[idx])
            for _ in range(10):
                pyautogui.press('backspace')
            enter_string(text)
            time.sleep(0.2)
            _is_type_correct = is_type_correct(
                save_to = './images/' + self.PNG_NAME + f'_{idx}.check.png',
                point_A = SCREENS.LOGIN_VERIFY_BOX_POINT_A[idx],
                point_B = SCREENS.LOGIN_VERIFY_BOX_POINT_B[idx],
                target = text
            )
        input()

        # 登入按鈕
        if input('continue? ') == '':
            pass
        else:
            click(*SCREENS.LOGIN_COMMIT_BUTTON[idx])
        time.sleep(0.5)

    def login_process(self, USER: dict, screen_no: int):
        n = 1
        try_login_times = 1
        while True:
            print(f"[*]第 {n} 次分析驗證碼")
            n += 1
            PNG_NAME = './images/verify.png'
            getPic(save_to=PNG_NAME)

            import cv2 as cv
            src = cv.imread(f'./{PNG_NAME}')
            is_recognize, text = recognize_text(src)

            if not is_recognize:
                pyautogui.click(1596, 842)
                time.sleep(0.5)
                continue
            print(f'[*]第 {try_login_times} 次嘗試登入中 -> 驗證碼: {text}')
            try_login_times += 1

            self.login_TaiwanJobs(
                account=USER['account'],
                password=USER['password'],
                verifyCode=text,
                screen_no=screen_no
            )

            time.sleep(1.5)

            if is_verifyCode_correct():
                break    
    
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

        time.sleep(sleep_time)
        pyautogui.click(1157, 954)




TASK = Task()
TASK.LOGIN()


def click_1(sleep: int = 2):
    print('[*]滑鼠點擊 上!')
    pyautogui.click(200, 1300)
    time.sleep(sleep)


def click_2(sleep: int = 2):
    print('[*]滑鼠點擊 下!')  
    pyautogui.click(200, 1450)
    time.sleep(sleep)


def getPic_readTime():
    im = ImageGrab.grab(
        bbox=(
            616, 297,
            700, 322
        )
    ) 

    # 儲存檔案
    im.save("readTime.jpg")


def getPic_sectionProgress():
    im = ImageGrab.grab(
        bbox=(
            614, 330,
            700, 356
        )
    ) 

    # 儲存檔案
    im.save("sectionProgress.jpg")


def getPic_className():
    im = ImageGrab.grab(
        bbox=(
            384, 247,
            986, 287
        )
    ) 

    # 儲存檔案
    im.save("className.jpg")


def main(closeTime: int):
    global clickTimes

    enddingTime = datetime.datetime.now()
    getPic_className()  
    img = Image.open('className.jpg')
    className = pytesseract.image_to_string(img, lang='chi_tra').replace(' ', '').replace('\n', '')
    clickTimes=0

    while True:
        now = datetime.datetime.now()
        if target_enddingTime < now:
            sys.exit()

        if (now - enddingTime).seconds == closeTime*60:
            print("[*]已達到表定之課程時間 !")
            return
        else:
            print(f"[*]距離表定之課程時間還有: {(now - enddingTime).seconds} 秒 ! ")

        print(f"\n[*]目前時間: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f'[*]目前閱讀之課程名稱: {className}')

        print("[>]正在獲取閱讀時數狀態")
        getPic_readTime()

        fileName = 'readTime.jpg'
        print(f"[*]狀態已儲存至 -> {fileName}")
        img = Image.open(fileName)

        print("[>]啟動文字辨識引擎")
        text = pytesseract.image_to_string(img, lang='chi_tra').replace(' ', '').replace('\n', '')

        print(f"[*]文字辨識結果: {text}")

        if '已達成' in text:
            print('[*]閱讀時數目標達成 ! ')
            return

        if '達成' not in text:
            pyautogui.click(200, 1300)
        
        click_1()
        click_2()
        clickTimes += 2
        print(f'[*]目前為止已點擊: {clickTimes} 下')

        clickStep = random.randint(20, 40)
        try:
            for seconds in range(1, clickStep):
                print(f"[*]距離下次點擊還有 {clickStep - seconds: 2d} 秒\r", end="")
                sys.stdout.flush()
                time.sleep(1)
        except KeyboardInterrupt:
            while True:
                todo = input('[?]跳過(1)或結束程式(2): ')
                if todo == '1':
                    break
                elif todo == '2':
                    sys.exit()
                else:
                    print('[!}請重新輸入...')
    

def click_sections(closeTime):
    x = 495
    y = 420
    # 調整切換章節速度，使軟體行為更像真人
    timeStep = [random.randint(5, 10) for _ in range(2)] + [random.randint(150, 250 + 5*x) for x in range(1, 15)]*10
    enddingTime = datetime.datetime.now()
    click_delta_y = 40

    for idx, step in enumerate(timeStep):
        if target_enddingTime < datetime.datetime.now():
            sys.exit()
            
        print(f"[*]正在點選章節標題: {y=: 4d}")
        pyautogui.click(200, 1300)
        pyautogui.click(x, y)

        if if_read_progess_done():
            return 'READ_PROGESS_DONE'

        if y >= 1950:
            pyautogui.scroll(-1000)
            y = 1980
            click_delta_y = -40

        if waiting_for_next_click(step, enddingTime, closeTime) == 'TIMES_UP':
            return 'TIMES_UP'

        y += click_delta_y
    else:
        return 'ALL_WORKS_DONE'


def refresh_page():
    pyautogui.click(200, 1300)
    pyautogui.click(183, 81)


def if_read_progess_done():
    getPic_sectionProgress()
    img = Image.open('sectionProgress.jpg')

    print("[>]啟動文字辨識引擎")
    text = pytesseract.image_to_string(img, lang='chi_tra').replace(' ', '').replace('\n', '')

    print(f"[*]文字辨識結果: {text}")

    if '已' in text:
        print('[*]達成章節閱讀目標 ! ')
        return True
    else:
        print('[*]尚未達成章節閱讀目標 ! ')
        return False


def waiting_for_next_click(step, enddingTime, closeTime):
    try:
        for t in range(1, step):
            now = datetime.datetime.now()
            if (now - enddingTime).seconds == closeTime*60:
                print("[*]已達到表定之課程時間 ! ")
                return 'TIMES_UP'
            print(f"[*]距離下次點擊章節標題還有 {step - t: 2d} 秒\r", end="")
            time.sleep(1)
            sys.stdout.flush()
    except KeyboardInterrupt:
        while True:
            todo = input('[?]跳過(1)或結束程式(2): ')
            if todo == '1':
                break
            elif todo == '2':
                sys.exit()
            else:
                print('[!}請重新輸入...')


def print_waiting(text, waitTime):
    for t in range(1, waitTime+1):
        print(f"{text}...({t}/{waitTime})\r", end='')
        time.sleep(1)
        sys.stdout.flush()
    else:
        print('[*]')


def check_pos():
    print(f"[*]解析度: {pyautogui.size()}")
    print(f"[*]滑鼠位置: {pyautogui.position()}")

def study():
    clickTimes = 0
    program_startTime = datetime.datetime.now()
    global target_enddingTime

    while True:
        is_registration = input('[?]是否已前往「補助企業辦理訓練資訊系統」完成登錄上課資訊(y/n)? ')
        if is_registration in ('y', 'Y'):
            break
        elif is_registration in ('n', 'N'):
            print('[!]請先前往登記，系統將自動開啟登入系統。')
            webbrowser.open_new('https://onjobtraining.wda.gov.tw/WDATraining')
            continue

    studyDate = '2022-01-30'
    try:
        # target = datetime.datetime.strptime(studyDate + ' 13:30:00', '%Y-%m-%d %H:%M:%S')   
        target = datetime.datetime.strptime(studyDate + ' 08:00:00', '%Y-%m-%d %H:%M:%S')    
        target_enddingTime = datetime.datetime.strptime(studyDate + ' 16:30:00', '%Y-%m-%d %H:%M:%S')
        # target_enddingTime = datetime.datetime.strptime(studyDate + ' 19:05:00', '%Y-%m-%d %H:%M:%S')
    except ValueError as f:
        print('[!]時間格式設定錯誤')
        print('[!]\t->' + str(f))
        sys.exit()

     # 課程時數表
    # 結構: {classCode: classTime}
    classInfo = {
        # CLSS_TO_ADD
    }
    urlBase = 'https://portal.wda.gov.tw/info/' 

    print(f"[!]已設定開始時間，正在等待開始...")
    mins = sum([t for t in classInfo.values()])
    print(f'[*]本次預計時數: {mins} mins -> {mins//60} hrs {mins - mins//60*60} mins')
    print(f'[*]本次上課之課程代碼: {list(classInfo.keys())}')
    while True:    
        sys.stdout.flush()
        if target < datetime.datetime.now():
            print('[!]已達指定開始時間，程式開始運行 !')
            click2_and_sleep((2820, 125), 0.1)
            print_waiting('[*]正在重新整理', 3)
            pyautogui.click(2067, 188)
            print_waiting('[*]正在開啟登入畫面', 3)
            try:
                login_process()
            except KeyboardInterrupt:
                input('[*]請手動登入完成後按下Enter')
            print_waiting('[*]等待登入過程載入', 5)
            break
        now = datetime.datetime.now()
        timeDelta = target - datetime.datetime.now()
        print(f"[*]現在時間: {now.strftime('%H:%M:%S')}\t距離程式開始還有: {timeDelta}\r", end='')
        time.sleep(1)   
    
    try:
        class_startTime = datetime.datetime.now()
        while True:
            for classCode, classTime in classInfo.items():
                webbrowser.open_new(urlBase + str(classCode))

                print_waiting('[*]等待上課去頁面載入', 5)
                # 點選"上課去"
                pyautogui.click(2042, 1150)

                # 等待課程頁面載入
                print_waiting('[*]等待課程頁面載入', 10)

                # 把章節主題點一點
                resp = click_sections(closeTime = classTime)
                if resp != 'TIMES_UP':
                    main(closeTime = classTime)
                # print_waiting('[*]模擬上課過程', 5)

                # 關掉當前分頁 防止系統偵測到同時兩個視窗
                pyautogui.click(764, 24)
                print("[!]關閉分頁")

            if target_enddingTime < datetime.datetime.now():
                sys.exit()
            else:
                print('[!]尚未達到預設之程式結束時間，將持續進行至設定之程式結束時間到達 ! ')
    except SystemExit:
        print('[*]已達設定之結束時間 !')
    finally:
        print('[*]' + '程式執行紀錄'.center(50, '='))
        print(f'[*]總執行時間: {datetime.datetime.now() - program_startTime} ')
        print(f'[*]總上課時間: {datetime.datetime.now() - class_startTime} ')
        print(f'[*]共上了: {len(classInfo)} 堂課')
        for classCode, classTime in classInfo.items():
            print(f'[*]\t課程代碼: {classCode} -> {classTime} 分鐘')
        print(f'[*]總閱讀時數: {sum((t for t in classInfo.values()))} ')
        print(f'[*]一共點擊了: {clickTimes} 下')
        print('[*]' + ''.center(50, '='))
        print('[!]提醒: 記得前往網站回報課程進度 !')
        print('[*]程式結束...')


if __name__ == '__main__TEST':
    while True:
        print('[*]' + f"線上課程自動掛機外掛".center(50, '='))
        print('[*]' + f"版本號: {version}".center(50))
        print('[*]' + ''.center(50, '='))
        print('[*]' + '\t1. 開始上課')
        print('[*]' + '\t2. 讀取滑鼠位置')
        print('[*]' + '\te. 結束程式')
        print('[*]' + ''.center(50, '='))
        func_Choose = input('[?]請選取要執行的功能? ')

        if func_Choose == 'e':
            break

        if func_Choose not in ('1', '2'):
            print('[!]請輸入正確的編號...')
            continue

        if func_Choose == '1':
            study()
            break
        elif func_Choose == '2':
            check_pos()

    print('[*]程式結束...')