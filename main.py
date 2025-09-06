import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import schema_get_files_info
from functions.get_file_contents import schema_get_file_content
from functions.write_file import schema_write_file
from functions.run_python_file import schema_run_python_file
from call_function import call_function

def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py 'your request'")
        sys.exit(1)

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    prompt = sys.argv[1]
    verbose = '--verbose' in sys.argv
    
    client = genai.Client(api_key=api_key)
    
    tools = types.Tool(function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file
    ])
    
    system_prompt = """You are a coding agent. The calculator project is in the calculator/ directory.

Always start by calling get_files_info to see files in calculator directory.
Read files before making changes. Make actual code fixes."""

    messages = [types.Content(role="user", parts=[types.Part(text=prompt)])]
    
    config = types.GenerateContentConfig(
        tools=[tools],
        system_instruction=system_prompt
    )

    # Simple agent loop - exactly like your original approach
    for iteration in range(10):
        response = client.models.generate_content(
            model="gemini-2.0-flash-001",
            contents=messages,
            config=config,
        )
        
        # Handle function calls - using your exact pattern
        if hasattr(response, 'function_calls') and response.function_calls:
            for function_call_part in response.function_calls:
                function_call_result = call_function(function_call_part, verbose=verbose)
                messages.append(types.Content(role="user", parts=function_call_result.parts))
        
        # Add model responses
        if hasattr(response, 'candidates') and response.candidates:
            for candidate in response.candidates:
                if hasattr(candidate, 'content') and candidate.content and candidate.content.parts:
                    messages.append(candidate.content)
        
        # Final response
        if hasattr(response, 'text') and response.text:
            print("\nResponse:")
            print(response.text)
            return

    print("Agent completed")

if __name__ == "__main__":
    main()