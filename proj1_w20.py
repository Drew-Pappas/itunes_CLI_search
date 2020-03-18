#########################################
##### Name: Drew Pappas             #####
##### Uniqname: drewpap             #####
#########################################

import requests, copy, webbrowser

class Media:

    def __init__(self, title="No Title", author="No Author", release_year = "No Release Year", url = "No URL", json = None): #Shorten?
        
        if json != None:
            self.json = json 
            
            if "trackName" in self.json.keys(): #Check to see if the JSON has a trackname, if it does use that
                self.title = self.json["trackName"]
            else: #If it does not, use the collection name instead
                self.title = self.json["collectionName"]

            self.author = self.json["artistName"]
            self.release_year = self.json["releaseDate"][:4]

            if "trackViewUrl" in self.json.keys():
                self.url = self.json["trackViewUrl"]
            else:
                self.url = self.json["collectionViewUrl"] 

        else:
            self.title = title
            self.author = author
            self.release_year = release_year
            self.url = url
    

    def info(self):
        '''Collects information about the current instance of the class and
            returns that information in a neatly printed string.

        Parameters
        ----------
        none

        Returns
        -------
        str
            a formatted string containing the instance title, author, and release year
        '''

        return f"{self.title} by {self.author} ({self.release_year})"


    def length(self):
        '''Returns the default length of a media object that has not been specified yet.

        Parameters
        ----------
        none

        Returns
        -------
        int
            the value of zero
        '''

        return 0


# Other classes, functions, etc. should go here

class Song(Media):

    def __init__(self, title='No Title', author='No Author', release_year='No Release Year', url='No URL', album = "No Album", genre = "No Genre", track_length = 0, json = None):
        
        super().__init__(title=title,author=author, release_year=release_year, url=url, json = json)
        
        if json != None:
            self.album = self.json["collectionName"]
            self.genre = self.json["primaryGenreName"]
            self.track_length = self.json["trackTimeMillis"] 
        else:
            self.album = album
            self.genre = genre
            self.track_length = track_length


    def info(self):
        '''Returns the superclass info and the song genre in a nicely printed string.

        Parameters
        ----------
        none

        Returns
        -------
        str
            the combination of information from the superclass and the genre of the instance
        '''

        return f"{super().info()} [{self.genre}]"


    def length(self):
        '''Takes the current song instance's track time in milliseconds and returns
        the time converted from milliseconds into seconds.

        Parameters
        ----------
        none

        Returns
        -------
        int
            the length of the track in seconds
        '''

        return int(self.track_length / 1000)


class Movie(Media):

    def __init__(self, title='No Title', author='No Author', release_year='No Release Year', url='No URL', rating = "No Rating", movie_length = 0, json = None):
        
        super().__init__(title=title, author=author, release_year=release_year, url=url, json = json)

        if json != None:
            self.rating = self.json["contentAdvisoryRating"]
            self.movie_length = self.json["trackTimeMillis"]
        else:
            self.rating = rating
            self.movie_length = movie_length


    def info(self):
        '''Returns the superclass info and the movie rating in a nicely printed string.

        Parameters
        ----------
        none

        Returns
        -------
        str
            the combination of information from the superclass and the rating of the instance
        '''
        
        return f"{super().info()} [{self.rating}]"


    def length(self):
        '''Takes the current movie instance's track time in milliseconds and returns
        the time converted from milliseconds into minutes.

        Parameters
        ----------
        none

        Returns
        -------
        int
            the length of the track in minutes
        '''

        return int(self.movie_length / 60000)


# Itunes API handling

def get_data_from_itunes(params = None):
    '''Calls the API from the endpoint and passes along parameters if there are any and 
        return the results found.

        Parameters
        ----------
        params : dict
            a dict of parameters to be utilized in the HTTP request

        Returns
        -------
        list
            a list of results found by the iTunes HTTP request
    '''

    base_url = "https://itunes.apple.com/search"
    if params != None:
        return requests.get(base_url, params).json()["results"][:-1]


def create_objects(list_of_api_results):
    '''Parses the list of api results for particular keys and converts those results
        into the appropriate objects. Those objects are then grouped and sent as a collection.

        Parameters
        ----------
        list_of_api_results : list
            a list of API results to be parsed into objects

        Returns
        -------
        dict
            a dictionary containing three groups of objects created from the list of api results passed
    '''

    object_dict = {}
    song_list = []
    movie_list = []
    media_list = []

    for json_result in list_of_api_results:
        if "kind" in json_result.keys():
            if "song" in json_result["kind"].lower():
                song_list.append(Song(json = json_result))
            elif "movie" in json_result["kind"].lower():
                movie_list.append(Movie(json = json_result))
        else:
            media_list.append(Media(json = json_result))
    
    object_dict["songs"] = song_list
    object_dict["movies"] = movie_list
    object_dict["other media"] = media_list

    return object_dict


def get_urls(dict_of_songs_movies_and_media):
    '''Parses the keys of the dictionary and extracts URLs associated with the objects from each key. Creates a new dictionary
        of those URLS indexed by a number.

        Parameters
        ----------
        dict_of_songs_movies_and_media : dict
            a dictionary containing lists of song, movie, and media objects

        Returns
        -------
        dict
            a dictionary of URLs parsed from the associated objects indexed by a number
    '''

    url_dict = {}
    copy_of_dict = copy.copy(dict_of_songs_movies_and_media)
    i = 1

    for key in copy_of_dict:
        for list_item in copy_of_dict[key]: # Iterate over all of the list items at the particular key
            url_dict[i] = list_item.url
            i+=1
    return url_dict


def print_interface(dict_of_songs_movies_and_media):
    '''Accepts a dictionary of objects with a .info() method and prints the information of those objects grouped by key

        Parameters
        ----------
        dict_of_songs_movies_and_media : dict
            a dict of objects that have a callable .info() method

        Returns
        -------
        none
    '''

    i = 1
    print()
    for key in dict_of_songs_movies_and_media:
        print(key.upper())
        if not dict_of_songs_movies_and_media[key]:
            print(f"No results found in this search")
        else:
            for list_item in dict_of_songs_movies_and_media[key]:
                print(f"{i} {list_item.info()}")
                i += 1
        print()

        
if __name__ == "__main__":
    # your control code for Part 4 (interactive search) should go here

    user_input = ""
    search_term = {}
    results_urls = None

    while True:
        if results_urls == None: # If there are no result urls, print this first
            user_input = input("Enter a search term or exit: ")
        else:
            user_input = input("Enter a number for more info, or another search term, or exit: ")


        if user_input.isnumeric() and results_urls != None and int(user_input) <= len(results_urls) and int(user_input) > 0: #Validate input to make sure numbers can match keys
            print(f"\nLaunching\n{results_urls[int(user_input)]}\nin web browser...\n")
            webbrowser.open(results_urls[int(user_input)])

        elif user_input.lower().strip() == "exit":
            print("Bye!")
            break

        else:
            search_term["term"] = user_input # Get the search term
            results = create_objects(get_data_from_itunes(search_term)) # Make objects based upon the search term
            results_urls = get_urls(results) # Get the URLS from the objects created
            print_interface(results) # Neatly print the information from the results found