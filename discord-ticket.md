# Questions for the Rayls team (not for the post)

Public thread: https://www.reddit.com/r/Rayls/s/EtnvbYGAQ9 (r/Rayls Technical Q&A, 20 Nov 2026).
Team framing (Alex, Rayls team, reply on r/Rayls, 20 Nov 2026 ~4:28 PM IST): Enygma Public is a testnet pilot. Everything is experimental and will most likely change before mainnet. Frame the post that way.

## Confirmed by the Rayls team (Alex, reply on r/Rayls, 20 Nov 2026)
Source: https://www.reddit.com/r/Rayls/s/EtnvbYGAQ9
1. **0x71AF09966CBED4434ccA97c40Fa38B8083548B95**: a team test wallet standing in for the treasury and the auditor on testnet. Not a Rayls Foundation address. Mainnet will use a different address.
   My own check: onchain it is an EOA that receives the 15% commission and the 0.25% fee. Who controls it is the team's statement only.
2. **RLS/USDr rate**: a fixed test price, not an oracle. 2.4 RLS per million gas; at 48 gwei USDr gas that is 50 RLS per USDr. Users see more because of the 15% on top (50 x 1.15 = 57.5) and because the fee is charged on the relayer's gas estimate (margin + overhead), not final gasUsed. Pricing model, rate and 15% are experimental.
   My own check: this matches my formula exactly (0.0000024 RLS/gas x 115/100 on padded estimated gas), and in my run gasUsed was 69 to 79% of the priced gas. That turns 57.5 into the ~70 to 81 RLS per USDr of actual gas I saw (70.5 in the reddit example tx, 72.6 for register).
3. **Chain fee split**: mainnet runs 50/50 now. FeeAggregator getConfig() returns 5000 / 0 / 5000 (validators / ecosystem / burn). 50/30/20 in the README is just an example; the split is configurable. It covers chain gas fees paid in USDr. The Enygma commission is a separate fee in RLS.
   **Confirmed by the team and independently verified**: `cast call 0x07E17E17e17E17e17E17e17e17e17e17E17E17E3 "getConfig()"` on https://mainnet-rpc.rayls.com at block 14,858,726 (20 Nov 2026 10:59:20 UTC / 4:29:20 PM IST) returns (5000, 0, 5000). The address is an EIP-1967 proxy whose implementation is the verified FeeAggregator at 0x07e17e17E17e17e17E17E17E17e17e17e17E17e4. Saved in `evidence/fee_split_mainnet.txt`.

## Still open (not in the post as facts)
4. Docs mention the 0.25% fee for USDr shield and unshield, and my own USDr shield (4 USDr, fee 0.01) and unshield (2 USDr, fee 0.005) on 20 Nov matched that exactly. Onchain, 61 of 121 USDr fee transfers belong to public USDr sends made through the wallet. Is that intended?
5. Three forwarder fees on 17 Nov 2026 17:07 to 17:11 UTC have no matching 15% payout: 0x3925cd6f0111f18dadd326ca74d9f72c6cdb14bdc4766eaab51a6deda56eab73, 0xc2bf33d02a4e7ffc8873dfdc3aa8f3dcb9e7cf6ae0ee027af5c865df06223f48, 0xedad565bc48d5580d678dfbb36ceb953f7c71847609e07a46f0e7edd4b31a644. Were they paid later, or skipped? (375 of 378 since 9 Nov match exactly.)
6. Faucet cooldown: the relayer returns `cooldown: 10800` (3 h, one kind per address) and said "gives again in 180 min" at 09:14 UTC, but https://docs.rayls.com/docs/try-enygma-public-on-testnet says "once an hour". In my run both accounts could claim again at 11:14 UTC, about 2 h later, and the amounts had changed from 50 RLS to 250 shielded RLS / 10 USDr. Which cooldown is intended?
7. Is the live relayer the same code as the relayer module shipped in the wallet bundle? Its fees match that code to the wei in everything I tested.
8. Invite registration "Paid by the invite": for @railfeetrace3 on 20 Nov ~11:30 UTC (5:00 PM IST) the relayer `/quote` returned `sponsored: true`, fee 0, but `/relay` answered `fee-too-low` (below 7199992680000000000 RLS wei). A new quote then asked 7.20 public RLS, which a fresh invited account does not have, so no registration tx went out. The claim itself (tx 0xbb2c67f40360a36dc6f2c3827e1d2ac63725578fea94208ef064739aefaf1a08, fee 12.696 RLS) went through fine. Is registration meant to be covered by the claim fee?

## Draft follow up comment for the same r/Rayls thread (he posts it himself if he wants)
thanks for the answers, all clear and i checked the fee aggregator getConfig myself, 5000 0 5000. my usdr shield and unshield also matched the 0.25% exactly. a few small things left from the testnet pilot:
1. docs say 0.25% on usdr shield and unshield but about half the usdr fee transfers onchain come from public usdr sends in the wallet. is that intended
2. three fees on 17 nov 17:07 to 17:11 utc have no 15% payout (tx 0x3925cd6f..., 0xc2bf33d0..., 0xedad565b...). paid later or skipped
3. faucet cooldown is 3 hours in the api but docs say once an hour. which one is right
4. i tried the invite flow with a fresh account. docs say the claim pays for both the claim and the registration. claim worked fine but the paid by the invite registration got fee too low from the relay and then asked for 7.2 public rls, which a new account doesnt have. is registration meant to be covered by the claim fee
5. is the live relayer the same code as the relayer module in the wallet bundle
thanks
