# Astro-Attack


## TODO:
Add de-spawning, e.g. bullets

Fix speed instant decellerating when stopping boosting

Make enemies turn smoothly

Add 2 more asteroid images

Patrol state: improve grouping with mothership

Attack state: make fighting seem more natural

Enemy health: Add health to enemy ships

Retreat state: If enemy health is low and player health is high - retreat

Add ship colliding with asteroids
Ship will bounce off
Ship will take damage proportional to speed^2

Make ships have a thruster animation

Add boost animation to ship and particle effect

Add targeting icon (space engineers)

Add auto-aim, if targeting icon near ship, then it gets closer (making aiming nicer)

### POTENTIAL

Have different shoot speed for enemy and player

Add money system, different currencies, get cash from killing

Add shop system

Add loot system

Add fuel system


## DONE:
Make Enemy ships move around

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

Make Enemy only shoot when close to red_ship

Add stars in background, layered, which move

Dampen intertia before moving, so that acceleration is dampened 1 tick later, not straight away

Improve star drawing code, so stars aren't brute force placed around the side

Improve bullet shooting, so that the position the bullet is spawned at is relative to the size of the ship

Add score counter

Stop spawning anything in starting chunks

Add zoom

Don't blit objects which will not be on the screen

Limit the zooming in and out based on the chunk distance
Make Enemy ships move around

Make all artwork the same scale

Improve asteroid image, add several asteroid images

Enemy Grouping