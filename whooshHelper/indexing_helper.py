import gzip
import os
import xml.etree.ElementTree as ElementTree

from whoosh.analysis import StopFilter
from whoosh.analysis import RegexTokenizer
from whoosh.analysis import StemFilter
from whoosh.analysis import CharsetFilter
from whoosh.analysis import NgramFilter
from whoosh.index import create_in
from whoosh.index import exists_in
from whoosh.index import open_dir
from whoosh.support.charset import accent_map
from whoosh.fields import *

from util import *

INDEX_FOLDER_NAME = "index"
READ_BYTE_BLOCK_SIZE = 419430400  # 400MB
END_BLOCK_FILE = b"</MedlineCitation>"
TAG = "INDEXING"


# Indexes documents
def index_documents():
    conf = config.get_config()
    if not os.path.exists(INDEX_FOLDER_NAME):
        os.mkdir(INDEX_FOLDER_NAME)
        log.print_console(TAG, "Creata cartella '" + INDEX_FOLDER_NAME + "'.")
    if exists_in(INDEX_FOLDER_NAME):
        ix = open_dir(INDEX_FOLDER_NAME)
        log.print_console(TAG, "Aperto indice esistente.")
    else:
        schema = create_schema()
        ix = create_in(INDEX_FOLDER_NAME, schema)
        log.print_console(TAG, "Creato nuovo indice.")
    writer = ix.writer(limitmb=conf['INDEXING_RAM_LIMIT_MB_FOR_PROC'], procs=conf['INDEXING_PROCS_NUMBER'],
                       multisegment=conf['INDEXING_MULTISEGMENT'])

    log.print_console(TAG, "Indicizzazione iniziata.")
    for dataset_folder in os.listdir(conf['DATASETS_FOLDER']):
        dataset_folder = conf['DATASETS_FOLDER'] + '/' + dataset_folder
        if os.path.isdir(dataset_folder):
            log.print_console(TAG, "Indicizzazione del dataset: '" + dataset_folder + "' iniziata.")
            documents_collection_folder = dataset_folder + '/' + conf['DOCUMENT_COLLECTION_FOLDER_NAME']
            for file in os.listdir(documents_collection_folder):
                if file.endswith(".gz"):
                    file = documents_collection_folder + '/' + file
                    log.print_console(TAG, "Indicizzazione del file: '" + file + "' iniziata.")
                    with gzip.open(file, 'rb') as f_in:
                        temp_files = split_dataset_document(f_in, documents_collection_folder)
                        f_in.close()
                        for temp_file in temp_files:
                            log.print_debug(TAG, "Indicizzazione del file temporaneo: '" + temp_file + "' iniziata.")
                            xml_file = open(temp_file)
                            xml = xml_file.read()
                            xml_file.close()
                            xml = clean_xml(xml)
                            xml = ElementTree.fromstring(xml)
                            for medline_citation in xml.iter('MedlineCitation'):
                                writer.update_document(**set_document_fields(medline_citation))
                            log.print_debug(TAG, "Indicizzazione del file temporaneo: '" + temp_file + "' terminata.")
                        remove_files(temp_files)
                    log.print_console(TAG, "Indicizzazione del file: '" + file + "' terminata.")
            log.print_console(TAG, "Indicizzazione del dataset: '" + dataset_folder + "' terminata.")
    writer.commit(optimize=True)
    log.print_console(TAG, "Indicizzazione terminata.")


# Create the schema for the index
def create_schema():
    my_analyzer = create_analyzer()
    schema = Schema(pmid=ID(unique=True, stored=True), publisher_name=TEXT(stored=True, analyzer=my_analyzer),
                    journal_title=TEXT(stored=True, analyzer=my_analyzer), issn=ID(stored=True),
                    volume=TEXT(stored=True, analyzer=my_analyzer), issue=TEXT(stored=True, analyzer=my_analyzer),
                    publish_date=DATETIME(stored=True), publish_season=TEXT(stored=True, analyzer=my_analyzer),
                    title=TEXT(stored=True, analyzer=my_analyzer), first_page=NUMERIC(stored=True),
                    last_page=NUMERIC(stored=True), language=TEXT(stored=True, analyzer=my_analyzer),
                    publication_type=TEXT(stored=True, analyzer=my_analyzer),
                    publication_date_received=DATETIME(stored=True), publication_date_accepted=DATETIME(stored=True),
                    publication_date_revised=DATETIME(stored=True), publication_date_aheadofprint=DATETIME(stored=True),
                    publication_date_epublish=DATETIME(stored=True), publication_date_ppublish=DATETIME(stored=True),
                    publication_date_ecollection=DATETIME(stored=True), content=TEXT(stored=True, analyzer=my_analyzer),
                    copyright=TEXT(stored=True, analyzer=my_analyzer),
                    coi_statment=TEXT(stored=True, analyzer=my_analyzer), keywords=KEYWORD)
    schema.add("author_first_name_*", TEXT(stored=True, analyzer=my_analyzer), glob=True)
    schema.add("author_last_name_*", TEXT(stored=True, analyzer=my_analyzer), glob=True)
    schema.add("author_middle_name_*", TEXT(stored=True, analyzer=my_analyzer), glob=True)
    schema.add("author_suffix_*", TEXT(stored=True, analyzer=my_analyzer), glob=True)
    schema.add("author_collective_name_*", TEXT(stored=True, analyzer=my_analyzer), glob=True)
    schema.add("author_affiliation_*", TEXT(stored=True, analyzer=my_analyzer), glob=True)
    schema.add("group_name_*", TEXT(stored=True, analyzer=my_analyzer), glob=True)
    schema.add("group_name_*_group_component_first_name_*", TEXT(stored=True, analyzer=my_analyzer), glob=True)
    schema.add("group_name_*_group_component_last_name_*", TEXT(stored=True, analyzer=my_analyzer), glob=True)
    schema.add("group_name_*_group_component_middle_name_*", TEXT(stored=True, analyzer=my_analyzer), glob=True)
    schema.add("group_name_*_group_component_suffix_*", TEXT(stored=True, analyzer=my_analyzer), glob=True)
    log.print_debug(TAG, "Schema creato")
    return schema


# Create the analyzer for the schema
def create_analyzer():
    conf = config.get_config()
    if conf['STOPWORDS']:
        if conf['CHARACTERS_FOLDING']:
            if conf['STEMMING']:
                if conf['QGRAMS']:
                    analyzer = RegexTokenizer() | StopFilter() | CharsetFilter(accent_map) | StemFilter() \
                               | NgramFilter(minsize=conf['QNUM_MIN'], maxsize=conf['QNUM_MAX'])
                else:
                    analyzer = RegexTokenizer() | StopFilter() | CharsetFilter(accent_map) | StemFilter()
            else:
                if conf['QGRAMS']:
                    analyzer = RegexTokenizer() | StopFilter() | CharsetFilter(accent_map) \
                               | NgramFilter(minsize=conf['QNUM_MIN'], maxsize=conf['QNUM_MAX'])
                else:
                    analyzer = RegexTokenizer() | StopFilter() | CharsetFilter(accent_map)
        else:
            if conf['STEMMING']:
                if conf['QGRAMS']:
                    analyzer = RegexTokenizer() | StopFilter() | StemFilter() \
                               | NgramFilter(minsize=conf['QNUM_MIN'], maxsize=conf['QNUM_MAX'])
                else:
                    analyzer = RegexTokenizer() | StopFilter() | StemFilter()
            else:
                if conf['QGRAMS']:
                    analyzer = RegexTokenizer() | StopFilter() \
                               | NgramFilter(minsize=conf['QNUM_MIN'], maxsize=conf['QNUM_MAX'])
                else:
                    analyzer = RegexTokenizer() | StopFilter()
    else:
        if conf['CHARACTERS_FOLDING']:
            if conf['STEMMING']:
                if conf['QGRAMS']:
                    analyzer = RegexTokenizer() | CharsetFilter(accent_map) | StemFilter() \
                               | NgramFilter(minsize=conf['QNUM_MIN'], maxsize=conf['QNUM_MAX'])
                else:
                    analyzer = RegexTokenizer() | CharsetFilter(accent_map) | StemFilter()
            else:
                if conf['QGRAMS']:
                    analyzer = RegexTokenizer() | CharsetFilter(accent_map) \
                               | NgramFilter(minsize=conf['QNUM_MIN'], maxsize=conf['QNUM_MAX'])
                else:
                    analyzer = RegexTokenizer() | CharsetFilter(accent_map)
        else:
            if conf['STEMMING']:
                if conf['QGRAMS']:
                    analyzer = RegexTokenizer() | StemFilter() \
                               | NgramFilter(minsize=conf['QNUM_MIN'], maxsize=conf['QNUM_MAX'])
                else:
                    analyzer = RegexTokenizer() | StemFilter()
            else:
                if conf['QGRAMS']:
                    analyzer = RegexTokenizer() | NgramFilter(minsize=conf['QNUM_MIN'], maxsize=conf['QNUM_MAX'])
                else:
                    analyzer = RegexTokenizer()
    log.print_debug(TAG, "Analizzatore creato")
    return analyzer


# Divides a large dataset document into smaller files
def split_dataset_document(file, folder_temp):
    j = 0
    xml = file.read(1)
    temp_files = []
    while xml:
        j = j + 1
        xml = xml + file.read(READ_BYTE_BLOCK_SIZE)
        test_end = file.read(len(END_BLOCK_FILE))
        xml = xml + test_end
        while not test_end == END_BLOCK_FILE and test_end != b"":
            if END_BLOCK_FILE.find(list(END_BLOCK_FILE)[0]) in test_end and test_end.find(b"<") != 0:
                test_end = test_end[test_end.find(b"<"):]
                read_num = len(END_BLOCK_FILE) - len(test_end)
            else:
                test_end = b""
                read_num = len(END_BLOCK_FILE)
            last_bytes = file.read(read_num)
            xml = xml + last_bytes
            test_end = test_end + last_bytes
        temp_file = folder_temp + '/temp' + str(j) + '.xml'
        with open(temp_file, 'wb') as f_out:
            f_out.write(xml)
            f_out.close()
            temp_files.append(temp_file)
            xml = file.read(1)
    return temp_files


# Look for some specific values in the xml element and inserts them into their fields into dictionary object
def set_document_fields(medline_citation):
    document = {}
    log.print_debug(TAG, "Ricerca dei campi nel documento iniziata.")
    pmid = list(medline_citation.findall("PMID"))
    if len(pmid) > 0:
        document['pmid'] = pmid[0].text
        print(document['pmid'])
    article = list(medline_citation.iter('Article'))
    if len(article) > 0:
        article = article[0]
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
                        month = int(month_to_int(pub_date_month[0].text))
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
                document['author_first_name_' + str(i)] = first_name[0].text
            last_name = list(author.iter('LastName'))
            if len(last_name) > 0:
                document['author_last_name_' + str(i)] = last_name[0].text
            middle_name = list(author.iter('MiddleName'))
            if len(middle_name) > 0:
                document['author_first_name_' + str(i)] = first_name[0].text
            suffix = list(author.iter('Suffix'))
            if len(suffix) > 0:
                document['author_suffix_' + str(i)] = suffix[0].text
            collective_name = list(author.iter('CollectiveName'))
            if len(collective_name) > 0:
                document['author_collective_name_' + str(i)] = collective_name[0].text
            affiliation = list(author.iter('Affiliation'))
            if len(affiliation) > 0:
                document['author_affiliation_' + str(i)] = affiliation[0].text
            i = i + 1
        i = 1
        for group in article.iter('Group'):
            document['group_name_' + str(i)] = group.find('GroupName').text
            k = 0
            for group_component in group.iter('IndividualName'):
                group_component_first_name = list(group_component.iter('FirstName'))
                if len(group_component_first_name) > 0:
                    key = 'group_name_' + str(i) + '_group_component_first_name_' + str(k)
                    document[key] = group_component_first_name[0].text
                group_component_last_name = list(group_component.iter('LastName'))
                if len(group_component_last_name) > 0:
                    key = 'group_name_' + str(i) + '_group_component_last_name_' + str(k)
                    document[key] = group_component_last_name[0].text
                group_component_middle_name = list(group_component.iter('MiddleName'))
                if len(group_component_middle_name) > 0:
                    key = 'group_name_' + str(i) + '_group_component_middle_name_' + str(k)
                    document[key] = group_component_middle_name[0].text
                group_component_suffix = list(group_component.iter('Suffix'))
                if len(group_component_suffix) > 0:
                    key = 'group_name_' + str(i) + '_group_component_suffix_' + str(k)
                    document[key] = group_component_suffix[0].text
                k = k + 1
            i = i + 1
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
                            month = int(month_to_int(pub_date_month[0].text))
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
        copyright_element = list(article.iter('CopyrightInformation'))
        if copyright_element:
            document['copyright'] = copyright_element[0].text
        coi_statment = list(article.iter('CoiStatement'))
        if coi_statment:
            document['coi_statment'] = coi_statment[0].text
        keywords = ""
        for object_element in article.iter('Object'):
            if object_element.attrib['Type'] == 'keyword':
                keywords = keywords + object_element.findall('Param')[0].text + ","
        if keywords != "":
            keywords = keywords[:-1]
            document['keywords'] = keywords
    log.print_debug(TAG, "Ricerca dei campi nel documento iniziata.")
    return document


# Removes files in a list from the filesystem
def remove_files(files):
    for file in files:
        os.remove(file)


# Cleans xml string and adds to it a root element to work properly
def clean_xml(xml):
    xml = re.sub(r'<.*?MedlineCitationSet?[^>]+>', '', xml)
    xml = "<root>" + xml + "</root>"
    return xml


# Converts a string consisting of three characters into its integer value
def month_to_int(month):
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
