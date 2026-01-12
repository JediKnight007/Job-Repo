import parse_utils

class QuerySeveral:
    word_freq_dict = {} # the dictionary of words to dict of ids to counts
    id_title_dict = {}  # the dictionary of ids to titles

    
    def __init__(self, wikifile):
        parse_utils.parse(wikifile, self.process_page)


    def process_page(self, wiki_page:str):
        """""  
        reads one wiki/xml file, processes each page, populating the
        dictionary that maps words->page_id->frequency counts
        
        parameters:
            wiki_page   the path to an xml file with pages (each with title, 
                        id, and text sections)
        """""
        
        page_id = int(wiki_page.find("id").text)
        page_title = wiki_page.find("title").text.strip()
        page_text = wiki_page.find("text").text.strip()
        if wiki_page.find("text").text is None: page_text = ""
        
        self.id_title_dict[page_id] = page_title

        tokens = parse_utils.get_tokens(page_title + " " + page_text)
        
        for word in tokens:
            if parse_utils.word_is_link(word):
                # split link into the text and the destination, but only process the text
                # TODO: Fill in!
                text, destination = parse_utils.split_link(word)
                self.text_processor(text, page_id)
                #Where are the query words being held? 
                
            else:
                # for non-links, just record its presence
                # TODO: Fill in!
                self.text_processor([word], page_id)
    
    def text_processor(self, term_list, page_ids): 
        for term in term_list:
            word_stem = parse_utils.stem_and_stop(term)
            if word_stem:
                if word_stem not in self.word_freq_dict: #word not even in dictionary
                    self.word_freq_dict[word_stem] = {} 
                if page_ids not in self.word_freq_dict[word_stem]: #Word does not appear on a given page
                    self.word_freq_dict[word_stem][page_ids] = 0
                self.word_freq_dict[word_stem][page_ids] +=1 #Increment if word is on page based on the stem and page id
    

    def query(self, search_term:str, format="title") -> list:
        """"
        searches for page titles that contain the search term

        Parameters:
        search_term -- the string to search for in wiki pages; for this
                       assignment these can be just single words

        format -- used to control whether a list of page ids or titles 
                  is returned. title is the default, but the value can
                  be set to "id" when query is called to get the page 
                  ids instead (ids might be less error-prone to check in tests)
        
        Returns:
        the list of pages that contain the search term (as per the format)
        """
        if format not in ["id", "title"]:
            raise ValueError("Invalid results format " + format)
        
        term_low = search_term.lower()
        if term_low in parse_utils.STOP_WORDS:
            print("WARNING: STOP WORD isn't indexed -- " + search_term)
            return []

        term_low = parse_utils.stem_and_stop(term_low)
        if term_low in self.word_freq_dict:
            # if the term is in the dictionary, get the list of ids and sort it
            # TODO: Fill in!
            id_list = self.word_freq_dict[term_low]
            sorted_id_list = sorted(id_list, key=lambda id: id_list[id], reverse=True)
            # If our query is for ids, just return the sorted list of ids
            if format is "id": 
                return sorted_id_list
            # If our query is for titles, convert the sorted list of ids to titles
            elif format is "title": 
                # TODO: Fill in!
                title_list = []
                for id in sorted_id_list:
                    title_list.append(self.id_title_dict[id])
                return title_list
            
        else: # term not in dictionary
            return []
        

