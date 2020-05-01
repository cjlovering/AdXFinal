package agent;

import java.io.IOException;
import java.util.*;
import java.util.stream.Collectors;
import java.util.stream.Stream;

import com.google.common.collect.ImmutableMap;

import adx.agent.AgentLogic;
import adx.exceptions.AdXException;
import adx.server.OfflineGameServer;
import adx.structures.SimpleBidEntry;
import adx.util.AgentStartupUtil;
import adx.structures.Campaign;
import adx.structures.MarketSegment;
import adx.variants.ndaysgame.NDaysAdBidBundle;
import adx.variants.ndaysgame.NDaysNCampaignsAgent;
import adx.variants.ndaysgame.NDaysNCampaignsGameServerOffline;
import adx.variants.ndaysgame.Tier1NDaysNCampaignsAgent;
import com.google.common.collect.Sets;

public class MyNDaysNCampaignsAgent extends NDaysNCampaignsAgent {
	private static final String NAME = "Archer"; // TODO: enter a name. please remember to submit the Google form.
	private final double adBidShade;
	private final double campaignBidShade;
	private final int aggresiveStart;
	private final int aggresiveEnd;

	private static final Map<MarketSegment, Double> avg = Stream.of(
			new AbstractMap.SimpleEntry<>(MarketSegment.MALE_YOUNG_LOW_INCOME, 1836 / 1.0),
			new AbstractMap.SimpleEntry<>(MarketSegment.MALE_YOUNG_HIGH_INCOME, 517 / 1.0),
			new AbstractMap.SimpleEntry<>(MarketSegment.MALE_OLD_LOW_INCOME, 1795 / 1.0),
			new AbstractMap.SimpleEntry<>(MarketSegment.MALE_OLD_HIGH_INCOME, 808 / 1.0),
			new AbstractMap.SimpleEntry<>(MarketSegment.FEMALE_YOUNG_LOW_INCOME, 1980 / 1.0),
			new AbstractMap.SimpleEntry<>(MarketSegment.FEMALE_YOUNG_HIGH_INCOME, 256 / 1.0),
			new AbstractMap.SimpleEntry<>(MarketSegment.FEMALE_OLD_LOW_INCOME, 2401 / 1.0),
			new AbstractMap.SimpleEntry<>(MarketSegment.FEMALE_OLD_HIGH_INCOME, 407 / 1.0)
	).collect(Collectors.toMap(AbstractMap.SimpleEntry::getKey, AbstractMap.SimpleEntry::getValue));

	private static final Map<MarketSegment, Double> segmentReach = Stream.of(
			new AbstractMap.SimpleEntry<>(
					MarketSegment.MALE_YOUNG,
					2353/ 1.0),
			new AbstractMap.SimpleEntry<>(
					MarketSegment.FEMALE_YOUNG,
					2236/ 1.0),
			new AbstractMap.SimpleEntry<>(
					MarketSegment.MALE_OLD,
					2603/ 1.0),
			new AbstractMap.SimpleEntry<>(
					MarketSegment.FEMALE_OLD,
					2808/ 1.0),
			new AbstractMap.SimpleEntry<>(
					MarketSegment.YOUNG_LOW_INCOME,
					3816/ 1.0),
			new AbstractMap.SimpleEntry<>(
					MarketSegment.YOUNG_HIGH_INCOME,
					773/ 1.0),
			new AbstractMap.SimpleEntry<>(
					MarketSegment.OLD_LOW_INCOME,
					4196/ 1.0),
			new AbstractMap.SimpleEntry<>(
					MarketSegment.OLD_HIGH_INCOME,
					1215/ 1.0),
			new AbstractMap.SimpleEntry<>(
					MarketSegment.MALE_LOW_INCOME,
					3631/ 1.0),
			new AbstractMap.SimpleEntry<>(
					MarketSegment.MALE_HIGH_INCOME,
					1325/ 1.0),
			new AbstractMap.SimpleEntry<>(
					MarketSegment.FEMALE_LOW_INCOME,
					4381/ 1.0),
			new AbstractMap.SimpleEntry<>(
					MarketSegment.FEMALE_HIGH_INCOME,
					663/ 1.0)
	).collect(Collectors.toMap(AbstractMap.SimpleEntry::getKey, AbstractMap.SimpleEntry::getValue));


	public MyNDaysNCampaignsAgent() {
		// TODO: fill this in (if necessary)
		this.adBidShade = 0.99D;
		this.campaignBidShade = 0.20D;
		this.aggresiveStart = 0;
		this.aggresiveEnd = 10;
	}
	public MyNDaysNCampaignsAgent(double adBidShade, double campaignBidShade, int aggressiveStart, int aggressiveEnd) {
		// TODO: fill this in (if necessary)
		this.adBidShade = adBidShade;
		this.campaignBidShade = campaignBidShade;
		this.aggresiveStart = aggressiveStart;
		this.aggresiveEnd = aggressiveEnd;
	}
	public MyNDaysNCampaignsAgent(double adBidShade, double campaignBidShade) {
		// TODO: fill this in (if necessary)
		this.adBidShade = adBidShade;
		this.campaignBidShade = campaignBidShade;
		this.aggresiveStart = 0;
		this.aggresiveEnd = 10;
	}

	@Override
	protected void onNewGame() {
		// TODO: fill this in (if necessary)
	}
	
	@Override
	protected Set<NDaysAdBidBundle> getAdBids() throws AdXException {
		// TODO: fill this in
		
		Set<NDaysAdBidBundle> bundles = new HashSet<>();

//		double cost = this.getActiveCampaigns().stream().mapToDouble(c -> this.getCumulativeReach(c)).sum();
		int currentDay = this.getCurrentDay();

		if (currentDay > this.aggresiveEnd) {
			for (Campaign c : this.getActiveCampaigns()) {
				SimpleBidEntry entry = new SimpleBidEntry(
						c.getMarketSegment(),
						Math.max(0.1D,
//								adBidShade * (c.getBudget()) / (double) (c.getReach() + 1.0E-4D)),
 						0.75 * adBidShade * (c.getBudget() - this.getCumulativeCost(c)) / ((double)(c.getReach() - this.getCumulativeReach(c)) + 1.0E-4D)),

						Math.max(0.0D, adBidShade * c.getBudget() - this.getCumulativeCost(c)));
				NDaysAdBidBundle bundle = new NDaysAdBidBundle(
						c.getId(),
						Math.max(0.0D, 0.85 * (c.getBudget() - this.getCumulativeCost(c))),
						Sets.newHashSet(new SimpleBidEntry[]{entry}));
				bundles.add(bundle);
			}
		} else {
		for (Campaign c : this.getActiveCampaigns()) {
			SimpleBidEntry entry = new SimpleBidEntry(
					c.getMarketSegment(),
					Math.max(0.1D,
							adBidShade * (c.getBudget()) / (double)(c.getReach() + 1.0E-4D)),
//							adBidShade * (c.getBudget() - this.getCumulativeCost(c)) / ((double)(c.getReach() - this.getCumulativeReach(c)) + 1.0E-4D)),

					Math.max(0.0D, adBidShade * (c.getBudget() - this.getCumulativeCost(c))));
			NDaysAdBidBundle bundle = new NDaysAdBidBundle(
					c.getId(),
					Math.max(0.0D, 0.85 * c.getBudget() - this.getCumulativeCost(c)),
					Sets.newHashSet(new SimpleBidEntry[]{entry}));
			bundles.add(bundle);
		}
		}

//		while(var2.hasNext()) {
//			Campaign c = (Campaign)var2.next();
//			SimpleBidEntry entry = new SimpleBidEntry(
//					c.getMarketSegment(),
//					Math.max(0.1D,
//							(c.getBudget() - this.getCumulativeCost(c)) / ((double)(c.getReach() - this.getCumulativeReach(c)) + 1.0E-4D)),
//					Math.max(1.0D, c.getBudget() - this.getCumulativeCost(c)));
//			NDaysAdBidBundle bundle = new NDaysAdBidBundle(
//					c.getId(),
//					Math.max(1.0D, c.getBudget() - this.getCumulativeCost(c)),
//					Sets.newHashSet(new SimpleBidEntry[]{entry}));
//			set.add(bundle);
//		}
		
		return bundles;
	}

	@Override
	protected Map<Campaign, Double> getCampaignBids(Set<Campaign> campaignsForAuction) throws AdXException {
		Map<Campaign, Double> bids = new HashMap<>();
		if (this.getCurrentDay() > this.aggresiveEnd) {
			for (Campaign c : campaignsForAuction) {
				// 0.35D --> ~2000
				// 0.25D --> ~3000
				// 0.20D --> ~3500
				// 0.17D
				bids.put(c, (double) c.getReach() * campaignBidShade * 0.5);
			}
		} else {
			for (Campaign c : campaignsForAuction) {
				// 0.35D --> ~2000
				// 0.25D --> ~3000
				// 0.20D --> ~3500
				// 0.17D
				bids.put(c, (double) c.getReach() * campaignBidShade);
			}
		}
//		for (Campaign c : campaignsForAuction) {
//			// 0.35D --> ~2000
//			// 0.25D --> ~3000
//			// 0.20D --> ~3500
//			// 0.17D
//			bids.put(c, (double) c.getReach() * campaignBidShade);
//		}
		return bids;
	}

	public static void main(String[] args) throws IOException, AdXException {
		// Here's an opportunity to test offline against some TA agents. Just run
		// this file in Eclipse to do so.
		// Feel free to change the type of agents.
		// Note: this runs offline, so:
		// a) It's much faster than the online test; don't worry if there's no delays.
		// b) You should still run the test script mentioned in the handout to make sure
		// your agent works online.
		if (args.length == 0) {
			Map<String, AgentLogic> test_agents = new ImmutableMap.Builder<String, AgentLogic>()
					.put("me0", new MyNDaysNCampaignsAgent(0.02D, 0.88D)) //1641
					.put("opponent_2", new Tier1NDaysNCampaignsAgent())
					.put("opponent_3", new Tier1NDaysNCampaignsAgent())
					.put("opponent_4", new Tier1NDaysNCampaignsAgent())
					.put("opponent_5", new Tier1NDaysNCampaignsAgent())
					.put("opponent_6", new Tier1NDaysNCampaignsAgent())
					.put("opponent_7", new Tier1NDaysNCampaignsAgent())
					.put("opponent_8", new Tier1NDaysNCampaignsAgent())
					.put("opponent_9", new Tier1NDaysNCampaignsAgent())
//					.put("me1", new MyNDaysNCampaignsAgent(0.01D, 0.90D)) //1641
//					.put("me2", new MyNDaysNCampaignsAgent(0.01D, 0.90D)) // 1537
//					.put("me3", new MyNDaysNCampaignsAgent(0.01D, 0.90D)) // 1000
//					.put("me4", new MyNDaysNCampaignsAgent(0.01D, 0.90D))//1418
//					.put("me5", new MyNDaysNCampaignsAgent(0.01D, 0.90D)) // win win vs top 5
//					.put("me6", new MyNDaysNCampaignsAgent(0.01D, 0.90D)) //1877
//					.put("me7", new MyNDaysNCampaignsAgent(0.01D, 0.90D)) //1877
//					.put("me8", new MyNDaysNCampaignsAgent(0.01D, 0.90D)) //1877 win win vs all me
//					.put("me9", new MyNDaysNCampaignsAgent(0.01D, 0.90D))
					.build(); //1877
			//					.put("opponent_1", new Tier1NDaysNCampaignsAgent())
//					.put("opponent_2", new Tier1NDaysNCampaignsAgent())
//					.put("opponent_3", new Tier1NDaysNCampaignsAgent())
//					.put("opponent_4", new Tier1NDaysNCampaignsAgent())
//					.put("opponent_5", new Tier1NDaysNCampaignsAgent())
//					.put("opponent_6", new Tier1NDaysNCampaignsAgent())
//					.put("opponent_7", new Tier1NDaysNCampaignsAgent())
//					.put("opponent_8", new Tier1NDaysNCampaignsAgent())
//					.put("opponent_9", new Tier1NDaysNCampaignsAgent()

//					.put("me0", new MyNDaysNCampaignsAgent(0.10D, 0.15D)) //1641
//					.put("me1", new MyNDaysNCampaignsAgent(0.90D, 0.15D)) //1641
//					.put("me2", new MyNDaysNCampaignsAgent(0.80D, 0.20D)) // 1537
//					.put("me3", new MyNDaysNCampaignsAgent(0.75D, 0.20D)) // 1000
//					.put("me4", new MyNDaysNCampaignsAgent(0.80D, 0.20D))//1418
//					.put("me5", new MyNDaysNCampaignsAgent(0.95D, 0.20D)) // win win vs top 5
//					.put("me6", new MyNDaysNCampaignsAgent(0.75D, 0.15D)) //1877
//					.put("me7", new MyNDaysNCampaignsAgent(0.80D, 0.15D)) //1877
//					.put("me8", new MyNDaysNCampaignsAgent(0.85D, 0.15D)) //1877 win win vs all me
//					.put("me9", new MyNDaysNCampaignsAgent(0.90D, 0.15D))

			// Don't change this.
			OfflineGameServer.initParams(new String[] { "offline_config.ini", "CS1951K-FINAL" });
			AgentStartupUtil.testOffline(test_agents, new NDaysNCampaignsGameServerOffline());
		} else {
			// Don't change this.
			AgentStartupUtil.startOnline(new MyNDaysNCampaignsAgent(), args, NAME);
		}
	}

}
