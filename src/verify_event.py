import numpy as np
import pandas as pd
import pickle
from on_chain import OnChain
from off_chain import OffChain


class Verification:

    def __init__(self):
        self.on_chain = OnChain()
        self.off_chain = OffChain()

    def retrieve_all_verified_events(self):
        """
        Verify events recorded in off-chain database and return tables of verified and
        unverified events according to on-chain storage.
        :return: verified events, unverified events
        """
        unverified_events = []
        select_query = """SELECT * FROM social_distancing"""
        retrieved_events = self.off_chain.select(select_query)
        events_df = pd.DataFrame(retrieved_events, columns=self.off_chain.cursor.column_names)
        for row, event in events_df.iterrows():
            verified = self.on_chain.verify_event(event["Event_ID"], event["Location"], event["Local_Time"], event["Violations"])
            if not verified:
                print("Event ID {} is not verifiable!".format(event["Event_ID"]))
                unverified_events.append(event["Event_ID"])
                events_df = events_df.drop([row])
        return events_df, unverified_events


if __name__ == "__main__":
    verify = Verification()
    events, unverified = verify.retrieve_all_verified_events()
    pickle.dump(unverified, open("unverified.p", "wb"))
    events.to_csv("../verified_data/verified_events.csv")
