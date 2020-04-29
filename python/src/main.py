import itertools
import copy
import random
from agent import RandomAgent
from campaign import Campaign, User, campaigns
import numpy as np

def second_price_auction(bids):
	"""
	input:
		bids: array of floats corresponding to each player's bids for the auction

	output:
		winning_bidder: index of highest value from bids. if no one bids it is randomly allotted!!!
		price_to_pay: second highest bid
	"""
	assert all([bid >= 0 for bid in bids])
	if len(bids) == 1:
		return bids[0], 0
	else:
		highest_bid = max(bids)
		all_highest_indices = [i for i, j in enumerate(bids) if j == highest_bid]
		if len(all_highest_indices) > 1:
			winning_bidder = random.choice(all_highest_indices)
			return winning_bidder, highest_bid
		else:
			winning_bidder = bids.index(highest_bid)

			new_list = copy.deepcopy(bids)

			# removing the largest element from temp list
			new_list.remove(highest_bid)
			# elements in original list are not changed
			# print(list1)

			price_to_pay = max(new_list)
			return winning_bidder, price_to_pay

def reverse_auction(bids, quality_scores, reach):
	"""
	input:
		bids: array of floats corresponding to each player's bids for the auction

	output:
		winning_bidder: index of highest value from bids. if no one bids it is randomly allotted!!!
		price_to_pay: second highest bid
	"""
	assert all([(bid == 0 or bid >= .1* reach) for bid in bids])
	if sum(bids) == max(bids): #Everyone bid 0 except for one player
		winning_bidder = bids.index(max(bids))
		budget = reach / (1.0 * sum(sorted(quality_scores)[0:3])/min(len(quality_scores), 3)) * quality_scores[winning_bidder]
	else:
		effective_bids = [bids[i] * quality_scores[i] for i in range(0, len(bids))]
		for i in range(0, len(effective_bids)):
			if effective_bids[i] == 0:
				effective_bids[i] = float("inf")
		lowest_bid = min(effective_bids)
		all_lowest_bidders = [i for i, j in enumerate(effective_bids) if j == lowest_bid]
		if len(all_lowest_bidders) > 1:
			winning_bidder = random.choice(all_lowest_bidders)
			budget = lowest_bid
		else:
			winning_bidder = effective_bids.index(lowest_bid)
			new_list = copy.deepcopy(effective_bids)
			new_list.remove(lowest_bid)
			budget = min(new_list) * quality_scores[winning_bidder]
	return winning_bidder, budget


def sample_user(campaigns):
	user_demographics = [c for c in campaigns if c.count_attrs == 3]
	user_distribution = [c.average_users for c in user_demographics]
	sum_users = sum(user_distribution)
	user_distribution = [i * 1.0 / sum_users for i in user_distribution]
	chosen_demographic = random.choices(user_demographics, weights=user_distribution)[0]
	user = User(attr_gender = chosen_demographic.attr_gender,
	 			attr_age = chosen_demographic.attr_age,
				attr_income = chosen_demographic.attr_income)
	return user

def generate_campaign(current_day=0):
	"""
	output:
		campaign: Randomly generated campaign object, without budget (bidders must bid).
	"""
	campaign = copy.deepcopy(random.choice(campaigns))
	reach_factor = random.choice([.3, .5, .7])
	length = random.choice(list(range(0, min(10 - current_day, 3))))
	campaign.length = length
	campaign.reach = (length+1) * reach_factor * campaign.average_users
	if current_day == 0:
		campaign.budget = campaign.reach
	campaign.start_day = current_day
	return campaign

if __name__ == "__main__":
	agents = [RandomAgent("RandomAgent{}".format(i)) for i in range(0, 10)]
	for current_day in range(0, 10):
		if current_day == 0:
			for agent in agents:
				agent.add_campaign(generate_campaign(current_day))
		else:
			campaigns_up_for_bid = [generate_campaign(current_day) for i in range(0, 5)]
			for campaign in campaigns_up_for_bid:
				bids = [agent.get_bid_for_campaign(campaign) for agent in agents]
				quality_scores = [agent.quality_score for agent in agents]
				winning_agent_idx, budget = reverse_auction(bids, quality_scores, campaign.reach)
				campaign.budget = budget
				agents[winning_agent_idx].active_campaigns.append(campaign)


		for user_idx in range(0,10000):
			user = sample_user(campaigns)
			bids = [agent.bid_on_user(user) for agent in agents]
			#if sum(bids) == 0:
			#	print(user.tostr())
			#	print([a.active_campaigns[0].matches_user(user) for a in agents])
			winning_agent_idx, price = second_price_auction(bids)
			agents[winning_agent_idx].update_campaign(user, price)
		#print(sum([a.active_campaigns[0].matching_impressions for a in agents if len(a.active_campaigns) > 0]))
		#print([a.active_campaigns[0].effective_reach() for a in agents])
		print("end of day {}. current profits:".format(current_day))
		for a in agents:
			a.end_of_day(current_day)
			print(a.name, a.profit)
	assert sum([len(a.active_campaigns) for a in agents]) == 0
	best_agent = np.argmax([a.profit for a in agents])
	print("{} wins!".format(agents[best_agent].name))
