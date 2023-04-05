from soroban import Soroban


def stellar_soroban_menu():
    print("1 - Authorize a new account")
    print("2 - Authorize a transaction")
    print("3 - Deploy a contract")
    print("4 - Deploy a wrapped token contract")
    print("5 - Invoke a contract")
    print("6 - Make a payment")
    print("0 - Exit")

    prompt = int(input("Enter your choice: "))
    if prompt == 1:
        # Authorize a new account
        Soroban.auth()
    elif prompt == 2:
        # Authorize a transaction
        Soroban.auth_with_transaction()
    elif prompt == 3:
        # Deploy a contract
        Soroban.deploy_contract()
    elif prompt == 4:
        # Deploy a wrapped token contract
        Soroban.deploy_create_wrapped_token_contract()
    elif prompt == 5:
        # Invoke a contract
        Soroban.invoke_contract()
    elif prompt == 6:
        # Make a payment
        Soroban.payment()
    elif prompt == 0:
        # Exit
        exit()
    else:
        print("Invalid choice")


if __name__ == "__main__":

    print("------------------------------------------------")
    print("-------------Stellar Soroban App----------------")
    print("------------------------------------------------")

    print("1 - Stellar Soroban Menu")
    print("0 - Exit")

    prompt = int(input("Enter your choice: "))
    if prompt == 1:
        stellar_soroban_menu()
    elif prompt == 0:
        exit()
    else:
        print("Invalid choice")
