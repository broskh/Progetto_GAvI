import json
import os


DEFAULT_BOOLEAN = True
DEFAULT_FUZZY = False
DEFAULT_PROBABILISTIC = False
DEFAULT_SORT_BY_DATE = False

IRCONFIG_FILE = "irConfig.json"
irConfig = {}


# Import information from irConfig file and opportunely set variables
def read_ir_config():
    global irConfig
    if os.path.isfile(IRCONFIG_FILE):
        json_file = open(IRCONFIG_FILE, 'r')
        irConfig = json.load(json_file)
    else:
        irConfig['BOOLEAN_MODEL'] = DEFAULT_BOOLEAN
        irConfig['FUZZY_MODEL'] = DEFAULT_FUZZY
        irConfig['PROBABILISTIC_MODEL'] = DEFAULT_PROBABILISTIC
        irConfig['SORT_BY_DATE'] = DEFAULT_SORT_BY_DATE

        json_file = open(IRCONFIG_FILE, 'w')
        json_file.write(json.dumps(irConfig))
    json_file.close()


# Export information to irConfig file and opportunely set variables
def write_ir_config(new_irConfig):
    json_file = open(IRCONFIG_FILE, 'w')
    json_file.write(json.dumps(new_irConfig))
    json_file.close()
    global irConfig
    irConfig = new_irConfig


# Return the current irConfig file
def get_ir_config():
    if irConfig == {}:
        read_ir_config()
    return irConfig.copy()
