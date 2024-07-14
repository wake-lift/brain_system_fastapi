from app.schemas.questions import SearchType


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


def get_searh_query(
        search_pattern: str,
        search_type: str,
        question_type: str = None
) -> dict:
    if search_type == SearchType.full_text_search and not question_type:
        return {
            'query': {
                'bool': {
                    'must': [
                        {'match': {'question': search_pattern}}
                    ]
                }
            }
        }
    if search_type == SearchType.full_text_search and question_type:
        return {
            'query': {
                'bool': {
                    'filter': [{
                        'term': {'question_type': question_type}
                    }],
                    'must': [
                        {'match': {'question': search_pattern}},
                    ],
                },
            },
        }
    if search_type == SearchType.fuzzy_search and not question_type:
        return {
            'query': {
                'match': {
                    'question': {
                        'query': search_pattern,
                        'fuzziness': 'auto',
                    },
                },
            },
        }
    if search_type == SearchType.fuzzy_search and question_type:
        return {
            'query': {
                'bool': {
                    'filter': [{
                        'term': {'question_type': question_type}
                    }],
                    'must': {
                        'match': {
                            'question': {
                                'query': search_pattern,
                                'fuzziness': 'auto'
                            }
                        }
                    }
                }
            }
        }
