import os
import xml.etree.ElementTree as ElementTree

from whoosh.index import open_dir
from whoosh import qparser
from whoosh.highlight import UppercaseFormatter
from whoosh.qparser import QueryParser

from util import *
from whooshHelper import *



TAG = "[evaluation]"

def precision(n_relevants_in_answer, n_answer):
    return n_relevants_in_answer/n_answer


def recall(n_relevants_in_answer, n_relevants):
    return n_relevants_in_answer/n_relevants


# param: lista di posizioni dei doc rilevanti in risposta, n doc rilevanti
# return: lista di dict {livellorecall, precision}
def standard_recall_levels(positions_relevants_in_answer, n_relevants):
    recall_points = []
    i = 1
    for x in positions_relevants_in_answer:
        rec = recall(i, n_relevants)
        prec = precision(i, x)
        recall_points.append({'recall': rec, 'precision': prec})
        i = i + 1
    standard_recall = [{'recall': 0, 'precision': '?'}]
    k = 0
    for j in range(10):
        rec_lev = (j+1)/10
        while recall_points[k]['recall'] < rec_lev:
            k = k + 1
            if k <= len(recall_points):
                recall_points.append({'recall': 1, 'precision': 0})
        standard_recall.append({'recall': rec_lev, 'precision': recall_points[k]['precision']})
    return standard_recall

# legge file query set e ritorna una lista di dict{id:int, testo:string}
def get_queries():
    queries = []
    conf = config.get_config()
    for dataset_folder in os.listdir(conf['DATASETS_FOLDER']):
        dataset_folder = conf['DATASETS_FOLDER'] + '/' + dataset_folder
        query_set_folder = dataset_folder + '/' + conf['QUERY_SET_FOLDER_NAME']
        for query_set_file in os.listdir(query_set_folder):
            with open(query_set_folder + '/' + query_set_file, 'rb') as queries_file:
                xml = queries_file.read()
                queries_file.close()
                xml = ElementTree.fromstring(xml)
                for xml_query in xml.iter('TOPIC'):
                    query = {}
                    qid = list(xml_query.findall("ID"))
                    if len(qid) > 0:
                        query['id'] = qid[0].text
                    title = list(xml_query.findall("TITLE"))
                    if len(title) > 0:
                        query['title'] = title[0].text
                    queries.append(query)
    return queries

#ritorna un dict{idQuery:listaPmidDocRilevantiQuery}
def get_relevants():
    relevants = {}
    conf = config.get_config()
    for dataset_folder in os.listdir(conf['DATASETS_FOLDER']):
        dataset_folder = conf['DATASETS_FOLDER'] + '/' + dataset_folder
        qrels_folder = dataset_folder + '/' + conf['QRELS_FOLDER_NAME']
        for qrels_file in os.listdir(qrels_folder):
            with open(qrels_folder + '/' + qrels_file, 'r') as file:
                lines = file.readlines()
                file.close()
                for line in lines:
                    qrel = line.split()
                    if int(qrel[3]) > 0:
                        if qrel[0] not in relevants:
                            relevants[qrel[0]] = [str(qrel[2])]
                        else:
                            relevants[qrel[0]].append(str(qrel[2]))
    return relevants

# param: querySet lista di dict{id: int, title: string}
# ritorna un dict{idQuery:lista di PmidDocInRisposta}
def get_answers(queries):
    answers = {}
    if os.path.exists(indexing_helper.INDEX_FOLDER_NAME):
        index = open_dir(indexing_helper.INDEX_FOLDER_NAME)

        irCfg = config.get_config()

        src = retrieveHelper.create_searcher(index, irCfg)

        for q in queries:
            parser, p_query = retrieveHelper.create_query(index, src, True, q['title'])

            log.print_log(TAG, 'searching')
            results = retrieveHelper.set_model_and_search(parser, src, irCfg, p_query)

            for r in results:
                if q['id'] not in answers:
                    supp = r['pmid']
                    answers[q['id']] = supp
                else:
                    supp = r['pmid']
                    answers[q['id']].append(supp)
    else:
        log.print_console("ERROR", "Index a collection of documents first")

    return answers

# param: answer=dict{idQuery:int, listaPmidDocInRisposta:lista di int}, relevants=dict{idQuery:listaPmidDocRilevantiQuery}
# return: dict{idQuery:listaPmidDocInRisposta}
def get_relevants_in_answers(answers, relevants):
    rel_in_answers = {}
    for r, a in zip(relevants, answers):
        for idr in relevants[r]:
            for ida in answers[a]:
                if idr == ida:
                    if r not in rel_in_answers:
                        rel_in_answers[str(relevants[r])] = idr
                    else:
                        rel_in_answers[str(relevants[r])].append(idr)
    return rel_in_answers


def run_evaluation():
    query_set = get_queries()

    answers = get_answers(query_set)
    n_answers = len(answers)

    relevants = get_relevants()
    for r in relevants:
        n_relevants = len(relevants)


    rel_in_ans = get_relevants_in_answers(answers, relevants)
    n_rel_in_ans = len(rel_in_ans)

    pos_rel_in_ans = []
    for id in rel_in_ans:
        for doc in rel_in_ans[id]:
            pos_rel_in_ans.append(answers[id[doc]])

    return precision(n_rel_in_ans, n_answers), recall(n_rel_in_ans, n_relevants), standard_recall_levels(pos_rel_in_ans, n_relevants)
