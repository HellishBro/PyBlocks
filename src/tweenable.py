from typing import Callable

class Tweenable:
    def __init__(self, tween_type: Callable[[float], float], init_val: float, duration: float):
        self.tween_type = tween_type
        self.prev_val = init_val
        self.next_val = init_val
        self.duration = duration
        self.t = 0

    def ended(self) -> bool:
        return self.prev_val == self.next_val

    def reset_to(self, value: float):
        self.prev_val = value
        self.next_val = value
        self.t = 0

    def new_target(self, value: float):
        self.prev_val = self.get_value()
        self.next_val = value
        self.t = 0

    def get_value(self) -> float:
        if self.prev_val == self.next_val:
            return self.prev_val
        return self.tween_type(self.t / self.duration) * (self.next_val - self.prev_val) + self.prev_val

    def next(self, dt: float) -> float:
        if self.prev_val == self.next_val:
            return self.prev_val

        self.t += dt
        if self.t > self.duration:
            self.reset_to(self.next_val)

        return self.get_value()
