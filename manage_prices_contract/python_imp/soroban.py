import time
import config
from stellar_sdk import Asset, Keypair, TransactionBuilder
from stellar_sdk import xdr as stellar_xdr
from stellar_sdk.soroban import ContractAuth, AuthorizedInvocation
from stellar_sdk.soroban.soroban_rpc import TransactionStatus
from stellar_sdk.soroban.types import Uint32, Uint128, Address, Symbol


class Soroban:
    def auth():
        contract_id = input("Enter contract ID: ")

        tx_submitter_kp = input("Enter transaction submitter keypair: ")
        tx_submitter_kp = Keypair.from_secret(tx_submitter_kp)

        op_submitter_kp = input("Enter operation submitter keypair: ")
        op_submitter_kp = Keypair.from_secret(op_submitter_kp)

        # contract_id = "b17af0ec4ac76e7f1085c473a3fd45377519b18796b907f9ef643e1f1061df3e"
        # tx_submitter_kp = Keypair.from_secret(
        #     "SAAPYAPTTRZMCUZFPG3G66V4ZMHTK4TWA6NS7U4F7Z3IMUD52EK4DDEV"
        # )
        # # If tx_submitter_kp and op_invoker_kp use the same account, the submission will fail, a bug?
        # op_submitter_kp = Keypair.from_secret(
        #     "SAEZSI6DY7AXJFIYA4PM6SIBNEYYXIEM2MSOTHFGKHDW32MBQ7KVO6EN"
        # )

        try:
            nouce = config.soroban_server.get_nonce(
                contract_id, tx_submitter_kp.public_key
            )

            func_name = input("Enter function name: ")
            func_args = input("Enter function arguments: ")

            invocation = AuthorizedInvocation(
                contract_id=contract_id,
                function_name=func_name,
                function_args=func_args,
                sub_invocations=[],
            )

            contract_auth = ContractAuth(
                address=Address(tx_submitter_kp.public_key),
                nonce=Uint32(nouce),
                invocation=invocation,
            )

            contract_auth.sign(op_submitter_kp, config.network_passphrase)

            source = config.soroban_server.load_account(tx_submitter_kp.public_key)

            tx = (
                TransactionBuilder(
                    source_account=source,
                    network_passphrase=config.network_passphrase,
                    base_fee=config.base_fee,
                )
                .append_invoke_contract_function_op(
                    contract_id=contract_id,
                    function_name=func_name,
                    parameters=func_args,
                    auth=contract_auth,
                )
                .add_time_bounds(0, 0)
                .build()
            )

            simulate_transaction_data = config.soroban_server.simulate_transaction(tx)
            print(f"Simulate transaction: {simulate_transaction_data}")

            print(f"setting footprint and signing transaction")

            assert simulate_transaction_data.results is not None
            tx.set_footpoint(simulate_transaction_data.results[0].footprint)
            tx.sign(tx_submitter_kp)

            print(f"Signed XDR:\n {tx.to_xdr()}")

            send_transaction_data = config.soroban_server.send_transaction(tx)
            print(f"send transaction:" + str(send_transaction_data))

            while True:
                print(f"waiting for transaction to be included in ledger")
                get_transaction_status_data = (
                    config.soroban_server.get_transaction_status(
                        send_transaction_data.id
                    )
                )
                if get_transaction_status_data.status != TransactionStatus.PENDING:
                    break
                time.sleep(2)

            print(f"get transaction status: {get_transaction_status_data}")

            if get_transaction_status_data.status == TransactionStatus.SUCCESS:
                result = stellar_xdr.SCVal.from_xdr(
                    get_transaction_status_data.results[0].xdr
                )
                print(f"get transaction result: {result}")
        except Exception as e:
            print(f"Error: {e}")
            return
