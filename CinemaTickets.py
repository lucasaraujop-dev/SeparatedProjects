seats = [
    "A1", "A2", "A3", "A4", "A5",
    "B1", "B2", "B3", "B4", "B5",
    "C1", "C2", "C3", "C4", "C5",
    "D1", "D2", "D3", "D4", "D5",
    "E1", "E2", "E3", "E4", "E5"
]

original_seats = [
    "A1", "A2", "A3", "A4", "A5",
    "B1", "B2", "B3", "B4", "B5",
    "C1", "C2", "C3", "C4", "C5",
    "D1", "D2", "D3", "D4", "D5",
    "E1", "E2", "E3", "E4", "E5"
]

buyers = [
    "", "", "", "", "",
    "", "", "", "", "",
    "", "", "", "", "",
    "", "", "", "", "",
    "", "", "", "", ""
    ]

chosen_seats = []
while True:
    print("\n--------Cinema UFPB--------")
    print("[1] View Seating Map")
    print("[2] Buy Ticket")
    print("[3] Exit")
    choice = input("Choose an Option: ")
    
    if choice == "1":
        print("\n------SCREEN------")

        count = 1

        for seat in seats:
            print(seat, end=" ")
            if count % 5 == 0:
                print()
            count += 1

    elif choice == "2":
        User = input("Enter your name: ")
        Seat = input("Enter the seat you want to buy: ").upper()

        # O 'or' diz: Aceite o assento se ele estiver livre OU se já foi comprado antes
        if Seat in original_seats:
            position = original_seats.index(Seat)
            if buyers[position] == "":
                seats[position] = "XX"
                buyers[position] = User
                chosen_seats.append(Seat)
                print(f"Ticket for seat {Seat} bought successfully!")
            elif buyers[position] != "":
                print(f"Sorry, the seat {Seat} is already taken by {buyers[position]}.")

    elif choice == "3":
        print("Thank you for using the Cinema Ticket System. Goodbye!")
        break