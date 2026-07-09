# What the 80-80 wage subsidy would cost—and how many Americans it would put back to work

*Draft: 2026-07-08 | Authors: Benjamin Glasner and Adam Ozimek | Status: internal draft (pre-review)*
*Series: Agglomerations, installment three, following "How to End Low-Wage Work Forever" and its FAQ sequel.*

The 80-80 wage subsidy would raise pay for 20.8 million American workers at a net fiscal cost of roughly $72 billion to $78 billion per year—and expand work on two margins: roughly 1.48 million non-workers drawn into jobs (a deliberately conservative floor sits near 1 million), plus the equivalent of a quarter-million full-time workers in added hours among part-timers already on payrolls.

**Why it matters:** When we proposed the 80-80 wage subsidy, we deferred the hardest questions—what it costs, who gets the money, and how many non-workers it actually pulls into jobs. We have now built a full microsimulation to answer them, and the results sharpen the case in one direction and complicate it in another: the subsidy costs far less per new job than the industrial-policy alternatives, but the safety net claws back roughly half of its value for the single mothers it is best positioned to help.

A quick refresher for new readers: the 80-80 wage subsidy fills 80 percent of the gap between a worker's employer-paid wage and a target wage set at 80 percent of the national median wage, paid out in every paycheck. The formula treats $7.25 per hour, the federal minimum wage, as the lowest creditable base wage, which blunts any incentive to misreport pay.[^1] Figure 1 shows the schedule: the lower the employer wage, the larger the fill, and every dollar of employer raise still lifts take-home pay.

**Figure 1. How the 80-80 subsidy fills the wage gap.**

![How the 80-80 subsidy fills the wage gap](../output/figures/main/fig01_subsidy_schedule.png)

One housekeeping note before the numbers. The original posts used 2024 data, with a $20 median wage and a $16 target. The simulation uses the most recent 12 months of Current Population Survey data (May 2025 through May 2026), which put the weighted median hourly wage for paid-hourly workers at $21.00 and the target at $16.80. Every figure below reflects the updated data.[^2]

The rest of this post follows the format of the FAQ: the questions we expect you to ask, in the order we expect you to ask them.

## What does it cost?

Start with the static answer—assume nobody changes their behavior. The subsidy reaches 20.8 million workers at a gross cost of just under $90 billion per year. After the federal government recaptures taxes on the subsidy and banks savings from safety-net programs, the net cost falls to $72.1 billion. The average recipient collects $4,314 per year in subsidy and keeps roughly $3,400 to $3,500 in net income after those interactions.

People do change their behavior, so we model that two ways. A reduced-form approach applies employment and hours elasticities benchmarked to the Earned Income Tax Credit (EITC) literature and Congressional Budget Office conventions. A structural search-and-matching model lets workers and firms bargain over the subsidy directly, holding incumbent wages sticky and varying the worker's bargaining share from 0.3 to 0.7. The two approaches land in nearly the same place.

**Table 1. Annual fiscal cost of the 80-80 wage subsidy, by modeling approach**

| Scenario | Gross cost ($ billions per year) | Net cost ($ billions per year) |
|---|---|---|
| Static (no behavioral response) | 89.8 | 72.1 |
| Reduced-form, lower | 92.3 | 73.6 |
| Reduced-form, central | 96.9 | 76.1 |
| Reduced-form, upper | 103.9 | 77.9 |
| Structural, sticky incumbent wages | 93.8–95.0 | 74.6–75.8 |
| Incumbent hours response (adds to any row above) | +0.8 to +3.3 | +0.3 to +1.9 |
| Incidence upper bound (all wages renegotiate) | up to 161.7 | — |

*Note: Net cost equals gross cost minus federal tax recapture and safety-net offsets. The hours-response row is the added cost if part-time workers extend their hours in response to the per-hour subsidy (see "How sure are you?"). The final row is a disclosed bound, not a forecast; see "Will employers just capture it?" below.*
*Source: Economic Innovation Group 80-80 wage subsidy simulation, 2026.*

Our central estimate: roughly $93 billion to $97 billion gross and $72 billion to $78 billion net per year, with perhaps $2 billion more if part-timers extend their hours. For scale, that net figure buys a per-paycheck raise for one in every seven or eight American workers. Figure 2 traces how the gross cost becomes the net cost: the government recaptures payroll and income taxes and banks safety-net savings, partly offset by higher Affordable Care Act premium tax credits.

**Figure 2. From gross to net: taxes and safety-net offsets.**

![From gross to net: taxes and safety-net offsets](../output/figures/main/fig02_cost_waterfall.png)

## Who gets the money?

The eligible population looks like the low-wage workforce, because it is the low-wage workforce: every paid-hourly worker earning between $7.25 and $16.80 per hour.

**Table 2. Who receives the subsidy (static eligible base, 20.81 million workers)**

| Group | Recipients (millions) | Share of recipients (%) | Share of the group's workers (%) |
|---|---|---|---|
| **Sex** | | | |
| Women | 12.34 | 59.3 | 19.0 |
| Men | 8.46 | 40.7 | 12.2 |
| **Age** | | | |
| 16–24 | 6.55 | 31.5 | 40.3 |
| 25–34 | 4.98 | 23.9 | 14.6 |
| 35–44 | 3.56 | 17.1 | 10.7 |
| 45–54 | 2.94 | 14.1 | 10.4 |
| 55–64 | 2.78 | 13.3 | 12.2 |
| **Education** | | | |
| Less than high school | 2.26 | 10.9 | 37.9 |
| High school diploma or GED | 8.57 | 41.2 | 23.6 |
| Some college or associate's degree | 6.56 | 31.5 | 19.3 |
| Bachelor's degree | 2.68 | 12.9 | 7.4 |
| Graduate degree | 0.73 | 3.5 | 3.4 |
| **Race and ethnicity** | | | |
| White, non-Hispanic | 9.41 | 45.2 | 12.6 |
| Hispanic | 5.95 | 28.6 | 21.1 |
| Black, non-Hispanic | 3.43 | 16.5 | 21.3 |
| Other | 2.02 | 9.7 | 13.3 |
| **Family type** | | | |
| Single, no children | 11.37 | 54.6 | 22.2 |
| Married, with children | 4.13 | 19.9 | 9.3 |
| Single, with children | 2.73 | 13.1 | 19.8 |
| Married, no children | 2.58 | 12.4 | 10.4 |

*Note: "Share of the group's workers" is recipients in the group divided by all hourly workers ages 16 to 64 in that same group (134.3 million weighted). The denominator is the wage-observed hourly workforce; it excludes the self-employed and workers without a measurable hourly wage. Overall, 15.5 percent of hourly workers receive the subsidy.*
*Source: Economic Innovation Group 80-80 wage subsidy simulation, 2026.*

The third column reframes the story. The share-of-recipients column tells you where the money pools; the share-of-workers column tells you how deeply the subsidy reaches into each group. Read together, three patterns stand out. First, the subsidy skews female both ways: women are 59.3 percent of recipients, and 19.0 percent of women hourly workers qualify versus 12.2 percent of men (men nonetheless collect a slightly larger average subsidy, $4,481 per year versus $4,199). Second, it reaches deepest among the youngest and the least credentialed: 40.3 percent of workers ages 16 to 24 qualify—the highest take-up of any group—as do 37.9 percent of workers without a high school diploma, against just 3.4 percent of those with a graduate degree. The subsidy concentrates on exactly the workers the last four decades of wage growth left behind. Third, single parents stand out on reach: 19.8 percent of single-parent hourly workers qualify, well above the 9.3 percent take-up among married parents, whose households more often clear the wage target on a second earner. Figure 3 shows the take-up rates side by side.

**Figure 3. Share of each group's hourly workers who qualify.**

![Share of each group's hourly workers who qualify](../output/figures/main/fig03_takeup_by_group.png)

The subsidy is also steeply progressive within the eligible range, by construction. The lower the wage, the larger the gap the subsidy fills.

**Table 3. Average annual subsidy by hourly wage**

| Hourly wage band | Workers (millions) | Average annual subsidy ($) |
|---|---|---|
| $7.25–9.00 | 1.93 | 11,773 |
| $9.00–11.00 | 1.70 | 8,573 |
| $11.00–13.00 | 3.31 | 6,221 |
| $13.00–16.80 | 13.87 | 2,301 |

*Source: Economic Innovation Group 80-80 wage subsidy simulation, 2026.*

**Figure 4. The lowest-wage workers receive the largest subsidies.**

![The lowest-wage workers receive the largest subsidies](../output/figures/main/fig04_subsidy_by_wage.png)

The geography works the same way, and it delivers on the place-based argument from the first post. Because the target wage is national but wages are local, money flows automatically to lagging labor markets. Figure 5 maps the pattern: the average subsidy in Louisiana is $5,521 per year and in Mississippi $5,529, versus $3,751 in California. Louisiana alone has 404,000 eligible workers; West Virginia has 134,000, averaging $4,734 each. No commission picks winners. The formula finds distressed places on its own.

**Figure 5. Average annual subsidy per eligible worker by state.**

![Average annual subsidy per eligible worker by state](../output/figures/main/fig05_avg_subsidy_by_state.png)

Finally, the subsidy does not operate in a vacuum. Its interactions with existing programs cut both ways, as a share of gross cost:

- **Supplemental Nutrition Assistance Program (SNAP):** savings equal to 13.0 percent of gross cost.
- **Medicaid and the Children's Health Insurance Program (CHIP):** savings equal to 14.4 percent.
- **Temporary Assistance for Needy Families (TANF) and the EITC:** savings equal to 3.2 and 1.6 percent, respectively.
- **Affordable Care Act (ACA) premium tax credits:** added costs equal to 26.4 percent of gross cost, because higher incomes shift some workers from Medicaid into subsidized marketplace coverage. This is a real fiscal interaction, not a modeling artifact, and any serious cost estimate has to carry it.

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
| **Evidence-central** | **1.48** |
| High (joint upper corner) | 3.80 |
| Full range across the parameter grid | 0.23–3.80 |
| *Evidence-central, by group* | |
| Single mothers | 0.24 |
| Other women | 1.06 |
| Men | 0.18 |

*Note: The three headline scenarios are internally-consistent bundles of the model's uncertain parameters, not single-lever excursions. The conservative floor applies no wage penalty; the evidence-central applies a modest, status-differentiated non-employment wage penalty (about 10 percent on average) that the offer-decay evidence supports; the high scenario is the joint upper corner (a 20 percent penalty, full offer dispersion, and the upper participation elasticities together). The full 0.23–3.80 million range spans every combination of the three uncertain axes—wage penalty, offer dispersion, and participation elasticity (see "How sure are you?").*
*Source: Economic Innovation Group 80-80 wage subsidy simulation, 2026.*

Our central estimate is 1.48 million non-workers drawn into work, with a deliberately conservative floor of 1.02 million and a joint upper corner of 3.80 million. The floor is what the model produces when it applies *no* discount to non-workers' potential wages; but the evidence is clear that wage offers decay during long spells out of work, so a zero penalty is a conservative choice, not a neutral one. The evidence-central corrects that one choice—applying a modest, status-differentiated penalty (lighter for the recently unemployed, heavier for the long-detached)—while leaving everything else at its central setting. We are candid that the model also runs the other way in places: it lets every viable match form instantly, prices no childcare or commuting costs, and omits unemployment insurance from the no-work baseline—each of which pushes the count *up*. The true center is genuinely two-sided; we headline the evidence-central estimate because a zero wage penalty is the one setting the evidence rules out. These figures model each non-worker as facing a *distribution* of wage offers around their predicted wage, not a single number: real labor markets offer the same person different wages at different employers, so every demographic group has some members the subsidy can reach. Figure 7 shows the scenarios by group, with reference marks scaling the closest real-world precedents to our pool; Figure 7b shows who the entrants are.

**Figure 7. Induced entry into work, by group (evidence-central, with floor–high range).**

![Induced entry into work, by group, evidence-central with floor to high range](../output/figures/main/fig07_entry_band_by_cell.png)

**Figure 7b. Who the model predicts will enter, by prior status.**

![Who the model predicts will enter, by prior status](../output/figures/main/fig07b_entrants_by_status.png)

The entrants look like the people a wage offer can actually move: about a third are unemployed job-seekers—whose monthly job-finding rates are five to six times those of other non-participants—and nearly all the rest are non-participants without disability or retirement barriers. The disabled and retired, who make up a third of the non-employed population, contribute about 3 percent of modeled entrants.

Where do those numbers come from? We want to be precise about provenance, because the band edges and the central estimate rest on different evidence. The central anchors stay on the EITC and CBO evidence base. The edges come from the closest real-world experiments with subsidy-like payments. The Canadian Self-Sufficiency Project, which paid large earnings supplements to long-term welfare recipients, raised any-employment by 10.4 percentage points in its second year—that anchors the upper edge for single mothers.[^3] MDRC's Paycheck Plus demonstration in New York City anchors the upper edge for men, and its Atlanta replication, which found no detectable employment effect, anchors the lower edge.[^4] For married and childless women, the entry estimates reflect the research finding that the EITC's negative effect on married women's employment operates through household-income phase-outs—phase-outs the 80-80 wage subsidy does not have, because it is assessed individually on each worker's own paycheck.

Is 1.48 million small? Measured against the historical record, it is not. The closest macro-scale precedent—the 1990s EITC expansion, worth thousands of dollars a year, permanent, aimed at the most wage-responsive population ever measured, and amplified by a boom and welfare reform—raised single mothers' employment by roughly 3.5 to 4 percentage points over six years through the subsidy channel alone.[^7] Scaled to our reachable pool, that is about 0.9 million entrants—just below our conservative *floor* of 1.02 million. Our evidence-central of 1.48 million sits well above that precedent, between the Paycheck Plus demonstrations and the exceptional response of the Self-Sufficiency Project, and our full range brackets everything from Paycheck Plus Atlanta's null to well beyond SSP. These effects also build over years, not months: Paycheck Plus's employment gains peaked in year three, and the 1990s surge took most of a decade. Our figures are steady-state levels, not first-year effects.

Two features of the entrants matter for interpreting the cost numbers. First, entrants start part-time and part-year: matched to comparable low-wage incumbents, they average roughly 975 hours of work per year. Second, that is precisely why the marginal cost per entrant is low—though how low depends on how entrant hours are assigned, a sensitivity we test explicitly and return to in the next section.

Three stress tests worth disclosing, all computed on the evidence-central pool. If no married person with an employed spouse ever enters—zeroing out household coordination entirely, a bound and not a prediction—the estimate falls from 1.48 million to 1.20 million. If take-up matches mature programs like the EITC and SNAP (roughly 80 percent) rather than the 100 percent we assume, it falls to 1.19 million, and costs scale down proportionally. And there is a bookkeeping choice worth understanding: participation elasticities are estimated as employment-*rate* responses—their natural base is the affected group's employed workforce—while our headline expresses entry as a share of the reachable non-employed pool. We report both bases so the convention is a visible choice rather than a hidden one; they bracket each other and raise single-mother entry when the employment-stock base is used.

The reachable population is disciplined by the wage distribution itself. Figure 8 plots the imputed potential wage offers of the non-employed pool: 47.8 percent fall below the $16.80 target, compared with 23.6 percent of paid-hourly workers—non-workers face worse wage prospects than workers, as selection implies, but most could still command offers above the target and are therefore beyond the subsidy's reach.

**Figure 8. Imputed potential wages of the non-employed, relative to the target.**

![Imputed potential wages of the non-employed, relative to the target](../output/figures/main/fig08_pool_wage_distribution.png)

## What about men specifically?

Honesty requires a direct answer here, because male non-employment motivated the first post: roughly 10 million prime-age men, 14 percent of the total, are without work, including about one in five in Louisiana and West Virginia.[^1]

The modeled male entry is real but modest—roughly 180,000 at the evidence-central estimate (about 120,000 at the conservative floor), rising toward 810,000 in the high scenario. The experimental record explains why we do not project more. In Paycheck Plus, employment gains concentrated among the most disadvantaged men: noncustodial fathers and the formerly incarcerated saw a 5.8 percentage point employment gain in the third year, though the pooled three-year estimate was not statistically significant, and the Atlanta replication found no effect at all.[^4] And the survey evidence is sobering about the pool itself: roughly half of prime-age men outside the labor force report a serious health condition, and a quarter to a third receive disability benefits—barriers a higher wage does not remove.[^6]

The right reading is not that a wage subsidy fails men. It is that a wage subsidy reaches the men a wage can reach—disproportionately unemployed job-seekers and the most disadvantaged—while leaving the broader prime-age male employment crisis, much of it rooted in health, disability, and demand-side exclusion, in need of complementary tools. We would rather report that finding straight than oversell the policy we proposed.

## Will employers just capture it?

The classic objection to wage subsidies is that employers pocket them by cutting wage offers. The structural model addresses this head-on.

Under the realistic assumption that incumbent workers' wages are sticky—existing pay does not instantly renegotiate when the subsidy arrives—firms capture about 2 percent of the gross subsidy at the central bargaining split, and no more than about 3 percent across the full range of bargaining assumptions. The subsidy overwhelmingly lands in workers' pockets. Part of the reason is the minimum wage itself: most new entrants earn near the $7.25 floor, where the law caps how far a firm can push the cash wage down to absorb the subsidy. Figure 9 contrasts the realistic sticky-wage case with the all-renegotiate bound.

**Figure 9. Employers capture little under realistic wage stickiness.**

![Employers capture little under realistic wage stickiness](../output/figures/main/fig09_firm_capture.png)

We also computed the theoretical worst case, and we want it on the record. If every wage in the economy immediately renegotiated, gross cost could rise to $162 billion and firm capture could reach 55 percent. We report this as a disclosed incidence bound, not a forecast: wholesale instant renegotiation of incumbent wages contradicts both the wage-rigidity evidence and ordinary experience of how pay adjusts. But readers deserve to see the bound, and program design—such as the $7.25 base-wage floor already in the proposal—exists precisely to keep reality near the sticky-wage case.

## What does it cost per new job, compared with the alternatives?

The first post cataloged what the United States currently pays for job creation: more than $154,000 per job under Buy American procurement rules, $106,000 to $196,000 per job for state and local business incentives, and roughly $900,000 per job saved by steel tariffs.[^5]

The subsidy's arithmetic is different in kind, so the comparison requires care. The costs attributable to new entrants—the subsidy payments the program makes only because those 1.48 million people entered work—total $8.5 billion gross per year, or about $5,700 gross and $4,200 net per new worker per year. That is the true marginal cost of each additional job, and it is low partly because entrants work part-time and part-year schedules. One caveat we test explicitly: that low figure depends on *how* we assign entrants their hours. Matching entrants to comparable low-wage incumbents by predicted wage puts them at the bottom of the hours ladder; assigning hours independently of predicted wage would roughly double entrant hours and the marginal cost per job (to around $10,300 gross). We flag the sensitivity rather than bury it.

But that figure is not constructed the same way as the per-job numbers above, and pretending otherwise would flatter our own proposal. Those figures divide a program's total cost by jobs created, for programs whose spending mostly flows elsewhere—procurement premiums, incumbent firms, and consumers paying tariff-inflated prices. The 80-80 wage subsidy's spending also mostly flows elsewhere: to raising pay for 20.8 million people who already work. The closest apples-to-apples comparison charges the subsidy's entire central net cost (roughly $74 billion, structural model) to its entrants, which yields about $51,000 per new job at the evidence-central estimate (ranging from roughly $20,000 in the high scenario to $74,000 at the conservative floor)—below the bottom of the state and local incentive range across that range, and far below Buy American and tariffs. And unlike those programs, the "overhead" here is not deadweight. It is a raise for a fifth of the hourly workforce, and job creation is a co-benefit rather than the purchase. Figure 10 places both constructions against the alternatives on a log scale.

**Figure 10. Cost per job: the 80-80 subsidy versus other job-creation policies.**

![Cost per job: the 80-80 subsidy versus other job-creation policies](../output/figures/main/fig10_cost_per_job.png)

## Does it play badly with the rest of the safety net?

Here is the finding we did not fully anticipate, and the one policymakers should sit with.

In the FAQ post, we argued the subsidy beats the EITC on work entry because it is per-paycheck, transparent, non-categorical, and free of the EITC's benefit cliff. The simulation vindicates that argument in structure—the 80-80 wage subsidy has no cliff of its own—but reveals it as incomplete in practice: **the subsidy inherits everyone else's cliffs.**

Under our modeling assumption that the subsidy is taxable and counts against means-tested benefit eligibility, benefit phase-outs bite hardest for single mothers. For the median single mother in the entry pool, the subsidy raises the net return to working by about 19 percent, versus about 27 percent for other women and 24 percent for men—every dollar of subsidy that raises her income also phases her out of SNAP, Medicaid, and TANF, and the interaction eats roughly a third of the advantage other entrants enjoy. That gap is narrower than earlier versions of this analysis suggested (once we model realistic variation in wage offers, the reachable single mothers sit less deep in the phase-out range), but the mechanism is unchanged and the knife-edge cases below show it at its sharpest.

The knife-edge cases are the starkest illustration: roughly one in nine of the modeled entrants clear their entry threshold only because employers pay above the bargained wage across a benefit cliff. Their entry decision balances on program-interaction details no worker can be expected to compute. Figure 11 shows why, for one representative single-parent household: net income climbs with earnings, then drops at the points where Medicaid and other benefits phase out.

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

- **Cost is the firm result.** Static, reduced-form, and structural approaches all land between $72 billion and $78 billion net per year, plus up to about $2 billion if part-timers extend their hours. Getting outside that range requires the all-wages-renegotiate scenario we consider implausible.
- **Entry is the wider band, and we vary its drivers jointly.** Three parameters move the entry estimate: the participation *elasticity* (genuine disagreement in the experimental record, between Paycheck Plus Atlanta's null and the Self-Sufficiency Project's exceptional response); wage-offer *dispersion* (how wide a distribution of offers each non-worker faces around their predicted wage, netting CPS measurement error out of the estimated spread); and wage-offer *levels* (the offer decay that long non-employment causes, which our cross-sectional wage model cannot detect—careful studies measure offers falling nearly 1 percent per month out of work[^8]). Rather than move one lever at a time, we report internally-consistent bundles: a conservative floor with no wage penalty (1.02 million), an evidence-central that applies the modest penalty the decay evidence supports (1.48 million), and a high joint corner that stacks all three upward (3.80 million). Across every combination the estimate spans 0.23 to 3.80 million (Figure 14). We headline the evidence-central because a zero wage penalty is the one setting the evidence rules out.
- **The hours margin matters nearly as much as entry.** Our benchmark hours elasticity (0.05) comes from the EITC literature—but the EITC's phase-out suppresses the very incentive the 80-80 preserves, since the subsidy pays in full on every added hour up to 40 per week. Under consensus elasticities for clean wage variation (0.2 to 0.33), part-time workers already on payrolls would add the equivalent of 0.25 million to 0.36 million full-time workers—alongside the entry margin's roughly 0.7 million full-time equivalents (Figure 15). How the entry margin's hours are assigned is itself a sensitivity: matching entrants to comparable incumbents by predicted wage places them at part-time schedules, and assigning hours independently would roughly double their full-time-equivalent contribution.
- **What would move the estimates:** the true wage opportunities of the long non-employed, hours responses among part-timers, take-up, and above all the statutory treatment of the subsidy in benefit eligibility, which shifts both the net cost and the composition of who enters.

**Figure 14. Induced entry across the parameter grid (penalty, dispersion, and elasticity).**

![Induced entry across the penalty, dispersion, and elasticity grid](../output/figures/main/fig14_mpl_uncertainty.png)

**Figure 15. The intensive margin: added hours among part-time incumbents.**

![The intensive margin: added hours among part-time incumbents](../output/figures/main/fig15_hours_margin.png)

Figure 13 makes the first point visual: the static, reduced-form, and structural models all cluster in the $72–78 billion net range; only the all-wages-renegotiate bound escapes it.

**Figure 13. Net annual cost is stable across models; only full wage renegotiation escapes the $72–78 billion range.**

![Net annual cost is stable across models; only full wage renegotiation escapes the range](../output/figures/main/fig13_cost_band.png)

One note on language. The model works by assigning each non-worker an entry threshold and asking whether the subsidy clears it. Those thresholds are calibration devices that bundle everything standing between a person and a job—health, caregiving, the value of time at home, the risk of losing benefits—not literal wage demands. No survey has ever measured the reservation wages of people outside the labor force, and we do not claim to have done so.

We built the simulation so that others can interrogate these choices: the [interactive version](https://eig-wage-subsidy.streamlit.app) is live, a [technical appendix](2026-07-09_technical-appendix.md) walks through every modeling decision and the evidence behind it, and the methodology documentation is public.

**The bottom line:** For roughly $72 to $78 billion net per year, the 80-80 wage subsidy would raise pay for 20.8 million workers, direct the largest checks to the poorest workers and the most distressed states, and expand work on two margins—roughly 1.48 million new entrants (a deliberately conservative floor near 1 million; as high as 3.80 million if the offer-decay, dispersion, and elasticity evidence all run to the top of their ranges), plus a quarter-million full-time-equivalents of added work from part-timers extending their hours. Its marginal cost per new job is a few thousand dollars, and even charging the program's entire net cost to its entrants yields a per-job price (about $51,000) below the state and local incentive programs the country already runs—with the difference that the "overhead" here is a raise for a fifth of the hourly workforce rather than deadweight. The remaining design questions are answerable. We just answered the expensive ones.

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
- Medium-high: net cost band across behavioral models ($72–78 billion), which is stable across independent modeling approaches.
- Medium: evidence-central entry estimate (1.48 million; status-differentiated ~10% penalty, λ=0.75, central elasticities) and its group/status composition; the conservative floor (1.02 million, no penalty) and the high joint corner (3.80 million) bound it, and the full 27-cell parameter grid (penalty × dispersion × elasticity) spans 0.23–3.80 million (`entry_scenario_grid.parquet`, `entry_headline_scenarios.parquet`).
- Medium: the incumbent hours margin (0.08–0.36 million FTE) — the eps_int band transports consensus intensive elasticities to this design; no program with the 80-80's exact no-phase-out per-hour structure has been evaluated.
- Medium: single-mother clawback finding; conditional on the modeling assumption that the subsidy is taxable and counts toward means-tested eligibility.
- Flagged: all [TO VERIFY] items are citation details (dates, URLs, exact report references), not simulation numbers. Resolve before publication.

**Assumptions**
- All simulation figures reflect the 2026-07-09 pipeline run; the vintage difference versus the posts ($21.00/$16.80 vs. $20/$16) is disclosed in the text.
- The potential-wage model is estimated on paid-hourly earners (the market the target prices); its selection correction is small on this frame (ρσ ≈ +0.08) and the three imputation variants converge, so the dominant potential-wage uncertainty is the disclosed non-employment wage-penalty band {0, 10, 20 percent}, anchored to measured wage-offer decay.
- Entry propensity within each demographic cell is weighted by prior labor-force status (CPS U→E vs N→E flow ratios; SSDI work-capacity evidence) and the employment probit; the calibrated cell totals are unchanged by this weighting.
- Table 2's "share of the group's workers" column: numerator and denominator are both computed from the adapted CPS ORG panel (`_load_and_adapt_org_panel`), so recipients match the published counts exactly; the denominator is the pre-wage-threshold base (paid-hourly, wage-observed, ages 16–64, `earnwt`>0, minus the child-dependent exclusion, `earnwt`/n_months weighted), 134.3 million weighted. It is the wage-observed hourly workforce, not all employed persons (self-employed and workers without a measurable hourly wage are excluded). This reconstructs the `pct_in_group` field that `02a_descriptive_stats.py` intends but currently emits as null because its `data/external/org_workers_*.parquet` base file is absent from this checkout.
- The subsidy is modeled as taxable income that counts against means-tested benefit eligibility; the clawback and knife-edge entry findings are conditional on this and would change under alternative statutory treatment.
- Sticky incumbent wages are treated as the realistic incidence case; the all-renegotiate scenario is presented as a bound only.
- The $20,000–$74,000 fully-loaded-cost-per-entrant range is author arithmetic ($75.2B structural central net divided by the 3.80M high-corner and 1.02M floor entrant counts respectively; ≈$51,000 at the 1.48M evidence-central); the ~$5,700 gross / ~$4,200 net marginal figures divide the evidence-central entrant-attributable costs ($8.5B/$6.2B) by 1.48M entrants.
- Entrant hours are quantile-matched (MPL percentile → incumbent hours percentile within cell), which concentrates entrants at part-time schedules (mean ≈ 976 hours per year at the evidence-central) and lowers marginal entrant cost. PI-3 is now computed on the evidence-central pool: `entrant_hours_sensitivity.parquet` reports the rank mapping alongside an independent-draw and a cell-median mapping; the independent draw roughly doubles entrant hours and the marginal cost per job (~$10,300 gross vs ~$5,700). The fiscal total is barely affected (entrants are a few $B of ~$94B); the marginal-cost and full-time-equivalent claims carry the sensitivity.
- Offer dispersion: mean-preserving lognormal spread around each person's conditional-mean imputation, with group-specific residual SDs (education × age, 0.29–0.55) scaled by λ=0.75 (central; nets out approximate CPS measurement error; band {0.50, 1.00} in Figure 14). Hash-quantile draws, salted independently of the entry lottery; deterministic.
- Firm-capture figures reflect the corrected entrant-incidence accounting (actual firm surplus at the possibly floor-pinned wage, not (1−β)·subsidy — post-implementation review finding PI-1, fixed 2026-07-08).
- Word count of body prose (excluding tables, figures, footnotes, and this section): approximately 2,900 words after the 2026-07-09 revision.
