import aiohttp
from pprint import pprint

url = "https://graphql-gateway.axieinfinity.com/graphql"



async def _makeRequest(user_criteria):

    axies = []

    payload = {
        "operationName": "GetAxieLatest",
        "variables": {
            "from": 0,
            "size": 20,
            "sort": "PriceAsc",
            "auctionType": "Sale",
            "criteria" : {"classes" : user_criteria['classes'],
                          "breedCount" : user_criteria['breedCount'],
                          "pureness" : [i for i in range(user_criteria['pureness'][0], user_criteria['pureness'][1] + 1)]}
        },
        "query": "query GetAxieLatest($auctionType: AuctionType, $criteria: AxieSearchCriteria, $from: Int, $sort: SortBy, $size: Int, $owner: String) {\n  axies(auctionType: $auctionType, criteria: $criteria, from: $from, sort: $sort, size: $size, owner: $owner) {\n    total\n    results {\n      ...AxieRowData\n      __typename\n    }\n    __typename\n  }\n}\n\nfragment AxieRowData on Axie {\n  id\n  image\n  class\n  name\n  genes\n  owner\n  class\n  stage\n  title\n  breedCount\n  level\n  parts {\n    ...AxiePart\n    __typename\n  }\n  stats {\n    ...AxieStats\n    __typename\n  }\n  auction {\n    ...AxieAuction\n    __typename\n  }\n  __typename\n}\n\nfragment AxiePart on AxiePart {\n  id\n  name\n  class\n  type\n  specialGenes\n  stage\n  abilities {\n    ...AxieCardAbility\n    __typename\n  }\n  __typename\n}\n\nfragment AxieCardAbility on AxieCardAbility {\n  id\n  name\n  attack\n  defense\n  energy\n  description\n  backgroundUrl\n  effectIconUrl\n  __typename\n}\n\nfragment AxieStats on AxieStats {\n  hp\n  speed\n  skill\n  morale\n  __typename\n}\n\nfragment AxieAuction on Auction {\n  startingPrice\n  endingPrice\n  startingTimestamp\n  endingTimestamp\n  duration\n  timeLeft\n  currentPrice\n  currentPriceUSD\n  suggestedPrice\n  seller\n  listingIndex\n  state\n  __typename\n}\n"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url=url, json=payload) as res:

            if res.status != 200:
                return False

            resp = await res.json()

    try:
        resp_data = resp['data']['axies']['results']


    except TypeError:
        pprint(resp)
        return False

    for i in resp_data:


        axie_info = {
            'class' : i['class'],
            'breed_count' : i['breedCount'],
            'health' : i['stats']['hp'],
            'speed' : i['stats']['speed'],
            'skill' : i['stats']['skill'],
            'morale' : i['stats']['morale'],
            'body_parts' : [x['name'] for x in i['parts']],
            'body_parts_id' : [x['id'] for x in i['parts']],
            'pureness' : len([x['class'] for x in i['parts'] if x['class'] == i['class']]),
            'numMystic' : len([x['specialGenes'] for x in i['parts'] if x['specialGenes'] == "Mystic"]),
            'abilities' : [],
            'id' : str(i['id']),
            'url' : f"https://marketplace.axieinfinity.com/axie/{i['id']}",
            'image' : i['image'],
            'price' : round(int(i['auction']['currentPrice']) * 10 ** -18, 6),
            'time_left' : i['auction']['timeLeft']
        }


        for x in i['parts']:
            for j in x['abilities']:
                ability_name = j.get('name', None)
                axie_info['abilities'].append(ability_name)


        axies.append(axie_info)


    return axies



async def get_filtered_data(user_criteria):

    data = await _makeRequest(user_criteria)
    filtered_data = []

    if not data:
        return


    for axie in data:

        try:


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


            #Filtering Morale
            if not len(user_criteria['morale']) == 0:

                if user_criteria['morale'][0] <= axie['morale'] <= user_criteria['morale'][1]:
                    pass

                else:
                    continue


            # Filtering Parts
            if len(user_criteria['parts']) == 0:
                pass

            elif all(i.lower() in [x.lower() for x in axie['body_parts']] for i in user_criteria['parts']):
                pass

            else:
                continue


            # Filtering Abilities
            if len(user_criteria['abilities']) == 0:
                pass

            elif all(i.lower() in [x.lower() for x in axie['abilities']] for i in user_criteria['abilities']):
                pass


            else:
                continue


            #Filtering Breed Count

            if not len(user_criteria['breedCount']) == 0:

                if user_criteria['breedCount'][0] <= axie['breed_count'] <= user_criteria['breedCount'][1]:
                    pass

                else:
                    continue



            #Filtering numMystic
            if not len(user_criteria['numMystic']) == 0:

                if user_criteria['numMystic'][0] <= axie['numMystic'] <= user_criteria['numMystic'][1]:
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

        except AttributeError:
            continue

    print(filtered_data)
    return filtered_data

