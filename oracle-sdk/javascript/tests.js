const assert = require("chai").assert;
const OracleClient = require("./lightecho_stellar_oracle"); // Import your JavaScript SDK

const CONTRACT_ID = OracleClient.TESTNET_CONTRACT_XLM;
const SECRET = "SAES4O3NXUE2CPIB7YH3O5ROAONADPZRXOEYFC4JPLNY6STOBM2RYLGH";

describe("OracleClient", () => {
  let client;

  before(() => {
    client = new OracleClient({
      contractId: CONTRACT_ID,
      signerSecret: SECRET,
      network: "testnet",
    });
  });

  it("should initialize", async () => {
    // TODO: Implement this test
  });

  it("should check if has admin", async () => {
    const hasAdmin = await client.hasAdmin();
    assert.isBoolean(hasAdmin);
  });

  it("should write admin", async () => {
    // TODO: Implement this test
  });

  it("should read admin", async () => {
    const admin = await client.readAdmin();
    assert.isString(admin);
  });

  it("should get sources", async () => {
    const sources = await client.sources();
    assert.isArray(sources);
  });

  it("should get price by source", async () => {
    // TODO: Implement this test
  });

  it("should get last price by source", async () => {
    // TODO: Implement this test
  });

  it("should add price", async () => {
    // TODO: Implement this test
  });

  it("should get assets", async () => {
    const assets = await client.assets();
    assert.isArray(assets);
  });

  it("should get decimals", async () => {
    const decimals = await client.decimals();
    assert.isNumber(decimals);
  });

  it("should get resolution", async () => {
    const resolution = await client.resolution();
    assert.isNumber(resolution);
  });

  it("should get price", async () => {
    // TODO: Implement this test
  });

  it("should get prices", async () => {
    // TODO: Implement this test
  });

  it("should get last price", async () => {
    // TODO: Implement this test
  });
});

// Run the tests
//mocha.run();
