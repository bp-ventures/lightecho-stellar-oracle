/**
 * Lightecho Stellar Oracle SDK for the Soroban network.
 */
import StellarSdk from "stellar-sdk";

class OracleClient {
  /**
   * TESTNET values
   */
  static TESTNET_RPC_URL = "https://soroban-testnet.stellar.org";
  static TESTNET_NETWORK_PASSPHRASE = "Test SDF Network ; September 2015";
  static TESTNET_CONTRACT_XLM =
    "CA335SIV2XT6OC3SOUTZBHTX5IXMFO3WYBD3NNVBP37JXX4FXFNF5CI6";
  static TESTNET_CONTRACT_USD = "";

  /**
   * Initializes a new OracleClient instance.
   *
   * @param {string} contractId - The contract ID.
   * @param {string} rpcServerUrl - The RPC server URL.
   * @param {string} networkPassphrase - The network passphrase.
   * @param {string} sourceSecret - The source account secret.
   * @param {object} options - Additional options (default baseFee: 50000).
   */
  constructor(
    contractId,
    rpcServerUrl,
    networkPassphrase,
    sourceSecret,
    options = {
      baseFee: 50000,
      logCallback: null,
    }
  ) {
    this.contract = new StellarSdk.Contract(contractId);
    this.networkPassphrase = networkPassphrase;
    this.rpcServerUrl = rpcServerUrl;
    this.sourceSecret = sourceSecret;
    this.options = options;
    this.contractId = contractId;
  }

  /**
   * Initializes a new OracleClient instance for TESTNET with XLM base.
   *
   * @param {string} network - Stellar network. One of: public, testnet, futurenet.
   * @param {string} sourceSecret - The source account secret to be used in transactions.
   */
  static newInstance(
    network,
    sourceSecret,
    options = {
      baseFee: 50000,
      logCallback: null,
    }
  ) {
    switch (network) {
      case "public":
        throw "Not available yet.";
      case "testnet":
        return new OracleClient(
          OracleClient.TESTNET_CONTRACT_XLM,
          OracleClient.TESTNET_RPC_URL,
          OracleClient.TESTNET_NETWORK_PASSPHRASE,
          sourceSecret,
          options
        );
      case "futurenet":
        throw "Not available yet.";
      default:
        throw "Invalid value for network";
    }
  }

  log(message) {
    if (this.options.logCallback) {
      this.options.logCallback(message);
    }
  }

  /**
   * Parses a Soroban value and returns the corresponding JavaScript value.
   *
   * @param {object} val - The Soroban value to be parsed.
   * @returns {any} - The parsed JavaScript value.
   */
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
    return StellarSdk.Address.account(val["_value"]["_value"]).toString();
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

  /**
   * Submits a transaction to the blockchain oracle contract.
   *
   * @param {object} contractOp - The contract operation to execute.
   * @param {string} signerSecret - The secret of the signer account (default: this.sourceSecret).
   * @returns {any} - The result of the transaction.
   */
  async submitTx(contractOp, signerSecret = this.sourceSecret) {
    const server = new StellarSdk.SorobanRpc.Server(this.rpcServerUrl);
    const keypair = StellarSdk.Keypair.fromSecret(signerSecret);
    this.log(`Loading account ${keypair.publicKey()}`);
    const account = await server.getAccount(keypair.publicKey());
    let transaction = new StellarSdk.TransactionBuilder(account, {
      fee: this.options.baseFee,
      networkPassphrase: this.networkPassphrase,
    })
      .addOperation(contractOp)
      .setTimeout(30)
      .build();
    this.log(`Preparing transaction...`);
    transaction = await server.prepareTransaction(transaction);
    transaction.sign(keypair);
    this.log(`Submitting transaction...`);
    let response = await server.sendTransaction(transaction);
    const hash = response.hash;
    this.log(`Transaction hash: ${hash}`);
    this.log(`Awaiting confirmation...`);
    while (true) {
      response = await server.getTransaction(hash);
      if (response.status !== "NOT_FOUND") {
        break;
      }
      await new Promise((resolve) => setTimeout(resolve, 1000));
    }

    if (response.status === "SUCCESS") {
      this.log(`Transaction successful.`);
      return this.parseScVal(response.returnValue);
    } else {
      this.log(`Transaction failed.`);
      throw response;
    }
  }

  /**
   * Gets the Soroban value representing an asset.
   *
   * @param {string} assetCode - The asset code.
   * @param {string} assetAddress - The Soroban asset address (Token Interface)
   * @returns {object} - The Soroban value representing the asset.
   */
  getAssetEnum(assetCode, assetAddress) {
    if (assetAddress) {
      return StellarSdk.xdr.ScVal.scvVec([
        StellarSdk.xdr.ScVal.scvSymbol(Buffer.from("Stellar", "utf-8")),
        new StellarSdk.Asset(assetCode, assetAddress).contractId(
          this.networkPassphrase
        ),
      ]);
    }
    return StellarSdk.xdr.ScVal.scvVec([
      StellarSdk.xdr.ScVal.scvSymbol(Buffer.from("Other", "utf-8")),
      StellarSdk.xdr.ScVal.scvSymbol(assetCode),
    ]);
  }

  /**
   * Converts a JavaScript number to a Soroban U64 value.
   *
   * @param {number} n - The JavaScript number to convert.
   * @returns {object} - The Soroban U64 value.
   */
  numberToScvU64(n) {
    return StellarSdk.xdr.ScVal.scvU64(
      new StellarSdk.xdr.Uint64(BigInt.asUintN(64, BigInt(n))) // reiterpret as unsigned
    );
  }

  numberToScvI128(n) {
    const v = BigInt(n);
    const hi64 = BigInt.asIntN(64, v >> 64n); // encode top 64 w/ sign bit
    const lo64 = BigInt.asUintN(64, v); // grab btm 64, encode sign

    return StellarSdk.xdr.ScVal.scvI128(
      new StellarSdk.xdr.Int128Parts({
        hi: new StellarSdk.xdr.Int64(hi64),
        lo: new StellarSdk.xdr.Uint64(lo64),
      })
    );
  }

  /**
   * Converts an integer to a decimal string with 18 decimal places.
   *
   * @param {number} integerValue - The integer value to convert.
   * @returns {string} - The decimal string representation.
   */
  convertIntegerToDecimalString(integerValue) {
    const decimalValue = integerValue / Math.pow(10, 18);
    const decimalString = decimalValue.toString();
    return decimalString;
  }

  /**
   * Converts a decimal number to a custom integer with 18 decimal places.
   *
   * @param {number} n - The decimal number to convert.
   * @returns {BigInt} - The custom integer value.
   */
  convertToInt18DecimalPlaces(n) {
    const integerPart = Math.floor(n);
    const decimalPart = (n - integerPart) * 1e18;

    const customInteger = BigInt(
      integerPart.toString() + decimalPart.toFixed(0)
    );
    return customInteger;
  }

  /**
   * Initializes the oracle contract with admin and asset information.
   *
   * @param {string} admin - The admin's public key.
   * @param {string} baseAssetCode - The code of the base asset.
   * @param {string} baseAssetAddress - The Soroban asset address (Token Interface)
   * @param {number} decimals - The number of decimals for the contract.
   * @param {number} resolution - The resolution value.
   * @returns {any} - The result of the transaction.
   */
  async initialize(
    admin,
    baseAssetCode,
    baseAssetAddress,
    decimals,
    resolution
  ) {
    this.log(`Invoking initialize()...`);
    return await this.submitTx(
      this.contract.call(
        "initialize",
        StellarSdk.xdr.ScVal.scvAddress(
          new StellarSdk.Address(admin).toScAddress()
        ),
        this.getAssetEnum(baseAssetCode, baseAssetAddress),
        StellarSdk.xdr.ScVal.scvU32(parseInt(decimals)),
        StellarSdk.xdr.ScVal.scvU32(parseInt(resolution))
      )
    );
  }

  /**
   * Writes a new admin for the contract.
   *
   * @param {string} admin_pubkey - The public key of the new admin.
   * @returns {any} - The result of the transaction.
   */
  async write_admin(admin_pubkey) {
    this.log(`Invoking write_admin()...`);
    return await this.submitTx(
      this.contract.call(
        "write_admin",
        StellarSdk.xdr.ScVal.scvAddress(
          new StellarSdk.Address(admin_pubkey).toScAddress()
        )
      )
    );
  }

  /**
   * Reads the current admin of the contract.
   *
   * @returns {any} - The result of the transaction.
   */
  async read_admin() {
    this.log(`Invoking read_admin()...`);
    return await this.submitTx(this.contract.call("read_admin"));
  }

  /**
   * Retrieves sources associated with the contract.
   *
   * @returns {any} - The result of the transaction.
   */
  async sources() {
    this.log(`Invoking sources()...`);
    return await this.submitTx(this.contract.call("sources"));
  }

  /**
   * Retrieves price records for a specific source and asset.
   *
   * @param {number} source - The source identifier.
   * @param {string} assetCode - The asset code.
   * @param {string} assetAddress - The Soroban asset address (Token Interface)
   * @param {number} records - The number of records to retrieve.
   * @returns {Array} - An array of price records.
   */
  async prices_by_source(source, assetCode, assetAddress, records) {
    this.log(`Invoking prices_by_source()...`);
    let prices = await this.submitTx(
      this.contract.call(
        "prices_by_source",
        StellarSdk.xdr.ScVal.scvU32(parseInt(source)),
        this.getAssetEnum(assetCode, assetAddress),
        StellarSdk.xdr.ScVal.scvU32(parseInt(records))
      )
    );
    let results = [];
    for (let price of prices) {
      results.push({
        price: this.convertIntegerToDecimalString(price["price"]),
        timestamp: price["timestamp"],
      });
    }
    return results;
  }

  /**
   * Retrieves a price record for a specific source, asset, and timestamp.
   *
   * @param {number} source - The source identifier.
   * @param {string} assetCode - The asset code.
   * @param {string} assetAddress - The Soroban asset address (Token Interface)
   * @param {number} timestamp - The timestamp of the price record.
   * @returns {object|null} - The price record or null if not found.
   */
  async price_by_source(source, assetCode, assetAddress, timestamp) {
    this.log(`Invoking price_by_source()...`);
    let price = await this.submitTx(
      this.contract.call(
        "price_by_source",
        StellarSdk.xdr.ScVal.scvU32(parseInt(source)),
        this.getAssetEnum(assetCode, assetAddress),
        this.numberToScvU64(parseInt(timestamp))
      )
    );
    if (price !== null && price !== undefined) {
      price = {
        price: this.convertIntegerToDecimalString(price["price"]),
        timestamp: price["timestamp"],
      };
    }
    return price;
  }

  /**
   * Retrieves the latest price record for a specific source and asset.
   *
   * @param {number} source - The source identifier.
   * @param {string} assetCode - The asset code.
   * @param {string} assetAddress - The Soroban asset address (Token Interface)
   * @returns {object|null} - The latest price record or null if not found.
   */
  async lastprice_by_source(source, assetCode, assetAddress) {
    this.log(`Invoking lastprice_by_source()...`);
    let price = await this.submitTx(
      this.contract.call(
        "lastprice_by_source",
        StellarSdk.xdr.ScVal.scvU32(parseInt(source)),
        this.getAssetEnum(assetCode, assetAddress)
      )
    );
    if (price !== null && price !== undefined) {
      price = {
        price: this.convertIntegerToDecimalString(price["price"]),
        timestamp: price["timestamp"],
      };
    }
    return price;
  }

  /**
   * Retrieves the base asset of the contract.
   *
   * @returns {any} - The result of the transaction.
   */
  async base() {
    this.log(`Invoking base()...`);
    return await this.submitTx(this.contract.call("base"));
  }

  /**
   * Retrieves the list of supported assets by the contract.
   *
   * @returns {any} - The result of the transaction.
   */
  async assets() {
    this.log(`Invoking assets()...`);
    return await this.submitTx(this.contract.call("assets"));
  }

  /**
   * Retrieves the number of decimals for the contract's assets.
   *
   * @returns {any} - The result of the transaction.
   */
  async decimals() {
    this.log(`Invoking decimals()...`);
    return await this.submitTx(this.contract.call("decimals"));
  }

  /**
   * Retrieves the resolution value of the contract.
   *
   * @returns {any} - The result of the transaction.
   */
  async resolution() {
    this.log(`Invoking resolution()...`);
    return await this.submitTx(this.contract.call("resolution"));
  }

  /**
   * Retrieves a price record for a specific asset and timestamp.
   *
   * @param {string} assetCode - The asset code.
   * @param {string} assetAddress - The Soroban asset address (Token Interface)
   * @param {number} timestamp - The timestamp of the price record.
   * @returns {object|null} - The price record or null if not found.
   */
  async price(assetCode, assetAddress, timestamp) {
    this.log(`Invoking price()...`);
    let price = await this.submitTx(
      this.contract.call(
        "price",
        this.getAssetEnum(assetCode, assetAddress),
        this.numberToScvU64(parseInt(timestamp))
      )
    );
    if (price !== null && price !== undefined) {
      price = {
        price: this.convertIntegerToDecimalString(price["price"]),
        timestamp: price["timestamp"],
      };
    }
    return price;
  }

  /**
   * Retrieves price records for a specific asset and number of records.
   *
   * @param {string} assetCode - The asset code.
   * @param {string} assetAddress - The Soroban asset address (Token Interface)
   * @param {number} records - The number of records to retrieve.
   * @returns {Array} - An array of price records.
   */
  async prices(assetCode, assetAddress, records) {
    this.log(`Invoking prices()...`);
    let prices = await this.submitTx(
      this.contract.call(
        "prices",
        this.getAssetEnum(assetCode, assetAddress),
        StellarSdk.xdr.ScVal.scvU32(parseInt(records))
      )
    );
    let results = [];
    for (let price of prices) {
      results.push({
        price: this.convertIntegerToDecimalString(price["price"]),
        timestamp: price["timestamp"],
      });
    }
    return results;
  }

  /**
   * Retrieves the latest price record for a specific asset.
   *
   * @param {string} assetCode - The asset code.
   * @param {string} assetAddress - The Soroban asset address (Token Interface)
   * @returns {object|null} - The latest price record or null if not found.
   */
  async lastprice(assetCode, assetAddress) {
    this.log(`Invoking lastprice()...`);
    let price = await this.submitTx(
      this.contract.call(
        "lastprice",
        this.getAssetEnum(assetCode, assetAddress)
      )
    );
    if (price !== null && price !== undefined) {
      price = {
        price: this.convertIntegerToDecimalString(price["price"]),
        timestamp: price["timestamp"],
      };
    }
    return price;
  }
}
export default OracleClient;
