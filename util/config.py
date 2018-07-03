import json
import os

DEFAULT_LOG_FILE = "search_retrieval.log"
DEFAULT_DEBUG = False
DEFAULT_DATASETS_FOLDER = "datasets"
DEFAULT_DOCUMENT_COLLECTION_FOLDER_NAME = "Document_collections"
DEFAULT_QRELS_FOLDER_NAME = "qrels"
DEFAULT_QUERY_SET_FOLDER_NAME = "Query_set"
DEFAULT_STEMMING = True
DEFAULT_STOPWORDS = True
DEFAULT_CHARACTERS_FOLDING = True
DEFAULT_QGRAMS = True
DEFAULT_QNUM_MIN = 2
DEFAULT_QNUM_MAX = 2
DEFAULT_INDEXING_RAM_LIMIT_MB_FOR_PROC = 128
DEFAULT_INDEXING_PROCS_NUMBERS = 1
DEFAULT_INDEXING_MULTISEGMENT = False
DEFAULT_BOOLEAN = True
DEFAULT_FUZZY = False
DEFAULT_PROBABILISTIC = False
DEFAULT_SORT_BY_DATE = False

CONFIG_FILE = "config.json"
config = {}


# Import information from config file and opportunely set variables
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
        config['STEMMING'] = DEFAULT_STEMMING
        config['STOPWORDS'] = DEFAULT_STOPWORDS
        config['CHARACTERS_FOLDING'] = DEFAULT_CHARACTERS_FOLDING
        config['QGRAMS'] = DEFAULT_QGRAMS
        config['QNUM_MIN'] = DEFAULT_QNUM_MIN
        config['QNUM_MAX'] = DEFAULT_QNUM_MAX
        config['INDEXING_RAM_LIMIT_MB_FOR_PROC'] = DEFAULT_INDEXING_RAM_LIMIT_MB_FOR_PROC
        config['INDEXING_PROCS_NUMBER'] = DEFAULT_INDEXING_PROCS_NUMBERS
        config['INDEXING_MULTISEGMENT'] = DEFAULT_INDEXING_MULTISEGMENT
        config['BOOLEAN_MODEL'] = DEFAULT_BOOLEAN
        config['FUZZY_MODEL'] = DEFAULT_FUZZY
        config['PROBABILISTIC_MODEL'] = DEFAULT_PROBABILISTIC
        config['SORT_BY_DATE'] = DEFAULT_SORT_BY_DATE

        json_file = open(CONFIG_FILE, 'w')
        json_file.write(json.dumps(config))
    json_file.close()


# Export information to config file and opportunely set variables
def write_config(new_config):
    json_file = open(CONFIG_FILE, 'w')
    json_file.write(json.dumps(new_config))
    json_file.close()
    global config
    config = new_config


# Return the current config file
def get_config():
    if config == {}:
        read_config()
    return config.copy()


# def set_log_file(log_file):
#     return set_field('LOG_FILE', log_file)
#
#
# def set_debug(debug):
#     return set_field('DEBUG', debug)
#
#
# def set_datasets_folder(datasets_folder):
#     return set_field('DATASETS_FOLDER', datasets_folder)
#
#
# def set_document_collection_folder_name(document_collection_folder_name):
#     return set_field('DOCUMENT_COLLECTION_FOLDER_NAME', document_collection_folder_name)
#
#
# def set_qrels_folder_name(qrels_folder_name):
#     return set_field('QRELS_FOLDER_NAME', qrels_folder_name)
#
#
# def set_query_set_folder_name(query_set_folder_name):
#     return set_field('QUERY_SET_FOLDER_NAME', query_set_folder_name)
#
#
# def set_stemming(stemming):
#     return set_field('STEMMING', stemming)
#
#
# def set_stopwords(stopwords):
#     return set_field('STOPWORDS', stopwords)
#
#
# def set_characters_folding(characters_folding):
#     return set_field('CHARACTERS_FOLDING', characters_folding)
#
#
# def set_qgrams(qgrams):
#     return set_field('QGRAMS', qgrams)
#
#
# def set_qnum_min(qnum_min):
#     return set_field('QNUM_MIN', qnum_min)
#
#
# def set_qnum_max(qnum_max):
#     return set_field('QNUM_MAX', qnum_max)
#
#
# def set_indexing_ram_limit_mb_for_proc(indexing_ram_limit_mb_for_proc):
#     return set_field('DEFAULT_INDEXING_RAM_LIMIT_MB_FOR_PROC', indexing_ram_limit_mb_for_proc)
#
#
# def set_indexing_procs_number(indexing_procs_number):
#     return set_field('DEFAULT_INDEXING_PROCS_NUMBER', indexing_procs_number)
#
#
# def set_indexing_multisegment(indexing_multisegment):
#     return set_field('DEFAULT_INDEXING_MULTISEGMENT', indexing_multisegment)
#
#
# def set_field(key, value):
#     global config
#     config[key] = value
#     json_file = open(CONFIG_FILE, 'w')
#     json_file.write(json.dumps(config))
#     json_file.close()
#     return config
