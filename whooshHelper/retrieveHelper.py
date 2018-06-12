import os

from whoosh import qparser
from whoosh.qparser import QueryParser

from irUtil import *


def retrieve_docs(index):

    irCfg = irConfig.get_ir_config()

    try:
        print('[retrieve_docs] creating searcher')
        src = index.searcher()

        goOn = True
        while goOn:
            query = input('Enter query text: ')
            parser = QueryParser('content', schema=index.schema)
            print('[retrieve_docs] parser created')
            simplify_parser(parser)
            print('[retrieve_docs] parser simplified')
            print('[retrieve_docs] creating queryObject')
            p_query = parser.parse(query)

            print('[retrieve_docs] correcting query if needed')
            corrected = src.correct_query(p_query, query)
            if corrected.query != p_query:
                print("Showing results for: ", corrected.string)
                p_query = corrected.query

            print("[retrieve_docs] setting up collector")

            print('[retrieve_docs] searching')
            results = set_model_and_search(parser, src, irCfg, p_query)

            for r in results:
                print(r['title'], r['publish_date'])

            print('Found ', results.estimated_length(), ' matching documents')
            print()

            while True:
                searchAgain = input('Would you like to search again? (y/n): ')
                if searchAgain == 'Y' or searchAgain == 'y' or searchAgain == 'yes' or searchAgain == 'Yes':
                    goOn = True
                    clear_terminal()
                    break
                elif searchAgain == 'N' or searchAgain == 'n' or searchAgain == 'No' or searchAgain == 'no':
                    goOn = False
                    break
                input("Invalid value. Press enter to continue")

    finally:
        src.close()


def simplify_parser(prs):
    prs.default_set()


def set_model_and_search(prs, searcher, cfg, q):
    cltrTmp = searcher.collector(limit=10)

    if cfg['BOOLEAN_MODEL']:
        cltrTmp.prepare(searcher, q, searcher.boolean_context())
        if cfg['SORT_BY_DATE']:
            resultTmp = searcher.searc_with_collector(q, cltrTmp, sortedby='publish_date')
        else:
            resultTmp = searcher.searc_with_collector(q, cltrTmp)

        result = cltrTmp.results()
    elif cfg['FUZZY_MODEL']:
        prs.add_plugin(qparser.FuzzyTermPlugin())
        if cfg['SORT_BY_DATE']:
            result = searcher.search(q, sortedby='publish_date')
        else:
            result = searcher.search(q)
    else:
        pass

    return result


def clear_terminal():
    if os.name == 'nt':
        os.system('cls')
    elif os.name == 'posix':
        os.system('clear')
