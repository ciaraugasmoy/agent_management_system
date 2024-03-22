import os
import logging
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from app.commands import Command

class MovieExpertChat2(Command):
    def __init__(self):
        super().__init__()
        self.name = "movies2"
        self.description = "Interact with a Movie Expert AI to explore movie preferences."
        load_dotenv()
        API_KEY = os.getenv('OPEN_AI_KEY')
        # you can try GPT4 but it costs a lot more money than the default 3.5
        # self.llm = ChatOpenAI(openai_api_key=API_KEY, model="gpt-4-0125-preview")  # Initialize once and reuse
        self.llm = ChatOpenAI(openai_api_key=API_KEY)  # Initialize once and reuse

    def calculate_tokens(self, text):
        # More accurate token calculation mimicking OpenAI's approach
        return len(text) + text.count(' ')

    def interact_with_ai(self, user_input, character_name):
        # Generate a more conversational and focused prompt
        prompt_text = "You're a Movie Expert AI. Engage the user in a natural conversation about their movie preferences. Use your insights to recommend movies they might like."
        
        output_parser = StrOutputParser()
        chain = ChatPromptTemplate() | ChatPromptTemplate(prompt_text) | self.llm | output_parser

        response = chain.invoke({"input": user_input})

        # Token usage logging and adjustment for more accurate counting
        tokens_used = self.calculate_tokens(prompt_text + user_input + response)
        logging.info(f"OpenAI API call made. Tokens used: {tokens_used}")
        return response, tokens_used

    def interact_with_ai2(self, user_input, character_name):
        # Generate a more conversational and focused prompt
        prompt_text = "You're a book expert AI. Engage the user in a natural conversation about their book preferences. Use your insights to recommend movies they might like. short answer"
        
        output_parser = StrOutputParser()
        chain = ChatPromptTemplate() | ChatPromptTemplate(prompt_text) | self.llm | output_parser

        response = chain.invoke({"input": user_input})

        # Token usage logging and adjustment for more accurate counting
        tokens_used = self.calculate_tokens(prompt_text + user_input + response)
        logging.info(f"OpenAI API call made. Tokens used: {tokens_used}")
        return response, tokens_used


    def execute(self, *args, **kwargs):
        character_name = kwargs.get("character_name", "Movie Expert")
        print(f"Welcome to the Movie Expert Chat! Let's talk about your movie preferences. Type 'done' to exit anytime.")

        while True:
            user_input = input("You: ").strip()
            if user_input.lower() == "done":
                print("Thank you for using the Movie Expert Chat. Goodbye!")
                break
            
            try:
                response, tokens_used = self.interact_with_ai(user_input, character_name)
                print(f"Movie Expert: {response}")
                print(f"(This interaction used {tokens_used} tokens.)")
                response, tokens_used = self.interact_with_ai2(user_input, character_name)
                print(f"Movie Expert no history: {response}")
                print(f"(This interaction used {tokens_used} tokens.)")
            except Exception as e:
                print("Sorry, there was an error processing your request. Please try again.")
                logging.error(f"Error during interaction: {e}")

