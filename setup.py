#!/usr/bin/env python3
"""
DNC参数计算系统 - 打包配置
"""

from setuptools import setup, find_packages
import os

# 读取README文件
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# 读取requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="dnc-parameter-system",
    version="2.05",
    author="DNC开发团队",
    author_email="support@dnc-system.com",
    description="DNC参数计算系统 - 基于原始VB.NET项目重写的Python版本",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-organization/dnc-python-system",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Manufacturing",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "dnc-system=main:main",
        ],
    },
    package_data={
        "": [
            "config/*.ini",
            "data/master/*.csv",
            "data/master/prg1/*.csv",
            "data/master/prg2/*.csv",
            "data/master/prg3/*.csv",
        ],
    },
    include_package_data=True,
    data_files=[
        ("config", ["config/config.ini"]),
        ("", ["README.md", "INSTALL.md", "CLASS_DIAGRAM.md", "requirements.txt"]),
    ],
    project_urls={
        "Bug Reports": "https://github.com/your-organization/dnc-python-system/issues",
        "Source": "https://github.com/your-organization/dnc-python-system",
        "Documentation": "https://github.com/your-organization/dnc-python-system/wiki",
    },
    keywords="dnc parameter calculation manufacturing engineering",
    license="MIT",
    platforms=["Windows", "Linux", "Mac OS-X"],
)

if __name__ == "__main__":
    print("DNC参数计算系统打包配置")
    print("使用方法:")
    print("  python setup.py sdist bdist_wheel  # 创建发布包")
    print("  pip install .                      # 本地安装")
