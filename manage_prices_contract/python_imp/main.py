from soroban import Soroban

if __name__ == "__main__":
    print("------------------------------------------------")
    print("-------------Soroban Prices Oracle--------------")
    print("------------------------------------------------")

    print("1 - Prices Oracle Menu")
    print("0 - Exit")

    prompt = int(input("Enter your choice: "))
    if prompt == 1:
        Soroban.auth()
    elif prompt == 0:
        exit()
    else:
        print("Invalid choice")
