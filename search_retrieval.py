#!/usr/bin/python3
import shutil
from pathlib import Path
import argparse
import sys
import os
import time

from util import *
from whooshHelper import *
from irUtil import *

from whoosh.index import open_dir

TAG = "MAIN"


def main():
    manage_arguments()
    conf = config.get_config()
    # irConf = irConfig.get_ir_config()
    log.set_log_file(conf['LOG_FILE'])
    if conf['DEBUG']:
        log.enable_debug()
    else:
        log.disable_debug()
    log.print_log("-------", "-------")
    log.print_log("START", "")
    menu = ['Indicizza i documenti', 'Esegui query', 'Rimuovi i documenti indicizzati',
            'Modificare la configurazione', 'Esci']
    i = 1
    end = False
    while not end:
        clear_terminal()
        for voice in menu:
            print(str(i) + ") " + voice)
            i = i + 1
        log.print_log("MENU", "Menu principale mostrato.")
        value = input("Scegli un'opzione: ")
        clear_terminal()
        if value == '1':
            time_start = time.time()
            indexing_helper.index_documents()
            log.print_debug(TAG, "Tempo di indicizzazione: " + str(time.time() - time_start) + " sec")
        elif value == '2':
            print("Scelta 2")
            if os.path.exists(indexing_helper.INDEX_FOLDER_NAME):
                index = open_dir(indexing_helper.INDEX_FOLDER_NAME)
                retrieveHelper.retrieve_docs(index)
            else:
                log.print_console("ERROR", "Index a collection of documents first")
        elif value == '3':
            log.print_console(TAG, "Rimozione dell'indice in corso")
            shutil.rmtree(indexing_helper.INDEX_FOLDER_NAME, ignore_errors=True)
            input("Indice dei documenti rimosso. Premi invio per continuare")
        elif value == '4':
            conf = config_menu()
        elif value == '5':
            end = True
        else:
            log.print_console("ERROR", "Opzione scelta non valida")
        i = 1


def config_menu():
    temp_config = config.get_config()
    menu = ['Modifica il percorso cartella dei datasets',
            'Modifica il nome della cartella contenente la collezione di documenti dei dataset',
            'Modifica il nome della cartella contenente i qrels dei dataset',
            'Modifica il nome della cartella contenente le query dei dataset', 'Abilita/Disabilita lo stemming',
            'Abilita/Disabilita la rimozione di stopwords', 'Abilita/Disabilita l\'accent folding',
            'Abilita/Disabilita la scomposizione in q-grams', 'Modifica la dimensione minima dei q-grams',
            'Modifica la dimensione massima dei q-grams',
            'Modifica il limite di memoria RAM per processore (MB) utilizzata per l\'indicizzazione',
            'Modifica il numero di processori utilizzati per l\'indicizzazione',
            'Abilita/Disabilita il multisegment per l\'indicizzazione', 'Change IR model', 'Modifica il percorso del file di log',
            'Abilita/Disabilita il debug', 'Salva ed esci', 'Esci senza salvare']
    i = 1
    while True:
        clear_terminal()
        for voice in menu:
            print(str(i) + ") " + voice)
            i = i + 1
        log.print_log("MENU", "Menu di configurazione mostrato.")
        value = input("Scegli un'opzione: ")
        clear_terminal()
        if value == '1':
            while True:
                print("[Valore attuale: '" + temp_config['DATASETS_FOLDER'] + "']")
                print("[Valore accettato: Percorso assoluto o relativo (rispetto alla cartella radice del progetto)]")
                value = input("Immetti nuovo valore: ")
                if Path(value).is_dir():
                    break
                input("Valore inserito non valido. Premi invio per continuare")
                clear_terminal()
            temp_config['DATASETS_FOLDER'] = value
        elif value == '2':
            while True:
                print("[Valore attuale: '" + temp_config['DOCUMENT_COLLECTION_FOLDER_NAME'] + "']")
                print("[Valore accettato: Nome della cartella all'interno della cartella del dataset]")
                value = input("Immetti nuovo valore: ")
                if isinstance(value, str):
                    break
                input("Valore inserito non valido. Premi invio per continuare")
                clear_terminal()
            temp_config['DOCUMENT_COLLECTION_FOLDER_NAME'] = value
        elif value == '3':
            while True:
                print("[Valore attuale: '" + temp_config['QRELS_FOLDER_NAME'] + "']")
                print("[Valore accettato: Nome della cartella all'interno della cartella del dataset]")
                value = input("Immetti nuovo valore: ")
                if isinstance(value, str):
                    break
                input("Valore inserito non valido. Premi invio per continuare")
                clear_terminal()
            temp_config['QRELS_FOLDER_NAME'] = value
        elif value == '4':
            while True:
                print("[Valore attuale: '" + temp_config['QUERY_SET_FOLDER_NAME'] + "']")
                print("[Valore accettato: Nome della cartella all'interno della cartella del dataset]")
                value = input("Immetti nuovo valore: ")
                if isinstance(value, str):
                    break
                input("Valore inserito non valido. Premi invio per continuare")
                clear_terminal()
            temp_config['QUERY_SET_FOLDER_NAME'] = value
        elif value == '5':
            if temp_config['STEMMING']:
                old_value = "Yes"
            else:
                old_value = "No"
            while True:
                print("[Valore attuale: '" + old_value + "']")
                print("[Valore accettato: 'Yes' or 'No']")
                value = input("Immetti nuovo valore: ")
                if value == "Yes" or value == "Y" or value == "y":
                    value = True
                    break
                elif value == "No" or value == "N" or value == "n":
                    value = False
                    break
                input("Valore inserito non valido. Premi invio per continuare")
                clear_terminal()
            temp_config['STEMMING'] = value
        elif value == '6':
            if temp_config['STOPWORDS']:
                old_value = "Yes"
            else:
                old_value = "No"
            while True:
                print("[Valore attuale: '" + old_value + "']")
                print("[Valore accettato: 'Yes' or 'No']")
                value = input("Immetti nuovo valore: ")
                if value == "Yes" or value == "Y" or value == "y":
                    value = True
                    break
                elif value == "No" or value == "N" or value == "n":
                    value = False
                    break
                input("Valore inserito non valido. Premi invio per continuare")
                clear_terminal()
            temp_config['STOPWORDS'] = value
        elif value == '7':
            if temp_config['CHARACTERS_FOLDING']:
                old_value = "Yes"
            else:
                old_value = "No"
            while True:
                print("[Valore attuale: '" + old_value + "']")
                print("[Valore accettato: 'Yes' or 'No']")
                value = input("Immetti nuovo valore: ")
                if value == "Yes" or value == "Y" or value == "y":
                    value = True
                    break
                elif value == "No" or value == "N" or value == "n":
                    value = False
                    break
                input("Valore inserito non valido. Premi invio per continuare")
                clear_terminal()
            temp_config['CHARACTERS_FOLDING'] = value
        elif value == '8':
            if temp_config['QGRAMS']:
                old_value = "Yes"
            else:
                old_value = "No"
            while True:
                print("[Valore attuale: '" + old_value + "']")
                print("[Valore accettato: 'Yes' or 'No']")
                value = input("Immetti nuovo valore: ")
                if value == "Yes" or value == "Y" or value == "y":
                    value = True
                    break
                elif value == "No" or value == "N" or value == "n":
                    value = False
                    break
                input("Valore inserito non valido. Premi invio per continuare")
                clear_terminal()
            temp_config['QGRAMS'] = value
        elif value == '9':
            while True:
                print("[Valore attuale: '" + str(temp_config['QNUM_MIN']) + "']")
                print("[Valore accettato: numero intero]")
                value = input("Immetti nuovo valore: ")
                try:
                    value = int(value)
                    break
                except ValueError:
                    input("Valore inserito non valido. Premi invio per continuare")
                    clear_terminal()
            temp_config['QNUM_MIN'] = value
        elif value == '10':
            while True:
                print("[Valore attuale: '" + str(temp_config['QNUM_MAX']) + "']")
                print("[Valore accettato: numero intero]")
                value = input("Immetti nuovo valore: ")
                try:
                    value = int(value)
                    break
                except ValueError:
                    input("Valore inserito non valido. Premi invio per continuare")
                    clear_terminal()
            temp_config['QNUM_MAX'] = value
        elif value == '11':
            while True:
                print("[Valore attuale: '" + str(temp_config['INDEXING_RAM_LIMIT_MB_FOR_PROC']) + "']")
                print("[Valore accettato: numero intero]")
                value = input("Immetti nuovo valore: ")
                try:
                    value = int(value)
                    break
                except ValueError:
                    input("Valore inserito non valido. Premi invio per continuare")
                    clear_terminal()
            temp_config['INDEXING_RAM_LIMIT_MB_FOR_PROC'] = value
        elif value == '12':
            while True:
                print("[Valore attuale: '" + str(temp_config['INDEXING_PROCS_NUMBER']) + "']")
                print("[Valore accettato: numero intero]")
                value = input("Immetti nuovo valore: ")
                try:
                    value = int(value)
                    break
                except ValueError:
                    input("Valore inserito non valido. Premi invio per continuare")
                    clear_terminal()
            temp_config['INDEXING_PROCS_NUMBER'] = value
        elif value == '13':
            if temp_config['INDEXING_MULTISEGMENT']:
                old_value = "Yes"
            else:
                old_value = "No"
            while True:
                print("[Valore attuale: '" + old_value + "']")
                print("[Valore accettato: 'Yes' or 'No']")
                value = input("Immetti nuovo valore: ")
                if value == "Yes" or value == "Y" or value == "y":
                    value = True
                    break
                elif value == "No" or value == "N" or value == "n":
                    value = False
                    break
                input("Valore inserito non valido. Premi invio per continuare")
                clear_terminal()
            temp_config['INDEXING_MULTISEGMENT'] = value
        elif value == '14':
            irmenu = ir_config_menu()
        elif value == '15':
            while True:
                print("[Valore attuale: '" + temp_config['LOG_FILE'] + "']")
                print("[Valore accettato: Percorso assoluto o relativo (rispetto alla cartella radice del progetto)]")
                value = input("Immetti nuovo valore: ")
                if isinstance(value, str):
                    break
                input("Valore inserito non valido. Premi invio per continuare")
                clear_terminal()
            temp_config['LOG_FILE'] = value
        elif value == '16':
            if temp_config['DEBUG']:
                old_value = "Yes"
            else:
                old_value = "No"
            while True:
                print("[Valore attuale: '" + old_value + "']")
                print("[Valore accettato: 'Yes' or 'No']")
                value = input("Immetti nuovo valore: ")
                if value == "Yes" or value == "Y" or value == "y":
                    value = True
                    break
                elif value == "No" or value == "N" or value == "n":
                    value = False
                    break
                input("Valore inserito non valido. Premi invio per continuare")
                clear_terminal()
            temp_config['DEBUG'] = value
        elif value == '17':
            config.write_config(temp_config)
            break
        elif value == '18':
            break
        else:
            log.print_console("ERROR", "Opzione scelta non valida")
        i = 1
    return config.get_config()


def ir_config_menu():
    irConfigTmp = irConfig.get_ir_config()
    irMenu = ['BOOLEAN MODEL', 'FUZZY_MODEL', 'PROBABILISTIC_MODEL', 'SORT_BY_DATE',
              'Save & Quit',
              'Quit without saving']

    i = 1
    while True:
        for voice in irMenu:
            print(str(i) + ") " + voice)
            i = i + 1
        log.print_log("IRMENU", "IR configuration menu displayed")
        value = input("Choose the IR model you want to use: ")
        clear_terminal()
        if value == '1':
            clear_terminal()            
            print("Boolean model: ENABLED")
            print()
            cfgVal = True
            
            irConfigTmp['BOOLEAN_MODEL'] = cfgVal
            irConfigTmp['FUZZY_MODEL'] = not cfgVal
            irConfigTmp['PROBABILISTIC_MODEL'] = not cfgVal
        elif value == '2':
            clear_terminal()
            print("Fuzzy model: ENABLED")
            print()
            cfgVal = True

            irConfigTmp['BOOLEAN_MODEL'] = not cfgVal
            irConfigTmp['FUZZY_MODEL'] = cfgVal
            irConfigTmp['PROBABILISTIC_MODEL'] = not cfgVal
        elif value == '3':
            clear_terminal()
            print("Probabilistic model: ENABLED")
            print()
            cfgVal = True

            irConfigTmp['BOOLEAN_MODEL'] = not cfgVal
            irConfigTmp['FUZZY_MODEL'] = not cfgVal
            irConfigTmp['PROBABILISTIC_MODEL'] = cfgVal
        elif value == '4':
            if irConfigTmp['SORT_BY_DATE']:
                old_value = "Yes"
            else:
                old_value = "No"
            while True:
                print("[Actual value: '" + old_value + "']")
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
            irConfigTmp['SORT_BY_DATE'] = cafgVal
        elif value == '5':
            irConfig.write_ir_config(irConfigTmp)
            break
        elif value == '6':
            break
        else:
            log.print_console("IRMENU ERROR", "Invalid option")
        i = 1
    return irConfig.get_ir_config()


def manage_arguments():
    # Parse arguments.
    parser = argparse.ArgumentParser(description='Software per effettuare information retrieval')

    parser.add_argument('--datasets-folder', help="Modifica il percorso cartella dei datasets")
    parser.add_argument('--document-collection-folder-name',
                        help="Modifica il nome della cartella contenente la collezione di documenti dei dataset")
    parser.add_argument('--qrels-folder-name', help="Modifica il nome della cartella contenente i qrels dei dataset")
    parser.add_argument('--query-set-folder-name',
                        help="Modifica il nome della cartella contenente le query dei dataset")
    parser.add_argument('--stemming', help="Abilita/Disabilita lo stemming")
    parser.add_argument('--stopwords', help="Abilita/Disabilita la rimozione di stopwords")
    parser.add_argument('--characters-folding', help="Abilita/Disabilita l'accent folding")
    parser.add_argument('--qgrams', help="Abilita/Disabilita la scomposizione in q-grams")
    parser.add_argument('--qnum-min', help="Modifica la dimensione minima dei q-grams")
    parser.add_argument('--qnum-max', help="Modifica la dimensione massima dei q-grams")
    parser.add_argument('--indexing-ram-limit-mb-for-proc',
                        help="Modifica il limite di memoria RAM per processore (MB) utilizzata per l'indicizzazione")
    parser.add_argument('--indexing-procs-number',
                        help="Modifica il numero di processori utilizzati per l'indicizzazione")
    parser.add_argument('--indexing-multisegment', help="Abilita/Disabilita il multisegment per l'indicizzazione")
    parser.add_argument('--log-file', help="Modifica il percorso del file di log")
    parser.add_argument('--debug', help="Abilita/Disabilita il debug")

    new_conf = config.get_config()
    args = vars(parser.parse_args())
    if args['datasets_folder']:
        if Path(args['datasets_folder']).is_dir():
            new_conf['DATASETS_FOLDER'] = args['datasets_folder']
        else:
            print("dataset_folder non valido.")
            sys.exit(1)
    if args['document_collection_folder_name']:
        if isinstance(args['document_collection_folder_name'], str):
            new_conf['DOCUMENT_COLLECTION_FOLDER_NAME'] = args['document_collection_folder_name']
        else:
            print("document_collection_folder_name non valido.")
            sys.exit(1)
    if args['qrels_folder_name']:
        if isinstance(args['qrels_folder_name'], str):
            new_conf['QRELS_FOLDER_NAME'] = args['qrels_folder_name']
        else:
            print("qrels_folder_name non valido.")
            sys.exit(1)
    if args['query_set_folder_name']:
        if isinstance(args['query_set_folder_name'], str):
            new_conf['QUERY_SET_FOLDER_NAME'] = args['query_set_folder_name']
        else:
            print("query_set_folder_name non valido.")
            sys.exit(1)
    if args['stemming']:
        if args['stemming'] == 'True':
            new_conf['STEMMING'] = True
        elif args['stemming'] == 'False':
            new_conf['STEMMING'] = False
        else:
            print("stemming non valido.")
            sys.exit(1)
    if args['stopwords']:
        if args['stopwords'] == 'True':
            new_conf['STOPWORDS'] = True
        elif args['stopwords'] == 'False':
            new_conf['STOPWORDS'] = False
        else:
            print("stopwords non valido.")
            sys.exit(1)
    if args['characters_folding']:
        if args['characters_folding'] == 'True':
            new_conf['CHARACTERS_FOLDING'] = True
        elif args['characters_folding'] == 'False':
            new_conf['CHARACTERS_FOLDING'] = False
        else:
            print("characters_folding non valido.")
            sys.exit(1)
    if args['qgrams']:
        if args['qgrams'] == 'True':
            new_conf['QGRAMS'] = True
        elif args['qgrams'] == 'False':
            new_conf['QGRAMS'] = False
        else:
            print("qgrams non valido.")
            sys.exit(1)
    if args['qnum_min']:
        try:
            value = int(args['qnum_min'])
            new_conf['QNUM_MIN'] = value
        except ValueError:
            print("qnum_min non valido.")
            sys.exit(1)
    if args['qnum_max']:
        try:
            value = int(args['qnum_max'])
            new_conf['QNUM_MAX'] = value
        except ValueError:
            print("qnum_max non valido.")
            sys.exit(1)
    if args['indexing_ram_limit_mb_for_proc']:
        try:
            value = int(args['indexing_ram_limit_mb_for_proc'])
            new_conf['INDEXING_RAM_LIMIT_MB_FOR_PROC'] = value
        except ValueError:
            print("indexing_ram_limit_mb_for_proc non valido.")
            sys.exit(1)
    if args['indexing_procs_number']:
        try:
            value = int(args['indexing_procs_number'])
            new_conf['INDEXING_PROCS_NUMBER'] = value
        except ValueError:
            print("indexing_procs_number non valido.")
            sys.exit(1)
    if args['indexing_multisegment']:
        if args['indexing_multisegment'] == 'True':
            new_conf['INDEXING_MULTISEGMENT'] = True
        elif args['indexing_multisegment'] == 'False':
            new_conf['INDEXING_MULTISEGMENT'] = False
        else:
            print("indexing_multisegment non valido.")
            sys.exit(1)
    if args['log_file']:
        if isinstance(args['log_file'], str):
            new_conf['LOG_FILE'] = args['log_file']
        else:
            print("log_file non valido.")
            sys.exit(1)
    if args['debug']:
        if args['debug'] == 'True':
            new_conf['DEBUG'] = True
        elif args['debug'] == 'False':
            new_conf['DEBUG'] = False
        else:
            print("debug non valido.")
            sys.exit(1)
    config.write_config(new_conf)


def clear_terminal():
    if os.name == 'nt':
        os.system('cls')
    elif os.name == 'posix':
        os.system('clear')


if __name__ == '__main__':
    main()
