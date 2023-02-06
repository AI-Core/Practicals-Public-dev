import setuptools

setuptools.setup(
    name="computer-vision-marking-aicore",
    version="1.1.5",
    author="Ivan Ying",
    author_email="ivan@theaicore.com",
    description="An automated marking system for the computer vision scenario",
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=['requests', 'numpy', 'timeout-decorator']
)