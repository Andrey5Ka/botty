from utils.misc import kill_thread, color_filter, cut_roi
from template_finder import TemplateFinder
from screen import Screen
from config import Config
import mouse
from utils import custom_mouse
import keyboard
import cv2
from logger import Logger
import time
import random


class DeathManager:
    def __init__(self, screen: Screen, template_finder: TemplateFinder):
        self._config = Config()
        self._screen = screen
        self._template_finder = template_finder
        _, self._you_have_died_filtered = color_filter(cv2.imread("assets/templates/you_have_died.png"), self._config.colors["red"])
        self._search_roi = [self._config.ui_pos["death_roi_left"], self._config.ui_pos["death_roi_top"], self._config.ui_pos["death_roi_width"], self._config.ui_pos["death_roi_height"]]
        self._died = False
        self._do_monitor = False

    def stop_monitor(self):
        self._do_monitor = False

    def died(self):
        return self._died

    def pick_up_corpse(self):
        Logger.debug("Pick up corpse")
        x, y = self._screen.convert_screen_to_monitor((self._config.ui_pos["corpse_x"], self._config.ui_pos["corpse_y"]))
        custom_mouse.move(x, y, duration=random.random() * 0.15 + 0.3)
        mouse.click(button="left")
        self._died = False

    def start_monitor(self, run_thread):
        self._do_monitor = True
        while self._do_monitor:
            time.sleep(1.0) # no need to do this too frequent, when we died we are not in a hurry...
            roi_img = cut_roi(self._screen.grab(), self._search_roi)
            _, filtered_roi_img = color_filter(roi_img, self._config.colors["red"])
            res = cv2.matchTemplate(filtered_roi_img, self._you_have_died_filtered, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(res)
            if max_val > 0.94:
                Logger.warning("You have died!")
                # first wait a bit to make sure health manager is done with its chicken stuff which obviously failed
                kill_thread(run_thread)
                time.sleep(5)
                self._died = True
                keyboard.send("esc")
                self._template_finder.search_and_wait("A5_TOWN_1")
                time.sleep(2)
                self._do_monitor = False


# Testing:
if __name__ == "__main__":
    keyboard.wait("f11")
    config = Config()
    screen = Screen(config.general["monitor"])
    template_finder = TemplateFinder(screen)
    manager = DeathManager(screen, template_finder)
    manager.start_monitor(None)