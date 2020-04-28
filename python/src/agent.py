import random

class Agent(object):
	def __init__(self, name):
		self.active_campaigns = []
		self.profit = 0
		self.name = name

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

	def calculate_profit(self):
		for campaign in self.active_campaigns:
			#TODO: Multi-day: only execute this if the campaign is over
			self.profit += (campaign.budget * campaign.effective_reach() - campaign.cost)
			self.active_campaigns.remove(campaign)

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
