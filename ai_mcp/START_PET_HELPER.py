"""
CLICK ME TO START YOUR PET HELPER!
For kids!
"""

import asyncio
import os

# Pretty colors (if computer can show them)
os.system('color')

def show_pet():
    """Show a cute pet!"""
    print("""

         /\\_/\\
        ( o.o )
         > ^ <

        WOOF! I'M YOUR PET HELPER!
    """)

def main():
    """Start everything!"""

    # Clear screen
    os.system('cls' if os.name == 'nt' else 'clear')

    # Show the pet
    show_pet()

    print("\n" + "="*50)
    print("     MY PET HELPER")
    print("     The Best Friend for Kids!")
    print("="*50)

    print("\n[BIG LETTERS FOR GROWN-UPS]:")
    print("This AI pet helps kids with:")
    print("- Taking care of real pets")
    print("- Homework help (math, reading)")
    print("- Making kids happy when sad")
    print("- Playing fun games")
    print("- Daily pet tasks")

    print("\n" + "="*50)
    print("\n[FOR KIDS]:")
    print("YOUR PET WANTS TO PLAY!")
    print("\nPRESS ANY KEY TO START...")
    input()

    # Run the pet helper
    try:
        from pet_helper_simple import main as start_pet
        start_pet()
    except Exception as e:
        # If something breaks, show simple demo
        print("\n" + "="*50)
        print("PET HELPER DEMO MODE")
        print("="*50)

        print("\nYour pet can:")
        print("\n1. HELP WITH PETS")
        print("   'How do I feed my dog?'")
        print("   Pet: 'Get food, put in bowl, give water!'")

        print("\n2. MAKE YOU HAPPY")
        print("   'I feel sad'")
        print("   Pet: 'Here's a joke! You are awesome!'")

        print("\n3. HELP WITH HOMEWORK")
        print("   'Help with math'")
        print("   Pet: 'Let's count! 5 + 3 = 8!'")

        print("\n4. PLAY GAMES")
        print("   'Play with me'")
        print("   Pet: 'Let's play Pet Says! Touch your nose!'")

        print("\n" + "="*50)
        print("Your pet loves you!")
        print("Come back and play again!")
        print("="*50)

        input("\nPress ENTER to close...")

if __name__ == "__main__":
    main()