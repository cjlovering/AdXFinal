import random

class Agent(object):
	def __init__(self, name):
		self.active_campaigns = []
		self.profit = 0
		self.name = name
		self.quality_score = 1

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
				#TODO: Multi-day: only execute this if the campaign is over
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

class RandomAgent(Agent):
	def __init__(self, name):
		super(RandomAgent, self).__init__(name)

	def bid_on_user(self, user):
		relevant = False
		bid = 0
		for campaign in self.active_campaigns:
			if campaign.matches_user(user) == True and campaign.matching_impressions < campaign.reach:
				relevant = True
		if relevant == True:
			bid = random.random()
		return bid

	def get_bid_for_campaign(self, campaign):
		return random.uniform(0.1 * campaign.reach, campaign.reach)
