import pymongo

print('Connecting to the DBMS...')
client = pymongo.MongoClient()
print('Connected...')

# drop existing collections

client.repo.drop_collection('asmts_2016')
client.repo.drop_collection('parcels')
client.repo.drop_collection('missing_parcels')
client.repo.drop_collection('failed_parcels')
client.repo.drop_collection('parcels_w_loc')
client.repo.drop_collection('parcels_wo_loc')
client.repo.drop_collection('parcels_misloc')
client.repo.drop_collection('residential')
client.repo.drop_collection('outliers')

# create new collections

client.repo.create_collection('asmts_2016')
client.repo.create_collection('parcels')
client.repo.create_collection('missing_parcels')
client.repo.create_collection('failed_parcels')
client.repo.create_collection('parcels_w_loc')
client.repo.create_collection('parcels_wo_loc')
client.repo.create_collection('parcels_misloc')
client.repo.create_collection('residential')
client.repo.create_collection('outliers')

print('Disconnecting from the DBMS...')
client.close()
print('Disconnected...')

# EOF