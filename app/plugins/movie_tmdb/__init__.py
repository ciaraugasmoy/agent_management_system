import os
import logging
import requests
import urllib.parse
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.commands import Command

class MovieTMDB(Command):
    def __init__(self):
        super().__init__()
        self.name = "movies_tmdb"
        self.description = "Interact with a Movie Expert AI to explore movie preferences."
        load_dotenv()
        API_KEY = os.getenv('OPEN_AI_KEY')
        self.llm = ChatOpenAI(openai_api_key=API_KEY)  # Initialize once and reuse


    def calculate_tokens(self, text):
        return len(text) + text.count(' ')

    def interact_with_ai(self, user_input, prompt_text):
        # Generate a more conversational and focused prompt
        prompt = ChatPromptTemplate.from_messages([("system", prompt_text)]+[("user", user_input)])
        output_parser = StrOutputParser()
        chain = prompt | self.llm | output_parser
        response = chain.invoke({"input": user_input})
        # Token usage logging and adjustment for more accurate counting
        tokens_used = self.calculate_tokens(prompt_text + user_input + response)
        logging.info(f"OpenAI API call made. Tokens used: {tokens_used}")
        return response, tokens_used

    def find_id_param(self, type, query):
        '''Takes type and query to find ids of movies, people and keywords'''
        try:
            query = urllib.parse.quote(query.encode('utf-8'))
            query_url = f'https://api.themoviedb.org/3/search/{type}?query={query}&include_adult=false&language=en-US&page=1'
            logging.info(f"response before encoding. {query_url}")
            result = self.callAPI(query_url)
            id = str(result['results'][0]['id'])
            return id
        except Exception as e:
            print("Sorry, there was an error processing your request. Please try again.")
            logging.error(f"Error during interaction: {e}")
            return None


    def process_message(self, user_input):
        DISCOVER_URL = os.getenv('DISCOVER_URL')
        GENRE_PROMPT = os.getenv('GENRE_PROMPT')
        ACTOR_PROMPT = os.getenv('ACTOR_PROMPT')
        prompts = [GENRE_PROMPT]
        params = []
        total_tokens_used = 0

        try:
            response, tokens_used = self.interact_with_ai(user_input, GENRE_PROMPT)
            logging.info(f"response before encoding. {response}")
            param='with_genres='+urllib.parse.quote(response)
            params.append(param)
            total_tokens_used += tokens_used
        except Exception as e:
            print("Sorry, there was an error processing your request. Please try again.")
            logging.error(f"Error during interaction: {e}")

        try:
            query, tokens_used = self.interact_with_ai(user_input, ACTOR_PROMPT)
            logging.info(f"response before encoding. {response}")
            total_tokens_used += tokens_used
            if response != 'none':
                actor_id=self.find_id_param('person',query)#returns first id in list or false
                param = 'with_people='+actor_id
                params.append(param)
        except Exception as e:
            print("Sorry, there was an error processing your request. Please try again.")
            logging.error(f"Error during interaction: {e}")
        

        params = '&'.join(params)
        url=DISCOVER_URL+params
        return url, total_tokens_used

    def callAPI(self,url):
        BEARER_TOKEN = os.getenv('BEARER_TOKEN')
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {BEARER_TOKEN}"
        }
        response = requests.get(url, headers=headers)
        logging.info(f"tmdb API call made.")
        return response.json()
    
    def execute(self, *args, **kwargs):
        print(f"get tmdb suggestions, enter done to leave")

        while True:
            user_input = input("You: ").strip()
            if user_input.lower() == "done":
                print("Thank you Goodbye!")
                break
            if user_input.lower() == "api":
                print(self.find_id_param('person','tom hanks'))
                break
            response, total_tokens_used = self.process_message(user_input)
            print(f"URL: {response}")
            # print(self.callAPI(response))

            print(f"(This interaction used {total_tokens_used} tokens.)")
