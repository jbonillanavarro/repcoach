"""Smoothers for noisy angle readings and raw landmark positions."""

import math
from collections import deque
from types import SimpleNamespace


class MovingAverage:
    def __init__(self, window=5):
        self.window = window
        self.values = deque(maxlen=window)

    def update(self, value):
        if value is None:
            return None
        self.values.append(value)
        return sum(self.values) / len(self.values)


def _alpha(t_e, cutoff):
    r = 2 * math.pi * cutoff * t_e
    return r / (r + 1)


class OneEuroFilter:
    """Adaptive low-pass filter (Casiez et al., 2012): smooths hard when a
    signal is nearly still (kills jitter), and backs off smoothing when it's
    moving fast (kills lag) - unlike a fixed-alpha EMA which trades one for
    the other everywhere.
    """

    def __init__(self, t0, x0, min_cutoff=1.0, beta=0.3, d_cutoff=1.0):
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.x_prev = x0
        self.dx_prev = 0.0
        self.t_prev = t0

    def __call__(self, t, x):
        t_e = max(t - self.t_prev, 1e-3)

        a_d = _alpha(t_e, self.d_cutoff)
        dx = (x - self.x_prev) / t_e
        dx_hat = a_d * dx + (1 - a_d) * self.dx_prev

        cutoff = self.min_cutoff + self.beta * abs(dx_hat)
        a = _alpha(t_e, cutoff)
        x_hat = a * x + (1 - a) * self.x_prev

        self.x_prev, self.dx_prev, self.t_prev = x_hat, dx_hat, t
        return x_hat


class LandmarkSmoother:
    """Runs a OneEuroFilter per x/y/z coordinate of each landmark."""

    def __init__(self, min_cutoff=1.2, beta=2.0, d_cutoff=1.0):
        self.min_cutoff = min_cutoff
        self.beta = beta
        self.d_cutoff = d_cutoff
        self.filters = None

    def _make_filter(self, t0, x0):
        return OneEuroFilter(t0, x0, self.min_cutoff, self.beta, self.d_cutoff)

    def update(self, landmarks, t):
        if landmarks is None:
            return None

        if self.filters is None:
            self.filters = [
                (self._make_filter(t, lm.x), self._make_filter(t, lm.y), self._make_filter(t, lm.z))
                for lm in landmarks
            ]
            return [
                SimpleNamespace(x=lm.x, y=lm.y, z=lm.z, visibility=lm.visibility)
                for lm in landmarks
            ]

        out = []
        for (fx, fy, fz), lm in zip(self.filters, landmarks):
            out.append(SimpleNamespace(
                x=fx(t, lm.x), y=fy(t, lm.y), z=fz(t, lm.z), visibility=lm.visibility,
            ))
        return out
