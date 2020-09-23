import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sharpcvi2",
    version="1.0.0",
    author="CVI2: Computer Vision, Imaging and Machine Intelligence Research Group",
    author_email="shapify3D@uni.lu",
    description="Routines for the SHARP Challenge, ECCV 2020",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://cvi2.uni.lu/sharp2020/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
