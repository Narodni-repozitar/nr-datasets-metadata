import idutils


def _(x):
    """Identity function for string extraction."""
    return x

def always_valid(identifier):
    """Gives every identifier as valid."""
    return True

RDM_RECORDS_IDENTIFIERS_SCHEMES ={
        "ark": {
            "label": _("ARK"),
            "validator": idutils.is_ark,
            "datacite": "ARK"
        },
        "arxiv": {
            "label": _("arXiv"),
            "validator": idutils.is_arxiv,
            "datacite": "arXiv"
        },
        "bibcode": {
            "label": _("Bibcode"),
            "validator": idutils.is_ads,
            "datacite": "bibcode"
        },
        "doi": {
            "label": _("DOI"),
            "validator": idutils.is_doi,
            "datacite": "DOI"
        },
        "ean13": {
            "label": _("EAN13"),
            "validator": idutils.is_ean13,
            "datacite": "EAN13"
        },
        "eissn": {
            "label": _("EISSN"),
            "validator": idutils.is_issn,
            "datacite": "EISSN"
        },
        "handle": {
            "label": _("Handle"),
            "validator": idutils.is_handle,
            "datacite": "Handle"
        },
        "igsn": {
            "label": _("IGSN"),
            "validator": always_valid,
            "datacite": "IGSN"
        },
        "isbn": {
            "label": _("ISBN"),
            "validator": idutils.is_isbn,
            "datacite": "ISBN"
        },
        "issn": {
            "label": _("ISSN"),
            "validator": idutils.is_issn,
            "datacite": "ISSN"
        },
        "istc": {
            "label": _("ISTC"),
            "validator": idutils.is_istc,
            "datacite": "ISTC"
        },
        "lissn": {
            "label": _("LISSN"),
            "validator": idutils.is_issn,
            "datacite": "LISSN"
        },
        "lsid": {
            "label": _("LSID"),
            "validator": idutils.is_lsid,
            "datacite": "LSID"
        },
        "pmid": {
            "label": _("PMID"),
            "validator": idutils.is_pmid,
            "datacite": "PMID"
        },
        "purl": {
            "label": _("PURL"),
            "validator": idutils.is_purl,
            "datacite": "PURL"
        },
        "upc": {
            "label": _("UPC"),
            "validator": always_valid,
            "datacite": "UPC"
        },
        "url": {
            "label": _("URL"),
            "validator": idutils.is_url,
            "datacite": "URL"
        },
        "urn": {
            "label": _("URN"),
            "validator": idutils.is_urn,
            "datacite": "URN"
        },
        "w3id": {
            "label": _("W3ID"),
            "validator": always_valid,
            "datacite": "w3id"
        },
    }