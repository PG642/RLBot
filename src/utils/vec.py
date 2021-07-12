import math
from typing import Union

from rlbot.utils.game_state_util import Vector3, Rotator
from rlbot.utils.structures.game_data_struct import Rotator as GDRotator

from math import cos, sin

from enum import Enum


class UnitSystem(Enum):
    UNITY = 1,
    UNREAL = 2


class Vec3:
    """
    This class should provide you with all the basic vector operations that you need, but feel free to extend its
    functionality when needed.
    The vectors found in the GameTickPacket will be flat buffer vectors. Cast them to Vec3 like this:
    `car_location = Vec3(car.physics.location)`.

    Remember that the in-game axis are left-handed.

    When in doubt visit the wiki: https://github.com/RLBot/RLBot/wiki/Useful-Game-Values
    """
    # https://docs.python.org/3/reference/datamodel.html#slots
    __slots__ = [
        'x',
        'y',
        'z',
        'unit_system'
    ]

    def __init__(self, x: Union[float, 'Vec3', 'Vector3'] = 0, y: float = 0, z: float = 0,
                 unit_system: UnitSystem = UnitSystem.UNREAL):
        """
        Create a new Vec3. The x component can alternatively be another vector with an x, y, and z component, in which
        case the created vector is a copy of the given vector and the y and z parameter is ignored. Examples:

        a = Vec3(1, 2, 3)

        b = Vec3(a)

        """

        if hasattr(x, 'x'):
            # We have been given a vector. Copy it
            self.x = float(x.x)
            self.y = float(x.y) if hasattr(x, 'y') else 0
            self.z = float(x.z) if hasattr(x, 'z') else 0
        else:
            self.x = float(x)
            self.y = float(y)
            self.z = float(z)
        self.unit_system = unit_system

    def __getitem__(self, item: int):
        return (self.x, self.y, self.z)[item]

    def __add__(self, other: 'Vec3') -> 'Vec3':
        return Vec3(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other: 'Vec3') -> 'Vec3':
        return Vec3(self.x - other.x, self.y - other.y, self.z - other.z)

    def __neg__(self):
        return Vec3(-self.x, -self.y, -self.z)

    def __mul__(self, scale: float) -> 'Vec3':
        return Vec3(self.x * scale, self.y * scale, self.z * scale)

    def __rmul__(self, scale):
        return self * scale

    def __truediv__(self, scale: float) -> 'Vec3':
        scale = 1 / float(scale)
        return self * scale

    def __str__(self):
        return f"Vec3({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"

    def __repr__(self):
        return self.__str__()

    def flat(self):
        """Returns a new Vec3 that equals this Vec3 but projected onto the ground plane. I.e. where z=0."""
        return Vec3(self.x, self.y, 0)

    def length(self):
        """Returns the length of the vector. Also called magnitude and norm."""
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def dist(self, other: 'Vec3') -> float:
        """Returns the distance between this vector and another vector using pythagoras."""
        return (self - other).length()

    def normalized(self):
        """Returns a vector with the same direction but a length of one."""
        return self / self.length()

    def rescale(self, new_len: float) -> 'Vec3':
        """Returns a vector with the same direction but a different length."""
        return new_len * self.normalized()

    def dot(self, other: 'Vec3') -> float:
        """Returns the dot product."""
        return self.x * other.x + self.y * other.y + self.z * other.z

    def cross(self, other: 'Vec3') -> 'Vec3':
        """Returns the cross product."""
        return Vec3(
            self.y * other.z - self.z * other.y,
            self.z * other.x - self.x * other.z,
            self.x * other.y - self.y * other.x
        )

    def ang_to(self, ideal: 'Vec3') -> float:
        """Returns the angle to the ideal vector. Angle will be between 0 and pi."""
        cos_ang = self.dot(ideal) / (self.length() * ideal.length())
        return math.acos(cos_ang)

    def to_game_state_vector(self):
        return Vector3(self.x, self.y, self.z)


class Vec4:
    """
    This class should provide you with all the basic vector operations that you need, but feel free to extend its
    functionality when needed.
    The vectors found in the GameTickPacket will be flat buffer vectors. Cast them to Vec3 like this:
    `car_location = Vec4(car.physics.location)`.

    Remember that the in-game axis are left-handed.

    When in doubt visit the wiki: https://github.com/RLBot/RLBot/wiki/Useful-Game-Values
    """
    # https://docs.python.org/3/reference/datamodel.html#slots
    __slots__ = [
        'x',
        'y',
        'z',
        'w',
        'unit_system'
    ]

    def __init__(self, x: Union[float, 'Vec4'] = 0, y: float = 0, z: float = 0, w: float = 0,
                 unit_system: UnitSystem = UnitSystem.UNREAL):
        """
        Create a new Vec4. The x component can alternatively be another vector with an x, y, z and w component, in which
        case the created vector is a copy of the given vector and the y, z and w parameter are ignored. Examples:

        a = Vec4(1, 2, 3, 4)

        b = Vec4(a)

        """

        if hasattr(x, 'x'):
            # We have been given a vector. Copy it
            self.x = float(x.x)
            self.y = float(x.y) if hasattr(x, 'y') else 0
            self.z = float(x.z) if hasattr(x, 'z') else 0
            self.w = float(x.w) if hasattr(x, 'w') else 0
        else:
            self.x = float(x)
            self.y = float(y)
            self.z = float(z)
            self.w = float(w)
        self.unit_system = unit_system

    def __getitem__(self, item: int):
        return (self.x, self.y, self.z, self.w)[item]

    def __add__(self, other: 'Vec4') -> 'Vec4':
        return Vec4(self.x + other.x, self.y + other.y, self.z + other.z, self.w + other.w)

    def __sub__(self, other: 'Vec4') -> 'Vec4':
        return Vec4(self.x - other.x, self.y - other.y, self.z - other.z, self.w - other.w)

    def __neg__(self):
        return Vec4(-self.x, -self.y, -self.z, -self.w)

    def __mul__(self, scale: float) -> 'Vec4':
        return Vec4(self.x * scale, self.y * scale, self.z * scale, self.w * scale)

    def __rmul__(self, scale):
        return self * scale

    def __truediv__(self, scale: float) -> 'Vec4':
        scale = 1 / float(scale)
        return self * scale

    def __str__(self):
        return f"Vec4({self.x:.2f}, {self.y:.2f}, {self.z:.2f}, {self.w:.2f})"

    def __repr__(self):
        return self.__str__()

    def flat(self):
        """Returns a new Vec4 that equals this Vec4 but projected onto the ground plane. I.e. where z=0 and w=0."""
        return Vec4(self.x, self.y, 0, 0)

    def length(self):
        """Returns the length of the vector. Also called magnitude and norm."""
        return math.sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2 + self.w ** 2)

    def dist(self, other: 'Vec4') -> float:
        """Returns the distance between this vector and another vector using pythagoras."""
        return (self - other).length()

    def normalized(self):
        """Returns a vector with the same direction but a length of one."""
        return self / self.length()

    def rescale(self, new_len: float) -> 'Vec4':
        """Returns a vector with the same direction but a different length."""
        return new_len * self.normalized()

    def dot(self, other: 'Vec4') -> float:
        """Returns the dot product."""
        return self.x * other.x + self.y * other.y + self.z * other.z + self.w * other.w

    def cross(self, other: 'Vec4') -> 'Vec4':
        """Returns the cross product."""
        return Vec4(
            self.y * other.z - self.z * other.y,
            self.z * other.w - self.w * other.z,
            self.w * other.x - self.x * other.w,
            self.x * other.y - self.y * other.x
        )

    def ang_to(self, ideal: 'Vec4') -> float:
        """Returns the angle to the ideal vector. Angle will be between 0 and pi."""
        cos_ang = self.dot(ideal) / (self.length() * ideal.length())
        return math.acos(cos_ang)


class Location(Vec3):
    def to_unity_units(self) -> 'Location':
        if self.unit_system == UnitSystem.UNITY:
            return self

        tmp = self.x
        self.x = self.y
        self.y = self.z
        self.z = tmp
        self /= 100
        self.unit_system = UnitSystem.UNITY
        return self

    def to_unreal_units(self) -> 'Location':
        if self.unit_system == UnitSystem.UNREAL:
            return self

        tmp = self.z
        self.z = self.y
        self.y = self.x
        self.x = tmp
        self *= 100
        self.unit_system = UnitSystem.UNREAL
        return self


class Velocity(Vec3):
    def to_unity_units(self) -> 'Velocity':
        if self.unit_system == UnitSystem.UNITY:
            return self

        tmp = self.x
        self.x = self.y
        self.y = self.z
        self.z = tmp
        self /= 100
        self.unit_system = UnitSystem.UNITY
        return self

    def to_unreal_units(self) -> 'Velocity':
        if self.unit_system == UnitSystem.UNREAL:
            return self

        tmp = self.z
        self.z = self.y
        self.y = self.x
        self.x = tmp
        self *= 100
        self.unit_system = UnitSystem.UNREAL
        return self


class AngularVelocity(Vec3):
    def to_unity_units(self) -> 'AngularVelocity':
        if self.unit_system == UnitSystem.UNITY:
            return self

        tmp = self.x
        self.x = self.y
        self.y = self.z
        self.z = tmp
        self.unit_system = UnitSystem.UNITY
        return self

    def to_unreal_units(self) -> 'AngularVelocity':
        if self.unit_system == UnitSystem.UNREAL:
            return self

        tmp = self.z
        self.z = self.y
        self.y = self.x
        self.x = tmp
        self.unit_system = UnitSystem.UNREAL
        return self


class EulerAngles(Vec3):
    def __init__(self, pitch: Union[float, 'Quaternion', 'Rotator', 'GDRotator'] = 0, yaw: float = 0, roll: float = 0,
                 unit_system: UnitSystem = UnitSystem.UNREAL):
        super().__init__()
        if isinstance(pitch, Quaternion):
            q = pitch

            t0 = 2.0 * (q.w * q.y - q.z * q.x)
            t0 = 1.0 if t0 > +1.0 else t0
            t0 = -1.0 if t0 < -1.0 else t0
            self.x = math.degrees(math.asin(t0))

            t1 = 2.0 * (q.w * q.z + q.x * q.y)
            t2 = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
            self.y = math.degrees(math.atan2(t1, t2))

            t3 = 2.0 * (q.w * q.x + q.y * q.z)
            t4 = 1.0 - 2.0 * (q.x * q.x + q.y * q.y)
            self.z = math.degrees(math.atan2(t3, t4))
            self.unit_system = q.unit_system
        elif isinstance(pitch, (Rotator, GDRotator)):
            r = pitch
            self.x = r.pitch / math.pi * 180
            self.y = r.yaw / math.pi * 180
            self.z = r.roll / math.pi * 180
            self.unit_system = UnitSystem.UNREAL
        else:
            self.x = pitch
            self.y = yaw
            self.z = roll
            self.unit_system = UnitSystem.UNITY

    def to_unity_units(self) -> 'EulerAngles':
        if self.unit_system == UnitSystem.UNITY:
            return self
        self.x = (self.x > 0) * 360 - self.x
        self.y = (self.y > 0) * 360 - self.y
        self.z = (self.z > 0) * 360 - self.z
        self.unit_system = UnitSystem.UNITY
        return self

    #    if self.unit_system == UnitSystem.UNITY:
    #        return self
    #
    #     tmp = self.x
    #     self.x = self.y
    #     self.y = self.z
    #     self.z = tmp
    #     self.unit_system = UnitSystem.UNITY
    #     return self
    #
    def to_unreal_units(self) -> 'EulerAngles':
        self.unit_system = UnitSystem.UNREAL
        return self

    # if self.unit_system == UnitSystem.UNREAL:
    #     return self
    #
    #     tmp = self.z
    #     self.z = self.y
    #     self.y = self.x
    #     self.x = tmp
    #     self.unit_system = UnitSystem.UNREAL
    #     return self

    def to_game_state_vector(self):
        return Rotator(self.x / 180 * math.pi, self.y / 180 * math.pi, self.z / 180 * math.pi)


class Quaternion(Vec4):
    def __init__(self, x: Union[float, 'Quaternion', 'Rotator', 'GDRotator'] = 0, y: float = 0, z: float = 0,
                 w: float = 0, unit_system: UnitSystem = UnitSystem.UNREAL):
        super().__init__()
        if hasattr(x, 'pitch'):
            # x are euler angles
            cy = cos(x.yaw * 0.5)
            sy = sin(x.yaw * 0.5)
            cp = cos(x.pitch * 0.5)
            sp = sin(x.pitch * 0.5)
            cr = cos(x.roll * 0.5)
            sr = sin(x.roll * 0.5)

            self.x = sr * cp * cy - cr * sp * sy
            self.y = cr * sp * cy + sr * cp * sy
            self.z = cr * cp * sy - sr * sp * cy
            self.w = cr * cp * cy + sr * sp * sy
        elif hasattr(x, 'w'):
            # x is quaternion
            self.x = x.x
            self.y = x.y
            self.z = x.z
            self.w = x.w
        else:
            # x is scalar
            self.x = x
            self.y = y
            self.z = z
            self.w = w
        if isinstance(x, Quaternion):
            self.unit_system = x.unit_system
        else:
            self.unit_system = unit_system

    def to_unity_units(self) -> 'Quaternion':
        if self.unit_system == UnitSystem.UNITY:
            return self

        tmp = self.x
        self.x = self.y
        self.y = self.z
        self.z = tmp
        self.unit_system = UnitSystem.UNITY
        return self

    def to_unreal_units(self) -> 'Quaternion':
        if self.unit_system == UnitSystem.UNREAL:
            return self

        tmp = self.z
        self.z = self.y
        self.y = self.x
        self.x = tmp
        self.unit_system = UnitSystem.UNREAL
        return self
