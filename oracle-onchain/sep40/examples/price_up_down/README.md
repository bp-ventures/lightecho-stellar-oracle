This is an example Contract that implements a very simple price up/down checks
against an Oracle contract.

This contract contains three functions:
- `initialize`: initialize the contract with an Oracle contract id
- `lastprice`: returns latest asset price directly from the Oracle
- `get_price_up_down`: returns an enum:
  ```
  UpDown {
      up: false,
      down: false,
      equal: false,
  }
  ```
  - `up` will be `true` if current price is above the previous checked price.
  - `down` will be `true` if current price is below the previous checked price.
  - `equal` will be `true` if current price is the same the previous checked price.

  When this function is called, it will fetch the latest price from an Oracle
  and store it internally. The next time this function called, the latest price
  is fetched again and compared to the previously fetched price, and so on.
