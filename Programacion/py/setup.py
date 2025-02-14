from setuptools import setup

setup(
    name='VytalGym',
    version='1.0.0',
    py_modules=['app'],  # Nombre del archivo sin extensión
    entry_points={
        'console_scripts': [
            'VytalGym=app:main',  # Comando = archivo:funcion
        ],
    },
)
