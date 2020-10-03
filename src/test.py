from off_chain import OffChain

x = OffChain()
e = x.select("""SELECT * FROM social_distancing ORDER BY Event_ID DESC LIMIT 1""")
print(e)