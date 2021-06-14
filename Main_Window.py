import numpy as np
from PIL import Image, ImageQt
from os import path as OS_path
from os import walk as OS_walk
from os import makedirs as OS_makedirs
from sys import argv as SYS_argv
from sys import exit as SYS_exit
from re import search as RE_search
from copy import deepcopy as COPY_deepcopy
from threading import Thread as THREADING_Thread

from Main_Window_UI import Ui_Main_Window_UI

from PyQt5.Qt import QPoint
from PyQt5.QtGui import QPixmap, QIntValidator
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QWidget



ZOOM_LIMIT = 80
CLEAN_LIMIT = 1
BACKUP_LIMIT = 2000
DRAW_INTERVAL = 3000
DRAW_INTERVAL_CLEAN = 5



class Functional_Arithmetic:
    def __init__(self, main_window):
        self.main_window = main_window
        pass

    def Cutout_image(self, x0, y0, mode):
        # 0:由鼠标唤起
        # 1~4:由半自动唤起
        # 5~8:由全自动唤起
        if mode == 0:
            self.system_state.System_busy()
        elif mode == 1:
            x0 = 0
            y0 = 0
        elif mode == 2:
            x0 = 0
            y0 = self.image_label.current_image_image.size[1] - 1
        elif mode == 3:
            x0 = self.image_label.current_image_image.size[0] - 1
            y0 = 0
        elif mode == 4:
            x0 = self.image_label.current_image_image.size[0] - 1
            y0 = self.image_label.current_image_image.size[1] - 1
        elif mode == 5:
            x0 = 0
            y0 = 0
        elif mode == 6:
            x0 = 0
            y0 = self.image_label.current_image_image.size[1] - 1
        elif mode == 7:
            x0 = self.image_label.current_image_image.size[0] - 1
            y0 = 0
        elif mode == 8:
            x0 = self.image_label.current_image_image.size[0] - 1
            y0 = self.image_label.current_image_image.size[1] - 1

        self.system_state.current_image_edited = True
        color = np.array(self.color_label.color)
        color[3] = 255
        tolerance = self.all_bottons.tolerance
        transparent = np.array([0, 0, 0, 0])

        if self.image_label.current_image_array[y0, x0][3] != 0:
            stack = list()
            stack.append((x0, y0))
            self.image_label.current_image_array[y0, x0] = transparent

            count = 0
            while True:
                if len(stack) == 0:
                    break

                x, y = stack.pop()

                if count == 0:
                    if self.system_state.tomede:
                        self.backup_mod.Revoke_backup()
                        self.system_state.System_free()
                        return
                    else:
                        self.image_label.current_image_image = Image.fromarray(np.array(self.image_label.current_image_array, dtype='uint8'))
                        self.image_label.Draw_image_label()
                    count = 1

                if x + 1 < self.image_label.current_image_image.size[0] \
                and all(abs(self.image_label.current_image_array[y, x + 1] - color) <= tolerance) \
                and self.image_label.current_image_array[y, x + 1][3] != 0:
                    stack.append((x + 1, y))
                    self.image_label.current_image_array[y,x + 1] = transparent

                if x - 1 >= 0 \
                and all(abs(self.image_label.current_image_array[y, x - 1] - color) <= tolerance) \
                and self.image_label.current_image_array[y, x - 1][3] != 0:
                    stack.append((x - 1, y))
                    self.image_label.current_image_array[y,x - 1] = transparent

                if y + 1 < self.image_label.current_image_image.size[1] \
                and all(abs(self.image_label.current_image_array[y + 1, x] - color) <= tolerance) \
                and self.image_label.current_image_array[y + 1, x][3] != 0:
                    stack.append((x, y + 1))
                    self.image_label.current_image_array[y +1, x] = transparent

                if y - 1 >= 0 \
                and all(abs(self.image_label.current_image_array[y - 1, x] - color) <= tolerance) \
                and self.image_label.current_image_array[y - 1, x][3] != 0:
                    stack.append((x, y - 1))
                    self.image_label.current_image_array[y -1, x] = transparent

                count = count + 1 if count < DRAW_INTERVAL else 0

            self.image_label.current_image_image = Image.fromarray(np.array(self.image_label.current_image_array, dtype='uint8'))
            self.image_label.Draw_image_label()

        if mode == 0:
            self.backup_mod.Insert_backup()
            self.system_state.System_free()

        elif mode == 1:
            t = THREADING_Thread(target=self.functional_arithmetic.Cutout_image, args=(0, 0, 2,))
            t.start()
        elif mode == 2:
            t = THREADING_Thread(target=self.functional_arithmetic.Cutout_image, args=(0, 0, 3,))
            t.start()
        elif mode == 3:
            t = THREADING_Thread(target=self.functional_arithmetic.Cutout_image, args=(0, 0, 4,))
            t.start()
        elif mode == 4:
            t = THREADING_Thread(target=self.functional_arithmetic.Clean_image, args=(4,))
            t.start()

        elif mode == 5:
            t = THREADING_Thread(target=self.functional_arithmetic.Cutout_image, args=(0, 0, 6,))
            t.start()
        elif mode == 6:
            t = THREADING_Thread(target=self.functional_arithmetic.Cutout_image, args=(0, 0, 7,))
            t.start()
        elif mode == 7:
            t = THREADING_Thread(target=self.functional_arithmetic.Cutout_image, args=(0, 0, 8,))
            t.start()
        elif mode == 8:
            t = THREADING_Thread(target=self.functional_arithmetic.Clean_image, args=(8,))
            t.start()

    def Pick_color(self, x0, y0):
        self.color_label.color = list(self.image_label.current_image_array[y0, x0])
        self.main_window.R_LineEdit.setText(str(self.color_label.color[0]))
        self.main_window.G_LineEdit.setText(str(self.color_label.color[1]))
        self.main_window.B_LineEdit.setText(str(self.color_label.color[2]))
        self.main_window.A_LineEdit.setText(str(self.color_label.color[3]))

    def Coloring_image(self, x0, y0):
        self.system_state.current_image_edited = True

        radius = (self.all_bottons.brush_size // 2) ** 2

        coloring_area = [(i, j) for i in range(x0 - self.all_bottons.brush_size // 2, x0 + self.all_bottons.brush_size // 2 + 1)
                        for j in range(y0 - self.all_bottons.brush_size // 2, y0 + self.all_bottons.brush_size // 2 + 1)
                        if abs((i - x0)) ** 2 + abs((j - y0)) ** 2 <= radius
                        and 0 <= i and i < self.image_label.current_image_image.size[0]
                        and 0 <= j and j < self.image_label.current_image_image.size[1]]

        color = np.array(self.color_label.color)

        for point in coloring_area:
            self.image_label.current_image_array[point[1], point[0]] = color

        self.image_label.current_image_image = Image.fromarray(np.array(self.image_label.current_image_array, dtype='uint8'))
        self.image_label.Draw_image_label()

    def Filling_image(self, x0, y0):
        self.system_state.System_busy()

        self.system_state.current_image_edited = True
        initial_color = self.image_label.current_image_array[y0, x0].copy()
        tolerance = self.all_bottons.tolerance

        color = np.array(self.color_label.color)
        stack = list()
        stack.append((x0, y0))
        self.image_label.current_image_array[y0, x0] = color

        count = 1
        while True:
            if len(stack) == 0:
                break

            x, y = stack.pop()

            if count == 0:
                if self.system_state.tomede:
                    self.backup_mod.Revoke_backup()
                    self.system_state.System_free()
                    return
                else:
                    self.image_label.current_image_image = Image.fromarray(np.array(self.image_label.current_image_array, dtype='uint8'))
                    self.image_label.Draw_image_label()
                count = 1

            if x + 1 < self.image_label.current_image_image.size[0] \
            and all(abs(self.image_label.current_image_array[y, x + 1] - initial_color) <= tolerance) \
            and any(self.image_label.current_image_array[y, x + 1] != color):
                stack.append((x + 1, y))
                self.image_label.current_image_array[y, x + 1] = color

            if x - 1 >= 0 \
            and all(abs(self.image_label.current_image_array[y, x - 1] - initial_color) <= tolerance) \
            and any(self.image_label.current_image_array[y, x - 1] != color):
                stack.append((x - 1, y))
                self.image_label.current_image_array[y, x - 1] = color

            if y + 1 < self.image_label.current_image_image.size[1] \
            and all(abs(self.image_label.current_image_array[y + 1, x] - initial_color) <= tolerance) \
            and any(self.image_label.current_image_array[y + 1, x] != color):
                stack.append((x, y + 1))
                self.image_label.current_image_array[y + 1, x] = color

            if y - 1 >= 0 \
            and all(abs(self.image_label.current_image_array[y - 1, x] - initial_color) <= tolerance) \
            and any(self.image_label.current_image_array[y - 1, x] != color):
                stack.append((x, y - 1))
                self.image_label.current_image_array[y - 1, x] = color

            count = count + 1 if count < DRAW_INTERVAL else 0

        self.image_label.current_image_image = Image.fromarray(np.array(self.image_label.current_image_array, dtype='uint8'))
        self.image_label.Draw_image_label()
        self.backup_mod.Insert_backup()
        self.system_state.System_free()

    def Crop_image(self, mode):
        # 0:由按钮唤起
        # 1~4:由半自动唤起
        # 5~8:由全自动唤起
        # 9  :由半自动clean_image唤起
        # 10 :由全自动clean_image唤起

        if mode == 0:
            self.system_state.System_busy()
            color = np.array([0, 0, 0, 0])
        elif mode == 1 or mode == 5:
            color = np.array(self.color_label.color)
        elif mode == 9 or mode == 10:
            color = np.array([0, 0, 0, 0])

        self.system_state.current_image_edited = True
        tolerance = self.all_bottons.tolerance

        left, upper, right, lower = 0, 0, 0, 0

        flag = 0
        for x in range(self.image_label.current_image_image.size[0]):
            for y in range(self.image_label.current_image_image.size[1]):
                if not all(abs(self.image_label.current_image_array[y, x] - color) <= tolerance):
                    left = x
                    flag = 1
                    break
            if flag == 1:
                break

        flag = 0
        for y in range(self.image_label.current_image_image.size[1]):
            for x in range(self.image_label.current_image_image.size[0]):
                if not all(abs(self.image_label.current_image_array[y, x] - color) <= tolerance):
                    upper = y
                    flag = 1
                    break
            if flag == 1:
                break

        if self.system_state.tomede:
            self.backup_mod.Revoke_backup()
            self.system_state.System_free()
            return

        flag = 0
        for x in range(self.image_label.current_image_image.size[0] - 1, -1, -1):
            for y in range(self.image_label.current_image_image.size[1]):
                if not all(abs(self.image_label.current_image_array[y, x] - color) <= tolerance):
                    right = x
                    flag = 1
                    break
            if flag == 1:
                break

        flag = 0
        for y in range(self.image_label.current_image_image.size[1] - 1, -1, -1):
            for x in range(self.image_label.current_image_image.size[0]):
                if not all(abs(self.image_label.current_image_array[y, x] - color) <= tolerance):
                    lower = y
                    flag = 1
                    break
            if flag == 1:
                break

        if self.system_state.tomede:
            self.backup_mod.Revoke_backup()
            self.system_state.System_free()
            return

        self.image_label.current_image_image = self.image_label.current_image_image.crop((left, upper, right + 1, lower + 1))
        self.image_label.current_image_array = np.array(self.image_label.current_image_image, dtype='int')

        self.image_label.Set_scrollbar_value(0, 0)
        self.image_label.Draw_image_label()

        if mode == 0:
            self.backup_mod.Insert_backup()
            self.system_state.System_free()

        elif mode == 1:
            t = THREADING_Thread(target=self.functional_arithmetic.Cutout_image, args=(0, 0, 1,))
            t.start()

        elif mode == 5:
            t = THREADING_Thread(target=self.functional_arithmetic.Cutout_image, args=(0, 0, 5,))
            t.start()

        elif mode == 9:
            self.backup_mod.Insert_backup()
            self.system_state.System_free()

        elif mode == 10:
            if self.system_state.image_index == len(self.system_state.images) - 1:
                self.functional_arithmetic.Save_image()
                self.system_state.System_free()
            else:
                self.all_bottons.On_next_button_clicked()
                t = THREADING_Thread(target=self.functional_arithmetic.Auto_pick_color, args=(5,))
                t.start()

    def Clean_image(self, mode):
        # 0:由按钮唤起
        # 1~4:由半自动唤起
        # 5~8:由全自动唤起
        if mode == 0:
            self.system_state.System_busy()
        elif mode == 4:
            pass
        elif mode == 8:
            pass

        self.system_state.current_image_edited = True
        transparent = np.array([0, 0, 0, 0])
        pixels_transparency = self.image_label.current_image_array[:, :, 3:].copy()

        stack = list()
        block_list = list()

        flag = 0
        for j in range(self.image_label.current_image_image.size[1]):
            for i in range(self.image_label.current_image_image.size[0]):
                if pixels_transparency[j, i] != 0:
                    x, y = i, j
                    flag = 1
                    break
            if flag == 1:
                break

        count = 1
        array0 = np.array([0])
        while not np.all(pixels_transparency == array0):
            if count == 0:
                if self.system_state.tomede:
                    self.backup_mod.Revoke_backup()
                    self.system_state.System_free()
                    return
                else:
                    self.image_label.current_image_image = Image.fromarray(np.array(self.image_label.current_image_array, dtype='uint8'))
                    self.image_label.Draw_image_label()

                count = 1

            stack = [(x, y)]
            block_list = [(x, y)]
            current_point_backup = (x, y)
            pixels_transparency[y, x] = 0

            while True:
                if len(stack) == 0:
                    break

                if self.system_state.tomede:
                    self.backup_mod.Revoke_backup()
                    self.system_state.System_free()
                    return

                x, y = stack.pop()

                if x + 1 < self.image_label.current_image_image.size[0] \
                and pixels_transparency[y, x + 1] != 0:
                    stack.append((x + 1, y))
                    pixels_transparency[y, x + 1] = 0
                    block_list.append((x + 1, y))

                if x - 1 >= 0 \
                and pixels_transparency[y, x - 1] != 0:
                    stack.append((x - 1, y))
                    pixels_transparency[y, x - 1] = 0
                    block_list.append((x - 1, y))

                if y + 1 < self.image_label.current_image_image.size[1] \
                and pixels_transparency[y + 1, x] != 0:
                    stack.append((x, y + 1))
                    pixels_transparency[y + 1, x] = 0
                    block_list.append((x, y + 1))

                if y - 1 >= 0 \
                and pixels_transparency[y - 1, x] != 0:
                    stack.append((x, y - 1))
                    pixels_transparency[y - 1, x] = 0
                    block_list.append((x, y - 1))

            if len(block_list) <= CLEAN_LIMIT:
                for x, y in block_list:
                    self.image_label.current_image_array[y, x] = transparent

            x, y = current_point_backup
            flag = 0
            while y < self.image_label.current_image_image.size[1]:
                if self.system_state.tomede:
                    self.backup_mod.Revoke_backup()
                    self.system_state.System_free()
                    return

                while x < self.image_label.current_image_image.size[0]:
                    if pixels_transparency[y, x] != 0:
                        flag = 1
                        break
                    elif x < self.image_label.current_image_image.size[0] - 1:
                        x += 1
                    elif x == self.image_label.current_image_image.size[0] - 1:
                        x = 0
                        y += 1
                        if y == self.image_label.current_image_image.size[1]:
                            break

                if flag == 1:
                    break

            count = count + 1 if count < DRAW_INTERVAL_CLEAN else 0

        self.image_label.current_image_image = Image.fromarray(np.array(self.image_label.current_image_array, dtype='uint8'))
        self.image_label.Draw_image_label()

        if mode == 0:
            self.backup_mod.Insert_backup()
            self.system_state.System_free()

        elif mode == 4:
            t = THREADING_Thread(target=self.functional_arithmetic.Crop_image, args=(9,))
            t.start()

        elif mode == 8:
            t = THREADING_Thread(target=self.functional_arithmetic.Crop_image, args=(10,))
            t.start()

    def Image_binarization(self):
        self.system_state.System_busy()

        black = np.array([0, 0, 0, 255])
        white = np.array([255, 255, 255, 255])

        for y in range(self.image_label.current_image_image.size[1]):
            for x in range(self.image_label.current_image_image.size[0]):
                self.image_label.current_image_array[y,x] = white if self.image_label.current_image_array[y, x][3] == 0 else black

        self.image_label.current_image_image = Image.fromarray(np.array(self.image_label.current_image_array, dtype='uint8'))
        self.image_label.Draw_image_label()

        self.backup_mod.Insert_backup()
        self.system_state.System_free()

    def Auto_pick_color(self, mode):
        # 0:由系统唤起
        # 1~4:由半自动唤起
        # 5~8:由全自动唤起
        if mode == 0:
            pass
        elif mode == 1:
            self.system_state.System_busy()
        elif mode == 5:
            self.system_state.System_busy()

        colors = {}

        y1 = 0
        y2 = self.image_label.current_image_image.size[1] - 1
        for x in range(self.image_label.current_image_image.size[0]):
            if tuple(self.image_label.current_image_array[y1, x]) in colors:
                colors[tuple(self.image_label.current_image_array[y1, x])] += 1
            else:
                colors[tuple(self.image_label.current_image_array[y1, x])] = 1

            if tuple(self.image_label.current_image_array[y2, x]) in colors:
                colors[tuple(self.image_label.current_image_array[y2, x])] += 1
            else:
                colors[tuple(self.image_label.current_image_array[y2, x])] = 1

        x1 = 0
        x2 = self.image_label.current_image_image.size[0] - 1
        for y in range(1, self.image_label.current_image_image.size[1] - 1):
            if tuple(self.image_label.current_image_array[y, x1]) in colors:
                colors[tuple(self.image_label.current_image_array[y, x1])] += 1
            else:
                colors[tuple(self.image_label.current_image_array[y, x1])] = 1

            if tuple(self.image_label.current_image_array[y, x2]) in colors:
                colors[tuple(self.image_label.current_image_array[y, x2])] += 1
            else:
                colors[tuple(self.image_label.current_image_array[y, x2])] = 1

        max_count = max(colors.values())
        for k, v in colors.items():
            if v == max_count:
                color = k
                break

        self.main_window.R_LineEdit.setText(str(color[0]))
        self.main_window.G_LineEdit.setText(str(color[1]))
        self.main_window.B_LineEdit.setText(str(color[2]))
        self.main_window.A_LineEdit.setText(str(color[3]))

        if mode == 1:
            t = THREADING_Thread(target=self.functional_arithmetic.Crop_image, args=(1,))
            t.start()

        elif mode == 5:
            t = THREADING_Thread(target=self.functional_arithmetic.Crop_image, args=(5,))
            t.start()

    def Save_image(self):
        if self.system_state.image_loaded:
            if not OS_path.isdir("done"):
                OS_makedirs("done")

            self.system_state.images[self.system_state.image_index] = self.image_label.current_image_image.copy()
            file_name_index = len(self.system_state.file_names[self.system_state.image_index]) - self.system_state.file_names[self.system_state.image_index][::-1].find('.')
            self.image_label.current_image_image.save('done/' + self.system_state.file_names[self.system_state.image_index][:file_name_index] + 'png')

    def Import_path(self, path):
        if self.system_state.current_image_edited:
            self.functional_arithmetic.Save_image()

        images_backup = COPY_deepcopy(self.system_state.images)
        image_index_backup = self.system_state.image_index
        file_names_backup = COPY_deepcopy(self.system_state.file_names)

        self.system_state.images = ['']
        self.system_state.image_index = 1
        self.system_state.file_names = ['']

        for root, dir, filelist in OS_walk(path):
            for file in filelist:
                if RE_search('(jpg|jpeg|png|webp|bmp|tif|tga|JPG|JPEG|PNG|WEBP|BMP|TIF|TGA)$', file):
                    self.system_state.images.append(Image.open(root + '/' + file))
                    self.system_state.file_names.append(file)
            break

        if len(self.system_state.images) <= 1:
            QMessageBox.question(self.main_window, '这个目录里没有图片','小老弟你怎么回事？', QMessageBox.Yes)
            self.system_state.images = images_backup
            self.system_state.image_index = image_index_backup
            self.system_state.file_names = file_names_backup
            return

        self.image_label.current_image_image = self.system_state.images[self.system_state.image_index].convert('RGBA')
        self.image_label.current_image_array = np.array(self.image_label.current_image_image, dtype='int')

        self.image_label.zoom = 1
        self.system_state.image_loaded = True
        self.system_state.current_image_edited = False

        self.image_label.Set_scrollbar_value(0, 0)
        self.image_label.Set_scrollbar_display()

        self.backup_mod.backups = [self.image_label.current_image_image.copy()]
        self.backup_mod.backup_pin = 0

        self.image_label.Set_image_background()
        self.image_label.Draw_image_label()
        self.system_state.Update_image_count()

    def Import_image(self, path_list):
        if self.system_state.current_image_edited:
            self.functional_arithmetic.Save_image()

        self.system_state.images = ['']
        self.system_state.image_index = 1
        self.system_state.file_names = ['']

        for path in path_list:
            self.system_state.images.append(Image.open(path))
            self.system_state.file_names.append(path[(len(path) - path[::-1].find('/')):])

        self.image_label.current_image_image = self.system_state.images[self.system_state.image_index].convert('RGBA')
        self.image_label.current_image_array = np.array(self.image_label.current_image_image, dtype='int')

        self.image_label.zoom = 1
        self.system_state.image_loaded = True
        self.system_state.current_image_edited = False

        self.image_label.Set_scrollbar_value(0, 0)
        self.image_label.Set_scrollbar_display()

        self.backup_mod.backups = [self.image_label.current_image_image.copy()]
        self.backup_mod.backup_pin = 0

        self.image_label.Set_image_background()
        self.image_label.Draw_image_label()
        self.system_state.Update_image_count()



class Backup_Mod:
    def __init__(self, main_window):
        self.main_window = main_window

        self.backups = []
        self.backup_pin = 0

    def Insert_backup(self):
        self.main_window.Working_Status_Label.setText('')
        if self.backup_mod.backup_pin != len(self.backups) - 1:
            for i in range(self.backup_mod.backup_pin + 1, len(self.backups)):
                self.backups.pop()

            self.backups.append(self.image_label.current_image_image.copy())
            self.backup_mod.backup_pin += 1

        else:
            if len(self.backups) < BACKUP_LIMIT:
                self.backups.append(self.image_label.current_image_image.copy())
                self.backup_mod.backup_pin += 1
            else:
                self.backups.pop(0)
                self.backups.append(self.image_label.current_image_image.copy())

    def Revoke_backup(self):
        if self.system_state.image_loaded:
            if self.system_state.tomede:
                self.main_window.Working_Status_Label.setText('')
                self.image_label.current_image_image = self.backups[self.backup_mod.backup_pin].copy()
                self.image_label.current_image_array = np.array(self.image_label.current_image_image, dtype='int')
                self.image_label.Draw_image_label()

            elif self.backup_mod.backup_pin > 0:
                self.main_window.Working_Status_Label.setText('')
                self.image_label.current_image_image = self.backups[self.backup_mod.backup_pin - 1].copy()
                self.image_label.current_image_array = np.array(self.image_label.current_image_image, dtype='int')
                self.backup_mod.backup_pin -= 1
                self.image_label.Draw_image_label()

            elif self.backup_mod.backup_pin == 0:
                self.main_window.Working_Status_Label.setText('已经没有备份了')

    def Redo_backup(self):
        if self.system_state.image_loaded:
            if self.backup_mod.backup_pin != len(self.backups) - 1:
                self.main_window.Working_Status_Label.setText('')
                self.image_label.current_image_image = self.backups[self.backup_mod.backup_pin + 1].copy()
                self.image_label.current_image_array = np.array(self.image_label.current_image_image, dtype='int')
                self.backup_mod.backup_pin += 1
                self.image_label.Draw_image_label()

            else:
                self.main_window.Working_Status_Label.setText('已经没有备份了')



class System_State(QObject):
    start_timer = pyqtSignal()
    end_timer = pyqtSignal()

    def __init__(self, main_window):
        self.main_window = main_window
        QObject.__init__(self)

        self.tomede = False
        self.UIloaded = False
        self.system_busy = False
        self.image_loaded = False
        self.current_image_edited = False
        self.images = ['']
        self.file_names = ['']
        self.image_index = 1
        self.working_status_pin = 0
        self.working_status_text = ['少女祈祷中', '少女祈祷中.', '少女祈祷中..', '少女祈祷中...']

        self.timer = QTimer()
        self.timer.timeout.connect(self.Update_working_status)
        self.start_timer.connect(self.Start_timer)
        self.end_timer.connect(self.End_timer)

    def System_busy(self):
        self.system_state.tomede = False
        self.system_state.system_busy = True
        self.system_state.Update_working_status()
        self.system_state.start_timer.emit()

        if self.main_window.Cutout_RadioB.isChecked():
            self.all_bottons.radio_button_state = 1
        elif self.main_window.PickColor_RadioB.isChecked():
            self.all_bottons.radio_button_state = 2
        elif self.main_window.Coloring_RadioB.isChecked():
            self.all_bottons.radio_button_state = 3
        elif self.main_window.Filling_RadioB.isChecked():
            self.all_bottons.radio_button_state = 4

        self.main_window.Cutout_RadioB.setCheckable(False)
        self.main_window.PickColor_RadioB.setCheckable(False)
        self.main_window.Coloring_RadioB.setCheckable(False)
        self.main_window.Filling_RadioB.setCheckable(False)

        self.main_window.Full_Automatic_Button.setText('团长！团长停下来啊！')

        self.main_window.WorkDir_Button.setDisabled(True)
        self.main_window.Change_Background_Button.setDisabled(True)
        self.main_window.Previous_Button.setDisabled(True)
        self.main_window.Next_Button.setDisabled(True)
        self.main_window.Semi_Automatic_Button.setDisabled(True)
        self.main_window.Binarization_Button.setDisabled(True)
        self.main_window.Crop_Button.setDisabled(True)
        self.main_window.Clean_Button.setDisabled(True)
        self.main_window.Revoke_Button.setDisabled(True)
        self.main_window.Redo_Button.setDisabled(True)
        self.main_window.Save_Botton.setDisabled(True)

    def System_free(self):
        self.system_state.tomede = False
        self.system_state.system_busy = False
        self.system_state.end_timer.emit()

        self.main_window.Cutout_RadioB.setCheckable(True)
        self.main_window.PickColor_RadioB.setCheckable(True)
        self.main_window.Coloring_RadioB.setCheckable(True)
        self.main_window.Filling_RadioB.setCheckable(True)

        if self.all_bottons.radio_button_state == 1:
            self.main_window.Cutout_RadioB.setChecked(True)
        elif self.all_bottons.radio_button_state == 2:
            self.main_window.PickColor_RadioB.setChecked(True)
        elif self.all_bottons.radio_button_state == 3:
            self.main_window.Coloring_RadioB.setChecked(True)
        elif self.all_bottons.radio_button_state == 4:
            self.main_window.Filling_RadioB.setChecked(True)

        self.main_window.Full_Automatic_Button.setText('全自动')

        self.main_window.WorkDir_Button.setEnabled(True)
        self.main_window.Change_Background_Button.setEnabled(True)
        self.main_window.Previous_Button.setEnabled(True)
        self.main_window.Next_Button.setEnabled(True)
        self.main_window.Semi_Automatic_Button.setEnabled(True)
        self.main_window.Binarization_Button.setEnabled(True)
        self.main_window.Crop_Button.setEnabled(True)
        self.main_window.Clean_Button.setEnabled(True)
        self.main_window.Revoke_Button.setEnabled(True)
        self.main_window.Redo_Button.setEnabled(True)
        self.main_window.Save_Botton.setEnabled(True)

    def Update_working_status(self):
        self.main_window.Working_Status_Label.setText(self.system_state.working_status_text[self.system_state.working_status_pin])
        self.system_state.working_status_pin = self.system_state.working_status_pin + 1 if self.system_state.working_status_pin < 3 else 0

    def Update_image_count(self):
        self.main_window.Image_Count_Label.setText(str(self.system_state.image_index) + '/' + str(len(self.system_state.images) - 1))
        pass

    def Start_timer(self):
        self.system_state.timer.start(900)
        pass

    def End_timer(self):
        self.system_state.timer.stop()
        self.main_window.Working_Status_Label.setText('')

    def closeEvent(self, event):
        if self.system_state.image_loaded and self.system_state.current_image_edited:
            self.functional_arithmetic.Save_image()



class All_Bottons(QMainWindow):
    def __init__(self, main_window):
        self.main_window = main_window

        QMainWindow.__init__(self)
        intValidator = QIntValidator(self)
        intValidator.setRange(0, 255)
        self.main_window.T_LineEdit.setValidator(intValidator)
        intValidator.setRange(1, 255)
        self.main_window.S_LineEdit.setValidator(intValidator)

        self.tolerance = 0
        self.brush_size = 1
        self.radio_button_state = 1

        self.main_window.T_LineEdit.textChanged.connect(self.On_T_lineedit_textChanged)
        self.main_window.S_LineEdit.textChanged.connect(self.On_S_lineedit_textChanged)
        self.main_window.T_Scrollbar.valueChanged.connect(self.On_T_scrollbar_valueChanged)
        self.main_window.S_Scrollbar.valueChanged.connect(self.On_S_scrollbar_valueChanged)

        self.main_window.WorkDir_Button.clicked.connect(self.On_workDir_button_clicked)
        self.main_window.Change_Background_Button.clicked.connect(self.On_change_background_button_clicked)
        self.main_window.Previous_Button.clicked.connect(self.On_previous_button_clicked)
        self.main_window.Next_Button.clicked.connect(self.On_next_button_clicked)
        self.main_window.Full_Automatic_Button.clicked.connect(self.On_full_automatic_button_clicked)
        self.main_window.Semi_Automatic_Button.clicked.connect(self.On_semi_automatic_button_clicked)
        self.main_window.Binarization_Button.clicked.connect(self.On_binarization_button_clicked)
        self.main_window.Crop_Button.clicked.connect(self.On_crop_button_clicked)
        self.main_window.Clean_Button.clicked.connect(self.On_clean_button_clicked)
        self.main_window.Revoke_Button.clicked.connect(self.On_revoke_button_clicked)
        self.main_window.Redo_Button.clicked.connect(self.On_redo_button_clicked)
        self.main_window.Save_Botton.clicked.connect(self.On_save_button_clicked)

    def On_T_lineedit_textChanged(self):
        text = self.main_window.T_LineEdit.text()

        if len(text) == 0:
            text = '0'
            self.main_window.T_LineEdit.setText(text)
        elif text[0] == '0' and len(text) > 1:
            for i in range(len(text)):
                if text[0] == '0':
                    text = text.replace('0', '', 1)

            if len(text) == 0:
                text = '0'

        self.main_window.T_Scrollbar.setValue(eval(text))
        self.all_bottons.tolerance = eval(text)

    def On_S_lineedit_textChanged(self):
        text = self.main_window.S_LineEdit.text()

        if len(text) == 0:
            text = '1'
            self.main_window.S_LineEdit.setText(text)
        elif text[0] == '0' and len(text) > 1:
            for i in range(len(text)):
                if text[0] == '0':
                    text = text.replace('0', '', 1)

            if len(text) == 0:
                text = '1'

        self.main_window.S_Scrollbar.setValue(eval(text))
        self.all_bottons.brush_size = eval(text)

    def On_T_scrollbar_valueChanged(self):
        self.main_window.T_LineEdit.setText(str(self.main_window.T_Scrollbar.value()))
        pass

    def On_S_scrollbar_valueChanged(self):
        self.main_window.S_LineEdit.setText(str(self.main_window.S_Scrollbar.value()))
        pass

    def On_workDir_button_clicked(self):
        workroot = QFileDialog.getExistingDirectory(self.main_window, '文件目录')
        if workroot == '':
            return

        self.main_window.Working_Status_Label.setText('')
        self.functional_arithmetic.Import_path(workroot)

    def On_change_background_button_clicked(self):
        if self.image_label.image_label_background.size[0] == 700:
            self.image_label.image_label_background = self.image_label.image_label_background_B
        else:
            self.image_label.image_label_background = self.image_label.image_label_background_W

        self.main_window.Working_Status_Label.setText('')
        self.image_label.Draw_image_label()

    def On_previous_button_clicked(self):
        if self.system_state.image_loaded and self.system_state.image_index > 1:
            if self.system_state.current_image_edited:
                self.functional_arithmetic.Save_image()

            self.system_state.image_index -= 1
            self.image_label.current_image_image = self.system_state.images[self.system_state.image_index].copy().convert('RGBA')
            self.image_label.current_image_array = np.array(self.image_label.current_image_image, dtype='int')

            self.backup_mod.backups = [self.image_label.current_image_image.copy()]
            self.backup_mod.backup_pin = 0

            self.image_label.zoom = 1
            self.image_label.Set_scrollbar_value(0, 0)
            self.image_label.Set_scrollbar_display()
            self.system_state.current_image_edited = False
            self.main_window.Working_Status_Label.setText('')

            self.image_label.Set_image_background()
            self.image_label.Draw_image_label()
            self.system_state.Update_image_count()

        elif self.system_state.image_index == 1:
            self.main_window.Working_Status_Label.setText('这是第一张了')

    def On_next_button_clicked(self):
        if self.system_state.image_loaded and self.system_state.image_index < len(self.system_state.images) - 1:
            if self.system_state.current_image_edited:
                self.functional_arithmetic.Save_image()

            self.system_state.image_index += 1
            self.image_label.current_image_image = self.system_state.images[self.system_state.image_index].copy().convert('RGBA')
            self.image_label.current_image_array = np.array(self.image_label.current_image_image, dtype='int')

            self.backup_mod.backups = [self.image_label.current_image_image.copy()]
            self.backup_mod.backup_pin = 0

            self.image_label.zoom = 1
            self.image_label.Set_scrollbar_value(0, 0)
            self.image_label.Set_scrollbar_display()
            self.system_state.current_image_edited = False
            self.main_window.Working_Status_Label.setText('')

            self.image_label.Set_image_background()
            self.image_label.Draw_image_label()
            self.system_state.Update_image_count()

        elif self.system_state.image_index == len(self.system_state.images) - 1:
            self.main_window.Working_Status_Label.setText('这是最后一张了')

    def On_full_automatic_button_clicked(self):
        if self.system_state.image_loaded:
            if not self.system_state.system_busy:
                self.functional_arithmetic.Auto_pick_color(5)
            else:
                self.system_state.tomede = True

    def On_semi_automatic_button_clicked(self):
        if self.system_state.image_loaded:
            self.functional_arithmetic.Auto_pick_color(1)

    def On_binarization_button_clicked(self):
        if self.system_state.image_loaded:
            if not self.system_state.system_busy:
                t = THREADING_Thread(target=self.functional_arithmetic.Image_binarization, args=())
                t.start()

    def On_crop_button_clicked(self):
        if self.system_state.image_loaded:
            t = THREADING_Thread(target=self.functional_arithmetic.Crop_image, args=(0,))
            t.start()

    def On_clean_button_clicked(self):
        if self.system_state.image_loaded:
            t = THREADING_Thread(target=self.functional_arithmetic.Clean_image, args=(0,))
            t.start()

    def On_revoke_button_clicked(self):
        self.backup_mod.Revoke_backup()
        pass

    def On_redo_button_clicked(self):
        self.backup_mod.Redo_backup()
        pass

    def On_save_button_clicked(self):
        self.main_window.Working_Status_Label.setText('')
        self.functional_arithmetic.Save_image()



class Color_label(QMainWindow):
    def __init__(self, main_window):
        self.main_window = main_window

        QMainWindow.__init__(self)
        intValidator = QIntValidator(self)
        intValidator.setRange(0, 255)
        self.main_window.R_LineEdit.setValidator(intValidator)
        self.main_window.G_LineEdit.setValidator(intValidator)
        self.main_window.B_LineEdit.setValidator(intValidator)
        self.main_window.A_LineEdit.setValidator(intValidator)

        self.main_window.R_LineEdit.textChanged.connect(self.On_R_lineEdit_textChanged)
        self.main_window.G_LineEdit.textChanged.connect(self.On_G_lineEdit_textChanged)
        self.main_window.B_LineEdit.textChanged.connect(self.On_B_lineEdit_textChanged)
        self.main_window.A_LineEdit.textChanged.connect(self.On_A_lineEdit_textChanged)

        self.main_window.R_Scrollbar.valueChanged.connect(self.On_R_scrollbar_valueChanged)
        self.main_window.G_Scrollbar.valueChanged.connect(self.On_G_scrollbar_valueChanged)
        self.main_window.B_Scrollbar.valueChanged.connect(self.On_B_scrollbar_valueChanged)
        self.main_window.A_Scrollbar.valueChanged.connect(self.On_A_scrollbar_valueChanged)

        self.color = [255, 255, 255, 255]
        self.color_preview_background = Image.open('res/Transparent_label.png').convert('RGBA')

    def Draw_color_preview_label(self):
        color_preview_image = Image.new('RGBA', (120, 120), tuple(self.color))
        color_preview_background = self.color_label.color_preview_background.resize((120, 120))
        color_preview_background.alpha_composite(color_preview_image)

        self.main_window.Color_Preview_label.setPixmap(ImageQt.toqpixmap(color_preview_background))

    def On_R_lineEdit_textChanged(self):
        text = self.main_window.R_LineEdit.text()

        if len(text) == 0:
            text = '0'
            self.main_window.R_LineEdit.setText(text)
        elif text[0] == '0' and len(text) > 1:
            for i in range(len(text)):
                if text[0] == '0':
                    text = text.replace('0', '', 1)

            if len(text) == 0:
                text = '0'

        self.main_window.R_Scrollbar.setValue(eval(text))
        self.color_label.color[0] = eval(text)

        self.color_label.Draw_color_preview_label()

    def On_G_lineEdit_textChanged(self):
        text = self.main_window.G_LineEdit.text()

        if len(text) == 0:
            text = '0'
            self.main_window.G_LineEdit.setText(text)
        elif text[0] == '0' and len(text) > 1:
            for i in range(len(text)):
                if text[0] == '0':
                    text = text.replace('0', '', 1)

            if len(text) == 0:
                text = '0'

        self.main_window.G_Scrollbar.setValue(eval(text))
        self.color_label.color[1] = eval(text)

        self.color_label.Draw_color_preview_label()

    def On_B_lineEdit_textChanged(self):
        text = self.main_window.B_LineEdit.text()

        if len(text) == 0:
            text = '0'
            self.main_window.B_LineEdit.setText(text)
        elif text[0] == '0' and len(text) > 1:
            for i in range(len(text)):
                if text[0] == '0':
                    text = text.replace('0', '', 1)

            if len(text) == 0:
                text = '0'

        self.main_window.B_Scrollbar.setValue(eval(text))
        self.color_label.color[2] = eval(text)

        self.color_label.Draw_color_preview_label()

    def On_A_lineEdit_textChanged(self):
        text = self.main_window.A_LineEdit.text()

        if len(text) == 0:
            text = '0'
            self.main_window.A_LineEdit.setText(text)
        elif text[0] == '0' and len(text) > 1:
            for i in range(len(text)):
                if text[0] == '0':
                    text = text.replace('0', '', 1)

            if len(text) == 0:
                text = '0'

        self.main_window.A_Scrollbar.setValue(eval(text))
        self.color_label.color[3] = eval(text)

        self.color_label.Draw_color_preview_label()

    def On_R_scrollbar_valueChanged(self):
        self.main_window.R_LineEdit.setText(str(self.main_window.R_Scrollbar.value()))
        pass

    def On_G_scrollbar_valueChanged(self):
        self.main_window.G_LineEdit.setText(str(self.main_window.G_Scrollbar.value()))
        pass

    def On_B_scrollbar_valueChanged(self):
        self.main_window.B_LineEdit.setText(str(self.main_window.B_Scrollbar.value()))
        pass

    def On_A_scrollbar_valueChanged(self):
        self.main_window.A_LineEdit.setText(str(self.main_window.A_Scrollbar.value()))
        pass



class Image_label:
    def __init__(self, main_window):
        self.main_window = main_window

        self.zoom = 1
        self.scrollbar_offset = [0, 0]
        self.current_image_image = Image.new('RGBA', (100, 100))
        self.current_image_array = np.array(self.current_image_image, dtype='int')
        self.image_label_background_W = Image.open('res/TransparentBg-W.png').convert('RGBA')
        self.image_label_background_B = Image.open('res/TransparentBg-B.png').convert('RGBA')
        self.image_label_background = self.image_label_background_W

        self.main_window.Image_H_Scrollbar.valueChanged.connect(self.On_image_H_scrollbar_valueChanged)
        self.main_window.Image_V_Scrollbar.valueChanged.connect(self.On_image_V_scrollbar_valueChanged)

    def Draw_image_label(self):
        drawn_image_rect = [0, 0, 0, 0]
        drawn_image_rect[0] = self.image_label.scrollbar_offset[0]\
            if self.image_label.current_image_image.size[0] * self.image_label.zoom > self.main_window.Image_label.width()\
            else 0
        drawn_image_rect[1] = self.image_label.scrollbar_offset[1]\
            if self.image_label.current_image_image.size[1] * self.image_label.zoom > self.main_window.Image_label.height() \
            else 0
        drawn_image_rect[2] = self.image_label.scrollbar_offset[0] + self.main_window.Image_label.width()\
            if self.image_label.current_image_image.size[0] * self.image_label.zoom > self.main_window.Image_label.width()\
            else self.image_label.current_image_image.size[0] * self.image_label.zoom
        drawn_image_rect[3] = self.image_label.scrollbar_offset[1] + self.main_window.Image_label.height()\
            if self.image_label.current_image_image.size[1] * self.image_label.zoom > self.main_window.Image_label.height() \
            else self.image_label.current_image_image.size[1] * self.image_label.zoom

        drawn_label_rect = [0, 0, 0, 0]
        drawn_label_rect[0] = 0\
            if self.image_label.current_image_image.size[0] * self.image_label.zoom > self.main_window.Image_label.width()\
            else (self.main_window.Image_label.width() - self.image_label.current_image_image.size[0] * self.image_label.zoom) // 2
        drawn_label_rect[1] = 0\
            if self.image_label.current_image_image.size[1] * self.image_label.zoom > self.main_window.Image_label.height() \
            else (self.main_window.Image_label.height() - self.image_label.current_image_image.size[1] * self.image_label.zoom) // 2
        drawn_label_rect[2] = self.main_window.Image_label.width()\
            if self.image_label.current_image_image.size[0] * self.image_label.zoom > self.main_window.Image_label.width()\
            else drawn_label_rect[0] + self.image_label.current_image_image.size[0] * self.image_label.zoom
        drawn_label_rect[3] = self.main_window.Image_label.height()\
            if self.image_label.current_image_image.size[1] * self.image_label.zoom > self.main_window.Image_label.height() \
            else drawn_label_rect[1] + self.image_label.current_image_image.size[1] * self.image_label.zoom

        temp_image = self.image_label.current_image_image.resize((drawn_image_rect[2] - drawn_image_rect[0], drawn_image_rect[3] - drawn_image_rect[1]),
                                                                Image.NEAREST,
                                                                 (drawn_image_rect[0] // self.image_label.zoom, drawn_image_rect[1] // self.image_label.zoom, drawn_image_rect[2] // self.image_label.zoom, drawn_image_rect[3] // self.image_label.zoom))
        drawn_image_image = self.image_label.image_label_background.resize((self.main_window.Image_label.width(), self.main_window.Image_label.height()))
        drawn_image_image.alpha_composite(temp_image, ((drawn_label_rect[0], drawn_label_rect[1])))
        self.main_window.Image_label.setPixmap(ImageQt.toqpixmap(drawn_image_image))

    def Set_scrollbar_display(self):
        if self.image_label.current_image_image.size[0] * self.image_label.zoom > self.main_window.Image_label.width():
            self.main_window.Image_H_Scrollbar.setEnabled(True)
            self.main_window.Image_H_Scrollbar.setRange(0, self.image_label.current_image_image.size[0] * self.image_label.zoom - self.main_window.Image_label.width())
            self.main_window.Image_H_Scrollbar.setPageStep((self.image_label.current_image_image.size[0] * self.image_label.zoom - self.main_window.Image_label.width()) // 10)
        else:
            self.main_window.Image_H_Scrollbar.setDisabled(True)

        if self.image_label.current_image_image.size[1] * self.image_label.zoom > self.main_window.Image_label.height():
            self.main_window.Image_V_Scrollbar.setEnabled(True)
            self.main_window.Image_V_Scrollbar.setRange(0, self.image_label.current_image_image.size[1] * self.image_label.zoom - self.main_window.Image_label.height())
            self.main_window.Image_V_Scrollbar.setPageStep((self.image_label.current_image_image.size[1] * self.image_label.zoom - self.main_window.Image_label.height()) // 10)
        else:
            self.main_window.Image_V_Scrollbar.setDisabled(True)

    def Set_scrollbar_value(self, x, y):
        self.image_label.scrollbar_offset = [x, y]

        self.main_window.Image_H_Scrollbar.blockSignals(True)
        self.main_window.Image_V_Scrollbar.blockSignals(True)
        self.main_window.Image_H_Scrollbar.setValue(x)
        self.main_window.Image_V_Scrollbar.setValue(y)
        self.main_window.Image_H_Scrollbar.blockSignals(False)
        self.main_window.Image_V_Scrollbar.blockSignals(False)

    def On_image_H_scrollbar_valueChanged(self):
        self.image_label.scrollbar_offset[0] = self.main_window.Image_H_Scrollbar.value()
        self.image_label.Draw_image_label()

    def On_image_V_scrollbar_valueChanged(self):
        self.image_label.scrollbar_offset[1] = self.main_window.Image_V_Scrollbar.value()
        self.image_label.Draw_image_label()

    def wheelEvent(self, event):
        if self.system_state.image_loaded:
            if event.angleDelta().y() > 0:
                if self.image_label.zoom < ZOOM_LIMIT:
                    self.image_label.zoom += 1

                    self.main_window.Image_H_Scrollbar.blockSignals(True)
                    self.main_window.Image_V_Scrollbar.blockSignals(True)
                    self.image_label.Set_scrollbar_display()

                    if self.main_window.Image_H_Scrollbar.isEnabled():
                        self.main_window.Image_H_Scrollbar.setValue(self.image_label.scrollbar_offset[0] + (self.image_label.scrollbar_offset[0] + self.main_window.Image_label.width() // 2) // (self.image_label.zoom - 1))
                        self.image_label.scrollbar_offset[0] = self.main_window.Image_H_Scrollbar.value()
                    else:
                        self.main_window.Image_H_Scrollbar.setValue(0)
                        self.image_label.scrollbar_offset[0] = self.main_window.Image_H_Scrollbar.value()

                    if self.main_window.Image_V_Scrollbar.isEnabled():
                        self.main_window.Image_V_Scrollbar.setValue(self.image_label.scrollbar_offset[1] + (self.image_label.scrollbar_offset[1] + self.main_window.Image_label.height() // 2) // (self.image_label.zoom - 1))
                        self.image_label.scrollbar_offset[1] = self.main_window.Image_V_Scrollbar.value()
                    else:
                        self.main_window.Image_V_Scrollbar.setValue(0)
                        self.image_label.scrollbar_offset[1] = self.main_window.Image_V_Scrollbar.value()

                    self.main_window.Image_H_Scrollbar.blockSignals(False)
                    self.main_window.Image_V_Scrollbar.blockSignals(False)

                    self.image_label.Draw_image_label()

            elif event.angleDelta().y() < 0:
                if self.image_label.zoom > 1:
                    self.image_label.zoom -= 1

                    self.main_window.Image_H_Scrollbar.blockSignals(True)
                    self.main_window.Image_V_Scrollbar.blockSignals(True)
                    self.image_label.Set_scrollbar_display()

                    if self.main_window.Image_H_Scrollbar.isEnabled():
                        if self.image_label.scrollbar_offset[0] - (self.image_label.scrollbar_offset[0] + self.main_window.Image_label.width() // 2) // (self.image_label.zoom + 1) < self.main_window.Image_H_Scrollbar.maximum():
                            self.main_window.Image_H_Scrollbar.setValue(self.image_label.scrollbar_offset[0] - (self.image_label.scrollbar_offset[0] + self.main_window.Image_label.width() // 2) // (self.image_label.zoom + 1))
                        else:
                            self.main_window.Image_H_Scrollbar.setValue(self.main_window.Image_H_Scrollbar.maximum())

                        self.image_label.scrollbar_offset[0] = self.main_window.Image_H_Scrollbar.value()
                    else:
                        self.main_window.Image_H_Scrollbar.setValue(0)
                        self.image_label.scrollbar_offset[0] = self.main_window.Image_H_Scrollbar.value()

                    if self.main_window.Image_V_Scrollbar.isEnabled():
                        if self.image_label.scrollbar_offset[1] - (self.image_label.scrollbar_offset[1] + self.main_window.Image_label.height() // 2) // (self.image_label.zoom + 1) < self.main_window.Image_V_Scrollbar.maximum():
                            self.main_window.Image_V_Scrollbar.setValue(self.image_label.scrollbar_offset[1] - (self.image_label.scrollbar_offset[1] + self.main_window.Image_label.height() // 2) // (self.image_label.zoom + 1))
                        else:
                            self.main_window.Image_V_Scrollbar.setValue(self.main_window.Image_V_Scrollbar.maximum())

                        self.image_label.scrollbar_offset[1] = self.main_window.Image_V_Scrollbar.value()
                    else:
                        self.main_window.Image_V_Scrollbar.setValue(0)
                        self.image_label.scrollbar_offset[1] = self.main_window.Image_V_Scrollbar.value()

                    self.main_window.Image_H_Scrollbar.blockSignals(False)
                    self.main_window.Image_V_Scrollbar.blockSignals(False)

                    self.image_label.Draw_image_label()

    def resizeEvent(self, event):
        if not self.system_state.UIloaded:
            self.system_state.UIloaded = True
            return

        self.image_label.Set_scrollbar_display()
        self.color_label.Draw_color_preview_label()
        self.image_label.Draw_image_label()

    def Set_image_background(self):
        color_backup = self.color_label.color.copy()

        self.functional_arithmetic.Auto_pick_color(0)
        if int(self.color_label.color[0]) + int(self.color_label.color[1]) + int(self.color_label.color[2]) < 382 or self.color_label.color[3] == 0:
            self.image_label.image_label_background = self.image_label_background_W
        else:
            self.image_label.image_label_background = self.image_label_background_B

        self.main_window.R_LineEdit.setText(str(255))
        self.main_window.G_LineEdit.setText(str(255))
        self.main_window.B_LineEdit.setText(str(255))
        self.main_window.A_LineEdit.setText(str(255))

        self.color_label.color = color_backup

        self.image_label.Draw_image_label()



class Mouse_And_Key_Events(QWidget):
    def __init__(self, main_window):
        self.main_window = main_window
        QWidget.__init__(self)

        self.draging = False
        self.drag_first_point = QPoint()
        self.drag_second_point = QPoint()
        self.coloring = False

    def mousePressEvent(self, event):
        if self.main_window.Image_label.geometry().x() <= event.pos().x() and event.pos().x() <= self.main_window.Image_label.geometry().x() + self.main_window.Image_label.geometry().width()\
        and self.main_window.Image_label.geometry().y() <= event.pos().y() and event.pos().y() <= self.main_window.Image_label.geometry().y() + self.main_window.Image_label.geometry().height()\
        and self.system_state.image_loaded:
            click_point = [0, 0]
            click_point[0] = (event.pos().x() - self.main_window.Image_label.geometry().x() + self.image_label.scrollbar_offset[0]) // self.image_label.zoom\
                if self.main_window.Image_H_Scrollbar.isEnabled()\
                else ((event.pos().x() - self.main_window.Image_label.geometry().x())
                    - (self.main_window.Image_label.width() - self.image_label.current_image_image.size[0] * self.image_label.zoom) // 2) \
                    // self.image_label.zoom
            click_point[1] = (event.pos().y() - self.main_window.Image_label.geometry().y() + self.image_label.scrollbar_offset[1]) // self.image_label.zoom\
                if self.main_window.Image_V_Scrollbar.isEnabled()\
                else ((event.pos().y() - self.main_window.Image_label.geometry().y())
                    - (self.main_window.Image_label.height() - self.image_label.current_image_image.size[1] * self.image_label.zoom) // 2) \
                    // self.image_label.zoom

            if event.button() == Qt.LeftButton:
                if self.mouse_and_key_events.draging:
                    self.mouse_and_key_events.drag_first_point = event.pos()
                    self.setCursor(Qt.ClosedHandCursor)

                elif self.main_window.Cutout_RadioB.isChecked() and not self.system_state.system_busy:
                    if 0 <= click_point[0] and click_point[0] < self.image_label.current_image_image.size[0] \
                    and 0 <= click_point[1] and click_point[1] < self.image_label.current_image_image.size[1] \
                    and self.image_label.current_image_array[click_point[1], click_point[0]][3] != 0:
                        t = THREADING_Thread(target=self.functional_arithmetic.Cutout_image, args=(click_point[0], click_point[1], 0,))
                        t.start()

                elif self.main_window.PickColor_RadioB.isChecked():
                    if 0 <= click_point[0] and click_point[0] < self.image_label.current_image_image.size[0] \
                    and 0 <= click_point[1] and click_point[1] < self.image_label.current_image_image.size[1]:
                        self.functional_arithmetic.Pick_color(click_point[0], click_point[1])

                elif self.main_window.Coloring_RadioB.isChecked() and not self.system_state.system_busy:
                    if 0 <= click_point[0] and click_point[0] < self.image_label.current_image_image.size[0] \
                    and 0 <= click_point[1] and click_point[1] < self.image_label.current_image_image.size[1]:
                        self.mouse_and_key_events.coloring = True
                        self.functional_arithmetic.Coloring_image(click_point[0], click_point[1])

                elif self.main_window.Filling_RadioB.isChecked() and not self.system_state.system_busy:
                    if 0 <= click_point[0] and click_point[0] < self.image_label.current_image_image.size[0] \
                    and 0 <= click_point[1] and click_point[1] < self.image_label.current_image_image.size[1]:
                        t = THREADING_Thread(target=self.functional_arithmetic.Filling_image, args=(click_point[0], click_point[1],))
                        t.start()

            elif event.button() == Qt.RightButton and self.main_window.Cutout_RadioB.isChecked() and not self.system_state.system_busy:
                if 0 <= click_point[0] and click_point[0] < self.image_label.current_image_image.size[0] \
                and 0 <= click_point[1] and click_point[1] < self.image_label.current_image_image.size[1]:
                    self.functional_arithmetic.Pick_color(click_point[0], click_point[1])
                    if self.image_label.current_image_array[click_point[1], click_point[0]][3] != 0:
                        t = THREADING_Thread(target=self.functional_arithmetic.Cutout_image, args=(click_point[0], click_point[1], 0,))
                        t.start()

    def mouseMoveEvent(self, event):
        if self.main_window.Image_label.geometry().x() <= event.pos().x() and event.pos().x() <= self.main_window.Image_label.geometry().x() + self.main_window.Image_label.geometry().width()\
                and self.main_window.Image_label.geometry().y() <= event.pos().y() and event.pos().y() <= self.main_window.Image_label.geometry().y() + self.main_window.Image_label.geometry().height()\
                and self.system_state.image_loaded:
            click_point = [0, 0]
            click_point[0] = (event.pos().x() - self.main_window.Image_label.geometry().x() + self.image_label.scrollbar_offset[0]) // self.image_label.zoom\
                            if self.main_window.Image_H_Scrollbar.isEnabled()\
                            else ((event.pos().x() - self.main_window.Image_label.geometry().x())
                                - (self.main_window.Image_label.width() - self.image_label.current_image_image.size[0] * self.image_label.zoom) // 2) \
                                // self.image_label.zoom
            click_point[1] = (event.pos().y() - self.main_window.Image_label.geometry().y() + self.image_label.scrollbar_offset[1]) // self.image_label.zoom\
                            if self.main_window.Image_V_Scrollbar.isEnabled()\
                            else ((event.pos().y() - self.main_window.Image_label.geometry().y())
                                - (self.main_window.Image_label.height() - self.image_label.current_image_image.size[1] * self.image_label.zoom) // 2) \
                                // self.image_label.zoom

            if event.buttons() == Qt.LeftButton:
                if self.mouse_and_key_events.draging :
                    self.mouse_and_key_events.drag_second_point = event.pos()
                    self.Drag_image()
                    self.mouse_and_key_events.drag_first_point = self.mouse_and_key_events.drag_second_point

                elif self.main_window.Cutout_RadioB.isChecked() and not self.system_state.system_busy:
                    if (self.mouse_and_key_events.drag_first_point.x() != click_point[0] \
                        or self.mouse_and_key_events.drag_first_point.y() != click_point[1]) \
                    and 0 <= click_point[0] and click_point[0] < self.image_label.current_image_image.size[0] \
                    and 0 <= click_point[1] and click_point[1] < self.image_label.current_image_image.size[1] \
                    and self.image_label.current_image_array[click_point[1], click_point[0]][3] != 0:
                        t = THREADING_Thread(target=self.functional_arithmetic.Cutout_image, args=(click_point[0], click_point[1], 0,))
                        t.start()

                elif self.main_window.PickColor_RadioB.isChecked():
                    if (self.mouse_and_key_events.drag_first_point.x() != click_point[0] \
                        or self.mouse_and_key_events.drag_first_point.y() != click_point[1]) \
                    and 0 <= click_point[0] and click_point[0] < self.image_label.current_image_image.size[0] \
                    and 0 <= click_point[1] and click_point[1] < self.image_label.current_image_image.size[1]:
                        self.functional_arithmetic.Pick_color(click_point[0], click_point[1])

                elif self.main_window.Coloring_RadioB.isChecked() and not self.system_state.system_busy:
                    if (self.mouse_and_key_events.drag_first_point.x() != click_point[0] \
                        or self.mouse_and_key_events.drag_first_point.y() != click_point[1]) \
                    and 0 <= click_point[0] and click_point[0] < self.image_label.current_image_image.size[0] \
                    and 0 <= click_point[1] and click_point[1] < self.image_label.current_image_image.size[1]:
                        self.functional_arithmetic.Coloring_image(click_point[0], click_point[1])

                elif self.main_window.Filling_RadioB.isChecked() and not self.system_state.system_busy:
                    if (self.mouse_and_key_events.drag_first_point.x() != click_point[0] \
                        or self.mouse_and_key_events.drag_first_point.y() != click_point[1]) \
                    and 0 <= click_point[0] and click_point[0] < self.image_label.current_image_image.size[0] \
                    and 0 <= click_point[1] and click_point[1] < self.image_label.current_image_image.size[1]:
                        t = THREADING_Thread(target=self.functional_arithmetic.Filling_image, args=(click_point[0], click_point[1],))
                        t.start()

            elif event.buttons() == Qt.RightButton and self.main_window.Cutout_RadioB.isChecked() and not self.system_state.system_busy:
                if (self.mouse_and_key_events.drag_first_point.x() != click_point[0] \
                    or self.mouse_and_key_events.drag_first_point.y() != click_point[1]) \
                and 0 <= click_point[0] and click_point[0] < self.image_label.current_image_image.size[0] \
                and 0 <= click_point[1] and click_point[1] < self.image_label.current_image_image.size[1]:
                    self.functional_arithmetic.Pick_color(click_point[0], click_point[1])

                    if self.image_label.current_image_array[click_point[1], click_point[0]][3] != 0:
                        t = THREADING_Thread(target=self.functional_arithmetic.Cutout_image, args=(click_point[0], click_point[1], 0,))
                        t.start()

    def mouseReleaseEvent(self, event):
        self.setCursor(Qt.ArrowCursor)

        if self.coloring:
            self.backup_mod.Insert_backup()
            self.mouse_and_key_events.coloring = False

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.mouse_and_key_events.draging = True

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.mouse_and_key_events.draging = False

    def Drag_image(self):
        if self.main_window.Image_H_Scrollbar.isEnabled():
            self.image_label.scrollbar_offset[0] += self.mouse_and_key_events.drag_first_point.x() - self.mouse_and_key_events.drag_second_point.x()
            if self.image_label.scrollbar_offset[0] < 0:
                self.image_label.scrollbar_offset[0] = 0
            if self.image_label.scrollbar_offset[0] > self.image_label.current_image_image.size[0] * self.image_label.zoom - self.main_window.Image_label.width():
                self.image_label.scrollbar_offset[0] = self.image_label.current_image_image.size[0] * self.image_label.zoom - self.main_window.Image_label.width()

            self.main_window.Image_H_Scrollbar.blockSignals(True)
            self.main_window.Image_H_Scrollbar.setValue(self.image_label.scrollbar_offset[0])
            self.main_window.Image_H_Scrollbar.blockSignals(False)

        if self.main_window.Image_V_Scrollbar.isEnabled():
            self.image_label.scrollbar_offset[1] += self.mouse_and_key_events.drag_first_point.y() - self.mouse_and_key_events.drag_second_point.y()
            if self.image_label.scrollbar_offset[1] < 0:
                self.image_label.scrollbar_offset[1] = 0
            if self.image_label.scrollbar_offset[1] > self.image_label.current_image_image.size[1] * self.image_label.zoom - self.main_window.Image_label.height():
                self.image_label.scrollbar_offset[1] = self.image_label.current_image_image.size[1] * self.image_label.zoom - self.main_window.Image_label.height()

            self.main_window.Image_V_Scrollbar.blockSignals(True)
            self.main_window.Image_V_Scrollbar.setValue(self.image_label.scrollbar_offset[1])
            self.main_window.Image_V_Scrollbar.blockSignals(False)

        self.image_label.Draw_image_label()



class Main_Window(QMainWindow, Ui_Main_Window_UI):
    def __init__(self):
        QMainWindow.__init__(self)

        if not OS_path.isfile('res/Icon.ico'):
            QMessageBox.question(self, '阿勒勒？', 'Icon.ico没了？？？', QMessageBox.Yes)
            SYS_exit()
        if not OS_path.isfile('res/Transparent_label.png'):
            QMessageBox.question(self, '阿勒勒？', 'Transparent_label.png没了？？？', QMessageBox.Yes)
            SYS_exit()
        if not OS_path.isfile('res/TransparentBg-B.png'):
            QMessageBox.question(self, '阿勒勒？', 'TransparentBg-B.png没了？？？', QMessageBox.Yes)
            SYS_exit()
        if not OS_path.isfile('res/TransparentBg-W.png'):
            QMessageBox.question(self, '阿勒勒？', 'TransparentBg-W.png没了？？？', QMessageBox.Yes)
            SYS_exit()

        self.setupUi(self)

        self.main_window = self

        self.functional_arithmetic = Functional_Arithmetic(self.main_window)
        self.backup_mod = Backup_Mod(self.main_window)
        self.system_state = System_State(self.main_window)
        self.all_bottons = All_Bottons(self.main_window)
        self.color_label = Color_label(self.main_window)
        self.image_label = Image_label(self.main_window)
        self.mouse_and_key_events = Mouse_And_Key_Events(self.main_window)

        self.Set_functional_arithmetic()
        self.Set_backup_mod()
        self.Set_system_state()
        self.Set_all_bottons()
        self.Set_color_label()
        self.Set_image_label()
        self.Set_mouse_and_key_events()
        self.Set_QLabel_File_Dragable()

        self.wheelEvent = self.image_label.wheelEvent
        self.resizeEvent = self.image_label.resizeEvent
        self.mousePressEvent = self.mouse_and_key_events.mousePressEvent
        self.mouseMoveEvent = self.mouse_and_key_events.mouseMoveEvent
        self.mouseReleaseEvent = self.mouse_and_key_events.mouseReleaseEvent
        self.keyPressEvent = self.mouse_and_key_events.keyPressEvent
        self.keyReleaseEvent = self.mouse_and_key_events.keyReleaseEvent
        self.closeEvent = self.system_state.closeEvent

        self.color_label.Draw_color_preview_label()
        self.Image_label.setPixmap(ImageQt.toqpixmap(self.image_label.image_label_background))

    def Set_functional_arithmetic(self):
        self.functional_arithmetic.functional_arithmetic = self.functional_arithmetic
        self.functional_arithmetic.color_label = self.color_label
        self.functional_arithmetic.image_label = self.image_label
        self.functional_arithmetic.mouse_and_key_events = self.mouse_and_key_events
        self.functional_arithmetic.system_state = self.system_state
        self.functional_arithmetic.all_bottons = self.all_bottons
        self.functional_arithmetic.backup_mod = self.backup_mod

    def Set_backup_mod(self):
        self.backup_mod.functional_arithmetic = self.functional_arithmetic
        self.backup_mod.color_label = self.color_label
        self.backup_mod.image_label = self.image_label
        self.backup_mod.mouse_and_key_events = self.mouse_and_key_events
        self.backup_mod.system_state = self.system_state
        self.backup_mod.all_bottons = self.all_bottons
        self.backup_mod.backup_mod = self.backup_mod

    def Set_system_state(self):
        self.system_state.functional_arithmetic = self.functional_arithmetic
        self.system_state.color_label = self.color_label
        self.system_state.image_label = self.image_label
        self.system_state.mouse_and_key_events = self.mouse_and_key_events
        self.system_state.system_state = self.system_state
        self.system_state.all_bottons = self.all_bottons
        self.system_state.backup_mod = self.backup_mod

    def Set_all_bottons(self):
        self.all_bottons.functional_arithmetic = self.functional_arithmetic
        self.all_bottons.color_label = self.color_label
        self.all_bottons.image_label = self.image_label
        self.all_bottons.mouse_and_key_events = self.mouse_and_key_events
        self.all_bottons.system_state = self.system_state
        self.all_bottons.all_bottons = self.all_bottons
        self.all_bottons.backup_mod = self.backup_mod

    def Set_color_label(self):
        self.color_label.functional_arithmetic = self.functional_arithmetic
        self.color_label.color_label = self.color_label
        self.color_label.image_label = self.image_label
        self.color_label.mouse_and_key_events = self.mouse_and_key_events
        self.color_label.system_state = self.system_state
        self.color_label.all_bottons = self.all_bottons
        self.color_label.backup_mod = self.backup_mod

    def Set_image_label(self):
        self.image_label.functional_arithmetic = self.functional_arithmetic
        self.image_label.color_label = self.color_label
        self.image_label.image_label = self.image_label
        self.image_label.mouse_and_key_events = self.mouse_and_key_events
        self.image_label.system_state = self.system_state
        self.image_label.all_bottons = self.all_bottons
        self.image_label.backup_mod = self.backup_mod

    def Set_mouse_and_key_events(self):
        self.mouse_and_key_events.functional_arithmetic = self.functional_arithmetic
        self.mouse_and_key_events.color_label = self.color_label
        self.mouse_and_key_events.image_label = self.image_label
        self.mouse_and_key_events.mouse_and_key_events = self.mouse_and_key_events
        self.mouse_and_key_events.system_state = self.system_state
        self.mouse_and_key_events.all_bottons = self.all_bottons
        self.mouse_and_key_events.backup_mod = self.backup_mod

    def Set_QLabel_File_Dragable(self):
        self.Image_label.main_window = self.main_window

        self.Image_label.functional_arithmetic = self.functional_arithmetic
        self.Image_label.color_label = self.color_label
        self.Image_label.image_label = self.image_label
        self.Image_label.mouse_and_key_events = self.mouse_and_key_events
        self.Image_label.system_state = self.system_state
        self.Image_label.all_bottons = self.all_bottons
        self.Image_label.backup_mod = self.backup_mod



if __name__ == '__main__':
    app = QApplication(SYS_argv)
    main_window = Main_Window()
    main_window.show()
    SYS_exit(app.exec_())
