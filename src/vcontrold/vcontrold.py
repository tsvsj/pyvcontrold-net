import atexit
import datetime
import json
import socket
import time
import csv
import tempfile
import pathlib
import sys

from ._vcontrold_config import vcdConfig
from typing import Union, Optional


class vcontrold:
    """
    Class to interact with vcontrold via network.

    During the initialization the connection to vcontrold is made automatically. After the connection is established,
    the command ``getDevType`` is executed to identify the current heating control system. This will create the properties
    :py:attr:`device_model`, :py:attr:`device_id`, :py:attr:`device_protocol`.

    Note:
        Outputs to *stdout* are disabled by default, as it is assumed, that the module will be used within projects,
        where only the pure data is relevant. If you use the module for other purposes, it could make sense to enable
        informational logging, by calling with ``log_info=True``.

    Args:
        host (str): vcontrold IP address or hostname
        port (int): Port, on which vcontrold listens
        timeout (int): Timeout in seconds to establish a tcp connection. Defaults to 10.
        log_info (bool): Write informational logs to *stdout*. Defaults to ``False``.
        log_debug (bool): Write debug logs to *stdout*. Defaults to ``False``.

    Todo:
        * Multi-language support (at least english)
        * Caching for returned data
    """

    def __init__(self, host: str, port: int, timeout: int = 10, log_info: bool = False, log_debug: bool = False):
        # Logging
        self.__log_info = log_info
        self.__log_debug = log_debug

        # Connection
        self.__host = host
        self.__port = port
        self.__timeout = timeout
        self._connect()

        # Load config
        project_path = pathlib.Path(sys.modules['__main__'].__file__).parent.resolve()
        self.config_manager = vcdConfig(file=str((project_path / "vcontrold_config.yml")))
        self.config = self.config_manager.get_config()

        # Heating control system initialization
        self.__device_id = None
        self._identify_heating_control()

        # Return data
        self.viessmann_data = dict(
            meta=dict(),
            data=dict()
        )
        self.__output_format = "json"
        self.__switch_as_bool = True
        self.__exclude_timers = False
        self.__use_fahrenheit = False
        self.__filter_group = None
        self.__csv_delimiter = ","
        self.__csv_linebreak = "\n"
        self.__csv_single_quotes = False

        # Exit handler
        atexit.register(self._exit_handler)

    @property
    def device_model(self) -> str:
        """Identified heating device model.

        Returns:
            str: Heating control system model.

        .. versionadded:: 2.0.0
            Replaced the previous method ``get_device_model``
        """
        return self.__device_model

    @property
    def device_id(self) -> str:
        """Identified heating device ID.

        Returns:
            str: Heating control system device ID.

        .. versionadded:: 2.0.0
            Replaced the previous method ``get_device_id``
        """
        return str(self.__device_id)

    @property
    def device_protocol(self) -> str:
        """Identified heating communication protocol, used to communicate via Optolink.

        Returns:
            str: Heating control system communication protocol.

        .. versionadded:: 2.0.0
            Replaced the previous method ``get_device_protocol``
        """
        return self.__device_protocol

    @property
    def use_fahrenheit(self) -> bool:
        """
        Changes the temperature output to Fahrenheit.

        Args:
            use_fahrenheit (bool, optional): Whether to use Fahrenheit or not. Defaults to `False`.

        Returns:
            bool: The current value.

        .. versionadded:: 2.0.0
        """
        return self.__use_fahrenheit

    @use_fahrenheit.setter
    def use_fahrenheit(self, use_fahrenheit: bool):
        self.__use_fahrenheit = use_fahrenheit

    @property
    def output_format(self) -> str:
        """
        Controls the output format of :py:meth:`get_viessmann_data`

        Args:
            fmt (str, optional): Output format. Defaults to `json`.
                Supported formats: `json`, `dict`, `csv`

        Returns:
            str: The current output format.

        Example:
            >>> vcd = vcontrold(host="127.0.0.1", port=3002)
            >>> vcd.output_format
            json
            >>> vcd.output_format = "dict"
            >>> vcd.switch_as_bool
            dict

        .. versionadded:: 2.0.0
            Replaced the previous method ``set_output_format``
        """
        return self.__output_format

    @output_format.setter
    def output_format(self, fmt: str):
        fmt = fmt.lower()
        valid_formats = ['json', 'dict', 'csv']

        if fmt in valid_formats:
            self.__output_format = fmt
        else:
            print(f"Unsupported format requested. Available formats are {','.join(valid_formats)}")

    @property
    def switch_as_bool(self) -> bool:
        """:obj:`bool`: Controls the returned type for command units of type *switch*. ``True`` will return a *bool*
        value to signal whether something is on or off, while ``False`` returns *on*/*off* as *str*.

        Args:
            use_bool_return (bool, optional): Defaults to ``True``.

        Returns:
            :obj:`bool`: The current setting.

        Example:
            >>> vcd = vcontrold(host="127.0.0.1", port=3002)
            >>> vcd.switch_as_bool
            True
            >>> vcd.switch_as_bool = False
            >>> vcd.switch_as_bool
            False

        .. versionadded:: 2.0.0
        """
        return self.__switch_as_bool

    @switch_as_bool.setter
    def switch_as_bool(self, use_bool_return: bool):
        self.__switch_as_bool = use_bool_return

    @property
    def exclude_timers(self) -> bool:
        """:obj:`bool`: Controls if the returned data contains meta information about
        the execution time of each command and a global timer for the whole process.

        Args:
            exclude_timers (bool, optional): Defaults to ``False``.

        Returns:
            :obj:`bool`: The current setting.

        .. versionadded:: 2.0.0
        """
        return self.__exclude_timers

    @exclude_timers.setter
    def exclude_timers(self, exclude_timers: bool):
        self.__exclude_timers = exclude_timers

    @property
    def csv_delimiter(self) -> str:
        """:obj:`str`: Sets the delimiter character for CSV output.

        Args:
            delimiter (str): Defaults to ``,``.

        Returns:
            :obj:`str`: The current setting.

        .. warning::
           Avoid the use of CSV output in :py:meth:`output_format`. It will be completely removed in version 3.0.0.
        """
        return self.__csv_delimiter

    @csv_delimiter.setter
    def csv_delimiter(self, delimiter: str) -> None:
        self.__csv_delimiter = delimiter

    @property
    def csv_linebreak(self) -> str:
        """:obj:`str`: Sets the linebreak sequence for CSV output.

        Args:
            linebreak (str): Defaults to ``\\n``.

        Returns:
            :obj:`str`: The current setting.

        .. warning::
           Avoid the use of CSV output in :py:meth:`output_format`. It will be completely removed in version 3.0.0.
        """
        return self.__csv_linebreak

    @csv_linebreak.setter
    def csv_linebreak(self, linebreak: str) -> None:
        self.__csv_linebreak = linebreak

    def _exit_handler(self):
        """Exit handler is used, to reliably execute methods, when the Instance is exited"""
        self._save_config()
        self._close()

    def _save_config(self):
        """Used to save the potentially modified configuration."""
        self.config_manager.write_config(self.config)

    def _connect(self):
        """Connects to vcontrold"""
        self._sock = socket.socket()
        self._sock.settimeout(self.__timeout)
        self._sock.connect((self.__host, self.__port))

    def _close(self):
        """Closes connection to vcontrold"""
        self._sock.close()

    def _disable_command(self, command: str):
        """Disables a specific command in configuration file.

        Args:
            command (str): Command, which should be disabled.
        """
        self.config['vcontrold_commands']['get'][command]['status'] = "disabled"

    def _sanitize_data_value(self, command: str, value: str):
        """Method so sanitize returned values from vcontrold.

        Args:
            command (str): Command, from which the value was returned.
            value (str): The value returned from vcontrold.

        Returns:
            (tuple): Tuple containing:
                value (str): The actual sanitized value.
                unit (str): Unit of measurement for the actual value.

        .. versionchanged:: 2.0.0
            Fixed temperature return values, that contain the string *Grad Celsius*
            Added conversion to Fahrenheit
        """
        # Remove trailing linebreaks and whitespaces
        value = value.rstrip("\n").strip()

        # Sanitize, based on unit
        command_unit = self.config['vcontrold_commands']['get'][command]['unit']

        if command_unit.lower() == "error":
            error = value.split(" ", 1)
            error_date = error[0]
            error_msg = error[1]
            dt = datetime.datetime.strptime(error_date, "%Y-%m-%dT%H:%M:%S%z")

            return dict(
                parsed={'date': dt.strftime('%Y-%m-%d'), 'time': dt.strftime('%H:%M:%S'), 'errorMessage': error_msg},
                original=value
            ), None
            # return f"{dt.strftime('%Y-%m-%d - %H:%M:%S')}: {error_msg}"
        if command_unit.lower() == "hours":
            value = round(float(value), 2)
            return value, command_unit.lower()
        if command_unit.lower() == "none":
            return value, None
        if command_unit.lower() == "number":
            value = round(float(value), 2)
            return value, command_unit.lower()
        if command_unit.lower() == "percent":
            value = round(float(value), 2)
            return value, "%"
        if command_unit.lower() == "power":
            value = round(float(value), 2)
            return value, "W"
        if command_unit.lower() == "shift":
            value = round(float(value), 2)
            return value, "shift"
        if command_unit.lower() == "slope":
            value = round(float(value), 2)
            return value, "slope"
        if command_unit.lower() == "switch":
            if self.__switch_as_bool is True:
                return True if int(value) == 1 else False, "bool"
            else:
                return "on" if int(value) == 1 else "off", "bool"
        if command_unit.lower() == "temperature":
            value = value.replace("Grad Celsius", "").strip()

            if self.__use_fahrenheit is True:
                value = float(value)
                value = (value * 1.8) + 32
                value = round(float(value), 2)
                unit = "F"
            else:
                value = round(float(value), 2)
                unit = "C"

            return value, unit

        if command_unit.lower() == "text":
            return value, "str"
        if command_unit.lower() == "time":
            dt = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S%z")
            return dt.strftime('%Y-%m-%d - %H:%M:%S'), "datetime"
        if command_unit.lower() == "timer":
            timetable = value.split("\n")
            timetable_entries_sanitized = []
            for time_entry in timetable:
                # Remove leading and trailing whitespaces
                time_entry = time_entry.strip()
                # Remote multiple whitespaces within the string
                time_entry = " ".join(time_entry.split())
                # Split by remaining white - results in on and off entry
                time_entry = time_entry.split(" ")
                # Split at first colon to get index
                time_entry_a = time_entry[0].split(":", 1)
                time_entry_index = time_entry_a[0]
                # Split again at first colon and use index 1, to get the actual value
                # Example: "An:05:00" -> time_entry_a[1].split(":", 1)[1] -> "05:00"
                time_entry_on = time_entry_a[1].split(":", 1)[1]
                time_entry_off = time_entry[1].split(":", 1)[1]

                timetable_entries_sanitized.append({
                    'index': time_entry_index,
                    'on': time_entry_on if time_entry_on != "--" else None,
                    'off': time_entry_off if time_entry_off != "--" else None
                })
            # return ';'.join(timetable_entries_sanitized)
            return dict(parsed=timetable_entries_sanitized, original=timetable), "timetable"

        return value, None

    def _identify_heating_control(self):
        """Used to identify the heating control system.

        Returns:
            bool: True if identification was successful. Other exits with message and exit code 1.
        """
        max_loop_count = 3
        loop_count = 1

        while loop_count < max_loop_count:
            self._read_prompt()
            self._sock.send('getDevType\n'.encode())
            hcs, unit = self._sanitize_data_value('getDevType', self._sock.recv(1000).decode('utf-8'))

            if hcs is not None and 'ID=' in hcs and 'Protokoll:' in hcs:
                device_model, device_id, device_protocol = hcs.split(" ")
                device_id = device_id.split("=")[1]
                device_protocol = device_protocol.split(":")[1]
                if self.__log_info is True:
                    print(f"Device correctly identified as model {device_model} (ID={device_id}, Protocol={device_protocol}) at attempt {loop_count} of {max_loop_count}")
                self.__device_model = device_model
                self.__device_id = int(device_id)
                self.__device_protocol = device_protocol
                # Exit if identified correctly
                break
            else:
                if self.__log_info is True:
                    print(f"Failed to identify heating control system. Returned data doesn't meet expectations. Attempt {loop_count} of {max_loop_count}")
                loop_count += 1

        return True

    def _read_prompt(self):
        """Reads and validates prompt from vcontrold BEFORE a command is sent.

        Returns:
            bool: Returns True, if the received data matches the expected string. Otherwise False is returned.
        """
        data = self._sock.recv(1000)
        if data.decode('utf-8') != 'vctrld>':
            if self.__log_info is True:
                print(f"Returned data is unexpected. Prompt 'vctrld>' expected, but received '{data}'")
            return False

        return True

    def _read(self, command: str):
        """Used to execute a specific command and process the returned data.

        This is basically the main method in the class.

        Args:
            command (str): The command to be executed against vcontrold.

        Returns:
            bool: Returns False, if the requested command is disabled, heating control system identification is not yet done or the command is not available for the specific heating control system. Returns True is everything works properly.

        """
        time_start = time.time()
        execute_command_state = "success"

        if self.config['vcontrold_commands']['get'][command]['status'] == "disabled":
            if self.__log_info is True:
                print(f"Command {command} is disabled and skipped.")
            return False
        elif self.__device_id not in self.config['vcontrold_commands']['get'][command]['devices']:
            if self.__log_info is True:
                print(f"Command {command} is not available for device ID {self.__device_id} and skipped (available device IDs: {self.config['vcontrold_commands']['get'][command]['devices']}).")
            return False
        else:
            self._read_prompt()
            self._sock.send(f'{command}\n'.encode())
            data = self._sock.recv(1000).decode('utf-8')

            # print(f"{command}: {data}")

            if data is None or 'NOT OK' in data:
                self._disable_command(command)
                data = ""
                execute_command_state = "failed"
            elif "command unknown" in data:
                if self.__log_info is True:
                    print(f"command {command} is unknown")
                self._disable_command(command)
                data = ""
                execute_command_state = "failed"
            elif "Wrong result, terminating" in data:
                if self.__log_info is True:
                    print(f"{command}: Failed to execute temporarily. Please retry to get the value.")
                data = ""
                execute_command_state = "failed_temporarily"

            data, unit = self._sanitize_data_value(command, data)

            time_end = time.time()
            duration = round(time_end - time_start, 3)

            return_data = {}
            return_data.update({command: {}})
            return_data[command].update({'value': data})
            return_data[command].update({'unit': unit})
            return_data[command].update({'description': self.config['vcontrold_commands']['get'][command]['description']})
            return_data[command].update({'state': execute_command_state})
            if self.exclude_timers is not True:
                return_data[command].update({'execution_time': f'{duration} seconds'})
            self.viessmann_data['data'].update(return_data)

            return True

    def get_units(self) -> list:
        """:obj:`list`: Get the units, configured in the configuration file.

        Be aware that the returned unit names are used internally, to sanitize the returned
        data and identify the real unit of measurement.

        The use of this command is only to modify units in ``vcontrold_config.yml``, if necessary.
        If you don't see a problem with the pre-defined units, don't change them.

        Returns:
            list: List of sorted units, found in the configuration file.

        Example:
            >>> vcd = vcontrold(host="127.0.0.1", port=3002)
            >>> vcd.get_units()
            ['error', 'hours', 'none', 'number', 'percent', 'power', 'shift', 'slope', 'switch', 'temperature', 'text', 'time', 'timer']
        """
        command_units = []
        for command, params in self.config["vcontrold_commands"]['get'].items():
            if type(params['unit']) == str and params['unit'] not in command_units:
                command_units.append(params['unit'])

        return sorted(command_units)

    def get_groups(self) -> list:
        """:obj:`list`: Get the groups, configured in the configuration file.

        The returned groups can be used in ``vcontrold_config.yml`` to modify existing
        group assignments or to create your own groups. Within ``vcontrold_config.yml``
        you can add custom groups or replace existing ones with your own, if you're not
        happy with the pre-defined groups.

        Refer to the :doc:`configuration` for more information.

        Returns:
            list: List of sorted groups, found in the configuration file.

        Example:
            >>> vcd = vcontrold(host="127.0.0.1", port=3002)
            >>> vcd.get_groups()
            ['burner', 'environment', 'error', 'mixer', 'operation-mode', 'power', 'pumps', 'solar', 'stats', 'system', 'temperature', 'timer']

        """

        device_groups = []
        for command, params in self.config["vcontrold_commands"]['get'].items():
            if type(params['groups']) == list and len(params['groups']) > 0:
                for group in params['groups']:
                    if type(group) == str and group not in device_groups:
                        device_groups.append(group)

        return sorted(device_groups)

    def get_items_per_group(self) -> dict:
        """:obj:`dict`: Get the groups with all assigned commands.

        The returned groups contain commands, which are assigned to the group. This
        is meant to be helpful for you, to create you own overview of the groups and
        assigned commands.

        Returns:
            dict: Contains groups as items, with assigned commands.

        Example:
            >>> vcd = vcontrold(host="127.0.0.1", port=3002)
            >>> vcd.get_items_per_group()
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
        """
        device_group_items = {}
        device_groups = self.get_groups()
        for group in device_groups:
            device_group_items.update({group: {'num_items': 0, 'items': []}})

            for command, params in self.config["vcontrold_commands"]['get'].items():
                if group in params['groups']:
                    device_group_items[group]['items'].append(command)
                    device_group_items[group]['num_items'] += 1

        return json.dumps(device_group_items, indent=4)

    @property
    def groups(self) -> Optional[list]:
        """Controls the group filter to a specific group or list of groups.

        :py:meth:`groups` filters the commands, executed when :py:meth:`get_viessmann_data` is called,
        by the applied group or list of groups.

        The group assignments in ``vcontrold_config.yml`` are made for this filter method.

        Note:
            You can provide either a single group (:obj:`str`) or a list of groups (:obj:`list`). I would
            recommend to always use the :obj:`str` type, as the single group selector may be removed
            in future versions.

        Args:
            group (:obj:`str` or :obj:`list`): Group to filter commands. Defaults to ``None``.

        Returns:
            list: The current list of groups to filter.

        .. versionadded:: 2.0.0
            Replaces previous method ``set_group``. Accepts ``list`` instead of only a single group name. Returns always `list`, if defined.
        """
        return self.__filter_group

    @groups.setter
    def groups(self, groups: Union[str, list]):
        # Convert provided group as str to list
        if type(groups) == str:
            groups = [groups]

        existing_groups = self.get_groups()
        new_groups = []
        for group in groups:
            if group in existing_groups:
                new_groups.append(group)
            else:
                print(f"Requested group {group} is not yet configured. If you want to use this group, you need to define it in the configuration file.")

        if len(new_groups) > 0:
            self.__filter_group = new_groups

    def unset_group(self) -> None:
        """Resets the group filter to any.

        Resets the group to any, if a group filter was previously defined with :py:meth:`groups`.
        """
        self.__filter_group = None

    def get_viessmann_data(self, max_values: int = None):
        """Requests and returns the actual data from vcontrold.

        This method uses :py:meth:`groups` to filter the executed commands, if defined. Otherwise,
        all available commands are executed.

        The argument ``max_values`` is intended for testing purposes, where you want to query a group
        of commands, but don't want to wait until all commands are executed, because you only need an example
        of the returned data. I've used this extensively while sanitizing the returned data.

        Note:
            Please be informed, that vcontrold takes some time, until an executed command returns any data.
            Each command will approximately need 2.5 seconds to complete. If all available commands are
            executed, the whole process can take several minutes, untils the reponse is generated. You should
            consider this when thinking about timeouts or max execution times.

        Args:
            max_values (int): Max number of executed commands.

        Returns:
            mixed: Returns data based on self.output_format. Defaults to JSON.

        """
        time_start = time.time()

        # Get the total number of executed commands
        commands_to_be_executed = []
        for command, params in self.config["vcontrold_commands"]['get'].items():
            if params["status"] == "enabled":
                if self.__filter_group is not None:
                    if not any(group in self.__filter_group for group in params['groups']):
                        continue
                commands_to_be_executed.append(command)

        num_commands = len(commands_to_be_executed)
        if max_values is not None:
            if max_values < num_commands:
                if max_values != 0:
                    if self.__log_info is True:
                        print(f"Limited the maximum returned values to {max_values}.")
                    num_commands = max_values
                else:
                    if self.__log_info is True:
                        print(f"Option 'max_values' is 0. This is interpreted as 'any'. Ignoring 'max_values'.")
            else:
                if self.__log_info is True:
                    print(f"Option 'max_values' ({max_values}) is greater than the number of commands to be executed ({commands_to_be_executed}). Ignoring 'max_values'.")

        loop_count = 1

        for command in commands_to_be_executed:
            if self.__log_info is True:
                # Write stdout
                sys.stdout.write(f"\rExecuting command {loop_count:02d} of {num_commands:02d} ({command:s})...")
                # Flush stdout
                sys.stdout.flush()

            # Execute the command
            self._read(command=command)

            if loop_count >= num_commands:
                break
            loop_count += 1

        if self.__log_info is True:
            print("")
            print("-------------------------------")

        time_end = time.time()
        duration = round(time_end - time_start, 3)
        if self.exclude_timers is not True:
            self.viessmann_data['meta'].update({'execution_time': f'{duration} seconds'})
        self.viessmann_data['meta'].update({'num_items': len(self.viessmann_data['data'])})

        # Return data
        if self.__output_format == "json":
            return json.dumps(self.viessmann_data, indent=4)
        elif self.__output_format == "dict":
            return self.viessmann_data
        elif self.__output_format == "csv":
            csv_keys = ['Command']
            csv_values = []
            if self.__csv_single_quotes is True:
                quote = "'"
            else:
                quote = '"'

            for command, command_value in self.viessmann_data['data'].items():
                # csv_data_string = quote + str(command) + quote + self.csv_delimiter
                csv_data_values = [str(command)]
                for cmd_key, cmd_value in command_value.items():
                    if cmd_key not in csv_keys:
                        csv_keys.append(cmd_key)
                    csv_data_values.append(cmd_value)

                csv_values.append(quote + (quote + self.__csv_delimiter + quote).join(csv_data_values) + quote)

            csv_data = quote + (quote + self.__csv_delimiter + quote).join(csv_keys) + quote + self.__csv_linebreak
            csv_data += self.__csv_linebreak.join(csv_values)
            return csv_data
