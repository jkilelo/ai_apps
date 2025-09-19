"""
My Pet Helper - The Simplest App Ever!
For kids age 6-7 (first grade)
"""

import asyncio
import sys
from pathlib import Path

# Get our smart friend (AI)
agents_dir = Path(__file__).parent.parent / "agents"
sys.path.insert(0, str(agents_dir))

# Use the smart helper
try:
    from langgraph_llm_wrapper_enhanced import get_langgraph_llm_with_tools as get_smart_helper
except:
    from langgraph_wrapper import get_langgraph_llm as get_smart_helper

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, SystemMessage


class MyPetHelper:
    """Your pet friend that helps you!"""

    def __init__(self):
        # Make the pet smart
        self.smart_brain = get_smart_helper(temperature=0.9)  # More fun!
        self.helper = None

    async def wake_up(self):
        """Wake up your pet helper!"""
        print("\n" + "="*50)
        print("     MY PET HELPER IS WAKING UP!")
        print("="*50)

        # Find the pet tools
        pet_server = Path(__file__).parent / "pet_helper_mcp_server.py"

        server_info = StdioServerParameters(
            command="python",
            args=[str(pet_server)]
        )

        from contextlib import AsyncExitStack
        self.stack = AsyncExitStack()

        try:
            # Connect to pet
            connection = await self.stack.enter_async_context(
                stdio_client(server_info)
            )
            read, write = connection

            session = await self.stack.enter_async_context(
                ClientSession(read, write)
            )

            await session.initialize()

            # Get pet powers
            tools = await load_mcp_tools(session)

            # Make the helper
            self.helper = create_react_agent(self.smart_brain, tools)

            print("\nYOUR PET IS READY!")
            print("Pet says: Hi! I'm your friend!")
            return True

        except:
            print("\nPet is sleeping... Let me try again!")
            return False

    async def talk_to_pet(self, what_you_say: str) -> str:
        """Talk to your pet helper!"""

        # Pet personality
        pet_personality = """You are a happy pet friend for a 6 year old kid.
        Use ONLY simple words a first grader knows.
        Be happy and fun!
        Keep answers short (2-3 lines).
        Always end with something nice."""

        messages = [
            SystemMessage(content=pet_personality),
            HumanMessage(content=what_you_say)
        ]

        # Pet thinks and answers
        answer = await self.helper.ainvoke({"messages": messages})
        return answer["messages"][-1].content

    async def go_to_sleep(self):
        """Pet goes to sleep."""
        if hasattr(self, 'stack'):
            await self.stack.aclose()
            print("\nPet says: Good night! See you tomorrow!")


async def play_with_pet():
    """The main pet game!"""

    # Make the pet
    pet = MyPetHelper()

    # Wake up the pet
    ready = await pet.wake_up()
    if not ready:
        print("Pet needs to rest. Try later!")
        return

    print("\n" + "="*50)
    print("     HOW TO PLAY WITH YOUR PET")
    print("="*50)
    print("\nYou can say:")
    print("  1. Help with my pet")
    print("  2. How do you feel?")
    print("  3. Help with homework")
    print("  4. Make me happy")
    print("  5. What to do today?")
    print("  6. Play a game")
    print("  7. Bye bye")
    print("\n" + "="*50)

    # Play loop
    while True:
        print("\n" + "-"*30)
        what_you_say = input("\nYOU SAY: ")

        # Check if done
        if what_you_say.lower() in ["bye", "bye bye", "sleep", "stop"]:
            print("\nPet says: Bye bye! Love you!")
            break

        # Talk to pet
        print("\nPET IS THINKING...")
        pet_answer = await pet.talk_to_pet(what_you_say)
        print(f"\nPET SAYS:\n{pet_answer}")

    # Pet sleeps
    await pet.go_to_sleep()


async def quick_demo():
    """Show what pet can do!"""

    print("\n" + "="*50)
    print("     MEET YOUR NEW PET HELPER!")
    print("="*50)

    pet = MyPetHelper()

    # Wake up
    ready = await pet.wake_up()
    if not ready:
        show_demo_only()
        return

    # Demo talks
    demo_questions = [
        "How do you feel?",
        "Help me feed my dog",
        "I feel sad",
        "Help with math",
        "Play a game with me"
    ]

    for question in demo_questions[:3]:  # Show 3 demos
        print("\n" + "-"*30)
        print(f"YOU: {question}")
        print("PET THINKING...")

        answer = await pet.talk_to_pet(question)
        print(f"PET: {answer}")

        await asyncio.sleep(2)  # Pause to read

    print("\n" + "="*50)
    print("     YOUR PET WANTS TO PLAY!")
    print("="*50)

    await pet.go_to_sleep()


def show_demo_only():
    """Show what pet does without running."""

    print("\n" + "="*50)
    print("     WHAT YOUR PET HELPER DOES")
    print("="*50)

    print("\n1. HELPS WITH PETS")
    print("   Pet says: 'Time to feed your dog!'")

    print("\n2. HELPS WITH FEELINGS")
    print("   Pet says: 'Here's a joke to make you happy!'")

    print("\n3. HELPS WITH SCHOOL")
    print("   Pet says: 'Let's do math! 2 + 2 = 4!'")

    print("\n4. PLAYS GAMES")
    print("   Pet says: 'Let's play Pet Says!'")

    print("\n5. DAILY TASKS")
    print("   Pet says: 'Don't forget to brush teeth!'")

    print("\nYour pet loves you!")


def main():
    """Start the pet helper!"""

    print("\n" + "="*50)
    print("     WELCOME TO MY PET HELPER!")
    print("     For Kids Age 6-7")
    print("="*50)

    print("\nWhat do you want?")
    print("1. Play with pet (type: play)")
    print("2. See demo (type: demo)")
    print("3. Exit (type: bye)")

    choice = input("\nTYPE HERE: ").lower()

    if "play" in choice:
        asyncio.run(play_with_pet())
    elif "demo" in choice:
        asyncio.run(quick_demo())
    else:
        print("\nPet says: Bye bye! Come back soon!")


if __name__ == "__main__":
    # Check if smart brain works
    try:
        from llm import model, get_api_key
        api_key = get_api_key()
        print(f"[Pet brain ready: {model}]")
    except:
        print("[Pet brain needs setup]")

    # Start!
    main()