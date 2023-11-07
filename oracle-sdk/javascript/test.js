import { assert } from "chai";
import OracleClient from "./lightecho_stellar_oracle.js";

const SECRET = "SAES4O3NXUE2CPIB7YH3O5ROAONADPZRXOEYFC4JPLNY6STOBM2RYLGH";

describe("OracleClient", () => {
  let client;

  before(() => {
    client = new OracleClient.newInstance("testnet", SECRET, {
      baseFee: 50000,
    });
  });

  it("should initialize", async () => {
    // TODO: Implement this test
  });

  it("should write admin", async () => {
    // TODO: Implement this test
  });

  it("should read admin", async () => {
    const admin = await client.read_admin();
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
