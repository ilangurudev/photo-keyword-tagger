"""
A simple hello world module for demonstration purposes.
"""


def say_hello(name: str = "World") -> str:
    """
    Returns a personalized greeting.
    
    Args:
        name: The name to greet (default: "World")
        
    Returns:
        A greeting string
    """
    return f"Hello, {name}! Welcome to Photo Keyword Tagger."


def main() -> None:
    """Main entry point for the hello world demo."""
    print(say_hello())


if __name__ == "__main__":
    main()

