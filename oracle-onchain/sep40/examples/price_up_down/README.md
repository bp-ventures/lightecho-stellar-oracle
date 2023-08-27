This is an example Contract that implements a minimalistic loan system.

The loan requires a collateral, which is an amount the borrower must send
and remains reserved by the contract until the loan gets paid, a timeout is reached,
or an exchange rate is reached (uses [Lightecho Oracle](../../contract)) to retrieve the exchange rate).

Summary of the loan flow:

- Borrower checks if loan is available
  - Contract returns the availability and the collateral requirements
- Borrower requests the loan, the request contains the desired amount
  - Contract checks if the borrower meets the requirements and returns a unique memo for the loan
- Borrower sends the collateral and includes the unique memo in the transaction
  - Contract detects the memo and triggers the start of the loan
  - Contract sends the loan amount to the borrower
- Periodically, the contract checks if:
  - Loan has expired
  - Collateral exchange rate has reached a minimum threshold (e.g. collateral
    was USD but the current USD exchange rate has become too low and the loan
    needs to be terminated). Uses [Lightecho Oracle](../../contract)) to retrieve the exchange rate.
