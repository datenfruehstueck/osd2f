#!/usr/bin/env python

from setuptools import find_packages, setup
from osd2f.utils import OSD2F_VERSION

setup(
    name="OSD2F",
    python_requires=">3.8",
    version=OSD2F_VERSION,
    description="Open Source Data Donation Framework",
    author="Bob van de Velde",
    author_email="osd2f@bob-as-a-service.com",
    license=open("LICENSE").read(),
    url="https://github.com/uvacw/osd2f",
    packages=find_packages(),
    package_data={
        "osd2f": [
            "static/*",
            "templates/*",
            "templates/*/*",
            "settings/*",
            "static/js/*",
            "static/js/libarchive/*",
            "static/js/libarchive/wasm-gen/*",
        ]
    },
    scripts=["bin/osd2f", "bin/osd2f-decrypt-submissions"],
    install_requires=[
        "asyncpg",
        "azure-keyvault-secrets",
        "azure-identity",
        "cryptography",
        "hypercorn",
        "msal",
        "pyyaml",
        "pydantic",
        "pydantic[email]",
        "pyjwt>=2.4.0",  # dependency of MSAL, insecure < 2.4.0
        "pyzipper",
        "quart",
        "quart-cors",
        "tortoise-orm",
    ],
)
