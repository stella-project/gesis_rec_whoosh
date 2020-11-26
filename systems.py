import jsonlines
import os.path
from whoosh.fields import Schema, ID, TEXT
from whoosh.qparser import QueryParser, syntax
from whoosh.index import open_dir, create_in


class Ranker(object):

    def __init__(self):
        self.idx = None

    def index(self):
        pass

    def rank_publications(self, query, page, rpp):

        itemlist = []

        return {
            'page': page,
            'rpp': rpp,
            'query': query,
            'itemlist': itemlist,
            'num_found': len(itemlist)
        }


class Recommender(object):

    def __init__(self):
        self.idx = None
        self.title_lookup = {}

    def index(self):
        schema = Schema(title=TEXT(stored=True),
                        content=TEXT,
                        identifier=ID(stored=True))

        if not os.path.exists("index"):
            os.mkdir("index")
        self.idx = create_in("index", schema)

        writer = self.idx.writer()

        with jsonlines.open('./data/gesis-search/datasets/dataset.jsonl') as reader:
            for obj in reader:
                title = obj.get('title') or ''
                title = title[0] if type(title) is list else title
                abstract = obj.get('abstract') or ''
                abstract = abstract[0] if type(abstract) is list else abstract
                writer.add_document(title=title,
                                    content=abstract,
                                    identifier=obj.get('id'))
        writer.commit()

        with jsonlines.open('./data/gesis-search/documents/publication.jsonl') as reader:
            for obj in reader:
                self.title_lookup[obj.get('id')] = obj.get('title')

    def recommend_datasets(self, item_id, page, rpp):

        itemlist = []

        if len(self.title_lookup) == 0:
            with jsonlines.open('./data/gesis-search/documents/publication.jsonl') as reader:
                for obj in reader:
                    self.title_lookup[obj.get('id')] = obj.get('title')

        doc_title = self.title_lookup.get(item_id)

        if doc_title:
            if self.idx is None:
                try:
                    self.idx = open_dir('index')
                except Exception as e:
                    pass

            # results = []
            # searcher = self.idx.searcher()
            # for term in doc_title.split():
            #
            #     query = QueryParser("content", self.idx.schema,).parse(term)
            #     term_results = searcher.search(query)
            #     for tr in list(term_results):
            #         results.append(tr)
            #
            # result_dict = {res.get('identifier'): res.score for res in results}
            # sort_res = sorted(result_dict.items(), key=lambda x: x[1], reverse=True)
            # itemlist = [item[0] for item in sort_res[page*rpp:(page+1)*rpp]]

            searcher = self.idx.searcher()
            query = QueryParser("content", self.idx.schema, group=syntax.OrGroup).parse(doc_title)
            results = searcher.search(query, limit=(page+1)*rpp)
            itemlist = [res.get('identifier') for res in results[page*rpp:(page+1)*rpp]]

            searcher.close()

        return {
            'page': page,
            'rpp': rpp,
            'item_id': item_id,
            'itemlist': itemlist,
            'num_found': len(itemlist)
        }

    def recommend_publications(self, item_id, page, rpp):

        itemlist = []

        return {
            'page': page,
            'rpp': rpp,
            'item_id': item_id,
            'itemlist': itemlist,
            'num_found': len(itemlist)
        }
