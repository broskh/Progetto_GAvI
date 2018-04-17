import json
import os

DEFAULT_LOG_FILE = "search_retrieval.log"
DEFAULT_DEBUG = False

DEFAULT_DATASETS_FOLDER = "datasets"
DEFAULT_DOCUMENT_COLLECTION_FOLDER_NAME = "Document_collections"
DEFAULT_QRELS_FOLDER_NAME = "qrels"
DEFAULT_QUERY_SET_FOLDER_NAME = "Query_set"

CONFIG_FILE = "config.json"
config = {}


# Import imformation from config file and opportunely set variables
def read_config():
    global config
    if os.path.isfile(CONFIG_FILE):
        json_file = open(CONFIG_FILE, 'r')
        config = json.load(json_file)
    else:
        config['LOG_FILE'] = DEFAULT_LOG_FILE
        config['DEBUG'] = DEFAULT_DEBUG
        config['DATASETS_FOLDER'] = DEFAULT_DATASETS_FOLDER
        config['DOCUMENT_COLLECTION_FOLDER_NAME'] = DEFAULT_DOCUMENT_COLLECTION_FOLDER_NAME
        config['QRELS_FOLDER_NAME'] = DEFAULT_QRELS_FOLDER_NAME
        config['QUERY_SET_FOLDER_NAME'] = DEFAULT_QUERY_SET_FOLDER_NAME
        json_file = open(CONFIG_FILE, 'w')
        json_file.write(json.dumps(config))
    json_file.close()
    return config


def set_log_file(log_file):
    return set_field('LOG_FILE', log_file)


def set_debug(debug):
    return set_field('DEBUG', debug)


def set_datasets_folder(datasets_folder):
    return set_field('DATASETS_FOLDER', datasets_folder)


def set_document_collection_folder_name(document_collection_folder_name):
    return set_field('DOCUMENT_COLLECTION_FOLDER_NAME', document_collection_folder_name)


def set_qrels_folder_name(qrels_folder_name):
    return set_field('QRELS_FOLDER_NAME', qrels_folder_name)


def set_query_set_folder_name(query_set_folder_name):
    return set_field('QUERY_SET_FOLDER_NAME', query_set_folder_name)


def set_field(key, value):
    global config
    config[key] = value
    json_file = open(CONFIG_FILE, 'w')
    json_file.write(json.dumps(config))
    json_file.close()
    return config
