> Note: This project uses an API key that is not included in the repository. If you want to use this project, please visit the website at [Reddi-Senti](https://reddi-senti.onrender.com/) instead of cloning the repository.

- - -

# Reddi-Senti    *Analyze sentiment on Reddit*
"Reddi-Senti" is a Flask web application that allows users to analyze the sentiment of keywords searched on Reddit, the popular social news aggregation and discussion website. With "Reddi-Senti," users can compare the sentiment of multiple keywords and view visualized graphs comparing the results of sentiment analysis for each keyword.
    
![result_graph](result_graph.png)

## Prerequisites
- Python 3.6 or later
- PostgreSQL


## Built with
- Flask - Python web framework
- Bootstrap - Front-end framework
- TextBlob - Python library that can be used to process textual data. 
  It provides a simple API for diving into common natural language processing (NLP) tasks such as part-of-speech tagging, noun phrase extraction, sentiment analysis, classification, translation, and more
- MatPlotLib -A plotting library for the Python programming language and its numerical mathematics extension NumPy
- wtform - Forms validation and rendering library for Python web development
- PostgreSQL - Database management system
- SQLalchemy - Communicate with database using Python

## API Used

- This project utilizes [reddit api](https://www.reddit.com/dev/api/)
- Endpoint  
    `/search.json  `
for reddit search and retrieve posts and comments related to the search term.
## Features
- Add Keyword : Users can add multiple keywords at a time
- Analyze machine : Analyze sentiment score for each keyword
- Result : Users can see analyzed results with visualized score graphs
- Dashboard : For a registered user to see saved results and delete them
- Demo analysis: Let user analyze keywords and see comparison graphs to try the app out without a log in
- User Profile: Users can edit own info and delete registered account



## Installing
### Clone the repository to your local machine using the command  
    git clone https://github.com/username/reddi-senti.git
### Navigate to the project directory.
### Create a virtual environment using   
    python3 -m venv venv
### Activate the virtual environment using  
    
    source venv/bin/activate
### Install the required Python packages using  
    
    pip3 install -r requirements.txt
### Create a PostgreSQL database for the project.
    createdb reddi-senti
### Run the application
    flask run

### Usage
Once you have the project up and running, you can navigate to http://localhost:5000/ to use the application. Push `Try it!` button and you will be redirected to a page that shows a form to add keyword and `Analyze` button to analyze the sentiment of keywords on reddit. You can create a new account with `Register` button or `Log in` with an existing one. After you log in, you can save your analysis cards and view them on your user dashboard.




## Author
[Pasinee Sombun](https://www.linkedin.com/in/pasinee-sb/)
