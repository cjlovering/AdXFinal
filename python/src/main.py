import copy
import itertools
import random
import tqdm

import numpy as np
import pandas as pd

from agent import RandomAgent, Tier1Agent, AgentV0, Strongarm
from campaign import Campaign, User, campaigns
from deap import creator, base, tools, algorithms


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


def reverse_auction(bids, quality_scores, reach):
    """
    input:
        bids: array of floats corresponding to each player's bids for the auction

    output:
        winning_bidder: index of highest value from bids. if no one bids it is randomly allotted!!!
        price_to_pay: second highest bid
    """
    assert all([(bid == 0 or bid >= 0.1 * reach) for bid in bids])
    max_bid = max(bids)
    if sum(bids) == max_bid:  # Everyone bid 0 except for one player
        winning_bidder = bids.index(max_bid)
        budget = (
            reach
            / (1.0 * sum(sorted(quality_scores)[0:3]) / min(len(quality_scores), 3))
            * quality_scores[winning_bidder]
        )
        stats = {
            "default_win": 1.0,
            "q_avg": np.mean(quality_scores),
            "q_win": quality_scores[winning_bidder],
            "winning_bid": max_bid,
            "budget": budget,
            "reach": reach,
        }
        return winning_bidder, budget, stats
    else:
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

        stats = {
            "default_win": 0.0,
            "q_avg": np.mean(quality_scores),
            "q_win": quality_scores[winner],
            "winning_bid": bids[winner],
            "budget": budget,
            "reach": reach,
        }
        return winner, budget, stats


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

def get_one_strongarm():
    agents = [Tier1Agent("Tier1Agent_{}".format(i)) for i in range(0, 9)] + [
        Strongarm()
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
    ad_stats = []
    bid_buckets = [agent.report_user_bids() for agent in agents]
    for user in sample_users(campaigns, num_users=10_000):
        bids = [bucket.bid(user) for bucket in bid_buckets]
        winning_agent_idx, price, stats = second_price_auction(bids)
        stats["demographic"] = user.demographic()
        ad_stats.append(stats)
        agents[winning_agent_idx].update_campaign(
            user, price, bid_buckets[winning_agent_idx]
        )

    for a in agents:
        a.end_of_day(0)

    # return data in tidy form.
    return [{"name": agent.name, **agent.stats} for agent in agents], ad_stats


def runGenAlg(weights):
    ad_bid_shade, ad_limit_shade, campaign_bid_factor= weights
    agents = [Tier1Agent("Tier1Agent_{}".format(i)) for i in range(0, 9)] + [
        AgentV0("AgentV0", ad_bid_shade, ad_limit_shade, campaign_bid_factor)
    ]
    agent_data, ad_bid_data, campaign_stats = zip(
        *[
            run_multi_day(agents)
            for _ in tqdm.tqdm(range(10), desc="Game", leave=False)
        ]
    )
    for agent in agent_data[0]:
        if agent["name"] == "AgentV0":
            profit = agent["profit"]
            return profit,

def run_multi_day(agents, last_day=9):
    ad_stats_dfs = []
    campaign_stats = []
    for current_day in tqdm.tqdm(range(0, last_day + 1), desc="Day", leave=False):
        ad_stats = []
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
                winning_agent_idx, budget, stats = reverse_auction(
                    bids, quality_scores, campaign.reach
                )
                stats["day"] = current_day
                # currently used by our models.
                stats["demographic"] = campaign.toSegment().demographic()
                campaign_stats.append(stats)
                campaign.budget = budget
                agents[winning_agent_idx].add_campaign(campaign)

        bid_buckets = [agent.report_user_bids() for agent in agents]
        for user in tqdm.tqdm(
            sample_users(campaigns, num_users=10_000), desc="User", leave=False
        ):
            bids = [bucket.bid(user) for bucket in bid_buckets]
            winning_agent_idx, price, stats = second_price_auction(bids)
            stats["demographic"] = user.demographic()
            stats["day"] = current_day
            agents[winning_agent_idx].update_campaign(
                user, price, bid_buckets[winning_agent_idx]
            )
            ad_stats.append(stats)
        # Average
        ad_stats_dfs.append(
            pd.DataFrame(ad_stats)
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
    return (
        # Agent stats : List[Dict[*str, float]]
        [{"name": agent.name, **agent.stats} for agent in agents],
        # Ad stats : List[pd.DataFrame[*str, float]]
        ad_stats_dfs,
        # Campaign stats : List[Dict[*str, float]]
        campaign_stats,
    )


if __name__ == "__main__":
    if False:
        agents = get_all_random()
        agent_data, ad_bid_data = zip(*[run_1_day(agents) for _ in range(100)])
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
        if True:
            agents = get_one_strongarm()#get_one_AgentV0()
        if False:
            agents = get_one_AgentV0()
        agent_data, ad_bid_data, campaign_stats = zip(
            *[
                run_multi_day(agents)
                for _ in tqdm.tqdm(range(100), desc="Game", leave=False)
            ]
        )
        agent_df = pd.DataFrame(itertools.chain.from_iterable(agent_data))
        agent_df.to_csv("agent.csv", index=False)
        profit_df = agent_df[["name", "profit"]]
        profit_df = profit_df.groupby("name").mean()
        print(profit_df)

        ad_bid_df = pd.concat(itertools.chain.from_iterable(ad_bid_data))
        ad_bid_df.to_csv("bid.csv", index=False)
        print(ad_bid_df.groupby("day").mean())

        campaign_stats_df = pd.DataFrame(itertools.chain.from_iterable(campaign_stats))
        campaign_stats_df.to_csv("campaign.csv", index=False)
        print(campaign_stats_df.mean())
    if False:
        creator.create("FitnessMax", base.Fitness, weights=(1.0,))
        creator.create("Individual", list, fitness=creator.FitnessMax)
        toolbox = base.Toolbox()

        toolbox.register("attr_bool", random.random)
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, n=3)
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)
        toolbox.register("evaluate", runGenAlg)
        toolbox.register("mate", tools.cxTwoPoint)
        toolbox.register("mutate", tools.mutGaussian, mu = [.99, .85,.6], sigma = [.15,.15,.15],indpb=0.2)
        toolbox.register("select", tools.selBest, k=3)
        population = toolbox.population(n=10)
        NGEN=20
        for gen in tqdm.tqdm(range(NGEN), desc = "generations"):
            offspring = algorithms.varAnd(population, toolbox, cxpb=0.5, mutpb=0.1)
            fits = toolbox.map(toolbox.evaluate, offspring)
            for fit, ind in zip(fits, offspring):
                ind.fitness.values = fit
            population = toolbox.select(offspring, k=len(population))
            print(population)
        top10 = tools.selBest(population, k=10)
        print(top10)
        ad_bid_shade, ad_limit_shade, campaign_bid_factor= top10[0]
        agents = [Tier1Agent("Tier1Agent_{}".format(i)) for i in range(0, 9)] + [
            AgentV0("AgentV0", ad_bid_shade, ad_limit_shade, campaign_bid_factor)
        ]
        agent_data, ad_bid_data, campaign_stats = zip(
            *[
                run_multi_day(agents)
                for _ in tqdm.tqdm(range(100), desc="Game", leave=False)
            ]
        )
        agent_df = pd.DataFrame(itertools.chain.from_iterable(agent_data))
        agent_df.to_csv("agent.csv", index=False)
        profit_df = agent_df[["name", "profit"]]
        profit_df = profit_df.groupby("name").mean()
        print(profit_df)

        ad_bid_df = pd.concat(itertools.chain.from_iterable(ad_bid_data))
        ad_bid_df.to_csv("bid.csv", index=False)
        print(ad_bid_df.groupby("day").mean())

        campaign_stats_df = pd.DataFrame(itertools.chain.from_iterable(campaign_stats))
        campaign_stats_df.to_csv("campaign.csv", index=False)
        print(campaign_stats_df.mean())
