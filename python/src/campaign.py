import numpy as np
import random


class Campaign(object):
    def __init__(
        self, average_users, attr_gender=None, attr_income=None, attr_age=None
    ):
        self.average_users = average_users
        self.attr_gender = attr_gender
        self.attr_age = attr_age
        self.attr_income = attr_income
        self.count_attrs = sum(
            [1 for x in [attr_gender, attr_age, attr_income] if x is not None]
        )
        self.length = None
        self.budget = None
        self.reach = None
        self.start_day = None
        self.matching_impressions = 0
        self.cost = 0
        self.id = round(random.randint(0, 1_000_000))

        assert (
            self.attr_age is not None
            or self.attr_gender is not None
            or self.attr_income is not None
        )

    def user_match_score(self, user):
        score = 0
        if self.attr_gender is not None and self.attr_gender == user.attr_gender:
            score += 1
        if self.attr_income is not None and self.attr_income == user.attr_income:
            score += 1
        if self.attr_age is not None and self.attr_age == user.attr_age:
            score += 1
        return score

    def matches_user(self, user):
        if (
            (self.attr_gender is None or self.attr_gender == user.attr_gender)
            and (self.attr_income is None or self.attr_income == user.attr_income)
            and (self.attr_age is None or self.attr_age == user.attr_age)
        ):
            return True
        else:
            return False

    def effective_reach(self):
        a = 4.08577
        b = 3.08577
        return (2 / a) * (
            np.arctan(a * (self.matching_impressions / self.reach) - b) - np.arctan(-b)
        )

    def tostr(self):
        return "Campaign with market segment {}_{}_{}:\n\tbudget {}\n\treach {}\n\t\tcurrently reached {}".format(
            self.attr_gender,
            self.attr_age,
            self.attr_income,
            self.budget,
            self.reach,
            self.matching_impressions,
        )


class User(object):
    def __init__(self, attr_gender, attr_income, attr_age):
        self.attr_gender = attr_gender
        self.attr_age = attr_age
        self.attr_income = attr_income

    def tostr(self):
        return "User {}_{}_{}".format(self.attr_gender, self.attr_age, self.attr_income)


campaigns = []
"""campaigns.append(Campaign(attr_gender="Male"))
campaigns.append(Campaign(attr_gender="Female"))
campaigns.append(Campaign(attr_age="Young"))
campaigns.append(Campaign(attr_age="Old"))
campaigns.append(Campaign(attr_income="High"))
campaigns.append(Campaign(attr_income="Low"))"""
campaigns.append(Campaign(average_users=2603, attr_gender="Male", attr_age="Old"))
campaigns.append(Campaign(average_users=2353, attr_gender="Male", attr_age="Young"))
campaigns.append(Campaign(average_users=1325, attr_gender="Male", attr_income="High"))
campaigns.append(Campaign(average_users=3681, attr_gender="Male", attr_income="Low"))
campaigns.append(Campaign(average_users=2808, attr_gender="Female", attr_age="Old"))
campaigns.append(Campaign(average_users=2236, attr_gender="Female", attr_age="Young"))
campaigns.append(Campaign(average_users=663, attr_gender="Female", attr_income="High"))
campaigns.append(Campaign(average_users=4381, attr_gender="Female", attr_income="Low"))
campaigns.append(Campaign(average_users=1215, attr_age="Old", attr_income="High"))
campaigns.append(Campaign(average_users=4196, attr_age="Old", attr_income="Low"))
campaigns.append(Campaign(average_users=773, attr_age="Young", attr_income="High"))
campaigns.append(Campaign(average_users=3816, attr_age="Young", attr_income="Low"))
campaigns.append(
    Campaign(average_users=808, attr_gender="Male", attr_age="Old", attr_income="High")
)
campaigns.append(
    Campaign(average_users=1795, attr_gender="Male", attr_age="Old", attr_income="Low")
)
campaigns.append(
    Campaign(
        average_users=517, attr_gender="Male", attr_age="Young", attr_income="High"
    )
)
campaigns.append(
    Campaign(
        average_users=1836, attr_gender="Male", attr_age="Young", attr_income="Low"
    )
)
campaigns.append(
    Campaign(
        average_users=407, attr_gender="Female", attr_age="Old", attr_income="High"
    )
)
campaigns.append(
    Campaign(
        average_users=2401, attr_gender="Female", attr_age="Old", attr_income="Low"
    )
)
campaigns.append(
    Campaign(
        average_users=256, attr_gender="Female", attr_age="Young", attr_income="High"
    )
)
campaigns.append(
    Campaign(
        average_users=1980, attr_gender="Female", attr_age="Young", attr_income="Low"
    )
)
