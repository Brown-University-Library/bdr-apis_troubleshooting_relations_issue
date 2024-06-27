import json, logging, os, pprint, sys
import requests
from dotenv import load_dotenv, find_dotenv

load_dotenv( find_dotenv(raise_error_if_not_found=True) )

lglvl: str = os.environ.get( 'LOGLEVEL', 'DEBUG' )
lglvldct = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO }
logging.basicConfig(
    level=lglvldct[lglvl],  # assigns the level-object to the level-key loaded from the envar
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger( __name__ )

PID = os.environ[ 'TARGET_PID' ]
SOLR_ROOT = os.environ[ 'SOLR_ROOT' ]

SOLR_TIMEOUT_SECONDS = 10


## helpers ----------------------------------------------------------

def call_solr( params: dict ) -> list:
    """ Calls solr with params. 
        Returns a list of solr docs. """
    url = f'{SOLR_ROOT}select/'
    try:
        r = requests.post (url, data=params, timeout=SOLR_TIMEOUT_SECONDS )
        if r.ok:
            data = json.loads(r.text)
            log.debug( f'data, ``{pprint.pformat(data)}``' )
            #make sure we got a hit
            if data['response']['docs']:
                return data['response']['docs']
            return []
        else:
            raise Exception(f'solr error: {r.status_code} - {r.text}')
    except requests.exceptions.Timeout:
        raise Exception('solr timeout')
    except requests.exceptions.ConnectionError:
        raise Exception('solr connection error')


## manager ----------------------------------------------------------

def run_manager():
    log.info( '\n\nstarting run_manager()' )
    log.debug( f'PID, ``{PID}``' )
    ## initial solr call --------------------------------------------
    params = {
        'q': f'pid:"{PID}" OR rel_is_annotation_of_ssim:"{PID}" OR '
             'rel_is_member_of_ssim:"{PID}" OR '
             'rel_is_derivation_of_ssim:"{PID}" OR '
             'rel_is_part_of_ssim:"{PID}" OR '
             'rel_dcterms_is_version_of_ssim:"{PID}" OR '
             'rel_is_transcript_of_ssim:"{PID}" OR '
             'rel_is_translation_of_ssim:"{PID}"',
        'fl': '*',
        'wt': 'json',
        'rows': 1
    }
    rsp = call_solr( params )
    

    sys.exit( 'done' )

    # Process the Solr data
    print(f"DEBUG [RelationsHandler.solr_data]")
    solr_data = solr_response
    
    # Extract the main item and check permissions
    print(f"DEBUG [RelationsHandler._get_main_item]")
    docs = solr_data.get('response', {}).get('docs', [])
    if not docs:
        raise Exception('Access Denied')
    
    item = docs[0]
    
    # Simulate permission check (in this case, simply checking if 'discover' field exists)
    if 'discover' not in item:
        raise Exception('Access Denied')
    
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
        raise Exception('Access Denied')
    
    print(f"DEBUG [test_access_denied_exception] Item and related items retrieved successfully")




if __name__ == '__main__':
    run_manager()