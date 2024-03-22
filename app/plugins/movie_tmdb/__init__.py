import os
import logging
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

    def interact_with_ai(self, user_input, character_name, prompt):
        output_parser = StrOutputParser()
        chain = prompt | self.llm | output_parser

        response = chain.invoke({"input": user_input})

        # Get the prompt text
        prompt_text = prompt.get_messages()[0][1]  # Assuming only one message in the prompt

        # Token usage logging and adjustment for more accurate counting
        tokens_used = self.calculate_tokens(prompt_text + user_input + response)
        logging.info(f"OpenAI API call made. Tokens used: {tokens_used}")
        return response, tokens_used



    def process_message(self, user_input, character_name):
        prompts = [
            ChatPromptTemplate.from_messages([("system", "you are a movie expert, recommend a movie")]),
            ChatPromptTemplate.from_messages([("system", "you are a book expert, recommend a book")]),
            ChatPromptTemplate.from_messages([("system", "you are a job expert, recommend a job")])
        ]

        responses = []
        total_tokens_used = 0

        for prompt in prompts:
            try:
                response, tokens_used = self.interact_with_ai(user_input, character_name, prompt)
                responses.append(response)
                total_tokens_used += tokens_used
            except Exception as e:
                print("Sorry, there was an error processing your request. Please try again.")
                logging.error(f"Error during interaction: {e}")

        combined_response = ' '.join(responses)
        return combined_response, total_tokens_used


    def execute(self, *args, **kwargs):
        character_name = kwargs.get("character_name", "Movie Expert")
        print(f"Welcome to the Movie Expert Chat! Give me a summary of what you want to watch and I'll give you some results. Type 'done' to exit anytime.")

        while True:
            user_input = input("You: ").strip()
            if user_input.lower() == "done":
                print("Thank you for using the Movie Expert Chat. Goodbye!")
                break

            response, total_tokens_used = self.process_message(user_input, character_name)
            print(f"Movie Expert: {response}")
            print(f"(This interaction used {total_tokens_used} tokens.)")
