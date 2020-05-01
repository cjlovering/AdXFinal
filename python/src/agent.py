import math
import random


class Agent(object):
    def __init__(self, name):
        self.active_campaigns = []
        self.profit = 0
        self.stats = {"cost": 0, "revenue": 0, "profit": 0, "budget": 0, "reach": 0}
        self.quality_score = 1
        self.name = name

    def reset(self):
        self.active_campaigns = []
        self.stats = {"cost": 0, "revenue": 0, "profit": 0, "budget": 0, "reach": 0}
        self.quality_score = 1
        self.profit = 0

    def add_campaign(self, campaign):
        self.active_campaigns.append(campaign)

    def update_campaign(self, user, price, bucket):
        assigned_price = False  # To prevent us from double counting costs
        for campaign in self.active_campaigns:
            if campaign.matches_user(user) == True:
                campaign.matching_impressions += 1
                if assigned_price == False:
                    assigned_price = True
                    campaign.cost += price
                    if price != 0:
                        bucket.segment_specific_costs[bucket.selected_segment] += price

    def end_of_day(self, day, quality_score_alpha=0.5):
        keep = []
        for campaign in self.active_campaigns:
            if day == campaign.start_day + campaign.length:
                # The campaign is over.
                self.stats["cost"] += campaign.cost
                self.stats["revenue"] += campaign.budget * campaign.effective_reach()
                self.stats["profit"] += (
                    campaign.budget * campaign.effective_reach() - campaign.cost
                )
                self.stats["budget"] += campaign.budget
                self.stats["reach"] += campaign.reach
                self.profit += (
                    campaign.budget * campaign.effective_reach() - campaign.cost
                )
                self.quality_score = (
                    1 - quality_score_alpha
                ) + quality_score_alpha * campaign.effective_reach()
                keep.append(False)
            else:
                assert day < campaign.start_day + campaign.length
                keep.append(True)
        updated_campaigns = []
        for i, campaign_continues in enumerate(keep):
            if campaign_continues == True:
                updated_campaigns.append(self.active_campaigns[i])
        self.active_campaigns = updated_campaigns

    """def calculate_profit(self):
        for campaign in self.active_campaigns:
            # TODO: Multi-day: only execute this if the campaign is over

            # Track stats.
            self.stats["cost"] += campaign.cost
            self.stats["revenue"] += campaign.budget * campaign.effective_reach()
            self.stats["profit"] += (
                campaign.budget * campaign.effective_reach() - campaign.cost
            )
            self.stats["budget"] += campaign.budget
            self.stats["reach"] += campaign.reach

            self.profit += campaign.budget * campaign.effective_reach() - campaign.cost
            self.active_campaigns.remove(campaign)"""


class BidBucket:
    def __init__(self, user, segment_to_bid, segment_to_limit):
        self.user = user
        self.segment_to_bid = segment_to_bid
        self.segment_to_limit = segment_to_limit
        self.per_day_limit = float("inf")

        self.segment_specific_costs = {
            segment: 0 for segment in self.segment_to_bid.keys()
        }

    def bid(self, user):
        # We assume that an agent does not provide competition for itself,
        # and if its overlapping campaigns (eventually market segments)
        # both would place bids on a user, it would prefer the higher bid.
        total_spent = sum(
            self.segment_specific_costs[segment]
            for segment in self.segment_specific_costs.keys()
        )
        bid = 0

        # kludgy way to report what segment we're bidding on, so we can assign cost
        self.selected_segment = None

        for segment in self.segment_to_bid.keys():
            bid_for_this_segment = self.segment_to_bid[segment]
            if (
                segment.matches_user(user)
                and (
                    self.segment_specific_costs[segment] + bid_for_this_segment
                    < self.segment_to_limit[segment]
                )
                and total_spent < self.per_day_limit
            ):
                if bid_for_this_segment > bid:
                    bid = bid_for_this_segment
                    self.selected_segment = segment
        return bid


class RandomAgent(Agent):
    def __init__(self, name):
        super(RandomAgent, self).__init__(name)

    def report_user_bids(self):
        """Build a BidBucket for active campaigns, for bids on
        users throughout the current day.
        """
        segment_to_bid = {}
        segment_to_limit = {}
        for campaign in self.active_campaigns:
            segment = campaign.toSegment()
            segment_to_bid[segment] = random.random()
            segment_to_limit[segment] = campaign.budget
        # TODO: We should limit both the sub-campaigns and the sup-campaigns.
        return BidBucket(self, segment_to_bid, segment_to_limit)

    def report_campaign_bids(self, campaigns):
        """Build a BidBucket for new campaigns.
        """
        campaign_to_bid = {}
        for campaign in campaigns:
            campaign_to_bid[campaign] = random.uniform(
                0.1 * campaign.reach, campaign.reach
            )
        return campaign_to_bid


class Tier1Agent(Agent):
    def __init__(self, name):
        super(Tier1Agent, self).__init__(name)

    def report_user_bids(self):
        campaign_to_bid = {}
        campaign_to_limit = {}
        for campaign in self.active_campaigns:
            campaign_to_bid[campaign] = max(
                0.1,
                (campaign.budget - campaign.cost)
                / (campaign.reach - campaign.matching_impressions),
            )
            campaign_to_limit[campaign] = max(1, campaign.budget - campaign.cost)
        # TODO: We should limit both the sub-campaigns and the sup-campaigns.
        return BidBucket(self, campaign_to_bid, campaign_to_limit)

    def report_campaign_bids(self, campaigns):
        """Build a BidBucket for new campaigns.
        """
        campaign_to_bid = {}
        for campaign in campaigns:
            campaign_to_bid[campaign] = random.uniform(
                0.1 * campaign.reach, campaign.reach
            )
        return campaign_to_bid


class AgentV0(Agent):
    def __init__(self, name, ad_bid_shade=0.99, ad_limit_shade=0.85):
        super(AgentV0, self).__init__(name)
        self.ad_bid_shade = ad_bid_shade
        self.ad_limit_shade = ad_limit_shade

    def report_user_bids(self):
        campaign_to_bid = {}
        campaign_to_limit = {}
        for campaign in self.active_campaigns:
            campaign_to_bid[campaign] = max(
                0.1, (self.ad_bid_shade * campaign.budget / campaign.reach)
            )
            campaign_to_limit[campaign] = self.ad_limit_shade * campaign.budget
        # TODO: We should limit both the sub-campaigns and the sup-campaigns.
        # TODO: We should switch the BidBucket to work with marketsegments, not
        # campaigns.
        return BidBucket(self, campaign_to_bid, campaign_to_limit)

    def report_campaign_bids(self, campaigns):
        """Build a BidBucket for new campaigns.
        """
        campaign_to_bid = {}
        for campaign in campaigns:
            campaign_to_bid[campaign] = 0.2 * campaign.reach
        return campaign_to_bid
