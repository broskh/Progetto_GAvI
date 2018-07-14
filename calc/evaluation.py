import os
import xml.etree.ElementTree as ElementTree

from util import *
from whooshHelper import *


TAG = "[evaluation]"


def precision(n_relevants_in_answer, n_answer):
    if n_answer == 0:
        return 0
    else:
        return n_relevants_in_answer/n_answer


def recall(n_relevants_in_answer, n_relevants):
    return n_relevants_in_answer/n_relevants


# param: lista di posizioni dei doc rilevanti in risposta, n doc rilevanti
# return: dict con chiave recall level e valore la precision
def standard_recall_levels(positions_relevants_in_answer, n_relevants):
    recall_points = []
    i = 1
    for x in positions_relevants_in_answer:
        rec = recall(i, n_relevants)
        prec = precision(i, x)
        recall_points.append({'recall': rec, 'precision': prec})
        i = i + 1
    standard_recall = {'0': '?'}
    recall_points.append({'recall': 1, 'precision': 0})
    k = 0
    for j in range(10):
        rec_lev = (j+1)/10
        while recall_points[k]['recall'] < rec_lev:
            k = k + 1
            # if k < len(recall_points):
            #     recall_points.append({'recall': 1, 'precision': 0})
        standard_recall[str(rec_lev)] = recall_points[k]['precision']
    return standard_recall


# legge file query set e ritorna una lista di dict{id:testo}
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


# ritorna un dict{idQuery:listaPmidDocRilevantiQuery}
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
def get_answers(index, queries):
    answers = {}
    irCfg = config.get_config()
    src = retrieveHelper.create_searcher(index, irCfg)

    for q in queries:
        parser, p_query = retrieveHelper.create_query(index, src, True, q['title'])
        log.print_log(TAG, 'searching')
        results = retrieveHelper.set_model_and_search(parser, src, irCfg, p_query)

        if results:
            for r in results:
                if q['id'] not in answers:
                    supp = [r['pmid']]
                    answers[q['id']] = supp
                else:
                    supp = r['pmid']
                    answers[q['id']].append(supp)
        else:
            answers[q['id']] = []
    return answers


# param: answer=dict{idQuery: listaPmidDocInRisposta}, relevants=dict{idQuery:listaPmidDocRilevantiQuery}
# return: dict{idQuery:lista di posizioni}
def get_positions_relevants_in_answers(answers, relevants):
    rel_in_answers = {}

    for r in relevants.keys():
        rel_in_answers[r] = []
        if answers[r]:
            pos = 0
            for docr in relevants[r]:
                for doca in answers[r]:
                    pos = pos + 1
                    if docr == doca:
                        rel_in_answers[r].append(pos)
            rel_in_answers[r].sort()
    return rel_in_answers


def run_evaluation(index):
    queries = get_queries()
    answers = get_answers(index, queries)
    relevants = get_relevants()
    pos_rel_in_ans = get_positions_relevants_in_answers(answers, relevants)
    prec = 0
    rec = 0
    stan_rec_lev = {}

    for query in queries:
        query_id = query['id']
        query_answers = answers[query_id]
        query_relevants = relevants[query_id]
        query_pos_rel_in_ans = pos_rel_in_ans[query_id]

        prec = prec + precision(len(query_pos_rel_in_ans), len(query_answers))
        rec = rec + recall(len(query_pos_rel_in_ans), len(query_relevants))
        temp_standard_rec_lev = standard_recall_levels(query_pos_rel_in_ans, len(query_relevants))
        for key, value in temp_standard_rec_lev.items():
            if key not in stan_rec_lev:
                stan_rec_lev[key] = value
            else:
                if key != '0':
                    stan_rec_lev[key] = stan_rec_lev[key] + value

    prec = prec/len(queries)
    rec = rec/len(queries)
    for key, value in stan_rec_lev.items():
        if key != '0':
            stan_rec_lev[key] = value/len(queries)

    return prec, rec, stan_rec_lev
