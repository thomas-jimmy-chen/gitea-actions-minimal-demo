from os.path import isfile, isdir
from os import mkdir

def check_argv(sys_argv: list, _SCREEN_SPLIT: list):
    msg = f'ERROR: TYPE IN THE AMOUNT OF SCREENS AFTER THE COMMAND, ALLOWS: {_SCREEN_SPLIT}'
    def _return(msg):
        msg += f'\n>>>> For example: python main.py 4'
        raise Exception(msg)

    if len(sys_argv) == 1:
        _return(msg)

    if int(sys_argv[1]) not in _SCREEN_SPLIT:
        msg += f'\nERROR: num_of_screen_split = {sys_argv[1]} is not allowed.'
        _return(msg)

def check_images_folder(_IMAGE_PATH: str):
    if not isdir(_IMAGE_PATH):
        print(f'ERROR: Path: {_IMAGE_PATH} is not found')
        mkdir(_IMAGE_PATH)
        print(f'>>>> Path: {_IMAGE_PATH} has been created automatic')
    
    print('check_images_folder -> SUCCESS')

def check_users_file(_USERS_PATH):
    if not bool(isfile(_USERS_PATH)):
        print(f'ERROR: File: {_USERS_PATH} is not found !')
        with open(_USERS_PATH, 'w') as f:
            for idx in range(4):
                f.write(f'[USER_{idx}]\n')
                f.write('account = \n')
                f.write('password = \n\n')
        msg = f'File: {_USERS_PATH} has been created automatic.'
        msg += f'\n>>>> Complete the {_USERS_PATH} before run this program.'
        raise Exception(msg)
    else:
        print('check_users_file -> SUCCESS')

def check_pytesseract(tesseract_cmd_path):
    if bool(isfile(tesseract_cmd_path)):
        print('check_pytesseract -> SUCCESS')
        return
        
    msg = f'ERROR: {tesseract_cmd_path} is not found'
    msg += f'\n>>>> Please refer to: https://github.com/UB-Mannheim/tesseract/wiki'
    raise Exception(msg)