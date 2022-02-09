from setuptools import find_packages, setup


URL = "https://github.com/gebauerm/ml_benchmark"
__version__ = "0.1.0"

install_requires = ["scikit-learn==0.24.2", "scipy==1.7.0", "torch", "tqdm==4.62.3", "rapidflow", "torchvision"],
test_require = ["pytest==6.2.5"]


setup(
    name='ml_benchmark',
    version=__version__,
    description='ml_benchmark - A ML-Job for Benchmarking.',
    license='MIT',
    author='Michael Gebauer',
    author_email='gebauerm23@gmail.com',
    url=URL,
    download_url=f'{URL}/archive/{__version__}.tar.gz',
    packages=find_packages(),
    install_requires=install_requires,
    extras_require={"test": test_require},
    dependency_links=[""],
    python_requires=">=3.7",
    include_package_data=True,
)
