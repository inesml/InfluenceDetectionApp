from twitter import *
import json
from py2neo import Graph, Node, Relationship
#from sets import Set
# from py2neo import watch


#authenticate("localhost:7474", "neo4j", "neo4j")

graph = Graph("http://neo4j:neo4j@localhost:7474/db/data/")

class KeyStore:

    def __init__(self, keyfile):
        self.keys = [line.rstrip('\n') for line in open(keyfile)]
        self.idx = 0
        key = self.keys[self.idx].split()
        self.api = Twitter(auth=OAuth(key[0], key[1], key[2], key[3]))

    def size(self):
        return len(self.keys)

    def change_credentials(self):
        self.idx = (self.idx + 1) % len(self.keys)
        key = self.keys[self.idx].split()
        self.api = Twitter(auth=OAuth(key[0], key[1], key[2], key[3]))

#hashtag a buscar
has_key = 'Manuela Carmena'

#1-CREATE CONSTRAINT ON (a:Author) ASSERT a.name is UNIQUE;
graph.run("CREATE CONSTRAINT ON (u:User) ASSERT u.userID IS UNIQUE")
graph.run("CREATE CONSTRAINT ON (m:Mentioned) ASSERT m.userID IS UNIQUE")
graph.run("CREATE CONSTRAINT ON (q:Quoted) ASSERT q.userID IS UNIQUE")
graph.run("CREATE CONSTRAINT ON (y:Replied) ASSERT y.userID IS UNIQUE")
graph.run("CREATE CONSTRAINT ON (r:Retweeted) ASSERT r.userID IS UNIQUE")
graph.run("CREATE CONSTRAINT ON (t:Retweeter) ASSERT t.userID IS UNIQUE")


#Buscamos los tweets que contienen un determinado hashtag : Timeline
def extract_tweet(key, hashtag):
    ''' Extrae el status de los tweets como diccionario'''
    search = key.search.tweets(q=hashtag, count =10, tweet_mode="extended")
    timeline = search['statuses']
    return timeline

def get_retweeters(key, id_tweet):
    ''' Extrae los ids de las personas que han retuiteado un determinado tuit, que buscamos con el id'''
    try:
        search_rt = key.statuses.retweeters.ids(_id=id_tweet)
        retweeters_id = search_rt['ids']
        return retweeters_id
    except KeyError:
        pass

def upload_tweets(timeline, key):
    for t in timeline:

        u = t["user"]
        e = t["entities"]

        tweet_user_name=u['name']
        tweet_id = t['id']
        user_timeline_ID = u['id']

        user = Node("User", name=tweet_user_name, type="Usuario", userID=u['id'],
                 screen_name=u['screen_name'], verified=u['verified'],
                 image=u['profile_image_url'], num_followers=u['followers_count'],
                 num_friends=u['friends_count'],
                 num_status=u['statuses_count'], language=u['lang'],
                 date_creation=u['created_at'],
                 num_fav_tweet=t['favorite_count'], num_rt_tweet=t['retweet_count'])
        graph.merge(user, "User", "userID")
        graph.push(user)
        # graph.run('MERGE (u:User)'
        #           'ON MATCH SET u.num_rt_tweet_2 = t["retweet_count"]'
        #           'RETURN u.name, u.num_rt_tweet_2')


        # for h in e.get("hashtags", []):
        #     hashtag = Node("Hashtag", name=h["text"].lower())
        #     graph.merge(hashtag)
        #     graph.merge(Relationship(hashtag, "TAGS", user))

        for m in e.get('user_mentions', []):
            mentionID = m['id']
            # llamamos a la api para sacar el perfil del usuario mencionado
            m_profile = key.users.show(_id=mentionID)
            mention = Node("Mentioned", name=m['name'], type="Mencionado",
                     userID=m['id'], screen_name=m['screen_name']
                           , verified=m_profile['verified'],
                           image=m_profile['profile_image_url'], num_followers=m_profile['followers_count'],
                           num_friends=m_profile['friends_count'],
                           num_status=m_profile['statuses_count'], languaje=m_profile['lang'],
                           date_creation=m_profile['created_at']
                           )
            graph.merge(mention,"Mentioned", "userID")
            graph.merge(Relationship(user, "MENTIONS", mention))


        replied_tweet = t.get("in_reply_to_status_id") # Id del tweet al que responde.
        # If the represented Tweet is a reply, this field will contain the integer representation of the original Tweets ID.

        reply = t.get("in_reply_to_user_id")
        if reply:
            r_tweet = key.statuses.show(_id=replied_tweet, tweet_mode="extended")  # saca el objeto tweet que ha sido respondido
            # reply_tweet = Node("Replied", userID=reply)
            r_user = key.users.show(_id=reply)
            reply_tweet = Node("Replied", type="Respondido", userID=reply,
                               screen_name=r_user['screen_name']
                               , verified= r_user['verified'],
                               image=r_user['profile_image_url'], num_followers=r_user['followers_count'],
                               num_friends=r_user['friends_count'],
                               num_status=r_user['statuses_count'], languaje=r_user['lang'],
                               date_creation=r_user['created_at'], num_fav_tweet=r_tweet['favorite_count'], num_rt_tweet=r_tweet['retweet_count']
                               )
            graph.merge(reply_tweet,"Replied", "userID")
            graph.merge(Relationship(user, "RESPONDS", reply_tweet))



        quoted_status = t.get("quoted_status", {}) #This field only surfaces when the Tweet is a quote Tweet. This attribute contains the Tweet object of the original Tweet that was quoted.
        quoted_id = t.get("quoted_status_id") #This field contains the integer value Tweet ID of the quoted Tweet
        # print('es quoted :')
        # print(quoted_id)
        # print(quoted_status)
        if quoted_status:
            uq = quoted_status["user"]
            eq = quoted_status['entities']
            quoted = Node("Quoted", name=uq['name'], type="Citado", userID=uq['id'],
                           screen_name=uq['screen_name'], verified=uq['verified'],
                           image=uq['profile_image_url'], num_followers=uq['followers_count'],
                           num_friends=uq['friends_count'],
                           num_status=uq['statuses_count'], languaje=uq['lang'],
                           date_creation=uq['created_at'],
                           num_fav_tweet=quoted_status['favorite_count'], num_rt_tweet=quoted_status['retweet_count'])
            graph.merge(quoted, "Quoted", "userID")
            graph.merge(Relationship(user, "QUOTED", quoted))

        ret = t.get("retweeted_status", {}).get(
            "id")  # este id es el del tweet hay que cambiarlo por el de los usuarios
        rett = t.get("retweeted_status", {})


        if ret:
            ur = rett["user"]
            er = rett["entities"]

            retweet = Node("Retweeted", name=ur['name'], type="Retuiteado", userID=ur['id'],
                        screen_name=ur['screen_name'], verified=ur['verified'],
                        image=ur['profile_image_url'], num_followers=ur['followers_count'],
                        num_friends=ur['friends_count'],
                        num_status=ur['statuses_count'], languaje=ur['lang'],
                        date_creation=ur['created_at'],
                        num_fav_tweet=rett['favorite_count'], num_rt_tweet=rett['retweet_count'])
            graph.merge(retweet,"Retweeted", "userID")
            graph.merge(Relationship(user, "RETWEETS", retweet))

            # Llamamos a la api para sacar los ids del tweet que han RT
            search_rt_list = key.statuses.retweeters.ids(_id=ret)
            ids_list = search_rt_list["ids"]

            # print(ids_list)
            if ids_list:
                for search_id in ids_list:

                    rt_profile = key.users.show(_id=search_id)    #son usuarios
                    u_rt=rt_profile
                    u_id = rt_profile["id"]
                    e_rt = rt_profile["entities"]
                    if u_id == user_timeline_ID:
                        pass
                    else:
                        retweeter = Node("Retweeter", name=u_rt['name'], type="Retuiteador", userID=u_rt['id'],
                                screen_name=u_rt['screen_name'], verified=u_rt['verified'],
                                image=u_rt['profile_image_url'], num_followers=u_rt['followers_count'],
                                num_friends=u_rt['friends_count'],
                                num_status=u_rt['statuses_count'], languaje=u_rt['lang'],
                                date_creation=u_rt['created_at'])
                        graph.merge(retweeter, "Retweeter", "userID")
                        graph.merge(Relationship(retweeter, "RETWEETS", retweet))

if __name__ ==  '__main__':
    key_store = KeyStore('./static/data/api_keys.txt')   # Leemos las claves del fichero con la funcion
    tries = 0
    requests = 0
    while True:
        try:
            timeline=extract_tweet(key_store.api, has_key)
            upload_tweets(timeline, key_store.api)


        except TwitterHTTPError as e:
            error_code = e.response_data['errors'][0]['code']
            if error_code == 'LIMIT_REACHED_ERROR':
                print 'All credentials limit reached, sleeping ...'