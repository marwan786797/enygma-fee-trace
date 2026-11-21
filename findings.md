# What does a private payment on a public blockchain actually cost? I traced Rayls Enygma Public fees to the wei

> **Testnet pilot.** Enygma Public is a testnet pilot. The Rayls team says the whole setup is experimental, and the pricing model, the RLS rate, the 15% commission and the test addresses will most likely change before mainnet (Alex, Rayls team, reply on r/Rayls, 20 Nov 2026: https://www.reddit.com/r/Rayls/s/EtnvbYGAQ9). Everything below describes how the pilot works today, not mainnet.

Short answer (testnet, 20 Nov 2026): a private RLS payment on Enygma Public costs a flat **4.416 test RLS** in gas, paid from shielded RLS. Registering costs about **7.2 RLS** once, shielding about **3.53 RLS** and unshielding about **4.53 RLS**; with USDr the forwarder fee is about 3.83 RLS to shield and 4.76 RLS to unshield plus **0.25% of the amount in USDr**. Creating an invite from a single shielded note costs 4.416 RLS and claiming it costs 12.696 RLS, taken out of the invite. Every fee is 100 parts gas plus 15 parts commission, and I matched the 15 parts onchain to the wei for all 14 of my own RLS fee steps (plus both 0.25% USDr fees) and for 375 of the 378 public forwarder fees since the current fee version went live on 9 Nov.
All numbers are testnet pilot numbers in test RLS, which has no value, at a fixed test price. No USD figures are claimed, and none of it is a mainnet cost.

Status: hands-on run complete on 20 Nov 2026 with three throwaway accounts: register, shield, private send and unshield in RLS; shield and unshield in USDr with the 0.25% fee; invite create and invite claim. One step did not finish: registering the invited account (see 2.1, notes).

---

## 1. Documented (Rayls' own published policies and docs)
| Policy | Rayls source |
|---|---|
| Each Enygma Public gas fee includes a 15% commission to the Rayls Foundation; shielding or unshielding USDr also costs 0.25% of the amount; the relayer collects fees and pays the Foundation's share once each tx is mined; the contracts take no fee. (On the testnet pilot the receiving address is a team test wallet, per the team; section 4) | https://docs.rayls.com/docs/how-enygma-public-works (section "Gas and fees") |
| The relayer pays the chain gas for every Enygma Public tx and charges the account in RLS; shielded payments always pay from shielded RLS | https://docs.rayls.com/docs/how-enygma-public-works |
| Every Enygma deployment must use RLS as its fee token | https://github.com/raylsnetwork/Enygma/blob/main/USAGE-POLICY.md |
| 50% of RLS from chain fees is sent to be burned on Ethereum, 50% to validators | https://docs.rayls.com/docs/public-chain-tokenomics |
| Since April 2026 the Foundation also burns 10% of its monthly unlocked supply | https://www.rayls.com/blog/rayls-tokenomics-a-united-tradfi-defi-economy |
| Foundation treasury schedule (50% of supply, linear unlock over 48 months) | https://www.rayls.com/blog/how-the-rayls-foundation-uses-treasury-funds |
| Testnet: wallet, faucet, chain ID 7295799, Rayls is the auditor | https://docs.rayls.com/docs/try-enygma-public-on-testnet |
| What the public, relayer and auditor see | https://docs.rayls.com/docs/enygma-public-who-sees-what |

Context only: the 50% chain-fee burn (now also read directly from mainnet, see 2.5) and the Foundation unlock burn are Rayls policies about the chain and the treasury. This pack does not test them, it tests the Enygma Public fee and its 15% commission.

## 2. Independently verified (I did it or recomputed it from onchain data)

### 2.1 My own run, step by step (throwaway testnet accounts made on the box)
Accounts: A `0x4f1aa6CB2C8932583F2844a855fB057C589F23E9` (@railfeetrace1), B `0x9d42151e47511d72DbBDD54824053a88F343d3e0` (@railfeetrace2), C `0xD0a85b7571000c6F8dC89699BBCD69862F343C7d` (@railfeetrace3, joined through B's invite). All three are normal EOA wallets with throwaway keys; no personal wallet was used.

| # | Step | Tx | Time UTC / IST | Fee paid (RLS) | App quote = paid | 15% payout (RLS), separate tx | Formula = paid |
|---|---|---|---|---|---|---|---|
| 1 | Faucet 50 RLS to A | [0xd2dd…12fd](https://testnet-explorer.rayls.com/tx/0xd2dda180d431c7f354e4cfc7f13611f881ba7fa0701ac17949fb2ae71a0612fd) | 09:14:18 UTC / 2:44:18 PM IST | | | | |
| 2 | Faucet 50 RLS to B | [0x9589…4639](https://testnet-explorer.rayls.com/tx/0x958989528701cb4b46cf7f6e212459f24dbba6cac0c8fa010bac1c819bbf4639) | 09:14:22 UTC / 2:44:22 PM IST | | | | |
| 3 | A registers | [0x150f…1ae3](https://testnet-explorer.rayls.com/tx/0x150f72f03097bea38cd561dd7a218f020e75704c3c8461b6827dec93d8a11ae3) | 09:20:44 UTC / 2:50:44 PM IST | 7.20007272 | yes | 0.93913992 [0xd57b…1c2c](https://testnet-explorer.rayls.com/tx/0xd57b3418ea64f405c381c14aded2ec2e9aed428d464c9b5f427119e856be1c2c) (+4 s) | yes |
| 4 | A shields 20 RLS (gas from public RLS) | [0x7f40…33c5](https://testnet-explorer.rayls.com/tx/0x7f40bd66f847847a14bcbfa0920a892d22124a23f98147957dc63c5913ed33c5) | 09:23:52 UTC / 2:53:52 PM IST | 3.52596348 | yes | 0.45990828 [0xcd01…8641](https://testnet-explorer.rayls.com/tx/0xcd015acccf7d9373ff1be8a3ec7c6fa005f1d247f7aa044e5fe937cc0ed98641) | yes |
| 5 | B registers | [0xdf23…f19e](https://testnet-explorer.rayls.com/tx/0xdf23fa21962a96cba37b0ca8e3853493d0a1fa6032d54b52ade26ec7902bf19e) | 09:26:24 UTC / 2:56:24 PM IST | 7.20007272 | yes | 0.93913992 [0x8d63…7146](https://testnet-explorer.rayls.com/tx/0x8d63915db37ae1d93eae2d4f8ecccf0ec6bccd17e6707426fa44a49936a47146) | yes |
| 6 | A pays B 5 RLS privately | [0xcf03…760b](https://testnet-explorer.rayls.com/tx/0xcf03bec70572a7e00f1c7fa0edd578791a3ab32b6ec8f660cde4f21a1bc7760b) | 09:28:50 UTC / 2:58:50 PM IST | 4.416 (shielded) | yes | 0.576 [0x4b33…7772](https://testnet-explorer.rayls.com/tx/0x4b336e05cfe3d7bcc4d7c0b0fef7ab28942b357e6132b587413e6d121a567772) | yes (flat) |
| 7 | A unshields 3 RLS to itself | [0x32eb…c159](https://testnet-explorer.rayls.com/tx/0x32ebfef8963c9af737c77597ea79f5fd2ebce62cd35c754e052be0846e06c159) | 09:30:34 UTC / 3:00:34 PM IST | 4.52841756 | yes | 0.59066316 [0x71d2…5150](https://testnet-explorer.rayls.com/tx/0x71d274d10ab2085e9b33f3d16e3a2be34bb3a4f6d48816f475d2302080845150) | yes |
| 8 | B shields 25 RLS (gas from public RLS) | [0x080e…4142](https://testnet-explorer.rayls.com/tx/0x080ede8a21709093e2ab4ec82e4a0f48e164d3156c4f40216b0b9bf78bbb4142) | 09:32:16 UTC / 3:02:16 PM IST | 3.52596348 | yes | 0.45990828 [0x95a1…d3c6](https://testnet-explorer.rayls.com/tx/0x95a1bf3dd07bcb85b44c33ae3f7f52f7c61f607635e84113b23d3ffd71aad3c6) | yes |
| 9 | B shields 5 RLS (gas from shielded RLS) | [0x669b…1bc3](https://testnet-explorer.rayls.com/tx/0x669b2b59a64debf80262ba21a01f7f50b3a783e35b4821163388354795271bc3) | 09:33:46 UTC / 3:03:46 PM IST | 7.38972336 (shielded) | yes | 0.96387696 [0x2bc3…941d](https://testnet-explorer.rayls.com/tx/0x2bc3e3384404348fe12debccbb116fecd9dabbfe21e3cd7823f471a6fc00941d) | yes |
| 10 | A pays B 3 RLS privately | [0x404a…efb0](https://testnet-explorer.rayls.com/tx/0x404af8ae6776de39a7f2621a9f8d0091b5bdeed4ce916ebfa7bff0ab908defb0) | 09:35:04 UTC / 3:05:04 PM IST | 4.416 (shielded) | yes | 0.576 [0x55ef…2158](https://testnet-explorer.rayls.com/tx/0x55ef82fe61a67f338ac63196753fcf5dde740b6ad2c6ba876db7d85b83af2158) | yes (flat) |
| 11 | B shields 5 RLS (gas from public RLS) | [0xef31…c5c6](https://testnet-explorer.rayls.com/tx/0xef3173e279adfcda2ee61b270d4f46f8843a9dc092704608f41c32d76b71c5c6) | 09:36:26 UTC / 3:06:26 PM IST | 3.52580064 | yes | 0.45988704 [0xef2d…d1f2](https://testnet-explorer.rayls.com/tx/0xef2d6036ab96847619e3b51f1026c031d8115d2feae9a9d63d60498e5dd3f1d2) | yes |
| 12 | Faucet (reopened) 250 shielded RLS to B, one note | [0x8a33…3919](https://testnet-explorer.rayls.com/tx/0x8a3387e2c07e86b049c4426b36d4ea6f54fb3eeaa76eec26bbb643f2e68b3919) | 11:14:41 UTC / 4:44:41 PM IST | | | | |
| 13 | Faucet (reopened) 10 USDr to A | [0xc034…8ce4](https://testnet-explorer.rayls.com/tx/0xc034dd85c1cbc4025cd6adb4e43657269acd857eb7f28f312e1ca1df87418ce4) | 11:14:45 UTC / 4:44:45 PM IST | | | | |
| 14 | A shields 4 USDr (gas from public RLS) | [0x732f…e8c6](https://testnet-explorer.rayls.com/tx/0x732f75d1fc8cccc6fb0fcc2d79632f40d4d13935eb85bfabf66733eafda9e8c6) | 11:16:32 UTC / 4:46:32 PM IST | 3.8329638 | yes | 0.4999518 [0xf1fc…3127](https://testnet-explorer.rayls.com/tx/0xf1fc73238fecb68b2f1b2e45375f608921bb4e4e236b6660d7f108430d803127) (+5 s) | yes (+100,000 token-fee gas) |
| 15 | 0.25% token fee on step 14, A to `0x71AF…8B95` | [0x60db…a706](https://testnet-explorer.rayls.com/tx/0x60db7c585a66aad2e06ece47d09d74f764522f4373e4bbd33b36c601bf41a706) | 11:16:36 UTC / 4:46:36 PM IST | 0.01 USDr | | | yes: ceil(4 x 0.25%) = 0.01 |
| 16 | A unshields 2 USDr to itself (gas from public RLS) | [0xfdaa…e202](https://testnet-explorer.rayls.com/tx/0xfdaa7706b311a027e937003d49d89a041c086bf1bd5256de66da12c87141e202) | 11:21:56 UTC / 4:51:56 PM IST | 4.75776528 | yes | 0.62057808 [0xe240…fd11](https://testnet-explorer.rayls.com/tx/0xe2400171258c3bc39e80e7e5bd531e9be7bfe46095a5e6fa603fe6e7e77dfd11) (+4 s) | yes (+100,000 token-fee gas) |
| 17 | 0.25% token fee on step 16, A to `0x71AF…8B95` | [0xc221…009e](https://testnet-explorer.rayls.com/tx/0xc2211c8322f30275dddbc9dc0d3dcdaf56e2c377d7f2147969524de8f736009e) | 11:22:00 UTC / 4:52:00 PM IST | 0.005 USDr | | | yes: ceil(2 x 0.25%) = 0.005 |
| 18 | B creates a 30 RLS invite (private, one note) | [0x116e…d7b4](https://testnet-explorer.rayls.com/tx/0x116ead0d6b4dd02fe7e74a8719ffd5bb8e04a26170d616a779379e06363db7d4) | 11:23:38 UTC / 4:53:38 PM IST | 4.416 (shielded) | yes | 0.576 [0xf826…70d4](https://testnet-explorer.rayls.com/tx/0xf826b63dab7ee8fce7b210ba82867d790282056210ba24490482bf52b51b70d4) (+4 s) | yes (flat 1.6M gas) |
| 19 | C claims the invite (fee taken out of the 30 RLS) | [0xbb2c…1a08](https://testnet-explorer.rayls.com/tx/0xbb2c67f40360a36dc6f2c3827e1d2ac63725578fea94208ef064739aefaf1a08) | 11:27:28 UTC / 4:57:28 PM IST | 12.696 (shielded) | yes | 1.656 [0xb018…dda8](https://testnet-explorer.rayls.com/tx/0xb018c296a547d4ef27acf59eae323934f6bc4be805f57bbb016687dffb28dda8) (+5 s) | yes (flat 4.6M gas) |
| 20 | B pays A 5 RLS privately (gas from shielded RLS), recorded for the proof video | [0x39d9…da94](https://testnet-explorer.rayls.com/tx/0x39d9f8d70d908ae11fb8e6818e93b8bf052a1fff47afe49b992443d852d4da94) | 11:46:39 UTC / 5:16:39 PM IST | 4.416 (shielded) | yes | 0.576 [0x32d0…8e2c](https://testnet-explorer.rayls.com/tx/0x32d0873328a58f13d644d5c983e5e699f4b49ca7bf71989ec372323856a88e2c) (+4 s) | yes (flat 1.6M gas) |
All on 20 Nov 2026. Full numbers per step (gas used, gas price, chain gas the relayer paid in USDr, calldata size, formula line): `evidence/hands_on_steps.json` / `.md`. Screens of each quote and result: `evidence/screens/` (A_14 to A_18 USDr, B_06 invite, C_01 to C_06 claim).

Notes on the new steps (run 11:14 to 11:35 UTC / 4:44 to 5:05 PM IST):
- USDr shield and unshield: the RLS gas fee matches the formula with the extra 100,000 gas the wallet adds when a token fee is attached. The 0.25% is not inside the shield tx: about 4 s later the relayer sends a separate tx (selector `0x284854e5` to the USDr precompile `0x…0400`) that moves exactly ceil(amount x 25/10,000) USDr from A to `0x71AF…8B95`, the same pattern as the 121 historical token fees (2.3). In the shield tx the USDr goes A to `0x74a6…4524` (an address with no code, role not documented) and on to the shared vault in the same tx.
- USDr unshield: the first two tries stopped in the app with "couldn't read the vault's full history… Nothing was sent" (relayer 500s). Nothing went onchain. After a fresh login the third try went through. That is a good safety behavior: the wallet would not build the proof until it had the full history.
- Invite: with one 250 RLS faucet note, creating the invite cost the flat 4.416 RLS (1.6M gas), not the 8.28 RLS (3.0M gas) the app showed earlier when it had to combine notes. The claim fee of 12.696 RLS = 4.6M gas x 2.4e12 x 1.15 (app: 11.04 gas + 1.66 commission). C received 17.304 RLS privately. Both 15% payouts landed 4 to 5 s later, to the wei.
- Step 20 (11:46 UTC / 5:16 PM IST) is one more private payment, B to A, recorded at 2x screen scale for the proof video. The relayer `/private-quote` response in `evidence/browser_B.log` gives `"fee":"4416000000000000000"` (4.416 RLS); the app screen rounds it to 4.42 = 3.84 gas + 0.58. On the explorer the tx is sent by the relayer `0xa5f0…0Ac8`, value 0, no token transfer listed; the 0.576 payout followed 4 s later.
- Registering C (the last invite step, "Paid by the invite"): the relayer `/quote` returned `sponsored: true, fee 0` (gas 2,404,421), but `/relay` answered `fee-too-low` ("The fee is below 7199992680000000000 RLS wei. Get a new quote."). A fresh quote then asked for 7.20 RLS from public RLS (6.26 gas + 0.94 commission, same formula as steps 3 and 5). C holds only shielded RLS, so the button stayed disabled and no registration tx was sent. This is a pilot behavior worth asking about, see section 5. Screens: `C_05_registered.png`, `C_06_registered.png`; relayer request/response: `evidence/browser_C.log`.

What each column means and how it was proven:
- **Fee paid**: for public-gas steps it is the `fee` field of the `Relayed` event the gas forwarder emits, read from the tx receipt [onchain]. For private payments and shielded-gas steps the fee is a shielded note, so it is not visible onchain by design; the number is the relayer's response to the wallet + the app screen [app UI / relayer API], then checked through the public 15% payout (fee x 15/115 must equal the payout to the wei, and it does).
- **App quote = paid**: the quote the relayer gave the wallet (`/quote`, saved in `evidence/browser_*.log`) equals the onchain fee [relayer API vs onchain]. The first screen shows "up to" (a bound from `/gas-quote`); the exact quote is lower and is what is charged.
- **15% payout**: an RLS `Transfer` from the relayer `0xa5f0…0Ac8` to `0x71AF…8B95` in a later tx, about 4 s after [onchain]. Its value equals floor(fee x 15 / 115) exactly [calculation].
- **Formula = paid**: I recomputed the fee from the signed request in the tx input (`req.gas` + calldata length) with the formula shipped in the wallet code, and it equals the fee to the wei [calculation from onchain input + app code].

### 2.2 The fee formula (from the live wallet code, matched against onchain)
The public wallet bundle (live now: https://enygma-testnet.rayls.com/assets/index-DlzVF1v6.js, sha256 ced27fe6df814a0b897c4c328193f4e8ec9aa3c82ad8f30492cb283012a1989f, checked 20 Nov 2026 ~11:40 UTC / 5:10 PM IST; the app was updated during the day, and the earlier build index-Nw3AggQS.js that my morning run used is saved in `evidence/wallet_bundle/` with identical fee constants and functions) contains the relayer's fee code:
- request gas = estimate x 1.2 + 20,000
- priced gas = request gas + 150,000 + 16 x (calldata bytes + 700) (+100,000 when a 0.25% token fee is attached)
- fee (RLS wei) = priced gas x rlsPerGas x 115 / 100, with rlsPerGas = 2,400,000,000,000 (relayer `/info`, testnet), that is 0.0000024 RLS per gas
- commission = fee x 15 / 115 (rounded down)
- private payment in RLS: flat 1,600,000 gas = **4.416 RLS**; a private payment that pays gas with a separate RLS note (other token, or an invite that has to combine notes): 3,000,000 gas = **8.28 RLS** (my invite from a single note cost the flat 4.416, step 18); invite claim: flat 4,600,000 gas = **12.696 RLS** out of the invite (step 19); paying a forwarder request from shielded RLS adds 1,400,000 gas
- token fee = ceil(amount x 25 / 10,000) (0.25%)
Example, step 3: (2,404,450 + 150,000 + 16 x (2,692 + 700)) = 2,608,722 gas x 0.0000024 x 1.15 = 7.20007272 RLS. Paid onchain: 7.20007272. Commission: 0.93913992 = 7.20007272 x 15/115.

### 2.3 Every forwarder fee since launch (`evidence/fees_history.csv`, snapshot block 24,667,602 = 20 Nov 2026 09:41:12 UTC / 3:11 PM IST)
- 715 `Relayed` events across both gas forwarders (474 current, 241 earlier): 528 paid a fee, 187 were sponsored (fee 0).
- Current fee version (from 9 Nov 2026 16:04 UTC): **378 paid fees; 375 have a separate payout of exactly fee x 15/115**, median 4 s after. 241.39751436 RLS of commission matched to 1,862.26140468 RLS of fees.
- Formula check on the same 378: 321 reproduce exactly, 49 reproduce exactly with the +100,000 token-fee term, 8 are +96.5k to +97.1k gas (the code's separate approval-gas term, which I did not reproduce gas-for-gas).
- On top, 341 payouts have no public fee tx: they belong to fees paid privately from shielded RLS. The two most common values are 1.08 RLS (= 8.28 x 15/115, 101 times) and 0.576 RLS (= 4.416 x 15/115, 69 times), which are exactly the flat fees above.
- 0.25% USDr fee (`evidence/token_fee_check.csv`): all 121 USDr fee transfers into `0x71AF…8B95` since 27 Oct equal ceil(amount x 0.25%) of a matching USDr move by the same account: 30 shields, 30 unshields, 61 public USDr sends.
- Chart: `charts/daily_fee_and_commission.png`, `charts/median_fee_by_action.png`, `charts/hands_on_fee_split.png`.

### 2.4 Address types (explorer API, `evidence/address_types.md`)
| Address | Type | Role (source) |
|---|---|---|
| 0xa5f0C684EB49866a9f62f901Cd85f98a19DA0Ac8 | EOA (normal wallet) | Relayer (relayer `/info`; sender of every relayed tx) |
| 0x71AF09966CBED4434ccA97c40Fa38B8083548B95 | EOA (normal wallet) | Receives the 15% commission + 0.25% fee on testnet (relayer `/info` "treasury"; app config also lists it as auditor). Rayls team: a team test wallet standing in for the treasury and the auditor on testnet, not a Rayls Foundation address; mainnet will use a different address |
| 0x12B6640048DEB2e8fFDa4Bc10Bb2a640B70eCA6d | Contract, verified RlsGasForwarder | Gas forwarder (current) |
| 0x753cc3Abe9A1c49536ee74F1f424fCF693AAB5DD | Contract, verified RlsGasForwarder | Gas forwarder (earlier) |
| 0xA473291FFb33e2276F364fAE169f03c4406719e9 | EIP-1967 proxy -> UserRegistry | Registry |
| 0x9C5Ad5e5Ea5b5910E7fD1E1CC7b70ce0e4bF06c2 | EIP-1967 proxy -> SharedVault | Shared vault |
| 0x97b5d78dbe06d8c8c843f87b5aa2d8587b890795 | Contract Erc20CoinVault | RLS vault |
| 0x1edb224cf8637f92efadaf47ef9e70c044d75584 | Contract Erc20CoinVault | USDr vault |
| 0xBf099175a241194C38E977735D59CCb22596d775 | Contract OwnerMultisig, custom multisig (not a Safe), threshold 2 | Owner multisig (docs) |
| 0x07e17E17e17E17e17e17e17E17E17E17E17e17EA | EIP-1967 proxy | RLS token on testnet |
| 0x07E17E17e17E17e17E17e17e17e17e17E17E17E3 (mainnet) | EIP-1967 proxy -> verified FeeAggregator 0x07e1…17e4 | Chain fee split config (getConfig) |
| 0x0000000000000000000000000000000000000400 | Precompile (no real bytecode), shown as ERC-20 "USD Rayls" | USDr gas token |

### 2.5 Mainnet chain fee split, read directly from the FeeAggregator
- Address: [0x07E17E17e17E17e17E17e17e17e17e17E17E17E3](https://explorer.rayls.com/address/0x07E17E17e17E17e17E17e17e17e17e17E17E17E3), Rayls mainnet (chain id 72957). Type: EIP-1967 proxy (contract, not a wallet); implementation slot points to [0x07e17e17E17e17e17E17E17E17e17e17e17E17e4](https://explorer.rayls.com/address/0x07e17e17E17e17e17E17E17E17e17e17e17E17e4), verified as `FeeAggregator`. Full address taken from the explorer; it matches the team's 0x07E1…17e3.
- `cast call 0x07E17E17e17E17e17E17e17e17e17e17E17E17E3 "getConfig()" --rpc-url https://mainnet-rpc.rayls.com --block 14858726`
- Block 14,858,726 = 20 Nov 2026 10:59:20 UTC / 4:29:20 PM IST.
- Raw: `0x…1388 0x…0000 0x…1388` → decoded `(validatorPoolBps 5000, ecosystemBps 0, burnBps 5000)` = 50% validators, 0% ecosystem, 50% burn. Output saved in `evidence/fee_split_mainnet.txt`; rerun with `scripts/check_fee_split.sh 14858726`.
- Scope: this is the split of chain gas fees (paid in USDr). The Enygma 15% commission is a separate RLS fee and is not part of it.

### 2.6 Fresh out of sample check (added 20 Nov 2026, about 7 PM IST)
Script: `scripts/fresh_check.py`. Reads nothing saved: only the public RPC https://testnet-rpc.rayls.com (eth_getLogs, eth_getTransactionByHash, eth_getBlockByNumber).
- Window: blocks 24,667,603 to 24,692,010 (20 Nov 2026 09:41:14 UTC to 13:24:52 UTC / 3:11 PM to 6:54:52 PM IST), i.e. every forwarder fee after the history snapshot block 24,667,602.
- 18 `Relayed` events on the current forwarder 0x12B6…CA6d. 2 have fee 0 (sponsored, nothing to check: 0x814a8bfbc00dab9c79fafb47af3aaa2b092ebf0d6a985b4cbc3f558990377bad, 0x399762a5eda19ba31e8c2a5d5cb5280ab4fc781b4dd5a571dac94dbefcda06aa). 16 paid fees, 14 of them from accounts that are not my test accounts (my 2 are steps 14 and 16).
- Formula: fee == (req.gas + 150000 + 16 x (calldata + 700) [+100000 token fee]) x 2.4e12 wei x 115/100, req.gas and calldata decoded from the signed request in the tx input: **16 of 16 exact** (3 with the +100,000 token fee term).
- Commission: RLS transfer relayer -> 0x71AF of floor(fee x 15/115) within 600 blocks: **16 of 16 exact**.
- 9 more payouts in the window match privately paid fees (0.576 x3, 1.656 x3, 1.08, 0.61296048, 1.00395684).
- Negative control (`--self-test`): price moved by 1 wei per gas and expected payout by 1 wei: 0 of 16 formula, 0 of 16 payout. The checker rejects a wrong number.
- Output: `evidence/fresh_check_24692010.json`, `evidence/fresh_check_24692010_selftest.json`.
- Also rerun at about 7 PM IST: `scripts/hands_on.py` (public RPC live) gave output identical to the saved `evidence/hands_on_steps.json` for all 20 steps; `scripts/code_check.py` found the same fee constants and functions in the live bundle index-BRJsQdqQ.js (sha256 05b6ebb65b9114ff75558b007eb42cd92924fe2daf23164e4f8e93245d8044f3), only variable names differ from index-DlzVF1v6.js.

- Rechecked 20 Nov 2026 about 10:50 PM IST: index-BRJsQdqQ.js now 404s; the live build is index-Dlv-HYaZ.js (sha256 7530bbc2d7a301c50e28923529cb9315f88145a9a25a7c71db8a1f34afd9ca68) with the same fee constants and functions, only variable names differ.

### 2.7 Saved data vs fresh reads (verification boundaries)
- Fresh from the chain each run: hands_on.py, fresh_check.py, trace_tx.py, check_addresses.py, check_fee_split.sh, code_check.py (live bundle).
- Uses saved data unless refreshed: fetch_history.py caches tx details in evidence/raw/forwarder_tx_details.json (`--refresh` refetches all); check_token_fee.py reads the payout list saved by fetch_history.py; make_charts.py reads the CSVs.
- Saved and not re-creatable: the app quotes (evidence/browser_*.log, screens/). They are checked against the onchain fee or, for shielded fees, against the public payout (payout x 115/15 = fee).

## 3. My analysis
- **Comparison (sources read 20 Nov 2026 ~7 PM IST):** RAILGUN docs: 0.25% deduction per shield and unshield to the treasury; Broadcasters pay gas and take a premium from the private balance, "generally ~10%" of gas, set per Broadcaster; a Broadcaster fee expires after about 3 minutes (docs.railgun.org wiki/learn/railgun-deductions, community-faqs/readme/costs-and-fees, developer-guide/wallet/transactions/ux-private-transactions). Zcash ZIP 317: fee scales with logical actions and "should not leak private information ... computable from only the public data" (zips.z.cash/zip-0317). Enygma Public: 0.25% on USDr shield/unshield, single relayer run by Rayls (who-sees-what), fixed 15/100 on top of gas, flat private payment fee on the pilot.
- **Privacy holds in the fee too.** A private RLS payment always costs the same 4.416 RLS, so the public 0.576 RLS payout is identical for a 5 RLS and a 3 RLS payment (steps 6 and 10) and comes from the relayer, not the payer. The fee trail shows that a payment happened, not who paid whom or how much, which matches "Who sees what".
- **You never pay more than the quote.** The fee is fixed before signing (padded gas x a fixed RLS price per gas). Actual gas used was 70 to 80% of the priced gas in my run (e.g. 2,066,871 used vs 2,608,722 priced for register); the relayer carries the real chain gas in USDr.
- **The testnet RLS price per gas:** rlsPerGas 0.0000024 RLS = 48 gwei (the testnet gas price the relayer paid) x 50. I read this from the data first; the Rayls team has since confirmed it is a fixed test price (section 4).
- **Why a fee looks like ~72 to 81 RLS per USDr of real gas, not 50:** 50 x 1.15 (commission) = 57.5 RLS per USDr of priced gas, and the priced gas is the relayer's padded estimate. In my run gasUsed was 69 to 79% of the priced gas (USDr shield 959,486 of 1,388,827 = 69%; USDr unshield 1,243,519 of 1,723,828 = 72%) (register 2,066,871 / 2,608,722 = 79%), so per USDr of actual gas it is 57.5 / 0.79 = 72.6 RLS for register and about 81 for a shield. That is exactly the team's explanation, rebuilt from onchain numbers.
- **The 15% is "15 on top of 100", not 15% of the total**: 15/115 = 13.04% of what the user pays.
- One relayer, one commission address, a payout ~4 s after each tx: simple to audit from public data, which is what made this whole check possible.

## 4. Confirmed by the Rayls team (Alex, reply on r/Rayls, 20 Nov 2026)
Source: https://www.reddit.com/r/Rayls/s/EtnvbYGAQ9 (r/Rayls Technical Q&A, "How do Enygma Public fees work on Rayls testnet? 3 questions on commission fee rate and burn split"). Reply by Rayls team member Alex, 20 Nov 2026 (~4:28 PM IST).
These are the team's answers. They are kept apart from my own checks: where I could check something myself it says so.
| # | Question | Team answer | My own check |
|---|---|---|---|
| 1 | Who controls 0x71AF…8B95? | A team test wallet standing in for the treasury and the auditor on testnet. Not a Rayls Foundation address. Mainnet will use a different address. | Onchain I can only show it is an EOA that receives the 15% and the 0.25% (2.3, 2.4). Control: team statement only. |
| 2 | Where does the testnet RLS fee price come from? | A fixed test price, not an oracle: 2.4 RLS per million gas, which at 48 gwei USDr gas is 50 RLS per USDr. Users see more because of the 15% on top (50 x 1.15 = 57.5) and because the fee is charged on the relayer's gas estimate (margin + overhead), not on final gasUsed. Pricing model, rate and 15% are experimental. | Matches my formula exactly: 0.0000024 RLS/gas x 115/100, charged on padded estimated gas (2.2), and my observed gasUsed of 69 to 79% of the priced gas (section 3). Relayer `/info` rlsPerGas = 2400000000000 wei = 2.4 RLS per million gas. |
| 3 | Live chain fee split: 50/50 (docs) or 50/30/20 (repo README)? | Mainnet runs 50/50 now: FeeAggregator getConfig() returns 5000 / 0 / 5000 (validators / ecosystem / burn). 50/30/20 in the README is only an example; the split is configurable. It covers chain gas fees paid in USDr; the Enygma commission is a separate fee in RLS. | **Confirmed by the team and independently verified** (2.5). |

## 5. Still unconfirmed (open, see discord-ticket.md)
- Docs (How Enygma Public works, Invites) say "the claim pays for both" (claim and registration). In my run the claim went through but the registration then asked for 7.20 public RLS (2.1 notes). Doc vs observed, asked as an open question in the article.
- The live bundle also has a constant `0.0000032` (used as `100n*Br(Fr)`), next to the fee code. Meaning not confirmed (maybe the "up to" bound); not used in any claim.
- Whether the 0.25% is meant to apply to public USDr sends through the wallet too (61 of 121 USDr fee transfers), since the docs only mention shield/unshield.
- Three forwarder fees on 17 Nov 2026 17:07 to 17:11 UTC with no matching 15% payout (375 of 378 match).
- Faucet cooldown: the relayer says 3 h (10800 s, and "gives again in 180 min" at 09:14 UTC), the docs say once an hour, and in my run both accounts could claim again at 11:14 UTC, 2 h after the first claim. The amounts also changed in between (50 RLS then 250 shielded RLS / 10 USDr), so the faucet config may have been updated and this is not a clean measurement.
- Invite registration: the quote said sponsored (fee 0, "Paid by the invite") but the relay rejected it as fee-too-low and asked for 7.20 public RLS (2.1, notes). The 4.6M gas claim fee may already include registration gas; I could not confirm that.
- Whether the live relayer runs the same code as the relayer module in the wallet bundle (its outputs match it in everything I tested).

## Method and limits
- Testnet pilot only, experimental and expected to change before mainnet. Test RLS and USDr have no value; nothing here is a mainnet cost or price claim. The one mainnet read is the chain fee split (2.5).
- Read-only public RPC + Blockscout API for all data. Older txs the public RPC no longer serves were read from the Blockscout v2 API (`tx_data_source` column).
- The run used throwaway keys made on the box and a scripted browser (headless Chrome) on enygma-testnet.rayls.com, signing as the throwaway key. No personal wallet, no mainnet.
- Before 9 Nov 16:04 UTC the testnet ran an earlier fee version: 150 forwarder fees from 27 Oct to 9 Nov follow different pricing and have no separate payout. They are in the CSV but left out of the checks above.

## 2.8 App quote screenshots (added 20 Nov 2026, about 11:10 PM IST)
- Register (wallet A, @railfeetrace1, A_04 at 09:18:22 UTC): app shows "up to 8.00 RLS, 6.96 gas + 1.04". That is /gas-quote action=register rlsFee 8004000000000000000 (2,900,000 gas x 2.4e12 x 1.15), a max. The signed /quote returned fee 7200072720000000000, charged onchain 7.20007272 (tx 0x150f72f0…).
- Send (A_10): app "4.42 RLS, 3.84 gas + 0.58 Rayls Foundation (15%)" = /private-quote fee 4416000000000000000.
- USDr shield (A_14): "Fee, 0.25%: 0.0100 USDr"; gas choice shielded up to 8.00 (shieldedRlsFee 8.004) or public up to 4.14 (rlsFee 4.14). Public chosen, charged 3.8329638.
- 8.28 (B_05, 09:37:32 UTC, before the 250 RLS faucet): "8.28 RLS, 7.20 gas + 1.08", app note "One action spends at most two of your RLS notes". Bundle privateQuote: rlsFee = (Gr+Kr) gas = 1.6M + 1.4M = 3.0M x 2.4e12 x 1.15 = 8.28, used when no single note covers amount + fee (uT: single-input check), and always for non RLS tokens (fee 0, rlsFee only).
