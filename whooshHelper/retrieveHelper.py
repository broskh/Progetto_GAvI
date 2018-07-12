import os

from whoosh import qparser
from whoosh.highlight import UppercaseFormatter
from whoosh.qparser import QueryParser

from util import *
from . import scoring

TAG = "[rh - retrieve_docs]"


def retrieve_docs(index):

    irCfg = config.get_config()

    try:
        log.print_log(TAG, 'creating searcher')
        if irCfg['VECTOR_MODEL']:
            src = index.searcher(weighting=scoring.Cosine())
        else:
            src = index.searcher()

        goOn = True
        while goOn:
            query = input('Enter query text: ')
            parser = QueryParser('content', schema=index.schema)
            log.print_log(TAG, 'parser created')
            simplify_parser(parser)
            log.print_log(TAG, 'parser simplified')
            log.print_log(TAG, 'creating queryObject')
            p_query = parser.parse(query)

            log.print_log(TAG, 'correcting query if needed')
            corrected = src.correct_query(p_query, query)
            if corrected.query != p_query:
                print("Showing results for: ", corrected.string)
                p_query = corrected.query

            log.print_log(TAG, 'searching')
            results = set_model_and_search(parser, src, irCfg, p_query)
            results.formatter = UppercaseFormatter()

            for r in results:
                if 'publish_date' in r.keys():
                    print(r['title'], '-', r['publish_date'])
                else:
                    print(r['title'], '- no date')

                print('\n\t', end='')
                i = 0
                for char in r.highlights("content"):
                    print(char, end='')
                    i = i + 1
                    if i % 128 == 0:
                        print()
                        print('\t', end='')
                print('\n')

                for j in range(128):
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
            w = scoring.BM25F(B=0.75, K1=1.5)
            result = searcher.search(q, scored=True)

    elif cfg['VECTOR_MODEL']:
        if cfg['SORT_BY_DATE']:
            result = searcher.search(q, sortedby="publish_date")
            for r in result:
                w.score(searcher, 21, r['content'], r['pmid'], 1)
        else:
            result = searcher.search(q)

    return result


def clear_terminal():
    if os.name == 'nt':
        os.system('cls')
    elif os.name == 'posix':
        os.system('clear')
