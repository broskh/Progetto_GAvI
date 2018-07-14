#!/usr/bin/python3
import shutil
from pathlib import Path
import argparse
import sys
import os
import time

from util import *
from whooshHelper import *
from calc import *

from whoosh.index import open_dir

TAG = "MAIN"


def main():
    manage_arguments()
    conf = config.get_config()
    log.set_log_file(conf['LOG_FILE'])
    if conf['DEBUG']:
        log.enable_debug()
    else:
        log.disable_debug()
    log.print_log("-------", "-------")
    log.print_log("START", "")
    menu = ['Index documents', 'Run query', 'Remove indexed documents',
            'Settings', 'Evaluation', 'Quit']
    i = 1
    end = False
    while not end:
        clear_terminal()
        for voice in menu:
            print(str(i) + ") " + voice)
            i = i + 1
        log.print_log("MENU", "Menu principale mostrato.")
        value = input("Choose an option: ")
        clear_terminal()
        if value == '1':
            time_start = time.time()
            indexing_helper.index_documents()
            log.print_debug(TAG, "Tempo di indicizzazione: " + str(time.time() - time_start) + " sec")
        elif value == '2':
            if os.path.exists(indexing_helper.INDEX_FOLDER_NAME):
                index = open_dir(indexing_helper.INDEX_FOLDER_NAME)
                retrieveHelper.retrieve_docs(index)
            else:
                log.print_console("ERROR", "Index a collection of documents first")
        elif value == '3':
            log.print_console(TAG, "Rimozione dell'indice in corso")
            shutil.rmtree(indexing_helper.INDEX_FOLDER_NAME, ignore_errors=True)
            input("The index has been removed. Press Enter to continue")
        elif value == '4':
            conf_menu = config_menu()
        elif value == '5':
            if os.path.exists(indexing_helper.INDEX_FOLDER_NAME):
                index = open_dir(indexing_helper.INDEX_FOLDER_NAME)
                clear_terminal()
                cfg_mod = config.get_config()
                if cfg_mod['BOOLEAN_MODEL']:
                    print("Computing Precision, Recall and Standard levels Recall using Boolean Model...")
                elif cfg_mod['FUZZY_MODEL']:
                    print("Computing Precision, Recall and Standard levels Recall using Fuzzy Model...")
                elif cfg_mod['PROBABILISTIC_MODEL']:
                    print("Computing Precision, Recall and Standard levels Recall using Probabilistic Model...")
                elif cfg_mod['VECTOR_MODEL']:
                    print("Computing Precision, Recall and Standard levels Recall using Vector Space Model...")
                precision, recall, std_recall = evaluation.run_evaluation(index)
                print('Precision: ', precision*100, '%')
                print('Recall: ', recall*100, '%')
                print('Recall a livelli standard: ')
                keys = list(std_recall.keys())
                keys.sort()
                for key in keys:
                    try:
                        float(std_recall[key])
                        lev_prec = std_recall[key]*100
                    except ValueError:
                        lev_prec = std_recall[key]
                    print('\t', key, ':\t', lev_prec, '%')

            else:
                log.print_console("ERROR", "Index a collection of documents first")
            input("Press Enter to continue")
        elif value == '6':
            end = True
        else:
            log.print_console("ERROR", "Opzione scelta non valida")
        i = 1


def config_menu():
    temp_config = config.get_config()
    menu = ['Change the path of the datasets folder',
            'Change the name of the datasets\' documents colection folder',
            'Change the name of the datasets\' qrels folder',
            'Change the name of the datasets\' query set folder', 'Enable/Disable Stemming',
            'Enable/Disable Stopwords removal', 'Enable/Disable Accent Folding',
            'Enable/Disable Q-grams', 'Change q-grams\' minimum dimension',
            'Change q-grams\' maximum dimension',
            'Change the limit of RAM per processor (MB) used for indexing',
            'Change the number of processors used for indexing',
            'Enable/Disable Multisegment for indexing', 'Change the path of the log file',
            'Enable/Disable sorting by date', 'Choose the IR Model',
            'Enable/Disable debug', 'Save and Quit', 'Quit without saving']

    i = 1
    while True:
        clear_terminal()

        for voice in menu:
            if i == 1:
                print('INDEXING:')
            elif i == 15:
                print('SEARCHING: ')
            print(str(i) + ") " + voice)
            i = i + 1

        log.print_log("MENU", "Menu di configurazione mostrato.")
        value = input("Choose an option: ")
        clear_terminal()
        if value == '1':
            while True:
                print("[Current value: '" + temp_config['DATASETS_FOLDER'] + "']")
                print("[Accepted Value: Absolute path or relative (related to the project's root folder)]")
                value = input("Insert new value: ")
                if Path(value).is_dir():
                    break
                input("Invalid value. Press Enter to continue")
                clear_terminal()
            temp_config['DATASETS_FOLDER'] = value
        elif value == '2':
            while True:
                print("[Current value: '" + temp_config['DOCUMENT_COLLECTION_FOLDER_NAME'] + "']")
                print("[Accepted value: name of the folder inside the dataset's folder]")
                value = input("Insert new value: ")
                if isinstance(value, str):
                    break
                input("Invalid value. Press Enter to continue")
                clear_terminal()
            temp_config['DOCUMENT_COLLECTION_FOLDER_NAME'] = value
        elif value == '3':
            while True:
                print("[Current value: '" + temp_config['QRELS_FOLDER_NAME'] + "']")
                print("[Accepted value: name of the folder inside the dataset's folder]")
                value = input("Insert new value: ")
                if isinstance(value, str):
                    break
                input("Invalid value. Press Enter to continue")
                clear_terminal()
            temp_config['QRELS_FOLDER_NAME'] = value
        elif value == '4':
            while True:
                print("[Current value: '" + temp_config['QUERY_SET_FOLDER_NAME'] + "']")
                print("[Accepted value: name of the folder inside the dataset's folder]")
                value = input("Insert new value: ")
                if isinstance(value, str):
                    break
                input("Invalid value. Press Enter to continue")
                clear_terminal()
            temp_config['QUERY_SET_FOLDER_NAME'] = value
        elif value == '5':
            if temp_config['STEMMING']:
                old_value = "Yes"
            else:
                old_value = "No"
            while True:
                print("[Current value: '" + old_value + "']")
                print("[Accepted value: 'Yes' or 'No']")
                value = input("Insert new value: ")
                if value == "Yes" or value == "Y" or value == "y":
                    value = True
                    break
                elif value == "No" or value == "N" or value == "n":
                    value = False
                    break
                input("Invalid value. Press Enter to continue")
                clear_terminal()
            temp_config['STEMMING'] = value
        elif value == '6':
            if temp_config['STOPWORDS']:
                old_value = "Yes"
            else:
                old_value = "No"
            while True:
                print("[Current value: '" + old_value + "']")
                print("[Accepted value: 'Yes' or 'No']")
                value = input("Insert new value: ")
                if value == "Yes" or value == "Y" or value == "y":
                    value = True
                    break
                elif value == "No" or value == "N" or value == "n":
                    value = False
                    break
                input("Invalid value. Press Enter to continue")
                clear_terminal()
            temp_config['STOPWORDS'] = value
        elif value == '7':
            if temp_config['CHARACTERS_FOLDING']:
                old_value = "Yes"
            else:
                old_value = "No"
            while True:
                print("[Current value: '" + old_value + "']")
                print("[Accepted value: 'Yes' or 'No']")
                value = input("Insert new value: ")
                if value == "Yes" or value == "Y" or value == "y":
                    value = True
                    break
                elif value == "No" or value == "N" or value == "n":
                    value = False
                    break
                input("Invalid value. Press Enter to continue")
                clear_terminal()
            temp_config['CHARACTERS_FOLDING'] = value
        elif value == '8':
            if temp_config['QGRAMS']:
                old_value = "Yes"
            else:
                old_value = "No"
            while True:
                print("[Current value: '" + old_value + "']")
                print("[Accepted value: 'Yes' or 'No']")
                value = input("Insert new value: ")
                if value == "Yes" or value == "Y" or value == "y":
                    value = True
                    break
                elif value == "No" or value == "N" or value == "n":
                    value = False
                    break
                input("Invalid value. Press Enter to continue")
                clear_terminal()
            temp_config['QGRAMS'] = value
        elif value == '9':
            while True:
                print("[Current value: '" + str(temp_config['QNUM_MIN']) + "']")
                print("[Accepted value: integer number]")
                value = input("Immetti nuovo valore: ")
                try:
                    value = int(value)
                    break
                except ValueError:
                    input("Invalid value. Press Enter to continue")
                    clear_terminal()
            temp_config['QNUM_MIN'] = value
        elif value == '10':
            while True:
                print("[Current value: '" + str(temp_config['QNUM_MAX']) + "']")
                print("[Accepted value: integer number]")
                value = input("Immetti nuovo valore: ")
                try:
                    value = int(value)
                    break
                except ValueError:
                    input("Invalid value. Press Enter to continue")
                    clear_terminal()
            temp_config['QNUM_MAX'] = value
        elif value == '11':
            while True:
                print("[Current value: '" + str(temp_config['INDEXING_RAM_LIMIT_MB_FOR_PROC']) + "']")
                print("[Accepted value: integer number]")
                value = input("Immetti nuovo valore: ")
                try:
                    value = int(value)
                    break
                except ValueError:
                    input("Invalid value. Press Enter to continue")
                    clear_terminal()
            temp_config['INDEXING_RAM_LIMIT_MB_FOR_PROC'] = value
        elif value == '12':
            while True:
                print("[Current value: '" + str(temp_config['INDEXING_PROCS_NUMBER']) + "']")
                print("[Accepted value: integer number]")
                value = input("Immetti nuovo valore: ")
                try:
                    value = int(value)
                    break
                except ValueError:
                    input("Invalid value. Press Enter to continue")
                    clear_terminal()
            temp_config['INDEXING_PROCS_NUMBER'] = value
        elif value == '13':
            if temp_config['INDEXING_MULTISEGMENT']:
                old_value = "Yes"
            else:
                old_value = "No"
            while True:
                print("[Current value: '" + old_value + "']")
                print("[Accepted value: 'Yes' or 'No']")
                value = input("Insert new value: ")
                if value == "Yes" or value == "Y" or value == "y":
                    value = True
                    break
                elif value == "No" or value == "N" or value == "n":
                    value = False
                    break
                input("Invalid value. Press Enter to continue")
                clear_terminal()
            temp_config['INDEXING_MULTISEGMENT'] = value
        elif value == '14':
            while True:
                print("[Current value: '" + temp_config['LOG_FILE'] + "']")
                print("[Accepted value: Absolute path or relative (related to the project's root folder)]")
                value = input("Insert new value: ")
                if isinstance(value, str):
                    break
                input("Invalid value. Press Enter to continue")
                clear_terminal()
            temp_config['LOG_FILE'] = value
        elif value == '15':
            if temp_config['SORT_BY_DATE']:
                old_value = "Yes"
            else:
                old_value = "No"
                # cafVal = True
            while True:
                print("[Current value: '" + old_value + "']")
                print("[Accepted Values: 'Yes' or 'No']")
                cafgVal = input("Enter new value: ")
                if cafgVal == "Yes" or cafgVal == "yes" or cafgVal == "Y" or cafgVal == "y":
                    cafgVal = True
                    break
                elif cafgVal == "No" or cafgVal == "no" or cafgVal == "N" or cafgVal == "n":
                    cafgVal = False
                    break
                input("Invalid value: press enter to continue")
                clear_terminal()
            temp_config['SORT_BY_DATE'] = cafgVal
        elif value == '16':
            irmenu = ['Enable IR Boolean model', 'Enable IR Fuzzy Model',
                      'Enable IR Probabilistic Model', 'Enable IR Vector Model',
                      'Back']
            clear_terminal()
            while True:
                j = 1
                for voice in irmenu:
                    print(str(j) + ") " + voice)
                    j = j + 1
                log.print_log("MENU", "IR Model menu showed.")
                val = input("Choose an IR Model: ")

                if val == '1':
                    temp_config['BOOLEAN_MODEL'] = True
                    temp_config['FUZZY_MODEL'] = False
                    temp_config['PROBABILISTIC_MODEL'] = False
                    temp_config['VECTOR_MODEL'] = False
                    clear_terminal()
                    print("BOOLEAN MODEL Enabled.")

                elif val == '2':
                    temp_config['BOOLEAN_MODEL'] = False
                    temp_config['FUZZY_MODEL'] = True
                    temp_config['PROBABILISTIC_MODEL'] = False
                    temp_config['VECTOR_MODEL'] = False
                    clear_terminal()
                    print("FUZZY MODEL Enabled.")

                elif val == '3':
                    temp_config['BOOLEAN_MODEL'] = False
                    temp_config['FUZZY_MODEL'] = False
                    temp_config['PROBABILISTIC_MODEL'] = True
                    temp_config['VECTOR_MODEL'] = False
                    clear_terminal()
                    print("PROBABILISTIC MODEL Enabled.")
                elif val == '4':
                    temp_config['BOOLEAN_MODEL'] = False
                    temp_config['FUZZY_MODEL'] = False
                    temp_config['PROBABILISTIC_MODEL'] = False
                    temp_config['VECTOR_MODEL'] = True
                    clear_terminal()
                    print("VECTOR MODEL Enabled.")

                elif val == '88':
                    print(' date:', temp_config['SORT_BY_DATE'], ' boolean:', temp_config['BOOLEAN_MODEL'], ' fuzzy:',
                          temp_config['FUZZY_MODEL'], ' prob:', temp_config['PROBABILISTIC_MODEL'], ' vector:', temp_config['VECTOR_MODEL'])

                elif val == '5':
                    break
                else:
                    log.print_console("ERROR", "Opzione scelta non valida")
        elif value == '17':
            if temp_config['DEBUG']:
                    old_value = "Yes"
            else:
                    old_value = "No"
            while True:
                print("[Current value: '" + old_value + "']")
                print("[Accepted value: 'Yes' or 'No']")
                value = input("Insert new value: ")
                if value == "Yes" or value == "Y" or value == "y":
                    value = True
                    break
                elif value == "No" or value == "N" or value == "n":
                    value = False
                    break
                input("Invalid value. Press Enter to continue")
                clear_terminal()
            temp_config['DEBUG'] = value
        elif value == '18':
            config.write_config(temp_config)
            break
        elif value == '19':
            break
        else:
            log.print_console("ERROR", "Opzione scelta non valida")
        i = 1
    return config.get_config()


def manage_arguments():
    # Parse arguments.
    parser = argparse.ArgumentParser(description='Software for computing information retrieval')

    parser.add_argument('--datasets-folder', help="Change the path of the datasets folder")
    parser.add_argument('--document-collection-folder-name',
                        help="Change the name of the datasets\' documents colection folder")
    parser.add_argument('--qrels-folder-name', help="Change the name of the datasets\' qrels folder")
    parser.add_argument('--query-set-folder-name',
                        help="Change the name of the datasets\' query set folder")
    parser.add_argument('--stemming', help="Enable/Disable Stemming")
    parser.add_argument('--stopwords', help="Enable/Disable Stopwords removal")
    parser.add_argument('--characters-folding', help="Enable/Disable Accent Folding")
    parser.add_argument('--qgrams', help="Enable/Disable Q-grams")
    parser.add_argument('--qnum-min', help="Change q-grams\' minimum dimension")
    parser.add_argument('--qnum-max', help="Change q-grams\' maximum dimension")
    parser.add_argument('--indexing-ram-limit-mb-for-proc',
                        help="Change the limit of RAM per processor (MB) used for indexing")
    parser.add_argument('--indexing-procs-number',
                        help="Change the number of processors used for indexing")
    parser.add_argument('--indexing-multisegment', help="Enable/Disable Multisegment for indexing")
    parser.add_argument('--sort-by-date', help='Enables/Disables sorting by date of retrieved documents')
    parser.add_argument('--boolean-model', help='Enables Information Retrieval Boolean Model')
    parser.add_argument('--fuzzy-model', help='Enables Information Retrieval Fuzzy Model')
    parser.add_argument('--probabilistic-model', help='Enables Information Retrieval Probabilistic Model')
    parser.add_argument('--vector-model', help='Enables Information Retrieval Vector Model')
    parser.add_argument('--log-file', help="Change the path of the log file")
    parser.add_argument('--debug', help="Enable/Disable debug")

    new_conf = config.get_config()
    args = vars(parser.parse_args())
    if args['datasets_folder']:
        if Path(args['datasets_folder']).is_dir():
            new_conf['DATASETS_FOLDER'] = args['datasets_folder']
        else:
            print("Invalid dataset_folder.")
            sys.exit(1)
    if args['document_collection_folder_name']:
        if isinstance(args['document_collection_folder_name'], str):
            new_conf['DOCUMENT_COLLECTION_FOLDER_NAME'] = args['document_collection_folder_name']
        else:
            print("Invalid document_collection_folder_name.")
            sys.exit(1)
    if args['qrels_folder_name']:
        if isinstance(args['qrels_folder_name'], str):
            new_conf['QRELS_FOLDER_NAME'] = args['qrels_folder_name']
        else:
            print("Invalid qrels_folder_name.")
            sys.exit(1)
    if args['query_set_folder_name']:
        if isinstance(args['query_set_folder_name'], str):
            new_conf['QUERY_SET_FOLDER_NAME'] = args['query_set_folder_name']
        else:
            print("Invalid query_set_folder_name.")
            sys.exit(1)
    if args['stemming']:
        if args['stemming'] == 'True':
            new_conf['STEMMING'] = True
        elif args['stemming'] == 'False':
            new_conf['STEMMING'] = False
        else:
            print("Invalid stemming.")
            sys.exit(1)
    if args['stopwords']:
        if args['stopwords'] == 'True':
            new_conf['STOPWORDS'] = True
        elif args['stopwords'] == 'False':
            new_conf['STOPWORDS'] = False
        else:
            print("Invalid stopwords.")
            sys.exit(1)
    if args['characters_folding']:
        if args['characters_folding'] == 'True':
            new_conf['CHARACTERS_FOLDING'] = True
        elif args['characters_folding'] == 'False':
            new_conf['CHARACTERS_FOLDING'] = False
        else:
            print("Invalid characters_folding.")
            sys.exit(1)
    if args['qgrams']:
        if args['qgrams'] == 'True':
            new_conf['QGRAMS'] = True
        elif args['qgrams'] == 'False':
            new_conf['QGRAMS'] = False
        else:
            print("Invalid qgrams.")
            sys.exit(1)
    if args['qnum_min']:
        try:
            value = int(args['qnum_min'])
            new_conf['QNUM_MIN'] = value
        except ValueError:
            print("Invalid qnum_min.")
            sys.exit(1)
    if args['qnum_max']:
        try:
            value = int(args['qnum_max'])
            new_conf['QNUM_MAX'] = value
        except ValueError:
            print("Invalid qnum_max.")
            sys.exit(1)
    if args['indexing_ram_limit_mb_for_proc']:
        try:
            value = int(args['indexing_ram_limit_mb_for_proc'])
            new_conf['INDEXING_RAM_LIMIT_MB_FOR_PROC'] = value
        except ValueError:
            print("Invalid indexing_ram_limit_mb_for_proc.")
            sys.exit(1)
    if args['indexing_procs_number']:
        try:
            value = int(args['indexing_procs_number'])
            new_conf['INDEXING_PROCS_NUMBER'] = value
        except ValueError:
            print("Invalid indexing_procs_number.")
            sys.exit(1)
    if args['indexing_multisegment']:
        if args['indexing_multisegment'] == 'True':
            new_conf['INDEXING_MULTISEGMENT'] = True
        elif args['indexing_multisegment'] == 'False':
            new_conf['INDEXING_MULTISEGMENT'] = False
        else:
            print("Invalid indexing_multisegment.")
            sys.exit(1)
    if args['log_file']:
        if isinstance(args['log_file'], str):
            new_conf['LOG_FILE'] = args['log_file']
        else:
            print("Invalid log_file.")
            sys.exit(1)
    if args['sort_by_date']:
        if args['sort_by_date'] == 'True':
            new_conf['SORT_BY_DATE'] = True
        elif args['sort_by_date'] == 'False':
            new_conf['SORT_BY_DATE'] = False
        else:
            print("Invalid value!")
            sys.exit(1)
    if args['boolean_model']:
        if args['boolean_model'] == 'True':
            new_conf['BOOLEAN_MODEL'] = True
            new_conf['FUZZY_MODEL'] = False
            new_conf['PROBABILISTIC_MODEL'] = False
            new_conf['VECTOR_MODEL'] = False
        elif args['boolean_model'] == 'False':
            new_conf['BOOLEAN_MODEL'] = False
            new_conf['FUZZY_MODEL'] = True
            new_conf['PROBABILISTIC_MODEL'] = False
            new_conf['VECTOR_MODEL'] = False
        else:
            print("Invalid value!")
            sys.exit(1)
    if args['fuzzy_model']:
        if args['fuzzy_model'] == 'True':
            new_conf['FUZZY_MODEL'] = True
            new_conf['BOOLEAN_MODEL'] = False
            new_conf['PROBABILISTIC_MODEL'] = False
            new_conf['VECTOR_MODEL'] = False
        elif args['fuzzy_model'] == 'False':
            new_conf['FUZZY_MODEL'] = False
            new_conf['BOOLEAN_MODEL'] = True
            new_conf['PROBABILISTIC_MODEL'] = False
            new_conf['VECTOR_MODEL'] = False
        else:
            print("Invalid value!")
            sys.exit(1)
    if args['probabilistic_model']:
        if args['probabilistic_model'] == 'True':
            new_conf['FUZZY_MODEL'] = False
            new_conf['BOOLEAN_MODEL'] = False
            new_conf['PROBABILISTIC_MODEL'] = True
            new_conf['VECTOR_MODEL'] = False
        elif args['probabilistic_model'] == 'False':
            new_conf['FUZZY_MODEL'] = False
            new_conf['BOOLEAN_MODEL'] = True
            new_conf['PROBABILISTIC_MODEL'] = False
            new_conf['VECTOR_MODEL'] = False
    if args['vector_model']:
        if args['vector_model'] == 'True':
            new_conf['FUZZY_MODEL'] = False
            new_conf['BOOLEAN_MODEL'] = False
            new_conf['PROBABILISTIC_MODEL'] = False
            new_conf['VECTOR_MODEL'] = True
        elif args['vector_model'] == 'False':
            new_conf['FUZZY_MODEL'] = False
            new_conf['BOOLEAN_MODEL'] = True
            new_conf['PROBABILISTIC_MODEL'] = False
            new_conf['VECTOR_MODEL'] = False
        else:
            print("Invalid value!")
            sys.exit(1)
    if args['debug']:
        if args['debug'] == 'True':
            new_conf['DEBUG'] = True
        elif args['debug'] == 'False':
            new_conf['DEBUG'] = False
        else:
            print("Invalid debug.")
            sys.exit(1)
    config.write_config(new_conf)


def clear_terminal():
    if os.name == 'nt':
        os.system('cls')
    elif os.name == 'posix':
        os.system('clear')


if __name__ == '__main__':
    main()