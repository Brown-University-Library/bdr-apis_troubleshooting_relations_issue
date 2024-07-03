"""
This script is intened to reproduce an error with one of the Hall-Hoag organization-items.
That item appears as a non-public iem, despite it's permissions being set correctly.
We believe the issue has to do with preparing the data for the item's relations -- which we think
    causes an Exception that _appears_ as an AccessDenied exception.
This script isn't yet working, because it doesn't fail as expected -- and thus must not be accurately 
    reproducting the flow of solr calls that the actual code does. 

Usage:
- review the associated dot-env file.
- $ source ../env/bin/activate
- $ python main.py
"""

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

def prep_call_a_params() -> dict:
    """ Prepares the params for the initial solr-call. """
    params = {
        'fl': '*',
        'fq': 'display:("BDR_PUBLIC")',
        'q': f'pid:"{PID}" OR rel_is_annotation_of_ssim:"{PID}" OR '
            f'rel_is_member_of_ssim:"{PID}" OR '
            f'rel_is_derivation_of_ssim:"{PID}" OR '
            f'rel_is_part_of_ssim:"{PID}" OR '
            f'rel_dcterms_is_version_of_ssim:"{PID}" OR '
            f'rel_is_transcript_of_ssim:"{PID}" OR '
            f'rel_is_translation_of_ssim:"{PID}"',
        'rows': 5000,
        'sort': 'pid asc',
        'wt': 'json'
        }
    return params


def call_solr( params: dict ) -> dict:
    """ Calls solr with params. 
        Returns full solr-response, unlike the actual call_solr() function, at bottom for reference. """
    url = f'{SOLR_ROOT}select/'
    try:
        r = requests.post (url, data=params, timeout=SOLR_TIMEOUT_SECONDS )
        if r.ok:
            data = json.loads(r.text)
            if len( repr(data) ) > 5000:
                log.debug( f'PARTIAL solr-data, ``{pprint.pformat(data)[0:5000]}...``' )
            else:
                log.debug( f'FULL solr-data, ``{pprint.pformat(data)}``' )
            return data
            #make sure we got a hit
            # if data['response']['docs']:
            #     return data['response']['docs']
            # return []
        else:
            raise Exception(f'solr error: {r.status_code} - {r.text}')
    except requests.exceptions.Timeout:
        raise Exception('solr timeout')
    except requests.exceptions.ConnectionError:
        raise Exception('solr connection error')
    

def modify_solr_rsp( call_a_rsp: dict ) -> list:
    """ Modifies the full solr-response from call_solr() into a list of solr-docs. """
    return_data = []
    data = call_a_rsp
    if data['response']['docs']:
        return_data = data['response']['docs']
    else:
        log.debug( 'no docs found' )
    return return_data


def analyze_call_a_rsp( full_call_a_rsp: dict ) -> None:
    """ Logs keys from the full solr-response. """
    top_keys: list = list( full_call_a_rsp.keys() )  # ``['responseHeader', 'response']``
    log.debug( f'top_keys, ``{top_keys}``' )
    responseHeader_keys: list = list( full_call_a_rsp['responseHeader'].keys() )  # ``['status', 'QTime', 'params']``
    log.debug( f'responseHeader_keys, ``{responseHeader_keys}``' )  
    response_keys: list = list( full_call_a_rsp['response'].keys() )  # ``['numFound', 'start', 'docs']``
    log.debug( f'response_keys, ``{response_keys}``' )
    log.debug( f'numFound, ``{full_call_a_rsp["response"]["numFound"]}``' )
    return

def step_2_define_related_item_keys() -> list:
    """ Defines the keys to use to find related items. """
    related_item_keys = [
        'rel_dcterms_is_version_of_ssim', 
        'rel_is_annotation_of_ssim', 
        'rel_is_derivation_of_ssim',                
        'rel_is_member_of_ssim', 
        'rel_is_part_of_ssim', 
        'rel_is_transcript_of_ssim',
        'rel_is_translation_of_ssim'
        ]
    return related_item_keys


def step_2_make_related_params( rel: str ) -> dict:
    """ Makes the related-params. """
    related_params = {
        'q': f'{rel}:"{PID}"',
        'fl': '*',
        'wt': 'json',
        'rows': 1
        }
    log.debug( f"related_params, ``{related_params}``" )
    return related_params

## manager ----------------------------------------------------------

def run_manager():
    log.info( '\n\nstarting run_manager()' )
    log.debug( f'PID, ``{PID}``' )
    ## initial solr call --------------------------------------------
    """
    Result of SolrDataFetcher.get_solr_data(), just after
    `params = self._build_item_solr_params(self.pid, self.identities)`
    This first query seems to get anything related to the target-PID -- one resulting entry is the target-PID doc itself.
    """
    call_a_params = prep_call_a_params()
    full_call_a_rsp: dict = call_solr( call_a_params )
    analyze_call_a_rsp( full_call_a_rsp )
    modified_call_a_docs: list = modify_solr_rsp( full_call_a_rsp )  # returns a list of solr-docs

    ## grab first item -----------------------------------------------
    item: dict = modified_call_a_docs[0]
    log.debug( f'item, ``{pprint.pformat(item)}``' )
    # log.debug( f'just out of curiosity, item-2, ``{pprint.pformat(modified_call_a_docs[1])}``' )

    ## assert there is a `discover` key -----------------------------
    assert 'discover' in item, 'Access Denied'

    ## access related items -----------------------------------------
    related_items: list = []
    related_item_keys: list = step_2_define_related_item_keys()
    for rel in related_item_keys:
        related_params: dict = step_2_make_related_params( rel )
        related_solr_response = call_solr( related_params )
        related_docs: list = modify_solr_rsp( related_solr_response )
        if related_docs:
            related_item: dict = related_docs[0]
            log.debug( f"related_item found for rel, ``{rel}`` -- ``{pprint.pformat(related_item)}``" )
            related_items.append( related_item )
        else:
            log.debug( f"no related_docs found for rel, ``{rel}``" )
    log.debug( f'count of related_items, ``{len(related_items)}``' )
    # log.debug( f'related_items, ``{pprint.pformat(related_items)}``' )


    sys.exit( 'done' )



if __name__ == '__main__':
    run_manager()


## for reference ----------------------------------------------------

## actual call_solr() function -- which returns doc-list only
# def call_solr_a( params: dict ) -> list:
#     """ Calls solr with params. 
#         Returns a list of solr docs. """
#     url = f'{SOLR_ROOT}select/'
#     try:
#         r = requests.post (url, data=params, timeout=SOLR_TIMEOUT_SECONDS )
#         if r.ok:
#             data = json.loads(r.text)
#             log.debug( """The solr-response follows, but note that only the `docs` list is actually returned. 
# Am showing the full-solr-response here for the params, which'll be shown at the bottom
# in the `responseHeader` key. """ )
#             log.debug( f'PARTIAL solr-data, ``{pprint.pformat(data)[0:5000]}...``' )
#             #make sure we got a hit
#             if data['response']['docs']:
#                 return data['response']['docs']
#             return []
#         else:
#             raise Exception(f'solr error: {r.status_code} - {r.text}')
#     except requests.exceptions.Timeout:
#         raise Exception('solr timeout')
#     except requests.exceptions.ConnectionError:
#         raise Exception('solr connection error')
