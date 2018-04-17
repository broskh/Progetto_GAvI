import os
import shutil

from util import *

from whoosh.index import create_in
from whoosh.fields import *
from whoosh.index import open_dir
from whoosh.qparser import QueryParser

INDEX_FOLDER_NAME = "index"


def main():
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
        if choise == 1:
            indexDocuments()
        elif choise == 2:
            print("Scelta 2")
            if os.path.exists(config['DATASETS_FOLDER'] + "/" + INDEX_FOLDER_NAME):
                index = open_dir(config['DATASETS_FOLDER'] + "/" + INDEX_FOLDER_NAME)
            else:
                log.print_console ("ERROR", "Indicizza prima una collezioni documenti")
        elif choise == 3:
            shutil.rmtree(config['DATASETS_FOLDER'] + "/" + INDEX_FOLDER_NAME, ignore_errors=True)
        elif choise == 4:
            end = True
        else:
            log.print_console("ERROR", "Opzione scelta non valida")


def indexDocuments():
    schema = Schema(title=TEXT(stored=True), path=ID(stored=True), content=TEXT)
    if not os.path.exists(config['DATASETS_FOLDER'] + "/" + INDEX_FOLDER_NAME):
        os.mkdir(config['DATASETS_FOLDER'] + "/" + INDEX_FOLDER_NAME)
    ix = create_in(config['DATASETS_FOLDER'] + "/" + INDEX_FOLDER_NAME, schema)
    writer = ix.writer()
    writer.add_document(title=u"First document", path=u"/a", content=u"This is the first document we've added!")
    writer.add_document(title=u"Second document", path=u"/b", content=u"The second one is even more interesting!")
    writer.commit()


if __name__ == '__main__':
    main()


# with ix.searcher() as searcher:
#     query = QueryParser("content", ix.schema).parse("first")
#     results = searcher.search(query)
#     results[0]