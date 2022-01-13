# pyvcontrold-net

This is a simple library to interact with vcontrold ([@openv/vcontrold](https://github.com/openv/vcontrold)), the open-source daemon to communicate with Viessmann Vitotronic via Optolink. Documentation for vcontrold itself can be found at [@openv/openv Wiki](https://github.com/openv/openv/wiki).

# Disclaimer

I'm not responsible for the usage of this program by any other people. The software shouldn't harm the heater control in any way, but be aware, that there are official solutions from Viessmann, that can be purchased and safely used.

# Installation

```shell
$ pip install pycontrold-net
```

# Basic Usage
```python
from vcontrold import vcontrold

vcd = vcontrold.vcontrold(host="127.0.0.1", port=3002, timeout=5)
print(str(vcd.get_viessmann_data())
```
This will output all readable values.

# Advanced Usage

## Configuration

The library uses a configuration file, `vcontrold_config.yml`, in YAML format, which contains all known commands and defines several params for each command. The initial configuration will be created automatically within your project root (based on the file from which `__main__` is called). After the creation you can modify the configuration file as you like.

```yaml
vcontrold_commands:
  get:
    getBetriebArtM1:
      description: Betriebsart M1
      devices:
      - 2094
      groups:
      - operation-mode
      status: enabled
      unit: text
    getBrennerStatus:
      description: Ermittle den Brennerstatus
      devices:
      - 2094
      groups:
      - burner
      status: enabled
      unit: switch
    getSystemTime:
      description: Ermittle Systemzeit
      devices:
      - 2094
      groups:
      - system
      status: enabled
      unit: time
    ...
  set:
    setBetriebArtM1:
      description: Setze Betriebsart M1
      devices:
      - 2094
      groups: []
      status: enabled
      unit: none
    ...
```

The file basically consists of a single `dict`, `vcontrold_commands`, with two sub items `get` and `set`, both are of type `dict` as well. These are used to differ between `get`- and `set`-commands. `set`-commands are currently not yet implemented, although they already exist in the configuration.  

Each item of `get` or `set` is a vcontrold command, i.e.

```yaml
getBrennerStatus:                   # <-- vcontrold command
  description: Brennerstatus        # <-- description of the command (used in output)
  devices:                          # <-- list of device IDs, for which this command is valid
  - 2094
  groups:                           # <-- list of groups, to which this command is assigned
  - burner
  status: enabled                   # <-- status of the command
  unit: switch                      # <-- pre-defined unit for sanitization
```
Each command contains the following parameters:

| Parameter     | Type   | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
|---------------|--------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `description` | `str`  | A descriptive text for what the command returns. The description can be changed to anything else.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          |
| `devices`     | `list` | Each heating system control unit has its own ID in vcontrold, documented at [Github openv Wiki](https://github.com/openv/openv/wiki/Ger%C3%A4te). Not each command is available for each heating system. Which commands are available need to be defined in vcontrold itself.<br/>This parameter controls, whether the command will be automatically executed for the detected system. If your device ID is not listed, just add it to the list or replace the existing ID with your own (I assume, that everyone has only one heating system :wink:).                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| `groups`      | `list` | Each `get`-command is assigned to at least one group by default, to make filtering of read commands available. The list of groups may be expanded or changed as you like.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| `status`      | `str`  | Used to skip single commands in general. If the `status` of a command is `disabled`, it will not be executed, independently from the `group` or anything else.<br />Additionally, the `status` is used to automatically disable commands, which return unexpected outputs or not supported by the heating system. If, during `read_all` execution a command returns data, that doesn't match the expecation, it will be automatically disabled in the config file.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| `unit`        | `str`  | The unity of measurement. This is used internally to sanitize the returned values and change the format, if necessary. The valid unit types are pre-defined and may be advanced in futurer.<br />Currently available units are <br/><ul><li>`error` - Error messages. Especially for commands `getError[0-9]`.</li><li>`hours` - Cast to `float`, round to 2 decimal places and append _hours_.</li><li>`none` - Unspecified. Return as is.</li><li>`number` - Cast to `float` and round to 2 decimal places.</li><li>`percent` - Cast to `float`, round to 2 decimal places and append _%_.</li><li>`power` - Cast to `float`, round to 2 decimal places and append _W_.</li><li>`shift` - Cast to `float`, round to 2 decimal places and append _shift_.</li><li>`slope` - Cast to `float`, round to 2 decimal places and append _slope_.</li><li>`switch` - Returns either _on_/_off_ (`str`) or _true_/_false_ (`bool`), based on instance propery `switch_as_bool`.</li><li>`temperature` - Cast to `float`, round to 2 decimal places and append _°C_.</li><li>`text` - Return as is.</li><li>`time` - Parsed as `datetime` object and returned with format _%Y-%m-%d - %H:%M:%S_.</li><li>`timer` - Parsed the timetable, returnfed from vcontrold to a `list` of `dict`, where each time entry attribute is returned as _index_, _time_on_ and _time_off_</li></ul><br/>The parsing process may not be optimally implemented by now, because I didn't have enough data for different systems. Changes may be necessary in future version, to reflect differences from the different heating control system models. |

## Options
### Properties
The instance can be configured by modifying its properties directly. Currently there are only a few properties, which should be changed directly:

| Property         | Type   | Description                                                                                                                                                          |
|------------------|--------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `logging_quiet`  | `bool` | Controls whether to output general information or not. `True` will avoid log messages, while `False` writes useful information to _stdout_.<br/>Defaults to `False`. | 
| `switch_as_bool` | `bool` | Controls if the unit `switch` return boolean values or text, as described in [Configuration](#configuration).<br/>Defaults to `True`.                                |


```python
from vcontrold import vcontrold

vcd = vcontrold.vcontrold(host="127.0.0.1", port=3002, timeout=5)
# Return command values of unit switch as "on"/"off"  
vcd.switch_as_bool = False
# Avoid informational logging to stdout
vcd.logging_quiet = True

print(str(vcd.get_viessmann_data())
```

## Methods
### Group Filter
The `get_viessmann_data` basically executed all known commands. As each command is assigned to a group, it's possible to filter the commands by the assigned groups, by using the methods `set_group` (set filter) and `unset_group` (reset filter).

```python
from vcontrold import vcontrold

vcd = vcontrold.vcontrold(host="127.0.0.1", port=3002, timeout=5)
# Commands of group system
vcd.set_group("system")
print(str(vcd.get_viessmann_data())

# Commands of group pumps
vcd.set_group("pumps")
print(str(vcd.get_viessmann_data())

# All commands
vcd.unset_group()
print(str(vcd.get_viessmann_data())
```


### Get groups
As you may not be aware of the currently existing groups, you can use `get_groups` to get a list of the available groups:

```python
from vcontrold import vcontrold

vcd = vcontrold.vcontrold(host="127.0.0.1", port=3002, timeout=5)
print(str(vcd.get_groups())
```
Returns `list`:
```json
['burner', 'environment', 'error', 'mixer', 'operation-mode', 'power', 'pumps', 'solar', 'stats', 'system', 'temperature', 'timer']
```

### Get commands per group
If you want to know, which commands are currently assigned to which group, you may use `get_items_per_group`:

```python
from vcontrold import vcontrold
import json

vcd = vcontrold.vcontrold(host="127.0.0.1", port=3002, timeout=5)
print(json.dumps(vcd.get_items_per_group(), indent=4))
```

Returns `dict`:
```json
{
    "burner": {
        "num_items": 4,
        "items": [
            "getBrennerStarts",
            "getBrennerStatus",
            "getBrennerStunden1",
            "getBrennerStunden2"
        ]
    },
    "environment": {
        "num_items": 4,
        "items": [
            "getNeigungM1",
            "getNeigungM2",
            "getNiveauM1",
            "getNiveauM2"
        ]
    },
    ...
}
```

### Get device model
```python
from vcontrold import vcontrold

vcd = vcontrold.vcontrold(host="127.0.0.1", port=3002, timeout=5)
print(vcd.get_device_model())
```

Returns `str`:
```text
V200KW1
```

### Get device ID
```python
from vcontrold import vcontrold

vcd = vcontrold.vcontrold(host="127.0.0.1", port=3002, timeout=5)
print(vcd.get_device_id())
```

Returns `str`:
```text
2094
```

### Get device protocol
```python
from vcontrold import vcontrold

vcd = vcontrold.vcontrold(host="127.0.0.1", port=3002, timeout=5)
print(vcd.get_device_protocol())
```

Returns `str`:
```text
KW
```

### Output format
Currently there are 3 output formats available:
* JSON
* `dict`
* CSV

To be honest, I'm pretty sure that I will remove CSV soon, as it's not easy to convert the data to CSV, especially the time tables. So you should work with `dict` or JSON.

The output format can be set by using the method `set_output_format`:
```python
from vcontrold import vcontrold

vcd = vcontrold.vcontrold(host="127.0.0.1", port=3002, timeout=5)
# Returns JSON
vcd.set_output_format('json')
# Returns dict
vcd.set_output_format('dict')
# Returns CSV
vcd.set_output_format('csv')
```
The output format defaults to JSON.


### `get_viessmann_data`
The method `get_viessmann_data` is the main method, which returnd the actual data from vcontrold, in sanitized/parsed format. It returns the data based on [Output format](#output-format).

For testing purposes you can limit the number of returned values by specifying the `max_values` (`int`) argument:
```python
from vcontrold import vcontrold

vcd = vcontrold.vcontrold(host="127.0.0.1", port=3002, timeout=5)
vcd.logging_quiet=True
vcd.get_viessmann_data(max_values=1)
```
Returns `json`:
```json
{
    "meta": {
        "execution_time": "2.109 seconds",
        "num_items": 1
    },
    "data": {
        "getPumpeStatusM1": {
            "value": true,
            "unit": "switch",
            "description": "Ermittle den Status der Pumpe M1",
            "state": "success",
            "execution_time": "2.109 seconds"
        }
    }
}
```

# Contribution

As I have only one heating system at home, there is no possibility to add commands to the library, which don't work on my own heating system. So if you've identified commands, that are not initially included, open an issue and let me know to create a helpful library for all of the people out there, that don't have a fancy smart home heating control system. 

# Bugs/Issues

Please report any issues you find. I'll try to fix them asap.

# Donations

If you like my work and would like to support me, feel free to by me a cup of coffee.

<a href="https://www.buymeacoffee.com/tsvsj" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-green.png" alt="Buy Me A Coffee" style="height: 60px !important;width: 217px !important;" ></a>
