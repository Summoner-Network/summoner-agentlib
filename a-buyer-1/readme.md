# BuyerAgent

This agent drives the purchasing side of a simple negotiation protocol using the Summoner SDK. It:

* Generates a random “max acceptable price” and a matching price increment.
* Initiates negotiation rounds by offering a price (the “buyer offer”).
* Processes seller responses (`offer_response`), adjusting its offer up or down.
* Tracks each completed transaction (accept or refuse) in an async-SQLite database, keyed by a UUID transaction ID.
* Computes and prints a running success rate along with the last transaction’s ID.

## 📦 What It Does

* **Negotiation loop** (`negotiation` task):

  * Picks a random `MAX_ACCEPTABLE_PRICE` (65–80) and `PRICE_INCREMENT` (1–5).
  * Starts each round with `current_offer` chosen between 1 and `MAX_ACCEPTABLE_PRICE`.
  * Assigns a fresh `transaction_ID` (UUID) for the round.

* **Receive handler** (`offer_response` route):

  * Ignores messages not matching the current `transaction_ID`.
  * On `"offer"`, if price ≤ `MAX_ACCEPTABLE_PRICE`, marks `interested`; else raises its own offer.
  * On `"interested"`, if price ≤ `MAX_ACCEPTABLE_PRICE`, moves to `accept`; else to `refuse`.
  * On `"accept"`/`"accept_too"` or `"refuse"`/`"refuse_too"`, records the outcome (1 for accept, 0 for refuse) in SQLite and ends the round.

* **Send handler** (`buyer_offer` route):

  * Waits 2 s, then sends the current decision (`offer`, `interested`, `accept`, or `refuse`) along with the same `transaction_ID`.

* **History & Stats**:

  * Uses an on-disk `negotiation_history.db` with a `history` table (`id`, `success`, `transaction_id`, `timestamp`).
  * Records exactly one row per completed transaction.
  * Computes success rate (`#accepts / total`) and fetches the last `transaction_id` for display.

## ✏️ How It Works

1. **Startup**

   * `reset_db()` deletes any old database.
   * `init_db()` recreates the `history` table if missing.
   * Spawns the `negotiation` coroutine under a shared `state_lock`.

2. **Negotiation Task**

   * Runs forever, each iteration:

     * Locks state, randomizes parameters, sets `current_offer` and `transaction_ID`.
     * Prints the new round’s MIN, MAX, and TXID.
     * Spins until `negotiation_active` becomes `False` (via final accept/refuse).

3. **Receiving Seller Messages**

   * Each message on `offer_response` must include a matching `"TXID"`.
   * State transitions mirror buyer intent (≤ `MAX_ACCEPTABLE_PRICE` = good; ≥ = too expensive).
   * On final accept/refuse, calls `add_history()` with `(success, transaction_ID)`.

4. **Sending Buyer Messages**

   * Every 2 s, locks state to grab `current_offer`, `agreement`, and `transaction_ID`.
   * Returns a JSON dict with `"status"`, `"price"`, and `"TXID"`.

5. **Statistics**

   * `get_statistics()` runs two SQLite queries to count successes and total.
   * `get_last_transaction_id()` fetches the most recent `transaction_id`.
   * `show_statistics()` prints the rate and last TXID in cyan.

## ▶️ Running the Demo

You will need three terminals:

1. **Terminal 1: Start the Summoner server**

  ```bash
  python server.py
  ```

2. **Terminal 2: Launch BuyerAgent**

  ```bash
  python a-buyer-1/agents.py
  ```

3. **Terminal 3: Launch SellerAgent**

  ```bash
  python a-seller-1/agents.py
  ```

  You will see outputs like:

  ```
  2025-05-20 19:10:00 - BuyerAgent - INFO - Connected to server.
  ...
  [BuyerAgent] New negotiation started. MIN: 3, MAX: 78, TXID: None
  [BuyerAgent] Offering price: 3
  [Received] {'status': 'offer', 'price': 82, 'TXID': 92bb582a-15ec-4566-9501-4fcc7fd80e8f}
  [BuyerAgent] Increasing price at 4!
  [BuyerAgent] Offering price: 4
  [Received] {'status': 'offer', 'price': 78, 'TXID': 92bb582a-15ec-4566-9501-4fcc7fd80e8f}
  [BuyerAgent] Interested in offer at price 78!
  [BuyerAgent] Interested in offer: 78
  [Received] {'status': 'accept', 'price': 78, 'TXID': 92bb582a-15ec-4566-9501-4fcc7fd80e8f}

  [BuyerAgent] Negotiation success rate: 36.07% (22 successes / 61 total)  Last TXID: 92bb582a-15ec-4566-9501-4fcc7fd80e8f
  [BuyerAgent] Accepted offer: 78
  ```

## 🚦 Behavior Summary

| Event                                   | BuyerAgent Behavior                                       |
| --------------------------------------- | --------------------------------------------------------- |
| **New round**                           | Randomize MAX, INCR, starting offer, new TXID             |
| **Receive `"offer"` ≤ MAX**             | `interested` → lock in price                              |
| **Receive `"offer"` > MAX**             | Increase own offer by `PRICE_INCREMENT`                   |
| **Receive `"interested"` ≤ MAX**        | `accept`                                                  |
| **Receive `"interested"` > MAX**        | `refuse`                                                  |
| **Final `"accept_too"`/`"refuse_too"`** | Record outcome in DB, print stats, end round              |
| **Send handler**                        | Outputs JSON with status, price, and TXID every 2 s       |
| **Stats display**                       | Shows `% success` and last transaction ID in the terminal |

## 💡 Tips

* **Ensuring consistency**: always match on `"TXID"` before processing to avoid cross-round contamination.
* **Adjust timing**: modify the `await asyncio.sleep(2)` in your send handler to throttle faster or slower.
* **Inspect full history**: open `negotiation_history.db` with `sqlite3` or a GUI to see all past transactions.
* **Batch stats**: you could extend `get_statistics()` to include per-UUID breakdowns or timestamps.
