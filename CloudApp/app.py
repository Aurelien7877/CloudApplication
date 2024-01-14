import streamlit as st
from pymongo import MongoClient
import pandas as pd
import time
import matplotlib.pyplot as plt
from collections import Counter
from datetime import datetime
import re

#mongodb+srv://admin:admin@cluster0.h0vu1xg.mongodb.net/
#mongodb+srv://<username>:<password>@cluster0.aqxnqvy.mongodb.net/
### SECTION -------------------------------------------------------------------
@st.cache_resource()
def init_connection(user):
    if user =="standard": ##
        return MongoClient("mongodb+srv://standard:standard@cluster0.aqxnqvy.mongodb.net/")
    elif user =="analyst": ##
        return MongoClient("mongodb+srv://analyst:analyst@cluster0.aqxnqvy.mongodb.net/")
    elif user =="admin": ##
        return MongoClient("mongodb+srv://admin:admin@cluster0.aqxnqvy.mongodb.net/")
    else: return 0


@st.cache_data()
def get_data():
    db = client.EpicGame #establish connection to the 'sample_guide' db
    items = db.GameCritic.find() # return all result from the 'planets' collection
    items = list(items)        
    return items
#data = get_data()
### SECTION -------------------------------------------------------------------


### SECTION Interface utilisateur avec authentification -----------------------------------------
# 
def user_login(username,password):
    
    # Ajoutez un bouton pour valider l'authentification
    if username == "standard" and password == "standard":
        st.write("✅ Connexion successful")
        st.write("Go to 'Queries' section !")
        return "standard"
    elif username == "analyst" and password == "analyst":
        st.write("✅ Connexion successful")
        st.write("Go to 'Queries' section !")
        return "analyst"
    elif username == "admin" and password == "admin":
        st.write("✅ Connexion successful")
        st.write("Go to 'Queries' section !")
        return "admin"
    else:
        st.error("❌ Username or password incorrect ❌")
        return None
### SECTION -------------------------------------------------------------------
    
### SECTION TEMPS D'EXECUTION -------------------------------------------------------------------
def time_execution(func, *args, num_iterations=10):
    execution_times = []

    for _ in range(num_iterations):
        start_time = time.time()
        result = func(*args)
        end_time = time.time()

        execution_time = end_time - start_time
        execution_times.append(execution_time)

    min_execution_time = min(execution_times)
    max_execution_time = max(execution_times)

    #Pour le calcul du temps d'exécutio  on enleve le temps minimum et maximum comme indiqué par l'enoncé)
    average_execution_time = (sum(execution_times)-min_execution_time-max_execution_time) / (num_iterations - 2) 

    st.write(f"Average Execution Time: {round(average_execution_time, 2)} seconds")
    st.write(f"Min Execution Time: {round(min_execution_time,2)} seconds")
    st.write(f"Max Execution Time: {round(max_execution_time,2)} seconds")
    st.subheader("Execution time for 10 requests")
    return execution_times
# Fonctions pour récupérer les données depuis MongoDB
def get_game_info(game_name):
    def query():
        db = client.EpicGame
        return db.GameCritic.find_one({"name": game_name}, {"_id": 0})

    return time_execution(query),query()

def get_genre_action_games():
    def query():
        db = client.EpicGame
        return list(db.GameCritic.find({"genres": {"$regex": "ACTION"}}, {"_id": 0, "name": 1, "genres": 1}))

    return time_execution(query),query()

def get_shadow_complex_reviews():
    def query():
        db = client.EpicGame
        result = db.GameCritic.find_one({"name": "Shadow Complex Remastered"}, {"_id": 0, "critic": 1})
        return result.get("critic", [])

    return time_execution(query), query()

def get_games_2020():
    def query():
        db = client.EpicGame
        return list(db.GameCritic.find({"release_date": {"$regex": "2020"}}, {"_id": 0, "name": 1, "release_date": 1}))

    results = query()

    # Extract the release months from the date strings and count the games per month
    release_dates = [result["release_date"] for result in results]
    release_months = [datetime.strptime(date, "%Y-%m-%dT%H:%M:%S.%fZ").month for date in release_dates]
    game_counts = Counter(release_months)

    # Create a list of game counts for each month
    game_counts_per_month = [game_counts.get(month, 0) for month in range(1, 13)]

    return time_execution(query),query(),game_counts_per_month

def get_games_genre_followers(genre, followers):
    def query():
        db = client.EpicGame
        pipeline = [{"$match": {"genres": {"$regex": genre}}},
            {"$lookup": {
                "from": "twitter_accounts",
                "localField": "id",
                "foreignField": "fk_game_id",
                "as": "twitter_account"
            }},
            {"$unwind": "$twitter_account"},
            {"$match": {
                "twitter_account.followers": {"$gt": followers}
            }},
            {"$sort":{"twitter_account.followers":-1}},
            {"$project": {
                "_id":0,
                "game_name": "$name",
                "followers": "$twitter_account.followers",
                "genre": "$genres"
            }}]
        
        result = db.GameCritic.aggregate(pipeline)
        return list(result)
    
    return time_execution(query),query()
    
def get_critics_game(game):
    def query():
        db = client.EpicGame
        pipeline = [{"$match": {"name": game}},
            {"$unwind": "$critic"},
            {"$project": {
                "_id": 0,
                "comment": "$critic.comment",
                "rating": "$critic.rating"}}]
        
        result = db.GameCritic.aggregate(pipeline)
        return list(result)
        
    return time_execution(query),query()

def get_game_hardware(OS, RAM):
    def query():
        db = client.EpicGame
        pipeline = [{"$lookup": {
                "from": "necessary_hardware",
                "localField": "id",
                "foreignField": "fk_game_id",
                "as": "hardware"}},
            {"$match": {
                "hardware.operacional_system": {"$regex": OS},
                "hardware.memory": {"$regex": RAM}}},
            {"$project": {
                "_id": 0,
                "name": 1,
                "price": 1,
                "platform": 1}}]
        
        result = db.GameCritic.aggregate(pipeline)
        return list(result)
        
    return time_execution(query),query()

def get_tweets_game(game_name):
    def query():
        db = client.EpicGame  
        result = db.tweets.find(
            {"twitter_account_id": 1},
            {"twitter_account_id": 1, "timestamp": 1, "text": 1}
        ).sort("timestamp", -1).limit(5)
        return list(result)
    
    return time_execution(query), query()



def get_critic_trend_game(game):
    def query():
        db = client.EpicGame
        pipeline = [
            {"$match": {"name": game}},
            {"$unwind": "$critic"},
            {"$project": {
                "date": {"$dateFromString": {"dateString": "$critic.date"}},
                "rating": "$critic.rating"
            }},
            {"$group": {
                "_id": {"year": {"$year": "$date"}, "month": {"$month": "$date"}},
                "averageRating": {"$avg": "$rating"}
            }},
            {"$sort": {"_id.year": 1, "_id.month": 1}},
            {"$project": {
                "month": {"$toString": "$_id.month"},
                "year": {"$toString": "$_id.year"},
                "averageRating": {"$toDouble": "$averageRating"},
                "_id": 0
            }}
        ]
        
        result = db.GameCritic.aggregate(pipeline)
        return list(result)
        
    return time_execution(query),query()
    
def get_engagement_rate():
    def query():
        db = client.EpicGame
        pipeline = [
            {
                "$match": {"quantity_likes": {"$ne": 0}}},
            {
                "$group": {
                    "_id": "$twitter_account_id",
                    "totalTweets": {"$sum": 1},
                    "totalLikes": {"$sum": "$quantity_likes"},
                    "totalReplies": {"$sum": "$quantity_replys"}}
            },
            {
                "$project": {
                    "_id": 1,
                    "totalTweets": 1,
                    "totalLikes": 1,
                    "totalReplies": 1,
                    "avgEngagementRate": {
                        "$cond": {
                            "if": {"$eq": ["$totalLikes", 0]},
                            "then": 0,
                            "else": {"$divide": ["$totalReplies", "$totalLikes"]}
                        }
                    }
                }
            },
            {
                "$sort": {"avgEngagementRate": -1}  # Sort by avgEngagementRate in descending order
            }
        ]

        result = db.tweets.aggregate(pipeline)
        return list(result)

    return time_execution(query), query()


def get_followers_ranking():
    def query():
        db = client.EpicGame
        pipeline = [{"$lookup": {
                            "from": "GameCritic",
                            "localField": "fk_game_id",
                            "foreignField": "id",
                            "as": "gameData"}},
                    {"$unwind": "$gameData"},
                    {"$group": {
                            "_id": "$gameData.publisher",
                            "avgFollowers": {"$avg": {"$toInt": "$followers"}}}},
                    {"$project": {
                            "_id": 0,
                            "publisher": "$_id",
                            "avgFollowers": {"$round": ["$avgFollowers", 0]}}},
                    {"$sort": {"avgFollowers": -1}}]
        
        result = db.twitter_accounts.aggregate(pipeline)
        return list(result)
        
    return time_execution(query),query()


def preprocess_ram(ram):
    # Handle empty strings, convert "MB" to gigabytes (GB), and remove non-digit characters
    if not ram:
        ram_gb = 0  # Default to 0 GB for empty strings
    else:
        ram = ram.lower()
        if 'mb' in ram:
            ram = re.sub(r'\D', '', ram)  # Remove non-digit characters
            ram_gb = float(ram) / 1024  # Convert MB to GB
        else:
            ram = re.sub(r'\D', '', ram)  # Remove non-digit characters
            if not ram:
                ram_gb = 0
            else:
                ram_gb = float(ram)  # Leave it as GB
    return ram_gb

def get_price_RAM():
    def query():
        db = client.EpicGame
        pipeline = [
            {
                "$lookup": {
                    "from": "necessary_hardware",
                    "localField": "id",
                    "foreignField": "fk_game_id",
                    "as": "hardware"
                }
            },
            {"$unwind": "$hardware"},
            {
                "$group": {
                    "_id": {
                        "$trim": {
                            "input": {"$toLower": "$hardware.memory"},  # Convert to lowercase
                            "chars": " "
                        }
                    },
                    "averagePrice": {"$avg": {"$toDouble": "$price"}},
                    "numGames": {"$sum": 1}  # Count the number of games in each RAM category
                }
            },
        ]

        result = db.GameCritic.aggregate(pipeline)
        return list(result)

    return time_execution(query), query()


def get_db_stats(client):
    return client.EpicGame.command('dbStats')

# Retrieve cluster shards information
def get_cluster_shards(client):
    shard_infos = []
    
    for db_name in client.list_database_names():
        for col_name in client[db_name].list_collection_names():
            try:
                shard_infos.append(client[db_name][col_name].index_information())
            except:
                print('bug a cause de la vue créée')
    
    return {'We were unfortunately enable to shard the database, because this option is only available with Atlas (which isn\'t free)'}
    #return client.EpicGame.command("serverStatus")

def get_all_indexes(client):
    # Returns all indexes in the MongoDB cluster
    indexes = {}
    for db_name in client.list_database_names():
        for col_name in client[db_name].list_collection_names():
            try :
                indexes[f"{db_name}.{col_name}"] = client[db_name][col_name].index_information()
            except :
                print('bug a cause de la vue créée')
    return indexes

def drop_indexes():
    db = client.EpicGame
    db.GameCritic.drop_index("id_1")
    db.necessary_hardware.drop_index("fk_game_id_1")

def create_indexes():
    db = client.EpicGame
    db.GameCritic.create_index([("id", 1)])
    db.necessary_hardware.create_index([("fk_game_id", 1)])


def create_relevant_indexes():
    db = client.EpicGame

    # Creating indexes for get_critic_trend_game
    db.GameCritic.create_index([("name", 1)])

    # Creating indexes for get_engagement_rate
    db.tweets.create_index([("twitter_account_id", 1)])
    db.tweets.create_index([("quantity_likes", 1)])

    # Creating indexes for get_followers_ranking
    db.twitter_accounts.create_index([("fk_game_id", 1)])
    db.GameCritic.create_index([("id", 1)])
    db.GameCritic.create_index([("publisher", 1)])

def get_server_status(client):
    # Implement logic to retrieve server status
    return client.EpicGame.command("serverStatus")

def get_collection_stats(db):
    # Implement logic to retrieve collection stats
    return db.command("dbStats")

def get_server_status(client):
    return client.EpicGame.command("serverStatus")

def get_db_stats(client, db_name):
    return client[db_name].command("dbStats")

def get_collection_stats(db, collection_name):
    return db.command("collstats", collection_name)

def get_current_op(client):
    return client.admin.command('currentOp')

def create_view(client, db_name, view_name, source_collection, pipeline):
    db = client[db_name]
    db.command('create', view_name, viewOn=source_collection, pipeline=pipeline)

def query_view(client, db_name, view_name):
    db = client[db_name]
    results = list(db[view_name].find().limit(10))  # Limiting the results for display
    return results

def ping_mongo(client):
    start = time.time()
    client.admin.command('ping')
    return time.time() - start

with st.sidebar:
    st.title("Cloud Application Project - MongoDB ✅​")
    st.subheader("By Arthur Scelles, Timothé Vital, Alexandre Smadja, Aurélien Pouxviel")
    st.title("Menu :")
    
    section = st.radio("Please select a section :", ["Authentification", "Queries"])

### SECTION -------------------------------------------------------------------
    
# Interface utilisateur avec authentification
selected_user=''
client=''


if section == "Authentification":
    st.subheader("Authentification : 🔒 ")
    st.caption('1. For Standard User, username = standard, password = standard ')
    st.caption('2. For Analyste / Business User, username = analyst, password = analyst ')
    st.caption('3. For Admin user, username = admin, password = admin ')

    username = st.text_input("Username :")
    password = st.text_input("Password :", type="password")

    login_button = st.button("Login")
    if login_button:
        
        selected_user = user_login(username,password)
        st.session_state.selected_user = selected_user
        client = init_connection(selected_user)
        
        st.session_state.client = client


# Interface utilisateur pour les requêtes
if section == "Queries":
    st.title("Queries : 📊 ")
    try:
        selected_user = st.session_state.selected_user
        client = st.session_state.client
        st.write("User :", selected_user)
    except:
        st.write("No User, please log in")
    if selected_user:
        st.title(f"Welcome, {selected_user}!")

        # Afficher les résultats en fonction de l'utilisateur sélectionné
        if selected_user == "analyst":
            user_choice = st.radio("Select a query :", ["Recherche d'un jeu par genre avec un minimum d'abonnés Twitter","Recherche des critiques d’un jeu spécifique", "Recherche de jeux avec des spécifications matérielles compatibles", 
                                                        "Identification des tendances temporelles dans les critiques d’un jeu", 
                                                        "Le nombre d’abonnés moyen sur twitter par éditeur de jeux ",
                                                        "La moyenne des prix des jeux selon leur RAM nécessaire"])

            if user_choice == "Recherche d'un jeu par genre avec un minimum d'abonnés Twitter":
                deroulantGenre = st.selectbox("Select the game genre",
                                        ("ACTION","PUZZLE","SHOOTER","PLATFORMER","MULTIPLAYER"))
                sliderMinFollowers = st.slider("Select the minimum of followers",
                                               0, 150000, 75000)
                query = st.button("Search")
                if query:
                    timequery, result = get_games_genre_followers(deroulantGenre, sliderMinFollowers)
                    df_execution_times = pd.DataFrame(timequery, columns=["Execution Time (s)"])
                    st.line_chart(df_execution_times)
                    st.write('Du jeu le plus suivi au jeu le moins suivi sur Twitter (X)')
                    st.dataframe(result)

            elif user_choice == "Recherche des critiques d’un jeu spécifique":
                deroulantJeu = st.selectbox("Select the game",
                                            ("Super Meat Boy", "Shadow Complex Remastered", "Alan Wake’s American Nightmare", "Ticket to Ride", "LEGO® Batman™ 2: DC Super Heroes"))
                query = st.button("Search")
                
                if query:
                    timequery, result = get_critics_game(deroulantJeu)
                    df_execution_times = pd.DataFrame(timequery, columns=["Execution Time (s)"])
                    st.line_chart(df_execution_times)
                    
                    # Calculate min, max, and average rating$
                    try:
                        df_reviews = pd.DataFrame(result)
                        df_reviews["rating"] = pd.to_numeric(df_reviews["rating"], errors='coerce')
                        # Sort the DataFrame by rating in descending order
                        df_reviews = df_reviews.sort_values(by="rating", ascending=False)
                        st.write('Resulting table sorted by rating')
                        st.dataframe(df_reviews)

                        min_rating = df_reviews["rating"].min()
                        max_rating = df_reviews["rating"].max()
                        avg_rating = df_reviews["rating"].mean()
                    
                        st.subheader("Additional Information:")
                        st.write(f"Minimum Rating: {min_rating:.2f}")
                        st.write(f"Maximum Rating: {max_rating:.2f}")
                        st.write(f"Average Rating: {avg_rating:.2f}")
                    except:
                        st.write('An error occured')

            elif user_choice == "Recherche de jeux avec des spécifications matérielles compatibles":
                deroulantOS = st.selectbox("Select the operating system",
                                           ("Vista", "XP", "Windows 7"))
                deroulantRAM = st.selectbox("Select the RAM",
                                            ("2 GB","4 GB", "8 GB"))
                query = st.button("Search")
                if query:
                    timequery, result = get_game_hardware(deroulantOS, deroulantRAM)
                    df_execution_times = pd.DataFrame(timequery, columns=["Execution Time (s)"])
                    st.line_chart(df_execution_times)
                    st.dataframe(result)

            elif user_choice == "Suivi des activités récentes d'un compte Twitter de jeu":
                deroulantJeu = st.selectbox("Select the game",
                                            ("Super Meat Boy", "Shadow Complex Remastered", "Alan Wake’s American Nightmare", "Ticket to Ride", "LEGO® Batman™ 2: DC Super Heroes"))
                query = st.button("Search")
                if query:
                    timequery, result = get_tweets_game(deroulantJeu)
                    df_execution_times = pd.DataFrame(timequery, columns=["Execution Time (s)"])
                    st.line_chart(df_execution_times)
                    st.dataframe(result)

            elif user_choice == "Identification des tendances temporelles dans les critiques d’un jeu":
                deroulantJeu = st.selectbox("Select the game",
                                            ("Super Meat Boy", "Shadow Complex Remastered", "Alan Wake’s American Nightmare", "Ticket to Ride", "The Bridge"))
                query = st.button("Search")
                if query:
                    timequery, result = get_critic_trend_game(deroulantJeu)
                    df_execution_times = pd.DataFrame(timequery, columns=["Execution Time (s)"])
                    st.line_chart(df_execution_times)
                    st.dataframe(result)
                    df = pd.DataFrame(result)
                    df['date'] = pd.to_datetime(df['year'] + '-' + df['month'].str.zfill(2), format='%Y-%m')

                    df.sort_values(by='date', inplace=True)
                    df.reset_index(drop=True, inplace=True)
                    st.write(f"Tendance des critiques pour le jeu {deroulantJeu}")
                    st.line_chart(df.set_index('date')['averageRating'], use_container_width=True)



            elif user_choice == "Classement des jeux ayant le meilleur taux d’engagement sur Twitter pour chaque genre":
                query = st.button("Search")
                if query:
                    timequery, result = get_engagement_rate()
                    df_execution_times = pd.DataFrame(timequery, columns=["Execution Time (s)"])
                    st.line_chart(df_execution_times)
                    st.dataframe(result)

            elif user_choice == "Le nombre d’abonnés moyen sur twitter par éditeur de jeux ":
                query = st.button("Search")
                if query:
                    timequery, result = get_followers_ranking()
                    df_execution_times = pd.DataFrame(timequery, columns=["Execution Time (s)"])
                    st.line_chart(df_execution_times)
                    st.dataframe(result)

                    df = pd.DataFrame(result)
                    df_sorted = df.sort_values(by='avgFollowers', ascending=False)
                    df_top_10 = df_sorted.head(10)
                    df_top_10.set_index('publisher', inplace=True)
                    st.write("Average Followers Ranking by Publisher")
                    st.bar_chart(df_top_10['avgFollowers'])

            elif user_choice == "La moyenne des prix des jeux selon leur RAM nécessaire":
                if st.button("Run Query with existing indexes (recommended)"):
                    # Initial Query Execution
                    timequery, result = get_price_RAM()
                    df_execution_times = pd.DataFrame(timequery, columns=["Execution Time (s)"])
                    st.line_chart(df_execution_times)

                    # Data Preprocessing
                    df = pd.DataFrame(result)
                    df['_id'] = df['_id'].apply(preprocess_ram)  # Convert RAM to GB
                    df['averagePrice'] = df['averagePrice'].round(2)  # Round the average price

                    # Display Average Prices
                    avg_prices = df.groupby('_id')['averagePrice'].mean()
                    st.write("Prix moyen par RAM")
                    st.bar_chart(avg_prices)

                    # Weighted Average Prices
                    df['weightedAvgPrice'] = (df['averagePrice'] * df['numGames']) / df['numGames'].sum()
                    st.write("Prix moyen par RAM (pondéré par le nombre de jeux)")
                    st.bar_chart(df.set_index('_id')['weightedAvgPrice'])

                # Option to Run Query Without Indexes
                if st.button("Run query without existing indexes"):
                    # Dropping indexes
                    drop_indexes()
                    timequery, result = get_price_RAM()

                    # Display Execution Time for Query Without Indexes
                    df_execution_times = pd.DataFrame(timequery, columns=["Execution Time (s)"])
                    st.line_chart(df_execution_times)

                    # Recreate Indexes
                    create_indexes()
                    # Data Preprocessing
                    df = pd.DataFrame(result)
                    df['_id'] = df['_id'].apply(preprocess_ram)  # Convert RAM to GB
                    df['averagePrice'] = df['averagePrice'].round(2)  # Round the average price

                    # Display Average Prices
                    avg_prices = df.groupby('_id')['averagePrice'].mean()
                    st.write("Prix moyen par RAM")
                    st.bar_chart(avg_prices)

                    # Weighted Average Prices
                    df['weightedAvgPrice'] = (df['averagePrice'] * df['numGames']) / df['numGames'].sum()
                    st.write("Prix moyen par RAM (pondéré par le nombre de jeux)")
                    st.bar_chart(df.set_index('_id')['weightedAvgPrice'])

        elif selected_user == "admin":
            st.title("Admin Dashboard")
            selected_db_name = st.selectbox("Select Database", client.list_database_names())
            db = client[selected_db_name]
            selected_collection_name = st.selectbox("Select Collection", db.list_collection_names())

            if st.button("Monitor Cluster"):
                # Server Status
                server_status = get_server_status(client)
                st.subheader("Server Status")
                st.json(server_status)

                # Database Stats
                db_stats = get_db_stats(client, selected_db_name)
                st.subheader("Database Stats")
                st.json(db_stats)

                # Current Operations
                current_ops = get_current_op(client)
                st.subheader("Current Operations")
                st.json(current_ops)

                # Ping
                ping_time = ping_mongo(client)
                st.subheader("Ping")
                st.write(f"Ping time: {ping_time:.2f} seconds")

            if st.button("Show Collection Info"):
                # Collection Stats
                collection_stats = get_collection_stats(db, selected_collection_name)
                st.subheader(f"Collection '{selected_collection_name}' Stats")
                st.json(collection_stats)
            # Select View
            view_name = st.selectbox("Select View", ['critic_trend_view', 'engagement_rate_view', 'followers_ranking_view'])

            # Fetch and display data from the selected view
            if st.button("Fetch Data from View"):
                results = query_view(client, 'EpicGame', view_name)
                df = pd.DataFrame(results)
                st.dataframe(df)



        elif selected_user == "standard":
            user_choice = st.radio("Sélectionnez une requête :", ["Info du jeu 'Super Meat Boy'", "Jeux de genre ACTION", "Critiques de 'Shadow Complex Remastered'", "Jeux sortis en 2020"])

            if user_choice == "Info du jeu 'Super Meat Boy'":
                query = st.button("Search")
                if query:
                    
                    game_name = "Super Meat Boy"
                    timequery, game_info = get_game_info(game_name)
                    game_info = game_info or {}

                    st.line_chart(pd.DataFrame(timequery, columns=["Execution Time (s)"]))

                    st.subheader(f"Game Information for '{game_name}':")
                    
                    # Create a DataFrame with the game information
                    df_game_info = pd.DataFrame([game_info])

                    if "name" in game_info:
                        st.write(f"**Name:** {game_info['name']}")
                    if "platform" in game_info:
                        st.write(f"**Platform:** {game_info['platform']}")
                    if "genre" in game_info:
                        st.write(f"**Genre:** {game_info['genre']}")
                    if "release_date" in game_info:
                        release_date = game_info['release_date'].split('T')[0]
                        st.write(f"**Released in:** {release_date}")

                    st.write(f"**Additional Information (excluding critic ratings):**")
                    for key, value in game_info.items():
                        if key != "critic":
                            st.write(f"**{key.capitalize()}:** {value}")

                    # Display the unique game information
                    st.subheader("raw table : ")
                    st.dataframe(df_game_info)

            elif user_choice == "Jeux de genre ACTION":
                query = st.button("Search")
                if query:
                    timequery,result = get_genre_action_games()
                    df_execution_times = pd.DataFrame(timequery, columns=["Execution Time (s)"])
                    st.line_chart(df_execution_times)
                    st.dataframe(result)

            if user_choice == "Critiques de 'Shadow Complex Remastered'":
                query = st.button("Search")
                if query:
                    timequery, reviews = get_shadow_complex_reviews()
                    df_execution_times = pd.DataFrame(timequery, columns=["Execution Time (s)"])

                    # Create a DataFrame for the critic ratings
                    df_reviews = pd.DataFrame(reviews)

                    # Convert the "rating" column to numeric
                    df_reviews["rating"] = pd.to_numeric(df_reviews["rating"], errors='coerce')

                    # Calculate average rating for 'Shadow Complex Remastered'
                    average_rating_shadow_complex = df_reviews["rating"].mean()

                    lowest_rating_row = df_reviews[df_reviews["rating"] == df_reviews["rating"].min()]
                    highest_rating_row = df_reviews[df_reviews["rating"] == df_reviews["rating"].max()]

                    lowest_rating_comment = lowest_rating_row.iloc[0]["comment"]
                    lowest_rating = lowest_rating_row.iloc[0]["rating"]

                    highest_rating_comment = highest_rating_row.iloc[0]["comment"]
                    highest_rating = highest_rating_row.iloc[0]["rating"]

                    st.line_chart(df_execution_times)
                    st.subheader("Critic Reviews for 'Shadow Complex Remastered':")
                    st.dataframe(df_reviews)

                    st.subheader("Additional Information:")
                    st.write(f"**Average Rating for 'Shadow Complex Remastered':** {average_rating_shadow_complex:.2f}")
                    st.write(f"**Lowest Rating:** {lowest_rating:.2f} by '{lowest_rating_row.iloc[0]['author']}' of '{lowest_rating_row.iloc[0]['company']}'")
                    st.write(f"**Comment:** {lowest_rating_comment}")
                    st.write(f"**Highest Rating:** {highest_rating:.2f} by '{highest_rating_row.iloc[0]['author']}' of '{highest_rating_row.iloc[0]['company']}'")
                    st.write(f"**Comment:** {highest_rating_comment}")

            elif user_choice == "Jeux sortis en 2020":
                query = st.button("Search")
                if query:
                    timequery,result,game_counts_per_month = get_games_2020()   
                    df_execution_times = pd.DataFrame(timequery, columns=["Execution Time (s)"])
                    st.line_chart(df_execution_times)

                    # Create a list of sorted months for labeling
                    sorted_months = [f"2020-{str(month).zfill(2)}" for month in range(1, 13)]

                    # Create a DataFrame for the monthly game counts
                    df_game_counts = pd.DataFrame({
                        "Month": sorted_months,
                        "Number of Games Released": game_counts_per_month
                    })

                    # Create a line chart to visualize the number of games released each month
                    st.subheader("Number of Games Released Each Month in 2020:")
                    st.bar_chart(df_game_counts.set_index("Month"))
            