# Astro-Attack


TODO:
Adjust ship accleration (so faster if forward, slower if side to side)

Add ship colliding with asteroids

Add alien class

Add rendering order


DONE:
Fix angle, so it is between +180 and -180

CHUNKS is globalled in objects.py

When updating entities, don't update every entity's chunk 
In entity.update(), if the entity moved, put entity into it's new chunk

Add asteroid class

Add rotation acceleration, so red_ship doesn't immediately stop rotating