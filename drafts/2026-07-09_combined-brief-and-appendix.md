# What the 80-80 wage subsidy would cost—and how many Americans it would put back to work

*Draft: 2026-07-08 | Authors: Benjamin Glasner and Adam Ozimek | Status: internal draft (pre-review)*
*Series: Agglomerations, installment three, following "How to End Low-Wage Work Forever" and its FAQ sequel.*

The 80-80 wage subsidy would raise pay for 15.9 million American workers at a net fiscal cost of roughly $45 billion to $48 billion per year—and expand work on two margins: roughly 1.49 million non-workers drawn into jobs (a deliberately conservative floor sits near 1 million), plus the equivalent of nearly 200,000 full-time workers in added hours among part-timers already on payrolls.

**Why it matters:** When we proposed the 80-80 wage subsidy, we deferred the hardest questions—what it costs, who gets the money, and how many non-workers it actually pulls into jobs. We have now built a full microsimulation to answer them, and the results sharpen the case in one direction and complicate it in another: the subsidy costs far less per new job than the industrial-policy alternatives, but the safety net claws back roughly half of its value for the single mothers it is best positioned to help.

A quick refresher for new readers: the 80-80 wage subsidy fills 80 percent of the gap between a worker's employer-paid wage and a target wage set at 80 percent of the national median wage, paid out in every paycheck. The formula treats $7.25 per hour, the federal minimum wage, as the lowest creditable base wage, which blunts any incentive to misreport pay.[^1] Figure 1 shows the schedule: the lower the employer wage, the larger the fill, and every dollar of employer raise still lifts take-home pay.

**Figure 1. How the 80-80 subsidy fills the wage gap.**

![How the 80-80 subsidy fills the wage gap](../output/figures/main/fig01_subsidy_schedule.png)

One housekeeping note before the numbers. The original posts used 2024 data, with a $20 median wage and a $16 target. The simulation uses the most recent 12 months of Current Population Survey data (May 2025 through May 2026), which put the weighted median hourly wage for paid-hourly workers at $21.00 and the target at $16.80. Every figure below reflects the updated data.[^2]

The rest of this post follows the format of the FAQ: the questions we expect you to ask, in the order we expect you to ask them.

## What does it cost?

Start with the static answer—assume nobody changes their behavior. The subsidy reaches 15.9 million workers at a gross cost of just under $56 billion per year. After the federal government recaptures taxes on the subsidy and banks savings from safety-net programs, the net cost falls to $45.1 billion. The average recipient collects $3,518 per year in subsidy and keeps roughly $2,800 in net income after those interactions.

People do change their behavior, so we model that two ways. A reduced-form approach applies employment and hours elasticities benchmarked to the Earned Income Tax Credit (EITC) literature and Congressional Budget Office conventions. A structural search-and-matching model lets workers and firms bargain over the subsidy directly, holding incumbent wages sticky and varying the worker's bargaining share from 0.3 to 0.7. The two approaches land in nearly the same place.

**Table 1. Annual fiscal cost of the 80-80 wage subsidy, by modeling approach**

| Scenario | Gross cost ($ billions per year) | Net cost ($ billions per year) |
|---|---|---|
| Static (no behavioral response) | 55.9 | 45.1 |
| Reduced-form, lower | 57.3 | 45.9 |
| Reduced-form, central | 59.8 | 46.7 |
| Reduced-form, upper | 63.6 | 47.6 |
| Structural, sticky incumbent wages | 59.6–60.7 | 47.4–48.4 |
| Incumbent hours response (adds to any row above) | +0.5 to +2.4 | +0.2 to +1.3 |
| Incidence upper bound (all wages renegotiate) | up to 109.1 | — |

*Note: Net cost equals gross cost minus federal tax recapture and safety-net offsets. The hours-response row is the added cost if part-time workers extend their hours in response to the per-hour subsidy (see "How sure are you?"). The final row is a disclosed bound, not a forecast; see "Will employers just capture it?" below.*
*Source: Economic Innovation Group 80-80 wage subsidy simulation, 2026.*

Our central estimate: roughly $57 billion to $64 billion gross and $45 billion to $48 billion net per year, with perhaps $2 billion more if part-timers extend their hours. For scale, that net figure buys a per-paycheck raise for about one in ten American workers. Figure 2 traces how the gross cost becomes the net cost: the government recaptures payroll and income taxes and banks safety-net savings, partly offset by higher Affordable Care Act premium tax credits.

**Figure 2. From gross to net: taxes and safety-net offsets.**

![From gross to net: taxes and safety-net offsets](../output/figures/main/fig02_cost_waterfall.png)

## Who gets the money?

The eligible population looks like the low-wage workforce, because it is the low-wage workforce: every paid-hourly worker earning between $7.25 and $16.80 per hour.

**Table 2. Who receives the subsidy (static eligible base, 15.88 million workers)**

| Group | Recipients (millions) | Share of recipients (%) | Share of the group's workers (%) |
|---|---|---|---|
| **Sex** | | | |
| Women | 9.61 | 60.5 | 26.2 |
| Men | 6.27 | 39.5 | 17.2 |
| **Age** | | | |
| 16–24 | 5.73 | 36.1 | 43.0 |
| 25–34 | 3.78 | 23.8 | 19.7 |
| 35–44 | 2.54 | 16.0 | 16.0 |
| 45–54 | 1.97 | 12.4 | 14.9 |
| 55–64 | 1.86 | 11.7 | 16.0 |
| **Education** | | | |
| Less than high school | 1.78 | 11.2 | 37.4 |
| High school diploma or GED | 6.85 | 43.1 | 25.2 |
| Some college or associate's degree | 5.33 | 33.5 | 22.7 |
| Bachelor's degree | 1.63 | 10.3 | 12.0 |
| Graduate degree | 0.29 | 1.8 | 6.8 |
| **Race and ethnicity** | | | |
| White, non-Hispanic | 7.17 | 45.1 | 19.4 |
| Hispanic | 4.44 | 27.9 | 23.5 |
| Black, non-Hispanic | 2.82 | 17.8 | 27.3 |
| Other | 1.45 | 9.1 | 20.5 |
| **Family type** | | | |
| Single, no children | 9.35 | 58.9 | 28.5 |
| Married, with children | 2.67 | 16.8 | 13.5 |
| Single, with children | 2.14 | 13.4 | 23.5 |
| Married, no children | 1.72 | 10.8 | 15.0 |

*Note: "Share of the group's workers" is recipients in the group divided by all paid-hourly workers ages 16 to 64 in that same group (73.3 million weighted). The denominator is the paid-hourly workforce; it excludes salaried workers, the self-employed, and workers without a measurable hourly wage. Overall, 21.7 percent of paid-hourly workers receive the subsidy.*
*Source: Economic Innovation Group 80-80 wage subsidy simulation, 2026.*

The third column reframes the story. The share-of-recipients column tells you where the money pools; the share-of-workers column tells you how deeply the subsidy reaches into each group. Read together, three patterns stand out. First, the subsidy skews female both ways: women are 60.5 percent of recipients, and 26.2 percent of women paid-hourly workers qualify versus 17.2 percent of men (men nonetheless collect a slightly larger average subsidy, $3,602 per year versus $3,464). Second, it reaches deepest among the youngest and the least credentialed: 43.0 percent of workers ages 16 to 24 qualify—the highest take-up of any group—as do 37.4 percent of workers without a high school diploma, against just 6.8 percent of those with a graduate degree. The subsidy concentrates on exactly the workers the last four decades of wage growth left behind. Third, single parents stand out on reach: 23.5 percent of single-parent paid-hourly workers qualify, well above the 13.5 percent take-up among married parents, whose households more often clear the wage target on a second earner. Figure 3 shows the take-up rates side by side.

**Figure 3. Share of each group's hourly workers who qualify.**

![Share of each group's hourly workers who qualify](../output/figures/main/fig03_takeup_by_group.png)

The subsidy is also steeply progressive within the eligible range, by construction. The lower the wage, the larger the gap the subsidy fills.

**Table 3. Average annual subsidy by hourly wage**

| Hourly wage band | Workers (millions) | Average annual subsidy ($) |
|---|---|---|
| $7.25–9.00 | 0.84 | 10,281 |
| $9.00–11.00 | 1.07 | 7,867 |
| $11.00–13.00 | 2.22 | 5,793 |
| $13.00–16.80 | 11.75 | 2,206 |

*Source: Economic Innovation Group 80-80 wage subsidy simulation, 2026.*

**Figure 4. The lowest-wage workers receive the largest subsidies.**

![The lowest-wage workers receive the largest subsidies](../output/figures/main/fig04_subsidy_by_wage.png)

The geography works the same way, and it delivers on the place-based argument from the first post. Because the target wage is national but wages are local, money flows automatically to lagging labor markets. Figure 5 maps the pattern: the average subsidy in Louisiana is $4,981 per year and in Mississippi $4,990, versus $2,392 in California. Louisiana alone has 317,000 eligible workers; West Virginia has 105,000, averaging $4,229 each. No commission picks winners. The formula finds distressed places on its own.

**Figure 5. Average annual subsidy per eligible worker by state.**

![Average annual subsidy per eligible worker by state](../output/figures/main/fig05_avg_subsidy_by_state.png)

Finally, the subsidy does not operate in a vacuum. Its interactions with existing programs cut both ways, as a share of gross cost:

- **Supplemental Nutrition Assistance Program (SNAP):** savings equal to 12.6 percent of gross cost.
- **Medicaid and the Children's Health Insurance Program (CHIP):** savings equal to 13.4 percent.
- **Temporary Assistance for Needy Families (TANF) and the EITC:** savings equal to 2.4 and 1.6 percent, respectively.
- **Affordable Care Act (ACA) premium tax credits:** added costs equal to 24.9 percent of gross cost, because higher incomes shift some workers from Medicaid into subsidized marketplace coverage. This is a real fiscal interaction, not a modeling artifact, and any serious cost estimate has to carry it.

## Does it actually pull people into work—and how many?

This is the question the whole proposal turns on, and it is the simulation's genuinely new contribution: the first structural estimates of labor-force entry for this policy.

In the first post, we told the story of Mike, whose reservation wage sat just above what any employer would offer him. The subsidy exists to close that gap, as Figure 6 illustrates. The simulation now estimates how many Mikes there are.

**Figure 6. How the subsidy clears a worker's entry threshold.**

![How the subsidy clears a worker's entry threshold](../output/figures/main/fig06_reservation_wage.png)

Before the number, the denominator deserves a hard look, because "59 million non-employed adults" overstates who a wage can plausibly reach. Roughly 7 million are unemployed and actively searching. Another 34 million are out of the labor force for other reasons—nearly half of them ages 16 to 24, mostly in school. About 10 million report being unable to work due to disability, and 9 million describe themselves as retired. Survey evidence says the barriers in those last groups are mostly not about wages: roughly half of prime-age men out of the labor force report a serious health condition, and even outright denial of disability benefits moves employment for only a minority of marginal applicants.[^6] A realistic wage-responsive entry pool is closer to 10 to 15 million people than 59 million.

**Table 4. New labor-force entrants under the 80-80 wage subsidy**

| Scenario | New entrants (millions) |
|---|---|
| Conservative floor (no non-employment wage penalty) | 1.02 |
| **Evidence-central** | **1.49** |
| High (joint upper corner) | 3.81 |
| Full range across the parameter grid | 0.23–3.81 |
| *Evidence-central, by group* | |
| Single mothers | 0.24 |
| Other women | 1.07 |
| Men | 0.18 |

*Note: The three headline scenarios are internally-consistent bundles of the model's uncertain parameters, not single-lever excursions. The conservative floor applies no wage penalty; the evidence-central applies a modest, status-differentiated non-employment wage penalty (about 10 percent on average) that the offer-decay evidence supports; the high scenario is the joint upper corner (a 20 percent penalty, full offer dispersion, and the upper participation elasticities together). The full 0.23–3.81 million range spans every combination of the three uncertain axes—wage penalty, offer dispersion, and participation elasticity (see "How sure are you?").*
*Source: Economic Innovation Group 80-80 wage subsidy simulation, 2026.*

Our central estimate is 1.49 million non-workers drawn into work, with a deliberately conservative floor of 1.02 million and a joint upper corner of 3.81 million. The floor is what the model produces when it applies *no* discount to non-workers' potential wages; but the evidence is clear that wage offers decay during long spells out of work, so a zero penalty is a conservative choice, not a neutral one. The evidence-central corrects that one choice—applying a modest, status-differentiated penalty (lighter for the recently unemployed, heavier for the long-detached)—while leaving everything else at its central setting. We are candid that the model also runs the other way in places: it lets every viable match form instantly, prices no childcare or commuting costs, and omits unemployment insurance from the no-work baseline—each of which pushes the count *up*. The true center is genuinely two-sided; we headline the evidence-central estimate because a zero wage penalty is the one setting the evidence rules out. These figures model each non-worker as facing a *distribution* of wage offers around their predicted wage, not a single number: real labor markets offer the same person different wages at different employers, so every demographic group has some members the subsidy can reach. Figure 7 shows the scenarios by group, with reference marks scaling the closest real-world precedents to our pool; Figure 7b shows who the entrants are.

**Figure 7. Induced entry into work, by group (evidence-central, with floor–high range).**

![Induced entry into work, by group, evidence-central with floor to high range](../output/figures/main/fig07_entry_band_by_cell.png)

**Figure 7b. Who the model predicts will enter, by prior status.**

![Who the model predicts will enter, by prior status](../output/figures/main/fig07b_entrants_by_status.png)

The entrants look like the people a wage offer can actually move: about a third are unemployed job-seekers—whose monthly job-finding rates are five to six times those of other non-participants—and nearly all the rest are non-participants without disability or retirement barriers. The disabled and retired, who make up a third of the non-employed population, contribute about 3 percent of modeled entrants.

Where do those numbers come from? We want to be precise about provenance, because the band edges and the central estimate rest on different evidence. The central anchors stay on the EITC and CBO evidence base. The edges come from the closest real-world experiments with subsidy-like payments. The Canadian Self-Sufficiency Project, which paid large earnings supplements to long-term welfare recipients, raised any-employment by 10.4 percentage points in its second year—that anchors the upper edge for single mothers.[^3] MDRC's Paycheck Plus demonstration in New York City anchors the upper edge for men, and its Atlanta replication, which found no detectable employment effect, anchors the lower edge.[^4] For married and childless women, the entry estimates reflect the research finding that the EITC's negative effect on married women's employment operates through household-income phase-outs—phase-outs the 80-80 wage subsidy does not have, because it is assessed individually on each worker's own paycheck.

Is 1.49 million small? Measured against the historical record, it is not. The closest macro-scale precedent—the 1990s EITC expansion, worth thousands of dollars a year, permanent, aimed at the most wage-responsive population ever measured, and amplified by a boom and welfare reform—raised single mothers' employment by roughly 3.5 to 4 percentage points over six years through the subsidy channel alone.[^7] Scaled to our reachable pool, that is about 0.9 million entrants—just below our conservative *floor* of 1.02 million. Our evidence-central of 1.49 million sits well above that precedent, between the Paycheck Plus demonstrations and the exceptional response of the Self-Sufficiency Project, and our full range brackets everything from Paycheck Plus Atlanta's null to well beyond SSP. These effects also build over years, not months: Paycheck Plus's employment gains peaked in year three, and the 1990s surge took most of a decade. Our figures are steady-state levels, not first-year effects.

Two features of the entrants matter for interpreting the cost numbers. First, entrants start part-time and part-year: matched to comparable low-wage incumbents, they average roughly 900 hours of work per year. Second, that is precisely why the marginal cost per entrant is low—though how low depends on how entrant hours are assigned, a sensitivity we test explicitly and return to in the next section.

Three stress tests worth disclosing, all computed on the evidence-central pool. If no married person with an employed spouse ever enters—zeroing out household coordination entirely, a bound and not a prediction—the estimate falls from 1.49 million to 1.21 million. If take-up matches mature programs like the EITC and SNAP (roughly 80 percent) rather than the 100 percent we assume, it falls to 1.20 million, and costs scale down proportionally. And there is a bookkeeping choice worth understanding: participation elasticities are estimated as employment-*rate* responses—their natural base is the affected group's employed workforce—while our headline expresses entry as a share of the reachable non-employed pool. We report both bases so the convention is a visible choice rather than a hidden one; they bracket each other and slightly lower single-mother entry when the employment-stock base is used.

The reachable population is disciplined by the wage distribution itself. Figure 8 plots the imputed potential wage offers of the non-employed pool: 47.8 percent fall below the $16.80 target, compared with 21.7 percent of paid-hourly workers—non-workers face worse wage prospects than workers, as selection implies, but most could still command offers above the target and are therefore beyond the subsidy's reach.

**Figure 8. Imputed potential wages of the non-employed, relative to the target.**

![Imputed potential wages of the non-employed, relative to the target](../output/figures/main/fig08_pool_wage_distribution.png)

## What about men specifically?

Honesty requires a direct answer here, because male non-employment motivated the first post: roughly 10 million prime-age men, 14 percent of the total, are without work, including about one in five in Louisiana and West Virginia.[^1]

The modeled male entry is real but modest—roughly 180,000 at the evidence-central estimate (about 120,000 at the conservative floor), rising toward 800,000 in the high scenario. The experimental record explains why we do not project more. In Paycheck Plus, employment gains concentrated among the most disadvantaged men: noncustodial fathers and the formerly incarcerated saw a 5.8 percentage point employment gain in the third year, though the pooled three-year estimate was not statistically significant, and the Atlanta replication found no effect at all.[^4] And the survey evidence is sobering about the pool itself: roughly half of prime-age men outside the labor force report a serious health condition, and a quarter to a third receive disability benefits—barriers a higher wage does not remove.[^6]

The right reading is not that a wage subsidy fails men. It is that a wage subsidy reaches the men a wage can reach—disproportionately unemployed job-seekers and the most disadvantaged—while leaving the broader prime-age male employment crisis, much of it rooted in health, disability, and demand-side exclusion, in need of complementary tools. We would rather report that finding straight than oversell the policy we proposed.

## Will employers just capture it?

The classic objection to wage subsidies is that employers pocket them by cutting wage offers. The structural model addresses this head-on.

Under the realistic assumption that incumbent workers' wages are sticky—existing pay does not instantly renegotiate when the subsidy arrives—firms capture about 3 percent of the gross subsidy at the central bargaining split, and no more than about 4 percent across the full range of bargaining assumptions. The subsidy overwhelmingly lands in workers' pockets. Part of the reason is the minimum wage itself: most new entrants earn near the $7.25 floor, where the law caps how far a firm can push the cash wage down to absorb the subsidy. Figure 9 contrasts the realistic sticky-wage case with the all-renegotiate bound.

**Figure 9. Employers capture little under realistic wage stickiness.**

![Employers capture little under realistic wage stickiness](../output/figures/main/fig09_firm_capture.png)

We also computed the theoretical worst case, and we want it on the record. If every wage in the economy immediately renegotiated, gross cost could rise to about $109 billion and firm capture could reach roughly 58 percent. We report this as a disclosed incidence bound, not a forecast: wholesale instant renegotiation of incumbent wages contradicts both the wage-rigidity evidence and ordinary experience of how pay adjusts. But readers deserve to see the bound, and program design—such as the $7.25 base-wage floor already in the proposal—exists precisely to keep reality near the sticky-wage case.

## What does it cost per new job, compared with the alternatives?

The first post cataloged what the United States currently pays for job creation: more than $154,000 per job under Buy American procurement rules, $106,000 to $196,000 per job for state and local business incentives, and roughly $900,000 per job saved by steel tariffs.[^5]

The subsidy's arithmetic is different in kind, so the comparison requires care. The costs attributable to new entrants—the subsidy payments the program makes only because those 1.49 million people entered work—total $7.8 billion gross per year, or about $5,300 gross and $3,900 net per new worker per year. That is the true marginal cost of each additional job, and it is low partly because entrants work part-time and part-year schedules. One caveat we test explicitly: that low figure depends on *how* we assign entrants their hours. Matching entrants to comparable low-wage incumbents by predicted wage puts them at the bottom of the hours ladder; assigning hours independently of predicted wage would roughly double entrant hours and the marginal cost per job (to around $9,800 gross). We flag the sensitivity rather than bury it.

But that figure is not constructed the same way as the per-job numbers above, and pretending otherwise would flatter our own proposal. Those figures divide a program's total cost by jobs created, for programs whose spending mostly flows elsewhere—procurement premiums, incumbent firms, and consumers paying tariff-inflated prices. The 80-80 wage subsidy's spending also mostly flows elsewhere: to raising pay for 15.9 million people who already work. The closest apples-to-apples comparison charges the subsidy's entire central net cost (roughly $48 billion, structural model) to its entrants, which yields about $32,000 per new job at the evidence-central estimate (ranging from roughly $13,000 in the high scenario to $47,000 at the conservative floor)—below the bottom of the state and local incentive range across that range, and far below Buy American and tariffs. And unlike those programs, the "overhead" here is not deadweight. It is a raise for more than a fifth of paid-hourly workers, and job creation is a co-benefit rather than the purchase. Figure 10 places both constructions against the alternatives on a log scale.

**Figure 10. Cost per job: the 80-80 subsidy versus other job-creation policies.**

![Cost per job: the 80-80 subsidy versus other job-creation policies](../output/figures/main/fig10_cost_per_job.png)

## Does it play badly with the rest of the safety net?

Here is the finding we did not fully anticipate, and the one policymakers should sit with.

In the FAQ post, we argued the subsidy beats the EITC on work entry because it is per-paycheck, transparent, non-categorical, and free of the EITC's benefit cliff. The simulation vindicates that argument in structure—the 80-80 wage subsidy has no cliff of its own—but reveals it as incomplete in practice: **the subsidy inherits everyone else's cliffs.**

Under our modeling assumption that the subsidy is taxable and counts against means-tested benefit eligibility, benefit phase-outs bite hardest for single mothers. For the median single mother in the entry pool, the subsidy raises the net return to working by about 18 percent, versus about 27 percent for other women and 23 percent for men—every dollar of subsidy that raises her income also phases her out of SNAP, Medicaid, and TANF, and the interaction eats roughly a third of the advantage other entrants enjoy. That gap is narrower than earlier versions of this analysis suggested (once we model realistic variation in wage offers, the reachable single mothers sit less deep in the phase-out range), but the mechanism is unchanged and the knife-edge cases below show it at its sharpest.

The knife-edge cases are the starkest illustration: roughly one in eight of the modeled entrants clear their entry threshold only because employers pay above the bargained wage across a benefit cliff. Their entry decision balances on program-interaction details no worker can be expected to compute. Figure 11 shows why, for one representative single-parent household: net income climbs with earnings, then drops at the points where Medicaid and other benefits phase out.

**Figure 11. Why the clawback bites: net income and the benefit cliffs a single-parent household crosses.**

![Why the clawback bites: net income and the benefit cliffs a single-parent household crosses](../output/figures/main/fig11_benefit_cliff.png)

The same dynamic governs how the subsidy pays off as a worker adds hours. Figure 11b holds the wage fixed at $10 per hour for that same Pennsylvania single parent and varies annual hours from zero to 3,000—60 hours a week for 50 weeks—with and without the subsidy. Across part-time and standard full-time schedules the subsidy adds real net income, roughly $7,800 at 20 hours a week and $5,600 at 40. But two features erode it. The subsidy stops growing once hours pass its cap of 2,080 a year—40 hours a week in the model—and because it counts as income the added earnings eventually push the household across the Medicaid and childcare cliffs. Past roughly 53 hours a week the subsidized household is actually worse off on net than the unsubsidized one—the clawback more than swallows the subsidy. It is the sharpest single illustration of why the subsidy's statutory treatment in benefit eligibility is a first-order design choice, not a detail to delegate.

**Figure 11b. Net income by hours worked, with and without the 80-80 subsidy.**

![Net income by hours worked, with and without the 80-80 subsidy](../output/figures/main/fig11b_net_income_by_hours.png)

Figure 12 shows the result across groups: the median single mother in the entry pool gains far less net value from working than everyone else.

**Figure 12. The safety-net clawback: median net gain from working, by group.**

![The safety-net clawback: median net gain from working, by group](../output/figures/main/fig12_clawback_net_gain.png)

The policy translation is simple. Whether the subsidy counts against SNAP, Medicaid, and TANF eligibility is a first-order design choice, not a technical detail to delegate to implementing agencies. If Congress wants the full entry effect for single mothers—the group with the strongest experimental evidence of responsiveness—it should decide that treatment deliberately, in statute.

## How sure are you?

Less sure than a point estimate would imply, which is why we publish bands.

- **Cost is the firm result.** Static, reduced-form, and structural approaches all land between $45 billion and $48 billion net per year, plus up to about $2 billion if part-timers extend their hours. Getting outside that range requires the all-wages-renegotiate scenario we consider implausible.
- **Entry is the wider band, and we vary its drivers jointly.** Three parameters move the entry estimate: the participation *elasticity* (genuine disagreement in the experimental record, between Paycheck Plus Atlanta's null and the Self-Sufficiency Project's exceptional response); wage-offer *dispersion* (how wide a distribution of offers each non-worker faces around their predicted wage, netting CPS measurement error out of the estimated spread); and wage-offer *levels* (the offer decay that long non-employment causes, which our cross-sectional wage model cannot detect—careful studies measure offers falling nearly 1 percent per month out of work[^8]). Rather than move one lever at a time, we report internally-consistent bundles: a conservative floor with no wage penalty (1.02 million), an evidence-central that applies the modest penalty the decay evidence supports (1.49 million), and a high joint corner that stacks all three upward (3.81 million). Across every combination the estimate spans 0.23 to 3.81 million (Figure 14). We headline the evidence-central because a zero wage penalty is the one setting the evidence rules out.
- **The hours margin matters nearly as much as entry.** Our benchmark hours elasticity (0.05) comes from the EITC literature—but the EITC's phase-out suppresses the very incentive the 80-80 preserves, since the subsidy pays in full on every added hour up to 40 per week. Under consensus elasticities for clean wage variation (0.2 to 0.33), part-time workers already on payrolls would add the equivalent of 0.19 million to 0.28 million full-time workers—alongside the entry margin's roughly 0.7 million full-time equivalents (Figure 15). How the entry margin's hours are assigned is itself a sensitivity: matching entrants to comparable incumbents by predicted wage places them at part-time schedules, and assigning hours independently would roughly double their full-time-equivalent contribution.
- **What would move the estimates:** the true wage opportunities of the long non-employed, hours responses among part-timers, take-up, and above all the statutory treatment of the subsidy in benefit eligibility, which shifts both the net cost and the composition of who enters.

**Figure 14. Induced entry across the parameter grid (penalty, dispersion, and elasticity).**

![Induced entry across the penalty, dispersion, and elasticity grid](../output/figures/main/fig14_mpl_uncertainty.png)

**Figure 15. The intensive margin: added hours among part-time incumbents.**

![The intensive margin: added hours among part-time incumbents](../output/figures/main/fig15_hours_margin.png)

Figure 13 makes the first point visual: the static, reduced-form, and structural models all cluster in the $45–48 billion net range; only the all-wages-renegotiate bound escapes it.

**Figure 13. Net annual cost is stable across models; only full wage renegotiation escapes the $45–48 billion range.**

![Net annual cost is stable across models; only full wage renegotiation escapes the range](../output/figures/main/fig13_cost_band.png)

One note on language. The model works by assigning each non-worker an entry threshold and asking whether the subsidy clears it. Those thresholds are calibration devices that bundle everything standing between a person and a job—health, caregiving, the value of time at home, the risk of losing benefits—not literal wage demands. No survey has ever measured the reservation wages of people outside the labor force, and we do not claim to have done so.

We built the simulation so that others can interrogate these choices: the [interactive version](https://eig-wage-subsidy.streamlit.app) is live, the technical appendix below walks through every modeling decision and the evidence behind it, and the methodology documentation is public.

**The bottom line:** For roughly $45 to $48 billion net per year, the 80-80 wage subsidy would raise pay for 15.9 million workers, direct the largest checks to the poorest workers and the most distressed states, and expand work on two margins—roughly 1.49 million new entrants (a deliberately conservative floor near 1 million; as high as 3.81 million if the offer-decay, dispersion, and elasticity evidence all run to the top of their ranges), plus nearly 200,000 full-time-equivalents of added work from part-timers extending their hours. Its marginal cost per new job is a few thousand dollars, and even charging the program's entire net cost to its entrants yields a per-job price (about $32,000) below the state and local incentive programs the country already runs—with the difference that the "overhead" here is a raise for more than a fifth of paid-hourly workers rather than deadweight. The remaining design questions are answerable. We just answered the expensive ones.

---

[^1]: Glasner, Benjamin, and Adam Ozimek, "How to End Low-Wage Work Forever," *Agglomerations*, Economic Innovation Group. [TO VERIFY: publication date and URL.]
[^2]: Economic Innovation Group, 80-80 Wage Subsidy Simulation, 2026. Eligibility, subsidy values, and hours from the Current Population Survey Outgoing Rotation Group, May 2025–May 2026, via IPUMS-CPS; tax and safety-net interactions from PolicyEngine-US, 2026 policy year.
[^3]: Michalopoulos, Charles, et al., *Making Work Pay: Final Report on the Self-Sufficiency Project for Long-Term Welfare Recipients*, Social Research and Demonstration Corporation, 2002, Table ES.1, https://www.srdc.org/wp-content/uploads/2022/07/SSP54.pdf (accessed July 8, 2026). [TO VERIFY: publication month.]
[^4]: Miller, Cynthia, et al., *Boosting the Earned Income Tax Credit for Singles: Final Impact Findings from the Paycheck Plus Demonstration in New York City*, MDRC, 2018, Tables ES.2 and 10, https://www.mdrc.org/sites/default/files/PaycheckPlus_FinalReport.pdf (accessed July 8, 2026); Yang, Edith, et al., *An Earned Income Tax Credit That Works for Singles: Final Impact Findings from the Paycheck Plus Demonstration in Atlanta*, MDRC, OPRE Report 2022-54, March 2022, https://www.mdrc.org/sites/default/files/Paycheck_Plus_Atlanta_Final_3.1_ALL_508.pdf (accessed July 8, 2026). The +5.8 percentage point Year 3 estimate for the noncustodial-father and formerly incarcerated subgroup is NYC report Table 10; the pooled three-year estimate (+2.8 percentage points) is not statistically significant. [TO VERIFY: NYC publication month.]
[^5]: Per-job cost figures for Buy American procurement, state and local business incentives, and steel tariffs are as cited in the first post (NBER, American Economic Association, and Peterson Institute for International Economics sources). [TO VERIFY: carry over the exact citations from the published post.]
[^6]: Krueger, Alan B., "Where Have All the Workers Gone? An Inquiry into the Decline of the U.S. Labor Force Participation Rate," *Brookings Papers on Economic Activity*, Fall 2017, https://www.brookings.edu/wp-content/uploads/2017/09/1_krueger.pdf (accessed July 9, 2026); Maestas, Nicole, Kathleen J. Mullen, and Alexander Strand, "Does Disability Insurance Receipt Discourage Work?," *American Economic Review* 103, no. 5 (2013): 1797–1829.
[^7]: Grogger, Jeffrey, "The Effects of Time Limits, the EITC, and Other Policy Changes on Welfare Use, Work, and Income among Female-Headed Families," *Review of Economics and Statistics* 85, no. 2 (2003): 394–408; Fang, Hanming, and Michael P. Keane, "Assessing the Impact of Welfare Reform on Single Mothers," *Brookings Papers on Economic Activity*, 2004, no. 1, https://www.brookings.edu/wp-content/uploads/2004/01/2004a_bpea_fang.pdf (accessed July 9, 2026). Both attribute roughly a third of the 1990s single-mother employment increase (~11 percentage points over 1993–2002) to the EITC.
[^8]: Schmieder, Johannes F., Till von Wachter, and Stefan Bender, "The Effect of Unemployment Benefits and Nonemployment Durations on Wages," *American Economic Review* 106, no. 3 (2016): 739–777 (wage offers decline approximately 0.8 percent per month of non-employment); Krueger, Alan B., and Andreas Mueller, "A Contribution to the Empirics of Reservation Wages," *American Economic Journal: Economic Policy* 8, no. 1 (2016): 142–179 (the unemployed set reservation wages near their prior wages, declining with the duration of non-employment).

---

## Evidence (internal, strip before publication)

**Sources**
- EIG 80-80 wage subsidy simulation, 2026 (this repository's pipeline, run 2026-07-09 — entry margins remodeled per the reality assessment: paid-hourly wage frame, status-weighted entry, group-specific offer dispersion at λ=0.75 folded into the headline, wage-penalty band, employment-stock base sensitivity, incumbent hours margin): all cost, eligibility, distributional, incidence, entry, and safety-net interaction figures.
- Entry-model reality assessment (`Infrastructure/explorations/2026-07-09_entry-model-reality-assessment.md`) and its literature pass (Krueger 2017; Maestas-Mullen-Strand 2013; Grogger 2003; Fang-Keane 2004; Schmieder-von Wachter-Bender 2016; Krueger-Mueller 2016; Hall-Mueller 2018; Fehr-Goette 2007): the risk-set framing, precedent ladder, penalty band, and hours-elasticity band.
- CPS Outgoing Rotation Group, 12 monthly samples 2025m5–2026m5, via IPUMS-CPS: eligible population, wages, hours; paid-hourly weighted median of $21.00 and target of $16.80.
- PolicyEngine-US, 2026 policy schedules: tax recapture and means-tested program interactions (with the project's post-processing corrections for ACA premium tax credits and Medicaid).
- Prior Agglomerations posts by Glasner and Ozimek: 80-80 design parameters, $7.25 base wage, the 2024-vintage $20 median/$16 target, the ~21 million under-$16 and prime-age male non-employment framing, and the external per-job cost figures (NBER/AEA/Peterson), which are attributed to the posts' citations, not to the simulation.
- Canadian Self-Sufficiency Project and MDRC Paycheck Plus (NYC and Atlanta): band-edge anchors for the entry estimates, as verified in this project's literature intake.

**Confidence**
- High: static cost, eligible counts, demographic and geographic distribution, program-interaction shares (direct simulation output).
- Medium-high: net cost band across behavioral models ($45–48 billion), which is stable across independent modeling approaches.
- Medium: evidence-central entry estimate (1.49 million; status-differentiated ~10% penalty, λ=0.75, central elasticities) and its group/status composition; the conservative floor (1.02 million, no penalty) and the high joint corner (3.81 million) bound it, and the full 27-cell parameter grid (penalty × dispersion × elasticity) spans 0.23–3.81 million (`entry_scenario_grid.parquet`, `entry_headline_scenarios.parquet`).
- Medium: the incumbent hours margin (0.06–0.28 million FTE) — the eps_int band transports consensus intensive elasticities to this design; no program with the 80-80's exact no-phase-out per-hour structure has been evaluated.
- Medium: single-mother clawback finding; conditional on the modeling assumption that the subsidy is taxable and counts toward means-tested eligibility.
- Flagged: all [TO VERIFY] items are citation details (dates, URLs, exact report references), not simulation numbers. Resolve before publication.

**Assumptions**
- All simulation figures reflect the 2026-07-09 pipeline run; the vintage difference versus the posts ($21.00/$16.80 vs. $20/$16) is disclosed in the text.
- The potential-wage model is estimated on paid-hourly earners (the market the target prices); its selection correction is small on this frame (ρσ ≈ +0.11) and the three imputation variants converge, so the dominant potential-wage uncertainty is the disclosed non-employment wage-penalty band {0, 10, 20 percent}, anchored to measured wage-offer decay.
- Entry propensity within each demographic cell is weighted by prior labor-force status (CPS U→E vs N→E flow ratios; SSDI work-capacity evidence) and the employment probit; the calibrated cell totals are unchanged by this weighting.
- Table 2's "share of the group's workers" column: numerator and denominator are both computed from the adapted CPS ORG panel (`_load_and_adapt_org_panel`), so recipients match the published counts exactly; the denominator is the pre-wage-threshold base (paid-hourly, wage-observed, ages 16–64, `earnwt`>0, minus the child-dependent exclusion, `earnwt`/n_months weighted), 73.3 million weighted. It is the paid-hourly workforce, not all employed persons (salaried workers, the self-employed, and workers without a measurable hourly wage are excluded). This reconstructs the `pct_in_group` field that `02a_descriptive_stats.py` intends but currently emits as null because its `data/external/org_workers_*.parquet` base file is absent from this checkout.
- The subsidy is modeled as taxable income that counts against means-tested benefit eligibility; the clawback and knife-edge entry findings are conditional on this and would change under alternative statutory treatment.
- Sticky incumbent wages are treated as the realistic incidence case; the all-renegotiate scenario is presented as a bound only.
- The $13,000–$47,000 fully-loaded-cost-per-entrant range is author arithmetic ($47.9B structural central net divided by the 3.81M high-corner and 1.02M floor entrant counts respectively; ≈$32,000 at the 1.49M evidence-central); the ~$5,300 gross / ~$3,900 net marginal figures divide the evidence-central entrant-attributable costs ($7.8B/$5.8B) by 1.49M entrants.
- Entrant hours are quantile-matched (MPL percentile → incumbent hours percentile within cell), which concentrates entrants at part-time schedules (mean ≈ 900 hours per year at the evidence-central) and lowers marginal entrant cost. PI-3 is now computed on the evidence-central pool: `entrant_hours_sensitivity.parquet` reports the rank mapping alongside an independent-draw and a cell-median mapping; the independent draw roughly doubles entrant hours and the marginal cost per job (~$9,800 gross vs ~$5,300). The fiscal total is barely affected (entrants are a few $B of ~$56B); the marginal-cost and full-time-equivalent claims carry the sensitivity.
- Offer dispersion: mean-preserving lognormal spread around each person's conditional-mean imputation, with group-specific residual SDs (education × age, 0.29–0.55) scaled by λ=0.75 (central; nets out approximate CPS measurement error; band {0.50, 1.00} in Figure 14). Hash-quantile draws, salted independently of the entry lottery; deterministic.
- Firm-capture figures reflect the corrected entrant-incidence accounting (actual firm surplus at the possibly floor-pinned wage, not (1−β)·subsidy — post-implementation review finding PI-1, fixed 2026-07-08).
- Word count of body prose (excluding tables, figures, footnotes, and this section): approximately 2,900 words after the 2026-07-09 revision.


```{=openxml}
<w:p><w:r><w:br w:type="page"/></w:r></w:p>
```

# Technical Appendix: How the 80-80 Wage Subsidy Simulation Works

*Companion to "What the 80-80 wage subsidy would cost—and how many Americans it would put back to work." Draft: 2026-07-09. Status: internal draft (pre-review).*

This appendix walks through the machinery behind every number in the main piece: what the model does, in what order, and—most importantly—what evidence justifies each modeling decision. We wrote it for readers who want to kick the tires. Nothing here is required to follow the main piece; everything here is required to audit it.

A reading note before we start. Every result in this project is one of three things, and we try to keep the labels visible throughout:

1. **Accounting.** Who earns what, who qualifies, what the checks add up to. These are arithmetic on survey data and involve no behavioral assumptions.
2. **Transported evidence.** Behavioral responses borrowed from the best available studies of *similar* policies. No program with the 80-80's exact design—permanent, universal, paid per paycheck, no phase-out—has ever been evaluated, so every behavioral parameter is imported from programs that differ in some respect. Where the direction of that difference is knowable, we say so.
3. **Disclosed judgment.** A small number of structural choices (functional forms, bounds, weights) that evidence informs but does not pin down. Each one is flagged, and each one has a sensitivity attached.

## 1. The data foundation

**Who is in the data.** The simulation runs on the Current Population Survey Outgoing Rotation Group (CPS ORG), the government's standard source for hourly wages: the twelve most recent complete monthly samples (May 2025 through May 2026, excluding October 2025, which was not fielded), obtained through IPUMS-CPS. Workers report wages in their fourth and eighth survey months; we use the earnings weight (`EARNWT`) for everything measured on workers and the population weight (`WTFINL`) for the non-employed. Monthly samples are averaged so all counts are period-average stocks, not sums.

**The policy parameters.** The target wage is 80 percent of the national median wage among paid-hourly workers—$21.00 in our window, so a $16.80 target. The subsidy pays 80 percent of the gap between a worker's employer-paid wage and that target, in every paycheck, on every hour up to 40 per week. Wages below the $7.25 federal minimum are treated as $7.25 (the anti-fraud base wage in the proposal). We compute the median on paid-hourly workers—not salaried workers with imputed hourly rates—because the policy prices, and its recipients work in, the hourly labor market. That choice matters more than it sounds; Section 4 returns to it.

**Eligibility (accounting).** A worker is eligible if they are a paid-hourly employee ages 16 to 64 earning under $16.80, excluding dependent children under 19. That yields 15.88 million workers—21.7 percent of the 73.3 million paid-hourly workforce—receiving an average of $3,518 per year. These figures involve no behavioral modeling.

**Taxes and transfers.** Every dollar of earnings and subsidy is run through pre-computed household net-income schedules from PolicyEngine-US (2026 policy year): federal and state income taxes, payroll taxes, EITC, Child Tax Credit, SNAP, Medicaid/CHIP, ACA premium tax credits, TANF, SSI, and smaller programs, keyed by family type and state. Net income includes the ACA and Medicaid values that PolicyEngine excludes by default. One deliberate design assumption runs through everything: **the subsidy is modeled as taxable income that counts against means-tested benefit eligibility.** This is the conservative reading; if Congress excluded the subsidy from means-tests (as it does the EITC), net costs would rise and the benefit-cliff interactions in Section 7 would shrink. We chose the conservative treatment and report its consequences rather than assuming them away.

## 2. Two behavioral models, on purpose

The simulation produces cost estimates two independent ways, and we publish both:

- **A reduced-form benchmark.** Labor-supply elasticities from the EITC and Congressional Budget Office literature, applied directly: "what would this cost if the subsidy behaves the way the EITC literature implies?" This is deliberately a *literal* use of the borrowed numbers—a transparent yardstick, not a claim about mechanism.
- **A structural search-and-matching model.** Employment happens when a worker-firm match generates enough surplus; wages come from Nash bargaining over that surplus; the subsidy is added surplus that worker and firm split. This model produces the entry, incidence, and cliff results in the main piece.

The two approaches land within a few billion dollars of each other on net cost ($45–48 billion), which is the strongest single robustness fact in the project. They differ on entry—the reduced-form benchmark of 0.48 million versus the structural model's conservative floor of 1.02 million and evidence-central of 1.49 million—for reasons that are fully attributable: different populations (the benchmark scales up existing low-wage workers; the structural model draws from the actual non-employed), different stimulus definitions (gross versus net-of-transfer), and different response aggregation. We keep the benchmark untouched precisely so readers can see what the structural machinery changes.

## 3. The non-employed pool: who could enter?

The structural entry model starts from every non-employed person ages 16 to 64 in the survey—59.3 million people. But that headline number is mostly people a wage cannot reach, and the model needs to know the difference. Using each person's reported labor-force status:

| Group | Millions | Evidence on wage-responsiveness |
|---|---|---|
| Unemployed (searching) | 7.0 | Job-finding rates of 25–28 percent per month; reservation wages near prior wages (Krueger and Mueller 2016) |
| Other non-participants | 33.8 | Heterogeneous; nearly half are ages 16–24 (mostly in school) |
| Unable to work (disabled) | 9.7 | Even full denial of disability benefits raises employment only ~28 points for the ~23 percent of marginal applicants (Maestas, Mullen, and Strand 2013) |
| Retired | 8.7 | Retirements are essentially permanent (Krueger 2017) |

Roughly half of prime-age men out of the labor force report a serious health condition, and a quarter to a third receive disability benefits (Krueger 2017). A realistic wage-responsive entry pool is therefore closer to 10–15 million than 59 million—and the model's mechanics respect that, in two ways described below (Sections 4 and 5).

## 4. Potential wages: what would a non-worker earn?

The subsidy can only reach a non-worker whose market wage would fall below $16.80. We cannot observe those wages, so we impute them, and this imputation is one of the two places the entry estimate is genuinely uncertain.

**The wage model.** We estimate a standard two-step selection model (Heckman 1979) on the ORG earner sample: a participation equation (who is a paid-hourly earner) and a log-wage equation (what they earn), with age, education (eight levels), sex, race and ethnicity, and state in both. The participation equation additionally includes household composition—marriage, children, presence of a child under five, and whether the person's spouse is employed, built from real within-household links in the CPS roster, not statistical matching. Both equations are survey-weighted—the participation probit by the population weight (WTFINL) and the wage regression by the ORG earnings weight (EARNWT), matching each equation's estimand. Because the imputation targets a *conditional mean*, unweighted estimation is also consistent and more efficient there (Solon, Haider, and Wooldridge 2015); we run it as a robustness, and the weighted and unweighted conditional pool medians differ by only about a dollar ($18.91 versus $20.10). Predictions for non-workers use the selection-consistent conditional mean and a Duan (1983) smearing retransformation.

**The frame matters more than the econometrics.** An earlier version of this model estimated the wage equation on *all* employed earners—including salaried workers, who are 44 percent of earners and have a median hourly-equivalent wage of $26.00, versus $21.00 for paid-hourly workers. On that contaminated frame, the selection correction looked large (ρσ ≈ +0.30) and the imputation was fragile: alternative treatments of the correction moved the entry estimate by a factor of seven. Re-estimated on the paid-hourly frame—the market these workers would actually enter—the correction shrinks to ρσ ≈ +0.11 and all three imputation variants converge (weighted median potential wage $17.18 to $20.68). The lesson we took: what looked like "strong negative selection into non-employment" was substantially the salaried/hourly divide leaking into the estimate.

**Offers are distributions, not points.** A conditional-mean imputation alone would make reachability a deterministic cliff: a 40-year-old man with a college degree would have exactly zero chance of facing a sub-target offer (his predicted wage is $31), and a 20-year-old without a diploma exactly 100 percent (predicted $15.34). Real labor markets do not work that way—the same person draws different offers from different employers. So each person's potential wage is drawn from a lognormal distribution centered on their (selection-corrected) conditional mean, with **group-specific spreads estimated from our own wage-equation residuals**: dispersion rises with education and age (residual SDs run from 0.29 for older workers without diplomas to 0.55 for older graduates), matching the documented wage-structure pattern. Under the distribution view, the college man faces roughly a one-in-ten chance of a sub-target offer and the young dropout roughly three-in-five—both sides of the cliff soften. Because residual variance bundles real dispersion with CPS measurement error (~0.10–0.15 log points), we scale the spread by λ = 0.75 in the headline (netting the error out approximately) and report λ = 0.50 and 1.00 as a band. Draws are deterministic hash-quantiles, salted independently of the entry lottery, and mean-preserving (they add spread without changing any person's expected wage).

**The result.** Non-workers' imputed wage offers sit below workers': 47.8 percent of the pool draws offers below the $16.80 target, versus 21.7 percent of paid-hourly workers earning below it. Negative selection, softened cliffs.

**The honest caveat, and what we do about it.** The selection model has no clean instrument: every candidate participation shifter (marriage, young children, spouse's employment) plausibly relates to wages too, a known limitation of this entire literature (Mroz 1987; Puhani 2000). So the small estimated correction cannot rule out wage penalties the cross-section cannot see. And direct evidence says such penalties are real: wage *offers* decay by roughly 0.8 percent per month out of work (Schmieder, von Wachter, and Bender 2016), and unemployed workers accept re-employment at about 90 percent of prior wages (Krueger and Mueller 2016). Much of the non-employed stock has been out for years. We therefore fold an explicit **non-employment wage penalty** into the headline. Because a zero penalty is a conservative choice the offer-decay evidence rules out—not a neutral baseline—our **evidence-central** applies a modest, status-differentiated penalty (about 5 percent for the recently unemployed, rising to 15 percent for the long-detached, a pool-weighted mean near 10 percent), giving **1.49 million** entrants; the undiscounted **1.02 million** is retained as a labeled conservative *floor*, and a 20 percent across-the-board discount (a long-spell bound) is the high case. Under the penalty scenarios, 58 to 69 percent of the pool falls below target. We headline the evidence-central estimate rather than the floor because the discount's *size* for this specific population is judgment, but its *existence* is not.

## 5. The entry decision: who actually takes a job?

**The economics.** A non-worker enters if the net gain from working—run through their household's actual tax-and-transfer schedule—clears their personal threshold. Formally, person *i* with potential wage *y*, matched annual hours *h*, and schedule *NI(·)* enters when

> NI(y·h + subsidy) − NI(0) ≥ (1 + m_i) × [NI(y·h) − NI(0)]

The left side is the net gain of working with the subsidy; the bracketed term is the net gain their own unsubsidized wage would deliver; and *m_i* is a personal markup capturing everything else standing between that person and a job. Working in net-gain space (rather than comparing wages) matters because it makes the subsidy's *actual* value—after benefit phase-outs—the thing being evaluated. It is why the model can find, for example, that phase-outs claw back roughly half the subsidy's value for single mothers (main piece, Figure 12).

**What the thresholds are, and are not.** The markups *m_i* are calibration devices, drawn from an exponential distribution whose scale is set so that each demographic group's total entry matches evidence-based participation elasticities (below). They bundle health, caregiving, the value of time at home, non-wage job attributes, and benefit-loss risk into a single number. They are **not** measured reservation wages: no survey has ever measured reservation wages for people outside the labor force (Krueger and Mueller's respondents are unemployed UI recipients), and decisions to reject offers are driven by non-wage factors about two-thirds of the time even among active searchers (Hall and Mueller 2018). We flag this because the phrase "reservation wage" invites over-reading.

**Who gets low thresholds.** Within each demographic group, the entry lottery is weighted by prior labor-force status and estimated employment propensity: unemployed job-seekers receive five times the base weight (matching the roughly five-to-one ratio of monthly job-finding rates between the unemployed and other non-participants in CPS flow data), while the disabled and retired receive weights of 0.15 (per the disability-insurance work-capacity evidence above). The weights change *who* enters, not *how many*—group totals are pinned by the calibration—and they matter enormously for realism: about a third of modeled entrants are unemployed job-seekers and roughly 3 percent are disabled or retired. An earlier uniform-lottery version produced entrant pools dominated by student-age non-participants, which no one should have believed. (The entrant *composition* is sensitive to these disclosed judgment weights even though the *count* and *cost* are not: under a uniform lottery the unemployed share would be far lower. We flag the dependence rather than present the composition as a finding.)

**The elasticities and their sourcing.** The calibration targets come from extensive-margin participation elasticities, applied to the net-of-transfer wage gain with a saturating response function (a Michaelis-Menten form that matches the literature elasticity for small gains but caps the response as gains grow very large, since the 80-80 delivers proportional gains far outside the range any study has measured). The bands, per group:

| Group | Lower | Central | Upper | Anchors |
|---|---|---|---|---|
| Single mothers | 0.25 | 0.50 | 0.65 | Central: mid-range of EITC quasi-experimental estimates (Meyer 2002; McClelland and Mok 2012). Upper: the Canadian Self-Sufficiency Project, the most generous earnings-supplement experiment on record, implies ≈0.49 on the any-employment margin (+10.4 points on a 30.1 percent base, against a roughly 70 percent net earnings gain); we allow headroom above it because SSP subsidized only full-time work. Lower: the Kleven (2024) reappraisal arguing even EITC effects are fragile. |
| Other women | 0.05 | 0.20 | 0.40 | The EITC's famous *negative* effect on married women (Eissa and Hoynes 2004) operates through household-income phase-outs the individually-assessed 80-80 does not have, so it is deliberately not imported. What survives is the intra-household income effect (Blau and Kahn 2007 document it shrinking), bounding the low end near zero; the upper end reflects secondary earners' historically higher elasticities and Paycheck Plus NYC's verified women's effect (+3.2 points pooled). |
| Men | 0.00 | 0.05 | 0.15 | Central: the CBO's 0–0.1 range for men. Upper: MDRC's Paycheck Plus NYC found a 5.8-point year-three gain concentrated in the most disadvantaged men (noncustodial fathers, formerly incarcerated)—but the pooled estimate was insignificant and the subgroup is a minority of the male non-employed, so the diluted cell-level value lands near 0.15. Lower: the Atlanta replication's precise null. |

Every number in that table traces to a primary source read directly (the MDRC final report tables, the SRDC final report, NBER working-paper versions); the project's literature catalog stores each with verification status.

**A base-semantics disclosure.** Participation elasticities are estimated in employment-*rate* terms: a 1 percent rise in the net return raises the affected group's *employed stock* by eps percent. Their natural count base is therefore the eligible employed workforce (1.8 million single mothers, 7.8 million other women, 6.3 million men), not the non-employed pool. Our headline calibration instead expresses entry as a share of the *reachable non-employed pool*—a convention inherited from the model's structure, with one undesirable property: it couples the entry count to the imputation's reachability share. With dispersed offers the two bases move in the same direction but not identically: recalibrating on the employment-stock base moves the conservative floor from 1.02 to 0.59 million and leaves single-mother entry near 0.16 million (from 0.17). Both are reported—the employment-stock variant as a first-class sensitivity row—so the convention is a visible choice rather than a hidden one.

**Reality checks.** Because no ready-made precedent exists, we discipline the output against the record instead. The closest macro-scale precedent—the 1990s EITC expansion, permanent and worth thousands per year, aimed at the most responsive population ever measured—raised single mothers' employment about 3.5 to 4 percentage points over six years through the subsidy channel alone (Grogger 2003; Fang and Keane 2004). Scaled to our reachable pool, that is roughly 0.9 million entrants—just below our conservative floor of 1.02 million. Our evidence-central estimate (1.49 million) sits above that benchmark, between the Paycheck Plus demonstrations and SSP's exceptional response, and the full range brackets Paycheck Plus Atlanta's null on one end and approaches SSP-scale on the other. These effects also took years to build everywhere they were observed, so our figures are steady-state levels, not first-year impacts. Two further sensitivities, computed on the evidence-central pool: zeroing out entry by married people with employed spouses (a bound on household coordination, motivated by Bonin, Kempe, and Schneider 2003) moves it from 1.49 to 1.21 million; assuming 80 percent take-up (the EITC and SNAP range) moves it to 1.20 million.

## 6. The hours margin: the policy's most distinctive incentive

The 80-80 pays its full per-hour subsidy on every additional hour up to 40 per week—no plateau, no phase-out. A $10-an-hour worker's marginal hour pays $15.44, a 54 percent raise. Roughly 9 million eligible workers currently work fewer than 40 hours a week.

The EITC literature's consensus that hours barely respond (elasticities near 0.05) is the standard benchmark—but the EITC's plateau and phase-out *remove or reverse* the marginal-hour incentive for most recipients, so that consensus partly measures the design, not the workers. Evidence from clean wage variation without phase-outs points higher: consensus intensive-margin elasticities around 0.33 (Chetty 2012); large transitory responses to salient per-unit wage increases (Fehr and Goette 2007); and part-time-to-full-time conversion in both SSP and even an employer-side Finnish subsidy (Huttunen, Pirttilä, and Uusitalo 2013). We therefore report an hours band—elasticities of 0.05, 0.20, and 0.33—under which part-time incumbents add the equivalent of 0.06, 0.19, or 0.28 million full-time workers, at $0.5 to $2.4 billion added gross cost. At the central value the incumbent hours margin (0.19 million FTE) sits alongside the entry margin (about 0.7 million FTE at the evidence-central)—a structural feature of this design, and a reason entry counts alone understate the policy's labor-supply effect.

One honest caveat on the entry margin's hours. Entrants are matched to comparable low-wage incumbents by predicted wage (a rank-rank map), which—because predicted wage and hours are strongly correlated—places entrants at the bottom of the hours ladder (mean ≈900 hours a year) and drives the low marginal cost per entrant. We test that mapping explicitly (`entrant_hours_sensitivity.parquet`): assigning hours *independently* of predicted wage roughly doubles entrant hours, full-time equivalents, and the marginal cost per job. The fiscal total is barely affected—entrants are a few billion dollars of a ~$56 billion gross—but the marginal-cost and FTE claims carry this sensitivity, so we report it rather than pick the favorable mapping silently.

## 7. Wages, incidence, and the safety net

**Bargaining.** In the structural model, each match's wage is set by Nash bargaining: workers keep a share β of match surplus, firms the rest, with the subsidy entering as added surplus (Mortensen and Pissarides 1994; Hungerbühler and Lehmann 2006). We run β at 0.3, 0.5, and 0.7, spanning the efficient benchmark (Hosios 1990), matching-model calibrations (Shimer 2005), and the measured ~70 percent worker capture of EITC dollars (Rothstein 2010). Wages cannot fall below the $7.25 minimum (Flinn 2006)—which turns out to be the binding force for most entrants, since they bargain from low potential wages.

**Sticky versus flexible wages.** Our headline case holds incumbent wages fixed (wage rigidity for existing matches; Hall and Milgrom 2008): firms capture about 3 percent of the subsidy at the central bargaining split—no more than about 4 percent across the β range, and under 2 percent when the worker's bargaining share is high—entirely on new hires, computed as actual firm surplus at the (usually minimum-wage-constrained) hire wage. The disclosed worst case—every wage in the economy renegotiates immediately—raises gross cost to $109.1 billion with 58 percent firm capture. We consider it a bound, not a forecast, and show it so readers can see what the stickiness assumption is worth.

**The safety-net interaction.** Because the subsidy counts as income (Section 1), every entrant's and worker's gain is filtered through benefit phase-outs. Two headline consequences: the median single mother's net return to working rises about 18 percent (versus roughly 27 percent for other women and 23 percent for men), and roughly one in eight of the entrants clear their threshold only because the model lets employers pay above the bargained wage across a benefit cliff. The cliffs are real features of the current safety net (main piece, Figures 11 and 11b), not artifacts; the modeling choice is that the subsidy is exposed to them.

## 8. What this model does not do

- **No demand side.** Every viable match forms; no displacement of existing workers by entrants, no employer screening frictions. At ~1.49 million entrants (steady state) against 6–7 million monthly hires this is unlikely to bind, but it is assumed, not shown—and, like the omitted fixed costs of work and the missing unemployment insurance in the counterfactual, it runs the *other* way from the conservative wage-penalty and dispersion settings, which is why the true center is genuinely two-sided.
- **No fixed costs of work.** Childcare and commuting costs are not priced (no expense measure exists in the CPS; an acquisition is queued). Their absence overstates entry, most for single mothers—partially offset by our conservative benefit-clawback treatment.
- **No unemployment insurance in the counterfactual, and annual schedules against monthly status.** Both overstate the net gain of entry for the unemployed subset; the pool carries a flag so this can be bounded.
- **No dynamics.** Steady-state levels; the precedents suggest three to nine years to build.
- **No general-equilibrium wage effects** beyond the bargaining split, and **no behavioral take-up model** (the 0.80 scalar is a disclosure, not a mechanism).
- **The imputation has no clean instrument** (Section 4)—the wage-penalty band is the honest expression of what that leaves unknown.

## 9. Reading the uncertainty

| Quantity | Range | Dominant driver |
|---|---|---|
| Net fiscal cost | $45–48 billion (+ up to ~$2 billion hours margin) | Robust across all three models; the firm result |
| Induced entry | 1.02M floor / **1.49M evidence-central** / 3.81M high; 0.23–3.81M across the full penalty × dispersion × elasticity grid | Joint scenario grid; the non-employment wage penalty is the single largest lever |
| Hours margin | 0.06–0.28 million FTE | Whether the EITC hours null transports to a no-phase-out design |
| Firm capture | <2 percent (sticky) to 58 percent (full renegotiation) | Wage-rigidity assumption |
| Who benefits (distribution) | Point estimates | Accounting; no behavioral content |

## 10. Reproducibility

The full pipeline is deterministic (fixed hash-based assignment, no random seeds in the entry model; identical outputs byte-for-byte across reruns) and runs end-to-end from `code/run_all.py`. All analysis-consumable intermediates are parquet files under `output/data/intermediate_results/population/`, indexed by a generated manifest with a one-line loader (`code/_utils/intermediates.py`). Diagnostics for the entry model—selection-model coefficients, calibration targets versus realized shares, imputation-variant percentiles—are persisted to `nonemployed_pool_diagnostics.json` on every run. Figures regenerate from two R scripts against the same parquets. The interactive simulation is live at eig-wage-subsidy.streamlit.app, and the entry-model methodology is documented in the repository (`docs/entry_from_nonemployment_methodology.md`), including the full revision history of the decisions described here.

## Key sources

**Program evaluations (primary reports read directly):** Card and Hyslop (2005), *Econometrica*, and Michalopoulos et al. (2002), SRDC — the Canadian Self-Sufficiency Project. Miller et al. (2018), MDRC — Paycheck Plus New York City. Yang et al. (2022), MDRC/OPRE — Paycheck Plus Atlanta. Miller and Knox (2001), MDRC — Parents' Fair Share.

**EITC and participation:** Meyer (2002); Meyer and Rosenbaum (2001); Eissa and Hoynes (2004); Grogger (2003); Fang and Keane (2004); Nichols and Rothstein (2016); McClelland and Mok (2012), CBO; Kleven (2024); Chetty (2012).

**Non-employment, reservation wages, and wage penalties:** Krueger and Mueller (2016); Hall and Mueller (2018); Schmieder, von Wachter, and Bender (2016); Krueger (2017); Maestas, Mullen, and Strand (2013); Abraham and Kearney (2020); CEA (2016).

**Hours responses:** Fehr and Goette (2007); Chetty (2012); Huttunen, Pirttilä, and Uusitalo (2013).

**Matching and incidence:** Mortensen and Pissarides (1994); Hosios (1990); Shimer (2005); Rothstein (2010); Hall and Milgrom (2008); Flinn (2006); Hungerbühler and Lehmann (2006); Bonin, Kempe, and Schneider (2003).

Full citations with verification status are maintained in the project's literature catalog; each entry records whether its load-bearing numbers were verified against the primary source.

---

## Evidence (internal, strip before publication)

**Sources:** all simulation figures from the 2026-07-09 pipeline run (post-reality-assessment); model mechanics from `code/01_data_preparation/01h_nonemployed_pool.py`, `code/02_descriptive_analysis/{02b,02d,02f}*.py`, `code/00_setup/00_config.py`; provenance from `docs/entry_from_nonemployment_methodology.md`, `Infrastructure/explorations/2026-07-09_entry-model-reality-assessment.md`, and the literature catalog (73 entries, validated).
**Confidence:** High that every number here matches current pipeline outputs (checked against the same run as the main draft); High on the sourcing claims (all anchors primary-verified this project); Medium on prose characterizations of contested literatures (Kleven vs. mainstream EITC estimates; hours-elasticity transport), which are flagged as such in text.
**Assumptions:** figures quoted (evidence-central 1.49M [status-differentiated ~10% penalty, λ=0.75, central eps: sm 0.24 / ow 1.07 / men 0.18; entrant gross $7.8B / net $5.8B]; conservative floor 1.02M; high joint corner 3.81M; full grid 0.23–3.81M; $45–48B net; 47.8%/21.7% below-target; ρσ +0.11; λ=0.75 × group SDs 0.29–0.55; 19/27/24 evidence-central-pool clawback medians; hours band 0.06/0.19/0.28M incumbent FTE vs ~0.7M entry FTE; PI-3 entrant-hours sensitivity rank/independent/median on the evidence-central pool; Heckman survey-weighted primary [WTFINL probit / EARNWT wage OLS], unweighted robustness) are the 2026-07-09 re-centered values and must be regenerated together with the main draft if the pipeline changes. Citation formatting is author-date prose style; convert to EIG footnote format at publication if this appendix ships publicly.
