import os
import xml.etree.ElementTree as ElementTree

from util import *


def precision(n_relevants_in_answer, n_answer):
    return n_relevants_in_answer/n_answer


def recall(n_relevants_in_answer, n_relevants):
    return n_relevants_in_answer/n_relevants


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
            if k < len(recall_points):
                recall_points.append({'recall': 1, 'precision': 0})
        standard_recall.append({'recall': rec_lev, 'precision': recall_points[k]['precision']})
    return standard_recall


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


# def get_relevants_in_answers(answer, relevants):
#
#
# def get_answers(topics, searcher):
#
#
# def run_evaluation():
#     return precision, recall, standard_levels_recall
