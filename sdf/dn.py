import numpy as np

_min = np.minimum
_max = np.maximum

def union(a, *bs, k=None):
    def f(p):
        d1 = a(p)
        for b in bs:
            d2 = b(p)
            K = k or getattr(b, '_k', None)
            if K is None:
                d1 = _min(d1, d2)
            else:
                h = np.clip(0.5 + 0.5 * (d2 - d1) / K, 0, 1)
                m = d2 + (d1 - d2) * h
                d1 = m - K * h * (1 - h)
        return d1
    return f

def difference(a, *bs, k=None):
    def f(p):
        d1 = a(p)
        for b in bs:
            d2 = b(p)
            K = k or getattr(b, '_k', None)
            if K is None:
                d1 = _max(d1, -d2)
            else:
                h = np.clip(0.5 - 0.5 * (d2 + d1) / K, 0, 1)
                m = d1 + (-d2 - d1) * h
                d1 = m + K * h * (1 - h)
        return d1
    return f

def intersection(a, *bs, k=None):
    def f(p):
        d1 = a(p)
        for b in bs:
            d2 = b(p)
            K = k or getattr(b, '_k', None)
            if K is None:
                d1 = _max(d1, d2)
            else:
                h = np.clip(0.5 - 0.5 * (d2 - d1) / K, 0, 1)
                m = d2 + (d1 - d2) * h
                d1 = m + K * h * (1 - h)
        return d1
    return f

def blend(a, *bs, k=0.5):
    def f(p):
        d1 = a(p)
        for b in bs:
            d2 = b(p)
            K = k or getattr(b, '_k', None)
            d1 = K * d2 + (1 - K) * d1
        return d1
    return f

def negate(other):
    def f(p):
        return -other(p)
    return f

def shell(other, thickness):
    def f(p):
        return np.abs(other(p)) - thickness
    return f

def repeat(other, spacing, count=None, stagger=False):
    count = np.array(count) if count is not None else None
    spacing = np.array(spacing)
    def f(p):
        if count is None:
            i = np.round(p / spacing)
        else:
            i = np.clip(np.round(p / spacing), -count, count)
        if stagger:
            # TODO: more configurable staggering
            i1 = np.where((i[:,0] % 2 == 0).reshape((-1, 1)), i, i + [0, 0.5, 0])
            i2 = np.where((i[:,0] % 2 == 0).reshape((-1, 1)), i, i - [0, 0.5, 0])
            q1 = p - spacing * i1
            q2 = p - spacing * i2
            d1 = other(q1)
            d2 = other(q2)
            return _min(d1, d2)
        q = p - spacing * i
        return other(q)
    return f
