var SorobanClient = require("soroban-client");

export default class OracleClient {
  constructor(
    contractId,
    rpcServerUrl,
    networkPassphrase,
    sourceSecret,
    apiUrl,
    options = {
      baseFee: 50000,
    }
  ) {
    this.contract = new SorobanClient.Contract(contractId);
    this.networkPassphrase = networkPassphrase;
    this.rpcServerUrl = rpcServerUrl;
    this.sourceSecret = sourceSecret;
    this.apiUrl = apiUrl;
    this.options = options;
  }

  parseScMap(val) {
    const resultMap = {};
    for (let _value of val["_value"]) {
      const attributes = _value["_attributes"];
      const key = this.parseScVal(attributes["key"]);
      const value = this.parseScVal(attributes["val"]);
      resultMap[key] = value;
    }
    return resultMap;
  }

  parseScSymbol(val) {
    const _value = val["_value"];
    const buf = Buffer.from(_value);
    return buf.toString("utf-8");
  }

  parseScI128(val) {
    const attributes = val["_value"]["_attributes"];
    const hi = attributes["hi"];
    const lo = attributes["lo"];
    const fullInt = (BigInt(hi) << BigInt(32)) + BigInt(lo);
    return parseInt(fullInt.toString());
  }

  parseScU64(val) {
    return parseInt(BigInt(val["_value"]).toString());
  }

  parseScAddressTypeAccount(val) {
    return SorobanClient.StellarBase.Address.account(
      val["_value"]["_value"]
    ).toString();
  }

  parseScVec(val) {
    let vec = [];
    for (let value of val["_value"]) {
      vec.push(this.parseScVal(value));
    }
    return vec;
  }

  parseScU32(val) {
    return parseInt(BigInt(val["_value"]).toString());
  }

  parseScVal(val) {
    switch (val["_switch"]["name"]) {
      case "scvVoid":
        return null;
      case "scvVec":
        return this.parseScVec(val);
      case "scvMap":
        return this.parseScMap(val);
      case "scvSymbol":
        return this.parseScSymbol(val);
      case "scvI128":
        return this.parseScI128(val);
      case "scvU64":
        return this.parseScU64(val);
      case "scvU32":
        return this.parseScU32(val);
      case "scvAddress":
        return this.parseScVal(val["_value"]);
      case "scAddressTypeAccount":
        return this.parseScAddressTypeAccount(val);
      default:
        throw `Unexpected switch name: ${val["_switch"]["name"]}`;
    }
  }

  async submitTx(contractOp, signerSecret = this.sourceSecret) {
    const server = new SorobanClient.Server(this.rpcServerUrl);
    const keypair = SorobanClient.Keypair.fromSecret(signerSecret);
    const account = await server.getAccount(keypair.publicKey());
    let transaction = new SorobanClient.TransactionBuilder(account, {
      fee: this.options.baseFee,
      networkPassphrase: this.networkPassphrase,
    })
      .addOperation(contractOp)
      .setTimeout(30)
      .build();
    transaction = await server.prepareTransaction(transaction);
    transaction.sign(keypair);
    //console.log(`xdr: ${transaction.toEnvelope().toXDR("base64")}`);
    let response = await server.sendTransaction(transaction);
    const hash = response.hash;
    while (true) {
      response = await server.getTransaction(hash);
      if (response.status !== "NOT_FOUND") {
        break;
      }
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }

    if (response.status === "SUCCESS") {
      return this.parseScVal(response.returnValue);
      // We had issues trying to parse the result using SorobanClient,
      // so we call an external API to parse it.
      //let parsedResult = await axios.post(
      //  `${this.apiUrl}/soroban/parse-result-xdr/`,
      //  { xdr: response.resultMetaXdr }
      //);
      //return parsedResult;
    } else {
      throw response;
    }
  }

  getAssetEnum(assetCode, assetIssuer) {
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
  }

  numberToScvU64(n) {
    return SorobanClient.xdr.ScVal.scvU64(
      new SorobanClient.xdr.Uint64(BigInt.asUintN(64, BigInt(n))) // reiterpret as unsigned
    );
  }

  numberToScvI128(n) {
    const v = BigInt(n);
    const hi64 = BigInt.asIntN(64, v >> 64n); // encode top 64 w/ sign bit
    const lo64 = BigInt.asUintN(64, v); // grab btm 64, encode sign

    return SorobanClient.xdr.ScVal.scvI128(
      new SorobanClient.xdr.Int128Parts({
        hi: new SorobanClient.xdr.Int64(hi64),
        lo: new SorobanClient.xdr.Uint64(lo64),
      })
    );
  }

  convertToInt18DecimalPlaces(n) {
    const integerPart = Math.floor(n);
    const decimalPart = (n - integerPart) * 1e18;

    const customInteger = BigInt(
      integerPart.toString() + decimalPart.toFixed(0)
    );
    return customInteger;
  }

  async initialize(
    admin,
    baseAssetCode,
    baseAssetIssuer,
    decimals,
    resolution
  ) {
    return await this.submitTx(
      this.contract.call(
        "initialize",
        SorobanClient.xdr.ScVal.scvAddress(
          new SorobanClient.Address(admin).toScAddress()
        ),
        this.getAssetEnum(baseAssetCode, baseAssetIssuer),
        SorobanClient.xdr.ScVal.scvU32(parseInt(decimals)),
        SorobanClient.xdr.ScVal.scvU32(parseInt(resolution))
      )
    );
  }

  async bump_instance() {
    return await this.submitTx(this.contract.call("bump_instance"));
  }

  async has_admin() {
    //TODO re-test and fix
    return await this.submitTx(this.contract.call("has_admin"));
  }

  async write_admin(admin_pubkey) {
    //TODO test
    return await this.submitTx(
      this.contract.call(
        "write_admin",
        SorobanClient.xdr.ScVal.scvAddress(
          new SorobanClient.Address(admin_pubkey).toScAddress()
        )
      )
    );
  }

  async read_admin() {
    return await this.submitTx(this.contract.call("read_admin"));
  }

  async sources() {
    return await this.submitTx(this.contract.call("sources"));
  }

  async prices_by_source(source, assetCode, assetIssuer, records) {
    return await this.submitTx(
      this.contract.call(
        "prices_by_source",
        SorobanClient.xdr.ScVal.scvU32(parseInt(source)),
        this.getAssetEnum(assetCode, assetIssuer),
        SorobanClient.xdr.ScVal.scvU32(parseInt(records))
      )
    );
  }

  async price_by_source(source, assetCode, assetIssuer, timestamp) {
    return await this.submitTx(
      this.contract.call(
        "price_by_source",
        SorobanClient.xdr.ScVal.scvU32(parseInt(source)),
        this.getAssetEnum(assetCode, assetIssuer),
        this.numberToScvU64(parseInt(timestamp))
      )
    );
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

  async add_price(source, assetCode, assetIssuer, price, timestamp) {
    return await this.submitTx(
      this.contract.call(
        "add_price",
        SorobanClient.xdr.ScVal.scvU32(parseInt(source)),
        this.getAssetEnum(assetCode, assetIssuer),
        this.numberToScvI128(
          this.convertToInt18DecimalPlaces(parseFloat(price))
        ),
        this.numberToScvU64(parseInt(timestamp))
      )
    );
  }

  async remove_prices(sources, assets, start_timestamp, end_timestamp) {
    throw "Not implemented yet";
  }

  async base() {
    return await this.submitTx(this.contract.call("base"));
  }

  async assets() {
    return await this.submitTx(this.contract.call("assets"));
  }

  async decimals() {
    return await this.submitTx(this.contract.call("decimals"));
  }

  async resolution() {
    return await this.submitTx(this.contract.call("resolution"));
  }

  async price(assetCode, assetIssuer, timestamp) {
    return await this.submitTx(
      this.contract.call(
        "prices",
        this.getAssetEnum(assetCode, assetIssuer),
        this.numberToScvU64(parseInt(timestamp))
      )
    );
  }

  async prices(assetCode, assetIssuer, records) {
    await this.submitTx(
      this.contract.call(
        "prices",
        this.getAssetEnum(assetCode, assetIssuer),
        SorobanClient.xdr.ScVal.scvU32(parseInt(records))
      )
    );
  }

  async lastprice(assetCode, assetIssuer) {
    return await this.submitTx(
      this.contract.call("lastprice", this.getAssetEnum(assetCode, assetIssuer))
    );
  }
}
