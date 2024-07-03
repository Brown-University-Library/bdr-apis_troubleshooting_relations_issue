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
