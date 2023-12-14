# What's your FTA?
## Recommendation and Chatbot service for FTA related contents

#### Team 15 (하정욱, 김진석, 이호원)
We aim to build conversational AI(+recommendation system) in the specialized domain of FTA.<br>
To do so, we constructed FTA related dataset from the scratch. Also, we leveraged the power of Retrieval system to build our model.

## Environmental Setting
- **requirements.txt:** environment of Python 3.10 & required packages

## Running the application

### Prepare OPENAI_API_KEY
- put your own api key in .env file.

### Prepare Dataset
- Download news and agreements dataset from [HERE](https://drive.google.com/drive/u/0/folders/1xHb17qcSF0sevaFwKW5HLhkbvRcnpccg) and place it inside 
Application/data/. <br/>

### Run the app
- `python -m streamlit ./Application/app.py` to run the app.