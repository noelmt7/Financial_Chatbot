from langchain_groq import ChatGroq

# Simple test to check API connection
groqApi = ChatGroq(model="llama3-70b-8192", api_key='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')
try:
    response = groqApi.invoke({'data': "Test connection"})
    print(response)
except Exception as e:
    print(f"Connection error: {e}")
