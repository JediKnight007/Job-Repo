from parse_utils import parse

class QuerySlow:
    matching_titles = []  # the titles of docs with the search term
    search_term = ''      # the search term 
    wikifile = ''         # the name of the wikifile being searched

    def __init__(self, wikifile: str):
        self.wikifile = wikifile


    def process_page(self, wiki_page:str) -> None:
        """
        reads one wiki/xml file and builds a list of all page titles for
        which self.search_term is in the title or text of that page
        
        Parameters:
        wiki_page -- the path to an xml file with (multiple) pages  
                     (each with title, id, and text sections)
        """
        # extract the id, title, and text from the xml page
        page_id = int(wiki_page.find("id").text)
        page_title = wiki_page.find("title").text.strip()
        page_text = wiki_page.find("text").text.strip()
        # if the page had no text area, set page_text to an empty string
        if wiki_page.find("text").text is None: page_text = ""
        
        # add the page title to the list of matches if the search text
        #  is in either the page title or the page text
        if (self.search_term in page_title) or (self.search_term in page_text):
            self.matching_titles.append(page_title)


    def query(self, search_term: str) -> list:
        """
        searches for page titles that contain the search term

        Parameters:
        search_term -- the string to search for in wiki pages; for this
                       assignment these can be just single words
        
        Returns:
        the list of titles of pages that contain the search term
        """
        self.matching_titles = []
        self.search_term = search_term
        parse(self.wikifile, self.process_page)
        return self.matching_titles


# this is a sample of how we might run/test this system
def sample_run():
    qs1 = QuerySlow('../wikis/Example1.xml')

    # "A" is a stop word so it won't yield any results
    assert(qs1.query("A")==[])

    # "G" is the title of page 1/G and the link text of page 3/C
    result = qs1.query("G")
    assert("G" in result)
    # query_slow does not parse links, so C would show up in the result
    # even though "G" is a link URL, not link text.
    # in your implementation of query_several, pages that only contain
    # search terms in link TITLES/URLs should NOT appear.
    # assert("C" not in result)
    assert(result.__len__() == 2)

    # "Z" isn't in the document 
    print(qs1.query("Z"))
    assert(qs1.query("Z")==[])
    

# uncomment the next line to have the sample run automatically when you run the file
sample_run()