class OracleClient {
  constructor(
    contractId,
    rpcServerUrl,
    networkPassphrase,
    sourceSecret,
    apiUrl
  ) {
    this.contract = new SorobanClient.Contract(contractId);
    this.networkPassphrase = networkPassphrase;
    this.rpcServerUrl = rpcServerUrl;
    this.sourceSecret = sourceSecret;
    this.apiUrl = apiUrl;
  }

  async submitTx(contractOp, signerSecret = this.sourceSecret) {
    const server = new SorobanClient.Server(this.rpcServerUrl);
    const keypair = SorobanClient.Keypair.fromSecret(signerSecret);
    const account = await server.getAccount(keypair.publicKey());
    let transaction = new SorobanClient.TransactionBuilder(account, {
      fee: 50000,
      networkPassphrase: this.networkPassphrase,
    })
      .addOperation(contractOp)
      .setTimeout(30)
      .build();
    transaction = await server.prepareTransaction(transaction);
    transaction.sign(keypair);
    console.log(`xdr: ${transaction.toEnvelope().toXDR("base64")}`);
    try {
      let response = await server.sendTransaction(transaction);
      const hash = response.hash;
      while (true) {
        response = await server.getTransaction(hash);
        if (response.status !== "NOT_FOUND") {
          break;
        }
        await new Promise((resolve) => setTimeout(resolve, 1000));
      }
      console.log(JSON.stringify(response));
      if (response.status === "SUCCESS") {
        console.log(`resultMetaXdr: ${response.resultMetaXdr}`);
        const horizonTx = `https://horizon-futurenet.stellar.org/transactions/${hash}`;
        console.log(horizonTx);
        // We had issues trying to parse the result using SorobanClient,
        // so we call an external API to parse it.
        let parsedResult = await axios.post(
          `${this.apiUrl}/soroban/parse-result-xdr/`,
          { xdr: response.resultMetaXdr }
        );
        return parsedResult;
      } else {
        console.error(response);
      }
    } catch (e) {
      console.error(e);
    }
  }

  getAssetEnum(assetCode, assetIssuer) {
    if (assetIssuer) {
      return SorobanClient.xdr.ScVal.scvVec([
        SorobanClient.xdr.ScVal.scvSymbol(
          ethereumjs.Buffer.Buffer.from("Stellar", "utf-8")
        ),
        SorobanClient.xdr.ContractId.contractIdFromAsset(
          new SorobanClient.StellarBase.Asset(assetCode, assetIssuer)
        ),
      ]);
    }
    return SorobanClient.xdr.ScVal.scvVec([
      SorobanClient.xdr.ScVal.scvSymbol(
        ethereumjs.Buffer.Buffer.from("Other", "utf-8")
      ),
      SorobanClient.xdr.ScVal.scvSymbol(assetCode),
    ]);
  }

  async lastprice_by_source(source, assetCode, assetIssuer) {
    return await this.submitTx(
      this.contract.call(
        "lastprice_by_source",
        SorobanClient.xdr.ScVal.scvU32(parseInt(source)),
        this.getAssetEnum(assetCode, assetIssuer)
      )
    );
  }

  async lastprice(assetCode, assetIssuer) {
    return await this.submitTx(
      this.contract.call("lastprice", this.getAssetEnum(assetCode, assetIssuer))
    );
  }
}
