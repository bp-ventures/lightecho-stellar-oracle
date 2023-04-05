import time
import config
from stellar_sdk import (
    Asset,
    Network,
    Keypair,
    TransactionBuilder,
)
from stellar_sdk import xdr as stellar_xdr
from stellar_sdk.soroban import SorobanServer, ContractAuth, AuthorizedInvocation
from stellar_sdk.soroban.soroban_rpc import TransactionStatus
from stellar_sdk.soroban.types import Uint32, Int128, Address, Symbol


class Soroban:
    def auth():
        contract_id = "8542841a633aafc771f07bc472b7a799fa2e82cced417356505f569daaaedc47"
        tx_submitter_kp = Keypair.from_secret(
            "SAAPYAPTTRZMCUZFPG3G66V4ZMHTK4TWA6NS7U4F7Z3IMUD52EK4DDEV"
        )
        op_invoker_kp = Keypair.from_secret(
            "SAEZSI6DY7AXJFIYA4PM6SIBNEYYXIEM2MSOTHFGKHDW32MBQ7KVO6EN"
        )

        nonce = config.soroban_server.get_nonce(contract_id, op_invoker_kp.public_key)
        func_name = "increment"
        args = [Address(op_invoker_kp.public_key), Uint32(10)]

        invocation = AuthorizedInvocation(
            contract_id=contract_id,
            function_name=func_name,
            args=args,
            sub_invocations=[],
        )

        contract_auth = ContractAuth(
            address=Address(op_invoker_kp.public_key),
            nonce=nonce,
            root_invocation=invocation,
        )

        contract_auth.sign(op_invoker_kp, config.network_passphrase)

        source = config.soroban_server.load_account(tx_submitter_kp.public_key)
        tx = (
            TransactionBuilder(source, config.network_passphrase)
            .add_time_bounds(0, 0)
            .append_invoke_contract_function_op(
                contract_id=contract_id,
                function_name=func_name,
                parameters=args,
                auth=[contract_auth],
            )
            .build()
        )

        simulate_transaction_data = config.soroban_server.simulate_transaction(tx)
        print(f"simulated transaction: {simulate_transaction_data}")

        print(f"setting footprint and signing transaction...")
        assert simulate_transaction_data.results is not None
        tx.set_footpoint(simulate_transaction_data.results[0].footprint)
        tx.sign(tx_submitter_kp)

        print(f"Signed XDR:\n{tx.to_xdr()}")

        send_transaction_data = config.soroban_server.send_transaction(tx)
        print(f"sent transaction: {send_transaction_data}")

        while True:
            print("waiting for transaction to be confirmed...")
            get_transaction_status_data = config.soroban_server.get_transaction_status(
                send_transaction_data.id
            )
            if get_transaction_status_data.status != TransactionStatus.PENDING:
                break
            time.sleep(3)
        print(f"transaction status: {get_transaction_status_data}")

        if get_transaction_status_data.status == TransactionStatus.SUCCESS:
            result = stellar_xdr.SCVal.from_xdr(get_transaction_status_data.results[0].xdr)  # type: ignore
            print(f"transaction result: {result}")

    def auth_with_transaction():

        contract_id = "f9da8befbc0084f01dfdd28ecfb3970abb53824390c563aa76bbc85c99b5e422"
        tx_submitter_kp = Keypair.from_secret(
            "SAKFQFUYTCWME2TK2AIRALDJKZBGOAEAKFJ2XIB5BZWO2BNV5ZMVTR3U"
        )

        func_name = "hello"
        args = [Address(tx_submitter_kp.public_key), Uint32(10)]

        invocation = AuthorizedInvocation(
            contract_id=contract_id,
            function_name=func_name,
            args=args,
            sub_invocations=[],
        )

        contract_auth = ContractAuth(
            address=None,
            nonce=None,
            root_invocation=invocation,
        )

        source = config.soroban_server.load_account(tx_submitter_kp.public_key)
        tx = (
            TransactionBuilder(source, config.network_passphrase)
            .add_time_bounds(0, 0)
            .append_invoke_contract_function_op(
                contract_id=contract_id,
                function_name=func_name,
                parameters=args,
                auth=[contract_auth],
            )
            .build()
        )

        simulate_transaction_data = config.soroban_server.simulate_transaction(tx)
        print(f"simulated transaction: {simulate_transaction_data}")

        print(f"setting footprint and signing transaction...")
        assert simulate_transaction_data.results is not None
        tx.set_footpoint(simulate_transaction_data.results[0].footprint)
        tx.sign(tx_submitter_kp)

        print(f"Signed XDR:\n{tx.to_xdr()}")

        send_transaction_data = config.soroban_server.send_transaction(tx)
        print(f"sent transaction: {send_transaction_data}")

        while True:
            print("waiting for transaction to be confirmed...")
            get_transaction_status_data = config.soroban_server.get_transaction_status(
                send_transaction_data.id
            )
            if get_transaction_status_data.status != TransactionStatus.PENDING:
                break
            time.sleep(3)
        print(f"transaction status: {get_transaction_status_data}")

        if get_transaction_status_data.status == TransactionStatus.SUCCESS:
            result = stellar_xdr.SCVal.from_xdr(get_transaction_status_data.results[0].xdr)  # type: ignore
            print(f"transaction result: {result}")

    def deploy_contract():
        secret = "SAAPYAPTTRZMCUZFPG3G66V4ZMHTK4TWA6NS7U4F7Z3IMUD52EK4DDEV"

        contract_file_path = "samples\soroban_hello_world_contract.wasm"

        kp = Keypair.from_secret(secret)

        print(f"instantiating contract...")
        source = config.soroban_server.load_account(kp.public_key)
        tx = (
            TransactionBuilder(source, config.network_passphrase)
            .set_timeout(300)
            .append_install_contract_code_op(
                contract=contract_file_path,  # the path to the contract, or binary data
                source=kp.public_key,
            )
            .build()
        )

        simulate_transaction_data = config.soroban_server.simulate_transaction(tx)
        print(f"simulated transaction: {simulate_transaction_data}")

        # The footpoint is predictable, maybe we can optimize the code to omit this step
        print(f"setting footprint and signing transaction...")
        assert simulate_transaction_data.results is not None
        tx.set_footpoint(simulate_transaction_data.results[0].footprint)
        tx.sign(kp)

        send_transaction_data = config.soroban_server.send_transaction(tx)
        print(f"sent transaction: {send_transaction_data}")

        while True:
            print("waiting for transaction to be confirmed...")
            get_transaction_status_data = config.soroban_server.get_transaction_status(
                send_transaction_data.id
            )
            if get_transaction_status_data.status != TransactionStatus.PENDING:
                break
            time.sleep(3)
        print(f"transaction status: {get_transaction_status_data}")

        wasm_id = None
        if get_transaction_status_data.status == TransactionStatus.SUCCESS:
            result = stellar_xdr.SCVal.from_xdr(get_transaction_status_data.results[0].xdr)  # type: ignore
            wasm_id = result.obj.bin.hex()  # type: ignore
            print(f"wasm id: {wasm_id}")

        assert wasm_id, "wasm id should not be empty"

        print("creating contract...")

        source = config.soroban_server.load_account(
            kp.public_key
        )  # refresh source account, because the current SDK will increment the sequence number by one after building a transaction

        tx = (
            TransactionBuilder(source, config.network_passphrase)
            .set_timeout(300)
            .append_create_contract_op(
                wasm_id=wasm_id,
                source=kp.public_key,
            )
            .build()
        )

        simulate_transaction_data = config.soroban_server.simulate_transaction(tx)
        print(f"simulated transaction: {simulate_transaction_data}")

        # The footpoint is predictable, maybe we can optimize the code to omit this step
        print(f"setting footprint and signing transaction...")
        assert simulate_transaction_data.results is not None
        tx.set_footpoint(simulate_transaction_data.results[0].footprint)
        tx.sign(kp)

        send_transaction_data = config.soroban_server.send_transaction(tx)
        print(f"sent transaction: {send_transaction_data}")

        while True:
            print("waiting for transaction to be confirmed...")
            get_transaction_status_data = config.soroban_server.get_transaction_status(
                send_transaction_data.id
            )
            if get_transaction_status_data.status != TransactionStatus.PENDING:
                break
            time.sleep(3)
        print(f"transaction status: {get_transaction_status_data}")

        wasm_id = None
        if get_transaction_status_data.status == TransactionStatus.SUCCESS:
            result = stellar_xdr.SCVal.from_xdr(get_transaction_status_data.results[0].xdr)  # type: ignore
            contract_id = result.obj.bin.hex()  # type: ignore
            print(f"contract id: {contract_id}")

    def deploy_create_wrapped_token_contract():
        secret = "SAAPYAPTTRZMCUZFPG3G66V4ZMHTK4TWA6NS7U4F7Z3IMUD52EK4DDEV"

        hello_asset = Asset(
            "HELLO", "GBCXQUEPSEGIKXLYODHKMZD7YMTZ4IUY3BYPRZL4D5MSJZHHE7HG6RWR"
        )

        kp = Keypair.from_secret(secret)
        source = config.soroban_server.load_account(kp.public_key)

        tx = (
            TransactionBuilder(
                source_account=source,
                network_passphrase=config.network_passphrase,
                base_fee=100,
            )
            .append_deploy_create_token_contract_with_asset_op(
                asset=hello_asset,
                source=kp.public_key,
            )
            .set_timeout(30)
            .build()
        )

        simulate_transaction_data = config.soroban_server.simulate_transaction(tx)
        print(f"simulated transaction: {simulate_transaction_data}")

        print(f"setting footprint and signing transaction...")
        assert simulate_transaction_data.results is not None
        tx.set_footprint(simulate_transaction_data.results[0].footprint)
        tx.sign(kp)

        send_transaction_data = config.soroban_server.send_transaction(tx)
        print(f"sent transaction: {send_transaction_data}")

        while True:
            print("waiting for transaction to be confirmed...")
            get_transaction_status_data = config.soroban_server.get_transaction_status(
                send_transaction_data.id
            )
            if get_transaction_status_data.status != TransactionStatus.PENDING:
                break
            time.sleep(3)
        print(f"transaction status: {get_transaction_status_data}")

        if get_transaction_status_data.status == TransactionStatus.SUCCESS:
            result = stellar_xdr.SCVal.from_xdr(
                get_transaction_status_data.results[0].xdr
            )
            contract_id = result.obj.bin.hex()
            print(f"contract id: {contract_id}")

    def invoke_contract():
        secret = "SAAPYAPTTRZMCUZFPG3G66V4ZMHTK4TWA6NS7U4F7Z3IMUD52EK4DDEV"
        contract_id = "348548af2ce5e6970147a80b3097f2d9ea89e5f6830e5da0adca7f7db15e6aa9"

        kp = Keypair.from_secret(secret)
        source = config.soroban_server.load_account(kp.public_key)

        tx = (
            TransactionBuilder(source, config.network_passphrase)
            .set_timeout(300)
            .append_invoke_contract_function_op(
                contract_id=contract_id,
                function_name="hello",
                parameters=[Symbol("world")],
                source=kp.public_key,
            )
            .build()
        )

        simulate_transaction_data = config.soroban_server.simulate_transaction(tx)
        print(f"simulated transaction: {simulate_transaction_data}")

        print(f"setting footprint and signing transaction...")
        assert simulate_transaction_data.results is not None
        tx.set_footpoint(simulate_transaction_data.results[0].footprint)
        tx.sign(kp)

        send_transaction_data = config.soroban_server.send_transaction(tx)
        print(f"sent transaction: {send_transaction_data}")

        while True:
            print("waiting for transaction to be confirmed...")
            get_transaction_status_data = config.soroban_server.get_transaction_status(
                send_transaction_data.id
            )
            if get_transaction_status_data.status != TransactionStatus.PENDING:
                break
            time.sleep(3)
        print(f"transaction status: {get_transaction_status_data}")

        if get_transaction_status_data.status == TransactionStatus.SUCCESS:
            result = stellar_xdr.SCVal.from_xdr(get_transaction_status_data.results[0].xdr)  # type: ignore
            output = [x.sym.sc_symbol.decode() for x in result.obj.vec.sc_vec]  # type: ignore
            print(f"transaction result: {output}")

    def payment():

        alice_kp = Keypair.from_secret(
            "SAAPYAPTTRZMCUZFPG3G66V4ZMHTK4TWA6NS7U4F7Z3IMUD52EK4DDEV"
        )  # GDAT5HWTGIU4TSSZ4752OUC4SABDLTLZFRPZUJ3D6LKBNEPA7V2CIG54
        bob_kp = Keypair.from_secret(
            "SAEZSI6DY7AXJFIYA4PM6SIBNEYYXIEM2MSOTHFGKHDW32MBQ7KVO6EN"
        )  # GBMLPRFCZDZJPKUPHUSHCKA737GOZL7ERZLGGMJ6YGHBFJZ6ZKMKCZTM
        native_token_contract_id = (
            "d93f5c7bb0ebc4a9c8f727c5cebc4e41194d38257e1d0d910356b43bfc528813"
        )

        alice_source = config.soroban_server.load_account(alice_kp.public_key)

        args = [
            Address(alice_kp.public_key),  # from
            Address(bob_kp.public_key),  # to
            Int128(100 * 10**7),  # amount, 100 XLM
        ]

        alice_root_invocation = AuthorizedInvocation(
            contract_id=native_token_contract_id,
            function_name="xfer",
            args=args,
            sub_invocations=[],
        )

        alice_contract_auth = ContractAuth(
            address=None,
            nonce=None,
            root_invocation=alice_root_invocation,
        )

        tx = (
            TransactionBuilder(alice_source, config.network_passphrase)
            .add_time_bounds(0, 0)
            .append_invoke_contract_function_op(
                contract_id=native_token_contract_id,
                function_name="xfer",
                parameters=args,
                auth=[alice_contract_auth],
            )
            .build()
        )

        simulate_transaction_data = config.soroban_server.simulate_transaction(tx)
        print(f"simulated transaction: {simulate_transaction_data}")

        print(f"setting footprint and signing transaction...")
        assert simulate_transaction_data.results is not None
        tx.set_footpoint(simulate_transaction_data.results[0].footprint)
        tx.sign(alice_kp)

        print(f"Signed XDR:\n{tx.to_xdr()}")

        send_transaction_data = config.soroban_server.send_transaction(tx)
        print(f"sent transaction: {send_transaction_data}")

        while True:
            print("waiting for transaction to be confirmed...")
            get_transaction_status_data = config.soroban_server.get_transaction_status(
                send_transaction_data.id
            )
            if get_transaction_status_data.status != TransactionStatus.PENDING:
                break
            time.sleep(3)
        print(f"transaction status: {get_transaction_status_data}")

        if get_transaction_status_data.status == TransactionStatus.SUCCESS:
            result = stellar_xdr.SCVal.from_xdr(get_transaction_status_data.results[0].xdr)  # type: ignore
            print(f"transaction result: {result}")
