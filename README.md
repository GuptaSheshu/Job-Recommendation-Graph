# Job Recommendation System

## Getting Started
This github repository contains an interactive API's for recommending job opening based on filters and keyword. A databse of 430 jobs are created by scrapping the data from multiple sources, specifically from amazon and glassdoor. The useful information about the jobs are dumped in a JSON file, and can be used directly rather than calling APIs everytime. 

### Setup
Dependencies :-
- BeautifulSoup
- requests
- pandas
- numpy 
- selenium
- webdriver_manager
- contextlib
- flask

Installation of all this library can be done by running ``pip install -r requirement.txt`` in the appropriate terminal.

## File distribution
This repository contains following files :-
1. ``amazon_data_scrapping.py`` Python file to scrap data from *jobs.amazon* website, it extract useful information about the job such as 1) Job title, 2) Company Name, 3) Job URL, 4) Job Location, 5) Job description.
2. ``glassdoor_data_scrapping.py`` Python file to scrap data from *glassdoor* website, it extract same attribute as the above file *amazon_data_scrapping* file does.
3. ``config.py`` Python file contains all the essential function such as loading/saving of cache, a class wrapping the job information, and supporting function for graph nodes connections.
4. ``graph.py`` A class representation of graph.
5. ``main.py`` Main file which create the graph, make connection, and recommend based on the user input. For better interaction flask is initialized and use it for better interaction.
6. ``template/index.html`` A HTML script for flask.

## Execution
Simply run the *main.py* file using ``python main.py`` in an appropriate terminal. Then the terminal will pop up a local URL, which can be used to interact with python script on web browser. The web browser will let user decide on what kind of job they are looking for, based on the query, the python script will generate suggestion satisfying the user requirements. The user will be able to see general information about the Jobs such as title, location, company name, and URL which user can click to divert the page to the company website where they can apply directly. 

