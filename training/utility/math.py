from rlbot.utils.game_state_util import Vector3
from math import sqrt, pow


class Vec3:
    def __init__(self, *args):
        arglength = len(args)
        if arglength == 0:
            self.x = self.y = self.z = 0
        if arglength == 1:
            if isinstance(args[0], int):
                self.x = self.y = self.z = args[0]
            if isinstance(args[0], Vector3):
                self.x = args[0].x
                self.y = args[0].y
                self.z = args[1].z
        if arglength == 3:
            self.x = args[0]
            self.y = args[1]
            self.z = args[2]

    def __add__(self, vec):
        if isinstance(vec, int):
            return Vec3(self.x + vec, self.y + vec, self.z + vec)
        return Vec3(self.x + vec.x, self.y + vec.y, self.z + vec.z)

    def __sub__(self, vec):
        if isinstance(vec, int):
            return Vec3(self.x - vec, self.y - vec, self.z - vec)
        return Vec3(self.x - vec.x, self.y - vec.y, self.z - vec.z)

    def __truediv__(self, scalar):
        return Vec3(self.x / scalar, self.y / scalar, self.z / scalar)

    def __mul__(self, scalar):
        return Vec3(self.x * scalar, self.y * scalar, self.z * scalar)

    def cross(self, vec):
        return Vec3(self.y * vec.z - self.z * vec.y, self.z * vec.x - self.x * vec.z, self.x * vec.y - self.y * vec.x)

    def dot(self, vec):
        return self.x * vec.x + self.y * vec.y + self.z * vec.z

    def length(self):
        return pow(self.x, 2) + pow(self.y, 2) + pow(self.z, 2)

    def norm(self):
        return sqrt(self.length())

    def normalize(self):
        return self / self.norm()

    def __str__(self):
        return "Vec3({0}, {1}, {2})".format(self.x, self.y, self.z)

    def __lt__(self, vec):
        return self.length() < vec.length()

    def __gt__(self, vec):
        return self.length() > vec.length()

    def __eq__(self, vec):
        return self.x == vec.x and self.y == vec.y and self.z == vec.z

    def toRLVec(self):
        return Vector3(self.x, self.y, self.z)
