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

    # order of bids smallest to largest
    order = np.argsort(bid_values)
    winner = order[-1]
    second = bid_values[order[-2]]
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


def sample_user(campaigns):
    user_demographics = [c for c in campaigns if c.count_attrs == 3]
    user_distribution = [c.average_users for c in user_demographics]
    sum_users = sum(user_distribution)
    user_distribution = [i * 1.0 / sum_users for i in user_distribution]
    chosen_demographic = random.choices(user_demographics, weights=user_distribution)[0]
    user = User(
        attr_gender=chosen_demographic.attr_gender,
        attr_age=chosen_demographic.attr_age,
        attr_income=chosen_demographic.attr_income,
    )
    return user


def generate_campaign(first_day=False):
    """
    output:
        campaign: Randomly generated campaign object, without budget (bidders must bid).
    """
    campaign = copy.deepcopy(random.choice(campaigns))
    reach_factor = random.choice([0.3, 0.5, 0.7])
    days = random.choice([1])
    campaign.length = days
    campaign.reach = days * reach_factor * campaign.average_users
    if first_day == True:
        campaign.budget = campaign.reach
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
        agent.add_campaign(generate_campaign(first_day=True))

    bid_buckets = [agent.bid_on_campaigns() for agent in agents]
    for _ in range(0, 10000):
        user = sample_user(campaigns)
        bids = [bucket.bid(user) for bucket in bid_buckets]
        # if sum(bids) == 0:
        # 	print(user.tostr())
        # 	print([a.active_campaigns[0].matches_user(user) for a in agents])
        winning_agent_idx, price = second_price_auction(bids)
        agents[winning_agent_idx].update_campaign(user, price)
    # print(sum([a.active_campaigns[0].matching_impressions for a in agents]))
    # print([a.active_campaigns[0].effective_reach() for a in agents])
    for a in agents:
        a.calculate_profit()
        # print(a.name, a.profit)
    # best_agent = np.argmax([a.profit for a in agents])
    # print("{} wins!".format(agents[best_agent].name))

    # return data in tidy form.
    return [{"name": agent.name, **agent.stats} for agent in agents]


if __name__ == "__main__":
    agents = get_one_AgentV0()
    output = pd.DataFrame(
        itertools.chain.from_iterable([run_1_day(agents) for _ in range(100)])
    )
    output.to_csv("1_day_1_campaign.csv", index=False)
    display = output[["name", "profit"]]
    profits = display.groupby("name").mean()
    print(profits)
