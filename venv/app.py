from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient
from flask import Flask, render_template, request
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pymongo import MongoClient
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split



app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb+srv://w1798587:Success%402024@cluster0.69rs1dl.mongodb.net/")
#client = MongoClient("mongodb://localhost:27017/")
db = client["IntellCollab"]
users_collection = db["User_Project"]
collection = db['User_Project']
# users_collection = db["User_Project"]
projects_collection = db["User_Project"]
# collection = db['User_Project']


# Retrieve data from MongoDB
cursor = collection.find()

# Convert data to DataFrame
data = list(cursor)
df = pd.DataFrame(data)

# Remove duplicates
df.drop_duplicates(subset=['Industry_Project_Name'], keep='first', inplace=True)

# Remove rows with missing values
df.dropna(subset=['Project_Description', 'Skills', 'Industry_Company_Name'], inplace=True)

# Standardize text data
#df['Project_Description'] = df['Project_Description'].str.lower()
df['Skills'] = df['Skills'].str.lower()
#df['Industry_Company_Name'] = df['Industry_Company_Name'].str.lower()



# Remove punctuation
import string
df['Project_Description'] = df['Project_Description'].apply(lambda x: x.translate(str.maketrans('', '', string.punctuation)))
df['Skills'] = df['Skills'].apply(lambda x: x.translate(str.maketrans('', '', string.punctuation)))
#df['Industry_Company_Name'] = df['Industry_Company_Name'].apply(lambda x: x.translate(str.maketrans('', '', string.punctuation)))

# Extract length of project descriptions as a feature
df['Description_Length'] = df['Project_Description'].apply(len)

# Split data into training and testing sets
train_data, test_data = train_test_split(df, test_size=0.2, random_state=42)


# Content-Based Filtering
tfidf_vectorizer = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf_vectorizer.fit_transform(df['Skills'])




@app.route('/recommend_projects', methods=['POST'])
def recommend_projects():
    skills = request.form.get('skills')
    if skills:
        project_skills = [skill.strip() for skill in skills.split(',')]
        skills_vector = tfidf_vectorizer.transform([', '.join(project_skills)])
        similarity_scores = cosine_similarity(skills_vector, tfidf_matrix)
        recommendations = [(project, company, score) for project, company, score in zip(df['Industry_Project_Name'], df['Industry_Company_Name'], similarity_scores[0])]
        recommendations.sort(key=lambda x: x[2], reverse=True)
        recommended_projects = recommendations[:5]  # Get top 5 recommended projects
    else:
        recommended_projects = []
    return render_template('dashboard.html', recommended_projects=recommended_projects)



# Recommendatiion

def recommend_projects(user_skills, user_interests):
    # Query collection based on user skills and interests
    recommended_projects = projects_collection.find({
        "$or": [
            {"skills": {"$in": user_skills}},
            {"interests": {"$in": user_interests}}
        ]
    }).limit(5)  # Limit the number of recommended projects to 5 for example
    return recommended_projects


    
    
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])  # Allow both GET and POST requests
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Query the user from the MongoDB collection
        user = users_collection.find_one({"username": username, "user_password": password})
        if user:
            # Successful login
            return redirect(url_for('dashboard', username=username))
        else:
            # Failed login
            return render_template('login.html', message="Invalid username or password")
    else:
        # If GET request, render the login page
        return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/dashboard/<username>')
def dashboard(username):
    # Retrieve user information
    user = users_collection.find_one({"username": username})
    if user:
        # Retrieve user skills and interests
        user_skills = [user.get("faculty_skill1", ""), user.get("faculty_skill2", "")]
        user_interests = [user.get("faculty_interest1", ""), user.get("faculty_interest2", "")]
        # Call the recommender system function
        recommended_projects = recommend_projects(user_skills, user_interests)
        return render_template('dashboard.html', username=username, projects=recommended_projects)
    else:
        return render_template('dashboard.html', username=username, projects=None)


#SignUp Main #####################



@app.route('/signup', methods=['GET', 'POST'])
def signup_handler():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        password2 = request.form['re-enter_password']
        user_type = request.form['user_type']  # Assuming the user type is selected from a dropdown
        
        # Check if passwords match
        if password != password2:
            return render_template('signup.html', message="Passwords do not match.")
        
        # Check user type and validate email accordingly
        if user_type == 'Academic':
            if not email.endswith('.ac.uk') or email.count('@') != 1 or sum(c.isdigit() for c in email) > 1:
                return render_template('signup.html', message="Invalid email for academic. It should end with ac.uk and contain no more than 1 number.")
        elif user_type == 'Student':
            if not email.endswith('.ac.uk') or email.count('@') != 1 or sum(c.isdigit() for c in email) < 2:
                return render_template('signup.html', message="Invalid email for student. It should end with ac.uk and contain two or more numbers.")
        elif user_type == 'Industry Expert':
            if not email.endswith('.com') or email.count('@') != 1:
                return render_template('signup.html', message="Invalid email for industry expert. It should end with .com.")
        else:
            return render_template('signup.html', message="Invalid user type.")
        
        # Check if the username already exists in the database
        existing_user = users_collection.find_one({"username": username})
        if existing_user:
            return render_template('signup.html', message="Username already exists. Please choose another username.")
        
        try:
            # Insert the new user into the database
            new_user = {
                "username": username,
                "user_email": email,
                "user_password": password,
                "user_type": user_type,
                "projects": []  # Initialize an empty list for projects
                # Add additional fields as needed
            }
            users_collection.insert_one(new_user)
        
            # Redirect the user to the dashboard with username as a parameter
            return redirect(url_for('dashboard', username=username))
        except Exception as e:
            return render_template('signup.html', message="An error occurred while creating the account. Please try again later.")

    else:
        return render_template('signup.html')





    


# Define the dashboard route to handle both GET and POST requests
@app.route('/dashboard', methods=['GET', 'POST'])
def new_dashboard():
    if request.method == 'POST':
        # Get user inputs from the form
        skill1 = request.form['skill1']
        skill2 = request.form['skill2']
        interest1 = request.form['interest1']
        interest2 = request.form['interest2']
        
        # Get recommendations based on user inputs
        recommended_projects = get_recommendations(skill1, skill2, interest1, interest2)
        
        return render_template('dashboard.html', username="User", projects=recommended_projects)
    else:
        # Render the dashboard template with no projects initially
        return render_template('dashboard.html', username="User", projects=None)




@app.route('/add_project', methods=['GET', 'POST'])
def add_project():
    if request.method == 'POST':
        # Retrieve data from the form
        project_name = request.form['project_name']
        project_description = request.form['project_description']
        skills = request.form['skills']
        industry_company_name = request.form['industry_company_name']

        # Insert the project into the database
        users_collection.insert_one({
            "project_name": project_name,
            "project_description": project_description,
            "skills": skills,
            "industry_company_name": industry_company_name
        })

        # Redirect to the dashboard page
        return redirect('/')
    else:
        # Render the HTML form for adding a project
        return render_template('add_project.html')




if __name__ == '__main__':
    app.run(debug=True)






























# from flask import Flask, render_template, request, redirect, url_for
# from pymongo import MongoClient
# from flask import Flask, render_template, request
# from flask import Flask, render_template, request, redirect, url_for
# import pandas as pd
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# from pymongo import MongoClient
# from sklearn.model_selection import train_test_split
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# from sklearn.model_selection import train_test_split



# app = Flask(__name__)

# # MongoDB connection
# client = MongoClient("mongodb+srv://w1798587:Success%402024@cluster0.69rs1dl.mongodb.net/")
# #client = MongoClient("mongodb://localhost:27017/")
# db = client["IntellCollab"]
# users_collection = db["User_Project"]
# projects_collection = db["User_Project"]
# collection = db['User_Project']


# # Retrieve data from MongoDB
# cursor = collection.find()

# # Convert data to DataFrame
# data = list(cursor)
# df = pd.DataFrame(data)

# # Remove duplicates
# df.drop_duplicates(subset=['Industry_Project_Name'], keep='first', inplace=True)

# # Remove rows with missing values
# df.dropna(subset=['Project_Description', 'Skills', 'Industry_Company_Name'], inplace=True)

# # Standardize text data
# #df['Project_Description'] = df['Project_Description'].str.lower()
# df['Skills'] = df['Skills'].str.lower()
# #df['Industry_Company_Name'] = df['Industry_Company_Name'].str.lower()



# # Remove punctuation
# import string
# df['Project_Description'] = df['Project_Description'].apply(lambda x: x.translate(str.maketrans('', '', string.punctuation)))
# df['Skills'] = df['Skills'].apply(lambda x: x.translate(str.maketrans('', '', string.punctuation)))
# #df['Industry_Company_Name'] = df['Industry_Company_Name'].apply(lambda x: x.translate(str.maketrans('', '', string.punctuation)))

# # Extract length of project descriptions as a feature
# df['Description_Length'] = df['Project_Description'].apply(len)

# # Split data into training and testing sets
# train_data, test_data = train_test_split(df, test_size=0.2, random_state=42)


# # Content-Based Filtering
# tfidf_vectorizer = TfidfVectorizer(stop_words='english')
# tfidf_matrix = tfidf_vectorizer.fit_transform(df['Skills'])


# ''' @app.route('/recommend_projects', methods=['POST'])
# def recommend_projects():
#     skills = request.form.get('skills')
#     if skills:
#         project_skills = [skill.strip() for skill in skills.split(',')]
#         skills_vector = tfidf_vectorizer.transform([', '.join(project_skills)])
#         similarity_scores = cosine_similarity(skills_vector, tfidf_matrix)
#         recommendations = [(project, company, score) for project, company, score in zip(df['Industry_Project_Name'], df['Industry_Company_Name'], similarity_scores[0])]
#         recommendations.sort(key=lambda x: x[2], reverse=True)
#         recommended_projects = recommendations[:5]  # Get top 5 recommended projects
#     else:
#         recommended_projects = []
#     return render_template('dashboard.html', recommended_projects=recommended_projects) '''


# @app.route('/recommend_projects', methods=['POST'])
# def recommend_projects():
#     skills = request.form.get('skills')
#     if skills:
#         project_skills = [skill.strip() for skill in skills.split(',')]
#         skills_vector = tfidf_vectorizer.transform([', '.join(project_skills)])
#         similarity_scores = cosine_similarity(skills_vector, tfidf_matrix)
#         recommendations = [(project, company, score) for project, company, score in zip(df['Industry_Project_Name'], df['Industry_Company_Name'], similarity_scores[0])]
#         recommendations.sort(key=lambda x: x[2], reverse=True)
#         recommended_projects = recommendations[:5]  # Get top 5 recommended projects
#     else:
#         recommended_projects = []
#     return render_template('dashboard.html', recommended_projects=recommended_projects)



# ''' @app.route('/recommend_projects', methods=['POST'])
# def recommend_projects():
#     skills = request.form.get('skills')
#     if skills:
#         project_skills = [skill.strip() for skill in skills.split(',')]
#         skills_vector = tfidf_vectorizer.transform([', '.join(project_skills)])
#         similarity_scores = cosine_similarity(skills_vector, tfidf_matrix)
#         #recommendations = [(project, company, score) for project, company, score in zip(df['Industry_Project_Name'], df['Industry_Company_Name'], similarity_scores[0])]
#         recommendations = [(project, company, score, Skills, description) for project, company, score, Skills, description in zip(df['Industry_Project_Name'], df['Industry_Company_Name'], similarity_scores[0], df['Skills'], df['Project_Description'])]
#         recommendations.sort(key=lambda x: x[2], reverse=True)
#         recommended_projects = recommendations[:5]  # Get top 5 recommended projects
#     else:
#         recommended_projects = []
#     return render_template('dashboard.html', recommended_projects=recommended_projects) '''





# # @app.route('/recommend_projects', methods=['POST'])
# # def recommend_projects():
# #     skills = request.form.get('skills')
# #     if skills:
# #         project_skills = [skill.strip() for skill in skills.split(',')]
# #         skills_vector = tfidf_vectorizer.transform([', '.join(project_skills)])
# #         similarity_scores = cosine_similarity(skills_vector, tfidf_matrix)
# #         recommendations = [(project, company, similarity, description, skills) for project, company, similarity, description, skills in zip(df['Industry_Project_Name'], df['Industry_Company_Name'], similarity_scores[0], df['Project_Description'], df['Skills'])]
# #         recommendations.sort(key=lambda x: x[2], reverse=True)
# #         recommended_projects = recommendations[:5]  # Get top 5 recommended projects
# #     else:
# #         recommended_projects = []
# #     return render_template('dashboard.html', recommended_projects=recommended_projects)




# # Dummy skills and interests data
# skills = ["Machine Learning", "Python", "Data Analysis"]
# interests = ["Artificial Intelligence", "Web Development", "Data Science"]

# def recommend_projects(user_skills, user_interests):
#     # Query projects collection based on user skills and interests
#     recommended_projects = projects_collection.find({
#         "$or": [
#             {"skills": {"$in": user_skills}},
#             {"interests": {"$in": user_interests}}
#         ]
#     }).limit(5)  # Limit the number of recommended projects to 5 for example
#     return recommended_projects

# @app.route('/profile', methods=['GET', 'POST'])
# def profile():
#     if request.method == 'POST':
#         username = request.form['username']
#         name = request.form['name']
#         skill1 = request.form['skill1']
#         skill2 = request.form['skill2']
#         interest1 = request.form['interest1']
#         interest2 = request.form['interest2']
#         role = request.form['role']
#         # Update user profile information in the database
#         users_collection.update_one(
#             {"faculty_username": username},
#             {"$set": {
#                 "faculty_name": name,
#                 "faculty_skill1": skill1,
#                 "faculty_skill2": skill2,
#                 "faculty_interest1": interest1,
#                 "faculty_interest2": interest2,
#                 "faculty_role": role
#             }},
#             upsert=True  # Insert the document if it doesn't exist
#         )
#         # Redirect the user to the dashboard with username as a parameter
#         return redirect(url_for('dashboard', username=username))
#     else:
#         return render_template('profile.html')
    
    
# @app.route('/')
# def index():
#     return render_template('home.html')

# @app.route('/login', methods=['GET', 'POST'])  # Allow both GET and POST requests
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         # Query the user from the MongoDB collection
#         user = users_collection.find_one({"username": username, "user_password": password})
#         if user:
#             # Successful login
#             return redirect(url_for('dashboard', username=username))
#         else:
#             # Failed login
#             return render_template('login.html', message="Invalid username or password")
#     else:
#         # If GET request, render the login page
#         return render_template('login.html')

# @app.route('/signup')
# def signup():
#     return render_template('signup.html')

# @app.route('/dashboard/<username>')
# def dashboard(username):
#     # Retrieve user information
#     user = users_collection.find_one({"username": username})
#     if user:
#         # Retrieve user skills and interests
#         user_skills = [user.get("faculty_skill1", ""), user.get("faculty_skill2", "")]
#         user_interests = [user.get("faculty_interest1", ""), user.get("faculty_interest2", "")]
#         # Call the recommender system function
#         recommended_projects = recommend_projects(user_skills, user_interests)
#         return render_template('dashboard.html', username=username, projects=recommended_projects)
#     else:
#         return render_template('dashboard.html', username=username, projects=None)


# #SignUp Main #####################

# ''' @app.route('/signup', methods=['GET', 'POST'])
# def signup_handler():
#     if request.method == 'POST':
#         username = request.form['username']
#         email = request.form['email']
#         password = request.form['password']
        
#         password2 = request.form['re-enter_password']
        
#         # Check if the username already exists in the database
#         existing_user = users_collection.find_one({"username": username})
#         if existing_user:
#             return render_template('signup.html', message="Username already exists. Please choose another username.")
        
#         try:
#             # Insert the new user into the database
#             new_user = {
#                 "username": username,
#                 "user_email": email,
#                 "user_password": password,
#                 # Add additional fields as needed
#             }
#             users_collection.insert_one(new_user)
        
#             # Redirect the user to the dashboard with username as a parameter
#             return redirect(url_for('dashboard.html', username=username))
#         except Exception as e:
#             return render_template('signup.html', message="An error occurred while creating the account. Please try again later.")

#     else:
#         return render_template('signup.html')
    
#      '''
     
# @app.route('/signup', methods=['GET', 'POST'])
# def signup_handler():
#     if request.method == 'POST':
#         username = request.form['username']
#         email = request.form['email']
#         password = request.form['password']
#         password2 = request.form['re-enter_password']
#         user_type = request.form['user_type']  # Assuming the user type is selected from a dropdown
        
#         # Check if passwords match
#         if password != password2:
#             return render_template('signup.html', message="Passwords do not match.")
        
#         # Check user type and validate email accordingly
#         if user_type == 'Academic':
#             if not email.endswith('.ac.uk') or email.count('@') != 1 or sum(c.isdigit() for c in email) > 1:
#                 return render_template('signup.html', message="Invalid email for academic. It should end with ac.uk and contain no more than 1 number.")
#         elif user_type == 'Student':
#             if not email.endswith('.ac.uk') or email.count('@') != 1 or sum(c.isdigit() for c in email) < 2:
#                 return render_template('signup.html', message="Invalid email for student. It should end with ac.uk and contain two or more numbers.")
#         elif user_type == 'Industry Expert':
#             if not email.endswith('.com') or email.count('@') != 1:
#                 return render_template('signup.html', message="Invalid email for industry expert. It should end with .com.")
#         else:
#             return render_template('signup.html', message="Invalid user type.")
        
#         # Check if the username already exists in the database
#         existing_user = users_collection.find_one({"username": username})
#         if existing_user:
#             return render_template('signup.html', message="Username already exists. Please choose another username.")
        
#         try:
#             # Insert the new user into the database
#             new_user = {
#                 "username": username,
#                 "user_email": email,
#                 "user_password": password,
#                 "user_type": user_type,
#                 # Add additional fields as needed
#             }
#             users_collection.insert_one(new_user)
        
#             # Redirect the user to the dashboard with username as a parameter
#             return redirect(url_for('dashboard.html', username=username))
#         except Exception as e:
#             return render_template('signup.html', message="An error occurred while creating the account. Please try again later.")

#     else:
#         return render_template('login.html')
    
# # def is_valid_email(email, role):
# #     if role == 'student':
# #         return len(email) > 2 and email.endswith('ac.uk')
# #     elif role == 'faculty':
# #         # Email should contain letters and maximum one number, and end with .ac.uk
# #         return re.match(r'^[a-zA-Z]+[0-9]{0,1}@.*\.ac\.uk$', email)
# #     elif role == 'industry':
# #         return email.endswith('.com')
# #     else:
# #         return False

# # @app.route('/signup', methods=['GET', 'POST'])
# # def new_signup():
# #     if request.method == 'POST':
# #         username = request.form['username']
# #         email = request.form['email']
# #         password = request.form['password']
# #         confirm_password = request.form['confirm_password']
# #         role = request.form['role']

# #         if password != confirm_password:
# #             return render_template('signup.html', message="Passwords do not match.")

# #         if not is_valid_email(email, role):
# #             return render_template('signup.html', message="Invalid email format for the selected role.")

# #         # Check if the username already exists in the database
# #         existing_user = users_collection.find_one({"faculty_username": username})
# #         if existing_user:
# #             return render_template('signup.html', message="Username already exists. Please choose another username.")

# #         try:
# #             # Insert the new user into the database
# #             new_user = {
# #                 "faculty_username": username,
# #                 "faculty_email": email,
# #                 "faculty_password": password,
# #                 "faculty_role": role,
# #                 # Add additional fields as needed
# #             }
# #             users_collection.insert_one(new_user)

# #             # Redirect the user to the dashboard with username as a parameter
# #             return redirect(url_for('dashboard', username=username))
# #         except Exception as e:
# #             return render_template('signup.html', message="An error occurred while creating the account. Please try again later.")

# #     else:
# #         return render_template('signup.html', skills=skills, interests=interests) 
 
 
 
 
 
    
# ######################### Search Proects Search Bar ##########
# # Define a function to search projects based on the search query


# # Other routes and functions...
# ###########################


# # Define your collaborative filtering recommendation function
# def get_collaborative_recommendations(skill1, skill2):
#     # Query projects collection based on user skills
#     collaborative_recommendations = projects_collection.find({
#         "$or": [
#             {"Skills": {"$in": [skill1]}},
#             {"Skills": {"$in": [skill2]}}
#         ]
#     })
#     return list(collaborative_recommendations)

# # Define your content-based filtering recommendation function
# def get_content_based_recommendations(interest1, interest2):
#     # Query projects collection based on user interests
#     content_based_recommendations = projects_collection.find({
#         "$or": [
#             {"faculty_interests": {"$in": [interest1]}},
#             {"faculty_interests": {"$in": [interest2]}}
#         ]
#     })
#     return list(content_based_recommendations)


# # Define your recommendation merging function
# def merge_recommendations(collaborative_recommendations, content_based_recommendations):
#     # Placeholder for merging recommendations
#     # For simplicity, let's just concatenate the lists
#     merged_recommendations = collaborative_recommendations + content_based_recommendations
#     return merged_recommendations

# # Define your recommendation generation function
# def get_recommendations(skill1, skill2, interest1, interest2):
#     # Get recommendations from collaborative filtering
#     collaborative_recommendations = get_collaborative_recommendations(skill1, skill2)
    
#     # Get recommendations from content-based filtering
#     content_based_recommendations = get_content_based_recommendations(interest1, interest2)
    
#     # Merge recommendations from both approaches
#     recommendations = merge_recommendations(collaborative_recommendations, content_based_recommendations)
    
#     return recommendations

# # Define the dashboard route to handle both GET and POST requests
# @app.route('/dashboard', methods=['GET', 'POST'])
# def new_dashboard():
#     if request.method == 'POST':
#         # Get user inputs from the form
#         skill1 = request.form['skill1']
#         skill2 = request.form['skill2']
#         interest1 = request.form['interest1']
#         interest2 = request.form['interest2']
        
#         # Get recommendations based on user inputs
#         recommended_projects = get_recommendations(skill1, skill2, interest1, interest2)
        
#         return render_template('dashboard.html', username="User", projects=recommended_projects)
#     else:
#         # Render the dashboard template with no projects initially
#         return render_template('dashboard.html', username="User", projects=None)


# ''' @app.route('/dashboard_page', methods=['GET', 'POST'])  # Rename the route
# def dashboard_page():
#     if request.method == 'POST':
#         skill1 = request.form['skill1']
#         skill2 = request.form['skill2']
#         interest1 = request.form['interest1']
#         interest2 = request.form['interest2']
        
#         # Query projects collection based on user skills and interests
#         projects = projects_collection.find({
#             "$or": [
#                 {"skills": {"$in": [skill1, skill2]}},
#                 {"interests": {"$in": [interest1, interest2]}}
#             ]
#         })
        
#         return render_template('dashboard.html', username="User", projects=projects)
#     else:
#         return render_template('dashboard.html', username="User", projects=None) '''

# @app.route('/add_project', methods=['GET', 'POST'])
# def add_project():
#     if request.method == 'POST':
#         # Retrieve data from the form
#         project_name = request.form['project_name']
#         project_description = request.form['project_description']
#         skills = request.form['skills']
#         industry_company_name = request.form['industry_company_name']

#         # Insert the project into the database
#         projects_collection.insert_one({
#             "project_name": project_name,
#             "project_description": project_description,
#             "skills": skills,
#             "industry_company_name": industry_company_name
#         })

#         # Redirect to the dashboard page
#         return redirect('/')
#     else:
#         # Render the HTML form for adding a project
#         return render_template('add_project.html')


# if __name__ == '__main__':
#     app.run(debug=True)






















# from flask import Flask, render_template, request, redirect, url_for
# from pymongo import MongoClient
# from flask import Flask, render_template, request
# from flask import Flask, render_template, request, redirect, url_for
# import pandas as pd
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# from pymongo import MongoClient
# from sklearn.model_selection import train_test_split
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# from sklearn.model_selection import train_test_split



# app = Flask(__name__)

# # MongoDB connection
# client = MongoClient("mongodb+srv://w1798587:Success%402024@cluster0.69rs1dl.mongodb.net/")
# db = client["MyDatabase"]
# users_collection = db["Faculty"]
# projects_collection = db["Project"]
# collection = db['Faculty_Project']


# # Retrieve data from MongoDB
# cursor = collection.find()

# # Convert data to DataFrame
# data = list(cursor)
# df = pd.DataFrame(data)

# # Remove duplicates
# df.drop_duplicates(subset=['Industry_Project_Name'], keep='first', inplace=True)

# # Remove rows with missing values
# df.dropna(subset=['Project_Description', 'Skills', 'Industry_Company_Name'], inplace=True)

# # Standardize text data
# df['Project_Description'] = df['Project_Description'].str.lower()
# df['Skills'] = df['Skills'].str.lower()
# df['Industry_Company_Name'] = df['Industry_Company_Name'].str.lower()

# # Remove punctuation
# import string
# df['Project_Description'] = df['Project_Description'].apply(lambda x: x.translate(str.maketrans('', '', string.punctuation)))
# df['Skills'] = df['Skills'].apply(lambda x: x.translate(str.maketrans('', '', string.punctuation)))
# df['Industry_Company_Name'] = df['Industry_Company_Name'].apply(lambda x: x.translate(str.maketrans('', '', string.punctuation)))

# # Extract length of project descriptions as a feature
# df['Description_Length'] = df['Project_Description'].apply(len)

# # Split data into training and testing sets
# train_data, test_data = train_test_split(df, test_size=0.2, random_state=42)


# # Content-Based Filtering
# tfidf_vectorizer = TfidfVectorizer(stop_words='english')
# tfidf_matrix = tfidf_vectorizer.fit_transform(df['Project_Description'])


# @app.route('/recommend_projects', methods=['POST'])
# def recommend_projects():
#     skills = request.form.get('skills')
#     if skills:
#         project_skills = [skill.strip() for skill in skills.split(',')]
#         skills_vector = tfidf_vectorizer.transform([', '.join(project_skills)])
#         similarity_scores = cosine_similarity(skills_vector, tfidf_matrix)
#         recommendations = [(project, company, score) for project, company, score in zip(df['Industry_Project_Name'], df['Industry_Company_Name'], similarity_scores[0])]
#         recommendations.sort(key=lambda x: x[2], reverse=True)
#         recommended_projects = recommendations[:5]  # Get top 3 recommended projects
#     else:
#         recommended_projects = []
#     return render_template('dashboard.html', recommended_projects=recommended_projects)



# # @app.route('/recommend_projects', methods=['POST'])
# # def recommend_projects():
# #     skills = request.form.get('skills')
# #     if skills:
# #         project_skills = [skill.strip() for skill in skills.split(',')]
# #         skills_vector = tfidf_vectorizer.transform([', '.join(project_skills)])
# #         similarity_scores = cosine_similarity(skills_vector, tfidf_matrix)
# #         recommendations = [(project, company, similarity, description, skills) for project, company, similarity, description, skills in zip(df['Industry_Project_Name'], df['Industry_Company_Name'], similarity_scores[0], df['Project_Description'], df['Skills'])]
# #         recommendations.sort(key=lambda x: x[2], reverse=True)
# #         recommended_projects = recommendations[:5]  # Get top 5 recommended projects
# #     else:
# #         recommended_projects = []
# #     return render_template('dashboard.html', recommended_projects=recommended_projects)




# # Dummy skills and interests data
# skills = ["Machine Learning", "Python", "Data Analysis"]
# interests = ["Artificial Intelligence", "Web Development", "Data Science"]

# def recommend_projects(user_skills, user_interests):
#     # Query projects collection based on user skills and interests
#     recommended_projects = projects_collection.find({
#         "$or": [
#             {"skills": {"$in": user_skills}},
#             {"interests": {"$in": user_interests}}
#         ]
#     }).limit(5)  # Limit the number of recommended projects to 5 for example
#     return recommended_projects

# @app.route('/profile', methods=['GET', 'POST'])
# def profile():
#     if request.method == 'POST':
#         username = request.form['username']
#         name = request.form['name']
#         skill1 = request.form['skill1']
#         skill2 = request.form['skill2']
#         interest1 = request.form['interest1']
#         interest2 = request.form['interest2']
#         role = request.form['role']
#         # Update user profile information in the database
#         users_collection.update_one(
#             {"faculty_username": username},
#             {"$set": {
#                 "faculty_name": name,
#                 "faculty_skill1": skill1,
#                 "faculty_skill2": skill2,
#                 "faculty_interest1": interest1,
#                 "faculty_interest2": interest2,
#                 "faculty_role": role
#             }},
#             upsert=True  # Insert the document if it doesn't exist
#         )
#         # Redirect the user to the dashboard with username as a parameter
#         return redirect(url_for('dashboard', username=username))
#     else:
#         return render_template('profile.html', skills=skills, interests=interests)
    
    
# @app.route('/')
# def index():
#     return render_template('home.html')

# @app.route('/login', methods=['GET', 'POST'])  # Allow both GET and POST requests
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         # Query the user from the MongoDB collection
#         user = users_collection.find_one({"faculty_username": username, "faculty_password": password})
#         if user:
#             # Successful login
#             return redirect(url_for('dashboard', username=username))
#         else:
#             # Failed login
#             return render_template('login.html', message="Invalid username or password")
#     else:
#         # If GET request, render the login page
#         return render_template('login.html')

# @app.route('/signup')
# def signup():
#     return render_template('signup.html')

# @app.route('/dashboard/<username>')
# def dashboard(username):
#     # Retrieve user information
#     user = users_collection.find_one({"faculty_username": username})
#     if user:
#         # Retrieve user skills and interests
#         user_skills = [user.get("faculty_skill1", ""), user.get("faculty_skill2", "")]
#         user_interests = [user.get("faculty_interest1", ""), user.get("faculty_interest2", "")]
#         # Call the recommender system function
#         recommended_projects = recommend_projects(user_skills, user_interests)
#         return render_template('dashboard.html', username=username, projects=recommended_projects)
#     else:
#         return render_template('dashboard.html', username=username, projects=None)



# @app.route('/signup', methods=['GET', 'POST'])
# def signup_handler():
#     if request.method == 'POST':
#         username = request.form['username']
#         email = request.form['email']
#         password = request.form['password']
        
#         # Check if the username already exists in the database
#         existing_user = users_collection.find_one({"faculty_username": username})
#         if existing_user:
#             return render_template('signup.html', message="Username already exists. Please choose another username.")
        
#         try:
#             # Insert the new user into the database
#             new_user = {
#                 "faculty_username": username,
#                 "faculty_email": email,
#                 "faculty_password": password,
#                 # Add additional fields as needed
#             }
#             users_collection.insert_one(new_user)
        
#             # Redirect the user to the dashboard with username as a parameter
#             return redirect(url_for('dashboard', username=username))
#         except Exception as e:
#             return render_template('signup.html', message="An error occurred while creating the account. Please try again later.")

#     else:
#         return render_template('signup.html', skills=skills, interests=interests)
    
    
# ######################### Search Proects Search Bar ##########
# # Define a function to search projects based on the search query


# # Other routes and functions...
# ###########################


# # Define your collaborative filtering recommendation function
# def get_collaborative_recommendations(skill1, skill2):
#     # Query projects collection based on user skills
#     collaborative_recommendations = projects_collection.find({
#         "$or": [
#             {"Skills": {"$in": [skill1]}},
#             {"Skills": {"$in": [skill2]}}
#         ]
#     })
#     return list(collaborative_recommendations)

# # Define your content-based filtering recommendation function
# def get_content_based_recommendations(interest1, interest2):
#     # Query projects collection based on user interests
#     content_based_recommendations = projects_collection.find({
#         "$or": [
#             {"faculty_interests": {"$in": [interest1]}},
#             {"faculty_interests": {"$in": [interest2]}}
#         ]
#     })
#     return list(content_based_recommendations)


# # Define your recommendation merging function
# def merge_recommendations(collaborative_recommendations, content_based_recommendations):
#     # Placeholder for merging recommendations
#     # For simplicity, let's just concatenate the lists
#     merged_recommendations = collaborative_recommendations + content_based_recommendations
#     return merged_recommendations

# # Define your recommendation generation function
# def get_recommendations(skill1, skill2, interest1, interest2):
#     # Get recommendations from collaborative filtering
#     collaborative_recommendations = get_collaborative_recommendations(skill1, skill2)
    
#     # Get recommendations from content-based filtering
#     content_based_recommendations = get_content_based_recommendations(interest1, interest2)
    
#     # Merge recommendations from both approaches
#     recommendations = merge_recommendations(collaborative_recommendations, content_based_recommendations)
    
#     return recommendations

# # Define the dashboard route to handle both GET and POST requests
# @app.route('/dashboard', methods=['GET', 'POST'])
# def new_dashboard():
#     if request.method == 'POST':
#         # Get user inputs from the form
#         skill1 = request.form['skill1']
#         skill2 = request.form['skill2']
#         interest1 = request.form['interest1']
#         interest2 = request.form['interest2']
        
#         # Get recommendations based on user inputs
#         recommended_projects = get_recommendations(skill1, skill2, interest1, interest2)
        
#         return render_template('dashboard.html', username="User", projects=recommended_projects)
#     else:
#         # Render the dashboard template with no projects initially
#         return render_template('dashboard.html', username="User", projects=None)


# ''' @app.route('/dashboard_page', methods=['GET', 'POST'])  # Rename the route
# def dashboard_page():
#     if request.method == 'POST':
#         skill1 = request.form['skill1']
#         skill2 = request.form['skill2']
#         interest1 = request.form['interest1']
#         interest2 = request.form['interest2']
        
#         # Query projects collection based on user skills and interests
#         projects = projects_collection.find({
#             "$or": [
#                 {"skills": {"$in": [skill1, skill2]}},
#                 {"interests": {"$in": [interest1, interest2]}}
#             ]
#         })
        
#         return render_template('dashboard.html', username="User", projects=projects)
#     else:
#         return render_template('dashboard.html', username="User", projects=None) '''

# @app.route('/add_project', methods=['GET', 'POST'])
# def add_project():
#     if request.method == 'POST':
#         # Retrieve data from the form
#         project_name = request.form['project_name']
#         project_description = request.form['project_description']
#         skills = request.form['skills']
#         industry_company_name = request.form['industry_company_name']

#         # Insert the project into the database
#         projects_collection.insert_one({
#             "project_name": project_name,
#             "project_description": project_description,
#             "skills": skills,
#             "industry_company_name": industry_company_name
#         })

#         # Redirect to the dashboard page
#         return redirect('/')
#     else:
#         # Render the HTML form for adding a project
#         return render_template('add_project.html')


# if __name__ == '__main__':
#     app.run(debug=True)














# from flask import Flask, render_template, request, redirect, url_for
# from pymongo import MongoClient
# from flask import Flask, render_template, request
# from flask import Flask, render_template, request, redirect, url_for
# import pandas as pd
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# from pymongo import MongoClient

# app = Flask(__name__)

# # MongoDB connection
# client = MongoClient("mongodb+srv://w1798587:Success%402024@cluster0.69rs1dl.mongodb.net/")
# db = client["MyDatabase"]
# users_collection = db["Faculty"]
# projects_collection = db["Project"]
# collection = db['Faculty_Project']


# # Retrieve data from MongoDB
# cursor = collection.find()

# # Convert data to DataFrame
# data = list(cursor)
# df = pd.DataFrame(data)



# # Content-Based Filtering
# tfidf_vectorizer = TfidfVectorizer(stop_words='english')
# tfidf_matrix = tfidf_vectorizer.fit_transform(df['Project_Description'])


# @app.route('/recommend_projects', methods=['POST'])
# def recommend_projects():
#     skills = request.form.get('skills')
#     if skills:
#         project_skills = [skill.strip() for skill in skills.split(',')]
#         skills_vector = tfidf_vectorizer.transform([', '.join(project_skills)])
#         similarity_scores = cosine_similarity(skills_vector, tfidf_matrix)
#         recommendations = [(project, company, score) for project, company, score in zip(df['Industry_Project_Name'], df['Industry_Company_Name'], similarity_scores[0])]
#         recommendations.sort(key=lambda x: x[2], reverse=True)
#         recommended_projects = recommendations[:5]  # Get top 3 recommended projects
#     else:
#         recommended_projects = []
#     return render_template('dashboard.html', recommended_projects=recommended_projects)



# # Dummy skills and interests data
# skills = ["Machine Learning", "Python", "Data Analysis"]
# interests = ["Artificial Intelligence", "Web Development", "Data Science"]

# def recommend_projects(user_skills, user_interests):
#     # Query projects collection based on user skills and interests
#     recommended_projects = projects_collection.find({
#         "$or": [
#             {"skills": {"$in": user_skills}},
#             {"interests": {"$in": user_interests}}
#         ]
#     }).limit(5)  # Limit the number of recommended projects to 5 for example
#     return recommended_projects

# @app.route('/profile', methods=['GET', 'POST'])
# def profile():
#     if request.method == 'POST':
#         username = request.form['username']
#         name = request.form['name']
#         skill1 = request.form['skill1']
#         skill2 = request.form['skill2']
#         interest1 = request.form['interest1']
#         interest2 = request.form['interest2']
#         role = request.form['role']
#         # Update user profile information in the database
#         users_collection.update_one(
#             {"faculty_username": username},
#             {"$set": {
#                 "faculty_name": name,
#                 "faculty_skill1": skill1,
#                 "faculty_skill2": skill2,
#                 "faculty_interest1": interest1,
#                 "faculty_interest2": interest2,
#                 "faculty_role": role
#             }},
#             upsert=True  # Insert the document if it doesn't exist
#         )
#         # Redirect the user to the dashboard with username as a parameter
#         return redirect(url_for('dashboard', username=username))
#     else:
#         return render_template('profile.html', skills=skills, interests=interests)
    
    
# @app.route('/')
# def index():
#     return render_template('home.html')

# @app.route('/login', methods=['GET', 'POST'])  # Allow both GET and POST requests
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         # Query the user from the MongoDB collection
#         user = users_collection.find_one({"faculty_username": username, "faculty_password": password})
#         if user:
#             # Successful login
#             return redirect(url_for('dashboard', username=username))
#         else:
#             # Failed login
#             return render_template('login.html', message="Invalid username or password")
#     else:
#         # If GET request, render the login page
#         return render_template('login.html')

# @app.route('/signup')
# def signup():
#     return render_template('signup.html')

# @app.route('/dashboard/<username>')
# def dashboard(username):
#     # Retrieve user information
#     user = users_collection.find_one({"faculty_username": username})
#     if user:
#         # Retrieve user skills and interests
#         user_skills = [user.get("faculty_skill1", ""), user.get("faculty_skill2", "")]
#         user_interests = [user.get("faculty_interest1", ""), user.get("faculty_interest2", "")]
#         # Call the recommender system function
#         recommended_projects = recommend_projects(user_skills, user_interests)
#         return render_template('dashboard.html', username=username, projects=recommended_projects)
#     else:
#         return render_template('dashboard.html', username=username, projects=None)



# @app.route('/signup', methods=['GET', 'POST'])
# def signup_handler():
#     if request.method == 'POST':
#         username = request.form['username']
#         email = request.form['email']
#         password = request.form['password']
        
#         # Check if the username already exists in the database
#         existing_user = users_collection.find_one({"faculty_username": username})
#         if existing_user:
#             return render_template('signup.html', message="Username already exists. Please choose another username.")
        
#         try:
#             # Insert the new user into the database
#             new_user = {
#                 "faculty_username": username,
#                 "faculty_email": email,
#                 "faculty_password": password,
#                 # Add additional fields as needed
#             }
#             users_collection.insert_one(new_user)
        
#             # Redirect the user to the dashboard with username as a parameter
#             return redirect(url_for('dashboard', username=username))
#         except Exception as e:
#             return render_template('signup.html', message="An error occurred while creating the account. Please try again later.")

#     else:
#         return render_template('signup.html', skills=skills, interests=interests)
    
    
# ######################### Search Proects Search Bar ##########
# # Define a function to search projects based on the search query


# # Other routes and functions...
# ###########################


# # Define your collaborative filtering recommendation function
# def get_collaborative_recommendations(skill1, skill2):
#     # Query projects collection based on user skills
#     collaborative_recommendations = projects_collection.find({
#         "$or": [
#             {"Skills": {"$in": [skill1]}},
#             {"Skills": {"$in": [skill2]}}
#         ]
#     })
#     return list(collaborative_recommendations)

# # Define your content-based filtering recommendation function
# def get_content_based_recommendations(interest1, interest2):
#     # Query projects collection based on user interests
#     content_based_recommendations = projects_collection.find({
#         "$or": [
#             {"faculty_interests": {"$in": [interest1]}},
#             {"faculty_interests": {"$in": [interest2]}}
#         ]
#     })
#     return list(content_based_recommendations)


# # Define your recommendation merging function
# def merge_recommendations(collaborative_recommendations, content_based_recommendations):
#     # Placeholder for merging recommendations
#     # For simplicity, let's just concatenate the lists
#     merged_recommendations = collaborative_recommendations + content_based_recommendations
#     return merged_recommendations

# # Define your recommendation generation function
# def get_recommendations(skill1, skill2, interest1, interest2):
#     # Get recommendations from collaborative filtering
#     collaborative_recommendations = get_collaborative_recommendations(skill1, skill2)
    
#     # Get recommendations from content-based filtering
#     content_based_recommendations = get_content_based_recommendations(interest1, interest2)
    
#     # Merge recommendations from both approaches
#     recommendations = merge_recommendations(collaborative_recommendations, content_based_recommendations)
    
#     return recommendations

# # Define the dashboard route to handle both GET and POST requests
# @app.route('/dashboard', methods=['GET', 'POST'])
# def new_dashboard():
#     if request.method == 'POST':
#         # Get user inputs from the form
#         skill1 = request.form['skill1']
#         skill2 = request.form['skill2']
#         interest1 = request.form['interest1']
#         interest2 = request.form['interest2']
        
#         # Get recommendations based on user inputs
#         recommended_projects = get_recommendations(skill1, skill2, interest1, interest2)
        
#         return render_template('dashboard.html', username="User", projects=recommended_projects)
#     else:
#         # Render the dashboard template with no projects initially
#         return render_template('dashboard.html', username="User", projects=None)


# ''' @app.route('/dashboard_page', methods=['GET', 'POST'])  # Rename the route
# def dashboard_page():
#     if request.method == 'POST':
#         skill1 = request.form['skill1']
#         skill2 = request.form['skill2']
#         interest1 = request.form['interest1']
#         interest2 = request.form['interest2']
        
#         # Query projects collection based on user skills and interests
#         projects = projects_collection.find({
#             "$or": [
#                 {"skills": {"$in": [skill1, skill2]}},
#                 {"interests": {"$in": [interest1, interest2]}}
#             ]
#         })
        
#         return render_template('dashboard.html', username="User", projects=projects)
#     else:
#         return render_template('dashboard.html', username="User", projects=None) '''

# @app.route('/add_project', methods=['GET', 'POST'])
# def add_project():
#     if request.method == 'POST':
#         # Retrieve data from the form
#         project_name = request.form['project_name']
#         project_description = request.form['project_description']
#         skills = request.form['skills']
#         industry_company_name = request.form['industry_company_name']

#         # Insert the project into the database
#         projects_collection.insert_one({
#             "project_name": project_name,
#             "project_description": project_description,
#             "skills": skills,
#             "industry_company_name": industry_company_name
#         })

#         # Redirect to the dashboard page
#         return redirect('/')
#     else:
#         # Render the HTML form for adding a project
#         return render_template('add_project.html')


# if __name__ == '__main__':
#     app.run(debug=True)













# from flask import Flask, render_template, request, redirect, url_for
# from pymongo import MongoClient
# from flask import Flask, render_template, request
# from flask import Flask, render_template, request, redirect, url_for
# import pandas as pd
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# from pymongo import MongoClient

# app = Flask(__name__)

# # MongoDB connection
# client = MongoClient("mongodb+srv://w1798587:Success%402024@cluster0.69rs1dl.mongodb.net/")
# db = client["MyDatabase"]
# users_collection = db["Faculty"]
# projects_collection = db["Project"]
# collection = db['Faculty_Project']


# # Retrieve data from MongoDB
# cursor = collection.find()

# # Convert data to DataFrame
# data = list(cursor)
# df = pd.DataFrame(data)

# # Content-Based Filtering
# tfidf_vectorizer = TfidfVectorizer(stop_words='english')
# tfidf_matrix = tfidf_vectorizer.fit_transform(df['Project_Description'])




# # @app.route('/recommend_projects', methods=['POST'])
# # def recommend_projects():
# #     skills = request.form.get('skills')
# #     if skills:
# #         project_skills = [skill.strip() for skill in skills.split(',')]
# #         skills_vector = tfidf_vectorizer.transform([', '.join(project_skills)])
# #         similarity_scores = cosine_similarity(skills_vector, tfidf_matrix)
# #         recommendations = [(project, company, score) for project, company, score in zip(df['Industry_Project_Name'], df['Industry_Company_Name'], similarity_scores[0])]
# #         recommendations.sort(key=lambda x: x[2], reverse=True)
# #         recommended_projects = recommendations[:5]  # Get top 5 recommended projects
# #     else:
# #         recommended_projects = []
# #     return render_template('dashboard.html', recommended_projects=recommended_projects)



# # Dummy skills and interests data
# skills = ["Machine Learning", "Python", "Data Analysis"]
# interests = ["Artificial Intelligence", "Web Development", "Data Science"]

# def recommend_projects(user_skills, user_interests):
#     # Query projects collection based on user skills and interests
#     recommended_projects = projects_collection.find({
#         "$or": [
#             {"skills": {"$in": user_skills}},
#             {"interests": {"$in": user_interests}}
#         ]
#     }).limit(5)  # Limit the number of recommended projects to 5 for example
#     return recommended_projects

# @app.route('/profile', methods=['GET', 'POST'])
# def profile():
#     if request.method == 'POST':
#         username = request.form['username']
#         name = request.form['name']
#         skill1 = request.form['skill1']
#         skill2 = request.form['skill2']
#         interest1 = request.form['interest1']
#         interest2 = request.form['interest2']
#         role = request.form['role']
#         # Update user profile information in the database
#         users_collection.update_one(
#             {"faculty_username": username},
#             {"$set": {
#                 "faculty_name": name,
#                 "faculty_skill1": skill1,
#                 "faculty_skill2": skill2,
#                 "faculty_interest1": interest1,
#                 "faculty_interest2": interest2,
#                 "faculty_role": role
#             }},
#             upsert=True  # Insert the document if it doesn't exist
#         )
#         # Redirect the user to the dashboard with username as a parameter
#         return redirect(url_for('dashboard', username=username))
#     else:
#         return render_template('profile.html', skills=skills, interests=interests)
    
    
# @app.route('/')
# def index():
#     return render_template('home.html')

# @app.route('/login', methods=['GET', 'POST'])  # Allow both GET and POST requests
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         # Query the user from the MongoDB collection
#         user = users_collection.find_one({"faculty_username": username, "faculty_password": password})
#         if user:
#             # Successful login
#             return redirect(url_for('dashboard', username=username))
#         else:
#             # Failed login
#             return render_template('login.html', message="Invalid username or password")
#     else:
#         # If GET request, render the login page
#         return render_template('login.html')

# @app.route('/signup')
# def signup():
#     return render_template('signup.html')

# ''' @app.route('/dashboard/<username>')
# def dashboard(username):
#     # Retrieve user information
#     user = users_collection.find_one({"faculty_username": username})
#     if user:
#         # Retrieve user skills and interests
#         user_skills = [user.get("faculty_skill1", ""), user.get("faculty_skill2", "")]
#         user_interests = [user.get("faculty_interest1", ""), user.get("faculty_interest2", "")]
#         # Call the recommender system function
#         recommended_projects = recommend_projects(user_skills, user_interests)
#         return render_template('dashboard.html', username=username, projects=recommended_projects)
#     else:
#         return render_template('dashboard.html', username=username, projects=None) '''


# @app.route('/signup', methods=['GET', 'POST'])
# def signup_handler():
#     if request.method == 'POST':
#         username = request.form['username']
#         email = request.form['email']
#         password = request.form['password']
        
#         # Check if the username already exists in the database
#         existing_user = users_collection.find_one({"faculty_username": username})
#         if existing_user:
#             return render_template('signup.html', message="Username already exists. Please choose another username.")
        
#         try:
#             # Insert the new user into the database
#             new_user = {
#                 "faculty_username": username,
#                 "faculty_email": email,
#                 "faculty_password": password,
#                 # Add additional fields as needed
#             }
#             users_collection.insert_one(new_user)
        
#             # Redirect the user to the dashboard with username as a parameter
#             return redirect(url_for('dashboard', username=username))
#         except Exception as e:
#             return render_template('signup.html', message="An error occurred while creating the account. Please try again later.")

#     else:
#         return render_template('signup.html', skills=skills, interests=interests)
    
    
# ######################### Search Proects Search Bar ##########
# # Define a function to search projects based on the search query


# # Other routes and functions...
# ###########################


# # Define your collaborative filtering recommendation function
# def get_collaborative_recommendations(skill1, skill2):
#     # Query projects collection based on user skills
#     collaborative_recommendations = projects_collection.find({
#         "$or": [
#             {"Skills": {"$in": [skill1]}},
#             {"Skills": {"$in": [skill2]}}
#         ]
#     })
#     return list(collaborative_recommendations)

# # Define your content-based filtering recommendation function
# def get_content_based_recommendations(interest1, interest2):
#     # Query projects collection based on user interests
#     content_based_recommendations = projects_collection.find({
#         "$or": [
#             {"faculty_interests": {"$in": [interest1]}},
#             {"faculty_interests": {"$in": [interest2]}}
#         ]
#     })
#     return list(content_based_recommendations)


# # Define your recommendation merging function
# def merge_recommendations(collaborative_recommendations, content_based_recommendations):
#     # Placeholder for merging recommendations
#     # For simplicity, let's just concatenate the lists
#     merged_recommendations = collaborative_recommendations + content_based_recommendations
#     return merged_recommendations

# # Define your recommendation generation function
# def get_recommendations(skill1, skill2, interest1, interest2):
#     # Get recommendations from collaborative filtering
#     collaborative_recommendations = get_collaborative_recommendations(skill1, skill2)
    
#     # Get recommendations from content-based filtering
#     content_based_recommendations = get_content_based_recommendations(interest1, interest2)
    
#     # Merge recommendations from both approaches
#     recommendations = merge_recommendations(collaborative_recommendations, content_based_recommendations)
    
#     return recommendations

# ''' # Define the dashboard route to handle both GET and POST requests
# @app.route('/dashboard', methods=['GET', 'POST'])
# def new_dashboard():
#     if request.method == 'POST':
#         # Get user inputs from the form
#         skill1 = request.form['skill1']
#         skill2 = request.form['skill2']
#         interest1 = request.form['interest1']
#         interest2 = request.form['interest2']
        
#         # Get recommendations based on user inputs
#         recommended_projects = get_recommendations(skill1, skill2, interest1, interest2)
        
#         return render_template('dashboard.html', username="User", projects=recommended_projects)
#     else:
#         # Render the dashboard template with no projects initially
#         return render_template('dashboard.html', username="User", projects=None) '''


# ''' @app.route('/dashboard_page', methods=['GET', 'POST'])  # Rename the route
# def dashboard_page():
#     if request.method == 'POST':
#         skill1 = request.form['skill1']
#         skill2 = request.form['skill2']
#         interest1 = request.form['interest1']
#         interest2 = request.form['interest2']
        
#         # Query projects collection based on user skills and interests
#         projects = projects_collection.find({
#             "$or": [
#                 {"skills": {"$in": [skill1, skill2]}},
#                 {"interests": {"$in": [interest1, interest2]}}
#             ]
#         })
        
#         return render_template('dashboard.html', username="User", projects=projects)
#     else:
#         return render_template('dashboard.html', username="User", projects=None) '''


# @app.route('/dashboard', methods=['POST'])
# def final_dashboard():
#     skills = request.form.get('skills')
#     if skills:
#         project_skills = [skill.strip() for skill in skills.split(',')]
#         skills_vector = tfidf_vectorizer.transform([', '.join(project_skills)])
#         similarity_scores = cosine_similarity(skills_vector, tfidf_matrix)
#         recommendations = [(project, company, score) for project, company, score in zip(df['Industry_Project_Name'], df['Industry_Company_Name'], similarity_scores[0])]
#         recommendations.sort(key=lambda x: x[2], reverse=True)
#         recommended_projects = recommendations[:5]  # Get top 5 recommended projects
#     else:
#         recommended_projects = []
#     return render_template('dashboard.html', recommended_projects=final_dashboard)



# if __name__ == '__main__':
#     app.run(debug=True)






''' from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb+srv://w1798587:Success%402024@cluster0.69rs1dl.mongodb.net/")
db = client["MyDatabase"]
users_collection = db["Faculty"]
projects_collection = db["Project"]

# Dummy skills and interests data
skills = ["Machine Learning", "Python", "Data Analysis"]
interests = ["Artificial Intelligence", "Python", "Data Science"]

def recommend_projects(user_skills, user_interests):
    # Query projects collection based on user skills and interests
    recommended_projects = projects_collection.find({
        "$or": [
            {"skills": {"$in": user_skills}},
            {"interests": {"$in": user_interests}}
        ]
    }).limit(5)  # Limit the number of recommended projects to 5 for example
    return recommended_projects

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        skill1 = request.form['skill1']
        skill2 = request.form['skill2']
        interest1 = request.form['interest1']
        interest2 = request.form['interest2']
        role = request.form['role']
        # Update user profile information in the database
        users_collection.update_one(
            {"faculty_username": username},
            {"$set": {
                "faculty_name": name,
                "faculty_skill1": skill1,
                "faculty_skill2": skill2,
                "faculty_interest1": interest1,
                "faculty_interest2": interest2,
                "faculty_role": role
            }},
            upsert=True  # Insert the document if it doesn't exist
        )
        # Redirect the user to the dashboard with username as a parameter
        return redirect(url_for('dashboard', username=username))
    else:
        return render_template('profile.html', skills=skills, interests=interests)
    
    
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])  # Allow both GET and POST requests
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Query the user from the MongoDB collection
        user = users_collection.find_one({"faculty_username": username, "faculty_password": password})
        if user:
            # Successful login
            return redirect(url_for('dashboard', username=username))
        else:
            # Failed login
            return render_template('login.html', message="Invalid username or password")
    else:
        # If GET request, render the login page
        return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/dashboard/<username>')
def dashboard(username):
    # Retrieve user information
    user = users_collection.find_one({"faculty_username": username})
    if user:
        # Retrieve user skills and interests
        user_skills = [user.get("faculty_skill1", ""), user.get("faculty_skill2", "")]
        user_interests = [user.get("faculty_interest1", ""), user.get("faculty_interest2", "")]
        # Call the recommender system function
        recommended_projects = recommend_projects(user_skills, user_interests)
        return render_template('dashboard.html', username=username, projects=recommended_projects)
    else:
        return render_template('dashboard.html', username=username, projects=None)

if __name__ == '__main__':
    app.run(debug=True)
 '''



# from flask import Flask, render_template, request, redirect, url_for
# from pymongo import MongoClient

# app = Flask(__name__)

# # MongoDB connection
# client = MongoClient("mongodb+srv://w1798587:Success%402024@cluster0.69rs1dl.mongodb.net/")
# db = client["MyDatabase"]
# users_collection = db["Faculty"]
# projects_collection = db["Project"]

# # Dummy skills and interests data
# skills = ["Skill 1", "Skill 2", "Skill 3"]
# interests = ["Interest 1", "Interest 2", "Interest 3"]

# def recommend_projects(user_skills, user_interests):
#     # Query projects collection based on user skills and interests
#     recommended_projects = projects_collection.find({
#         "$or": [
#             {"skills": {"$in": user_skills}},
#             {"interests": {"$in": user_interests}}
#         ]
#     }).limit(5)  # Limit the number of recommended projects to 5 for example
#     return recommended_projects

# @app.route('/profile', methods=['GET', 'POST'])
# def profile():
#     if request.method == 'POST':
#         username = request.form['username']
#         name = request.form['name']
#         skill1 = request.form['skill1']
#         skill2 = request.form['skill2']
#         interest1 = request.form['interest1']
#         interest2 = request.form['interest2']
#         role = request.form['role']
#         # Update user profile information in the database
#         try:
#             users_collection.update_one(
#                 {"faculty_username": username},
#                 {"$set": {
#                     "faculty_name": name,
#                     "faculty_skill1": skill1,
#                     "faculty_skill2": skill2,
#                     "faculty_interest1": interest1,
#                     "faculty_interest2": interest2,
#                     "faculty_role": role
#                 }}
#             )
#             # Retrieve user skills and interests
#             user_skills = [skill1, skill2]
#             user_interests = [interest1, interest2]
#             # Call the recommender system function
#             recommended_projects = recommend_projects(user_skills, user_interests)
#             return render_template('dashboard.html', username=username, projects=recommended_projects)
#         except Exception as e:
#             # Handle database update errors
#             return render_template('error.html', message="An error occurred while updating your profile. Please try again later.")
#     else:
#         return render_template('profile.html', skills=skills, interests=interests)
    
# @app.route('/')
# def index():
#     return render_template('home.html')

# @app.route('/login', methods=['GET', 'POST'])  # Allow both GET and POST requests
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']
#         # Query the user from the MongoDB collection
#         user = users_collection.find_one({"faculty_username": username, "faculty_password": password})
#         if user:
#             # Successful login
#             return redirect(url_for('dashboard', username=username))
#         else:
#             # Failed login
#             return render_template('login.html', message="Invalid username or password")
#     else:
#         # If GET request, render the login page
#         return render_template('login.html')

# @app.route('/signup')
# def signup():
#     return render_template('signup.html')

# @app.route('/dashboard/<username>')
# def dashboard(username):
#     # Retrieve user information
#     user = users_collection.find_one({"faculty_username": username})
#     if user:
#         # Retrieve user skills and interests
#         user_skills = [user.get("faculty_skill1", ""), user.get("faculty_skill2", "")]
#         user_interests = [user.get("faculty_interest1", ""), user.get("faculty_interest2", "")]
#         # Call the recommender system function
#         recommended_projects = recommend_projects(user_skills, user_interests)
#         return render_template('dashboard.html', username=username, projects=recommended_projects)
#     else:
#         return render_template('error.html', message="User not found.")

# if __name__ == '__main__':
#     app.run(debug=True)



''' from flask import Flask, render_template, request, redirect, url_for
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB connection
client = MongoClient("mongodb+srv://w1798587:Success%402024@cluster0.69rs1dl.mongodb.net/")
db = client["MyDatabase"]
users_collection = db["Faculty"]
projects_collection = db["Project"]

# Dummy skills and interests data
skills = ["Skill 1", "Skill 2", "Skill 3"]
interests = ["Interest 1", "Interest 2", "Interest 3"]

def recommend_projects(user_skills, user_interests):
    # Query projects collection based on user skills and interests
    recommended_projects = projects_collection.find({
        "$or": [
            {"skills": {"$in": user_skills}},
            {"interests": {"$in": user_interests}}
        ]
    }).limit(5)  # Limit the number of recommended projects to 5 for example
    return recommended_projects

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        username = request.form['username']
        name = request.form['name']
        skill1 = request.form['skill1']
        skill2 = request.form['skill2']
        interest1 = request.form['interest1']
        interest2 = request.form['interest2']
        role = request.form['role']
        # Update user profile information in the database
        users_collection.update_one(
            {"faculty_username": username},
            {"$set": {
                "faculty_name": name,
                "faculty_skill1": skill1,
                "faculty_skill2": skill2,
                "faculty_interest1": interest1,
                "faculty_interest2": interest2,
                "faculty_role": role
            }}
        )
        # Retrieve user skills and interests
        user_skills = [skill1, skill2]
        user_interests = [interest1, interest2]
        # Call the recommender system function
        recommended_projects = recommend_projects(user_skills, user_interests)
        return render_template('dashboard.html', username=username, projects=recommended_projects)
    else:
        return render_template('profile.html', skills=skills, interests=interests)
    
@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])  # Allow both GET and POST requests
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Query the user from the MongoDB collection
        user = users_collection.find_one({"faculty_username": username, "faculty_password": password})
        if user:
            # Successful login
            return redirect(url_for('dashboard', username=username))
        else:
            # Failed login
            return render_template('login.html', message="Invalid username or password")
    else:
        # If GET request, render the login page
        return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/dashboard/<username>')
def dashboard(username):
    # Retrieve user information
    user = users_collection.find_one({"faculty_username": username})
    if user:
        # Retrieve user skills and interests
        user_skills = [user["faculty_skill1"], user["faculty_skill2"]]
        user_interests = [user["faculty_interest1"], user["faculty_interest2"]]
        # Call the recommender system function
        recommended_projects = recommend_projects(user_skills, user_interests)
        return render_template('dashboard.html', username=username, projects=recommended_projects)
    else:
        return render_template('dashboard.html', username=username, projects=None)

if __name__ == '__main__':
    app.run(debug=True)

 '''

''' from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Dummy user data (replace this with your actual user database)
users = {
    "user1": {"password": "password1", "projects": ["Project A", "Project B"]},
    "user2": {"password": "password2", "projects": ["Project C", "Project D"]}
}

# Dummy project data (replace this with your actual project database)
projects = {
    "Project A": {"description": "Description of Project A"},
    "Project B": {"description": "Description of Project B"},
    "Project C": {"description": "Description of Project C"},
    "Project D": {"description": "Description of Project D"}
}

# Dummy skills and interests data
skills = ["Skill 1", "Skill 2", "Skill 3"]
interests = ["Interest 1", "Interest 2", "Interest 3"]


@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])  # Allow both GET and POST requests
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]["password"] == password:
            # Successful login
            return redirect(url_for('dashboard', username=username))
        else:
            # Failed login
            return render_template('login.html', message="Invalid username or password")
    else:
        # If GET request, render the login page
        return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/dashboard/<username>')
def dashboard(username):
    user_projects = users[username]["projects"]
    recommended_projects = [projects[project] for project in user_projects]
    return render_template('dashboard.html', username=username, projects=recommended_projects)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        # Update user profile information
        username = request.form['username']
        name = request.form['name']
        skill1 = request.form['skill1']
        skill2 = request.form['skill2']
        interest1 = request.form['interest1']
        interest2 = request.form['interest2']
        role = request.form['role']
        # Update the user profile in the database (not implemented in this example)
        return redirect(url_for('dashboard', username=username))
    else:
        # Render the profile page with dropdown options for skills and interests
        return render_template('profile.html', skills=skills, interests=interests)

if __name__ == '__main__':
    app.run(debug=True) 
 '''


''' from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Dummy user data (replace this with your actual user database)
users = {
    "user1": {"password": "password1", "projects": ["Project A", "Project B"]},
    "user2": {"password": "password2", "projects": ["Project C", "Project D"]}
}

# Dummy project data (replace this with your actual project database)
projects = {
    "Project A": {"description": "Description of Project A"},
    "Project B": {"description": "Description of Project B"},
    "Project C": {"description": "Description of Project C"},
    "Project D": {"description": "Description of Project D"}
}

@app.route('/')
def index():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])  # Allow both GET and POST requests
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]["password"] == password:
            # Successful login
            return redirect(url_for('dashboard', username=username))
        else:
            # Failed login
            return render_template('login.html', message="Invalid username or password")
    else:
        # If GET request, render the login page
        return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/dashboard/<username>')
def dashboard(username):
    user_projects = users[username]["projects"]
    recommended_projects = [projects[project] for project in user_projects]
    return render_template('dashboard.html', username=username, projects=recommended_projects)

if __name__ == '__main__':
    app.run(debug=True) '''



''' from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Dummy user data (replace this with your actual user database)
users = {
    "user1": {"password": "password1", "projects": ["Project A", "Project B"]},
    "user2": {"password": "password2", "projects": ["Project C", "Project D"]}
}

# Dummy project data (replace this with your actual project database)
projects = {
    "Project A": {"description": "Description of Project A"},
    "Project B": {"description": "Description of Project B"},
    "Project C": {"description": "Description of Project C"},
    "Project D": {"description": "Description of Project D"}
}

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])  # Allow both GET and POST requests
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username]["password"] == password:
            # Successful login
            return redirect(url_for('dashboard', username=username))
        else:
            # Failed login
            return render_template('login.html', message="Invalid username or password")
    else:
        # If GET request, render the login page
        return render_template('login.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/dashboard/<username>')
def dashboard(username):
    user_projects = users[username]["projects"]
    recommended_projects = [projects[project] for project in user_projects]
    return render_template('dashboard.html', username=username, projects=recommended_projects)

if __name__ == '__main__':
    app.run(debug=True)

 '''

''' from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Dummy user data (replace this with your actual user database)
users = {
    "user1": {"password": "password1", "projects": ["Project A", "Project B"]},
    "user2": {"password": "password2", "projects": ["Project C", "Project D"]}
}

# Dummy project data (replace this with your actual project database)
projects = {
    "Project A": {"description": "Description of Project A"},
    "Project B": {"description": "Description of Project B"},
    "Project C": {"description": "Description of Project C"},
    "Project D": {"description": "Description of Project D"}
}

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username in users and users[username]["password"] == password:
        # Successful login
        return redirect(url_for('dashboard', username=username))
    else:
        # Failed login
        return render_template('login.html', message="Invalid username or password")

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/dashboard/<username>')
def dashboard(username):
    user_projects = users[username]["projects"]
    recommended_projects = [projects[project] for project in user_projects]
    return render_template('dashboard.html', username=username, projects=recommended_projects)

if __name__ == '__main__':
    app.run(debug=True)

 '''

''' from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Dummy user data (replace this with your actual user database)
users = {
    "user1": {"password": "password1", "projects": ["Project A", "Project B"]},
    "user2": {"password": "password2", "projects": ["Project C", "Project D"]}
}

# Dummy project data (replace this with your actual project database)
projects = {
    "Project A": {"description": "Description of Project A"},
    "Project B": {"description": "Description of Project B"},
    "Project C": {"description": "Description of Project C"},
    "Project D": {"description": "Description of Project D"}
}

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    if username in users and users[username]["password"] == password:
        # Successful login
        return redirect(url_for('dashboard', username=username))
    else:
        # Failed login
        return render_template('login.html', message="Invalid username or password")

@app.route('/dashboard/<username>')
def dashboard(username):
    user_projects = users[username]["projects"]
    recommended_projects = [projects[project] for project in user_projects]
    return render_template('dashboard.html', username=username, projects=recommended_projects)

if __name__ == '__main__':
    app.run(debug=True)

 '''


''' from flask import Flask, render_template, jsonify

app = Flask(__name__)

# Sample movie data
movies = [
    {"id": 1, "title": "Movie 1", "poster": "movie1.jpg"},
    {"id": 2, "title": "Movie 2", "poster": "movie2.jpg"},
    {"id": 3, "title": "Movie 3", "poster": "movie3.jpg"},
    # Add more movies as needed
]

# Sample recommendation function
def get_recommendations(movie_id):
    # Implement your recommendation logic here
    recommendations = ["Recommendation 1", "Recommendation 2", "Recommendation 3"]
    return recommendations

@app.route('/')
def index():
    return render_template('index.html', movies=movies)

@app.route('/recommend/<int:movie_id>')
def recommend(movie_id):
    recommendations = get_recommendations(movie_id)
    return jsonify(recommendations)

if __name__ == '__main__':
    app.run(debug=True)
 '''