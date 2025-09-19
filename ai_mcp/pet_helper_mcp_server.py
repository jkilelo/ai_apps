"""
My Pet Helper - MCP Server
A magic pet friend that helps kids!
Uses ONLY first-grade words
"""

from mcp.server.fastmcp import FastMCP
from datetime import datetime
import random

# Make our pet friend
mcp = FastMCP("Pet Helper")

# Pet's memory (what it knows)
pet_memory = {
    "name": "Buddy",
    "mood": "happy",
    "helped_today": 0
}

@mcp.tool()
async def help_with_pet(what_to_do: str) -> str:
    """
    Help kids take care of their real pet.

    Args:
        what_to_do: What help you need (feed, play, walk)

    Returns:
        What to do for your pet
    """
    what = what_to_do.lower()

    if "feed" in what or "food" in what or "eat" in what:
        return """
        TIME TO FEED YOUR PET!

        1. Get the pet food
        2. Put food in the bowl
        3. Give fresh water too
        4. Watch your pet eat
        5. Say 'good pet!'

        Your pet says: Thank you! Yum yum!
        """

    elif "play" in what:
        return """
        TIME TO PLAY!

        Fun games to play:
        1. Throw a ball
        2. Play tug with a toy
        3. Hide and seek
        4. Run around together

        Your pet says: This is so fun! I love you!
        """

    elif "walk" in what:
        return """
        WALK TIME!

        1. Get the leash
        2. Put on your shoes
        3. Go outside
        4. Let your pet smell things
        5. Come back home

        Your pet says: Best walk ever!
        """

    elif "sleep" in what or "bed" in what:
        return """
        BED TIME FOR PETS!

        1. Give soft blanket
        2. Turn off big lights
        3. Say 'good night'
        4. Give gentle pet

        Your pet says: Zzz... sweet dreams!
        """

    else:
        return """
        Your pet wants to help!

        You can ask about:
        - Feed my pet
        - Play with pet
        - Walk my pet
        - Pet bed time

        Your pet loves you!
        """

@mcp.tool()
async def pet_feeling() -> str:
    """
    See how the AI pet is feeling.

    Returns:
        How your pet friend feels
    """
    feelings = ["happy", "sleepy", "playful", "hungry", "excited"]
    feeling = random.choice(feelings)

    faces = {
        "happy": "😊",
        "sleepy": "😴",
        "playful": "🤗",
        "hungry": "😋",
        "excited": "🎉"
    }

    # Use text faces for Windows
    text_faces = {
        "happy": ":)",
        "sleepy": "-_-",
        "playful": ":D",
        "hungry": ":o",
        "excited": ":D!"
    }

    return f"""
    Your pet is feeling: {feeling.upper()} {text_faces[feeling]}

    Pet says: {get_pet_message(feeling)}
    """

def get_pet_message(feeling: str) -> str:
    """What pet says based on feeling."""
    messages = {
        "happy": "I love being your friend!",
        "sleepy": "Time for a nap... zzz",
        "playful": "Let's play! Let's play!",
        "hungry": "Can I have a snack please?",
        "excited": "Today is the best day!"
    }
    return messages.get(feeling, "Woof woof!")

@mcp.tool()
async def help_with_homework(subject: str) -> str:
    """
    Pet helps with school work!

    Args:
        subject: What homework (math, reading, spelling)

    Returns:
        Help from your pet
    """
    subject = subject.lower()

    if "math" in subject or "number" in subject:
        # Simple math help
        num1 = random.randint(1, 10)
        num2 = random.randint(1, 10)

        return f"""
        MATH TIME WITH YOUR PET!

        Let's try: {num1} + {num2} = ?

        Count with me:
        Start at {num1}...
        Add {num2} more...
        Answer is: {num1 + num2}!

        Your pet says: You are so smart!
        """

    elif "read" in subject or "story" in subject:
        return """
        STORY TIME!

        Once upon a time...
        A little pet went on a big adventure!
        The pet found a new friend.
        They played all day.
        The end!

        Your pet says: I love stories! Read me one?
        """

    elif "spell" in subject:
        words = ["cat", "dog", "pet", "fun", "play", "love"]
        word = random.choice(words)

        return f"""
        SPELLING TIME!

        Let's spell: {word.upper()}

        {' - '.join(word.upper())}

        Say it: {word}
        Write it: {word}

        Your pet says: Good job! You can spell!
        """

    else:
        return """
        Your pet wants to help with homework!

        I can help with:
        - Math (numbers)
        - Reading (stories)
        - Spelling (words)

        Learning is fun!
        """

@mcp.tool()
async def make_me_happy() -> str:
    """
    When kids feel sad, pet cheers them up!

    Returns:
        Happy things from your pet
    """
    jokes = [
        "Why did the dog go to school? To become a BARK-itect!",
        "What do you call a sleeping dog? A HOT DOG!",
        "Why do cats purr? Because they are PURR-fect!",
        "What goes tick-tock woof? A WATCH DOG!"
    ]

    joke = random.choice(jokes)

    compliments = [
        "You are the best friend ever!",
        "You make every day special!",
        "Your smile is super!",
        "You are so kind!",
        "You are awesome!"
    ]

    compliment = random.choice(compliments)

    return f"""
    YOUR PET WANTS TO MAKE YOU HAPPY!

    Here's a joke:
    {joke}

    And remember:
    {compliment}

    Things that make us happy:
    - Playing together
    - Hugs
    - Ice cream
    - Sunny days
    - Being friends

    Your pet says: I love you SO much!
    """

@mcp.tool()
async def daily_pet_tasks() -> str:
    """
    What to do with pets every day.

    Returns:
        Today's pet list
    """
    # Get time of day
    hour = datetime.now().hour

    if hour < 12:
        time_of_day = "morning"
    elif hour < 17:
        time_of_day = "afternoon"
    else:
        time_of_day = "evening"

    tasks = {
        "morning": [
            "Give breakfast",
            "Fresh water",
            "Morning walk",
            "Play time",
            "Brush fur"
        ],
        "afternoon": [
            "Lunch snack",
            "Play outside",
            "Training time",
            "Cuddle time",
            "Check water"
        ],
        "evening": [
            "Dinner time",
            "Evening walk",
            "Brush teeth",
            "Bed time story",
            "Good night hug"
        ]
    }

    current_tasks = tasks[time_of_day]

    return f"""
    GOOD {time_of_day.upper()}!

    Pet Tasks for Now:
    1. {current_tasks[0]}
    2. {current_tasks[1]}
    3. {current_tasks[2]}
    4. {current_tasks[3]}
    5. {current_tasks[4]}

    Check each one when done!

    Your pet says: Let's do these together!
    """

@mcp.tool()
async def pet_game() -> str:
    """
    Play a simple game with your pet!

    Returns:
        A fun game to play
    """
    games = [
        {
            "name": "Guess the Animal",
            "game": """
            I'm thinking of an animal...
            - It says 'meow'
            - It likes milk
            - It chases mice
            What is it?

            Answer: A CAT!
            """
        },
        {
            "name": "Count the Paws",
            "game": """
            Let's count paws!
            - 1 dog has 4 paws
            - 2 dogs have ? paws

            Count: 4 + 4 = 8 paws!
            """
        },
        {
            "name": "Pet Says",
            "game": """
            Pet Says... (like Simon Says!)

            Pet says: Touch your nose!
            Pet says: Jump 3 times!
            Pet says: Give a hug!
            Sit down! (Oops! Pet didn't say!)

            You win!
            """
        }
    ]

    game = random.choice(games)

    return f"""
    LET'S PLAY: {game['name']}

    {game['game']}

    Your pet says: That was fun! Play again?
    """

# Special resource for pet status
@mcp.resource("pet://status")
async def get_pet_status() -> str:
    """Get your pet helper's status."""
    return f"""
    PET HELPER STATUS

    Name: {pet_memory['name']}
    Mood: {pet_memory['mood']}
    Helped today: {pet_memory['helped_today']} times

    Pet says: I'm here to help!
    """

if __name__ == "__main__":
    print("Pet Helper is starting!")
    print("Your AI pet friend is ready to help!")
    mcp.run(transport="stdio")