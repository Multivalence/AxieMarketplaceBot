import aiohttp
import json

url = "https://axieinfinity.com/graphql-server-v2/graphql"


with open('./filters/axie-sold-criteria.json', 'r') as jsonFile:
    user_criteria = json.load(jsonFile)



async def _getAxieData(data):

    axies = []

    for i in data['data']['settledAuctions']['axies']['results']:

        payload = {
            "operationName": "GetAxieDetail",
            "variables": {
                "axieId": str(i['id'])
            },
            "query": "query GetAxieDetail($axieId: ID!) {\n  axie(axieId: $axieId) {\n    ...AxieDetail\n    __typename\n  }\n}\n\nfragment AxieDetail on Axie {\n  id\n  image\n  class\n  chain\n  name\n  genes\n  owner\n  birthDate\n  bodyShape\n  class\n  sireId\n  sireClass\n  matronId\n  matronClass\n  stage\n  title\n  breedCount\n  level\n  figure {\n    atlas\n    model\n    image\n    __typename\n  }\n  parts {\n    ...AxiePart\n    __typename\n  }\n  stats {\n    ...AxieStats\n    __typename\n  }\n  auction {\n    ...AxieAuction\n    __typename\n  }\n  ownerProfile {\n    name\n    __typename\n  }\n  battleInfo {\n    ...AxieBattleInfo\n    __typename\n  }\n  children {\n    id\n    name\n    class\n    image\n    title\n    stage\n    __typename\n  }\n  __typename\n}\n\nfragment AxieBattleInfo on AxieBattleInfo {\n  banned\n  banUntil\n  level\n  __typename\n}\n\nfragment AxiePart on AxiePart {\n  id\n  name\n  class\n  type\n  specialGenes\n  stage\n  abilities {\n    ...AxieCardAbility\n    __typename\n  }\n  __typename\n}\n\nfragment AxieCardAbility on AxieCardAbility {\n  id\n  name\n  attack\n  defense\n  energy\n  description\n  backgroundUrl\n  effectIconUrl\n  __typename\n}\n\nfragment AxieStats on AxieStats {\n  hp\n  speed\n  skill\n  morale\n  __typename\n}\n\nfragment AxieAuction on Auction {\n  startingPrice\n  endingPrice\n  startingTimestamp\n  endingTimestamp\n  duration\n  timeLeft\n  currentPrice\n  currentPriceUSD\n  suggestedPrice\n  seller\n  listingIndex\n  state\n  __typename\n}\n"
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url=url, json=payload) as res:

                if res.status != 200:
                    return False

                resp = await res.json()


        x = resp['data']['axie']

        axie_info = {
            'class' : x['class'],
            'breed_count' : x['breedCount'],
            'health' : x['stats']['hp'],
            'speed' : x['stats']['speed'],
            'skill' : x['stats']['skill'],
            'morale' : x['stats']['morale'],
            'body_parts' : [i['name'] for i in x['parts']],
            'abilities' : [],
            'owner_profile' : x['ownerProfile']['name'],
            'id' : str(i['id']),
            'url' : f"https://marketplace.axieinfinity.com/axie/{i['id']}",
            'image' : x['image'],
            'price' : int(i["transferHistory"]['results'][0]["withPrice"]) * 10 ** -18
        }

        for i in x['parts']:
            for j in i['abilities']:
                ability_name = j.get('name', None)
                axie_info['abilities'].append(ability_name)



        axies.append(axie_info)


    return axies


async def _makeRequest():

    payload = {
        "operationName": "GetRecentlyAxiesSold",
        "variables": {
            "from": 0,
            "size": 10,
            "sort": "Latest",
            "auctionType" : "Sale"
        },
        "query": "query GetRecentlyAxiesSold($from: Int, $size: Int) {\n  settledAuctions {\n    axies(from: $from, size: $size) {\n      total\n      results {\n        ...AxieSettledBrief\n        transferHistory {\n          ...TransferHistoryInSettledAuction\n          __typename\n        }\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment AxieSettledBrief on Axie {\n  id\n  name\n  image\n  class\n  breedCount\n  __typename\n}\n\nfragment TransferHistoryInSettledAuction on TransferRecords {\n  total\n  results {\n    ...TransferRecordInSettledAuction\n    __typename\n  }\n  __typename\n}\n\nfragment TransferRecordInSettledAuction on TransferRecord {\n  from\n  to\n  txHash\n  timestamp\n  withPrice\n  withPriceUsd\n  fromProfile {\n    name\n    __typename\n  }\n  toProfile {\n    name\n    __typename\n  }\n  __typename\n}\n"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, json=payload) as res:

            if res.status != 200:
                return False

            resp = await res.json()

    return await _getAxieData(resp)



async def get_filtered_data():

    data = await _makeRequest()
    filtered_data = []

    if not data:
        return


    for axie in data:

        # Filtering Classes
        for _class in axie['class']:

            if len(user_criteria['classes']) == 0:
                break

            if _class in user_criteria['classes']:
                break

        else:
            continue


        # Filtering Parts
        for part in axie['body_parts']:

            if len(user_criteria['parts']) == 0:
                break

            if part in user_criteria['parts']:
                break

        else:
            continue


        # Filtering Abilities

        for ability in axie['abilities']:

            if len(user_criteria['abilities']) == 0:
                break

            if ability in user_criteria['abilities']:
                break


        else:
            continue


        #Filtering Breed Count

        if not len(user_criteria['breedCount']) == 0:

            if user_criteria['breedCount'][0] <= axie['breed_count'] <= user_criteria['breedCount'][1]:
                pass

            else:
                continue



        #Filtering Health

        if not len(user_criteria['health']) == 0:

            if user_criteria['health'][0] <= axie['health'] <= user_criteria['health'][1]:
                pass

            else:
                continue


        #Filtering Speed

        if not len(user_criteria['speed']) == 0:

            if user_criteria['speed'][0] <= axie['speed'] <= user_criteria['speed'][1]:
                pass

            else:
                continue


        #Filtering Skill

        if not len(user_criteria['skill']) == 0:

            if user_criteria['skill'][0] <= axie['skill'] <= user_criteria['skill'][1]:
                pass

            else:
                continue


        #Filtering Price
        if not len(user_criteria['price']) == 0:

            if user_criteria['price'][0] <= axie['price'] <= user_criteria['price'][1]:
                pass

            else:
                continue


        #Filtering Morale

        if len(user_criteria['morale']) == 0:
            filtered_data.append(axie)
            continue

        elif user_criteria['morale'][0] <= axie['morale'] <= user_criteria['morale'][1]:
            filtered_data.append(axie)
            continue

        else:
            continue

    return filtered_data




