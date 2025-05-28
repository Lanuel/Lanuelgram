


"""
topping_price = {
    'caramel': 0.30,
    'chocolate': 0.50,
    'vanilla': 0.49,
    'pop': 0.20,
    'cheese': 0.40,
    'burger': 0.70,
    'drinks': 2.50,
}

drink_price = {
    'malt': 1.50,
    'coke': 0.75,
    'fanta': 0.75,
}

drink_message = "
                \nSelect your choice of drink below:
                1. Malt
                2. Coke
                3. Fanta
                4. Quit
                "

# Helper to get user input and handle quitting
def get_input(prompt, username=None):
    user_input = input(prompt).strip().lower()
    if user_input == "quit":
        goodbye = f"\nThanks for using our app{f' {username.title()}' if username else ''}, we hope you'll patronize us soon! 💚"
        print(goodbye)
        return None
    return user_input

# Helper to handle drink selection
def choose_drinks():
    drink_chosen = []
    drink_cost = 0
    print(drink_message)

    while True:
        try:
            choice = int(input("Choice: "))
            if choice == 1:
                print("You have selected Malt.")
                drink_chosen.append("malt")
            elif choice == 2:
                print("You have selected Coke.")
                drink_chosen.append("coke")
            elif choice == 3:
                print("You have selected Fanta.")
                drink_chosen.append("fanta")
            elif choice == 4:
                print("You have chosen to quit, thank you!")
                break
            else:
                print("Invalid number. Please enter a number from 1 to 4.")
        except ValueError:
            print("Invalid input. Enter a number between 1 and 4.")
    
    for drink in drink_chosen:
        drink_cost += drink_price.get(drink, 0)
    return drink_chosen, drink_cost

# Main function
def pizza_maker(size, *args, **kwargs):
    active = True
    while active:
        print("\n" + "*" * 65)

        username = get_input("Hello, please enter your username (Type 'quit' to exit): ")
        if not username:
            break

        first_name = get_input("Enter your first name (Type 'quit' to exit): ", username)
        if not first_name:
            break

        last_name = get_input("Enter your last name (Type 'quit' to exit): ", username)
        if not last_name:
            break

        print("*" * 65)
        print(f"\nThis is an order for a {size}-inch pizza by {username.title()}.")

        cost = 0
        unavailable_toppings = []

        # Topping selection
        for topping in args:
            print(f"\tYou selected: {topping} ✔")
            if topping in topping_price:
                cost += topping_price[topping]
            else:
                unavailable_toppings.append(topping)

        # Cost is scaled by size
        total_cost = size * cost

        # Handle unavailable toppings
        if unavailable_toppings:
            print()
            for topping in unavailable_toppings:
                print(f'NB: Sorry, "{topping.upper()}" isn\'t available at the moment. ❌')

        # Drink handling
        drink_cost = 0
        want_drink = input("\nWould you want a drink (Yes/No)? ").strip().lower()
        if want_drink == "yes":
            _, drink_cost = choose_drinks()
        else:
            print("No drink chosen!")

        print()
        print("=" * 62)
        print(f"\tSummary: The total cost of your order is ${(total_cost + drink_cost):.2f}.")
        print("=" * 62)

        print("\nFind below the details of the customer for delivery:")
        print(f"\tFull name: {first_name.title()} {last_name.title()}")
        for key, value in kwargs.items():
            print(f"\t{key.capitalize()}: {value}")

        if cost > 0:
            print(f"\nThanks for patronizing us {username.title()}, we'll be expecting you again soon! 💚💛💙")

# Call the function
pizza_maker(
    10,
    'caramel',
    'strawberry',
    'cheese',
    'chocolate',
    'vanilla',
    'pop',
    location='New York',
    gender='male',
    phone='0987654321'
)
"""