cpsportlets_content_search_voc_vocabulary = {
    'data': {
        'tuples': (
            ('related', 'Related', 'cpsportlets_content_search_related_label'),
            ('pending', 'Pending', 'cpsportlets_content_search_pending_label'),
            ('last_modified', 'Last modified', 'cpsportlets_content_search_last_modified_label'),
            ('recent', 'Recent', 'cpsportlets_content_search_recent_label'),
            ('upcoming', 'Upcoming', 'cpsportlets_content_search_upcoming_label'),
        ),
    },
}

cpsportlets_content_sort_on_voc_vocabulary = {
    'data': {
        'tuples': (
            ('Title', 'Title', 'cpsportlets_content_sort_on_Title_label'),
            ('Date', 'Date', 'cpsportlets_content_sort_on_Date_label'),
            ('review_state', 'Review state', 'cpsportlets_content_sort_on_review_state_label'),
            ('Creator', 'Creator', 'cpsportlets_content_sort_on_Creator_label'),
        ),
    },
}

cpsportlets_content_portal_types_vocabulary = {
    'type': 'CPS Method Vocabulary',
    'data': {
        'get_vocabulary_method': 'getSearchableTypesVocabulary',
            }
    }

vocabularies = {'cpsportlets_content_search_voc': cpsportlets_content_search_voc_vocabulary,
                'cpsportlets_content_sort_on_voc': cpsportlets_content_sort_on_voc_vocabulary,
                'cpsportlets_content_portal_types_voc': cpsportlets_content_portal_types_vocabulary,
               }

return vocabularies
