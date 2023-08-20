import { program } from "commander";
import SorobanClient from "soroban-client";

const rpcServerUrl = "https://rpc-futurenet.stellar.org:443/";
const sourceSecretKey =
  "SBKEDTLZ6DACGUDTBL7O2LPTEW46KGVZUEXSQGEXCBE5KFKZGDCD4YWW";
const sourceKeypair = SorobanClient.Keypair.fromSecret(sourceSecretKey);
const sourcePublicKey = sourceKeypair.publicKey();
const contractId = "CC5DJV3O2GJSZOGSPJUPCEZ3S2IMVTUM2AHO4R7P3VJSVPKDZWHGRZDN";

const getAssetEnum = (assetCode, assetIssuer) => {
  if (assetIssuer) {
    return SorobanClient.xdr.ScVal.scvVec([
      SorobanClient.xdr.ScVal.scvSymbol(Buffer.from("Stellar", "utf-8")),
      SorobanClient.xdr.ContractId.contractIdFromAsset(
        new SorobanClient.StellarBase.Asset(assetCode, assetIssuer)
      ),
    ]);
  }
  return SorobanClient.xdr.ScVal.scvVec([
    SorobanClient.xdr.ScVal.scvSymbol(Buffer.from("Other", "utf-8")),
    SorobanClient.xdr.ScVal.scvSymbol(assetCode),
  ]);
};

const initialize = async (admin, base, decimals, resolution) => {
  try {
    const server = new SorobanClient.Server(rpcServerUrl);
    const account = await server.getAccount(sourcePublicKey);
    const fee = 100;
    const contract = new SorobanClient.Contract(contractId);
    let transaction = new SorobanClient.TransactionBuilder(account, {
      fee,
      networkPassphrase: SorobanClient.Networks.FUTURENET,
    })
      .addOperation(
        contract.call(
          "initialize",
          SorobanClient.xdr.ScVal.scvAddress(
            new SorobanClient.Address(admin).toScAddress()
          ),
          getAssetEnum(base, ""),
          SorobanClient.xdr.ScVal.scvU32(parseInt(decimals)),
          SorobanClient.xdr.ScVal.scvU32(parseInt(resolution))
        )
      )
      .setTimeout(30)
      .build();

    transaction = await server.prepareTransaction(transaction);
    transaction.sign(sourceKeypair);
    console.log(transaction.toEnvelope().toXDR("base64"));
    let response = await server.sendTransaction(transaction);
    const hash = response.hash;
    console.log(`Transaction hash: ${hash}`);
    while (true) {
      console.log("Awaiting transaction to be confirmed");
      response = await server.getTransaction(hash);
      if (response.status !== "NOT_FOUND") {
        break;
      }
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }
    console.log("Transaction status:", response.status);
    //console.log(JSON.stringify(response));
  } catch (e) {
    console.error(e);
  }
};

program
  .version("1.0.0")
  .description("Lightecho Oracle CLI")
  //.option('-f, --file <filename>', 'Specify a file')
  .command("initialize")
  .description("Call initialize() function of the deployed contract.")
  .argument("<admin>")
  .argument("<base>")
  .argument("<decimals>")
  .argument("<resolution>")
  .action(initialize);

program.parse(process.argv);
