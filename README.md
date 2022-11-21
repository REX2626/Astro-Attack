# Astro-Attack


## TODO:
Make Enemy ships move around

Make Enemy only shoot when close to red_ship

Add ship colliding with asteroids

Add animation framework

Add stars in background, layered, which move

### POTENTIAL

Add money system, different currencies, get cash from killing

Add shop system

Add loot system

Add fuel system


## DONE:
Fix angle, so it is between +180 and -180

CHUNKS is globalled in objects.py

When updating entities, don't update every entity's chunk 
In entity.update(), if the entity moved, put entity into it's new chunk

Add asteroid class

Add rotation acceleration, so red_ship doesn't immediately stop rotating

Make turning more snappy

Adjust ship accleration (so faster if forward, slower if side to side)

Make bullet fire from the front of the ship

Add Images file

Make ship more detailed, have cross in the centre
Make ship smaller

Add a constants file (maybe class), so that any file can use any constant (without any circular import shenanigans)

Add player health

Add enemy ship class