import streamlit as st
from pymongo import MongoClient
import pandas as pd
import time
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

    average_execution_time = sum(execution_times) / num_iterations
    min_execution_time = min(execution_times)
    max_execution_time = max(execution_times)
    st.write(f"Average Execution Time: {average_execution_time} seconds")
    st.write(f"Min Execution Time: {min_execution_time} seconds")
    st.write(f"Max Execution Time: {max_execution_time} seconds")
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

    return time_execution(query),query()

def get_games_2020():
    def query():
        db = client.EpicGame
        return list(db.GameCritic.find({"release_date": {"$regex": "2020"}}, {"_id": 0, "name": 1, "release_date": 1}))

    return time_execution(query),query()

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
            game_info = get_game_info("Super Meat Boy")
            st.write(game_info)
        
        if selected_user == "admin":
            game_info = get_game_info("Super Meat Boy")
            st.write(game_info)


        elif selected_user == "standard":
            user_choice = st.radio("Sélectionnez une requête :", ["Info du jeu 'Super Meat Boy'", "Jeux de genre ACTION", "Critiques de 'Shadow Complex Remastered'", "Jeux sortis en 2020"])

            if user_choice == "Info du jeu 'Super Meat Boy'":
                timequery,result = get_game_info("Super Meat Boy")
                df_execution_times = pd.DataFrame(timequery, columns=["Execution Time (s)"])
                st.line_chart(df_execution_times)
                st.dataframe(result)

            elif user_choice == "Jeux de genre ACTION":
                timequery,result = get_genre_action_games()
                df_execution_times = pd.DataFrame(timequery, columns=["Execution Time (s)"])
                st.line_chart(df_execution_times)
                st.dataframe(result)

            elif user_choice == "Critiques de 'Shadow Complex Remastered'":
                timequery,result = get_shadow_complex_reviews()
                df_execution_times = pd.DataFrame(timequery, columns=["Execution Time (s)"])
                st.line_chart(df_execution_times)
                st.dataframe(result)

            elif user_choice == "Jeux sortis en 2020":
                timequery,result = get_games_2020()
                df_execution_times = pd.DataFrame(timequery, columns=["Execution Time (s)"])
                st.line_chart(df_execution_times)
                st.dataframe(result)
            

