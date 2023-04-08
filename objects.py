import pygame
import math
import images
import game
import random



class Vector1D():
    def __init__(self, x) -> None:
        self.x = x

    def __add__(self, arg):

        # Adding Vectors
        if type(arg) == Vector1D:
            return Vector1D(self.x + arg.x)

        # Adding Vector and number
        else:
            return Vector1D(self.x + arg)

    def __radd__(self, arg):
        return self.x + arg

    def __sub__(self, arg):
        return Vector1D(self.x - arg.x)

    def __mul__(self, arg):

        # Multiplying Vectors
        if type(arg) == Vector1D:
            return Vector1D(self.x * arg.x)

        # Multiplying Vector by int
        else:
            return Vector1D(self.x * arg)

    def __truediv__(self, arg):

        # Vector divided by Vector
        if type(arg) == Vector1D:
            return Vector1D(self.x / arg.x)

        # Vector divided by number
        else:
            return Vector1D(self.x / arg)

    def magnitude(self):
        return abs(self.x)

    def set_magnitude(self, magnitude):
        new_vector = self * magnitude / self.magnitude()
        self.x = new_vector.x

    def clamp(self, maximum):
        if self.magnitude() > maximum:
            self.set_magnitude(maximum)

    def get_clamp(self, maximum):
        if self.magnitude() > maximum:
            # Set magnitude to maximum
            return self * maximum / self.magnitude()
        return self



class Vector():
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y

    def __add__(self, arg):

        # Adding Vectors
        if type(arg) == Vector:
            return Vector(self.x + arg.x, self.y + arg.y)

        # Adding Vector to Scalar
        else:
            return Vector(self.x + arg, self.y + arg)

    def __truediv__(self, arg):

        # Dividing Vectors
        if type(arg) == Vector:
            return Vector(self.x / arg.x, self.y / arg.y)
        
        # Dividing Vector by Scalar
        else:
            return Vector(self.x / arg, self.y / arg)

    def __rtruediv__(self, arg):
        
        # arg can't be a Vector
        return Vector(self.x / arg, self.y / arg)

    def __floordiv__(self, arg):

        # Dividing Vector by Scalar
        return Vector(int(self.x // arg), int(self.y // arg))
    
    def __sub__(self, arg):

        # Subtracting Vectors
        if type(arg) == Vector:
            return Vector(self.x - arg.x, self.y - arg.y)
        
        # Subtracting Scalar from Vector
        else:
            return Vector(self.x - arg, self.y - arg)

    def __mul__(self, arg):

        # Multiplying Vectors
        if type(arg) == Vector:
            return Vector(self.x * arg.x, self.y * arg.y)

        # Multiplying Vector with Scalar
        else:
            return Vector(self.x * arg, self.y * arg)

    def __rmul__(self, arg):

        # arg can't be a Vector
        return Vector(self.x * arg, self.y * arg)

    def __mod__(self, arg):
        return Vector(int(self.x) % arg, int(self.y) % arg)

    def __repr__(self):
        return str((self.x, self.y))

    def __round__(self):
        return Vector(round(self.x), round(self.y))

    def clamp(self, maximum):
        if self.magnitude() > maximum:
            self.set_magnitude(maximum)

    def get_clamp(self, maximum):
        if self.magnitude() > maximum:
            # Set magnitude to maximum
            return self * maximum / self.magnitude()
        return self

    def magnitude(self):
        return (self.x**2 + self.y**2) ** 0.5

    def set_magnitude(self, magnitude):
        # cringe way of updating self
        # can't do "self = new_vector" as self is just a variable
        new_vector = self * magnitude / self.magnitude()
        self.x = new_vector.x
        self.y = new_vector.y

    def get_angle_to(self, position):
        angle = math.atan((-position.y + self.y) / (position.x - self.x))
        return angle - math.pi/2 if self.x < position.x else angle + math.pi/2

    def get_angle(self):
        """Get's the Vector's angle from the origin"""
        return math.atan2(self.y, self.x)

    def rotate(self, angle):
        x1, y1 = self.x, self.y
        # The positive and negative signs are different
        # Because y increases downwards (for our coord system)
        self.x = y1*math.sin(angle) + x1*math.cos(angle)
        self.y = y1*math.cos(angle) - x1*math.sin(angle)

    def get_rotate(self, angle):
        x1, y1 = self.x, self.y
        # The positive and negative signs are different
        # Because y increases downwards (for our coord system)
        x = y1*math.sin(angle) + x1*math.cos(angle)
        y = y1*math.cos(angle) - x1*math.sin(angle)
        return Vector(x, y)

    def rotate_about(self, angle, position):
        self.x -= position.x
        self.y -= position.y
        self.rotate(angle)
        self.x += position.x
        self.y += position.y

    def copy(self):
        return Vector(self.x, self.y)

    def in_range(self, x, y, width, height):
        return self.x >= x and self.x <= x + width and self.y >= y and self.y <= y + height
    
    def to_tuple(self):
        return (self.x, self.y)



def random_vector(magnitude: float) -> Vector:
    """Returns a vector with random direction and given magnitude"""
    random_direction = random.random() * 2 * math.pi    # Get random direction

    random_vector = Vector(magnitude * math.cos(random_direction), magnitude * math.sin(random_direction))  # Get random vector with magnitude
    
    return random_vector



class Object():
    def __init__(self, position, image=lambda: images.DEFAULT) -> None:
        
        # Make position a vector
        if type(position) != Vector:
            self.position = Vector(position[0], position[1])
        else:
            self.position: Vector = position
        
        self.image = image()

        self.load_image = image # a function that returns a pygame Surface
        self.scale = 1
        self.scaled_image = self.image

        # Set the size (dimensions), original size of image, doesn't change when rotating
        self.size = Vector(self.image.get_width(), self.image.get_height())
    
    def __setstate__(self, state):
        self.__dict__.update(state)
        self.image = self.load_image()
        self.scaled_image = pygame.transform.scale_by(self.image, self.scale)
        
    def update(self, delta_time):
        pass

    def distance_to(self, object):
        return (self.position - object.position).magnitude()

    def get_zoomed_image(self):
        if self.scale != game.ZOOM:
            # if self.scaled_image isn't the right scale -> recalculate the scaled_image
            self.scale = game.ZOOM
            self.scaled_image = pygame.transform.scale_by(self.image, self.scale)

        return self.scaled_image

    def draw(self, win: pygame.Surface, focus_point):
        image = self.get_zoomed_image()
        offset = game.CENTRE_POINT - Vector(image.get_width(), image.get_height()) * 0.5
        win.blit(image, (round((self.position - focus_point) * game.ZOOM + offset)).to_tuple())



class MoveableObject(Object):
    def __init__(self, position, velocity, image=lambda: images.DEFAULT) -> None:
        super().__init__(position, image)

        # Make velocity a vector
        if type(velocity) != Vector:
            self.velocity = Vector(velocity[0], velocity[1])
        else:
            self.velocity: Vector = velocity

    def update(self, delta_time):

        game.CHUNKS.move_entity(self, delta_time)

    def move_towards(self, target_position, speed):

        self.velocity = target_position - self.position
        self.velocity.set_magnitude(speed)


class Entity(MoveableObject):
    def __init__(self, position, velocity, rotation=0, image=lambda: images.DEFAULT) -> None:
        super().__init__(position, velocity, image)

        # self.rotation is stored as radians
        self.rotation = rotation
        self.image_rotation = 0
        self.rotated_image = self.image
        self.set_rotation(rotation)
    
    def __setstate__(self, state):
        super().__setstate__(state)
        self.rotated_image = pygame.transform.rotate(self.scaled_image, self.rotation / math.pi * 180)

    def set_rotation(self, rotation):
        self.rotation = rotation

    def rotate_to(self, delta_time, rotation, speed):   
        # Simplify rotation (if self.rotation < -math.pi or self.rotation > math.pi)
        self.rotation = (self.rotation - math.pi) % (2*math.pi) - math.pi

        # Choose shortest angle to rotate
        if self.rotation + math.pi < rotation:
            self.rotation += 2 * math.pi
        elif self.rotation - math.pi > rotation:
            self.rotation -= 2 * math.pi

        # Change rotation (set to wanted to rotation when reached)
        if rotation < self.rotation:
            self.rotation = max(rotation, self.rotation - speed * delta_time)
        else:
            self.rotation = min(rotation, self.rotation + speed * delta_time)

    def accelerate(self, acceleration: Vector):
        self.velocity += acceleration

    def accelerate_to(self, target_position: Vector, magnitude: float):
        acceleration = target_position - self.position
        acceleration.set_magnitude(magnitude)
        self.accelerate(acceleration)

    def accelerate_in_direction(self, angle: float, magnitude: float):
        self.accelerate(Vector(-math.sin(angle)*magnitude, -math.cos(angle)*magnitude))

    def accelerate_onto_pos(self, target_position: Vector, max_acceleration: float, max_speed: float):
        distance_to_target = (self.position - target_position).magnitude()

        distance_to_decelerate_from_max = (max_speed)**2 / (2 * 200) # 200 is the value for inertial dampening
        #distance_to_decelerate = -(self.velocity.magnitude())**2 / (2 * max_acceleration)

        if distance_to_target < distance_to_decelerate_from_max:
            # Let inertial dampening slow the entity down
            return
        else:
            self.accelerate_to(target_position, max_acceleration)

    def get_image(self):
        if self.scale != game.ZOOM:
            # if self.scaled_image isn't the right scale -> recalculate the scaled_image
            self.scale = game.ZOOM
            self.scaled_image = pygame.transform.scale_by(self.image, self.scale)

            # if image has been rescaled, then it will also need to be rotated again
            self.image_rotation = self.rotation
            self.rotated_image = pygame.transform.rotate(self.scaled_image, self.rotation / math.pi * 180)

            return self.rotated_image
        
        if self.image_rotation != self.rotation:
            self.image_rotation = self.rotation
            self.rotated_image = pygame.transform.rotate(self.scaled_image, self.rotation / math.pi * 180)

        return self.rotated_image

    def draw(self, win: pygame.Surface, focus_point):
        image = self.get_image()
        offset = game.CENTRE_POINT - Vector(image.get_width(), image.get_height()) * 0.5
        win.blit(image, (round((self.position - focus_point) * game.ZOOM + offset)).to_tuple())