from dotenv import load_dotenv
import streamlit as st
import pandas as pd
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
import os
import time


# Load dataset
news_data = pd.read_csv('Combined_News_DJIA.csv')  # Your news dataset

# Set API key directly
GROQ_API_KEY = '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'

# Streamlit UI
st.title("Financial Investment Advisor")
st.write("Enter a prompt related to stock investments to receive a suggestion based on recent news:")

# Input prompt
user_prompt = st.text_area("Prompt", "Provide details or questions about the stock investment:")

# Function to generate investment suggestion
def generate_investment_suggestion(prompt_message, data):
    # Truncate or summarize dataset to fit within context length limits
    data_summary = news_data.head(5).to_string()[:1000]  # Limit summary to 1000 characters
    
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "You are a financial analyst providing investment advice based on news data. Analyze the provided prompt and news data to offer suggestions on whether to invest in the stock market."),
            ("user", f"Prompt: {prompt_message}\nRelevant News Data Summary: {data_summary}")
        ]
    )

    groqApi = ChatGroq(model="llama3-70b-8192", temperature=0.1, api_key=GROQ_API_KEY)
    outputparser = StrOutputParser()
    chainSec = prompt | groqApi | outputparser

    # Implement rate limiting logic
    max_tokens_per_minute = 5000
    start_time = time.time()
    token_usage = 0

    def rate_limit_check(tokens):
        nonlocal token_usage
        if token_usage + tokens > max_tokens_per_minute:
            elapsed_time = time.time() - start_time
            if elapsed_time < 60:  # Within the same minute
                wait_time = 60 - elapsed_time
                st.write(f"Rate limit exceeded. Waiting for {wait_time:.2f} seconds...")
                time.sleep(wait_time)
            # Reset timer and token usage
            start_time = time.time()
            token_usage = 0

    # Generate investment suggestion with rate limiting
    response = None
    try:
        rate_limit_check(1000)  # Estimate tokens for this request
        response = chainSec.invoke({'data': prompt_message})
        token_usage += len(response)  # Update with actual token usage
    except Exception as e:
        st.write(f"An error occurred: {e}")

    return response

if st.button("Generate Suggestion"):
    if user_prompt.strip():  # Check if prompt is not empty
        investment_suggestion = generate_investment_suggestion(user_prompt, news_data)
        st.write("Investment Suggestion:")
        st.write(investment_suggestion)
    else:
        st.write("Please enter a prompt to generate a suggestion.")
