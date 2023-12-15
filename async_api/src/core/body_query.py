person_search = '''{{
    "from": {page_from},
    "size": {page_size},
    "query": {{
        "match": {{
            "full_name": {{
                "query": "{query}",
                "fuzziness": "auto"
            }}
        }}
    }}
}}'''

genres = ''' {{    
    "from": {page_from},
    "size": {page_size} 
    }} '''
