# Privacy Policy: Just One More Bet

**Version 1.0 — effective 2026-10-05**

### The short version

- If you **agree**, at the end of each run the game sends a summary of that run so we can
  **balance the game**. If you don't agree, nothing is sent.
- We **don't** send your name, your email or any account data. The game has no accounts.
- Each summary carries a **random number** that identifies this install of the game, not you.
  Because that number repeats across runs, this data is **not fully anonymous**: it is
  pseudonymous.
- The data is stored with **Supabase**, on servers in the **United States**.
- No ads. We don't sell the data and we don't share it with anyone for advertising.
- You can change your mind anytime in **Settings → Send run statistics**.

### Who we are and how to reach us

We are **Walter Daniel Mejía Palacios** and **Samuel Fernando Calderón Reyes**, the developers of
*Just One More Bet*. We are not a company, just the two people making this game, and we are
jointly responsible for this data.

For any question or request about your data, email either of us; both of us handle requests:

- waltermejia61@hotmail.com
- sfernandocalderon@gmail.com

### What we send

Only if you agreed, the game sends **one row per run** with the following:

| Data | What it is |
|---|---|
| Run ID | A random number created when the run starts, so the same run is never stored twice |
| Install ID (`jugador_id`) | A random number created the first time you agree and stored on your device. It tells us how many runs the same install plays (whether people "come back"). It is not derived from your name, email or anything on your device |
| Run start and end | Time according to your device clock, in UTC |
| Received time | When the row reached our server |
| Time played | Seconds you were in control of the character. The intro, pauses and time with the game minimized don't count |
| Intro | Whether you watched it, skipped it, or it didn't apply |
| Day and casino reached | How far you got |
| How it ended | Debt paid, out of money, short payment or run abandoned |
| Seed | The number that generates your run, used to reproduce it and find bugs |
| Final money and debt paid | In the game's colones (fictional currency) |
| Tables | For each game (slots, roulette, blackjack, horse races): how many times you played, how much you bet and how much you won, in fictional currency |
| Game version | For example, `0.9.0` |
| Platform | Windows, Android, web or other |
| Build type | Release or test build |

**We don't send:** name, email, passwords, contacts, photos, precise location, advertising IDs or
device hardware IDs. Our table has no column for your IP address.

### What our provider (Supabase) logs

Like any internet server, Supabase receives the **IP address** each request comes from and keeps
technical logs with that IP and an **approximate location** (country and city derived from the
IP). On our current plan, those logs are deleted after **1 day**. We don't use those logs to identify anyone
and we don't match them with the run rows.

### What is stored on your device

- **Your choice** (whether you agreed), so we don't ask every run.
- **The install ID**, only after you agree.
- **A queue of pending rows**: with no connection, rows wait on your device (200 at most; when
  full, the oldest are dropped) and are retried when you open the game and at the end of each run.
- **A run in progress**: if you close the game mid-run or it crashes, next time it is sent as
  "abandoned" with whatever you played (only if you agreed).
- **Local statistics** about your runs, which the game uses without sending them anywhere.

In the web version, all of this lives in your browser's storage. If you clear it, or your browser
clears it (for example, in private mode), the game will ask again and, if you agree, create a new
ID.

### Why we use the data

Only to **balance and improve the game**: where people get stuck, whether the debt is too harsh or
too easy, whether a table game pays too much or too little, and whether people come back. We
don't use it for advertising, we don't build profiles to make decisions about you, and we don't
sell it.

### Legal basis

Your **consent**, given when you press "Yes, send". You can withdraw it anytime, as easily as you
gave it, in Settings. Withdrawing doesn't affect what was already sent, but you can ask us to
delete it (see "Your rights").

### When data is sent

At the end of each run (debt paid, out of money, short payment, or abandoning it from the menu),
and when you open the game if something is pending. The game never waits for the network: if
sending fails, you keep playing and it retries later.

### Who receives the data and where it is

- **Supabase** stores the database on our behalf (as a data processor). The project is hosted in
  the **United States** (region `us-west-2`). Supabase uses other providers in turn (for example,
  Amazon Web Services and Cloudflare); their list is at
  https://supabase.com/legal/customer-resources/subprocessor-list.
- Our contract with Supabase includes its data processing agreement, with the European
  Commission's **Standard Contractual Clauses** for data leaving the EU or the UK:
  https://supabase.com/legal/customer-resources/data-processing-addendum.
- Nobody else receives the data. The public key inside the game can only **add** rows: nobody can
  read, change or delete them with it.
- If you download or play *Just One More Bet* on **itch.io**, itch.io handles your data under its
  own policy: https://itch.io/docs/legal/privacy-policy. This policy only covers what our game
  sends.

### How long we keep it

- **Run rows:** **24 months** from when they reach the server, then deleted
  automatically. We may keep **aggregated totals** indefinitely (for example, "average day reached
  in version 0.9"); they carry no ID and can't be linked to anyone.
- **Supabase technical logs (with IP):** 1 day on our current plan.
- **On your device:** until you turn sending off, clear the game's data or uninstall it.

### Your choices

- **Don't agree:** nothing is sent and no ID is created.
- **Turn sending off** in Settings: the pending queue is emptied and nothing else is sent.
  The ID is also deleted from your device; if you turn it back on, a new one is
  created.
- **Uninstall the game** or, on the web, clear the site's data: everything the game stored on your
  device is deleted.

### Your rights

Depending on where you live (for example, the European Union, the European Economic Area or the
United Kingdom), you have the right to **access**, **correct** and **delete** your data, to
**object** to its use, to **restrict** it, to **take it with you** and to **withdraw your
consent**.

Since we don't know who you are, we can only find your data if you give us your **install ID**.
You can see it in Settings, next to the switch, with a button to copy it. Email
either of us with that ID and what you want us to do. We'll reply within **one month**. If you
already deleted the ID from your device, we can't tell which rows were yours; in that case they
are only deleted when the retention period ends.

If you think we mishandled your data, you can complain to the data protection authority in your
country.

### Children

*Just One More Bet* is a game **for adults (18+)**: it has simulated gambling, alcohol and
tobacco. It is not meant for or aimed at minors, and we don't ask for age. If you are a parent or
guardian and believe a minor sent us data, email us with the install ID and we'll delete it.

### Security

Data travels encrypted (HTTPS). The database only accepts adding rows with the game's public key;
reading or deleting them needs a private key that is not in the game or in any published code.
Supabase encrypts stored data.

### Changes to this policy

If we change what the game collects, we'll update this policy **before** releasing that version,
change the date above and announce it in the devlog on the itch.io page. If the change is
significant, the game will ask you again.

Address of this policy: https://just-one-more-bet-web.vercel.app/en/privacy
