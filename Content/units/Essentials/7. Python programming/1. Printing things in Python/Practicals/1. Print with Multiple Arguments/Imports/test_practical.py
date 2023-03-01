def check_step_1(
    age: int,
) -> None:
    assert isinstance(age, int), "The variable 'age' should be an integer."
    print("Well done!")

def check_step_2(
    your_code: str,
) -> None:
    assert "Age" in your_code, "Your print statement should contain the word 'Age'"
    assert "Age:" in your_code, "Your print statement should contain the word 'Age' followed by a colon"
    assert "age" in your_code, "Your print statement should contain the variable 'age'"
    print("Well done!")

def check_step_3(
    name: str,
) -> None:
    assert isinstance(name, str), "The variable 'name' should be a string."
    print("Well done!")

def check_step_4(
    your_code: str,
) -> None:
    assert "My name is" in your_code, "Your print statement should contain the phrase 'My name is'"
    assert "name" in your_code, "Your print statement should contain the variable 'name'"
    assert "and I am" in your_code, "Your print statement should contain the phrase 'and I am'"
    assert "age" in your_code, "Your print statement should contain the variable 'age'"
    print("Well done!")