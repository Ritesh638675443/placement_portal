import streamlit as st
import pandas as pd

# -----------------------------------
# Page Configuration
# -----------------------------------
st.set_page_config(
    page_title="Industrial Engineering CGPA Calculator",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 INDUSTRIAL ENGINEERING CGPA Calculator")
st.write("Anna University (R2023 Regulation)")

# -----------------------------------
# Grade Mapping
# -----------------------------------
grade_points = {
    "S": 10,
    "A+": 9,
    "A": 8,
    "B+": 7,
    "B": 6,
    "C": 5,
    "RA/U": 0,
    "SA": 0,
    "-": 0
}

# -----------------------------------
# Semester-wise Subjects
# (Only CGPA Subjects)
# -----------------------------------
semesters = {

    "Semester I": [
        ("Computer Programming in Python", 4),
        ("Engineering Chemistry", 4),
        ("Foundation English", 3),
        ("Matrices and Calculus", 4),
        ("Engineering Drawing and 3D Modelling", 4),
        ("Engineering Physics", 4),
        ("Heritage of Tamils", 1),
    ],

    "Semester II": [
        ("Basics of Electrical and Electronics Engineering", 3),
        ("Professional Communication", 3),
        ("Ordinary Differential Equations and Transform Techniques", 4),
        ("Engineering Mechanics", 4),
        ("Makerspace", 3),
        ("Material Science", 3),
        ("Tamils and Technology", 1),
    ],

    "Semester III": [
        ("Mechanics of Materials", 4),
        ("Fluid Mechanics and Machinery", 4),
        ("Work System Design", 4),
        ("Industrial Standards for Industrial Engineering", 1),
        ("Probability and Statistics", 4),
        ("Manufacturing Processes", 4),
    ]
}

overall_credit_points = 0
overall_credits = 0

# -----------------------------------
# Semester Calculations
# -----------------------------------
for semester, subjects in semesters.items():

    st.header(semester)

    semester_credit_points = 0
    semester_credits = 0
    records = []

    for subject, credit in subjects:

        grade = st.selectbox(
            f"{subject} ({credit} Credits)",
            options=list(grade_points.keys()),
            key=f"{semester}_{subject}"
        )

        gp = grade_points[grade]
        credit_points = gp * credit

        semester_credit_points += credit_points
        semester_credits += credit

        records.append({
            "Subject": subject,
            "Credits": credit,
            "Grade": grade,
            "Grade Point": gp,
            "Credit Points": credit_points
        })

    df = pd.DataFrame(records)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

    sgpa = semester_credit_points / semester_credits

    st.success(f"📘 {semester} GPA : **{sgpa:.2f}**")

    overall_credit_points += semester_credit_points
    overall_credits += semester_credits

    st.divider()

# -----------------------------------
# Overall CGPA
# -----------------------------------
cgpa = overall_credit_points / overall_credits

st.header("🎯 Overall CGPA")

col1, col2, col3 = st.columns(3)

col1.metric("Total Credits", overall_credits)
col2.metric("Total Credit Points", overall_credit_points)
col3.metric("CGPA", f"{cgpa:.2f}")

st.markdown("---")

# -----------------------------------
# Grade Scale
# -----------------------------------
st.subheader("📖 Anna University Grade Scale")

grade_df = pd.DataFrame({
    "Letter Grade": [
        "S",
        "A+",
        "A",
        "B+",
        "B",
        "C",
        "RA/U",
        "SA",
        "-"
    ],
    "Meaning": [
        "Outstanding",
        "Excellent",
        "Very Good",
        "Good",
        "Average",
        "Satisfactory",
        "Reappear",
        "Shortage of Attendance",
        "Withheld"
    ],
    "Grade Point": [
        10,
        9,
        8,
        7,
        6,
        5,
        0,
        0,
        0
    ]
})

st.table(grade_df)

st.info(
    """
**Notes**

- Only subjects included in the CGPA are considered.
- UHV (Yoga for Human Excellence / Universal Human Values), NCC/NSS/NSO/YRC, and Audit Courses are **excluded** from CGPA calculation.
- Total Credits Considered:
  - Semester I : **24**
  - Semester II : **21**
  - Semester III : **21**
  - **Overall Credits : 66**
"""
)
