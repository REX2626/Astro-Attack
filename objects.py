from __future__ import annotations
from typing import Iterator
import images
import game
import random
import math
import pygame



class Vector():
    __slots__ = ("x", "y")
    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def __add__(self, arg: Vector | float) -> Vector:

        # Adding Vectors
        if isinstance(arg, Vector):
            return Vector(self.x + arg.x, self.y + arg.y)

        # Adding Vector to Scalar
        else:
            return Vector(self.x + arg, self.y + arg)

    def __truediv__(self, arg: Vector | float) -> Vector:

        # Dividing Vectors
        if isinstance(arg, Vector):
            return Vector(self.x / arg.x, self.y / arg.y)

        # Dividing Vector by Scalar
        else:
            return Vector(self.x / arg, self.y / arg)

    def __rtruediv__(self, arg: float) -> Vector:

        # arg can't be a Vector
        return Vector(self.x / arg, self.y / arg)

    def __floordiv__(self, arg: float) -> Vector:

        # Dividing Vector by Scalar
        return Vector(int(self.x // arg), int(self.y // arg))

    def __sub__(self, arg: Vector | float) -> Vector:

        # Subtracting Vectors
        if isinstance(arg, Vector):
            return Vector(self.x - arg.x, self.y - arg.y)

        # Subtracting Scalar from Vector
        else:
            return Vector(self.x - arg, self.y - arg)

    def __mul__(self, arg: Vector | float) -> Vector:

        # Multiplying Vectors
        if isinstance(arg, Vector):
            return Vector(self.x * arg.x, self.y * arg.y)

        # Multiplying Vector with Scalar
        else:
            return Vector(self.x * arg, self.y * arg)

    def __rmul__(self, arg: float) -> Vector:

        # arg can't be a Vector
        return Vector(self.x * arg, self.y * arg)

    def __neg__(self) -> Vector:
        return Vector(-self.x, -self.y)

    def __bool__(self) -> bool:
        return bool(self.x) or bool(self.y)

    def __repr__(self) -> str:
        return str((self.x, self.y))

    def __round__(self) -> Vector:
        return Vector(round(self.x), round(self.y))

    def __iter__(self) -> Iterator[float]:
        yield self.x
        yield self.y

    def clamp(self, maximum: float) -> None:
        if self.magnitude() > maximum:
            self.set_magnitude(maximum)

    def get_clamp(self, maximum: float) -> Vector:
        if self.magnitude() > maximum:
            # Set magnitude to maximum
            return self * maximum / self.magnitude()
        return self

    def magnitude(self) -> float:
        return (self.x**2 + self.y**2) ** 0.5

    def set_magnitude(self, magnitude: float) -> None:
        factor = magnitude / self.magnitude()
        self.x *= factor
        self.y *= factor

    def with_magnitude(self, magnitude: float) -> Vector:
        if self.magnitude() == 0: return Vector(0, 0)
        return self * magnitude / self.magnitude()

    def get_angle_to(self, position: Vector) -> float:
        angle = math.atan((-position.y + self.y) / (position.x - self.x))
        return angle - math.pi/2 if self.x < position.x else angle + math.pi/2

    def get_angle(self) -> float:
        """Get's the Vector's angle from the origin"""
        return math.atan2(self.y, self.x)

    def rotate(self, angle: float) -> None:
        x1, y1 = self.x, self.y
        # The positive and negative signs are different
        # Because y increases downwards (for our coord system)
        self.x = y1*math.sin(angle) + x1*math.cos(angle)
        self.y = y1*math.cos(angle) - x1*math.sin(angle)

    def get_rotated(self, angle: float) -> Vector:
        x1, y1 = self.x, self.y
        # The positive and negative signs are different
        # Because y increases downwards (for our coord system)
        x = y1*math.sin(angle) + x1*math.cos(angle)
        y = y1*math.cos(angle) - x1*math.sin(angle)
        return Vector(x, y)

    def rotate_about(self, angle: float, position: Vector) -> None:
        self.x -= position.x
        self.y -= position.y
        self.rotate(angle)
        self.x += position.x
        self.y += position.y

    def dist_to(self, other: Vector) -> float:
        return (self - other).magnitude()

    def copy(self) -> Vector:
        return Vector(self.x, self.y)

    def in_range(self, x: float, y: float, width: float, height: float) -> bool:
        return self.x >= x and self.x <= x + width and self.y >= y and self.y <= y + height

    def to_tuple(self) -> tuple:
        return self.x, self.y



def random_vector(magnitude: float) -> Vector:
    """Returns a vector with random direction and given magnitude"""
    random_direction = random.random() * 2 * math.pi    # Get random direction

    random_vector = Vector(magnitude * math.cos(random_direction), magnitude * math.sin(random_direction))  # Get random vector with magnitude

    return random_vector



class Object():
    def __init__(self, position: Vector, image=lambda: images.DEFAULT) -> None:

        self.position = position
        self.image = image()

        self.load_image = image  # a function that returns a pygame Surface
        self.scale = 1
        self.scaled_image = self.image

        # Set the size (dimensions), original size of image, doesn't change when rotating
        self.size = Vector(self.image.get_width(), self.image.get_height())

    def __setstate__(self, state: dict) -> None:
        self.__dict__.update(state)
        self.image = self.load_image()
        self.scaled_image = pygame.transform.scale_by(self.image, self.scale)

    def update(self, delta_time: float) -> None:
        pass

    def distance_to(self, object: Object) -> float:
        return (self.position - object.position).magnitude()

    def get_zoomed_image(self) -> pygame.Surface:
        if self.scale != game.ZOOM:
            # if self.scaled_image isn't the right scale -> recalculate the scaled_image
            self.scale = game.ZOOM
            self.scaled_image = pygame.transform.scale_by(self.image, self.scale)

        return self.scaled_image

    def draw(self, win: pygame.Surface, focus_point: Vector) -> None:
        image = self.get_zoomed_image()
        offset = game.CENTRE_POINT - Vector(image.get_width(), image.get_height()) * 0.5
        win.blit(image, (round((self.position - focus_point) * game.ZOOM + offset)).to_tuple())



class MoveableObject(Object):
    def __init__(self, position: Vector, velocity: Vector, image=lambda: images.DEFAULT) -> None:
        super().__init__(position, image)

        self.velocity = velocity

    def update(self, delta_time: float) -> None:
        game.CHUNKS.move_entity(self, delta_time)

    def move_towards(self, target_position: Vector, speed: float) -> None:
        self.velocity = target_position - self.position
        self.velocity.set_magnitude(speed)


class Entity(MoveableObject):
    def __init__(self, position: Vector, velocity: Vector, rotation: float = 0, image=lambda: images.DEFAULT) -> None:
        super().__init__(position, velocity, image)

        # self.rotation is stored as radians, -pi < rotation < pi
        # 0 is upwards, +ve is anti-clockwise
        self.rotation = rotation
        self.image_rotation = 0
        self.rotated_image = self.image

    def __setstate__(self, state: dict) -> None:
        super().__setstate__(state)
        self.rotated_image = pygame.transform.rotate(self.scaled_image, math.degrees(self.rotation))

    def rotate_to(self, delta_time: float, rotation: float, speed: float) -> None:
        # Simplify rotation (-pi < self.rotation < pi)
        self.rotation = (self.rotation - math.pi) % (2*math.pi) - math.pi

        # Choose shortest angle to rotate
        if self.rotation + math.pi < rotation:
            self.rotation += 2 * math.pi
        elif self.rotation - math.pi > rotation:
            self.rotation -= 2 * math.pi

        # Change rotation (set to target rotation when reached)
        if rotation < self.rotation:
            self.rotation = max(rotation, self.rotation - speed * delta_time)
        else:
            self.rotation = min(rotation, self.rotation + speed * delta_time)

    def accelerate(self, acceleration: Vector) -> None:
        self.velocity += acceleration

    def accelerate_to(self, target_position: Vector, magnitude: float) -> None:
        acceleration = target_position - self.position
        acceleration.set_magnitude(magnitude)
        self.accelerate(acceleration)

    def accelerate_in_direction(self, angle: float, magnitude: float) -> None:
        self.accelerate(Vector(-math.sin(angle)*magnitude, -math.cos(angle)*magnitude))

    def accelerate_onto_pos(self, target_position: Vector, max_acceleration: float, max_speed: float) -> None:
        distance_to_target = (self.position - target_position).magnitude()

        acceleration = target_position - self.position
        acceleration.set_magnitude(max_acceleration)
        new_velocity = self.velocity + acceleration
        new_velocity.clamp(max_speed)

        distance_to_decelerate = (new_velocity.x**2 + new_velocity.y**2) / (2 * 200) # 200 is the value for inertial dampening

        if distance_to_target < distance_to_decelerate:
            # Let inertial dampening slow the entity down
            return
        else:
            self.velocity = new_velocity

    def get_image(self) -> pygame.Surface:
        if self.scale != game.ZOOM:
            # if self.scaled_image isn't the right scale -> recalculate the scaled_image
            self.scale = game.ZOOM
            self.scaled_image = pygame.transform.scale_by(self.image, self.scale)

            # if image has been rescaled, then it will also need to be rotated again
            self.image_rotation = self.rotation
            self.rotated_image = pygame.transform.rotate(self.scaled_image, math.degrees(self.rotation))

            return self.rotated_image

        if self.image_rotation != self.rotation:
            self.image_rotation = self.rotation
            self.rotated_image = pygame.transform.rotate(self.scaled_image, math.degrees(self.rotation))

        return self.rotated_image

    def draw(self, win: pygame.Surface, focus_point: Vector) -> None:
        image = self.get_image()
        offset = game.CENTRE_POINT - Vector(image.get_width(), image.get_height()) * 0.5
        win.blit(image, (round((self.position - focus_point) * game.ZOOM + offset)).to_tuple())
