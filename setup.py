from setuptools import find_packages, setup
import os

env_vars = ["AUTH_USER", "AUTH_PASSWORD", "DEPLOYMENT_BRANCH"]
env_vars = {e: os.getenv(e) for e in env_vars}


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


with open("requirements.txt", "r", encoding="utf-8") as fh:
    requires = fh.read().split("\n")
    requires = [r.strip() for r in requires if len(r.strip()) > 0]
    requires = [r.format(**env_vars) for r in requires]


setup(
    name='on_field_gear_compliance_hackathon',
    packages=find_packages(),
    version='0.1.0',
    author='mayank1903',
    description='A repo to work with on field gear compliance',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    data_files=['requirements.txt'],
    install_requires=requires,
)
