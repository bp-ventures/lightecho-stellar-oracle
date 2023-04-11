import time
import config
from stellar_sdk import Asset, Keypair, TransactionBuilder
from stellar_sdk import xdr as stellar_xdr
from stellar_sdk.soroban import types, ContractAuth, AuthorizedInvocation, SorobanServer
from stellar_sdk.soroban.soroban_rpc import GetTransactionStatus
from stellar_sdk.soroban.types import Uint32, Uint128, Address, Symbol


class Soroban:
    def invoke_contract(prompt):
        if prompt == 1:
            args = [
                Address("GALGFV6YVKMVAWHK6QA7GCC67VKBW73A3PB5IKZGKT5ID5AGK4S3Y7GX"),
                Uint32(1),
                Uint32(1),
            ]
        elif prompt == 2:
            args = [
                Address("GALGFV6YVKMVAWHK6QA7GCC67VKBW73A3PB5IKZGKT5ID5AGK4S3Y7GX"),
                Uint32(5),
                Uint32(5),
            ]
        elif prompt == 3 or prompt == 4:
            args = []

        Soroban.invoke(
            args=args,
            fun_name="create"
            if prompt == 1
            else "update"
            if prompt == 2
            else "get"
            if prompt == 3
            else "delete",
        )

    def invoke(args, fun_name):
        secret = "SCNLUY7SFXJYVIULV66V2OQHNB4XDWYFGNNCN5YBBC3MZT5XN4X7IJP6"

        # This contract id should be a valid contract id on the futurenet network.
        contract_id = "71bba71125a417479f6f3069ed336e9e5246132f624a738a08250c156aad3f92"

        try:
            kp = Keypair.from_secret(secret)
            soroban_server = SorobanServer(config.rpc_server_url)
            source = soroban_server.load_account(kp.public_key)

            # Let's build a transaction that invokes the function.
            tx = (
                TransactionBuilder(source, config.network_passphrase)
                .set_timeout(300)
                .append_invoke_contract_function_op(
                    contract_id=contract_id,
                    function_name=fun_name,
                    parameters=args,
                    source=kp.public_key,
                )
                .build()
            )

            simulate_transaction_data = soroban_server.simulate_transaction(tx)
            # print(f"simulated transaction: {simulate_transaction_data}")

            print(f"setting footprint and signing transaction...")
            assert simulate_transaction_data.results is not None
            tx.set_footpoint(simulate_transaction_data.results[0].footprint)
            tx.sign(kp)

            send_transaction_data = soroban_server.send_transaction(tx)
            # print(f"sent transaction: {send_transaction_data}")

            print("waiting for transaction to be confirmed...")
            while True:
                get_transaction_data = soroban_server.get_transaction(
                    send_transaction_data.hash
                )
                if get_transaction_data.status != GetTransactionStatus.NOT_FOUND:
                    break
                time.sleep(3)

            # print(f"transaction: {get_transaction_data}")
            print(f"transaction confirmed")

            if get_transaction_data.status == GetTransactionStatus.SUCCESS:
                assert get_transaction_data.result_meta_xdr is not None
                transaction_meta = stellar_xdr.TransactionMeta.from_xdr(
                    get_transaction_data.result_meta_xdr
                )
                result = transaction_meta.v3.tx_result.result.results[0].tr.invoke_host_function_result.success  # type: ignore
                # output = [x.sym.sc_symbol.decode() for x in result.vec.sc_vec]  # type: ignore
                # print(f"transaction result: {output}")

                # Comment if you want to invoke get function
                if fun_name == "create" or fun_name == "update" or fun_name == "delete":
                    print(f"transaction result: {result}")
                else:
                    struct = types.Struct.from_xdr_sc_val(result)
                    print(
                        f"key: {struct.fields[0].key}, value: {types.Uint32.from_xdr_sc_val(struct.fields[0].value).value}"
                    )
                    print(
                        f"key: {struct.fields[1].key}, value: {types.Uint32.from_xdr_sc_val(struct.fields[1].value).value}"
                    )
                    print(
                        f"key: {struct.fields[2].key}, value: {types.Address.from_xdr_sc_val(struct.fields[2].value).address}"
                    )

                # Uncomment if you want to invoke get function
                # struct = types.Struct.from_xdr_sc_val(result)
                # print(
                #     f"key: {struct.fields[0].key}, value: {types.Uint32.from_xdr_sc_val(struct.fields[0].value).value}"
                # )
                # print(
                #     f"key: {struct.fields[1].key}, value: {types.Uint32.from_xdr_sc_val(struct.fields[1].value).value}"
                # )
                # print(
                #     f"key: {struct.fields[2].key}, value: {types.Address.from_xdr_sc_val(struct.fields[2].value).address}"
                # )
        except Exception as e:
            print(f"Error: {e}")
            return
