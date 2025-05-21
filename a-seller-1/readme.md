# SellerAgent

This agent manages the selling side of a simple negotiation protocol using the Summoner SDK. It:

* Generates a random “min acceptable price” and a matching price decrement.
* Initiates negotiation rounds by waiting for buyer offers.
* Processes buyer messages (`offer_receipt`), adjusting its price down or holding interest.
* Tracks each completed transaction (accept or refuse) in an async-SQLite database, keyed by a UUID transaction ID.
* Computes and prints a running success rate along with the last transaction’s ID.

## 📦 What It Does

* **Negotiation loop** (`negotiation` task):

  * Picks a random `MIN_ACCEPTABLE_PRICE` (60–90) and `PRICE_DECREMENT` (1–5).
  * Starts each round with `current_offer` chosen between `MIN_ACCEPTABLE_PRICE` and 100.
  * Assigns a fresh `transaction_ID` (UUID) for the round.

* **Receive handler** (`offer_receipt` route):

  * Ignores messages not matching the current `transaction_ID` or outside an active round.
  * On `"offer"`, if price ≥ `MIN_ACCEPTABLE_PRICE`, marks `interested`; else lowers its own offer by `PRICE_DECREMENT`.
  * On `"interested"`, if price ≥ `MIN_ACCEPTABLE_PRICE`, moves to `accept`; else to `refuse`.
  * On `"accept"`/`"accept_too"` or `"refuse"`/`"refuse_too"`, records the outcome (1 for accept, 0 for refuse) in SQLite and ends the round.

* **Send handler** (`offer_response` route):

  * Waits 3 s, then sends the current decision (`offer`, `interested`, `accept`, or `refuse`) along with the same `transaction_ID`.

* **History & Stats**:

  * Uses an on-disk `negotiation_history.db` with a `history` table (`id`, `success`, `transaction_id`, `timestamp`).
  * Records exactly one row per completed transaction.
  * Computes success rate (`#accepts ÷ total`) and fetches the last `transaction_id` for display.

## ✏️ How It Works

1. **Startup**

   * `reset_db()` deletes any old database file.
   * `init_db()` creates the `history` table if missing.
   * Spawns the `negotiation` coroutine under a shared `state_lock`.

2. **Negotiation Task**

   * Runs continuously, each iteration:

     * Locks state, randomizes parameters, sets `current_offer` and `transaction_ID`.
     * Prints the new round’s MIN, MAX, and TXID.
     * Spins until `negotiation_active` is set to `False` by a final accept/refuse.

3. **Receiving Buyer Messages**

   * Listens on `offer_receipt`. Expects a JSON dict with `"status"`, `"price"`, and `"TXID"`.
   * Verifies `content["TXID"]` matches the active round’s UUID.
   * Transitions state according to seller logic (≥ `MIN_ACCEPTABLE_PRICE` = interested/accept; else decrease/refuse).
   * On final `"accept_too"`/`"refuse_too"`, calls `add_history()` and `show_statistics()`, then resets the round.

4. **Sending Seller Messages**

   * Every 3 s, locks state to grab `current_offer`, `agreement`, and `transaction_ID`.
   * Returns a JSON dict with `"status"`, `"price"`, and `"TXID"`.

5. **Statistics**

   * `get_statistics()` counts successful vs. total transactions.
   * `get_last_transaction_id()` fetches the most recent `transaction_id`.
   * `show_statistics()` prints the rate and last TXID in cyan.

## ▶️ Running the Demo

You’ll need three terminals:

1. **Terminal 1: Start the Summoner server**

  ```bash
  python server.py
  ```

2. **Terminal 2: Launch SellerAgent**

  ```bash
  python a-seller-1/agents.py
  ```

3. **Terminal 3: Launch BuyerAgent**

  ```bash
  python a-buyer-1/agents.py
  ```

  You will see outputs like:

  ```
  2025-05-20 19:15:00 - SellerAgent - INFO - Connected to server.
  ...
  [SellerAgent] New negotiation started. MIN: 65, MAX: 86, TXID: 92bb582a-15ec-4566-9501-4fcc7fd80e8f
  [Received] {'status': 'offer', 'price': 3, 'TXID': None}
  [SellerAgent] Decreasing price at 82!
  [SellerAgent] Offering price: 82
  [Received] {'status': 'offer', 'price': 4, 'TXID': 92bb582a-15ec-4566-9501-4fcc7fd80e8f}
  [SellerAgent] Decreasing price at 78!
  [SellerAgent] Offering price: 78
  [Received] {'status': 'interested', 'price': 78, 'TXID': 92bb582a-15ec-4566-9501-4fcc7fd80e8f}
  [SellerAgent] Accepting offer at price 78!
  [Received] {'status': 'accept', 'price': 78, 'TXID': 92bb582a-15ec-4566-9501-4fcc7fd80e8f}
  [Received] {'status': 'accept_too', 'price': 78, 'TXID': 92bb582a-15ec-4566-9501-4fcc7fd80e8f}

  [SellerAgent] Negotiation success rate: 36.07% (22 successes / 61 total)  Last TXID: 92bb582a-15ec-4566-9501-4fcc7fd80e8f
  ```

## 🚦 Behavior Summary

| Event                                   | SellerAgent Behavior                                |
| --------------------------------------- | --------------------------------------------------- |
| **New round**                           | Randomize MIN, DEC, starting offer, new TXID        |
| **Receive `"offer"` ≥ MIN**             | `interested` → lock in buyer’s price                |
| **Receive `"offer"` < MIN**             | Decrease own offer by `PRICE_DECREMENT`             |
| **Receive `"interested"` ≥ MIN**        | `accept`                                            |
| **Receive `"interested"` < MIN**        | `refuse`                                            |
| **Final `"accept_too"`/`"refuse_too"`** | Record outcome in DB, print stats, end round        |
| **Send handler**                        | Outputs JSON with status, price, and TXID every 3 s |
| **Stats display**                       | Shows `% success` and last transaction ID in cyan   |

## 💡 Tips

* **TXID matching**: always verify the incoming `"TXID"` before processing to separate rounds safely.
* **Tuning timing**: adjust `await asyncio.sleep(0.2)` in the negotiation spin or `3` s in the send handler for faster/slower pacing.
* **Review history**: inspect `negotiation_history.db` with `sqlite3` to audit every transaction’s ID, timestamp, and outcome.
* **Extensibility**: you can extend the `history` schema with buyer/seller roles or price columns if you need richer analytics.
