# 1. overview of the api :

## resumé de l'api : 
api permetant la gestion de projet ,l'ajout d'issue a un projet ,de commentaire a une issue ,ainsi que de definir quelle issue sont assigné a quelle utilisateur

## avantage de l'api :
ORM gèrent completement chacune des interaction avec la base de donné ce qui permet une gestion simplifié ,chaque model dispose de son/ses propre(s) serializer ainsi l'Api dispose d'une forme de modularité pour s'integrer au mieu avec les client 
er la documentation approprié postman

# 2. tutorial

how to install the application
  1. first you need to clone the repository in the desired location
    ```git clone https://github.com/toutouff/P10_DRF```
  2. after you have to create the virtual environement 
    ```python3 -venv NameOfTheEnvironement```
  3. then install required package
    ```pip intall -r requirements.txt```


how to use the application 
  1. to run it just run the manage.py file with the runserver argument then precise on what IP and PORT you wanna run it (default = 127.0.0.1:8000) 
    ```python3 manage.py runserver```
  2. then you can access different endpoint by passing certain data to the body of the request the following documentation regroup every endpoint,with detail on required data

# 3. exemple 
  to find exemple of request and documentation on the different endpoint go see the postman documentation 
  https://documenter.getpostman.com/view/25555539/2s93RTRYXj

# 4. glossary


