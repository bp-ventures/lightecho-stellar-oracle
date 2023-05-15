### BPV - Blockchain Oracle

### BACKGROUND
Price Oracles serve as an essential element in the next-generation Stellar Soroban smart contract system, which leverages the Rust programming language. They are widely applied in lending schemes that incorporate approaches like overcollateralized loans. Decentralized systems require a secure and reliable way to access external data, especially when it comes to financial data that impacts decision-making within the applications (1). Since blockchain networks are typically isolated from the outside world, price oracles act as a bridge between off-chain data and on-chain applications, ensuring accurate and trustworthy information for users and developers. 

Major oracle disruptions could endanger billions of dollars stored in Soroban-based agreements. Recognizing the focused risks is crucial, as the ever-expanding assortment of projects within the system typically hinges on a few price oracles. A breakdown in even one of these oracles might trigger a catastrophic ripple effect throughout the entire ecosystem. As a result, the seamless integration of dependable and secure price oracles is crucial for the success of Stellar Soroban.

We previously developed LightEcho.io, an aggregator that compiles pricing data from various sources, including Decentralized Exchanges (DEXs), Centralized Exchanges (CEXs), Instant Exchanges (ICE), and Peer-to-Peer (P2P) exchanges. It collects data from over 50 sources. This platform showcases Stellar pricing information. 

For this project, we aim to create two distinct types of oracle contracts within the Stellar Soroban ecosystem:
1) An embedded oracle, in which all prices are stored inside the contract data on-chain, and the prices can be obtained at any time by invoking the contract function directly from another contract.
2) A callback-based oracle, in which a price is requested alongside a contract ID for receiving the price later, then a backend aggregator (off-chain) detects the request via getEvents, and invokes the receiver contract, passing the price as a parameter to the function being invoked. Although the idea of a callback-based oracle sounds interesting, there are some limitations we might face, so we haven't decided if/how we'll implement this approach.

The sources of the prices that are fed into those contracts will be decentralized, meaning there will be multiple sources, each one controlled by a different trusted market data providing, company or exchange. It's on the consumer (of the contracts) to decide which price source to rely on when retrieving a price.

In developing an effective pricing mechanism, we have carefully considered several stages in our journey. For on-chain data, our strategy involves gathering data from Stellar Classic (such as the XLM-USDC price). This will be accomplished through an RPC call that computes the current price based on the Liquidity Pool within Stellar Classic. Additionally, we plan to explore the potential of extracting data from Uniswap, further diversifying our data sources and enhancing accuracy.

For the centralized pricing systems we will both investigate using the pricing model from CME(6) and use a hybrid model taking the best of Maker Dao and Cornell University's "Town Crier" model(2).

Our design goals for this project encompass the following key aspects:

-    Data Accuracy: We prioritize providing users with reliable and precise information, which is vital for informed decision-making in the trading landscape.
-    Uptime: Ensuring the system remains highly available is essential; our aim is to achieve five times the standard uptime, offering users uninterrupted access to crucial data.
-    Efficiency: Recognizing the inherent limitations of blockchain data storage, we plan to store only on-chain data for XLM-USD pricing. For the remaining data, we will implement a request-response model, optimizing storage usage while maintaining access to essential information.
-    Diversity: The trading environment lacks a single source of truth. By incorporating multiple oracles and data sources, we empower end users to select a source that aligns with their unique requirements and preferences.
-    No Token: We would prefer the system is to function without the need for a specific token for usage or incentives. Instead, we prefer leveraging XLM as the underlying mechanism to streamline the user experience, and provide incentives.
-    Resistance to Manipulation: To safeguard the integrity of the system, we aim to build robust mechanisms that prevent price manipulation and ensure the authenticity of the data provided, fostering trust and confidence among users. As well as address Information Security concerns (8)
-    Support Stellar's core mission of Remittance to Emerging markets and global financial access

By addressing these design goals, we strive to create a comprehensive, reliable, and user-friendly system on Stellar that caters to the diverse needs of the smart contract and trading ecosystem.


### PILOT:

Embedded Oracle
For our pilot we have taken the developer discussion from Alex and Orbitens (3) and we believe have made it more flexible. While incorporating data structures used in traditional finance (4). You can see the current pilot implementation in the Github repository located [here](https://github.com/bp-ventures/soroban-contracts)

An overview of our modifications to the structure proposed by Alex and Orbitens (3):
-  Base is of type Symbol instead of Address:
   `fn base(env: Env) -> Symbol;`
-  Base will always represent an off-chain currency by their ISO-4217 code, e.g. US Dollar is USD, Euro is EUR, Bitcoin is XBT/BTC (10).
-  We renamed "price" to "rate", for simplifying the semantic of the values. A rate of 10 means that for 1 unit of the base asset, you get 10 units of the quote asset.
- Each rate entry will have the following structure:
  ```
  pub struct RateEntry {
      pub rate: u128,  // unsigned 128-bit integer since it's not possible to have negative rate
      pub decimals: u128,  // indicates how many decimals the rate has
      pub timestamp: u64,  // timestamp in UNIX seconds
  }
  ```
- A decimal rate can be derived from RateEntry by using this formula: `rate_d = rate / (10^decimals)`

- The reason we put the decimals field inside the RateEntry structure (instead of having it as a global value) is due to how rates can be too high or too low in value. For example, some currency pairs like USD-BTC might require us to represent the rate with many decimal places because the rate is too low. In some other cases we might not need so many decimal places to represent a rate. Therefore we chose to keep each RateEntry with its own decimals indicator.

- The source indicates where the rate is coming from. Each source is independent from the other

- A rate can be retrieved by invoking the get_rates() contract function:
  `fn get_rates(env: Env, asset_code: Symbol, asset_issuer: Option<Bytes>) -> Option<Map<u128, RateEntry>>;`

- This function is equivalent to the price() function from the structure proposed by Alex and Orbitlens (3), and the difference is that instead of requiring the asset contract address as a parameter, we require the classic Stellar asset code + asset issuer combination. This is to simplify the usage of the contract, as we intend to support primarily the popular assets from classic Stellar like USDC, BTC, etc, in which their issuers are widely known, but their contract IDs in Soroban are yet undefined (need clarification on whether this still holds true at the moment). The return value is a Map, where each key represents the rate source, and each value contains the RateEntry for that source. Examples of sources: classic Stellar, Binance, Kraken, Coingecko, etc. Each source is represented by an integer, and sources are independently managed in a decentralized way, where specific accounts are authorized to update only a single source or set of sources. Our goal with this is to provide rates coming from many different sources to allow consumers of the contract to be able to choose which sources they trust, and get rates from trusted sources. This get_rate() structure is yet not definitive and is subject to changes.

- Removed assets(), decimals(), resolution(), prices() and lastprice() functions, as we judge them not necessary due to how each RateEntry is independent with it's own decimals and timestamp values, and we won't store more than one entry per rate (the rate will always be the latest), so there's no point having functions that return an array of rates. We might re-add those functions or add other functions with similar purposes depending on the feedback we receive from the community.
- In order to insert or update a rate, we have the set_rate() function:
`fn set_rate(env: Env, asset_code: Symbol, asset_issuer: Option<Bytes>, source: u128, rate: u128, decimals: u128, timestamp: u64)`
- This function requires authorization depending on the value of source. A restricted list of accounts will be able to update rates, and ideally each source can be updated by an independent trusted account.
- In the future we might add a set_rates() function to set many rates at once.

Please feel free to ask questions and provide feedback via the Discussions page located at:
[https://github.com/bp-ventures/lightecho-soroban-oracle](https://github.com/bp-ventures/lightecho-soroban-oracle)


### REFERENCE:

#### 1 - Ethereum Oracles
https://ethereum.org/en/developers/docs/oracles/
  
#### 2 - The Oracle Problem: Unlocking the Potential of Blockchain By Jennifer Yen, Upenn
https://www.cis.upenn.edu/~fbrett/assets/theses/jennifer_yen.pdf

#### 3 - Script3 and Orbitlens discussion
https://groups.google.com/g/stellar-dev/c/KV2XaQzcPPQ

#### 4 - FIX 4.3 Market Data
https://www.onixs.biz/fix-dictionary/4.3/app_g.html

#### 5 - Chainlink whitepaper
https://research.chain.link/whitepaper-v1.pdf

#### 6 - CME BRTI calculation
https://www.cmegroup.com/education/bitcoin/infographic-cme-cf-brr-and-brti.html

#### 7 - OpenZeppelin Oracle discussion
https://blog.openzeppelin.com/secure-smart-contract-guidelines-the-dangers-of-price-oracles/

#### 8 - OpenZepplin Oracle Security
https://github.com/OpenZeppelin/workshops/blob/master/16-dangers-price-oracles-smart-contracts/slides.pdf

#### 9 - Uniswap Oracles (TWAP)
https://docs.uniswap.org/contracts/v2/concepts/core-concepts/oracles

#### 10 - Bitcoin currency code: XBT vs BTC
https://support.kraken.com/hc/en-us/articles/360001206766-Bitcoin-currency-code-XBT-vs-BTC
