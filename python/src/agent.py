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

    def update_campaign(self,user,price):
        assigned_price = False #To prevent us from double counting costs
        for campaign in self.active_campaigns:
            if campaign.matches_user(user) == True:
                campaign.matching_impressions += 1
                if assigned_price == False:
                    assigned_price = True
                    campaign.cost += price

    def end_of_day(self, day, quality_score_alpha = .5):
        keep = []
        for campaign in self.active_campaigns:
            if day == campaign.start_day + campaign.length:
                #The campaign is over.
                self.stats["cost"] += campaign.cost
                self.stats["revenue"] += campaign.budget * campaign.effective_reach()
                self.stats["profit"] += (
                    campaign.budget * campaign.effective_reach() - campaign.cost
                )
                self.stats["budget"] += campaign.budget
                self.stats["reach"] += campaign.reach
                self.profit += (campaign.budget * campaign.effective_reach() - campaign.cost)
                self.quality_score = (1 - quality_score_alpha) + quality_score_alpha * campaign.effective_reach()
                keep.append(False)
            else:
                assert day < campaign.start_day + campaign.length
                keep.append(True)
        updated_campaigns = []
        for i, campaign_continues in enumerate(keep):
            if campaign_continues == True:
                updated_campaigns.append(self.active_campaigns[i])
        self.active_campaigns = updated_campaigns

    '''def calculate_profit(self):
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
            self.active_campaigns.remove(campaign)'''


class BidBucket:
    def __init__(self, user, campaign_to_bid, campaign_to_limit):
        self.user = user
        self.campaign_to_bid = campaign_to_bid
        self.campaign_to_limit = campaign_to_limit

    def bid(self, user):
        # We assume that an agent does not provide competition for itself,
        # and if its overlapping campaigns (eventually market segments)
        # both would place bids on a user, it would prefer the higher bid.
        bid = 0
        for campaign in self.user.active_campaigns:
            if (
                campaign.matches_user(user)
                and campaign.cost < self.campaign_to_limit[campaign]
            ):
                bid = max(self.campaign_to_bid[campaign], bid)
        return bid


class RandomAgent(Agent):
    def __init__(self, name):
        super(RandomAgent, self).__init__(name)

    def bid_on_user(self, user):
        relevant = False
        bid = 0
        for campaign in self.active_campaigns:
            if (
                campaign.matches_user(user) == True
                and campaign.matching_impressions < campaign.reach
            ):
                relevant = True
        if relevant == True:
            bid = random.random()
        return bid

    def bid_on_campaigns(self):
        campaign_to_bid = {}
        campaign_to_limit = {}
        for campaign in self.active_campaigns:
            campaign_to_bid[campaign] = random.random()
            campaign_to_limit[campaign] = campaign.budget
        # TODO: We should limit both the sub-campaigns and the sup-campaigns.
        return BidBucket(self, campaign_to_bid, campaign_to_limit)

    def bid_on_new_campaign(self, campaign):
        return random.uniform(0.1 * campaign.reach, campaign.reach)


class Tier1Agent(Agent):
    def __init__(self, name):
        super(Tier1Agent, self).__init__(name)

    def bid_on_campaigns(self):
        campaign_to_bid = {}
        campaign_to_limit = {}
        for campaign in self.active_campaigns:
            campaign_to_bid[campaign] = max(0.1, campaign.budget / campaign.reach)
            campaign_to_limit[campaign] = campaign.budget
        # TODO: We should limit both the sub-campaigns and the sup-campaigns.
        return BidBucket(self, campaign_to_bid, campaign_to_limit)


class AgentV0(Agent):
    def __init__(self, name, ad_bid_shade=0.99, ad_limit_shade=0.85):
        super(AgentV0, self).__init__(name)
        self.ad_bid_shade = ad_bid_shade
        self.ad_limit_shade = ad_limit_shade

    def bid_on_campaigns(self):
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
