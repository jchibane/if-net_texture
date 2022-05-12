import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sharp-cvi2-artec3d",
    version="3.0.0",
    author="CVI2: Computer Vision, Imaging and Machine Intelligence Research Group & Artec3D",
    author_email="shapify3D@uni.lu",
    description="Routines for the 3rd SHARP Challenge, CVPR 2022",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://cvi2.uni.lu/sharp2022/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'numpy', 'open3d==0.10', 'argparse',
        'opencv-python', 'nptyping', 'moderngl', 'pathlib', 'scipy'
        #use --allow-unverified
    ],

)
