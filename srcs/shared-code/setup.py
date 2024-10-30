from setuptools import setup, find_packages

setup(
    name="lib-transcendence",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "requests",
        "django",
        "djangorestframework",
    ],
    author="fguirama",
    description="Temporary lib for dev ft_transcendence.",
    python_requires=">=3.10",
)
