# LOADING ALL THE NECESSARY LIBRARY
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from fuzzywuzzy import fuzz
import re
import pandas as pd
import plotly.express as px
import os
import streamlit as st 



def load_dataset(file_path):
    dataset = {}
    with open(file_path, 'r') as file:
        lines = file.readlines()
        current_key = None
        current_value = ""

        for line in lines:
            # Remove leading and trailing whitespaces
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Check if the line has a colon ':'
            if ':' in line:
                # If current_key is not None, add it to the dataset
                if current_key is not None:
                    dataset[current_key] = current_value

                # Split the line into key and value
                current_key, current_value = map(str.strip, line.split(':', 1))

            else:
                # If the line doesn't contain a colon, append it to the current value
                current_value += '\n' + line

        # Add the last key-value pair to the dataset
        if current_key is not None:
            dataset[current_key] = current_value

    return dataset


external_dataset_path = r'data.txt'
dataset = load_dataset(external_dataset_path)


def sem():
    st.write("Enter the Semester Number (1 - 7)")
    semester = st.number_input(
        "Semester Number", min_value=1, max_value=7, step=1)
    reg = st.text_input("Enter Registration Number:")
    if st.button("Submit"):
        semesters = {
            1: pd.read_csv('SEMESTER 1.csv'),
            2: pd.read_csv('SEMESTER 2.csv'),
            3: pd.read_csv('SEMESTER 3.csv'),
            4: pd.read_csv('SEMESTER 4.csv'),
            5: pd.read_csv('SEMESTER 5.csv'),
            6: pd.read_csv('SEMESTER 6.csv'),
            7: pd.read_csv('SEMESTER 7.csv')
        }

        st.write(f"Student Grade for Semester {semester} is:")
        student_grade = semesters[semester][semesters[semester]['REGISTER NUMBER'] == reg].iloc[0]
        
        # Styling the table to set its width and height
        student_grade_styled = student_grade.to_frame().T.style.set_table_attributes('style="width: 800px; height: 300px;"')
        
        # Displaying the styled table
        st.write(student_grade_styled)
            

def overall():
    st.write("The Grade split criteria followed is given below:")
    st.write("Grade O: 91-100")
    st.write("Grade A+: 81-90")
    st.write("Grade A: 71-80")
    st.write("Grade B+: 61-70")
    st.write("Grade C: 50-55")
    st.write("Grade F: 0-49")
    st.write("Grade Ab - Absent")
    st.write("Grade I: Insufficient Attendance")
    st.write("The Attendance split-up criteria followed is given below:")
    st.write("Code H: 95% and above")
    st.write("Code 9: 85-94%")
    st.write("Code 8: 75-84%")
    st.write("Code L: Below 75%")

    st.write("The Overall Attendance and CGPA Percentage for all the 7 Semesters is:")

    reg = st.text_input("Enter Registration Number:")
    if st.button("Generate Report"):
        data = pd.read_csv('FUTURE GOAL AND ATTENDANCE.csv')

        if reg in data['Registration Number'].values:
            student_row = data[data['Registration Number'] == reg].iloc[0]
            name = student_row['STUDENT NAME']
            register = student_row['Registration Number']
            att = student_row['ATTENDANCE PERCENTAGE:']
            cgpa = student_row['CGPA']
            cgpa = float(cgpa)

            st.write("Student Name:", name)
            st.write("Register Number:", register)
            st.write("Overall Attendance:", att)
            st.write("Overall CGPA:", cgpa)

            fig_attendance = px.pie(values=[att, 100 - att], names=['Attendance', 'Absent'],
                                    title=f'Attendance Distribution for Student {register}')
            st.plotly_chart(fig_attendance)

            fig_cgpa = px.pie(values=[cgpa, 10 - cgpa], names=['CGPA', 'CGPA Left'],
                              title=f'CGPA Distribution for Student {register}')
            st.plotly_chart(fig_cgpa)
        else:
            st.write("Student not found! Enter a valid register number.")

# Function to display summary report


def summary_report():
    st.write("Academic Summary Report")
    st.write("Branch: B Tech Computer Science Engineering")
    st.write("Section: Artificial Intelligence and Machine Learning(AIML)")
    st.write("Class Incharge: Dr. S K B Sangeetha")
    st.write("Batch: 2020-2024")
    st.write("Total No.of.Students: 56")

    df = pd.read_csv('Minor_project_dataset_CSE-AIML - Sheet1.csv')

    grade_oe_i = df['GRADE FOR OE-I']
    grade_foreign_language = df['GRADE FOR FOREIGN LANGUAGE :']
    grade_pe_i = df['GRADE FOR PE-I']

    fig = px.line(df, x=df.index, y=[grade_oe_i, grade_foreign_language, grade_pe_i],
                  markers=True, labels={'value': 'Grade', 'variable': 'Subject'},
                  title='Line Chart for Grades', hover_data=['Registration Number'])
    fig.update_layout(xaxis_title='Registration Number', yaxis_title='Grade')
    st.plotly_chart(fig)

    future_goal_data = df['FUTURE GOAL:']
    future_goal_counts = future_goal_data.value_counts().reset_index()
    future_goal_counts.columns = ['Future Goals', 'Count']
    fig = px.pie(future_goal_counts, names='Future Goals', values='Count',
                 title='Distribution of Future Goals', height=500, width=700)
    fig.update_traces(textinfo='percent+label', hole=0.3)
    st.plotly_chart(fig)

    cgpa_data = df['CGPA OVERALL:']
    attendance_data = df['ATTENDANCE PERCENTAGE:']

    criteria = []

    for cgpa, attendance in zip(cgpa_data, attendance_data):
        if cgpa >= 8.5 and attendance >= 85:
            criteria.append("High CGPA & High Attendance")
        elif cgpa >= 8.5 and attendance < 85:
            criteria.append("High CGPA & Low Attendance")
        elif cgpa < 8.5 and attendance < 85:
            criteria.append("Low CGPA & Low Attendance")
        else:
            criteria.append("Low CGPA & High Attendance")

    df['Cluster'] = criteria

    color_dict = {
        "High CGPA & High Attendance": 'blue',
        "High CGPA & Low Attendance": 'green',
        "Low CGPA & Low Attendance": 'red',
        "Low CGPA & High Attendance": 'black'
    }

    fig = px.scatter(df, x='CGPA OVERALL:', y='ATTENDANCE PERCENTAGE:', color='Cluster', color_discrete_map=color_dict,
                     labels={'CGPA OVERALL:': 'CGPA OVERALL',
                             'ATTENDANCE PERCENTAGE:': 'ATTENDANCE PERCENTAGE'},
                     title='Student Category Customization Clustering Analysis Plot for CGPA and Attendance',
                     hover_data={'Registration Number'})
    st.plotly_chart(fig)


def check_eligibility(percentage_10th, percentage_12th, cgpa, arrears, aptitude, coding, interview):
    categories = []
    feedback = []

    if percentage_10th >= 80 and percentage_12th >= 80 and cgpa >= 8.0 and arrears == 0:
        categories.append("Marquee Placement")
        feedback.append(
            "Congratulations! You have excellent academic performance and eligible for Marquee Placement.")
    if percentage_10th >= 70 and percentage_12th >= 70 and cgpa >= 7.0 and arrears == 0:
        categories.append("Super Dream Placement")
        feedback.append(
            "Congratulations! You meet the criteria for Super Dream Placement. Keep up the good work!")
    if percentage_10th >= 60 and percentage_12th >= 60 and cgpa >= 6.0 and arrears == 0:
       if aptitude >= 6 and coding >= 5 and interview >= 6:
           categories.append("Dream Placement")
           feedback.append(
               "Congratulations! You are eligible for Dream Placement. Keep up the good work!")
    if aptitude >= 6 and coding >= 4 and interview >= 6:
        categories.append("Non-Engineering, IT, Core Placement")
        feedback.append(
            "You qualify for Non-Engineering, IT, Core Placement. Keep improving your coding skills!")

    return categories, feedback


def placement_eligibility(reg):
    st.write("This module gives the Student's Placement Eligibility details.")
    st.write("")
    dataset = pd.read_csv('Student Details (Responses).csv')

    # Check if the register number exists in the dataset
    if reg in dataset['Register Number'].values:
        student = dataset[dataset['Register Number'] == reg].iloc[0]
        Name = student['Name']
        tenth_percentage = float(student['10th Percentage'])
        twelfth_percentage = float(student['12th Percentage'])
        aptitude_rating = int(
            student['Rate yourself for Aptitude (out of 10)'])
        coding_rating = int(
            student['Rate yourself for coding skills (out of 10)'])
        interview_rating = int(
            student['Rate yourself for Interview skills (out of 10)'])
        cgpa = float(student['CGPA OVERALL:'])
        arrears = int(student['ARREARS/BACKLOGS:'])

        st.write(f"10th Percentage: {tenth_percentage}")
        st.write(f"12th Percentage: {twelfth_percentage}")
        st.write(f"Overall CGPA: {cgpa}")

        if tenth_percentage >= 60 and twelfth_percentage >= 60 and cgpa >= 6.0 and arrears == 0:
            st.write(f"{Name} is Eligible for Placement")
        else:
            st.write(f"{Name} is Not Eligible for Placement")

        st.write("Further more details about Placements!")
        categories, feedback = check_eligibility(
            tenth_percentage, twelfth_percentage, cgpa, arrears, aptitude_rating, coding_rating, interview_rating)
        st.write(
            f"{Name} ({reg}): Your are Eligible to the below offers in SRM Campus Placement")
        for category, message in zip(categories, feedback):
            st.write(f"- {category}: {message}")
    else:
        st.write(
            "Register number not found in the dataset. Please enter a valid register number.")


def academics():
    st.write("This section is specialized for retrieving the student information of CSE-AIML (2020 - 2024)")
    reg = st.text_input("Please enter the student register number:")
    df = pd.read_csv('FUTURE GOAL AND ATTENDANCE.csv')

    if reg in df['Registration Number'].values:
        student_row = df[df['Registration Number'] == reg].iloc[0]
        name = student_row['STUDENT NAME']
        register = student_row['Registration Number']
        dept = student_row['Department']
        sec = student_row['SECTION']
        year = student_row['YEAR OF PASSING:']
        mail = student_row['COLLEGE MAIL ID:']

        st.write("Student Information:")
        st.write(f"Name: {name}")
        st.write(f"Register Number: {register}")
        st.write(f"Department: {dept}")
        st.write(f"Section: {sec}")
        st.write(f"Year of Passing: {year}")
        st.write(f"Mail ID: {mail}")

        # option = st.selectbox("Select an option to continue:", [
        #                       "Semester Marks", "Overall Attendance and CGPA", "CSE-AIML Summary Report", "Placement Prediction"])

        # if option == "Semester Marks":
        #     sem(reg)
        # elif option == "Overall Attendance and CGPA":
        #     overall(reg)
        # elif option == "CSE-AIML Summary Report":
        #     summary_report()
        # elif option == "Placement Prediction":
        #     placement_eligibility(reg)
    elif reg.strip()=="":
        st.write("")
    else:
        st.write("Student not found! Enter a valid register number.")


class FeedbackGenerator:
    def __init__(self, student_data):
        self.student_data = student_data

    def generate_feedback(self):
        feedback = f"Feedback for {self.student_data['STUDENT NAME']}({self.student_data['Registration Number']}): "

        # Analyze academic performance
        feedback += self.analyze_academic_performance()

        # Analyze club participation
        feedback += self.analyze_club_participation()

        # Analyze internship experience
        feedback += self.analyze_internship_experience()

        # Add wishes for future endeavors
        feedback += self.goal()

        return feedback

    def analyze_academic_performance(self):
        grades = {
            '10th grade': float(self.student_data['10 GRADE']),
            '12th grade': float(self.student_data['12 GRADE']),
            'cgpa': float(self.student_data['CGPA'])
        }

        excellent_performance = all(grade >= 70 for grade in grades.values())

        if excellent_performance:
            return "\nExcellent performance in your 10th, 12th grade and Undergraduate degree, in which you have secured Distinction!. \n" \
                   "It was really a awesome and a appreciatable result.\n"
        else:
            return "Your academic performance has been commendable. Try securing high places and exploring more opportunities. "

    def analyze_club_participation(self):
        if self.student_data['IN ANY CLUB?'] == 1:
            feedback = f"I personally congratulate you for your active participation in college clubs named {self.student_data['COLLEGE CLUB']}\n " \
                       f"and leading College Club Activities by serving as '{self.student_data['WORKED AS?']}'.Hope You will lead high places.\n "
            return feedback
        else:
            feedback = f"I encourage you to consider participating in college clubs for a well-rounded experience,\n"\
                       f"where you could find the opportunities to get and explore many new stages.\n"
            return feedback

    def analyze_internship_experience(self):
        if self.student_data['NO_OF_INTERNSHIP'] > 0:
            feedback = f"I also appreciate your preliminary work experience as you have completed {self.student_data['NO_OF_INTERNSHIP']} internships,\n in the domain of {self.student_data['INTERNSHIP_DOMAIN']}\n. "
            return feedback
        else:
            return "I encourage you to explore internship opportunities for more practical exposure.\n"

    def goal(self):
        if self.student_data['FUTURE GOAL'].lower() != 'others':
            if self.student_data['FUTURE GOAL'].lower() == 'higher studies':
                feedback = f"I wish you a best of luck to acheive great heights by pursuing your \n{self.student_data['FUTURE GOAL']} in your dream domain of {self.student_data['FUTURE DOMAIN:']}.Congrats and Best of luck for you! "
                return feedback
            if self.student_data['FUTURE GOAL'].lower() == 'placements':
                feedback = f"I hope you will find a suitable firm for your\n {self.student_data['FUTURE GOAL']} that best suites your aspirations, in your dream career domain of {self.student_data['FUTURE DOMAIN:']}.Congrats and Wishing  you Best of luck!"
                return feedback
        else:
            return "I Hope you have some Intersting Career options, to proceed in terms of reaching great heights in your future path.\n Congratulation to you, and Wishing you to have an admirable future!"


def about_srm():
    st.title("About SRMIST Vadapalani")
    st.write("This section answer's all the general queries regarding SRMIST Vadapalani, under the below options!")
    st.write("1. Mission and Vision Of SRM")
    st.write("2. History of SRM Group of Institutions")
    st.write("3. SRM Vadapalani Campus Tour")
    st.write("4. SRM Vadapalani Website")
    user_query = st.text_input("Enter your query:")
    get_response(user_query)
    
def FET():
    st.title("Faculty of Engineering and Technology @Vadapalani")
    st.write("This section explores all the departmental details at SRM Vadapalani!")
    st.write("Please select a department from the options listed.")
    options = ["Select","Computer Science", "Electronics and Communication", "Mechanical","Career Development Center","Chemistry","English and Foreign Languages","Mathematics","Physics"]
    choice = st.sidebar.selectbox("Select Option", options)

    if choice == "Computer Science":
        st.markdown("### Department of Computer Science and Engineering")
        st.write("About the Department:")
        st.write("Computer Science is a rapidly evolving discipline today and at SRM, we go to great lengths to ensure that our faculty and students can devote themselves to take maximal advantage of modern computer science and engineering – to solve a wide range of complex scientific, technological and social problems.")
        st.write("Department Website Link - www.srmistvdp.edu.in/department-of-computer-science-and-engineering")
        st.write("Programs Offered by the Department")

        st.write("Under Graduate Programs")
        st.write(
            "    - B.Tech - Computer Science and Engineering\n")
        st.write(
            "    - B.Tech - Computer Science and Engineering with specialization in Artificial Intelligence and Machine Learning\n")
        st.write(
            "    - B.Tech - Computer Science & Business System (in collaboration with TCS)\n")
        st.write(
            "    - B.Tech - Computer Science and Engineering with specialization in Big Data Analytics\n")
        st.write(
            "    - B.Tech - Computer Science and Engineering with specialization in Cyber Security")
        st.write("Post Graduate Programs")
        st.write(
            "    - M.tech - Computer Science and Engineering\n")
        st.write("Doctorate Programs")
        st.write(
            "    - Ph.D in Computer Science and Engineering")
    elif choice == "Electronics and Communication":
        st.markdown("### Department of Electronics and Communication Engineering")
        st.write("About the Department:")
        st.write("Electronics and Communication Engineering (ECE) is a swiftly advancing field, with new ideas emerging every other second. From mobile phones to fibre optics and remote sensing, there are exciting avenues to explore and create. The ECE department at SRM Institute of Science and Technology prepares students for career in this constantly evolving disciplines.")
        st.write("Department Website Link - www.srmistvdp.edu.in/department-of-electronics-and-communication-engineering")
        st.write("Programs Offered by the Department")

        st.write("Under Graduate Programs")
        st.write(
            "    - B.Tech - Electronics and Communication Engineering\n")
        st.write(
            "    - B.Tech - Electronics and Communication Engineering with specialization in Data Science\n")
        st.write("Post Graduate Programs")
        st.write(
            "    - M.tech - ELectronics and Communication Engineering with specialization in VLSI\n")
        st.write("Doctorate Programs")
        st.write(
            "    - Ph.D in Electronics and Communication Engineering")
    elif choice == "Mechanical":
        st.markdown("### Department of Mechanical Engineering")
        st.write("About the Department:")
        st.write("Mechanical Engineers require a solid understanding of key concepts invluding mechanics, kinematics, thermodynamics, energy and manufacturing. They use these principles in design and analysis of automobiles, thus contributing to the fourth industrial revolution known as Industry 4.0.")
        st.write("To compete in this ongrowing world, the Mechanical Engineering department is functionally divided into four broad areas of specializations-")
        st.write("  1) Design")
        st.write("  2) Manufacturing")
        st.write("  3) Thermal")    
        st.write("  4) Materials Engineering")
        st.write("Department Website Link - www.srmistvdp.edu.in/department-of-mechanical-engineering")
        st.write("Programs Offered by the Department")

        st.write("Under Graduate Programs")
        st.write(
            "    - B.Tech - Mechanical Engineering\n")
        st.write(
            "    - B.Tech - Mechanical Engineering with specialization in Artificial Intelligence and Machine Learning\n")
        st.write("Doctorate Programs")
        st.write(
            "    - Ph.D in Mechanical Engineering")
    elif choice == "Career Development Center":
        st.markdown("### Department of Career Development Center")
        st.write("About the Department:")
        st.write("The Career Development Centre at SRM Institute of Science and Technology, understands the pulse of the corporate world and is helping the students to prepare for their career. Besides, the Career Development Centre consists of leading members who are dedicated to providing guidance to the students on creating a clear career plan, setting realistic careergoals and planned timtable on professional development for their future.")
        st.write("Mission:")
        st.write("Create opportunitirs for students to explore and demonstrate their potential. Adopt innovative practices to enhance the learners' professional competencies. Empower students to surpass challenges and emerge as global thought leaders.")  
        st.write("Vision")
        st.write("To transform young minds into socially responsible individuals who can inspire, innovate and overcome challenged in the global environment.")
        st.write("Department Website Link - www.srmistvdp.edu.in/department-of-career-development-centre")
        st.write("Courses Offered by the Department")
        st.write("Under Graduate Programs")
        st.write("1. Soft Skills - Employability skills")
        st.write("2. Quantitative Aptitude and Logical Reasoning")
        st.write("3. Verbal Aptitude \n")
        
    elif choice == "Chemistry":
        st.markdown("### Department of Chemistry")
        st.write("About the Department:")
        st.write("The Department of Chemistry was started in 2009. We have highly qualified, dedicated faculty members. We offer courses for first year B. Tech Students of all branches. The Chemistry laboratory is designed to support and illustrate chemical concepts studied in the lecture portion of the course, as well as to introduce important laboratory techniques and encourage analytical thinking. The research lab is well established and the faculties are actively engaged in research activities. Some of the areas of interest are synthesis of Heterocyclic compounds, Sensor material and Chiral molecules. The aim of the department is to broadly educate basic Chemistry and develop research interest among students")
        st.write("Research Activities:")
        st.write("The areas of research interest of the faculty members includes")  
        st.write(
            "   - Organic synthesis")
        st.write(
            "   - Fluorescent sensors")
        st.write(
            "   - Asymmetric Synthesis")
        st.write(
            "   - Computational Chemistry")
        st.write("Infrastructure")
        st.write("The department has independent laboratories fully equipped with instruments and consumables.")

    elif choice == "English and Foreign Languages":
        st.markdown("### Department of English and Foreign Languages")
        st.write("About the Department:")
        st.write("The Department of English and other Foreign Languages was established in 2009. The department has well qualified and vibrant faculty members. We offer courses to B.tech students of all three branches.The Department has a High-tech Computer Assisted Language Laboratory (CALL) with the audio-visual equipment to aid in imparting language skills. The Department of English and Foreign Languages offers value education to develop the students’ ability to think critically, understand and appreciate diversity, adhere to ethical values, and communicate effectively in a global environment.")
        st.write("Programs Offered:")
        st.write("1. French")  
        st.write(
            "   French, deemed as a global language, is widely used in Europe and Canada. The course also enhances the scope of engineering students finding placement in companies with French collaborations in India. Students are also trained for the Level-I exam in French conducted by the French cultural centre, Alliance Française, Nungambakkam, Chennai, which is internationally recognized.")
        st.write("2. German")  
        st.write(
            "   Numerous German companies are emerging in India. The increased cooperation between the two countries have opened job opportunities in Germany as well. Learning German helps students to get preference over others in getting employment in such companies and in seeking employment abroad.")
        st.write("3. Japanese")  
        st.write(
            "   Engineering students benefit greatly in receiving instruction in the three Japanese scripts, namely Hiragana, Katakana and Kanji. As more and more Japanese clients seek software solutions from India, knowing the language is a definite advantage for fresh engineers who intend to join software companies.")

    elif choice == "Mathematics":
        st.markdown("### Department of Mathematics")
        st.write("About the Department:")
        st.write("The charm of numerals and equations holds the limelight here at SRM’s Mathematics Department. The department caters to engineering students of B.Tech., M.Tech., MBA and Ph.D.")
        st.write("Activities:")
        st.write("The ELITE Mathematics club acts as a forum for budding mathematicians, providing them a unique platform to bring laurels in the field. It is also the platform for events that are aimed at making mathematics fun to learn. The club conducts symposiums, special guest lectures and national level conferences(NCRTMA) every year. This club opens up new vistas for budding mathematicians to fly high, by winning laurels.")
        st.write("Research")
        st.write("Considering how mathematics plays a critical role in various fields from vehicle design to architecture, the faculty encourages research in both fundamental and applied mathematics. The key areas of research interest include,")
        st.write(
            "   - 	Functional Analysis")
        st.write(
            "   - 	Stocastic Processes")
        st.write(
            "   - 	Fuzzy logic and its Applications")
        st.write(
            "   - 	Graph Theory")
        st.write(
            "   - 	Functional Analysis")
        st.write(
            "   - 	Number Theory")
        st.write(
            "   - 	Fluid Dynamics")

    elif choice == "Physics":
        st.markdown("### Department of Physics")
        st.write("About the Department:")
        st.write("Acceleration has gripped the world of physics in the international arena and research studies in this field have broken more barriers than just sound. Physics is linked with the future progress of humankind and the next generation of SRM students are prepared to be a part of it.Dedicated, experienced and well qualified faculty members make up the department. They continually update their grasp on global trends and breakthroughs by attending and presenting papers in national and international conferences.")
        st.write("Academics:")
        st.write("The department caters to engineering students of B.Tech. The programs focus on the fields of Electronics and Communication systems, Computer architecture, & Materials sciences, Hospital industry and Health physics.")
        st.write("Activities")
        st.write("The department conducts seminars and symposiums periodically in emerging areas of materials technology.  The department also organizes to distinct events like National Science Day an EXOT every year to all the colleges and school students across the National.")
        st.write("Research:")
        st.write("The areas of research interest of the faculty members include,")
        st.write(
            "   - 	Nanotechnology")
        st.write(
            "   - 	Crystal Engineering")
        st.write(
            "   - 	Molecular Spectroscopy")
        st.write(
            "   - 	Non-linear Optics")
        st.write(
            "   - 	Ceramic Technology")
        

nlp = spacy.load("en_core_web_sm")

# Load the dataset
dataset1 = {
    "academic assistance of srm vadapalani": "SRM Vadapalani offers comprehensive academic assistance to students, including tutoring, counseling, and academic resources.",
    "semester marks": "You can check your semester marks by logging into the student portal and accessing the 'Academic Records' section.",
    "overall attendance and cgpa": "Your overall attendance and CGPA can be viewed in the student portal under the 'Academic Records' section.",
    "summary report": "The summary report provides an overview of your academic performance, including grades, attendance, and CGPA.",
    "placement prediction": "Placement prediction helps students assess their likelihood of securing a job placement based on their academic and extracurricular achievements.",
    # Add more dataset entries as needed
}

# Tokenize and vectorize the dataset
messages = list(dataset1.keys())
vectorizer = TfidfVectorizer()
message_vectors = vectorizer.fit_transform(messages)

special_keywords_group1 = ["academic", "academic assistance", "grade", "course", "attendance", "report", "marks",
                           "academic assistance of SRM Vadapalani", "placement", "overall attendance and cgpa",
                           "semester marks", "semester", "overall attendance", "overall cgpa",
                           "placement prediction", "summary report"]


def fuzzy_match(query, dataset, threshold=80):
    best_match = None
    highest_similarity = 0

    for key in dataset:
        similarity = fuzz.ratio(query.lower(), key.lower())
        if similarity > highest_similarity and similarity >= threshold:
            highest_similarity = similarity
            best_match = key
    return best_match


def get_response(user_query):
    # Tokenize and vectorize user query
    user_query = user_query.lower()

    # Check for fuzzy matching in the dataset
    fuzzy_matched_key = fuzzy_match(user_query, dataset)
    if fuzzy_matched_key:
        response = dataset[fuzzy_matched_key]
        st.write("Chatbot:", response)
        return

    # Tokenize and vectorize user query
    query_tokens = nlp(user_query)
    query_vector = vectorizer.transform([user_query])

    # Calculate cosine similarity between user query and dataset messages
    similarities = cosine_similarity(query_vector, message_vectors)

    # Find the index of the most similar message
    index_most_similar = similarities.argmax()

    # Check if the similarity is below a certain threshold
    similarity_threshold = 0.2
    if similarities[0, index_most_similar] <= similarity_threshold:
        if any(keyword in user_query.lower() for keyword in special_keywords_group1):
            academics()
        elif user_query.strip() == "":
            st.write("Chatbot:")
        else:
            st.write("Chatbot: I didn't understand. Please try again.")
    else:
        # Retrieve and print the response
        response = dataset[messages[index_most_similar]]
        st.write("Chatbot:", response)

# Streamlit app layout
def srm_academic():
    st.title("Academic Assistance of SRM Vadapalani")
    st.write("This module serves the purpose by giving away all the academic details of the Students!")
    st.write("Select an option to explore more!")
    options = ["Select","Student Information","Semester Grades", "Student Overall Attendance and CGPA", "Class Summary Report"]
    choice = st.sidebar.selectbox("Select Option", options)

    if choice == "Semester Grades":
        st.markdown("### Student Grades")
        sem()
    elif choice == "Student Overall Attendance and CGPA":
        st.markdown("### Student Statistics")
        overall()
    elif choice == "Class Summary Report":
        st.markdown("### Class Summary Report")
        summary_report()
    elif choice == "Student Information":
        st.markdown("### Student Information")
        academics()
    
    


def main():
    st.title("Chattitude: Your Educational Companion")
    st.write(
        "Welcome to Chattitude, your virtual companion on the exciting journey of exploration!")

    st.write(
        "Let's embark on this educational adventure of SRM Institute of Science and Technology.")
    st.write("This is exclusively for Vadapalani Campus, where every question is a step towards knowledge and understanding.")

    st.write("Ready to dive into the world of learning? Let's get started!")

    st.write("Here are some of the menu options listed below, that I can support you to move further in this adventure!")
    main_options = ["Select","About SRM Institute of Science and Technology","Faculty of Engineering @ SRM Vadapalani", "Academic Assistance of SRM Vadapalani","Placement Eligibility","Feedback" ,"Exit"]
    main_choice = st.selectbox("Select Option", main_options)
    
    if main_choice == "About SRM Institute of Science and Technology":
        about_srm()
    elif main_choice == "Faculty of Engineering @ SRM Vadapalani":
        FET()
    elif main_choice == "Academic Assistance of SRM Vadapalani":
        srm_academic()
    elif main_choice == "Placement Eligibility":
        st.markdown("### Student Placement Eligibility")
        reg = st.text_input("Enter Registration Number:")
        if st.button("Check Eligibility"):
            placement_eligibility(reg)
    elif main_choice == "Feedback":
        st.markdown("### Personalized Feedback")
        reg = st.text_input("Enter Registration Number:")
        if st.button("Generate Feedback"):
            feed_df = pd.read_csv('FEEDBACK DATASET.csv')
            if reg in feed_df['Registration Number'].values:
                student_data = feed_df[feed_df['Registration Number']==reg].iloc[0]
                feedback_generator = FeedbackGenerator(student_data)
                feedback_result = feedback_generator.generate_feedback()
                st.write(feedback_result)
            elif reg.strip()=="":
                st.write("")
            else:
                st.write("Student not found! Enter a valid register number.")

    elif main_choice == "Exit":
        st.write("Chatbot: Thanks for choosing me! Hoping you would've had a good experience! Until next time, Goodbye!")
        exit(0)

    # Streamlit app logic
    #user_query = st.text_input("User:", key="user_input")

if __name__ == "__main__":
    main()