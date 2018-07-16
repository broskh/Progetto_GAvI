import os

from whoosh import qparser, scoring
from whoosh.highlight import UppercaseFormatter
from whoosh.qparser import QueryParser

from util import *
# from . import scoring

TAG = "[rh - retrieve_docs]"


def retrieve_docs(index):

    irCfg = config.get_config()

    try:
        src = create_searcher(index, irCfg)

        goOn = True
        while goOn:
            log.print_log(TAG, 'searching')
            parser, p_query = create_query(index, src, False)
            results = set_model_and_search(parser, src, irCfg, p_query)
            results.formatter = UppercaseFormatter()

            for r in results:
                if 'publish_date' in r.keys():
                    print(r['title'], '-', r['publish_date'].strftime('%Y-%m-%d'))
                else:
                    print(r['title'], '- no date')

                print()
                print(r['content'])
                print()

                for j in range(3):
                    print('-', end='')
                    j += j+1
                print('\n')

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

    print("Searching...")
    if cfg['BOOLEAN_MODEL']:
        cltrTmp = 0
        if cfg['SORT_BY_DATE']:
            cltrTmp = searcher.collector.SortingCollector(limit=10, sortedby="publish_date")
            cltrTmp.prepare(searcher, q, searcher.boolean_context())
            resultTmp = searcher.search_with_collector(q, cltrTmp)
        else:
            cltrTmp = searcher.collector(limit=10)
            cltrTmp.prepare(searcher, q, searcher.boolean_context())
            resultTmp = searcher.search_with_collector(q, cltrTmp)
        result = cltrTmp.results()

    elif cfg['FUZZY_MODEL']:
        prs.add_plugin(qparser.FuzzyTermPlugin())
        if cfg['SORT_BY_DATE']:
            result = searcher.search(q, sortedby="publish_date")
        else:
            result = searcher.search(q)

    elif cfg['PROBABILISTIC_MODEL']:
        if cfg['SORT_BY_DATE']:
            result = searcher.search(q, sortedby="publish_date")
        else:
            result = searcher.search(q)

    elif cfg['VECTOR_MODEL']:
        if cfg['SORT_BY_DATE']:
            result = searcher.search(q, sortedby="publish_date")
        else:
            result = searcher.search(q)

    return result


def create_searcher(index, cfg):
    log.print_log(TAG, 'creating searcher')
    print("Creating Searcher...")
    if cfg['VECTOR_MODEL']:
        src = index.searcher(weighting=scoring.TF_IDF())
    elif cfg['PROBABILISTIC_MODEL']:
        src = index.searcher(weighting=scoring.BM25F())
    else:
        src = index.searcher()

    return src


def create_query(index, src, evaluation, q=""):

    if not evaluation:
        query = input('Enter query text: ')
        parser = QueryParser('content', schema=index.schema)
        log.print_log(TAG, 'parser created')
        simplify_parser(parser)
        log.print_log(TAG, 'parser simplified')
        log.print_log(TAG, 'creating queryObject')
        p_query = parser.parse(query)

        while True:
            log.print_log(TAG, 'correcting query if needed')
            corrected = src.correct_query(p_query, query)
            if corrected.query != p_query:
                print("Did you mean: \"", corrected.string, "\"? (YES/No): ", end="")
                user_choice = input()
                if user_choice == "" or user_choice == "Yes" or user_choice == "yes" or user_choice == "Y" or user_choice == "y":
                    print("Showing results for: ", corrected.string)
                    p_query = corrected.query
                    break
                elif user_choice == "No" or user_choice == "no" or user_choice == "N" or user_choice == "n":
                    print("Showing results for: ", p_query)
                    break
                else:
                    input("Invalid value. Press Enter to continue")
            else:
                break
    else:
        parser = QueryParser('content', schema=index.schema)
        log.print_log(TAG, 'parser created')
        simplify_parser(parser)
        log.print_log(TAG, 'parser simplified')
        log.print_log(TAG, 'creating queryObject')
        p_query = parser.parse(q)

    return parser, p_query


def clear_terminal():
    if os.name == 'nt':
        os.system('cls')
    elif os.name == 'posix':
        os.system('clear')
