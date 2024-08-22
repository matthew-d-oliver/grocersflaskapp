import json
import datetime
import openai
import os

def query_completion(prompt: str, engine: str = 'gpt-3.5-turbo', temperature: float = 0.2, max_tokens: int = 1500, top_p: int = 1, frequency_penalty: float = 0.2, presence_penalty: float = 0) -> object:
    """
    Function for querying GPT-3.5 Turbo.
    """
    estimated_prompt_tokens = int(len(prompt.split()) * 1.6)
    estimated_answer_tokens = 2049 - estimated_prompt_tokens
    response = openai.ChatCompletion.create(
    model=engine,
    messages=[{"role": "user", "content": prompt}],
    temperature=temperature,
    max_tokens=min(4096-estimated_prompt_tokens-150, max_tokens),
    top_p=top_p,
    frequency_penalty=frequency_penalty,
    presence_penalty=presence_penalty
    )
    return response
    
def lambda_handler(event, context):
    '''Provide an event that contains the following keys:
      - prompt: text of an open ai prompt
    '''
    try:
        openai.api_key = os.environ.get('openai_key')
        
        print("Init:")
        print(datetime.datetime.now())
        print("Event:")
        print(event)
        
        if 'body' in event:
            get_body = json.loads(event['body'])
            client_recipe = get_body['body']
            
            recipe_instance = Recipe(
                title=client_recipe['ingredients']['title']
                produce=client_recipe['ingredients']['produce'],
                protein=client_recipe['ingredients']['protein'],
                dish_style=client_recipe['ingredients']['dish_style'],
                cuisine_style=client_recipe['ingredients']['cuisine_style'],
                servings=client_recipe['ingredients']['servings']
            )
            recipe_instance.make_prompt()
            recipe_instance.generate_recipe()
            response_text = recipe_instance.recipe 
        
            response = {
                "statusCode": 200,
                "headers": {},
                "body": response_text
            }
        
    except Exception as e:
        print(f"Error: {e}")
        response = {
            "statusCode": 500,
            "headers": {},
            "body": "Internal Server Error"
        }
    
    return response

class Recipe:
    """
    Initialize a Recipe object with the specified attributes.

    Attributes:
        title (str): Title of the recipe
        produce (list): List of locally grown organic produce.
        protein (str): Type of protein for the recipe.
        dish_style (str): Style of the dish (e.g., one-pan meal, side dish).
        cuisine_style (str): Style of cuisine (e.g., Mediterranean, South Asian).
        servings (int): Number of servings for the recipe.
        recipe_text (str): The generated recipe text.
    """

    def __init__(self, title = False, produce, protein = False, dish_style = False, cuisine_style = False, servings = False):
        """
        Initialize a Recipe object.
        """
        self.title = title
        self.produce = produce
        self.protein = protein
        self.dish_style = dish_style
        self.cuisine_style = cuisine_style
        self.servings = servings
        self.prompt = None  # To store the generated recipe
        self.receipt = None # return value from the API call 
        self.recipe = None # to store the output fom chatGPT

    def make_prompt(self):
        """
        Generate a recipe based on the specified attributes and store it in recipe_text.
        """
        
        prompt = f"Pretend you're a chef coming up with a meal, and you need to generate a recipe using:\n{', '.join(self.produce)} for produce\n"
        if self.title:
            prompt += f"{self.title} as the title\n"
        if self.protein: 
           prompt += f"{self.protein} as the protein\n"
        if self.dish_style: 
           prompt += f"make the recipe prepared in the style of {self.dish_style}\n" 
        if self.cuisine_style: 
           prompt += f"with the cuisine being {self.cuisine_style}\n"
        if self.servings: 
           prompt += f"for {self.servings} serving(s)"
               
        prompt += "\nYou should format this recipe by giving a title, 1 sentence description, then list ingredients (amount) and then give step by step instructions of how to make the recipe"
        self.prompt = prompt
        # print(self.prompt)

    def generate_recipe(self):
        """
        Call openAi API and MAKE THAT RECIPE
        """
        self.receipt = query_completion(self.prompt)
        # print(self.receipt)
        self.recipe = self.receipt['choices'][0]['message']['content']


    def display_recipe(self):
        """
        Display the generated recipe. Print an appropriate message if the recipe is not generated.
        """
        if self.recipe:
            print(self.recipe)
        else:
            print("Recipe not generated yet. Call generate_recipe() first.")

