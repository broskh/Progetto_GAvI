import os
import shutil
import gzip
import re
import xml.etree.ElementTree as ET

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
            index_documents()
        elif choise == '2':
            print("Scelta 2")
            if os.path.exists(INDEX_FOLDER_NAME):
                index = open_dir(INDEX_FOLDER_NAME)
            else:
                log.print_console("ERROR", "Indicizza prima una collezioni documenti")
        elif choise == '3':
            shutil.rmtree(INDEX_FOLDER_NAME, ignore_errors=True)
        elif choise == '4':
            end = True
        else:
            log.print_console("ERROR", "Opzione scelta non valida")
        i = 1


def clean_xml(xml):
    xml = re.sub(r'<(/)?MedlineCitationSet>', '', xml)
    xml = "<root>" + xml + "</root>"
    return xml


def index_documents():
    schema = Schema(publisher_name=TEXT, journal_title=TEXT, issn=ID, volume=NUMERIC, issue=TEXT, publish_date=DATETIME,
                    publish_season=TEXT, title=TEXT, first_page=NUMERIC, last_page=NUMERIC, language=TEXT,
                    publication_type=TEXT, publication_date_received=DATETIME, publication_date_accepted=DATETIME,
                    publication_date_revised=DATETIME, publication_date_aheadofprint=DATETIME,
                    publication_date_epublish=DATETIME, publication_date_ppublish=DATETIME,
                    publication_date_ecollection=DATETIME, content=TEXT, copyright=TEXT, coi_statment=TEXT,
                    keywords=KEYWORD)  # (stored=True)
    schema.add("author_first_name_*", TEXT, glob=True)
    schema.add("author_last_name_*", TEXT, glob=True)
    schema.add("author_middle_name_*", TEXT, glob=True)
    schema.add("author_suffix_*", TEXT, glob=True)
    schema.add("author_collective_name_*", TEXT, glob=True)
    schema.add("author_affiliation_*", TEXT, glob=True)
    schema.add("group_name_*", TEXT, glob=True)
    schema.add("group_name_*_group_component_first_name_*", TEXT, glob=True)
    schema.add("group_name_*_group_component_last_name_*", TEXT, glob=True)
    schema.add("group_name_*_group_component_middle_name_*", TEXT, glob=True)
    schema.add("group_name_*_group_component_suffix_*", TEXT, glob=True)

    if not os.path.exists(INDEX_FOLDER_NAME):
        os.mkdir(INDEX_FOLDER_NAME)
    ix = create_in(INDEX_FOLDER_NAME, schema)
    writer = ix.writer()

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
                            xml_file = open(temp_file)
                            xml = xml_file.read()
                            xml = clean_xml(xml)
                            xml = ET.fromstring(xml)
                            for article in xml.iter('Article'):
                                document = {}
                                publisher_name = list(article.iter('PublisherName'))
                                if len(publisher_name) > 0:
                                    document['publisher_name'] = publisher_name[0].text
                                journal_title = list(article.iter('JournalTitle'))
                                if len(journal_title) > 0:
                                    document['journal_title'] = journal_title[0].text
                                issn = list(article.iter('ISSN'))
                                if len(issn) > 0:
                                    document['issn'] = issn[0].text
                                volume = list(article.iter('Volume'))
                                if len(volume) > 0:
                                    document['volume'] = volume[0].text
                                issue = list(article.iter('Issue'))
                                if len(issue) > 0:
                                    document['issue'] = issue[0].text
                                journal = list(article.iter('Journal'))
                                if len(journal) > 0:
                                    pub_date = list(journal[0].iter('PubDate'))
                                    if len(pub_date) > 0:
                                        pub_date_year = list(pub_date[0].iter('Year'))
                                        if len(pub_date_year) > 0:
                                            year = int(pub_date_year[0].text)
                                            pub_date_month = list(pub_date[0].iter('Month'))
                                            if len(pub_date_month) > 0:
                                                month = int(true_month(pub_date_month[0].text))
                                                pub_date_day = list(pub_date[0].iter('Day'))
                                                if len(pub_date_day) > 0:
                                                    day = int(pub_date_day[0].text)
                                                    publish_date = datetime.datetime(year, month, day)
                                                    document['publish_date'] = publish_date
                                publish_season = list(article.iter('Season'))
                                if len(publish_season) > 0:
                                    document['publish_season'] = publish_season[0].text
                                title = list(article.iter('ArticleTitle'))
                                if len(title) > 0:
                                    document['title'] = title[0].text
                                first_page = list(article.iter('FirstPage'))
                                if len(first_page) > 0:
                                    document['first_page'] = first_page[0].text
                                last_page = list(article.iter('LastPage'))
                                if len(last_page) > 0:
                                    document['last_page'] = last_page[0].text
                                language = list(article.iter('Language'))
                                if len(language) > 0:
                                    document['language'] = language[0].text
                                i = 1
                                for author in article.iter('Author'):
                                    first_name = list(author.iter('FirstName'))
                                    if len(first_name) > 0:
                                        document['author_first_name_'+str(i)] = first_name[0].text
                                    last_name = list(author.iter('LastName'))
                                    if len(last_name) > 0:
                                        document['author_last_name_'+str(i)] = last_name[0].text
                                    middle_name = list(author.iter('MiddleName'))
                                    if len(middle_name) > 0:
                                        document['author_first_name_'+str(i)] = first_name[0].text
                                    suffix = list(author.iter('Suffix'))
                                    if len(suffix) > 0:
                                        document['author_suffix_'+str(i)] = suffix[0].text
                                    collective_name = list(author.iter('CollectiveName'))
                                    if len(collective_name) > 0:
                                        document['author_collective_name_'+str(i)] = collective_name[0].text
                                    affiliation = list(author.iter('Affiliation'))
                                    if len(affiliation) > 0:
                                        document['author_affiliation_'+str(i)] = affiliation[0].text
                                    i = i+1
                                i = 1
                                for group in article.iter('Group'):
                                    document['group_name_'+str(i)] = group.find('GroupName').text
                                    k = 0
                                    for group_component in group.iter('IndividualName'):
                                        group_component_first_name = list(group_component.iter('FirstName'))
                                        if len(group_component_first_name) > 0:
                                            key = 'group_name_'+str(i)+'_group_component_first_name_'+str(k)
                                            document[key] = group_component_first_name[0].text
                                        group_component_last_name = list(group_component.iter('LastName'))
                                        if len(group_component_last_name) > 0:
                                            key = 'group_name_'+str(i)+'_group_component_last_name_'+str(k)
                                            document[key] = group_component_last_name[0].text
                                        group_component_middle_name = list(group_component.iter('MiddleName'))
                                        if len(group_component_middle_name) > 0:
                                            key = 'group_name_'+str(i)+'_group_component_middle_name_'+str(k)
                                            document[key] = group_component_middle_name[0].text
                                        group_component_suffix = list(group_component.iter('Suffix'))
                                        if len(group_component_suffix) > 0:
                                            key = 'group_name_'+str(i)+'_group_component_suffix_'+str(k)
                                            document[key] = group_component_suffix[0].text
                                        k = k+1
                                    i = i+1
                                publication_type = list(article.iter('PublicationType'))
                                if len(publication_type) > 0:
                                    document['publication_type'] = publication_type[0].text
                                history = list(article.iter('History'))
                                if len(history) > 0:
                                    for pub_date in history[0].iter('PubDate'):
                                        if len(list(pub_date)) > 0:
                                            pub_date_year = list(pub_date.iter('Year'))
                                            if len(pub_date_year) > 0:
                                                year = int(pub_date_year[0].text)
                                                pub_date_month = list(pub_date.iter('Month'))
                                                if len(pub_date_month) > 0:
                                                    month = int(true_month(pub_date_month[0].text))
                                                    pub_date_day = list(pub_date.iter('Day'))
                                                    if len(pub_date_day) > 0:
                                                        day = int(pub_date_day[0].text)
                                                        publish_date = datetime.datetime(year, month, day)
                                                        if pub_date.attrib['PubStatus'] == 'received':
                                                            document['publication_date_received'] = publish_date
                                                        elif pub_date.attrib['PubStatus'] == 'accepted':
                                                            document['publication_date_accepted'] = publish_date
                                                        elif pub_date.attrib['PubStatus'] == 'revised':
                                                            document['publication_date_revised'] = publish_date
                                                        elif pub_date.attrib['PubStatus'] == 'aheadofprint':
                                                            document['publication_date_aheadofprint'] = publish_date
                                                        elif pub_date.attrib['PubStatus'] == 'eepublish':
                                                            document['publication_date_eepublish'] = publish_date
                                                        elif pub_date.attrib['PubStatus'] == 'ppublish':
                                                            document['publication_date_ppublish'] = publish_date
                                                        elif pub_date.attrib['PubStatus'] == 'ecollection':
                                                            document['publication_date_ecollection'] = publish_date
                                content = list(article.iter('AbstractText'))
                                if len(content) > 0:
                                    document['content'] = content[0].text
                                copyright = list(article.iter('CopyrightInformation'))
                                if copyright:
                                    document['copyright'] = copyright[0].text
                                coi_statment = list(article.iter('CoiStatement'))
                                if coi_statment:
                                    document['coi_statment'] = coi_statment[0].text
                                keywords = ""
                                for object in article.iter('Object'):
                                    if object.attrib['Type'] == 'keyword':
                                        keywords = keywords + object.findall('Param')[0].text + ","
                                if keywords != "":
                                    keywords = keywords[:-1]
                                    document['keywords'] = keywords
                                writer.add_document(**document)
                            os.remove(temp_file)
    writer.commit()


def true_month (month):
    if month.lower() == "jan":
        return 1
    if month.lower() == "feb":
        return 2
    if month.lower() == "mar":
        return 3
    if month.lower() == "apr":
        return 4
    if month.lower() == "may":
        return 5
    if month.lower() == "jun":
        return 6
    if month.lower() == "jul":
        return 7
    if month.lower() == "aug":
        return 8
    if month.lower() == "sep":
        return 9
    if month.lower() == "oct":
        return 10
    if month.lower() == "nov":
        return 11
    if month.lower() == "dec":
        return 12
    else:
        return int(month)


if __name__ == '__main__':
    main()
