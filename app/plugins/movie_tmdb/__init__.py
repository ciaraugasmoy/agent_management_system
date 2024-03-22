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
        BEARER_TOKEN = os.getenv('BEARER_TOKEN')
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
        GENRE_PROMPT = os.getenv('GENRE_PROMPT')
        ACTOR_PROMPT = os.getenv('ACTOR_PROMPT')
        prompts = [GENRE_PROMPT, ACTOR_PROMPT]
        responses = []
        total_tokens_used = 0
        for prompt in prompts:
            try:
                response, tokens_used = self.interact_with_ai(user_input, prompt)
                responses.append(response)
                total_tokens_used += tokens_used
            except Exception as e:
                print("Sorry, there was an error processing your request. Please try again.")
                logging.error(f"Error during interaction: {e}")

        combined_response = '&'.urllib.parse.quote(join(responses))
        return combined_response, total_tokens_used

    def callAPI(self,url,url_append):
        url = "https://api.themoviedb.org/3/discover/movie?include_adult=false&include_video=false&language=en-US&page=1&sort_by=popularity.desc"+url_append
        headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {BEARER_TOKEN}"
        }
        response = requests.get(url, headers=headers)
        print(response.text)
    
    def execute(self, *args, **kwargs):
        print(f"get tmdb suggestions, enter done to leave")

        while True:
            user_input = input("You: ").strip()
            if user_input.lower() == "done":
                print("Thank you Goodbye!")
                break

            response, total_tokens_used = self.process_message(user_input)
            print(f"URL: {response}")
            print(f"(This interaction used {total_tokens_used} tokens.)")
