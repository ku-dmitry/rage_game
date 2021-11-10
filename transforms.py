def transform(self, x, y):
    # return self.transform_2d(x, y)
    return self.perspective(x, y)


def transform_2d(x, y):
    """Flat view"""
    return x, y


def perspective(self, x, y):
    """Horizon view"""
    lin_y = self.perspective_point_y * y / self.height
    if lin_y > self.perspective_point_y:
        lin_y = self.perspective_point_y

    diff_x = x - self.perspective_point_x
    diff_y = self.perspective_point_y - lin_y
    factor_y = diff_y / self.perspective_point_y
    factor_y = factor_y ** 3
    tr_x = self.perspective_point_x + diff_x * factor_y
    tr_y = self.perspective_point_y - factor_y * self.perspective_point_y
    return int(tr_x), int(tr_y)


def warp(self, x, y):
    """Warped reality view"""
    pass
