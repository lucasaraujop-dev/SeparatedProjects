tasks = []

while True:
    print("\n--------To-Do List--------")
    print("[1] View Tasks")
    print("[2] Add Task")
    print("[3] Remove Task")
    print("[4] Exit")
    choice = input("Choose an Option: ")

    if choice == "1":
        if not tasks:
            print("No tasks in the list.")
        else:
            print("\n------TO DO LIST------")
            for index, task in enumerate(tasks, start=1): # index = posição da tarefa na lista, task = nome da tarefa
                print(f"{index}, {task}")
    
    elif choice == "2":
        new_task = input("Enter a new task: ")
        tasks.append(f"[] {new_task}")
        print(f"Task '{new_task}' added successfully.")

    elif choice == "3":
        if not tasks:
            print("No tasks to remove.")
        else:
            number = int(input("Enter the number of the task to remove: "))
            position = number - 1
            if 0 <= position < len(tasks):
                removed_task = tasks.pop(position)
                print(f"Task '{removed_task}' removed successfully.")
            else:
                print("Invalid task number.")
    elif choice == "4":
        print("Exiting the program.")
        break
    else:
        print("Invalid choice. Please try again.")