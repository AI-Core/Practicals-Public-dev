import setuptools

setuptools.setup(
    name="movie-rec-marking-aicore",
    version="0.1.2",
    author="Ivan Ying",
    author_email="ivan@theaicore.com",
    description="An automated marking system for the movie recommendation project",
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    install_requires=[
        'urllib3',
        'timeout-decorator',
    ]
)