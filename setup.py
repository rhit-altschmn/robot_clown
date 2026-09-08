from setuptools import find_packages, setup

package_name = 'robot_clown'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Mindy Altschul',
    maintainer_email='altschmn@rose-hulman.edu',
    description='Expressive Eyes for Stretch Robot',
    license='BSD-3-Clause',
    extras_require={
        'test': [
            'pytest',
        ],
    },
    entry_points={
        'console_scripts': [
            'keyboard_driver = robot_clown.keyboard_driver:main',
            'eye_listener = robot_clown.eye_listener:main'
        ],
    },
)
