from setuptools import setup, find_packages


with open("readme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


setup(
    name="langclient",
    version="0.1.1",
    description="Simple OpenAI language repl client",
    author="Juan Molina Riddell",
    author_email="jmriddell@protonmail.ch",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jmriddell/langclient",
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Natural Language :: English",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Utilities",
    ],
    packages=find_packages(),
    intall_requires=["openai", "pydantic"],
    entry_points=dict(console_scripts=["langclient=langclient.__main__:entrypoint"]),
)
