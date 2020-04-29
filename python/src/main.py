import itertools
import copy
import random
from agent import RandomAgent, Tier1Agent, AgentV0
from campaign import Campaign, User, campaigns
import numpy as np
import pandas as pd


def second_price_auction(bids):
    """
    input:
        bids: array of floats corresponding to each player's bids for the auction

    output:
        winning_bidder: index of highest value from bids. if no one bids it is randomly allotted!!!
        price_to_pay: second highest bid
    """
    bid_values = np.array(bids)

    # We shuffle the order of the bids so that we break ties randomly, rather than
    # based entirely off in the order of the bids.
    shuffled_order = np.arange(len(bids))
    np.random.shuffle(shuffled_order)

    # order of bids smallest to largest
    order = np.argsort(bid_values[shuffled_order])
    winner = shuffled_order[order[-1]]
    second = bid_values[shuffled_order[order[-2]]]
    return winner, second

    # bid_values_np = np.array(bid_values)

    # if (bid_values_np > 0).sum() == 1:
    #     # We have a single winner.
    #     return

    # if len(bids) == 1:
    #     return bids[0], 0
    # else:
    #     highest_bid = max(bids)
    #     all_highest_indices = [i for i, j in enumerate(bids) if j == highest_bid]
    #     if len(all_highest_indices) > 1:
    #         winning_bidder = random.choice(all_highest_indices)
    #         return winning_bidder, highest_bid
    #     else:
    #         winning_bidder = bids.index(highest_bid)

    #         new_list = copy.deepcopy(bids)

    #         # removing the largest element from temp list
    #         new_list.remove(highest_bid)
    #         # elements in original list are not changed
    #         # print(list1)

    #         price_to_pay = max(new_list)
    #         return winning_bidder, price_to_pay

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



# def sample_user(campaigns):
#     user_demographics = [c for c in campaigns if c.count_attrs == 3]
#     user_distribution = [c.average_users for c in user_demographics]
#     sum_users = sum(user_distribution)
#     user_distribution = [i * 1.0 / sum_users for i in user_distribution]
#     chosen_demographic = random.choices(user_demographics, weights=user_distribution)[0]
#     user = User(
#         attr_gender=chosen_demographic.attr_gender,
#         attr_age=chosen_demographic.attr_age,
#         attr_income=chosen_demographic.attr_income,
#     )
#     return user


def sample_users(campaigns, num_users):
    # Sample all users for the day.
    user_demographics = [c for c in campaigns if c.count_attrs == 3]
    user_distribution = [c.average_users for c in user_demographics]
    sum_users = sum(user_distribution)
    assert sum_users == 10_000, "double checking"
    user_distribution = [i * 1.0 / sum_users for i in user_distribution]
    chosen_demographics = random.choices(
        user_demographics, weights=user_distribution, k=num_users
    )
    users = [
        User(
            attr_gender=chosen_demographic.attr_gender,
            attr_age=chosen_demographic.attr_age,
            attr_income=chosen_demographic.attr_income,
        )
        for chosen_demographic in chosen_demographics
    ]
    return users


def generate_campaign(current_day=0, last_day=9):
    """
    output:
        campaign: Randomly generated campaign object, without budget (bidders must bid).
    """
    campaign = copy.deepcopy(random.choice(campaigns))
    reach_factor = random.choice([.3, .5, .7])
    length = random.choice(list(range(0, min((last_day + 1) - current_day, 3))))
    campaign.length = length
    campaign.reach = (length+1) * reach_factor * campaign.average_users
    if current_day == 0:
        campaign.budget = campaign.reach
    campaign.start_day = current_day
    return campaign


def get_all_random():
    agents = [RandomAgent("RandomAgent_{}".format(i)) for i in range(0, 10)]
    return agents


def get_one_tier1():
    agents = [RandomAgent("RandomAgent_{}".format(i)) for i in range(0, 9)] + [
        Tier1Agent("Tier1Agent_1")
    ]
    return agents


def get_all_tier1():
    agents = [Tier1Agent("Tier1Agent_{}".format(i)) for i in range(0, 10)]
    return agents


def get_one_AgentV0():
    agents = [Tier1Agent("Tier1Agent_{}".format(i)) for i in range(0, 9)] + [
        AgentV0("AgentV0")
    ]
    return agents


def run_1_day(agents):
    for agent in agents:
        agent.reset()
        agent.add_campaign(generate_campaign(current_day=0))

    bid_buckets = [agent.bid_on_campaigns() for agent in agents]
    for user in sample_users(campaigns, num_users=10_000):
        bids = [bucket.bid(user) for bucket in bid_buckets]
        print(bids)
        winning_agent_idx, price = second_price_auction(bids)
        agents[winning_agent_idx].update_campaign(user, price, bid_buckets[winning_agent_idx])

    for a in agents:
        a.end_of_day(0)

    # return data in tidy form.
    return [{"name": agent.name, **agent.stats} for agent in agents]


def run_multi_day(agents, last_day = 9):
    for current_day in range(0, last_day+1):
        if current_day == 0:
            for agent in agents:
                agent.reset()
                agent.add_campaign(generate_campaign(current_day, last_day))
        else:
            campaigns_up_for_bid = [generate_campaign(current_day, last_day) for i in range(0, 5)]
            bid_buckets = [agent.bid_on_new_campaigns(campaigns_up_for_bid) for agent in agents]
            for campaign in campaigns_up_for_bid:
                bids = [bucket.campaign_to_bid[campaign] for bucket in bid_buckets]
                quality_scores = [agent.quality_score for agent in agents]
                winning_agent_idx, budget = reverse_auction(bids, quality_scores, campaign.reach)
                campaign.budget = budget
                agents[winning_agent_idx].add_campaign(campaign)

        bid_buckets = [agent.bid_on_campaigns() for agent in agents]
        for user in sample_users(campaigns, num_users=10_000):
            bids = [bucket.bid(user) for bucket in bid_buckets]
            winning_agent_idx, price = second_price_auction(bids)
            agents[winning_agent_idx].update_campaign(user, price)

        for a in agents:
            a.end_of_day(current_day)
        '''if current_day != last_day:
            for a in agents:
                a.end_of_day(current_day)
                print(a.name, a.profit)'''
    assert sum([len(a.active_campaigns) for a in agents]) == 0, "No unresolved campaigns at auction close"
    #return data in tidy form
    #for agent in agents:
    #    print(agent.name, agent.profit, agent.stats["profit"])
    return [{"name": agent.name, **agent.stats} for agent in agents]

if __name__ == "__main__":
    agents = get_all_random()
    output = pd.DataFrame(
        itertools.chain.from_iterable([run_1_day(agents) for _ in range(10)])
    )
    output.to_csv("1_day_1_campaign.csv", index=False)
    display = output[["name", "profit"]]
    profits = display.groupby("name").mean()
    print(profits)
