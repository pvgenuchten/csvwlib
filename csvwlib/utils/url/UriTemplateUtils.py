from rdflib import URIRef, Literal
import re
from csvwlib.utils.ATDMUtils import ATDMUtils
from csvwlib.utils.json.CommonProperties import CommonProperties


class UriTemplateUtils:

    @staticmethod
    def insert_value_rdf(url, atdm_row, col_name, domain_url):
        """ Does the same what normal 'insert_value' but
        returns rdf type: URIRef of Literal based on uri"""
        filled_url = UriTemplateUtils.insert_value(url, atdm_row, col_name, domain_url)
        return URIRef(filled_url) if filled_url.startswith('http') else Literal(filled_url)

    @staticmethod
    def expand_template(template: str, row: dict) -> str:
        """
        Expand a CSVW-style URI template with values from a row dict.
        
        Args:
            template: A template string like "http://ex.org/book#{id}"
            row: A dict mapping column names or reserved vars to values.
        
        Returns:
            The expanded string.
        """
        def replacer(match):
            var = match.group(1)
            if var in row.keys():
                return str(row[var])
            raise KeyError(f"Missing value for template variable '{var}'")

        return re.sub(r"\{([^}]+)\}", replacer, template)

    @staticmethod
    def insert_value(url, atdm_row, col_name, domain_url):
        """ Inserts value into uri template - between {...}
        If url is common property, it is returned unmodified
        Also uri is expanded with domain url if necessary """
        if CommonProperties.is_common_property(url):
            return url
        url = UriTemplateUtils.expand(url, domain_url)
        if '{' not in url:
            return url

        cols = {
            "_row": str(atdm_row.get('number','')),
            "_sourceRow": str(atdm_row.get('url','').rsplit('=').pop()),
            "_name": str(col_name)
        }

        for k, v in atdm_row['cells'].items():
            cols[k] = str(v[0])

        return UriTemplateUtils.expand_template(url, cols)

    @staticmethod
    def expand(url, domain_url):
        if url.startswith('http'):
            return url
        else:
            return domain_url + url

    @staticmethod
    def prefix(url, csv_url):
        """ :return prefix of uri template - the part before {...}"""
        if url.startswith('http'):
            key = url[url.find('{') + 1:url.find('}')]
            if key.startswith('#'):
                url = url[:url.find('#') + 1]
                return url.replace('{', '')
            else:
                return url[:url.find('{')]
        else:
            return csv_url + url[:url.find('{')]
