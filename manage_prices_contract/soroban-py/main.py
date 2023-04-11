from soroban import Soroban

if __name__ == "__main__":
    print("------------------------------------------------")
    print("-------------Soroban Prices Oracle--------------")
    print("------------------------------------------------")

    print("1 - Invoke create function")
    print("2 - Invoke update function")
    print("3 - Invoke get function")
    print("4 - Invoke delete function")
    print("0 - Exit")

    prompt = int(input("Enter your choice: "))
    if prompt == 0:
        exit()
    elif prompt == 1 or prompt == 2 or prompt == 3 or prompt == 4:
        Soroban.invoke_contract(prompt)
    else:
        print("Invalid choice")
