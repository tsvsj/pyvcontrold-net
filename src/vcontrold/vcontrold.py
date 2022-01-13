import atexit
import datetime
import json
import socket
import time
import csv
import tempfile
import pathlib
import sys

from .vcontrold_config import vcdConfig


class vcontrold:
    def __init__(self, host: str, port: int, timeout: int = 10):
        """Initialization

        Args:
            host (str): vcontrold IP address or hostname
            port (int): Port, on which vcontrold listens
            timeout (int): Timeout in seconds to establish a tcp connection. Defaults to 10.
        """
        # Logging
        self.logging_quiet = False

        # Connection
        self.host = host
        self.port = port
        self.timeout = timeout
        self._connect()

        # Load config
        project_path = pathlib.Path(sys.modules['__main__'].__file__).parent.resolve()
        self.config_manager = vcdConfig(file=str((project_path / "vcontrold_config.yml")))
        self.config = self.config_manager.get_config()

        # Heating control system initialization
        self.device_id = None
        self._identify_heating_control()

        # Return data
        self.viessmann_data = dict(
            meta=dict(),
            data=dict()
        )
        self.output_format = "json"
        self.switch_as_bool = True
        self.filter_group = None
        self.csv_delimiter = ","
        self.csv_linebreak = "\n"
        self.csv_single_quotes = False

        # Exit handler
        atexit.register(self._exit_handler)

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
        self._sock.settimeout(self.timeout)
        self._sock.connect((self.host, self.port))

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
            value (str): The value returned from vcontrold.

        Returns:
            str: Sanitized string.
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
                parsed={ 'date': dt.strftime('%Y-%m-%d'), 'time': dt.strftime('%H:%M:%S'), 'errorMessage': error_msg },
                original=value
            )
            #return f"{dt.strftime('%Y-%m-%d - %H:%M:%S')}: {error_msg}"
        if command_unit.lower() == "hours":
            value = round(float(value), 2)
            return f"{value} hours"
        if command_unit.lower() == "none":
            f"{value}"
        if command_unit.lower() == "number":
            value = round(float(value), 2)
            return f"{value}"
        if command_unit.lower() == "percent":
            value = round(float(value), 2)
            return f"{value}%"
        if command_unit.lower() == "power":
            value = round(float(value), 2)
            return f"{value} W"
        if command_unit.lower() == "shift":
            value = round(float(value), 2)
            return f"{value} shift"
        if command_unit.lower() == "slope":
            value = round(float(value), 2)
            return f"{value} slope"
        if command_unit.lower() == "switch":
            if self.switch_as_bool is True:
                return True if int(value) == 1 else False
            else:
                return "on" if int(value) == 1 else "off"
        if command_unit.lower() == "temperature":
            value = round(float(value), 2)
            return f"{value} °C"
        if command_unit.lower() == "text":
            f"{value}"
        if command_unit.lower() == "time":
            dt = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S%z")
            return dt.strftime('%Y-%m-%d - %H:%M:%S')
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
            #return ';'.join(timetable_entries_sanitized)
            return dict(parsed=timetable_entries_sanitized, original=timetable)






        return value

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
            hcs = self._sanitize_data_value('getDevType', self._sock.recv(1000).decode('utf-8'))

            if hcs is not None and 'ID=' in hcs and 'Protokoll:' in hcs:
                device_model, device_id, device_protocol = hcs.split(" ")
                device_id = device_id.split("=")[1]
                device_protocol = device_protocol.split(":")[1]
                if self.logging_quiet is False:
                    print(f"Device correctly identified as model {device_model} (ID={device_id}, Protocol={device_protocol}) at attempt {loop_count} of {max_loop_count}")
                self.device_model = device_model
                self.device_id = int(device_id)
                self.device_protocol = device_protocol
                # Exit if identified correctly
                break
            else:
                if self.logging_quiet is False:
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
            if self.logging_quiet is False:
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
            if self.logging_quiet is False:
                print(f"Command {command} is disabled and skipped.")
            return False
        elif self.device_id not in self.config['vcontrold_commands']['get'][command]['devices']:
            if self.logging_quiet is False:
                print(f"Command {command} is not available for device ID {self.device_id} and skipped (available device IDs: {self.config['vcontrold_commands']['get'][command]['devices']}).")
            return False
        else:
            self._read_prompt()
            self._sock.send(f'{command}\n'.encode())
            data = self._sock.recv(1000).decode('utf-8')


            #print(f"{command}: {data}")

            if data is None or 'NOT OK' in data:
                self._disable_command(command)
                data = ""
                execute_command_state = "failed"
            elif "command unknown" in data:
                if self.logging_quiet is False:
                    print(f"command {command} is unknown")
                self._disable_command(command)
                data = ""
                execute_command_state = "failed"
            elif "Wrong result, terminating" in data:
                if self.logging_quiet is False:
                    print(f"{command}: Failed to execute temporarily. Please retry to get the value.")
                data = ""
                execute_command_state = "failed_temporarily"

            data = self._sanitize_data_value(command, data)

            time_end = time.time()
            duration = round(time_end - time_start, 3)
            self.viessmann_data['data'].update({
                command: {
                    'value': data,
                    'unit': self.config['vcontrold_commands']['get'][command]['unit'],
                    'description': self.config['vcontrold_commands']['get'][command]['description'],
                    'state': execute_command_state,
                    'execution_time': f'{duration} seconds'
                }
            })

            return True

    def get_device_model(self):
        """Returns the identified heating device model.

        Returns:
            str: Heating control system model.
        """
        return self.device_model

    def get_device_id(self):
        """Returns the identified heating device ID.

        Returns:
            str: Heating control system device ID.
        """
        return self.device_id

    def get_device_protocol(self):
        """Returns the identified heating communication protocol, used to communicate via Optolink.

        Returns:
            str: Heating control system communication protocol.
        """
        return self.device_protocol

    def get_units(self):
        """Get the units, configured in the configuration file.

        Returns:
            list: List of sorted units, found in the configuration file.
        """
        command_units = []
        for command, params in self.config["vcontrold_commands"]['get'].items():
            if type(params['unit']) == str and params['unit'] not in command_units:
                command_units.append(params['unit'])

        return sorted(command_units)

    def get_groups(self):
        """Get the groups, configured in the configuration file.

        Returns:
            list: List of sorted groups, found in the configuration file.
        """
        device_groups = []
        for command, params in self.config["vcontrold_commands"]['get'].items():
            if type(params['groups']) == list and len(params['groups']) > 0:
                for group in params['groups']:
                    if type(group) == str and group not in device_groups:
                        device_groups.append(group)

        return sorted(device_groups)

    def get_items_per_group(self):
        """Get the groups, together with number of applied commands and applied commands.

        Returns:
            dict: Contains groups as items, with applied num of command and commands.
        """
        device_group_items = {}
        device_groups = self.get_groups()
        for group in device_groups:
            device_group_items.update({ group: { 'num_items': 0, 'items': [] } })

            for command, params in self.config["vcontrold_commands"]['get'].items():
                if group in params['groups']:
                    device_group_items[group]['items'].append(command)
                    device_group_items[group]['num_items'] += 1

        return json.dumps(device_group_items, indent=4)

    def set_output_format(self, fmt: str):
        """Sets the output format of the actual data

        This method only sets the output format within the instance. The actual output is done via :method:get_viessmann_data

        Args:
            fmt (str): Defines the requests format. Currently support: json, dict
        """
        fmt = fmt.lower()
        valid_formats = ['json', 'dict', 'csv']

        if fmt in valid_formats:
            self.output_format = fmt
        else:
            print(f"Unsupported format requested. Available formats are {','.join(valid_formats)}")

    def set_csv_delimiter(self, delimiter: str):
        self.csv_delimiter = delimiter
    def set_csv_linebreak(self, linebreak: str):
        self.csv_linebreak = linebreak

    def set_group(self, group: str):
        """Sets the group filter to a specific group.

        After this method is applied, each data request will only return data for this group.

        Args:
            group (str): Group to filter commands.

        Returns:
            bool: True if group exists. False if group is not yet defined.
        """
        existing_groups = self.get_groups()
        if group in existing_groups:
            self.filter_group = group
            return True
        else:
            print(f"Requested group {group} is not yet configured. If you want to use this group, you need to define it in the configuration file.")
            return False

    def unset_group(self):
        """Resets the group filter to any.

        Resets the group to any, if a group filter was previously defined with :method:set_group

        Returns:
            bool: Always True.
        """
        self.filter_group = None
        return True

    def get_viessmann_data(self, max_values: int = None):
        """Requests and returns the actual data from vcontrold.

        Args:
            max_values (int): Return a maximum of max_values, instead of all values from a group or all. This is used to simply execute a test without waiting a long time until a group is completely executed.

        Returns:
            mixed: Returns data based on self.output_format. Defaults to JSON.

        """
        time_start = time.time()

        # Get the total number of executed commands
        commands_to_be_executed = []
        for command, params in self.config["vcontrold_commands"]['get'].items():
            if params["status"] == "enabled":
                if self.filter_group is not None:
                    if self.filter_group not in params['groups']:
                        continue
                commands_to_be_executed.append(command)

        num_commands = len(commands_to_be_executed)
        if max_values is not None:
            if max_values < num_commands:
                if max_values != 0:
                    if self.logging_quiet is False:
                        print(f"Limited the maximum returned values to {max_values}.")
                    num_commands = max_values
                else:
                    if self.logging_quiet is False:
                        print(f"Option 'max_values' is 0. This is interpreted as 'any'. Ignoring 'max_values'.")
            else:
                if self.logging_quiet is False:
                    print(f"Option 'max_values' ({max_values}) is greater than the number of commands to be executed ({commands_to_be_executed}). Ignoring 'max_values'.")


        loop_count = 1

        for command in commands_to_be_executed:
            if self.logging_quiet is False:
                # Write stdout
                sys.stdout.write(f"\rExecuting command {loop_count:02d} of {num_commands:02d} ({command:s})...")
                # Flush stdout
                sys.stdout.flush()

            # Execute the command
            self._read(command=command)



            if loop_count >= num_commands:
                break

            loop_count += 1

        if self.logging_quiet is False:
            print("")
            print("-------------------------------")


        time_end = time.time()
        duration = round(time_end - time_start, 3)
        self.viessmann_data['meta'].update({'execution_time': f'{duration} seconds'})
        self.viessmann_data['meta'].update({'num_items': len(self.viessmann_data['data'])})

        # Return data
        if self.output_format == "json":
            return json.dumps(self.viessmann_data, indent=4)
        elif self.output_format == "dict":
            return self.viessmann_data
        elif self.output_format == "csv":
            csv_keys = ['Command']
            csv_values = []
            if self.csv_single_quotes is True:
                quote = "'"
            else:
                quote = '"'

            for command,command_value in self.viessmann_data['data'].items():
                #csv_data_string = quote + str(command) + quote + self.csv_delimiter
                csv_data_values = [str(command)]
                for cmd_key, cmd_value in command_value.items():
                    if cmd_key not in csv_keys:
                        csv_keys.append(cmd_key)
                    csv_data_values.append(cmd_value)

                csv_values.append(quote + (quote + self.csv_delimiter + quote).join(csv_data_values) + quote)

            csv_data = quote + (quote + self.csv_delimiter + quote).join(csv_keys) + quote + self.csv_linebreak
            csv_data += self.csv_linebreak.join(csv_values)
            return csv_data



