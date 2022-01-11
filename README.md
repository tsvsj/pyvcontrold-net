# pyvcontrold

This is a simple library to interact with vcontrold ([@openv/vcontrold](https://github.com/openv/vcontrold)), the open-source daemon to communicate with Viessmann Vitotronic via Optolink. Documentation for vcontrold itself can be found at [@openv/openv Wiki](https://github.com/openv/openv/wiki).

# Disclaimer

I'm not responsible for the usage of this program by any other people. The software shouldn't harm the heater control in any way, but be aware, that there are official solutions from Viessmann, that can be purchased and safely used.

# Installation

```shell
$ pip install pycontrold
```

# Usage

## Configuration

The library uses a configuration file, `conf.yml`, in YAML format, which contains all known commands and defines several params for each command.

```yaml
vcontrold_commands:
  getBetriebArtM1:
    description: Betriebsart M1
    devices:
    - 2094
    groups:
    - operation-mode
    status: enabled
    unit: ''
  getBetriebArtM2:
    description: Betriebsart M2
    devices:
    - 2094
    groups:
    - operation-mode
    status: enabled
    unit: ''
```
The YAML the vcontrold commands are the keys (i.e. `getBetriebArtM1`, `getBetriebArtM2` or `getTempA`). Each command contains the following parameters:

| Parameter     | Type | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
|---------------|---------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `description` | `str`   | A descriptive text for what the command returns. The description can be changed to anything else.                                                                                                                                                                                                                                                                                                                                                                                                                                                      |
| `devices`     | `list`  | Each heating system control unit has its own ID in vcontrold, documented at [Github openv Wiki](https://github.com/openv/openv/wiki/Ger%C3%A4te). Not each command is available for each heating system. Which commands are available need to be defined in vcontrold itself.<br/>This parameter controls, whether the command will be automatically executed for the detected system. If your device ID is not listed, just add it to the list or replace the existing ID with your own (I assume, that everyone has only one heating system :wink:). |
| `groups`      | `list`  | Each `get`-command is assigned to at least one group by default, to make filtering of read commands available. The list of groups may be expanded or changed as you like.                                                                                                                                                                                                                                                                                                                                                                              |
| `status`      | `str`   | Used to skip single commands in general. If the `status` of a command is `disabled`, it will not be executed, independently from the `group` or anything else.<br />Additionally, the `status` is used to automatically disable commands, which return unexpected outputs or not supported by the heating system. If, during `read_all` execution a command returns data, that doesn't match the expecation, it will be automatically disabled in the config file.                                                                                     |
| `unit`         | `str`   | The unity of measurement. Is returned to identify the unit of a value.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |



## Basic
```python
from vcontrold import vcontrold

vcd = vcontrold(host="127.0.0.1", port=3002, timeout=5)
vcd.read_all()
```
This will output all readable values.

## Group Filter

The `read_all` method supports a `group` argument. Each command is optionally assigned to one or multiple groups, to filter which commands should be executed, while reading all.

```python
from vcontrold import vcontrold

vcd = vcontrold(host="127.0.0.1", port=3002, timeout=5)
vcd.read_all(group="temperature")
```
By filtering to the group `temperature`, only commands are executed, which are assigned to that group.

# Contribution

As I have only one heating system at home, there is no possibility to add commands to the library, which don't work on my own heating system. So if you've identified commands, that are not initially included, open an issue and let me know to create a helpful library for all of the people out there, that don't have a fancy smart home heating control system. 