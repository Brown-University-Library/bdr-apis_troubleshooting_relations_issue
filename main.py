import logging
from dotenv import load_dotenv, find_dotenv

load_dotenv( find_dotenv(raise_error_if_not_found=True) )


def run_manager():
    print('Running manager')


    pid = ''
    print(f"DEBUG [test_access_denied_exception] Starting test for PID: {pid}")
    
    # Simulate fetching data from Solr
    params = {
        'q': f'pid:"{pid}" OR rel_is_annotation_of_ssim:"{pid}" OR '
             'rel_is_member_of_ssim:"{pid}" OR '
             'rel_is_derivation_of_ssim:"{pid}" OR '
             'rel_is_part_of_ssim:"{pid}" OR '
             'rel_dcterms_is_version_of_ssim:"{pid}" OR '
             'rel_is_transcript_of_ssim:"{pid}" OR '
             'rel_is_translation_of_ssim:"{pid}"',
        'fl': '*',
        'wt': 'json',
        'rows': 1
    }
    print(f"DEBUG [SolrDataFetcher.get_solr_data] params, ``{params}``")
    
    # Simulated Solr response
    solr_response = {
        'response': {
            'docs': [
                {
                    'pid': '',
                    'all_ds_ids_ssim': ['MODS', 'irMetadata', 'RELS-EXT', 'rightsMetadata', 'RELS-INT'],
                    'discover': ['BDR_PUBLIC'],
                    'modify': ['BROWN:DEPARTMENT:LIBRARY:REPOSITORY'],
                    'delete': ['BROWN:DEPARTMENT:LIBRARY:REPOSITORY']
                }
            ]
        }
    }
    
    # Process the Solr data
    print(f"DEBUG [RelationsHandler.solr_data]")
    solr_data = solr_response
    
    # Extract the main item and check permissions
    print(f"DEBUG [RelationsHandler._get_main_item]")
    docs = solr_data.get('response', {}).get('docs', [])
    if not docs:
        raise AccessDeniedException('Access Denied')
    
    item = docs[0]
    
    # Simulate permission check (in this case, simply checking if 'discover' field exists)
    if 'discover' not in item:
        raise AccessDeniedException('Access Denied')
    
    # Simulate further related items processing
    print(f"DEBUG [RelationsHandler.main_item]")
    related_items = []
    for rel in ['rel_is_annotation_of_ssim', 'rel_is_member_of_ssim', 'rel_is_derivation_of_ssim',
                'rel_is_part_of_ssim', 'rel_dcterms_is_version_of_ssim', 'rel_is_transcript_of_ssim',
                'rel_is_translation_of_ssim']:
        related_params = {
            'q': f'{rel}:"{pid}"',
            'fl': '*',
            'wt': 'json',
            'rows': 1
        }
        print(f"DEBUG [SolrDataFetcher.get_solr_data] params, ``{related_params}``")
        
        # Simulated related Solr response
        related_solr_response = {
            'response': {
                'docs': [
                    {
                        'pid': f'related:{pid}',
                        'discover': ['BDR_PUBLIC']
                    }
                ]
            }
        }
        
        related_docs = related_solr_response.get('response', {}).get('docs', [])
        if related_docs:
            related_items.append(related_docs[0])
    
    # Final check to simulate the actual process
    print(f"DEBUG [RelationsHandler.main_item] related_items: {related_items}")
    if not related_items:
        raise AccessDeniedException('Access Denied')
    
    print(f"DEBUG [test_access_denied_exception] Item and related items retrieved successfully")




if __name__ == '__main__':
    run_manager()