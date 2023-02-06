# %%

class Player:
    def __init__(this_instance_of_the_class, name):
        print("initialising!")
        this_instance_of_the_class.name = name

    def hello(self):
        print(f"hello, my name is {self.name}")


player1 = Player("harry")
player1.hello()
player1.name

player2 = Player("jane")
john = Player("john")
# player2 = Player()

# %%
