import os
import yaml
import pathlib
from jinja2 import Environment, BaseLoader

VCONTROLD_CONFIG_DEFAULT = """
vcontrold_commands:
  get:
    getBetriebArtM1:
      description: Betriebsart M1
      status: enabled
      unit: 'text'
      groups: ['operation-mode']
      devices: [2094]
    getBetriebArtM2:
      description: Betriebsart M2
      status: enabled
      unit: 'text'
      groups: ['operation-mode']
      devices: [2094]
    getBetriebPartyM1:
      description: Betriebsart Party M1
      status: enabled
      unit: 'text'
      groups: ['operation-mode']
      devices: [2094]
    getBetriebPartyM2:
      description: Betriebsart Party M2
      status: enabled
      unit: 'text'
      groups: ['operation-mode']
      devices: [2094]
    getBetriebSparM1:
      description: Betriebsart Spar M1
      status: enabled
      unit: 'text'
      groups: ['operation-mode']
      devices: [2094]
    getBetriebSparM2:
      description: Betriebsart Spar M2
      status: enabled
      unit: 'text'
      groups: ['operation-mode']
      devices: [2094]
    getBrennerStarts:
      description: Ermittle die Brennerstarts
      status: enabled
      unit: 'number'
      groups: ['burner']
      devices: [2094]
    getBrennerStatus:
      description: Ermittle den Brennerstatus
      status: enabled
      unit: 'switch'
      groups: ['burner']
      devices: [2094]
    getBrennerStunden1:
      description: Ermittle die Brennerstunden Stufe 1
      status: enabled
      unit: 'hours'
      groups: ['burner']
      devices: [2094]
    getBrennerStunden2:
      description: Ermittle die Brennerstunden Stufe 2
      status: enabled
      unit: 'hours'
      groups: ['burner']
      devices: [2094]
    getDevType:
      description: Ermittle Device Typ der Anlage
      status: enabled
      unit: 'text'
      groups: ['system']
      devices: [2094]
    getError0:
      description: Ermittle Fehlerhistory Eintrag 1
      status: enabled
      unit: 'error'
      groups: ['error', 'system']
      devices: [2094]
    getError1:
      description: Ermittle Fehlerhistory Eintrag 2
      status: enabled
      unit: 'error'
      groups: ['error', 'system']
      devices: [2094]
    getError2:
      description: Ermittle Fehlerhistory Eintrag 3
      status: enabled
      unit: 'error'
      groups: ['error', 'system']
      devices: [2094]
    getError3:
      description: Ermittle Fehlerhistory Eintrag 4
      status: enabled
      unit: 'error'
      groups: ['error', 'system']
      devices: [2094]
    getError4:
      description: Ermittle Fehlerhistory Eintrag 5
      status: enabled
      unit: 'error'
      groups: ['error', 'system']
      devices: [2094]
    getError5:
      description: Ermittle Fehlerhistory Eintrag 6
      status: enabled
      unit: 'error'
      groups: ['error', 'system']
      devices: [2094]
    getError6:
      description: Ermittle Fehlerhistory Eintrag 7
      status: enabled
      unit: 'error'
      groups: ['error', 'system']
      devices: [2094]
    getError7:
      description: Ermittle Fehlerhistory Eintrag 8
      status: enabled
      unit: 'error'
      groups: ['error', 'system']
      devices: [2094]
    getError8:
      description: Ermittle Fehlerhistory Eintrag 9
      status: enabled
      unit: 'error'
      groups: ['error', 'system']
      devices: [2094]
    getError9:
      description: Ermittle Fehlerhistory Eintrag 10
      status: enabled
      unit: 'error'
      groups: ['error', 'system']
      devices: [2094]
    getMischerM1:
      description: Ermittle Mischerposition M1
      status: enabled
      unit: 'percent'
      groups: ['mixer']
      devices: [2094]
    getMischerM2:
      description: Ermittle Mischerposition M2
      status: enabled
      unit: 'percent'
      groups: ['mixer']
      devices: [2094]
    getMischerM3:
      description: Ermittle Mischerposition M3
      status: enabled
      unit: 'percent'
      groups: ['mixer']
      devices: [2094]
    getNeigungM1:
      description: Ermittle Neigung Heizkennlinie M1
      status: enabled
      unit: 'slope'
      groups: ['environment']
      devices: [2094]
    getNeigungM2:
      description: Ermittle Neigung Heizkennlinie M2
      status: enabled
      unit: 'slope'
      groups: ['environment']
      devices: [2094]
    getNiveauM1:
      description: Ermittle Niveau Heizkennlinie M1
      status: enabled
      unit: 'shift'
      groups: ['environment']
      devices: [2094]
    getNiveauM2:
      description: Ermittle Niveau Heizkennlinie M2
      status: enabled
      unit: 'shift'
      groups: ['environment']
      devices: [2094]
    getPumpeStatusM1:
      description: Ermittle den Status der Pumpe M1
      status: enabled
      unit: 'switch'
      groups: ['pumps']
      devices: [2094]
    getPumpeStatusM2:
      description: Ermittle den Status der Pumpe M2
      status: enabled
      unit: 'switch'
      groups: ['pumps']
      devices: [2094]
    getPumpeStatusSolar:
      description: Ermittle den Status der Zirkulationspumpe Solar
      status: disabled
      unit: 'switch'
      groups: ['pumps']
      devices: [2094]
    getPumpeStatusSp:
      description: Ermittle den Status der Speicherladepumpe
      status: enabled
      unit: 'switch'
      groups: ['pumps']
      devices: [2094]
    getPumpeStatusZirku:
      description: Ermittle den Status der Zirkulationspumpe
      status: enabled
      unit: 'switch'
      groups: ['pumps']
      devices: [2094]
    getSolarLeistung:
      description: Solar Leistung Gesamt
      status: enabled
      unit: 'power'
      groups: ['solar', 'power']
      devices: [2094]
    getSolarStatusWW:
      description: Ermittle den Status der Nachladeunterdrueckung
      status: enabled
      unit: 'none'
      groups: ['solar']
      devices: [2094]
    getSolarStunden:
      description: Solar Betriebsstunden
      status: enabled
      unit: 'hours'
      groups: ['solar', 'stats']
      devices: [2094]
    getStatusFrostM1:
      description: Status Frostwarnung M1
      status: enabled
      unit: 'temperature'
      groups: ['stats']
      devices: [2094]
    getStatusFrostM2:
      description: Status Frostwarnung M2
      status: enabled
      unit: 'temperature'
      groups: ['stats']
      devices: [2094]
    getStatusStoerung:
      description: Status Sammelstoerung
      status: enabled
      unit: 'switch'
      groups: ['error', 'stats']
      devices: [2094]
    getSystemTime:
      description: Ermittle Systemzeit
      status: enabled
      unit: time
      groups: ['system']
      devices: [2094]
    getTempA:
      description: Ermittle die Aussentemperatur
      status: enabled
      unit: temperature
      groups: ['temperature']
      devices: [2094]
    getTempKist:
      description: Ermittle die Kesseltemperatur
      status: enabled
      unit: temperature
      groups: ['temperature']
      devices: [2094]
    getTempKol:
      description: Ermittle die Kollektortemperatur
      status: enabled
      unit: temperature
      groups: ['temperature']
      devices: [2094]
    getTempKsoll:
      description: Ermittle die Kesselsolltemperatur
      status: enabled
      unit: temperature
      groups: ['temperature']
      devices: [2094]
    getTempPartyM1:
      description: Solltemperatur Partybetrieb M1
      status: enabled
      unit: temperature
      groups: ['temperature']
      devices: [2094]
    getTempPartyM2:
      description: Solltemperatur Partybetrieb M2
      status: enabled
      unit: temperature
      groups: ['temperature']
      devices: [2094]
    getTempRaumNorSollM1:
      description: Ermittle die Raumsolltemperatur normal M1
      status: enabled
      unit: temperature
      groups: ['temperature']
      devices: [2094]
    getTempRaumNorSollM2:
      description: Ermittle die Raumsolltemperatur normal M2
      status: enabled
      unit: temperature
      groups: ['temperature']
      devices: [2094]
    getTempRaumRedSollM1:
      description: Ermittle die Raumsolltemperatur reduziert M1
      status: enabled
      unit: temperature
      groups: ['temperature']
      devices: [2094]
    getTempRaumRedSollM2:
      description: Ermittle die Raumsolltemperatur reduziert M2
      status: enabled
      unit: temperature
      groups: ['temperature']
      devices: [2094]
    getTempSpu:
      description: Ermittle die Speichertemperatur unten
      status: enabled
      unit: temperature
      groups: ['temperature']
      devices: [2094]
    getTempVListM1:
      description: Ermittle die Vorlauftemperatur M1
      status: disabled
      unit: temperature
      groups: ['temperature']
      devices: [2094]
    getTempVListM2:
      description: Ermittle die Vorlauftemperatur M2
      status: enabled
      unit: temperature
      groups: ['temperature']
      devices: [2094]
    getTempVLsollM1:
      description: Ermittle die Vorlaufsolltemperatur M1
      status: enabled
      unit: temperature
      groups: ['temperature']
      devices: [2094]
    getTempVLsollM2:
      description: Ermittle die Vorlaufsolltemperatur M2
      status: enabled
      unit: temperature
      groups: ['temperature']
      devices: [2094]
    getTempVLsollM3:
      description: Ermittle die Vorlaufsolltemperatur M3
      status: enabled
      unit: temperature
      groups: ['temperature']
      devices: [2094]
    getTempWWist:
      description: Ermittle die Warmwassertemperatur
      status: enabled
      unit: temperature
      groups: ['temperature']
      devices: [2094]
    getTempWWsoll:
      description: Ermittle die Warmwassersolltemperatur
      status: enabled
      unit: temperature
      groups: ['temperature']
      devices: [2094]
    getTimerM1Di:
      description: Schaltzeit Dienstag M1
      status: enabled
      unit: 'timer'
      groups: ['timer']
      devices: [2094]
    getTimerM1Do:
      description: Schaltzeit Donnerstag M1
      status: enabled
      unit: 'timer'
      groups: ['timer']
      devices: [2094]
    getTimerM1Fr:
      description: Schaltzeit Freitag M1
      status: enabled
      unit: 'timer'
      groups: ['timer']
      devices: [2094]
    getTimerM1Mi:
      description: Schaltzeit Mittwoch M1
      status: enabled
      unit: 'timer'
      groups: ['timer']
      devices: [2094]
    getTimerM1Mo:
      description: Schaltzeit Montag M1
      status: enabled
      unit: 'timer'
      groups: ['timer']
      devices: [2094]
    getTimerM1Sa:
      description: Schaltzeit Samstag M1
      status: enabled
      unit: 'timer'
      groups: ['timer']
      devices: [2094]
    getTimerM1So:
      description: Schaltzeit Sonntag M1
      status: enabled
      unit: 'timer'
      groups: ['timer']
      devices: [2094]
    getTimerM2Di:
      description: Schaltzeit Dienstag M2
      status: enabled
      unit: 'timer'
      groups: ['timer']
      devices: [2094]
    getTimerM2Do:
      description: Schaltzeit Donnerstag M2
      status: enabled
      unit: 'timer'
      groups: ['timer']
      devices: [2094]
    getTimerM2Fr:
      description: Schaltzeit Freitag M2
      status: enabled
      unit: 'timer'
      groups: ['timer']
      devices: [2094]
    getTimerM2Mi:
      description: Schaltzeit Mittwoch M2
      status: enabled
      unit: 'timer'
      groups: ['timer']
      devices: [2094]
    getTimerM2Mo:
      description: Schaltzeit Montag M2
      status: enabled
      unit: 'timer'
      groups: ['timer']
      devices: [2094]
    getTimerM2Sa:
      description: Schaltzeit Samstag M2
      status: enabled
      unit: 'timer'
      groups: ['timer']
      devices: [2094]
    getTimerM2So:
      description: Schaltzeit Sonntag M2
      status: enabled
      unit: 'timer'
      groups: ['timer']
      devices: [2094]
    getTimerWWDi:
      description: Schaltzeit Dienstag Warmwasser
      status: enabled
      unit: 'timer'
      groups: ['timer']
      devices: [2094]
    getTimerWWDo:
      description: Schaltzeit Donnerstag Warmwasser
      status: enabled
      unit: 'timer'
      groups: ['timer']
      devices: [2094]
    getTimerWWFr:
      description: Schaltzeit Freitag Warmwasser
      status: enabled
      unit: 'timer'
      groups: ['timer']
      devices: [2094]
    getTimerWWMi:
      description: Schaltzeit Mittwoch Warmwasser
      status: enabled
      unit: 'timer'
      groups: ['timer']
      devices: [2094]
    getTimerWWMo:
      description: Schaltzeit Montag Warmwasser
      status: enabled
      unit: 'timer'
      groups: ['timer']
      devices: [2094]
    getTimerWWSa:
      description: Schaltzeit Samstag Warmwasser
      status: enabled
      unit: 'timer'
      groups: ['timer']
      devices: [2094]
    getTimerWWSo:
      description: Schaltzeit Sonntag Warmwasser
      status: enabled
      unit: 'timer'
      groups: ['timer']
      devices: [2094]
    getTimerZirkuDi:
      description: Schaltzeit Dienstag Zirku
      status: enabled
      unit: 'timer'
      groups: ['timer']
      devices: [2094]
    getTimerZirkuDo:
      description: Schaltzeit Donnerstag Zirku
      status: enabled
      unit: 'timer'
      groups: ['timer']
      devices: [2094]
    getTimerZirkuFr:
      description: Schaltzeit Freitag Zirku
      status: enabled
      unit: 'timer'
      groups: ['timer']
      devices: [2094]
    getTimerZirkuMi:
      description: Schaltzeit Mittwoch Zirku
      status: enabled
      unit: 'timer'
      groups: ['timer']
      devices: [2094]
    getTimerZirkuMo:
      description: Schaltzeit Montag Zirku
      status: enabled
      unit: 'timer'
      groups: ['timer']
      devices: [2094]
    getTimerZirkuSa:
      description: Schaltzeit Samstag Zirku
      status: enabled
      unit: 'timer'
      groups: ['timer']
      devices: [2094]
    getTimerZirkuSo:
      description: Schaltzeit Sonntag Zirku
      status: enabled
      unit: 'timer'
      groups: ['timer']
      devices: [2094]
  set:
    setBetriebArtM1:
      description: Setze Betriebsart M1
      status: enabled
      unit: 'none'
      groups: []
      devices: [2094]
    setBetriebPartyM1:
      description: Setze Betriebsart Party M1
      status: enabled
      unit: 'none'
      groups: []
      devices: [2094]
    setBetriebPartyM2:
      description: Setze Betriebsart Party M2
      status: enabled
      unit: 'none'
      groups: []
      devices: [2094]
    setBetriebSparM1:
      description: Setze Betriebsart Spar M1
      status: enabled
      unit: 'none'
      groups: []
      devices: [2094]
    setNeigungM1:
      description: Setze Neigung Heizkennlinie M1
      status: enabled
      unit: 'slope'
      groups: []
      devices: [2094]
    setNeigungM2:
      description: Setze Neigung Heizkennlinie M2
      status: enabled
      unit: 'slope'
      groups: []
      devices: [2094]
    setNiveauM1:
      description: Setze Niveau Heizkennlinie M1
      status: enabled
      unit: 'shift'
      groups: []
      devices: [2094]
    setNiveauM2:
      description: Setze Niveau Heizkennlinie M2
      status: enabled
      unit: 'shift'
      groups: []
      devices: [2094]
    setPumpeStatusZirku:
      description: Setze den Status der Zirkulationspumpe
      status: enabled
      unit: ''
      groups: []
      devices: [2094]
    setSystemTime:
      description: Setze Systemzeit
      status: enabled
      unit: T
      groups: []
      devices: [2094]
    setTempPartyM1:
      description: Setze die Warmwassersolltemperatur Party M1
      status: enabled
      unit: temperature
      groups: []
      devices: [2094]
    setTempPartyM2:
      description: Setze die Warmwassersolltemperatur Party M2
      status: enabled
      unit: temperature
      groups: []
      devices: [2094]
    setTempRaumNorSollM1:
      description: Setze die Raumsolltemperatur normal M1
      status: enabled
      unit: temperature
      groups: []
      devices: [2094]
    setTempRaumRedSollM1:
      description: Setze die Raumsolltemperatur reduziert M1
      status: enabled
      unit: temperature
      groups: []
      devices: [2094]
    setTempWWsoll:
      description: Setze die Warmwassersolltemperatur
      status: enabled
      unit: temperature
      groups: []
      devices: [2094]
    setTimerM1Di:
      description: Schaltzeit Dienstag M1
      status: enabled
      unit: ''
      groups: []
      devices: [2094]
    setTimerM1Do:
      description: ''
      status: enabled
      unit: ''
      groups: []
      devices: [2094]
    setTimerM1Fr:
      description: ''
      status: enabled
      unit: ''
      groups: []
      devices: [2094]
    setTimerM1Mi:
      description: ''
      status: enabled
      unit: ''
      groups: []
      devices: [2094]
    setTimerM1Mo:
      description: Schaltzeit Montag M1
      status: enabled
      unit: ''
      groups: []
      devices: [2094]
    setTimerM1Sa:
      description: Schaltzeit Samstag M1
      status: enabled
      unit: ''
      groups: []
      devices: [2094]
    setTimerM1So:
      description: Schaltzeit Sonntag M1
      status: enabled
      unit: ''
      groups: []
      devices: [2094]
    setTimerM2Di:
      description: Schaltzeit Dienstag M2
      status: enabled
      unit: ''
      groups: []
      devices: [2094]
    setTimerM2Do:
      description: Schaltzeit Donnerstag M2
      status: enabled
      unit: ''
      groups: []
      devices: [2094]
    setTimerM2Fr:
      description: Schaltzeit Freitag M2
      status: enabled
      unit: ''
      groups: []
      devices: [2094]
    setTimerM2Mi:
      description: Schaltzeit Mittwoch M2
      status: enabled
      unit: ''
      groups: []
      devices: [2094]
    setTimerM2Mo:
      description: Schaltzeit Montag M2
      status: enabled
      unit: ''
      groups: []
      devices: [2094]
    setTimerM2Sa:
      description: Schaltzeit Samstag M2
      status: enabled
      unit: ''
      groups: []
      devices: [2094]
    setTimerM2So:
      description: Schaltzeit Sonntag M2
      status: enabled
      unit: ''
      groups: []
      devices: [2094]
    setTimerWWDi:
      description: Schaltzeit Dienstag Warmwasser
      status: enabled
      unit: ''
      groups: []
      devices: [2094]
    setTimerWWDo:
      description: Schaltzeit Donnerstag Warmwasser
      status: enabled
      unit: ''
      groups: []
      devices: [2094]
    setTimerWWFr:
      description: Schaltzeit Freitag Warmwasser
      status: enabled
      unit: ''
      groups: []
      devices: [2094]
    setTimerWWMi:
      description: Schaltzeit Mittwoch Warmwasser
      status: enabled
      unit: ''
      groups: []
      devices: [2094]
    setTimerWWMo:
      description: Schaltzeit Montag Warmwasser
      status: enabled
      unit: ''
      groups: []
      devices: [2094]
    setTimerWWSa:
      description: Schaltzeit Samstag Warmwasser
      status: enabled
      unit: ''
      groups: []
      devices: [2094]
    setTimerWWSo:
      description: Schaltzeit Sonntag Warmwasser
      status: enabled
      unit: ''
      groups: []
      devices: [2094]
    setTimerZirkuDi:
      description: Schaltzeit Dienstag Zirkulatonspumpe
      status: enabled
      unit: ''
      groups: []
      devices: [2094]
    setTimerZirkuDo:
      description: Schaltzeit Donnerstag Zirkulatonspumpe
      status: enabled
      unit: ''
      groups: []
      devices: [2094]
    setTimerZirkuFr:
      description: Schaltzeit Freitag Zirkulatonspumpe
      status: enabled
      unit: ''
      groups: []
      devices: [2094]
    setTimerZirkuMi:
      description: Schaltzeit Mittwoch Zirkulatonspumpe
      status: enabled
      unit: ''
      groups: []
      devices: [2094]
    setTimerZirkuMo:
      description: Schaltzeit Montag Zirkulatonspumpe
      status: enabled
      unit: ''
      groups: []
      devices: [2094]
    setTimerZirkuSa:
      description: Schaltzeit Samstag Zirkulatonspumpe
      status: enabled
      unit: ''
      groups: []
      devices: [2094]
    setTimerZirkuSo:
      description: Schaltzeit Sonntag Zirkulatonspumpe
      status: enabled
      unit: ''
      groups: []
      devices: [2094]

"""


class vcdConfig():
    def __init__(self, file: str):
        self.config_file = file
        self.config = self._read_config()

    def _create_config(self):
        if not os.path.exists(self.config_file):
            j2_env = Environment(loader=BaseLoader).from_string(VCONTROLD_CONFIG_DEFAULT)
            j2_data = j2_env.render()
            print(f"Creating non-existent default config at path {self.config_file}...", end='')
            try:
                with open(self.config_file, "w") as outfile:
                    outfile.write(j2_data)
            except PermissionError:
                print("failed")
                print(f"Failed to create default config at path {self.config_file}, because permission denied. Please check directory permissions to allow the initial creation of the configuration file.")
            except:
                print("failed")
                raise
            else:
                print("success")

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
