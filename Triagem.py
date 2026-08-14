while True:
    # LEVEL
    priority_score = 0
    priorityRED = False
    priorityYELLOW = False
    priorityGREEN = False

    #VARIABLES
    elderly = False
    adult = False
    child = False

    print("\n------------------------------")
    print("Starting an new triage process...")
    print("\n------------------------------")
    patient = input("What's your name? ")
    if patient.strip() == "":
        print("Invalid name. Please enter a valid name.")
        continue

    print("Hello, " + patient + "! Please answer the following questions to determine your priority level.")

    age = int(input("What is your age? "))
    if age < 0:
        print("Invalid age. Please enter a valid age.")
        continue
    
    temperature = float(input("What is your body temperature? "))
    headache = input("Do you have a headache? (y/n) ")
    chest_pain = input("Do you have chest pain? (y/n) ")
    vomiting = input("Are you vomiting? (y/n) ")
    virus_symptoms = input("Do you have symptoms of a virus? (y/n) ")

    # AGE VERIFICATION
    if age >= 65:
        elderly = True
    elif age >= 18:
        adult = True    
    elif age >= 1:
        child = True        

    # PRIORITY LEVEL DETERMINATION
    if elderly:
        priority_score += 3
    if adult:
        priority_score += 1
    if child:
        priority_score += 2
    if temperature >= 38.0:
        priority_score += 2
    if headache == "y":
        priority_score += 1
    if chest_pain == "y":
        priority_score += 3
    if vomiting == "y":
        priority_score += 2
    if virus_symptoms == "y":
        priority_score += 1

    if priority_score >= 7:
        print("You are in the red priority level. Please seek immediate medical attention.")
        priorityRED = True
    elif priority_score >= 4:
        print("You are in the yellow priority level. Please wait for further instructions.")
        priorityYELLOW = True
    else:
        print("You are in the green priority level. Please wait for further instructions.")
        priorityGREEN = True
        
    break