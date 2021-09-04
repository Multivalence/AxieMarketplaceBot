import aiohttp
import json

url = "https://axieinfinity.com/graphql-server-v2/graphql"


with open('./filters/axie-listing-criteria.json', 'r') as jsonFile:
    user_criteria = json.load(jsonFile)


async def _makeRequest():

    axies = []

    criteria = {
        'classes' : user_criteria['classes'],
        'hp' : user_criteria['health'],
        'skill' : user_criteria['skill'],
        'speed' : user_criteria['speed'],
        'morale' : user_criteria['morale']
    }

    payload = {
        "operationName": "GetAxieLatest",
        "variables": {
            "from": 0,
            "size": 10,
            "sort": "PriceAsc",
            "auctionType": "Sale",
            "criteria": criteria
        },
        "query": "query GetAxieLatest($auctionType: AuctionType, $criteria: AxieSearchCriteria, $from: Int, $sort: SortBy, $size: Int, $owner: String) {\n  axies(auctionType: $auctionType, criteria: $criteria, from: $from, sort: $sort, size: $size, owner: $owner) {\n    total\n    results {\n      ...AxieRowData\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment AxieRowData on Axie {\n  id\n  image\n  class\n  name\n  genes\n  owner\n  class\n  stage\n  title\n  breedCount\n  level\n  parts {\n    ...AxiePart\n    __typename\n  }\n  stats {\n    ...AxieStats\n    __typename\n  }\n  auction {\n    ...AxieAuction\n    __typename\n  }\n  __typename\n}\n\nfragment AxiePart on AxiePart {\n  id\n  name\n  class\n  type\n  specialGenes\n  stage\n  abilities {\n    ...AxieCardAbility\n    __typename\n  }\n  __typename\n}\n\nfragment AxieCardAbility on AxieCardAbility {\n  id\n  name\n  attack\n  defense\n  energy\n  description\n  backgroundUrl\n  effectIconUrl\n  __typename\n}\n\nfragment AxieStats on AxieStats {\n  hp\n  speed\n  skill\n  morale\n  __typename\n}\n\nfragment AxieAuction on Auction {\n  startingPrice\n  endingPrice\n  startingTimestamp\n  endingTimestamp\n  duration\n  timeLeft\n  currentPrice\n  currentPriceUSD\n  suggestedPrice\n  seller\n  listingIndex\n  state\n  __typename\n}\n"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, json=payload) as res:

            if res.status != 200:
                return False

            resp = await res.json()


    for i in resp['data']['axies']['results']:


        axie_info = {
            'class' : i['class'],
            'breed_count' : i['breedCount'],
            'health' : i['stats']['hp'],
            'speed' : i['stats']['speed'],
            'skill' : i['stats']['skill'],
            'morale' : i['stats']['morale'],
            'body_parts' : [x['name'] for x in i['parts']],
            'pureness' : len([x['class'] for x in i['parts'] if x['class'] == i['class']]),
            'numMystic' : [x['stage'] for x in i['parts']],
            'abilities' : [],
            'id' : str(i['id']),
            'url' : f"https://marketplace.axieinfinity.com/axie/{i['id']}",
            'image' : i['image'],
            'price' : round(int(i['auction']['currentPrice']) * 10 ** -18, 3),
            'time_left' : i['auction']['timeLeft']
        }

        for x in i['parts']:
            for j in x['abilities']:
                ability_name = j.get('name', None)
                axie_info['abilities'].append(ability_name)


        axies.append(axie_info)


    return axies



async def get_filtered_data():

    data = await _makeRequest()
    filtered_data = []

    if not data:
        return


    for axie in data:

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


        #Filtering Pureness
        if not len(user_criteria['pureness']) == 0:
            if user_criteria['pureness'][0] <= axie['pureness'] <= user_criteria['pureness'][1]:
                pass

            else:
                continue


        #Filtering numMystic
        if not len(user_criteria['numMystic']) == 0:
            for i in axie['numMystic']:

                if user_criteria['numMystic'][0] <= i <= user_criteria['numMystic'][1]:
                    pass

                else:
                    continue



        #Filtering Price

        if len(user_criteria['price']) == 0:
            filtered_data.append(axie)
            continue

        elif user_criteria['price'][0] <= axie['price'] <= user_criteria['price'][1]:
            filtered_data.append(axie)
            continue

        else:
            continue


    return filtered_data

