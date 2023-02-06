

class Dog:

    def __init__(self, name, breed):
        self.name = name
        self.breed = breed

    def bark(self):
        name = "Jack"
        breed = "doberman"
        print(f"The dogs name is {name} and its breed is {breed}")


def bark():
    pass

sheepdog = Dog("Bob", "sheepdog")
collie = Dog("Anna", "Collie")
sheepdog.bark()
collie.bark()