from objects import Object
import images



class Effect(Object):
    def __init__(self, position, image=images.DEFAULT) -> None:
        super().__init__(position, image)



class Explosion(Effect):
    def __init__(self, position, image=images.DEFAULT) -> None:
        super().__init__(position, image)