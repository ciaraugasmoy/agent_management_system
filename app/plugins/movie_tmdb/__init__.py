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
        # More accurate token calculation mimicking OpenAI's approach
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
            response, tokens_used = self.interact_with_ai(user_input, ACTOR_PROMPT)
            logging.info(f"response before encoding. {response}")
            total_tokens_used += tokens_used
            if response != 'none':
                query = urllib.parse.quote(response.encode('utf-8'))
                act_url= f'https://api.themoviedb.org/3/search/person?query={query}&include_adult=false&language=en-US&page=1'
                print(f'actor url query{act_url}')
                actor_list=self.callAPI(act_url)
                actor_name = actor_list['results'][0]['name']
                logging.info(f"Actor name: {actor_name}")
                actor_id = str(actor_list['results'][0]['id'])
                param = 'with_people=' + urllib.parse.quote(actor_id.encode('utf-8'))
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
                query=urllib.parse.quote("tom hanks")
                call=self.callAPI(f'https://api.themoviedb.org/3/search/person?query={query}&include_adult=false&language=en-US&page=1')
                print (call['results'][0]['name'])
            response, total_tokens_used = self.process_message(user_input)
            print(f"URL: {response}")
            print(self.callAPI(response))

            print(f"(This interaction used {total_tokens_used} tokens.)")
