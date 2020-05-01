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
        stats: dictionary of stats about the auction
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

    # computing stats for analysis
    demand = (bid_values > 0).sum()
    if demand > 0:
        _min = bid_values[(bid_values > 0)].min()
        _max = bid_values[(bid_values > 0)].max()
        _mean = bid_values[(bid_values > 0)].mean()
    else:
        _min, _max, _mean = 0, 0, 0
    stats = {
        "demand": demand,
        "min_bid": _min,
        "max_bid": _max,
        "mean_bid": _mean,
        "price": second,
    }
    return winner, second, stats

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
    assert all([(bid == 0 or bid >= 0.1 * reach) for bid in bids])
    if sum(bids) == max(bids):  # Everyone bid 0 except for one player
        winning_bidder = bids.index(max(bids))
        budget = (
            reach
            / (1.0 * sum(sorted(quality_scores)[0:3]) / min(len(quality_scores), 3))
            * quality_scores[winning_bidder]
        )
        return winning_bidder, budget
    else:
        # effective_bids = [bids[i] * quality_scores[i] for i in range(0, len(bids))]

        # # this is game logic that prohibits bids below 0.1 * reach.
        # # for i in range(0, len(effective_bids)):
        # #     if effective_bids[i] < 0.1 * reach:
        # #         effective_bids[i] = float("inf")
        # for i in range(0, len(effective_bids)):
        #     if effective_bids[i] == 0:
        #         effective_bids[i] = float("inf")

        quality_scores = np.array(quality_scores)
        bids = np.array(bids)
        # The bids are then divided by the agents’ respective quality scores to
        # arrive at effective bids, before they are entered into the auction.
        effective_bids = bids / quality_scores
        effective_bids[bids < 0.1 * reach] = np.inf
        shuffled_order = np.arange(len(bids))
        np.random.shuffle(shuffled_order)

        # Order bid indices smallest to largest
        order = np.argsort(effective_bids[shuffled_order])
        # Budget: the second-lowest budget times the winning agent’s quality score
        winner = shuffled_order[order[0]]
        second = shuffled_order[order[1]]
        budget = effective_bids[second] * quality_scores[winner]
        return winner, budget

    #     lowest_bid = min(effective_bids)
    #     all_lowest_bidders = [
    #         i for i, j in enumerate(effective_bids) if j == lowest_bid
    #     ]
    #     if len(all_lowest_bidders) > 1:
    #         winning_bidder = random.choice(all_lowest_bidders)
    #         budget = lowest_bid
    #     else:
    #         winning_bidder = effective_bids.index(lowest_bid)
    #         new_list = copy.deepcopy(effective_bids)
    #         new_list.remove(lowest_bid)
    #         budget = min(new_list) * quality_scores[winning_bidder]
    # return winning_bidder, budget


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


def generate_campaign(current_day=0):
    """
    output:
        campaign: Randomly generated campaign object, without budget (bidders must bid).
    """
    campaign = copy.deepcopy(random.choice(campaigns))
    reach_factor = random.choice([0.3, 0.5, 0.7])
    # length = random.choice(list(range(0, min((last_day + 1) - current_day, 3))))
    length = random.choice(list(range(0, 3)))
    campaign.length = length
    campaign.reach = (length + 1) * reach_factor * campaign.average_users
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
    bid_stats = []
    bid_buckets = [agent.report_user_bids() for agent in agents]
    for user in sample_users(campaigns, num_users=10_000):
        bids = [bucket.bid(user) for bucket in bid_buckets]
        winning_agent_idx, price, stats = second_price_auction(bids)
        stats["demographic"] = user.demographic()
        bid_stats.append(stats)
        agents[winning_agent_idx].update_campaign(
            user, price, bid_buckets[winning_agent_idx]
        )

    for a in agents:
        a.end_of_day(0)

    # return data in tidy form.
    return [{"name": agent.name, **agent.stats} for agent in agents], bid_stats


def run_multi_day(agents, last_day=9):
    bid_stats = []
    bid_stats_dfs = []
    for current_day in range(0, last_day + 1):
        if current_day == 0:
            for agent in agents:
                agent.reset()
                agent.add_campaign(generate_campaign(current_day))
        else:
            campaigns_up_for_bid = [generate_campaign(current_day) for _ in range(0, 5)]
            # Note: Less campaigns become available towards the end of the 10-day game.
            # The distribution of campaign lengths does not change -- those that would end
            # after the last day are filtered out.
            campaigns_up_for_bid = [
                campaign
                for campaign in campaigns_up_for_bid
                # If the day is day 8 (it is really the 9th day), so
                # if its length is 2 then its really a 3 day campaign, so
                # not(8 + 2 <= 9), so we're good.
                # If its length is 1, its really a 2 day campaign, and will
                # run both today (day 8 --> 9th day) and tomorrow (day 9 --> 10th day).
                if current_day + campaign.length <= last_day
            ]
            campaign_to_bids = [
                agent.report_campaign_bids(campaigns_up_for_bid) for agent in agents
            ]
            for campaign in campaigns_up_for_bid:
                bids = [
                    campaign_to_bid[campaign] for campaign_to_bid in campaign_to_bids
                ]
                quality_scores = [agent.quality_score for agent in agents]
                winning_agent_idx, budget = reverse_auction(
                    bids, quality_scores, campaign.reach
                )
                campaign.budget = budget
                agents[winning_agent_idx].add_campaign(campaign)

        bid_buckets = [agent.report_user_bids() for agent in agents]
        for user in sample_users(campaigns, num_users=10_000):
            bids = [bucket.bid(user) for bucket in bid_buckets]
            winning_agent_idx, price, stats = second_price_auction(bids)
            stats["demographic"] = user.demographic()
            stats["day"] = current_day
            agents[winning_agent_idx].update_campaign(
                user, price, bid_buckets[winning_agent_idx]
            )
            bid_stats.append(stats)
        # Average
        bid_stats_dfs.append(
            pd.DataFrame(bid_stats)
            .groupby(["demographic", "day"], as_index=False)
            .mean()
        )
        for a in agents:
            a.end_of_day(current_day)
        """if current_day != last_day:
            for a in agents:
                a.end_of_day(current_day)
                print(a.name, a.profit)"""
    assert (
        sum([len(a.active_campaigns) for a in agents]) == 0
    ), "No unresolved campaigns at auction close"
    # return data in tidy form
    # for agent in agents:
    #    print(agent.name, agent.profit, agent.stats["profit"])
    return [{"name": agent.name, **agent.stats} for agent in agents], bid_stats_dfs


if __name__ == "__main__":
    if False:
        agents = get_all_random()
        agent_data, ad_bid_data = zip(*[run_1_day(agents) for _ in range(10)])
        agent_df = pd.DataFrame(itertools.chain.from_iterable(agent_data))
        agent_df.to_csv("agent.csv", index=False)
        profit_df = agent_df[["name", "profit"]]
        profit_df = profit_df.groupby("name").mean()
        print(profit_df)

        ad_bid_df = pd.DataFrame(itertools.chain.from_iterable(ad_bid_data))
        ad_bid_df.to_csv("bid.csv", index=False)
        print(ad_bid_df.groupby("demographic").mean())
        print(ad_bid_df.drop("demographic", axis=1).mean())

    if True:
        agents = get_all_tier1()
        agent_data, ad_bid_data = zip(*[run_multi_day(agents) for _ in range(100)])
        agent_df = pd.DataFrame(itertools.chain.from_iterable(agent_data))
        agent_df.to_csv("agent.csv", index=False)
        profit_df = agent_df[["name", "profit"]]
        profit_df = profit_df.groupby("name").mean()
        print(profit_df)

        ad_bid_df = pd.concat(itertools.chain.from_iterable(ad_bid_data))
        ad_bid_df.to_csv("bid.csv", index=False)
        print(ad_bid_df.groupby("day").mean())
