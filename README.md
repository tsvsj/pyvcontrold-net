<!-- pyvcontrold-net documentation master file -->
# pyvcontrold-net

![image](https://img.shields.io/github/last-commit/tsvsj/pyvcontrold-net?style=flat-square:alt:GitHublastcommit)
![image](https://img.shields.io/github/license/tsvsj/pyvcontrold-net?style=flat-square:alt:GitHub)
![image](https://img.shields.io/pypi/dm/pyvcontrold-net?style=flat-square:alt:PyPI-Downloads)
![image](https://img.shields.io/pypi/v/pyvcontrold-net?style=flat-square:alt:PyPI)
![image](https://img.shields.io/pypi/pyversions/pyvcontrold-net?style=flat-square:alt:PyPI-PythonVersion)
![image](https://img.shields.io/pypi/status/pyvcontrold-net?style=flat-square:alt:PyPI-Status)

This is a simple library to interact with vcontrold ([@openv/vcontrold](https://github.com/openv/vcontrold)), the open-source daemon to communicate with Viessmann Vitotronic via Optolink. Documentation for vcontrold itself can be found at [@openv/openv Wiki](https://github.com/openv/openv/wiki).

> :information_source: Please check out [pyvcontrol](https://github.com/joppi588/pyvcontrol) as well. This package supports direct communication via Optolink, instead of using vcontrold as middleware.

------
## Installation

Use pip to install the pyvcontrold-net package.

```console
(.venv) $ pip install pyvcontrold-net
```

After the installation is done, you can import the package and create an instance of vcontrold.

## Basic Usage

To use vcontrold you need to import the module vcontrold from the package vcontrold.

> :warning: You need to know your *device ID*. If you don't already know it, use :py:attr:`.device_id` to find the device ID of your heating control system. If your device ID is not listed in the ``devices`` node within ``vcontrold_config.yml``, you need to add it (or replace the existing) to each command. Otherwise no command will be processed!

```python
>>> from vcontrold import vcontrold
>>> vcd = vcontrold.vcontrold(host="127.0.0.1", port=3002, timeout=5)
>>> vcd.get_viessmann_data()
```

This will connect to you vcontold, execute all of the available commands and return the result as JSON.

For more information refer to the [Documentation](https://tsvsj.github.io/pyvcontrold-net/)

## Contribution

As I have only one heating system at home, there is no possibility to add commands to the library, which don’t work on my own heating system. So if you’ve identified commands, that are not initially included, open an issue and let me know to create a helpful library for all of the people out there, that don’t have a fancy smart home heating control system.

## Bugs/Issues

Please report any issues you find. I’ll try to fix them asap.

## Donations

If you like my work and would like to support me, feel free to by me a cup of coffee.

<a href="https://www.buymeacoffee.com/tsvsj" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-green.png" alt="Buy me a coffee" height=60></a>

## Disclaimer

I’m not responsible for the usage of this program by any other people. The software shouldn’t harm the heater control in any way, but be aware, that there are official solutions from Viessmann, that can be purchased and safely used.
