QUESTION_INDEX_MAPPING: dict = {
    'properties': {
        'pk': {
            'type': 'integer',
        },
        'question_type': {
            'type': 'keyword',
        },
        'question': {
            'type': 'text',
        },
    },
}

QUESTION_INDEX_SETTINGS: dict = {
    'analysis': {
        'filter': {
            'russian_stop': {
                'type': 'stop',
                'stopwords': '_russian_',
            },
            'russian_stemmer': {
                'type': 'stemmer',
                'language': 'russian',
            },
        },
        'analyzer': {
            'ru': {
                'tokenizer': 'standard',
                'filter': ['lowercase', 'russian_stop', 'russian_stemmer'],
            },
        },
    },
}

GET_ALL_DOCS_IN_INDEX: dict = {
    'query': {
        'match_all': {}
    }
}
