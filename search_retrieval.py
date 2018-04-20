import os
import shutil
import gzip

from util import *

from whoosh.index import create_in
from whoosh.fields import *
from whoosh.index import open_dir
from whoosh.qparser import QueryParser

INDEX_FOLDER_NAME = "index"
conf = {}


def main():
    global conf
    conf = config.read_config()
    log.set_log_file(conf['LOG_FILE'])
    if conf['DEBUG']:
        log.enable_debug()
    else:
        log.disable_debug()
    log.print_log("-------", "-------")
    log.print_log("START", "")
    menu = ['Indicizza i documenti', 'Esegui query', 'Rimuovi i documenti indicizzati', 'Esci']
    i = 1
    end = False
    while not end:
        log.print_log("MENU", "Menu mostrato")
        for voice in menu:
            print(str(i) + ") " + voice)
            i = i+1
        choise = input("Scegli un'opzione: ")
        if choise == '1':
            indexDocuments()
        elif choise == '2':
            print("Scelta 2")
            if os.path.exists(config['DATASETS_FOLDER'] + "/" + INDEX_FOLDER_NAME):
                index = open_dir(config['DATASETS_FOLDER'] + "/" + INDEX_FOLDER_NAME)
            else:
                log.print_console ("ERROR", "Indicizza prima una collezioni documenti")
        elif choise == '3':
            shutil.rmtree(config['DATASETS_FOLDER'] + "/" + INDEX_FOLDER_NAME, ignore_errors=True)
        elif choise == '4':
            end = True
        else:
            log.print_console("ERROR", "Opzione scelta non valida")
        i = 1


def indexDocuments():
    for dataset_folder in os.listdir(conf['DATASETS_FOLDER']):
        dataset_folder = conf['DATASETS_FOLDER'] + '/' + dataset_folder
        if os.path.isdir(dataset_folder):
            documents_collection_folder = dataset_folder + '/' + conf['DOCUMENT_COLLECTION_FOLDER_NAME']
            for file in os.listdir(documents_collection_folder):
                if file.endswith(".gz"):
                    file = documents_collection_folder + '/' + file
                    with gzip.open(file, 'rb') as f_in:
                        temp_file = documents_collection_folder + '/temp.xml'
                        with open(temp_file, 'wb') as f_out:
                            shutil.copyfileobj(f_in, f_out)
                            # DO SOMETHING WITH DOCUMENT FILE
                            os.remove(temp_file)

    # schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT)
    # if not os.path.exists(config['DATASETS_FOLDER'] + "/" + INDEX_FOLDER_NAME):
    #     os.mkdir(config['DATASETS_FOLDER'] + "/" + INDEX_FOLDER_NAME)
    # ix = create_in(config['DATASETS_FOLDER'] + "/" + INDEX_FOLDER_NAME, schema)
    # writer = ix.writer()
    # writer.add_document(title=u"First document", path=u"/a", content=u"This is the first document we've added!")
    # writer.add_document(title=u"Second document", path=u"/b", content=u"The second one is even more interesting!")
    # writer.commit()


if __name__ == '__main__':
    main()
