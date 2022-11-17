# Astro-Attack


# TODO:
Make turning more snappy

Adjust ship accleration (so faster if forward, slower if side to side)

Make ship more detailed, have cross in the centre
Make ship smaller

Add alien ship class

Add player health

Add ship colliding with asteroids

Make bullet fire from the front of the ship

Add animation framework

Add stars in background, layered, which move

### POTENTIAL ###

Add money system, different currencies, get cash from killing

Add shop system

Add loot system

Add fuel system


# DONE:
Fix angle, so it is between +180 and -180

CHUNKS is globalled in objects.py

When updating entities, don't update every entity's chunk 
In entity.update(), if the entity moved, put entity into it's new chunk

Add asteroid class

Add rotation acceleration, so red_ship doesn't immediately stop rotating