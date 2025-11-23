import subprocess
import re

class GestureHandler:
    def __init__(self):
        self.alt_pressed = False
        self.fingers_down = 0
        self.last_x = 0
        self.last_y = 0
        self.gesture_active = False
        self.min_delta = 35  # Decrease threshold for more overall sensitivity
        self.gesture_type = None
        self.action_triggered = False
        self.direction_determined = False
        self.horizontal_threshold_extra = 15  # Decrease horizontal threshold for more horizontal sensitivity (extra)

    def press_alt(self):
        if not self.alt_pressed:
            subprocess.run(['xdotool', 'keydown', 'alt'])
            self.alt_pressed = True

    def release_alt(self):
        if self.alt_pressed:
            subprocess.run(['xdotool', 'keyup', 'alt'])
            self.alt_pressed = False

    def tab_next(self): subprocess.run(['xdotool', 'key', 'Tab'])
    def tab_prev(self): subprocess.run(['xdotool', 'key', 'shift+Tab'])
    def show_desktop(self): subprocess.run(['xdotool', 'key', '--clearmodifiers', 'super+d'])
    def workspace_down(self): subprocess.run(['xdotool', 'key', '--clearmodifiers', 'ctrl+alt+Down'])
    def workspace_up(self): subprocess.run(['xdotool', 'key', 'ctrl+alt+Up'])
    def workspace_left(self): subprocess.run(['xdotool', 'key', 'ctrl+alt+Left'])
    def workspace_right(self): subprocess.run(['xdotool', 'key', 'ctrl+alt+Right'])
    def screenshot(self): subprocess.run(['xdotool', 'key', 'ctrl+Print'])
    def middle_click(self): subprocess.run(['xdotool', 'click', '--clearmodifiers', '2'])

    def get_current_workspace(self):
        try:
            result = subprocess.run(['wmctrl', '-d'], capture_output=True, text=True)
            for line in result.stdout.splitlines():
                if '*' in line:
                    parts = line.split()
                    if parts:
                        return int(parts[0])
        except Exception:
            pass
        return 0

    def get_workspace_count(self):
        try:
            result = subprocess.run(['wmctrl', '-d'], capture_output=True, text=True)
            return len([l for l in result.stdout.splitlines() if l.strip()])
        except Exception:
            return 1

    def create_and_switch_workspace(self):
        try:
            subprocess.run(['sh', '-c', 'wmctrl -n $(($(wmctrl -d | wc -l) + 1)) && wmctrl -s $(($(wmctrl -d | wc -l) - 1))'])
        except: pass

    def handle_gesture_begin(self, fingers, gesture_type='swipe'):
        self.fingers_down = fingers
        self.gesture_type = gesture_type
        self.last_x = 0
        self.last_y = 0
        self.action_triggered = False
        self.direction_determined = False
        if fingers in (3,4) and gesture_type == 'swipe':
            self.gesture_active = True

    def handle_tap(self, fingers):
        if fingers == 3 and not self.action_triggered:
            self.middle_click()
            self.action_triggered = True

    def handle_gesture_update(self, fingers, dx, dy):
        if not self.gesture_active or self.action_triggered:
            return

        self.last_x += dx
        self.last_y += dy

        if fingers == 3:

            if not self.direction_determined:
                if abs(self.last_x) < 20 and abs(self.last_y) < 20:
                    return

                if abs(self.last_y) > abs(self.last_x) + 25:
                    self.direction = 'vertical'
                    self.direction_determined = True
                    self.last_x = 0
                    return

                if abs(self.last_x) > abs(self.last_y) + 25:
                    self.direction = 'horizontal'
                    self.direction_determined = True
                    self.last_y = 0
                    return

                return

            if self.direction == 'vertical':
                self.last_x = 0

                if self.last_y < -self.min_delta:
                    self.workspace_down()
                    self.action_triggered = True
                    self.gesture_active = False
                elif self.last_y > self.min_delta:
                    self.show_desktop()
                    self.action_triggered = True
                    self.gesture_active = False
                return

            if self.direction == 'horizontal':
                self.last_y = 0

                horizontal_needed = self.min_delta + self.horizontal_threshold_extra

                if not self.alt_pressed:
                    self.press_alt()

                if self.last_x > horizontal_needed:
                    self.tab_next()
                    self.last_x = 0

                elif self.last_x < -horizontal_needed:
                    self.tab_prev()
                    self.last_x = 0

                return

        elif fingers == 4:
            if abs(self.last_y) > abs(self.last_x):

                if self.last_y < -self.min_delta:
                    self.workspace_up()
                    self.gesture_active = False
                    self.action_triggered = True
                    self.last_y = 0

                elif self.last_y > self.min_delta:
                    self.screenshot()
                    self.gesture_active = False
                    self.action_triggered = True
                    self.last_y = 0

            else:

                if self.last_x > self.min_delta:
                    self.workspace_left()
                    self.gesture_active = False
                    self.action_triggered = True
                    self.last_x = 0

                elif self.last_x < -self.min_delta:
                    current = self.get_current_workspace()
                    total = self.get_workspace_count()
                    if current >= total - 1:
                        self.create_and_switch_workspace()
                    else:
                        self.workspace_right()
                    self.gesture_active = False
                    self.action_triggered = True
                    self.last_x = 0

            return

    def handle_gesture_end(self):
        if self.gesture_active:
            self.release_alt()
            self.gesture_active = False
        self.fingers_down = 0
        self.last_x = 0
        self.last_y = 0
        self.gesture_type = None
        self.action_triggered = False
        self.direction_determined = False

def parse_libinput_events():
    handler = GestureHandler()
    
    try:
        process = subprocess.Popen(
            ['stdbuf', '-oL', 'libinput', 'debug-events'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
            bufsize=1
        )
    except FileNotFoundError:
        return
    
    if process.stdout is None:
        return
    
    for line in process.stdout:
        line = line.strip()
        
        if 'GESTURE_SWIPE_BEGIN' in line:
            match = re.search(r'GESTURE_SWIPE_BEGIN.*\s+(\d+)\s*$', line)
            if match:
                fingers = int(match.group(1))
                handler.handle_gesture_begin(fingers, 'swipe')
        
        elif 'GESTURE_PINCH_BEGIN' in line:
            match = re.search(r'GESTURE_PINCH_BEGIN.*\s+(\d+)\s*$', line)
            if match:
                fingers = int(match.group(1))
                handler.handle_gesture_begin(fingers, 'pinch')
        
        elif 'GESTURE_SWIPE_UPDATE' in line:
            match = re.search(r'GESTURE_SWIPE_UPDATE.*\s+(\d+)\s+(-?\d+\.\d+)/\s*(-?\d+\.\d+)', line)
            if match:
                fingers = int(match.group(1))
                dx = float(match.group(2))
                dy = float(match.group(3))
                handler.handle_gesture_update(fingers, dx, dy)
        
        elif 'GESTURE_SWIPE_END' in line or 'GESTURE_PINCH_END' in line:
            handler.handle_gesture_end()
        
        elif 'GESTURE_TAP_BEGIN' in line:
            match = re.search(r'GESTURE_TAP_BEGIN.*\s+(\d+)\s*$', line)
            if match:
                fingers = int(match.group(1))
                handler.handle_tap(fingers)

if __name__ == '__main__':
    try:
        parse_libinput_events()
    except KeyboardInterrupt:
        pass
    except Exception:
        pass