import ollama
from google import genai
from app.config.api_keys import gemini_api_key

def getResponseFromLLM(system_prompt : str, user_prompt : str, model_temp : float):

    client = genai.Client(api_key=gemini_api_key)

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=user_prompt,
        config=genai.types.GenerateContentConfig(
                system_instruction=system_prompt,
                response_mime_type="application/json", # Forces valid JSON output
                temperature= model_temp 
            )
        )
    
    return response


def warm_up_embedding_model():
    ollama.embed(model="embeddinggemma", input="warmup")
