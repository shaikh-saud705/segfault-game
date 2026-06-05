import random

from .. import constants as C
from ..utils import clamp, lerp


class Camera:
    """Deadzone follow camera clamped to world bounds, with screen shake."""

    def __init__(self, view_w, view_h):
        self.x = 0.0
        self.y = 0.0
        self.vw = view_w
        self.vh = view_h
        self.shake_mag = 0.0

    def resize(self, view_w, view_h):
        self.vw = view_w
        self.vh = view_h

    def add_shake(self, mag):
        self.shake_mag = min(22.0, self.shake_mag + mag)

    @property
    def offset(self):
        if self.shake_mag > 0:
            return (int(self.x + random.uniform(-self.shake_mag, self.shake_mag)),
                    int(self.y + random.uniform(-self.shake_mag, self.shake_mag)))
        return (int(self.x), int(self.y))

    def snap_to(self, tx, ty):
        self.x = tx - self.vw / 2
        self.y = ty - self.vh / 2
        self._clamp()

    def update(self, target_x, target_y):
        # deadzone box centred on screen
        cx = self.x + self.vw / 2
        cy = self.y + self.vh / 2
        dzw = C.CAMERA_DEADZONE_W / 2
        dzh = C.CAMERA_DEADZONE_H / 2

        desired_x, desired_y = self.x, self.y
        if target_x < cx - dzw:
            desired_x = self.x - (cx - dzw - target_x)
        elif target_x > cx + dzw:
            desired_x = self.x + (target_x - (cx + dzw))
        if target_y < cy - dzh:
            desired_y = self.y - (cy - dzh - target_y)
        elif target_y > cy + dzh:
            desired_y = self.y + (target_y - (cy + dzh))

        self.x = lerp(self.x, desired_x, C.CAMERA_LERP)
        self.y = lerp(self.y, desired_y, C.CAMERA_LERP)
        self._clamp()

        # decay shake
        if self.shake_mag > 0:
            self.shake_mag *= 0.82
            if self.shake_mag < 0.5:
                self.shake_mag = 0.0

    def _clamp(self):
        max_x = max(0, C.WORLD_WIDTH - self.vw)
        max_y = max(0, C.WORLD_HEIGHT - self.vh)
        self.x = clamp(self.x, 0, max_x)
        self.y = clamp(self.y, 0, max_y)
