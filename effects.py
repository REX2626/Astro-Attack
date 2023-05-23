from objects import Vector
import particles
import game
import math



def damage(position, damage):
    particles.ParticleSystem(position, start_size=3, max_start_size=5, end_size=1, colour=(200, 0, 0), max_colour=(255, 160, 0), duration=None, lifetime=0.4, frequency=int(30*damage+1), speed=240, speed_variance=80)

def explosion(position):
    particles.ParticleSystem(position, start_size=10, max_start_size=35, end_size=2, colour=(200, 0, 0), max_colour=(255, 160, 0), bloom=0.6, duration=None, lifetime=0.5, frequency=20, speed=220, speed_variance=100)
    particles.ParticleSystem(position, start_size=15, max_start_size=25, end_size=1, colour=game.DARK_GREY, duration=None, lifetime=0.3, frequency=10, speed=120, speed_variance=60)

def asteroid_debris(position):
    particles.ParticleSystem(position, start_size=10, end_size=0, colour=game.DARK_GREY, duration=None, lifetime=0.3, frequency=20, speed=200, speed_variance=40)

def missile_trail(entity) -> particles.ParticleSystem:
    boost_distance = 12
    boost_position = lambda missile: Vector(boost_distance * math.sin(missile.rotation), boost_distance * math.cos(missile.rotation))

    return particles.ParticleSystem(entity, entity_offset=boost_position, start_size=4, end_size=0, colour=(207, 207, 220), duration=None, lifetime=0.4, frequency=150, speed_variance=50, initial_velocity=lambda missile: Vector(0, 700).get_rotate(entity.rotation)+missile.velocity)

def missile_ship_trail(entity) -> particles.ParticleSystem:
    boost_distance = 20
    boost_position = lambda ship: Vector(boost_distance * math.sin(ship.rotation), boost_distance * math.cos(ship.rotation))

    return particles.ParticleSystem(entity, entity_offset=boost_position, start_size=4, end_size=0, colour=(207, 77, 17), bloom=1, duration=None, lifetime=0.5, frequency=150, initial_velocity=lambda ship: Vector(0, 400).get_rotate(ship.rotation)+ship.velocity)
