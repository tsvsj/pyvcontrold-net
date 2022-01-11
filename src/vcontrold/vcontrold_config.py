import os, sys
import yaml

from jinja2 import Environment, FileSystemLoader, PackageLoader


class vcdConfig():
    def __init__(self, file: str = f'{os.path.dirname(__file__)}/conf.yml'):
        self.config_file = file
        self.config = self._read_config()

    def _create_config(self):
        if not os.path.exists(self.config_file):
            #j2_filer_loader = FileSystemLoader(['templates', './templates'])
            try:
                j2_filer_loader = FileSystemLoader(f'{os.path.dirname(__file__)}/templates')
            except FileNotFoundError:
                print("Failed to find directory templates")
                raise

            j2_env = Environment(loader=j2_filer_loader)
            try:
                j2_template = j2_env.get_template('conf.j2.yml')
            except FileNotFoundError:
                print("Failed to find template file")
                exit(1)

            j2_data = j2_template.render()
            try:
                with open(self.config_file, "w") as outfile:
                    outfile.write(j2_data)
            except:
                raise

        return self._read_config()


    def _read_yaml_file(self):
        try:
            with open(self.config_file, "r") as conf:
                config = yaml.safe_load(conf)
        except FileNotFoundError:
            config = self._create_config()

        return config

    def _read_config(self):
        config = self._read_yaml_file()

        if config is None:
            print(f"Config is empty and will be re-created")
            config = self._create_config()

        return config

    def write_config(self, config: dict):
        try:
            with open(self.config_file, "w") as outfile:
                yaml.safe_dump(config, outfile, default_flow_style=False)
        except:
            raise

        return True


    def get_config(self):
        try:
            return self.config
        except:
            raise
