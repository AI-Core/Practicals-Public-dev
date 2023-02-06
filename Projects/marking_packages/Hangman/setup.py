import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hangman-marking-aicore",
    version="1.1.24",
    author="Ivan Ying",
    author_email="ivan@theaicore.com",
    description="An automated marking system for the hangman project",
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=['requests', 'timeout-decorator']
)